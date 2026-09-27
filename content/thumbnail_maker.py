"""
SOFIA LUXURY STORY
REAL-MEDIA THUMBNAIL MAKER

No AI image generation.

Thumbnail priority:
1. User library image
2. Sofia reference image
3. Clean luxury gradient

Uses Pillow only.
"""

import os
import textwrap
from pathlib import Path

from loguru import logger
from PIL import Image, ImageDraw, ImageFont, ImageEnhance


class ThumbnailMaker:
    """Create professional YouTube thumbnails without AI image generation."""

    SIZE = (1280, 720)

    def __init__(self):
        self.output_dir = Path("output/thumbnails")
        self.output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        self.library_dir = Path("library")
        self.sofia_reference = Path(
            "assets/sofia/sofia_reference.jpg"
        )

    # =====================================================
    # SOURCE MEDIA
    # =====================================================

    def _find_source_image(self) -> Path | None:
        allowed = {
            ".jpg",
            ".jpeg",
            ".png",
            ".webp",
        }

        if self.library_dir.exists():
            files = sorted(
                [
                    p
                    for p in self.library_dir.rglob("*")
                    if p.is_file()
                    and p.suffix.lower() in allowed
                ],
                key=lambda p: p.name.lower()
            )

            if files:
                return files[0]

        if self.sofia_reference.exists():
            return self.sofia_reference

        return None

    # =====================================================
    # BACKGROUND
    # =====================================================

    def _make_background(self) -> Image.Image:
        source = self._find_source_image()

        if source:
            try:
                image = Image.open(source).convert("RGB")
                image = self._cover_crop(
                    image,
                    self.SIZE
                )
                logger.info(
                    f"🖼️ Thumbnail source: {source}"
                )
                return image
            except Exception as exc:
                logger.warning(
                    f"Thumbnail source failed: {exc}"
                )

        # Clean fallback gradient.
        image = Image.new(
            "RGB",
            self.SIZE,
            (10, 10, 14)
        )

        draw = ImageDraw.Draw(image)

        for y in range(self.SIZE[1]):
            ratio = y / self.SIZE[1]
            value = int(18 + 28 * ratio)
            draw.line(
                [(0, y), (self.SIZE[0], y)],
                fill=(value, value, value + 5)
            )

        return image

    def _cover_crop(
        self,
        image: Image.Image,
        target: tuple
    ) -> Image.Image:
        target_w, target_h = target

        image_ratio = image.width / image.height
        target_ratio = target_w / target_h

        if image_ratio > target_ratio:
            new_height = target_h
            new_width = int(
                new_height * image_ratio
            )
        else:
            new_width = target_w
            new_height = int(
                new_width / image_ratio
            )

        image = image.resize(
            (new_width, new_height),
            Image.LANCZOS
        )

        left = max(
            0,
            (new_width - target_w) // 2
        )
        top = max(
            0,
            (new_height - target_h) // 2
        )

        return image.crop(
            (
                left,
                top,
                left + target_w,
                top + target_h
            )
        )

    # =====================================================
    # FONTS
    # =====================================================

    def _font(self, size: int):
        candidates = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
            "arial.ttf",
        ]

        for path in candidates:
            try:
                return ImageFont.truetype(
                    path,
                    size
                )
            except Exception:
                continue

        return ImageFont.load_default()

    # =====================================================
    # TEXT
    # =====================================================

    def _draw_centered_text(
        self,
        draw: ImageDraw.ImageDraw,
        text: str,
        y: int,
        font,
        fill=(255, 255, 255)
    ):
        bbox = draw.textbbox(
            (0, 0),
            text,
            font=font
        )

        width = bbox[2] - bbox[0]

        x = (
            self.SIZE[0] - width
        ) // 2

        # Shadow.
        draw.text(
            (x + 4, y + 4),
            text,
            font=font,
            fill=(0, 0, 0)
        )

        draw.text(
            (x, y),
            text,
            font=font,
            fill=fill
        )

    # =====================================================
    # CREATE
    # =====================================================

    def create_thumbnail(
        self,
        topic: str,
        niche: str = "luxury",
        style: str = "modern"
    ) -> str:

        topic = (
            str(topic)
            .strip()
            or "Sofia Luxury Story"
        )

        logger.info(
            f"🖼️ Creating real-media thumbnail for: "
            f"{topic[:60]}..."
        )

        background = self._make_background()

        # Slight enhancement.
        background = ImageEnhance.Contrast(
            background
        ).enhance(1.12)

        background = ImageEnhance.Color(
            background
        ).enhance(1.08)

        draw = ImageDraw.Draw(
            background
        )

        # Dark overlay for readability.
        draw.rectangle(
            [0, 0, self.SIZE[0], self.SIZE[1]],
            fill=(0, 0, 0, 105)
        )

        # Gold luxury accent.
        draw.rectangle(
            [
                0,
                self.SIZE[1] - 16,
                self.SIZE[0],
                self.SIZE[1]
            ],
            fill=(214, 168, 74)
        )

        # Brand.
        brand_font = self._font(34)

        draw.text(
            (45, 35),
            "SOFIA LUXURY STORY",
            font=brand_font,
            fill=(238, 202, 120)
        )

        # Main title.
        clean_topic = " ".join(
            topic.split()
        )

        lines = textwrap.wrap(
            clean_topic.upper(),
            width=25
        )

        title_font = self._font(64)

        y = 155

        for line in lines[:3]:
            self._draw_centered_text(
                draw,
                line,
                y,
                title_font
            )
            y += 82

        # Small label.
        label_font = self._font(28)

        draw.text(
            (45, self.SIZE[1] - 75),
            "CINEMATIC LUXURY • NEW STORY",
            font=label_font,
            fill=(255, 255, 255)
        )

        safe_name = "".join(
            char if char.isalnum() or char in "_-"
            else "_"
            for char in clean_topic[:45]
        ).strip("_")

        filename = (
            f"thumbnail_{safe_name or 'sofia_luxury'}.jpg"
        )

        output_path = (
            self.output_dir
            / filename
        )

        background.save(
            output_path,
            "JPEG",
            quality=95
        )

        size_kb = (
            os.path.getsize(output_path)
            / 1024
        )

        logger.info(
            f"✅ Thumbnail saved: "
            f"{output_path} "
            f"({size_kb:.1f} KB)"
        )

        return str(output_path)

    def create_multiple(
        self,
        topics: list,
        niche: str = "luxury"
    ) -> list:

        results = []

        for topic in topics:
            value = (
                topic.get("topic", topic)
                if isinstance(topic, dict)
                else topic
            )

            results.append(
                self.create_thumbnail(
                    value,
                    niche=niche
                )
            )

        return results


if __name__ == "__main__":
    maker = ThumbnailMaker()

    path = maker.create_thumbnail(
        "The Future of Luxury Technology",
        niche="luxury"
    )

    print(f"Thumbnail created: {path}")
