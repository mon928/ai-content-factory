"""
🎨 SOFIA LUXURY STORY - AI IMAGE GENERATOR

Uses Pollinations AI with Sofia's reference photo.

Main purpose:
- Keep Sofia visually consistent across story scenes
- Support realistic, cinematic, action, luxury and adventure scenes
- Use Sofia reference image for story visuals
- Use Pollinations image-to-image/reference-image generation
- Keep thumbnail/background generation independent from Sofia
"""

import os
import time
from pathlib import Path
from io import BytesIO
from typing import List, Dict, Optional

import requests
from loguru import logger
from PIL import Image


class AIImageGenerator:
    """Generate Sofia Luxury Story visuals using Pollinations AI."""

    STYLES = {
        "realistic": (
            "photorealistic cinematic photography, natural skin texture, "
            "realistic lighting, highly detailed, professional film still"
        ),
        "cinematic": (
            "cinematic film still, dramatic lighting, realistic photography, "
            "high detail, professional movie production"
        ),
        "luxury": (
            "ultra realistic luxury editorial photography, elegant lighting, "
            "premium fashion magazine quality, cinematic composition"
        ),
        "action": (
            "cinematic action movie still, dynamic composition, dramatic lighting, "
            "realistic motion, high detail, professional film production"
        ),
        "adventure": (
            "cinematic adventure movie still, dramatic environment, realistic "
            "lighting, epic composition, professional photography"
        ),
        "cartoon": (
            "high quality animated cinematic style, vibrant colors, detailed "
            "character design, polished animation"
        ),
        "anime": (
            "high quality anime cinematic style, detailed character design, "
            "dramatic lighting, professional animation"
        ),
        "3d": (
            "high quality 3D cinematic render, realistic materials, dramatic "
            "lighting, professional film quality"
        ),
        "sketch": (
            "professional pencil sketch, detailed hand drawn artwork, artistic"
        ),
        "watercolor": (
            "professional watercolor painting, detailed artistic composition"
        ),
        "minimal": (
            "clean minimalist professional visual, elegant composition"
        ),
        "cyberpunk": (
            "cinematic cyberpunk environment, neon lighting, futuristic city, "
            "high detail, professional movie still"
        ),
    }

    SOFIA_REFERENCE = "assets/sofia/IMG-20260918-WA0009.jpg"

    SOFIA_IDENTITY = """
Sofia is the central character of Sofia Luxury Story.

Use the supplied Sofia reference image as the identity reference.

Preserve Sofia's recognizable facial identity, facial proportions,
skin appearance, hair characteristics and overall natural appearance.

Sofia must remain the same woman from scene to scene.

Clothing, hairstyle details, pose, expression, environment and action
may change to match the story.

Do not replace Sofia with another woman.
Do not create a different face.
Do not turn Sofia into a generic model.

When the story is action, adventure, technology, luxury, travel,
romance or another genre, Sofia remains the central character.
"""

    def __init__(
        self,
        output_dir: str = "output/images",
        reference_image_path: Optional[str] = None,
    ):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.api_key = os.getenv("POLLINATIONS_API_KEY", "").strip()

        self.reference_image_path = Path(
            reference_image_path or self.SOFIA_REFERENCE
        )

        self.api_url = "https://gen.pollinations.ai/v1/images/edits"

        self.model = os.getenv(
            "POLLINATIONS_IMAGE_MODEL",
            "black-forest-labs/flux.1-kontext-pro",
        )

        if not self.api_key:
            logger.warning(
                "⚠️ POLLINATIONS_API_KEY is not set."
            )

        if not self.reference_image_path.exists():
            logger.warning(
                f"⚠️ Sofia reference image not found: "
                f"{self.reference_image_path}"
            )

    # ---------------------------------------------------------
    # HELPERS
    # ---------------------------------------------------------

    def _get_reference_path(
        self,
        reference_image_path: Optional[str] = None,
    ) -> Optional[Path]:

        path = Path(
            reference_image_path
            or self.reference_image_path
        )

        if path.exists():
            return path

        logger.warning(
            f"⚠️ Reference image not found: {path}"
        )

        return None

    def _build_prompt(
        self,
        prompt: str,
        style: str,
        use_reference: bool,
    ) -> str:

        style_prompt = self.STYLES.get(
            style,
            self.STYLES["realistic"]
        )

        if use_reference:
            return f"""
{self.SOFIA_IDENTITY}

SCENE:
{prompt}

VISUAL STYLE:
{style_prompt}

IMPORTANT:
Sofia must be clearly visible and remain the central subject.

Create a single polished cinematic image.
Preserve Sofia's identity from the reference image.
Change the environment, clothing, pose and action to fit the scene.
Keep the result photorealistic unless another style is explicitly requested.
No text, captions, logos, watermarks or duplicate people.
"""

        return f"""
SCENE:
{prompt}

VISUAL STYLE:
{style_prompt}

Create a polished professional cinematic image.
No text, captions, logos or watermarks.
"""

    # ---------------------------------------------------------
    # MAIN IMAGE GENERATOR
    # ---------------------------------------------------------

    def generate_image(
        self,
        prompt: str,
        style: str = "realistic",
        width: int = 1280,
        height: int = 720,
        filename: Optional[str] = None,
        use_reference: bool = True,
        reference_image_path: Optional[str] = None,
    ) -> str:
        """
        Generate one image.

        When use_reference=True, Sofia's reference photo is supplied
        to Pollinations so the generated image can maintain her identity.
        """

        if not self.api_key:
            logger.error(
                "❌ POLLINATIONS_API_KEY is missing."
            )
            return ""

        reference_path = None

        if use_reference:
            reference_path = self._get_reference_path(
                reference_image_path
            )

            if reference_path is None:
                logger.error(
                    "❌ Sofia reference image is required "
                    "but could not be found."
                )
                return ""

        full_prompt = self._build_prompt(
            prompt=prompt,
            style=style,
            use_reference=use_reference,
        )

        if filename is None:
            safe_name = (
                prompt[:50]
                .replace(" ", "_")
                .replace("/", "_")
                .replace("\\", "_")
            )
            filename = f"{safe_name}.jpg"

        output_path = self.output_dir / filename
        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        logger.info(
            f"🎨 Generating image: {prompt[:80]}..."
        )

        if use_reference:
            logger.info(
                f"👩 Sofia reference: {reference_path}"
            )

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
                        data = {
                "prompt": full_prompt,
                "model": self.model,
                "size": f"{width}x{height}",
                "response_format": "url",
            }

            files = None
            reference_file = None

            if reference_path:
                reference_file = open(
                    reference_path,
                    "rb"
                )

                files = {
                    "image": (
                        reference_path.name,
                        reference_file,
                        "image/jpeg",
                    )
                }

            try:
                response = requests.post(
                    self.api_url,
                    headers=headers,
                    data=data,
                    files=files,
                    timeout=300,
                )
            finally:
                if reference_file:
                    reference_file.close()

            if response.status_code != 200:
                logger.error(
                    f"❌ Pollinations error "
                    f"{response.status_code}: "
                    f"{response.text[:500]}"
                )
                return ""

            content_type = response.headers.get(
                "content-type",
                ""
            ).lower()

            if "image" in content_type:
                image_data = response.content

            elif "json" in content_type:
                try:
                    result = response.json()
                    image_url = None
                    image_data = None

                    if isinstance(result, dict):
                        data_items = result.get("data", [])

                        if data_items and isinstance(data_items, list):
                            first_item = data_items[0]

                            if isinstance(first_item, dict):
                                image_url = first_item.get("url")

                                if not image_url:
                                    b64_json = first_item.get(
                                        "b64_json"
                                    )

                                    if b64_json:
                                        import base64

                                        image_data = base64.b64decode(
                                            b64_json
                                        )

                    if image_url:
                        image_response = requests.get(
                            image_url,
                            timeout=180,
                        )

                        if image_response.status_code != 200:
                            logger.error(
                                "❌ Could not download generated image."
                            )
                            return ""

                        image_data = image_response.content

                    if not image_data:
                        logger.error(
                            "❌ Pollinations JSON did not contain "
                            "data[0].url or data[0].b64_json."
                        )
                        logger.error(
                            f"Response: {response.text[:1000]}"
                        )
                        return ""

                except Exception as e:
                    logger.error(
                        f"❌ Could not process JSON response: {e}"
                    )
                    return ""

            else:
                image_data = response.content
            image = Image.open(
                BytesIO(image_data)
            )

            image = image.convert("RGB")

            image.save(
                str(output_path),
                "JPEG",
                quality=95,
            )

            size_kb = (
                os.path.getsize(str(output_path))
                / 1024
            )

            logger.info(
                f"✅ Saved: {output_path} "
                f"({size_kb:.1f} KB)"
            )

            return str(output_path)

        except requests.Timeout:
            logger.error(
                "❌ Pollinations request timed out."
            )
            return ""

        except Exception as e:
            logger.error(
                f"❌ Image generation error: {e}"
            )
            return ""

    # ---------------------------------------------------------
    # STORY SCENES
    # ---------------------------------------------------------

    def generate_scene_images(
        self,
        scenes: List[Dict],
        style: str = "cinematic",
        width: int = 1920,
        height: int = 1080,
    ) -> List[str]:
        """
        Generate Sofia-centered images for story scenes.

        Every story scene uses Sofia's reference image.
        """

        logger.info(
            f"🎬 Generating {len(scenes)} Sofia story scenes..."
        )

        image_paths = []

        for i, scene in enumerate(scenes):

            scene_desc = scene.get(
                "description",
                scene.get(
                    "text",
                    f"Sofia in cinematic scene {i + 1}"
                )
            )

            # Make sure Sofia remains central even when
            # the original scene description does not mention her.
            prompt = f"""
Sofia is the main character in this scene.

{scene_desc}

Sofia must be the visual focus of the scene.
The environment and action should support Sofia's story.
"""

            path = self.generate_image(
                prompt=prompt,
                style=style,
                width=width,
                height=height,
                filename=f"scene_{i + 1:02d}.jpg",
                use_reference=True,
            )

            if path:
                image_paths.append(path)

            if i < len(scenes) - 1:
                time.sleep(1)

        logger.info(
            f"✅ Generated "
            f"{len(image_paths)}/{len(scenes)} Sofia scenes"
        )

        return image_paths

    # ---------------------------------------------------------
    # CHARACTER IMAGE
    # ---------------------------------------------------------

    def generate_character(
        self,
        character_desc: str,
        style: str = "realistic",
        filename: str = "sofia_character.jpg",
    ) -> str:
        """Generate a Sofia character reference image."""

        prompt = f"""
Create a professional character portrait of Sofia.

{character_desc}

Show Sofia clearly and naturally.
Preserve her identity from the reference photo.
Professional cinematic character photography.
"""

        return self.generate_image(
            prompt=prompt,
            style=style,
            width=1024,
            height=1024,
            filename=filename,
            use_reference=True,
        )

    # ---------------------------------------------------------
    # THUMBNAIL BACKGROUND
    # ---------------------------------------------------------

    def generate_thumbnail_bg(
        self,
        topic: str,
        niche: str = "luxury",
    ) -> str:
        """
        Generate a thumbnail background.

        Sofia reference is NOT used here because the thumbnail
        background should be independent.
        """

        prompts = {
            "luxury": (
                f"luxury lifestyle background, {topic}, "
                "premium fashion, elegant architecture, cinematic lighting"
            ),
            "tech": (
                f"futuristic technology background, {topic}, "
                "holograms, premium technology, cinematic lighting"
            ),
            "motivation": (
                f"inspirational luxury background, {topic}, "
                "golden light, success, cinematic composition"
            ),
            "gaming": (
                f"epic gaming background, {topic}, "
                "dramatic lighting, cinematic action"
            ),
            "education": (
                f"professional educational background, {topic}, "
                "modern clean environment"
            ),
            "cartoon": (
                f"high quality animated background, {topic}, "
                "colorful cinematic environment"
            ),
        }

        prompt = prompts.get(
            niche,
            prompts["luxury"]
        )

        return self.generate_image(
            prompt=prompt,
            style="realistic",
            width=1280,
            height=720,
            filename=(
                f"bg_{topic[:30].replace(' ', '_')}.jpg"
            ),
            use_reference=False,
        )


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("\n" + "=" * 60)
    print("🎬 SOFIA LUXURY STORY - IMAGE GENERATOR TEST")
    print("=" * 60)

    generator = AIImageGenerator()

    print("\n👩 Testing Sofia reference image...")

    test_path = generator.generate_image(
        prompt="""
Sofia standing beside a luxurious black sports car
outside a modern luxury hotel at night.
Elegant evening outfit.
Cinematic city lights in the background.
Professional movie still.
        """,
        style="cinematic",
        width=1280,
        height=720,
        filename="sofia_reference_test.jpg",
        use_reference=True,
    )

    print(f"\nResult: {test_path}")

    print("\n" + "=" * 60)
    print("✅ Sofia image generator test complete")
    print("=" * 60)
