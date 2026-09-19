"""
SOFIA LUXURY STORY
AI IMAGE GENERATOR

Generates cinematic Sofia visuals using Pollinations.
Includes graceful fallback when Pollinations has insufficient balance.
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
# SOFIA SETTINGS
# =========================================================

SOFIA_REFERENCE = Path(
    "assets/sofia/IMG-20260918-WA0009.jpg"
)

POLLINATIONS_API_KEY = os.getenv(
    "POLLINATIONS_API_KEY"
)

POLLINATIONS_IMAGE_URL = (
    "https://gen.pollinations.ai/v1/images/generations"
)

POLLINATIONS_EDIT_URL = (
    "https://gen.pollinations.ai/v1/images/edits"
)

# Use a lower-cost model by default.
# It can still be overridden with POLLINATIONS_IMAGE_MODEL.
DEFAULT_MODEL = (
    "black-forest-labs/flux.1-schnell"
)

SOFIA_IDENTITY = """
Sofia is the central character of Sofia Luxury Story.

Keep Sofia visually consistent with the supplied reference image.

Preserve her recognizable facial identity, hairstyle,
skin tone, age appearance and elegant overall appearance.

Sofia should look like the same woman throughout the story.

She can appear in different locations, clothing,
luxury settings, technology scenes, travel scenes
and action scenes, but her identity must remain consistent.
"""


# =========================================================
# AI IMAGE GENERATOR
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
            f"Model: {self.model}"
        )

        if SOFIA_REFERENCE.exists():

            logger.info(
                f"✅ Sofia reference found: "
                f"{SOFIA_REFERENCE}"
            )

        else:

            logger.warning(
                f"⚠️ Sofia reference not found: "
                f"{SOFIA_REFERENCE}"
            )


    # =====================================================
    # HEADERS
    # =====================================================

    def _headers(self) -> dict:

        headers = {
            "Accept": "application/json, image/jpeg, image/png"
        }

        if self.api_key:

            headers["Authorization"] = (
                f"Bearer {self.api_key}"
            )

        return headers


    # =====================================================
    # LOCAL SOFIA FALLBACK
    # =====================================================

    def _create_local_fallback(
        self,
        output_path: Path,
        scene_number: int = 0
    ) -> str:

        """
        Creates a local fallback image from the Sofia
        reference image when Pollinations cannot generate
        an image because of insufficient balance or API errors.

        This allows the video pipeline to continue instead
        of terminating the entire GitHub Action.
        """

        if not SOFIA_REFERENCE.exists():

            logger.error(
                "❌ No Sofia reference available for fallback."
            )

            return ""

        try:

            image = Image.open(
                SOFIA_REFERENCE
            ).convert("RGB")

            width = 1920
            height = 1080

            # -------------------------------------------------
            # Cover crop to 16:9
            # -------------------------------------------------

            source_ratio = image.width / image.height
            target_ratio = width / height

            if source_ratio > target_ratio:

                new_width = int(
                    image.height * target_ratio
                )

                left = (
                    image.width - new_width
                ) // 2

                image = image.crop(
                    (
                        left,
                        0,
                        left + new_width,
                        image.height
                    )
                )

            else:

                new_height = int(
                    image.width / target_ratio
                )

                top = (
                    image.height - new_height
                ) // 2

                image = image.crop(
                    (
                        0,
                        top,
                        image.width,
                        top + new_height
                    )
                )

            image = image.resize(
                (width, height),
                Image.Resampling.LANCZOS
            )

            # -------------------------------------------------
            # Create small visual variations between scenes
            # -------------------------------------------------

            variation = scene_number % 6

            if variation == 1:

                image = ImageEnhance.Brightness(
                    image
                ).enhance(1.08)

            elif variation == 2:

                image = ImageEnhance.Contrast(
                    image
                ).enhance(1.10)

            elif variation == 3:

                image = ImageEnhance.Color(
                    image
                ).enhance(1.08)

            elif variation == 4:

                image = image.filter(
                    ImageFilter.SMOOTH
                )

            elif variation == 5:

                image = ImageEnhance.Sharpness(
                    image
                ).enhance(1.20)

            image.save(
                output_path,
                "JPEG",
                quality=95
            )

            logger.warning(
                f"⚠️ Local Sofia fallback created: "
                f"{output_path}"
            )

            return str(output_path)

        except Exception as e:

            logger.error(
                f"❌ Local fallback failed: {e}"
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

            # ---------------------------------------------
            # DIRECT IMAGE RESPONSE
            # ---------------------------------------------

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


            # ---------------------------------------------
            # JSON RESPONSE
            # ---------------------------------------------

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
                scene_number
            )


        if not self.api_key:

            logger.warning(
                "⚠️ POLLINATIONS_API_KEY is missing."
            )

            return self._create_local_fallback(
                output_path,
                scene_number
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
                        "↩️ Switching to local Sofia "
                        "fallback so video creation "
                        "can continue."
                    )

                    self.pollinations_disabled = True

                    return self._create_local_fallback(
                        output_path,
                        scene_number
                    )


                return self._create_local_fallback(
                    output_path,
                    scene_number
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
                scene_number
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
                scene_number
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
                        "↩️ Switching to local Sofia "
                        "fallback."
                    )

                    self.pollinations_disabled = True

                    return self._create_local_fallback(
                        output_path,
                        scene_number
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
                f"⚠️ Reference generation "
                f"failed: {e}"
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
                "Hollywood-style composition, realistic",

            "luxury":
                "ultra-luxury editorial photography, "
                "premium fashion magazine style",

            "action":
                "cinematic action movie photography, "
                "dynamic composition, realistic motion",

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

Keep her appearance consistent with the reference image.

Do not replace Sofia with another woman.

Do not change her identity.

Create a polished cinematic frame suitable for
Sofia Luxury Story.

No text.
No captions.
No watermark.
"""


        logger.info(
            f"🎨 Generating Sofia scene: "
            f"{prompt[:100]}"
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
        # Normal generation fallback
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
                    f"Sofia scene {index + 1}"
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

                time.sleep(1)


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
High contrast.
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
            "Sofia standing in a luxurious modern "
            "penthouse overlooking a futuristic city "
            "at night"
        ),
        style="cinematic",
        width=1920,
        height=1080,
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
