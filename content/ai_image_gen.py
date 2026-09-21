"""
SOFIA LUXURY STORY
AI IMAGE GENERATOR

Generation order:
1. Pollinations
2. Gemini 3.1 Flash Image using Sofia reference
3. Local Sofia reference fallback

The Gemini fallback is used when Pollinations has no balance,
fails, or is unavailable.

Designed for GitHub Actions.
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
# PROJECT SETTINGS
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

SOFIA_REFERENCE = (
    PROJECT_ROOT
    / "assets"
    / "sofia"
    / "sofia_reference.jpg"
)

POLLINATIONS_API_KEY = os.getenv(
    "POLLINATIONS_API_KEY"
)

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)

POLLINATIONS_IMAGE_URL = (
    "https://gen.pollinations.ai/v1/images/generations"
)

POLLINATIONS_EDIT_URL = (
    "https://gen.pollinations.ai/v1/images/edits"
)

GEMINI_INTERACTIONS_URL = (
    "https://generativelanguage.googleapis.com/v1beta/interactions"
)

DEFAULT_POLLINATIONS_MODEL = (
    "black-forest-labs/flux.1-schnell"
)

DEFAULT_GEMINI_MODEL = (
    "gemini-3.1-flash-image"
)


# =========================================================
# SOFIA IDENTITY
# =========================================================

SOFIA_IDENTITY = """
Sofia is the central character of Sofia Luxury Story.

Use the supplied Sofia reference image as the identity reference.

Preserve Sofia's recognizable facial identity, facial structure,
skin tone, hairstyle, age appearance and overall recognizable look.

She must look like the SAME WOMAN from the supplied reference.

The reference image is an IDENTITY reference, NOT a background
or pose reference.

Sofia must be allowed to appear in completely different:
- locations
- poses
- camera angles
- outfits
- activities
- lighting
- environments
- luxury settings

Do NOT simply reproduce the original photograph.

Do NOT copy the original bathroom.
Do NOT copy the original mountain background.
Do NOT copy the original pose.
Do NOT copy the original composition.

Create a genuinely new photograph while preserving Sofia's identity.
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

        self.pollinations_model = os.getenv(
            "POLLINATIONS_IMAGE_MODEL",
            DEFAULT_POLLINATIONS_MODEL
        )

        self.gemini_model = os.getenv(
            "GEMINI_IMAGE_MODEL",
            DEFAULT_GEMINI_MODEL
        )

        self.pollinations_api_key = (
            os.getenv("POLLINATIONS_API_KEY")
            or POLLINATIONS_API_KEY
        )

        self.gemini_api_key = (
            os.getenv("GEMINI_API_KEY")
            or GEMINI_API_KEY
        )

        self.pollinations_disabled = False

        self.gemini_disabled = False

        logger.info(
            "🎨 Sofia AI Image Generator initialized"
        )

        logger.info(
            f"Pollinations model: "
            f"{self.pollinations_model}"
        )

        logger.info(
            f"Gemini model: "
            f"{self.gemini_model}"
        )

        if SOFIA_REFERENCE.exists():
            logger.info(
                "✅ Sofia reference found: "
                f"{SOFIA_REFERENCE}"
            )
        else:
            logger.warning(
                "⚠️ Sofia reference NOT found: "
                f"{SOFIA_REFERENCE}"
            )

        if self.gemini_api_key:
            logger.info(
                "✅ Gemini API key detected."
            )
        else:
            logger.warning(
                "⚠️ GEMINI_API_KEY is not available."
            )


    # =====================================================
    # POLLINATIONS HEADERS
    # =====================================================

    def _pollinations_headers(self) -> dict:

        headers = {
            "Accept": (
                "application/json, "
                "image/jpeg, "
                "image/png"
            )
        }

        if self.pollinations_api_key:
            headers["Authorization"] = (
                "Bearer "
                + self.pollinations_api_key
            )

        return headers


    # =====================================================
    # FIT IMAGE TO REQUESTED SIZE
    # =====================================================

    def _fit_image(
        self,
        image: Image.Image,
        width: int,
        height: int
    ) -> Image.Image:

        image = image.convert("RGB")

        target_ratio = (
            width / height
        )

        source_ratio = (
            image.width / image.height
        )

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

        return image.resize(
            (width, height),
            Image.Resampling.LANCZOS
        )


    # =====================================================
    # LOCAL FALLBACK
    # =====================================================

    def _create_local_fallback(
        self,
        output_path: Path,
        width: int,
        height: int,
        scene_number: int = 0
    ) -> str:

        if not SOFIA_REFERENCE.exists():

            logger.error(
                "❌ Sofia reference does not exist."
            )

            return ""

        try:

            image = Image.open(
                SOFIA_REFERENCE
            ).convert("RGB")

            image = self._fit_image(
                image,
                width,
                height
            )

            variation = (
                scene_number % 6
            )

            if variation == 1:

                image = ImageEnhance.Brightness(
                    image
                ).enhance(1.06)

            elif variation == 2:

                image = ImageEnhance.Contrast(
                    image
                ).enhance(1.08)

            elif variation == 3:

                image = ImageEnhance.Color(
                    image
                ).enhance(1.06)

            elif variation == 4:

                image = image.filter(
                    ImageFilter.SMOOTH
                )

            elif variation == 5:

                image = ImageEnhance.Sharpness(
                    image
                ).enhance(1.15)

            image.save(
                output_path,
                "JPEG",
                quality=95
            )

            logger.warning(
                "⚠️ Local Sofia fallback created: "
                f"{output_path}"
            )

            return str(output_path)

        except Exception as e:

            logger.error(
                "❌ Local fallback failed: "
                f"{e}"
            )

            return ""


    # =====================================================
    # SAVE POLLINATIONS RESPONSE
    # =====================================================

    def _save_pollinations_response(
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

            if (
                content_type.startswith("image/")
                or response.content[:8]
                == b"\x89PNG\r\n\x1a\n"
                or response.content[:2]
                == b"\xff\xd8"
            ):

                image = Image.open(
                    BytesIO(response.content)
                ).convert("RGB")

                image.save(
                    output_path,
                    "JPEG",
                    quality=95
                )

                return str(output_path)

            data = response.json()

            image_url = None

            if isinstance(data, dict):

                items = data.get("data")

                if (
                    isinstance(items, list)
                    and items
                ):

                    first = items[0]

                    if isinstance(first, dict):

                        image_url = first.get(
                            "url"
                        )

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
                            ).convert("RGB")

                            image.save(
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
                    timeout=90
                )

                image_response.raise_for_status()

                image = Image.open(
                    BytesIO(
                        image_response.content
                    )
                ).convert("RGB")

                image.save(
                    output_path,
                    "JPEG",
                    quality=95
                )

                return str(output_path)

            logger.error(
                "❌ Pollinations returned "
                "no usable image."
            )

            return ""

        except Exception as e:

            logger.error(
                "❌ Could not save Pollinations "
                f"image: {e}"
            )

            return ""


    # =====================================================
    # POLLINATIONS TEXT IMAGE
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
            return ""

        if not self.pollinations_api_key:

            logger.warning(
                "⚠️ POLLINATIONS_API_KEY missing."
            )

            return ""

        payload = {
            "prompt": prompt,
            "model": self.pollinations_model,
            "size": f"{width}x{height}",
            "n": 1,
            "response_format": "b64_json"
        }

        try:

            response = requests.post(
                POLLINATIONS_IMAGE_URL,
                headers={
                    **self._pollinations_headers(),
                    "Content-Type":
                        "application/json"
                },
                json=payload,
                timeout=180
            )

            if response.status_code != 200:

                logger.warning(
                    "⚠️ Pollinations HTTP "
                    f"{response.status_code}: "
                    f"{response.text[:400]}"
                )

                if response.status_code == 402:

                    logger.warning(
                        "⚠️ Pollinations balance "
                        "is insufficient."
                    )

                    self.pollinations_disabled = True

                return ""

            return self._save_pollinations_response(
                response,
                output_path
            )

        except Exception as e:

            logger.warning(
                "⚠️ Pollinations request failed: "
                f"{e}"
            )

            return ""


    # =====================================================
    # POLLINATIONS REFERENCE EDIT
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
            return ""

        if not self.pollinations_api_key:
            return ""

        if not SOFIA_REFERENCE.exists():
            return ""

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
                    "model":
                        self.pollinations_model,
                    "size":
                        f"{width}x{height}",
                    "response_format":
                        "b64_json"
                }

                response = requests.post(
                    POLLINATIONS_EDIT_URL,
                    headers={
                        "Authorization":
                            "Bearer "
                            + self.pollinations_api_key
                    },
                    files=files,
                    data=data,
                    timeout=240
                )

            if response.status_code != 200:

                logger.warning(
                    "⚠️ Pollinations reference "
                    "edit HTTP "
                    f"{response.status_code}: "
                    f"{response.text[:400]}"
                )

                if response.status_code == 402:

                    self.pollinations_disabled = True

                return ""

            return self._save_pollinations_response(
                response,
                output_path
            )

        except Exception as e:

            logger.warning(
                "⚠️ Pollinations reference "
                f"generation failed: {e}"
            )

            return ""


    # =====================================================
    # GEMINI REFERENCE IMAGE
    # =====================================================

    def _generate_gemini_reference_image(
        self,
        prompt: str,
        output_path: Path,
        width: int,
        height: int,
        scene_number: int = 0
    ) -> str:

        if self.gemini_disabled:
            return ""

        if not self.gemini_api_key:

            logger.warning(
                "⚠️ GEMINI_API_KEY is missing."
            )

            return ""

        if not SOFIA_REFERENCE.exists():

            logger.warning(
                "⚠️ Sofia reference image "
                "does not exist."
            )

            return ""

        try:

            with open(
                SOFIA_REFERENCE,
                "rb"
            ) as f:

                reference_bytes = f.read()

            reference_b64 = (
                base64.b64encode(
                    reference_bytes
                ).decode("utf-8")
            )

            aspect_ratio = (
                "9:16"
                if height > width
                else "16:9"
            )

            scene_variation = [
                "Use a medium full-body composition.",
                "Use a three-quarter camera angle.",
                "Use a low cinematic camera angle.",
                "Use a slightly elevated camera angle.",
                "Use a candid walking composition.",
                "Use a dramatic editorial portrait composition.",
                "Use a wide environmental composition.",
                "Use a close cinematic fashion composition."
            ]

            variation = scene_variation[
                scene_number
                % len(scene_variation)
            ]

            gemini_prompt = f"""
Create a completely NEW photorealistic cinematic
photograph for Sofia Luxury Story.

{SOFIA_IDENTITY}

SCENE:
{prompt}

CAMERA:
{variation}

IMPORTANT VISUAL REQUIREMENTS:

1. Sofia must remain the same recognizable woman
   from the supplied reference image.

2. Preserve her facial identity.

3. Change the environment completely according
   to the scene description.

4. Change the pose according to the scene.

5. Change the camera angle according to the scene.

6. Change the composition.

7. Change the lighting when appropriate.

8. Change her outfit when the story requires it.

9. Do NOT reproduce the bathroom from the reference.

10. Do NOT reproduce the mountain background
    from the reference.

11. Do NOT reproduce the exact original pose.

12. Do NOT simply crop, zoom, recolor, or duplicate
    the supplied photograph.

13. The result must look like a newly photographed
    scene from Sofia's story.

14. Sofia should be naturally integrated into
    the new environment.

15. Photorealistic skin and realistic human anatomy.

16. Premium luxury editorial photography.

17. Cinematic lighting.

18. Natural proportions.

19. No text.

20. No captions.

21. No logos.

22. No watermark added by the prompt.

The supplied image is only for Sofia's identity.
Generate a new scene.
"""

            payload = {
                "model": self.gemini_model,

                "input": [
                    {
                        "type": "text",
                        "text": gemini_prompt
                    },
                    {
                        "type": "image",
                        "mime_type": "image/jpeg",
                        "data": reference_b64
                    }
                ],

                "response_format": {
                    "type": "image",
                    "mime_type": "image/jpeg",
                    "aspect_ratio": aspect_ratio,
                    "image_size": "1K"
                }
            }

            logger.info(
                "🤖 Generating NEW Sofia scene "
                "with Gemini..."
            )

            response = requests.post(
                GEMINI_INTERACTIONS_URL,
                headers={
                    "x-goog-api-key":
                        self.gemini_api_key,
                    "Content-Type":
                        "application/json"
                },
                json=payload,
                timeout=300
            )

            if response.status_code != 200:

                logger.warning(
                    "⚠️ Gemini HTTP "
                    f"{response.status_code}: "
                    f"{response.text[:800]}"
                )

                return ""

            data = response.json()

            image_b64 = (
                self._find_image_base64(
                    data
                )
            )

            if not image_b64:

                logger.warning(
                    "⚠️ Gemini response did not "
                    "contain image data."
                )

                return ""

            image_bytes = (
                base64.b64decode(
                    image_b64
                )
            )

            image = Image.open(
                BytesIO(image_bytes)
            ).convert("RGB")

            image = self._fit_image(
                image,
                width,
                height
            )

            image.save(
                output_path,
                "JPEG",
                quality=95
            )

            logger.info(
                "✅ NEW Gemini Sofia scene saved: "
                f"{output_path}"
            )

            return str(output_path)

        except Exception as e:

            logger.warning(
                "⚠️ Gemini image generation "
                f"failed: {e}"
            )

            return ""


    # =====================================================
    # FIND IMAGE DATA INSIDE GEMINI RESPONSE
    # =====================================================

    def _find_image_base64(
        self,
        value
    ) -> Optional[str]:

        if isinstance(value, dict):

            # Direct output_image format
            output_image = value.get(
                "output_image"
            )

            if isinstance(
                output_image,
                dict
            ):

                data = output_image.get(
                    "data"
                )

                if isinstance(
                    data,
                    str
                ) and data:

                    return data

            # Generic image object
            if (
                value.get("type") == "image"
                and isinstance(
                    value.get("data"),
                    str
                )
            ):

                return value["data"]

            for key, item in value.items():

                # Avoid recursively scanning
                # enormous metadata fields.
                if key in {
                    "text",
                    "search_suggestions"
                }:
                    continue

                result = (
                    self._find_image_base64(
                        item
                    )
                )

                if result:
                    return result

        elif isinstance(value, list):

            for item in value:

                result = (
                    self._find_image_base64(
                        item
                    )
                )

                if result:
                    return result

        return None


    # =====================================================
    # GEMINI TEXT-TO-IMAGE
    # =====================================================

    def _generate_gemini_text_image(
        self,
        prompt: str,
        output_path: Path,
        width: int,
        height: int,
        scene_number: int = 0
    ) -> str:

        if self.gemini_disabled:
            return ""

        if not self.gemini_api_key:
            return ""

        try:

            aspect_ratio = (
                "9:16"
                if height > width
                else "16:9"
            )

            payload = {

                "model":
                    self.gemini_model,

                "input": [
                    {
                        "type": "text",
                        "text": prompt
                    }
                ],

                "response_format": {
                    "type": "image",
                    "mime_type": "image/jpeg",
                    "aspect_ratio":
                        aspect_ratio,
                    "image_size": "1K"
                }
            }

            response = requests.post(
                GEMINI_INTERACTIONS_URL,
                headers={
                    "x-goog-api-key":
                        self.gemini_api_key,
                    "Content-Type":
                        "application/json"
                },
                json=payload,
                timeout=300
            )

            if response.status_code != 200:

                logger.warning(
                    "⚠️ Gemini text image HTTP "
                    f"{response.status_code}: "
                    f"{response.text[:600]}"
                )

                return ""

            data = response.json()

            image_b64 = (
                self._find_image_base64(
                    data
                )
            )

            if not image_b64:
                return ""

            image_bytes = (
                base64.b64decode(
                    image_b64
                )
            )

            image = Image.open(
                BytesIO(image_bytes)
            ).convert("RGB")

            image = self._fit_image(
                image,
                width,
                height
            )

            image.save(
                output_path,
                "JPEG",
                quality=95
            )

            logger.info(
                "✅ Gemini image saved: "
                f"{output_path}"
            )

            return str(output_path)

        except Exception as e:

            logger.warning(
                "⚠️ Gemini text generation "
                f"failed: {e}"
            )

            return ""


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
                "sofia_scene_"
                + str(int(time.time()))
                + ".jpg"
            )

        output_path = (
            self.output_dir
            / filename
        )

        style_text = {

            "realistic":
                "photorealistic cinematic photography, "
                "luxury editorial style, natural skin, "
                "realistic lighting",

            "cinematic":
                "cinematic photography, dramatic lighting, "
                "premium film composition, realistic",

            "luxury":
                "ultra-luxury editorial photography, "
                "premium fashion magazine style",

            "action":
                "cinematic action photography, "
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

STORY SCENE:
{prompt}

VISUAL STYLE:
{style_text}

The image must be a NEW scene.

Sofia remains the main visual character.

Use the reference image ONLY to preserve
Sofia's identity.

The location, pose, composition,
camera angle and lighting must be based
on the story scene rather than the reference.

No text.
No captions.
No logos.
"""


        logger.info(
            "🎨 Generating Sofia scene "
            f"{scene_number}: "
            f"{prompt[:120]}"
        )


        # =================================================
        # 1. TRY POLLINATIONS REFERENCE EDIT
        # =================================================

        if (
            use_reference
            and not self.pollinations_disabled
            and self.pollinations_api_key
            and SOFIA_REFERENCE.exists()
        ):

            result = (
                self._generate_reference_image(
                    final_prompt,
                    output_path,
                    width,
                    height,
                    scene_number
                )
            )

            if result:

                logger.info(
                    "✅ Pollinations generated "
                    "Sofia scene."
                )

                return result


        # =================================================
        # 2. TRY POLLINATIONS TEXT GENERATION
        # =================================================

        if (
            not self.pollinations_disabled
            and self.pollinations_api_key
        ):

            result = (
                self._generate_text_image(
                    final_prompt,
                    output_path,
                    width,
                    height,
                    scene_number
                )
            )

            if result:

                logger.info(
                    "✅ Pollinations generated "
                    "text-based scene."
                )

                return result


        # =================================================
        # 3. GEMINI REFERENCE GENERATION
        # =================================================

        if (
            use_reference
            and not self.gemini_disabled
            and self.gemini_api_key
            and SOFIA_REFERENCE.exists()
        ):

            logger.info(
                "🔄 Pollinations unavailable."
            )

            logger.info(
                "🤖 Switching to Gemini "
                "for a NEW Sofia scene."
            )

            result = (
                self._generate_gemini_reference_image(
                    final_prompt,
                    output_path,
                    width,
                    height,
                    scene_number
                )
            )

            if result:

                return result


        # =================================================
        # 4. GEMINI TEXT GENERATION
        # =================================================

        if (
            not self.gemini_disabled
            and self.gemini_api_key
        ):

            logger.info(
                "🤖 Trying Gemini text-to-image."
            )

            result = (
                self._generate_gemini_text_image(
                    final_prompt,
                    output_path,
                    width,
                    height,
                    scene_number
                )
            )

            if result:

                return result


        # =================================================
        # 5. LAST RESORT LOCAL FALLBACK
        # =================================================

        logger.warning(
            "⚠️ All AI image generation "
            "methods failed."
        )

        return self._create_local_fallback(
            output_path,
            width,
            height,
            scene_number
        )


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

        for index, scene in enumerate(
            scenes
        ):

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

                image_paths.append(
                    path
                )

            else:

                logger.warning(
                    f"⚠️ Scene {index + 1} "
                    "could not be generated."
                )

            if index < len(scenes) - 1:

                time.sleep(1)

        logger.info(
            "✅ Generated "
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
Create a premium cinematic luxury thumbnail
background for a Sofia Luxury Story.

Topic:
{topic}

Niche:
{niche}

Create a visually striking luxury environment
with premium architecture, technology,
fashion or lifestyle elements related to the topic.

High contrast.
Cinematic lighting.
Premium editorial photography.

No people.
No Sofia.
No text.
No captions.
No watermark.
"""

        safe_topic = "".join(
            c if c.isalnum()
            else "_"
            for c in topic[:40]
        )

        filename = (
            "thumbnail_"
            + safe_topic
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
            "Sofia walking through an ultra-modern "
            "luxury penthouse overlooking a futuristic "
            "city at sunset, wearing an elegant "
            "high-fashion outfit, cinematic editorial "
            "photography, confident natural pose"
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
