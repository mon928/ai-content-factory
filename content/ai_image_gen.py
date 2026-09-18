"""
SOFIA LUXURY STORY
AI IMAGE GENERATOR

Generates cinematic Sofia visuals using Pollinations.
Sofia remains the central visual character.
"""

import os
import time
import base64
from pathlib import Path
from io import BytesIO
from typing import List, Dict, Optional

import requests
from loguru import logger
from PIL import Image


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

DEFAULT_MODEL = (
    "black-forest-labs/flux.1-kontext-pro"
)


SOFIA_IDENTITY = """
Sofia is the central character of Sofia Luxury Story.
Keep Sofia visually consistent with the supplied reference image.
Preserve her recognizable facial identity, hairstyle, skin tone,
age appearance and overall elegant appearance.

Sofia should look like the same woman throughout the story.

She can appear in different locations, clothing, environments,
luxury settings, technology scenes, travel scenes and action
scenes, but her identity must remain consistent.
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
    # SAVE IMAGE
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
                or response.content[:8] == b"\x89PNG\r\n\x1a\n"
                or response.content[:2] == b"\xff\xd8"
            ):

                image = Image.open(
                    BytesIO(response.content)
                )

                image.convert("RGB").save(
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
                                    BytesIO(image_bytes)
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
    # TEXT-TO-IMAGE
    # =====================================================

    def _generate_text_image(
        self,
        prompt: str,
        output_path: Path,
        width: int,
        height: int
    ) -> str:

        if not self.api_key:

            logger.warning(
                "⚠️ POLLINATIONS_API_KEY is missing."
            )

        payload = {
            "prompt": prompt,
            "model": self.model,
            "size": f"{width}x{height}",
            "n": 1,
            "response_format": "b64_json"
        }

        response = requests.post(
            POLLINATIONS_IMAGE_URL,
            headers={
                **self._headers(),
                "Content-Type": "application/json"
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

            return ""

        return self._save_response_image(
            response,
            output_path
        )


    # =====================================================
    # REFERENCE IMAGE EDIT
    # =====================================================

    def _generate_reference_image(
        self,
        prompt: str,
        output_path: Path,
        width: int,
        height: int
    ) -> str:

        if not SOFIA_REFERENCE.exists():

            logger.warning(
                "⚠️ Sofia reference image does not exist."
            )

            return self._generate_text_image(
                prompt,
                output_path,
                width,
                height
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
                    f"with HTTP {response.status_code}."
                )

                logger.warning(
                    response.text[:500]
                )

                logger.info(
                    "↩️ Falling back to text-to-image."
                )

                return self._generate_text_image(
                    prompt,
                    output_path,
                    width,
                    height
                )

            return self._save_response_image(
                response,
                output_path
            )

        except Exception as e:

            logger.warning(
                f"⚠️ Reference image generation "
                f"failed: {e}"
            )

            logger.info(
                "↩️ Falling back to text-to-image."
            )

            return self._generate_text_image(
                prompt,
                output_path,
                width,
                height
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
        use_reference: bool = True
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
No text, no captions, no watermark.
"""


        logger.info(
            f"🎨 Generating Sofia scene: "
            f"{prompt[:100]}"
        )


        # Reference-image generation
        if (
            use_reference
            and self.api_key
            and SOFIA_REFERENCE.exists()
        ):

            result = self._generate_reference_image(
                final_prompt,
                output_path,
                width,
                height
            )

            if result:

                logger.info(
                    f"✅ Sofia reference scene saved: "
                    f"{result}"
                )

                return result


        # Normal generation fallback
        result = self._generate_text_image(
            final_prompt,
            output_path,
            width,
            height
        )

        if result:

            logger.info(
                f"✅ Sofia scene saved: {result}"
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
                use_reference=True
            )

            if path:

                image_paths.append(path)

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
                c if c.isalnum() else "_"
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
            use_reference=False
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
        use_reference=True
    )

    if result:

        print(
            f"✅ Test image created: {result}"
        )

    else:

        print(
            "❌ Test image generation failed."
        )
