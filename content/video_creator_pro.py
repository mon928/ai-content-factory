"""
🎬 SOFIA LUXURY STORY VIDEO CREATOR

Sofia is the central AI storyteller and creative identity.

Creates approximately 5-minute Sofia Luxury Story videos
for luxury, technology, lifestyle, action, drama, entertainment,
and other story topics.

Features:
- Sofia identity
- Controlled visual generation
- Pexels stock video support
- AI image fallback
- Ken Burns animation
- Professional transitions
- Background music
- Voice-over
- Text overlays
- 1080p output
"""

import os
import random
import requests
from pathlib import Path
from loguru import logger

from moviepy import (
    AudioFileClip,
    ImageClip,
    VideoFileClip,
    CompositeVideoClip,
    CompositeAudioClip,
    concatenate_videoclips,
    TextClip,
    ColorClip
)

from moviepy.video.fx import FadeIn, FadeOut

import numpy as np
from dotenv import load_dotenv

from content.ai_image_gen import AIImageGenerator

load_dotenv()


class ProfessionalVideoCreator:
    """
    Creates Sofia Luxury Story videos.

    Sofia is the central storyteller and identity used
    throughout the video creation process.
    """

    def __init__(self, resolution=(1920, 1080), fps=30):

        self.resolution = resolution
        self.fps = fps

        self.width, self.height = resolution

        self.ai_image_gen = AIImageGenerator()

        self.pexels_key = os.getenv("PEXELS_API_KEY")

        # Sofia visual identity
        self.sofia_identity = (
            "Sofia Luxury Story, Sofia is the central AI storyteller, "
            "elegant intelligent modern woman, cinematic luxury aesthetic, "
            "premium editorial style, sophisticated visual storytelling, "
            "high-end fashion and technology atmosphere, realistic "
            "cinematic photography, dramatic professional lighting"
        )

        self.color_palettes = {
            "luxury": [
                (18, 14, 20),
                (210, 170, 80),
                (255, 255, 255)
            ],
            "tech": [
                (15, 15, 40),
                (0, 150, 255),
                (255, 255, 255)
            ],
            "motivation": [
                (20, 20, 20),
                (255, 180, 0),
                (255, 255, 255)
            ],
            "education": [
                (10, 30, 60),
                (80, 220, 100),
                (255, 255, 255)
            ],
            "action": [
                (15, 15, 15),
                (220, 60, 40),
                (255, 255, 255)
            ],
            "drama": [
                (20, 15, 30),
                (180, 80, 120),
                (255, 255, 255)
            ],
            "cartoon": [
                (30, 20, 50),
                (255, 100, 200),
                (255, 255, 255)
            ]
        }

    # =========================================================
    # MUSIC
    # =========================================================

    def _get_bg_music(self, mood="luxury") -> str:

        possible_moods = [
            mood,
            "luxury",
            "tech"
        ]

        for selected_mood in possible_moods:

            music_path = Path(
                f"data/assets/bg_music_{selected_mood}.mp3"
            )

            if music_path.exists():
                return str(music_path)

        return ""

    # =========================================================
    # AI IMAGE
    # =========================================================

    def _generate_scene_image(
        self,
        description: str,
        style: str,
        index: int
    ) -> str:

        output_dir = Path("output/scene_images")
        output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        prompt = (
            f"{self.sofia_identity}. "
            f"Scene {index + 1}. "
            f"{description}. "
            "Cinematic composition, premium production quality, "
            "realistic details, professional photography, "
            "no text, no watermark, 16:9."
        )

        try:

            return self.ai_image_gen.generate_image(
                prompt=prompt,
                style=style,
                width=self.width,
                height=self.height,
                filename=f"sofia_scene_{index + 1:03d}.jpg"
            )

        except Exception as e:

            logger.warning(
                f"AI image generation failed: {e}"
            )

            return ""

    # =========================================================
    # PEXELS SEARCH
    # =========================================================

    def _search_stock_videos(
        self,
        query: str,
        count: int = 5
    ) -> list:

        if not self.pexels_key:
            return []

        try:

            url = "https://api.pexels.com/videos/search"

            headers = {
                "Authorization": self.pexels_key
            }

            params = {
                "query": query,
                "per_page": min(count, 15),
                "orientation": "landscape"
            }

            response = requests.get(
                url,
                headers=headers,
                params=params,
                timeout=20
            )

            if response.status_code == 200:

                videos = response.json().get(
                    "videos",
                    []
                )

                logger.info(
                    f"📹 Pexels found {len(videos)} videos for '{query}'"
                )

                return videos

            logger.warning(
                f"Pexels returned status {response.status_code}"
            )

        except Exception as e:

            logger.warning(
                f"Pexels search failed: {e}"
            )

        return []

    # =========================================================
    # DOWNLOAD PEXELS VIDEO
    # =========================================================

    def _download_stock_video(
        self,
        video_data: dict,
        path: str
    ) -> bool:

        try:

            video_files = video_data.get(
                "video_files",
                []
            )

            if not video_files:
                return False

            suitable = []

            for video_file in video_files:

                width = video_file.get(
                    "width",
                    0
                )

                height = video_file.get(
                    "height",
                    0
                )

                link = video_file.get(
                    "link"
                )

                if link and width >= 1280:

                    suitable.append(
                        (
                            width * height,
                            video_file
                        )
                    )

            if suitable:

                suitable.sort(
                    key=lambda item: item[0],
                    reverse=True
                )

                best = suitable[0][1]

            else:

                best = video_files[0]

            response = requests.get(
                best["link"],
                timeout=45
            )

            if response.status_code != 200:
                return False

            with open(path, "wb") as file:

                file.write(
                    response.content
                )

            return True

        except Exception as e:

            logger.warning(
                f"Stock video download failed: {e}"
            )

            return False

    # =========================================================
    # ANIMATED IMAGE CLIP
    # =========================================================

    def _create_animated_clip(
        self,
        image_path: str,
        duration: float,
        text: str = ""
    ):

        if not image_path or not Path(image_path).exists():

            colors = self.color_palettes.get(
                "luxury",
                [(18, 14, 20), (210, 170, 80), (255, 255, 255)]
            )

            clip = ColorClip(
                size=self.resolution,
                color=colors[0],
                duration=duration
            )

            return clip

        clip = ImageClip(
            image_path,
            duration=duration
        )

        # Gentle Ken Burns movement
        zoom_factor = random.uniform(
            1.04,
            1.10
        )

        def ken_burns_effect(
            get_frame,
            t
        ):

            progress = (
                t / duration
                if duration > 0
                else 0
            )

            current_zoom = (
                1.0
                + (zoom_factor - 1.0)
                * progress
            )

            frame = get_frame(t)

            height, width = frame.shape[:2]

            new_height = int(
                height * current_zoom
            )

            new_width = int(
                width * current_zoom
            )

            from PIL import Image as PILImage

            pil_img = PILImage.fromarray(
                frame
            )

            pil_img = pil_img.resize(
                (new_width, new_height),
                PILImage.LANCZOS
            )

            left = (
                new_width - width
            ) // 2

            top = (
                new_height - height
            ) // 2

            pil_img = pil_img.crop(
                (
                    left,
                    top,
                    left + width,
                    top + height
                )
            )

            return np.array(
                pil_img
            )

        try:

            clip = clip.transform(
                ken_burns_effect
            )

        except Exception as e:

            logger.warning(
                f"Ken Burns effect failed: {e}"
            )

        # Text overlay
        if text:

            try:

                text_clip = TextClip(
                    text=text,
                    font_size=52,
                    color="white",
                    stroke_color="black",
                    stroke_width=3,
                    size=(
                        self.width - 180,
                        None
                    ),
                    method="caption"
                )

                text_clip = (
                    text_clip
                    .with_position(
                        (
                            "center",
                            self.height - 170
                        )
                    )
                    .with_duration(duration)
                )

                clip = CompositeVideoClip(
                    [
                        clip,
                        text_clip
                    ]
                )

            except Exception as e:

                logger.warning(
                    f"Text overlay failed: {e}"
                )

        return clip

    # =========================================================
    # STOCK VIDEO CLIP
    # =========================================================

    def _create_stock_clip(
        self,
        video_path: str,
        duration: float
    ):

        try:

            clip = VideoFileClip(
                video_path
            )

            if clip.duration > duration:

                max_start = max(
                    0,
                    clip.duration - duration
                )

                start = random.uniform(
                    0,
                    max_start
                )

                clip = clip.subclipped(
                    start,
                    start + duration
                )

            elif clip.duration < duration:

                repeats = int(
                    duration / clip.duration
                ) + 1

                clips = [
                    clip
                ]

                for _ in range(
                    repeats - 1
                ):
                    clips.append(
                        VideoFileClip(
                            video_path
                        )
                    )

                clip = concatenate_videoclips(
                    clips
                ).subclipped(
                    0,
                    duration
                )

            # Resize to 1920x1080
            clip = clip.resized(
                width=self.width
            )

            if clip.h < self.height:

                clip = clip.resized(
                    height=self.height
                )

            clip = clip.cropped(
                x_center=clip.w / 2,
                y_center=clip.h / 2,
                width=self.width,
                height=self.height
            )

            return clip

        except Exception as e:

            logger.warning(
                f"Could not create stock clip: {e}"
            )

            return None

    # =========================================================
    # MAIN VIDEO CREATOR
    # =========================================================

    def create_professional_video(
        self,
        voiceover_path: str,
        topic: str,
        script_text: str = "",
        niche: str = "luxury",
        style: str = "professional",
        add_music: bool = True,
        output_path: str = "output/sofia_luxury_story.mp4"
    ) -> str:

        logger.info(
            f"🎬 Creating Sofia Luxury Story: {topic[:80]}"
        )

        if not Path(
            voiceover_path
        ).exists():

            logger.error(
                f"Voiceover not found: {voiceover_path}"
            )

            return ""

        # -----------------------------------------------------
        # LOAD AUDIO
        # -----------------------------------------------------

        audio = AudioFileClip(
            voiceover_path
        )

        total_duration = audio.duration

        logger.info(
            f"⏱️ Voice-over duration: {total_duration:.1f}s"
        )

        # -----------------------------------------------------
        # TARGET ABOUT FIVE MINUTES
        # -----------------------------------------------------

        if total_duration > 330:

            logger.warning(
                "Voice-over is longer than expected for a Sofia Luxury Story."
            )

        # -----------------------------------------------------
        # SPLIT SCRIPT
        # -----------------------------------------------------

        sentences = (
            script_text
            .replace("\n", " ")
            .split(".")
        )

        sentences = [
            sentence.strip()
            for sentence in sentences
            if len(sentence.strip()) > 10
        ]

        # -----------------------------------------------------
        # CONTROLLED NUMBER OF VISUALS
        #
        # About 15 scenes for a 5-minute story.
        # This prevents dozens of AI image generations.
        # -----------------------------------------------------

        target_scenes = 15

        if total_duration < 120:

            target_scenes = max(
                8,
                int(total_duration / 10)
            )

        elif total_duration < 240:

            target_scenes = 12

        else:

            target_scenes = 15

        num_scenes = min(
            target_scenes,
            15
        )

        scene_duration = (
            total_duration / num_scenes
        )

        logger.info(
            f"🎬 Sofia story: {num_scenes} visual scenes "
            f"at approximately {scene_duration:.1f}s each"
        )

        # -----------------------------------------------------
        # PREPARE SCENE DESCRIPTIONS
        # -----------------------------------------------------

        scene_descriptions = []

        for i in range(
            num_scenes
        ):

            if sentences:

                sentence = sentences[
                    i % len(sentences)
                ]

            else:

                sentence = (
                    f"{topic} - Sofia Luxury Story scene {i + 1}"
                )

            scene_descriptions.append(
                sentence[:180]
            )

        # -----------------------------------------------------
        # VISUAL CLIPS
        # -----------------------------------------------------

        video_clips = []

        # Search Pexels only when available
        stock_results = []

        if self.pexels_key:

            search_terms = [
                topic,
                "luxury lifestyle",
                "luxury fashion",
                "modern technology",
                "cinematic city",
                "business luxury"
            ]

            for search_term in search_terms:

                results = self._search_stock_videos(
                    search_term,
                    count=3
                )

                stock_results.extend(
                    results
                )

                if len(stock_results) >= num_scenes:
                    break

        # -----------------------------------------------------
        # CREATE SCENES
        # -----------------------------------------------------

        for i in range(
            num_scenes
        ):

            scene_text = scene_descriptions[i]

            clip = None

            # -------------------------------------------------
            # TRY PEXELS FIRST
            # -------------------------------------------------

            if stock_results:

                stock_index = (
                    i % len(stock_results)
                )

                stock_data = (
                    stock_results[stock_index]
                )

                stock_path = Path(
                    "output/scene_images"
                    f"/sofia_stock_{i + 1:03d}.mp4"
                )

                if self._download_stock_video(
                    stock_data,
                    str(stock_path)
                ):

                    clip = self._create_stock_clip(
                        str(stock_path),
                        scene_duration
                    )

            # -------------------------------------------------
            # AI IMAGE FALLBACK
            # -------------------------------------------------

            if clip is None:

                logger.info(
                    f"🎨 Generating Sofia AI scene {i + 1}/{num_scenes}"
                )

                img_path = (
                    self._generate_scene_image(
                        description=(
                            f"Sofia Luxury Story scene. "
                            f"{scene_text}"
                        ),
                        style="realistic",
                        index=i
                    )
                )

                if img_path:

                    clip = (
                        self._create_animated_clip(
                            image_path=img_path,
                            duration=scene_duration,
                            text=(
                                scene_text[:90]
                                if i % 3 == 0
                                else ""
                            )
                        )
                    )

            # -------------------------------------------------
            # FINAL FALLBACK
            # -------------------------------------------------

            if clip is None:

                colors = self.color_palettes.get(
                    niche,
                    self.color_palettes["luxury"]
                )

                clip = ColorClip(
                    size=self.resolution,
                    color=colors[0],
                    duration=scene_duration
                )

            # -------------------------------------------------
            # TRANSITIONS
            # -------------------------------------------------

            try:

                if i == 0:

                    clip = clip.with_effects(
                        [
                            FadeIn(0.5)
                        ]
                    )

                else:

                    clip = clip.with_effects(
                        [
                            FadeIn(0.3),
                            FadeOut(0.3)
                        ]
                    )

            except Exception:
                pass

            video_clips.append(
                clip
            )

        # -----------------------------------------------------
        # COMBINE VIDEO
        # -----------------------------------------------------

        logger.info(
            "🎞️ Combining Sofia story scenes..."
        )

        final_video = concatenate_videoclips(
            video_clips,
            method="compose"
        )

        # Match exact voice-over length
        if final_video.duration > total_duration:

            final_video = (
                final_video
                .subclipped(
                    0,
                    total_duration
                )
            )

        # -----------------------------------------------------
        # VOICE
        # -----------------------------------------------------

        final_video = (
            final_video
            .with_audio(audio)
        )

        # -----------------------------------------------------
        # BACKGROUND MUSIC
        # -----------------------------------------------------

        if add_music:

            music_path = self._get_bg_music(
                "luxury"
            )

            if music_path and Path(
                music_path
            ).exists():

                try:

                    music = AudioFileClip(
                        music_path
                    )

                    if music.duration < total_duration:

                        repeats = (
                            int(
                                total_duration
                                / music.duration
                            ) + 1
                        )

                        music_clips = []

                        for _ in range(
                            repeats
                        ):

                            music_clips.append(
                                AudioFileClip(
                                    music_path
                                )
                            )

                        music = concatenate_videoclips(
                            music_clips
                        )

                    music = music.subclipped(
                        0,
                        total_duration
                    )

                    music = music.with_volume(
                        0.07
                    )

                    final_audio = CompositeAudioClip(
                        [
                            audio,
                            music
                        ]
                    )

                    final_video = (
                        final_video
                        .with_audio(
                            final_audio
                        )
                    )

                    logger.info(
                        "🎵 Sofia background music added"
                    )

                except Exception as e:

                    logger.warning(
                        f"Music failed: {e}"
                    )

        # -----------------------------------------------------
        # SOFIA INTRO TITLE
        # -----------------------------------------------------

        try:

            title = TextClip(
                text=(
                    "SOFIA LUXURY STORY"
                ),
                font_size=72,
                color="white",
                stroke_color="black",
                stroke_width=4,
                size=(
                    self.width - 120,
                    None
                ),
                method="caption"
            )

            title = (
                title
                .with_position("center")
                .with_duration(3)
                .with_effects(
                    [
                        FadeIn(0.4),
                        FadeOut(0.6)
                    ]
                )
            )

            final_video = CompositeVideoClip(
                [
                    final_video,
                    title
                ]
            )

        except Exception as e:

            logger.warning(
                f"Sofia title failed: {e}"
            )

        # -----------------------------------------------------
        # WRITE VIDEO
        # -----------------------------------------------------

        Path(
            output_path
        ).parent.mkdir(
            parents=True,
            exist_ok=True
        )

        logger.info(
            "🚀 Rendering final Sofia Luxury Story..."
        )

        final_video.write_videofile(
            output_path,
            fps=self.fps,
            codec="libx264",
            audio_codec="aac",
            bitrate="6000k",
            preset="fast",
            threads=4
        )

        # -----------------------------------------------------
        # CLEANUP
        # -----------------------------------------------------

        try:
            audio.close()
        except Exception:
            pass

        for clip in video_clips:

            try:
                clip.close()
            except Exception:
                pass

        # -----------------------------------------------------
        # RESULT
        # -----------------------------------------------------

        if Path(
            output_path
        ).exists():

            size_mb = (
                os.path.getsize(
                    output_path
                )
                / (1024 * 1024)
            )

            logger.info(
                f"✅ SOFIA LUXURY STORY CREATED: "
                f"{output_path} ({size_mb:.1f} MB)"
            )

            return output_path

        logger.error(
            "❌ Final Sofia video was not created."
        )

        return ""


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("\n" + "=" * 60)
    print("🎬 SOFIA LUXURY STORY VIDEO CREATOR TEST")
    print("=" * 60)

    creator = ProfessionalVideoCreator(
        resolution=(1920, 1080)
    )

    test_topic = (
        "Sofia discovers the future of luxury technology"
    )

    test_script = """
    Sofia takes us inside the future of luxury technology.
    The world of luxury is changing faster than ever.
    New technology is transforming fashion and lifestyle.
    Sofia explores the most fascinating innovations.
    From intelligent cars to futuristic homes.
    From smart fashion to incredible new experiences.
    Sofia shows us why luxury is no longer just about price.
    It is about experience, design, technology and imagination.
    But there is an even bigger story behind this transformation.
    The next generation of luxury will feel completely different.
    Sofia explores what this means for the future.
    And the journey is only beginning.
    """

    voice_file = None

    for vf in Path(
        "output"
    ).glob(
        "voiceover_*.mp3"
    ):

        voice_file = str(vf)
        break

    if voice_file:

        result = creator.create_professional_video(
            voiceover_path=voice_file,
            topic=test_topic,
            script_text=test_script,
            niche="luxury",
            add_music=True,
            output_path=(
                "output/"
                "sofia_luxury_story_test.mp4"
            )
        )

        if result:

            print(
                "\n✅ Sofia Luxury Story:"
            )

            print(result)

        else:

            print(
                "\n❌ Sofia video creation failed."
            )

    else:

        print(
            "\n⚠️ No voice-over found."
        )

    print(
        "\n" + "=" * 60
    )
    print(
        "✅ Sofia Luxury Story Test Complete!"
    )
