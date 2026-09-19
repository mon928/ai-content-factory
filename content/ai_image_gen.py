"""
SOFIA LUXURY STORY
AI IMAGE GENERATOR

Generates cinematic Sofia visuals using Pollinations when available.

When Pollinations is unavailable or has insufficient balance,
the exact Sofia reference image stored in:

    assets/sofia/sofia_reference.jpg

is used as a safe local fallback.

The local fallback preserves Sofia's vertical 9:16 composition
so her face and full body remain visible.
"""

import os
import time
import base64
from pathlib import Path
from io import BytesIO
from typing import List, Dict, Optional

import requests
from loguru import logger
from PIL import Image, ImageEnhance, ImageFilter


# =========================================================
# PATHS
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

SOFIA_REFERENCE = (
    PROJECT_ROOT
    / "assets"
    / "sofia"
    / "sofia_reference.jpg"
)


# =========================================================
# POLLINATIONS SETTINGS
# =========================================================

POLLINATIONS_API_KEY = os.getenv(
    "POLLINATIONS_API_KEY"
)

POLLINATIONS_IMAGE_URL = (
    "https://gen.pollinations.ai/v1/images/generations"
)

POLLINATIONS_EDIT_URL = (
    "https://gen.pollinations.ai/v1/images/edits"
)

DEFAULT_MODEL = (
    "black-forest-labs/flux.1-schnell"
)


# =========================================================
# SOFIA IDENTITY
# =========================================================

SOFIA_IDENTITY = """
Sofia is the central character of Sofia Luxury Story.

Keep Sofia visually consistent with the supplied reference image.

Preserve her recognizable facial identity, facial features,
skin tone, hairstyle, age appearance and overall appearance.

Sofia must look like the same woman throughout the story.

Do not replace Sofia with another woman.

Do not create a different face.

Sofia can appear in different luxury locations,
technology environments, travel locations, hotels,
penthouse apartments, cars and cinematic settings.

Her identity must remain consistent.
"""


# =========================================================
# IMAGE GENERATOR
# =========================================================

class AIImageGenerator:

    def __init__(
        self,
        output_dir: str = "output/images"
    ):

        self.output_dir = Path(output_dir)

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        self.model = os.getenv(
            "POLLINATIONS_IMAGE_MODEL",
            DEFAULT_MODEL
        )

        self.api_key = (
            os.getenv("POLLINATIONS_API_KEY")
            or POLLINATIONS_API_KEY
        )

        self.pollinations_disabled = False

        logger.info(
            "🎨 Sofia AI Image Generator initialized"
        )

        logger.info(
            f"Project root: {PROJECT_ROOT}"
        )

        logger.info(
            f"Sofia reference: {SOFIA_REFERENCE}"
        )

        logger.info(
            f"Model: {self.model}"
        )

        if SOFIA_REFERENCE.exists():

            try:

                with Image.open(
                    SOFIA_REFERENCE
                ) as image:

                    logger.info(
                        "✅ Sofia reference found: "
                        f"{SOFIA_REFERENCE}"
                    )

                    logger.info(
                        f"Reference size: "
                        f"{image.width}x{image.height}"
                    )

            except Exception as e:

                logger.warning(
                    f"⚠️ Sofia reference exists "
                    f"but could not be opened: {e}"
                )

        else:

            logger.error(
                "❌ Sofia reference image NOT FOUND:"
            )

            logger.error(
                str(SOFIA_REFERENCE)
            )


    # =====================================================
    # HEADERS
    # =====================================================

    def _headers(self) -> dict:

        headers = {
            "Accept": (
                "application/json, "
                "image/jpeg, "
                "image/png"
            )
        }

        if self.api_key:

            headers["Authorization"] = (
                f"Bearer {self.api_key}"
            )

        return headers


    # =====================================================
    # LOAD SOFIA REFERENCE
    # =====================================================

    def _load_sofia_reference(self) -> Optional[Image.Image]:

        if not SOFIA_REFERENCE.exists():

            logger.error(
                "❌ Sofia reference image does not exist:"
            )

            logger.error(
                str(SOFIA_REFERENCE)
            )

            return None

        try:

            image = Image.open(
                SOFIA_REFERENCE
            ).convert("RGB")

            return image

        except Exception as e:

            logger.error(
                f"❌ Could not open Sofia reference: {e}"
            )

            return None


    # =====================================================
    # RESIZE WITHOUT DESTROYING SOFIA
    # =====================================================

    def _fit_reference_to_size(
        self,
        image: Image.Image,
        width: int,
        height: int
    ) -> Image.Image:

        """
        Resize the Sofia reference while preserving her
        composition as much as possible.

        For vertical 9:16 video output, the source photo
        is already 9:16, so it is resized directly.

        We avoid the old 16:9 cover crop that was cutting
        away Sofia's face/body.
        """

        source_ratio = image.width / image.height
        target_ratio = width / height

        # -------------------------------------------------
        # Nearly identical aspect ratio
        # -------------------------------------------------

        if abs(
            source_ratio - target_ratio
        ) < 0.08:

            return image.resize(
                (width, height),
                Image.Resampling.LANCZOS
            )

        # -------------------------------------------------
        # Target is wider than Sofia reference
        # -------------------------------------------------

        if target_ratio > source_ratio:

            new_width = int(
                image.height * target_ratio
            )

            if new_width <= image.width:

                left = (
                    image.width - new_width
                ) // 2

                cropped = image.crop(
                    (
                        left,
                        0,
                        left + new_width,
                        image.height
                    )
                )

                return cropped.resize(
                    (width, height),
                    Image.Resampling.LANCZOS
                )

            # -------------------------------------------------
            # If widening would crop too much, fit instead
            # and use a premium blurred background.
            # -------------------------------------------------

            fitted_height = height

            fitted_width = int(
                image.width
                * fitted_height
                / image.height
            )

            foreground = image.resize(
                (
                    fitted_width,
                    fitted_height
                ),
                Image.Resampling.LANCZOS
            )

            background = image.resize(
                (width, height),
                Image.Resampling.LANCZOS
            )

            background = background.filter(
                ImageFilter.GaussianBlur(18)
            )

            canvas = background.copy()

            x = (
                width - fitted_width
            ) // 2

            canvas.paste(
                foreground,
                (x, 0)
            )

            return canvas

        # -------------------------------------------------
        # Target is taller/narrower
        # -------------------------------------------------

        new_height = int(
            image.width / target_ratio
        )

        if new_height <= image.height:

            top = (
                image.height - new_height
            ) // 2

            cropped = image.crop(
                (
                    0,
                    top,
                    image.width,
                    top + new_height
                )
            )

            return cropped.resize(
                (width, height),
                Image.Resampling.LANCZOS
            )

        return image.resize(
            (width, height),
            Image.Resampling.LANCZOS
        )


    # =====================================================
    # LOCAL SOFIA FALLBACK
    # =====================================================

    def _create_local_fallback(
        self,
        output_path: Path,
        scene_number: int = 0,
        width: int = 720,
        height: int = 1280
    ) -> str:

        """
        Uses the real Sofia reference image locally.

        IMPORTANT:
        The old version converted Sofia's vertical photo
        to 1920x1080 and cropped her.

        This version keeps the vertical composition for
        normal Sofia scenes.
        """

        image = self._load_sofia_reference()

        if image is None:

            return ""

        try:

            image = self._fit_reference_to_size(
                image,
                width,
                height
            )

            # -------------------------------------------------
            # Subtle cinematic variations.
            #
            # These are deliberately gentle so Sofia's
            # identity and appearance remain unchanged.
            # -------------------------------------------------

            variation = scene_number % 8

            if variation == 1:

                image = ImageEnhance.Brightness(
                    image
                ).enhance(1.04)

            elif variation == 2:

                image = ImageEnhance.Contrast(
                    image
                ).enhance(1.06)

            elif variation == 3:

                image = ImageEnhance.Color(
                    image
                ).enhance(1.05)

            elif variation == 4:

                image = ImageEnhance.Sharpness(
                    image
                ).enhance(1.10)

            elif variation == 5:

                image = ImageEnhance.Brightness(
                    image
                ).enhance(0.97)

                image = ImageEnhance.Contrast(
                    image
                ).enhance(1.04)

            elif variation == 6:

                image = ImageEnhance.Color(
                    image
                ).enhance(1.03)

                image = ImageEnhance.Sharpness(
                    image
                ).enhance(1.08)

            elif variation == 7:

                image = image.filter(
                    ImageFilter.SMOOTH_MORE
                )

            image.save(
                output_path,
                "JPEG",
                quality=95,
                optimize=True
            )

            logger.warning(
                "⚠️ Using local Sofia reference fallback:"
            )

            logger.warning(
                f"   {output_path}"
            )

            return str(output_path)

        except Exception as e:

            logger.error(
                f"❌ Local Sofia fallback failed: {e}"
            )

            return ""


    # =====================================================
    # SAVE IMAGE RESPONSE
    # =====================================================

    def _save_response_image(
        self,
        response,
        output_path: Path
    ) -> str:

        try:

            content_type = (
                response.headers.get(
                    "content-type",
                    ""
                ).lower()
            )

            # -------------------------------------------------
            # DIRECT IMAGE RESPONSE
            # -------------------------------------------------

            if (
                content_type.startswith("image/")
                or response.content[:8]
                == b"\x89PNG\r\n\x1a\n"
                or response.content[:2]
                == b"\xff\xd8"
            ):

                image = Image.open(
                    BytesIO(response.content)
                )

                image.convert(
                    "RGB"
                ).save(
                    output_path,
                    "JPEG",
                    quality=95
                )

                return str(output_path)


            # -------------------------------------------------
            # JSON RESPONSE
            # -------------------------------------------------

            data = response.json()

            image_url = None

            if isinstance(data, dict):

                if data.get("data"):

                    first = data["data"][0]

                    if isinstance(first, dict):

                        image_url = first.get(
                            "url"
                        )

                        if not image_url:

                            b64 = first.get(
                                "b64_json"
                            )

                            if b64:

                                image_bytes = (
                                    base64.b64decode(
                                        b64
                                    )
                                )

                                image = Image.open(
                                    BytesIO(
                                        image_bytes
                                    )
                                )

                                image.convert(
                                    "RGB"
                                ).save(
                                    output_path,
                                    "JPEG",
                                    quality=95
                                )

                                return str(
                                    output_path
                                )

                image_url = (
                    image_url
                    or data.get("url")
                    or data.get("image_url")
                )

            if image_url:

                image_response = requests.get(
                    image_url,
                    timeout=60
                )

                image_response.raise_for_status()

                image = Image.open(
                    BytesIO(
                        image_response.content
                    )
                )

                image.convert(
                    "RGB"
                ).save(
                    output_path,
                    "JPEG",
                    quality=95
                )

                return str(output_path)


            logger.error(
                "❌ Pollinations response contained "
                "no usable image."
            )

            return ""

        except Exception as e:

            logger.error(
                f"❌ Could not save generated image: {e}"
            )

            return ""


    # =====================================================
    # TEXT TO IMAGE
    # =====================================================

    def _generate_text_image(
        self,
        prompt: str,
        output_path: Path,
        width: int,
        height: int,
        scene_number: int = 0
    ) -> str:

        if self.pollinations_disabled:

            logger.warning(
                "⚠️ Pollinations disabled for this run."
            )

            return self._create_local_fallback(
                output_path,
                scene_number,
                width,
                height
            )


        if not self.api_key:

            logger.warning(
                "⚠️ POLLINATIONS_API_KEY is missing."
            )

            return self._create_local_fallback(
                output_path,
                scene_number,
                width,
                height
            )


        payload = {
            "prompt": prompt,
            "model": self.model,
            "size": f"{width}x{height}",
            "n": 1,
            "response_format": "b64_json"
        }

        try:

            response = requests.post(
                POLLINATIONS_IMAGE_URL,
                headers={
                    **self._headers(),
                    "Content-Type":
                        "application/json"
                },
                json=payload,
                timeout=180
            )

            if response.status_code != 200:

                logger.error(
                    f"❌ Pollinations HTTP "
                    f"{response.status_code}: "
                    f"{response.text[:500]}"
                )

                # -----------------------------------------
                # INSUFFICIENT BALANCE
                # -----------------------------------------

                if response.status_code == 402:

                    logger.warning(
                        "⚠️ Pollinations balance is "
                        "insufficient."
                    )

                    logger.warning(
                        "↩️ Switching permanently to "
                        "the new local Sofia reference "
                        "for this workflow run."
                    )

                    self.pollinations_disabled = True

                    return self._create_local_fallback(
                        output_path,
                        scene_number,
                        width,
                        height
                    )

                return self._create_local_fallback(
                    output_path,
                    scene_number,
                    width,
                    height
                )

            return self._save_response_image(
                response,
                output_path
            )

        except Exception as e:

            logger.error(
                f"❌ Pollinations request failed: {e}"
            )

            return self._create_local_fallback(
                output_path,
                scene_number,
                width,
                height
            )


    # =====================================================
    # REFERENCE IMAGE EDIT
    # =====================================================

    def _generate_reference_image(
        self,
        prompt: str,
        output_path: Path,
        width: int,
        height: int,
        scene_number: int = 0
    ) -> str:

        if self.pollinations_disabled:

            return self._create_local_fallback(
                output_path,
                scene_number,
                width,
                height
            )


        if not SOFIA_REFERENCE.exists():

            logger.warning(
                "⚠️ Sofia reference image does not exist."
            )

            return self._generate_text_image(
                prompt,
                output_path,
                width,
                height,
                scene_number
            )


        if not self.api_key:

            return self._generate_text_image(
                prompt,
                output_path,
                width,
                height,
                scene_number
            )


        try:

            with open(
                SOFIA_REFERENCE,
                "rb"
            ) as image_file:

                files = {
                    "image": (
                        SOFIA_REFERENCE.name,
                        image_file,
                        "image/jpeg"
                    )
                }

                data = {
                    "prompt": prompt,
                    "model": self.model,
                    "size": f"{width}x{height}",
                    "response_format": "b64_json"
                }

                response = requests.post(
                    POLLINATIONS_EDIT_URL,
                    headers={
                        "Authorization":
                            f"Bearer {self.api_key}"
                    },
                    files=files,
                    data=data,
                    timeout=240
                )

            if response.status_code != 200:

                logger.warning(
                    f"⚠️ Reference generation failed "
                    f"with HTTP "
                    f"{response.status_code}."
                )

                logger.warning(
                    response.text[:500]
                )

                # -----------------------------------------
                # INSUFFICIENT BALANCE
                # -----------------------------------------

                if response.status_code == 402:

                    logger.warning(
                        "⚠️ Pollinations balance "
                        "insufficient."
                    )

                    logger.warning(
                        "↩️ Using the new Sofia "
                        "reference image locally."
                    )

                    self.pollinations_disabled = True

                    return self._create_local_fallback(
                        output_path,
                        scene_number,
                        width,
                        height
                    )

                logger.info(
                    "↩️ Falling back to text-to-image."
                )

                return self._generate_text_image(
                    prompt,
                    output_path,
                    width,
                    height,
                    scene_number
                )

            return self._save_response_image(
                response,
                output_path
            )

        except Exception as e:

            logger.warning(
                f"⚠️ Reference generation failed: {e}"
            )

            return self._generate_text_image(
                prompt,
                output_path,
                width,
                height,
                scene_number
            )


    # =====================================================
    # MAIN IMAGE GENERATOR
    # =====================================================

    def generate_image(
        self,
        prompt: str,
        style: str = "realistic",
        width: int = 1920,
        height: int = 1080,
        filename: Optional[str] = None,
        use_reference: bool = True,
        scene_number: int = 0
    ) -> str:

        if not filename:

            filename = (
                f"sofia_scene_"
                f"{int(time.time())}.jpg"
            )

        output_path = (
            self.output_dir /
            filename
        )

        style_text = {

            "realistic":
                "photorealistic cinematic photography, "
                "luxury editorial style, natural skin, "
                "realistic lighting",

            "cinematic":
                "cinematic photography, dramatic lighting, "
                "premium Hollywood-style composition, "
                "realistic skin and natural detail",

            "luxury":
                "ultra-luxury editorial photography, "
                "premium fashion magazine style, "
                "expensive cinematic atmosphere",

            "action":
                "cinematic action movie photography, "
                "dynamic composition, realistic movement",

            "travel":
                "luxury travel photography, cinematic "
                "composition, beautiful natural lighting",

            "technology":
                "futuristic luxury technology photography, "
                "premium cinematic lighting"

        }.get(
            style,
            "photorealistic cinematic photography"
        )

        final_prompt = f"""
{SOFIA_IDENTITY}

{prompt}

Style:

{style_text}

IMPORTANT:

Sofia must remain the main visual character.

Keep Sofia's face and identity consistent with
the supplied reference image.

Do not replace Sofia with another woman.

Do not create a different person.

Sofia should be clearly visible in the frame.

Preserve realistic facial proportions.

Create a polished cinematic frame suitable for
Sofia Luxury Story.

No text.
No captions.
No watermark.
"""

        logger.info(
            "🎨 Generating Sofia scene:"
        )

        logger.info(
            prompt[:150]
        )

        # -------------------------------------------------
        # Reference-image generation
        # -------------------------------------------------

        if (
            use_reference
            and self.api_key
            and SOFIA_REFERENCE.exists()
            and not self.pollinations_disabled
        ):

            result = self._generate_reference_image(
                final_prompt,
                output_path,
                width,
                height,
                scene_number
            )

            if result:

                logger.info(
                    f"✅ Sofia reference scene saved: "
                    f"{result}"
                )

                return result

        # -------------------------------------------------
        # Normal generation / local fallback
        # -------------------------------------------------

        result = self._generate_text_image(
            final_prompt,
            output_path,
            width,
            height,
            scene_number
        )

        if result:

            logger.info(
                f"✅ Sofia scene saved: "
                f"{result}"
            )

        return result


    # =====================================================
    # MULTIPLE SCENES
    # =====================================================

    def generate_scene_images(
        self,
        scenes: List[Dict],
        style: str = "cinematic",
        width: int = 1920,
        height: int = 1080
    ) -> List[str]:

        image_paths = []

        logger.info(
            f"🎬 Generating "
            f"{len(scenes)} Sofia scenes..."
        )

        for index, scene in enumerate(scenes):

            description = scene.get(
                "description",
                scene.get(
                    "text",
                    scene.get(
                        "action",
                        f"Sofia scene {index + 1}"
                    )
                )
            )

            filename = (
                f"scene_{index + 1:03d}.jpg"
            )

            path = self.generate_image(
                prompt=description,
                style=style,
                width=width,
                height=height,
                filename=filename,
                use_reference=True,
                scene_number=index + 1
            )

            if path:

                image_paths.append(path)

            else:

                logger.warning(
                    f"⚠️ Scene {index + 1} "
                    f"could not be generated."
                )

            if index < len(scenes) - 1:

                time.sleep(0.5)

        logger.info(
            f"✅ Generated "
            f"{len(image_paths)}/"
            f"{len(scenes)} Sofia scenes"
        )

        return image_paths


    # =====================================================
    # THUMBNAIL
    # =====================================================

    def generate_thumbnail_bg(
        self,
        topic: str,
        niche: str = "luxury"
    ) -> str:

        prompt = f"""
Luxury cinematic background for a Sofia Luxury Story
thumbnail about:

{topic}

Premium editorial composition.
Elegant lighting.
Luxury technology and lifestyle atmosphere.

No people.
No text.
No watermark.
"""

        filename = (
            "thumbnail_"
            + "".join(
                c if c.isalnum()
                else "_"
                for c in topic[:40]
            )
            + ".jpg"
        )

        return self.generate_image(
            prompt=prompt,
            style="luxury",
            width=1920,
            height=1080,
            filename=filename,
            use_reference=False,
            scene_number=0
        )


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    print(
        "\n=========================================="
    )

    print(
        "SOFIA LUXURY STORY IMAGE GENERATOR TEST"
    )

    print(
        "==========================================\n"
    )

    generator = AIImageGenerator()

    result = generator.generate_image(
        prompt=(
            "Sofia standing confidently in a "
            "luxurious modern penthouse overlooking "
            "a futuristic city at night. "
            "Her face is clearly visible. "
            "Full-body cinematic composition."
        ),
        style="cinematic",
        width=720,
        height=1280,
        filename="sofia_test.jpg",
        use_reference=True,
        scene_number=1
    )

    if result:

        print(
            f"✅ Test image created: {result}"
        )

    else:

        print(
            "❌ Test image generation failed."
        )
