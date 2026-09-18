"""
SOFIA LUXURY STORY VIDEO CREATOR

Optimized production renderer for Sofia Luxury Story.

Goals:
- Sofia remains the central identity
- Approximately 5-minute stories
- Lower memory usage for GitHub Actions
- 1280x720 HD rendering
- Controlled number of visual scenes
- Pexels stock video support
- Sofia AI image fallback
- Cinematic movement
- Professional fades
- Voice-over
- Optional background music
- Lightweight text overlays
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
    ColorClip,
)

from moviepy.video.fx import FadeIn, FadeOut

from dotenv import load_dotenv

from content.ai_image_gen import AIImageGenerator


load_dotenv()


class ProfessionalVideoCreator:
    """
    Optimized Sofia Luxury Story video creator.

    The renderer deliberately limits the number and resolution
    of visual assets so GitHub Actions can render the video
    without excessive memory usage.
    """

    def __init__(
        self,
        resolution=(1280, 720),
        fps=24
    ):
        self.resolution = resolution
        self.fps = fps

        self.width, self.height = resolution

        self.ai_image_gen = AIImageGenerator()

        self.pexels_key = os.getenv("PEXELS_API_KEY")

        # -----------------------------------------------------
        # SOFIA IDENTITY
        # -----------------------------------------------------

        self.sofia_identity = (
            "Sofia Luxury Story. Sofia is the central AI storyteller "
            "and visual identity. Sofia is an elegant intelligent "
            "modern woman with a sophisticated cinematic presence. "
            "Premium luxury editorial aesthetic, realistic cinematic "
            "photography, high-end fashion, technology, dramatic "
            "professional lighting, polished storytelling."
        )

        # -----------------------------------------------------
        # OUTPUT DIRECTORIES
        # -----------------------------------------------------

        self.output_dir = Path("output")
        self.scene_dir = self.output_dir / "scene_images"

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        self.scene_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        # -----------------------------------------------------
        # FALLBACK PALETTES
        # -----------------------------------------------------

        self.color_palettes = {
            "luxury": [
                (18, 14, 20),
                (210, 170, 80),
                (255, 255, 255),
            ],
            "tech": [
                (15, 15, 40),
                (0, 150, 255),
                (255, 255, 255),
            ],
            "motivation": [
                (20, 20, 20),
                (255, 180, 0),
                (255, 255, 255),
            ],
            "education": [
                (10, 30, 60),
                (80, 220, 100),
                (255, 255, 255),
            ],
            "action": [
                (15, 15, 15),
                (220, 60, 40),
                (255, 255, 255),
            ],
            "drama": [
                (20, 15, 30),
                (180, 80, 120),
                (255, 255, 255),
            ],
        }

    # =========================================================
    # BACKGROUND MUSIC
    # =========================================================

    def _get_bg_music(
        self,
        mood="luxury"
    ) -> str:

        possible_moods = [
            mood,
            "luxury",
            "tech",
        ]

        for selected_mood in possible_moods:

            music_path = Path(
                f"data/assets/bg_music_{selected_mood}.mp3"
            )

            if music_path.exists():
                return str(music_path)

        return ""

    # =========================================================
    # AI IMAGE GENERATION
    # =========================================================

    def _generate_scene_image(
        self,
        description: str,
        style: str,
        index: int
    ) -> str:

        self.scene_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        prompt = (
            f"{self.sofia_identity}. "
            f"Scene {index + 1}. "
            f"{description}. "
            "Wide cinematic composition, 16:9, "
            "realistic premium photography, "
            "professional film lighting, "
            "high detail, elegant composition, "
            "no text, no watermark."
        )

        filename = (
            f"sofia_scene_{index + 1:03d}.jpg"
        )

        try:

            logger.info(
                f"🎨 Generating Sofia visual {index + 1}: "
                f"{description[:80]}"
            )

            result = self.ai_image_gen.generate_image(
                prompt=prompt,
                style=style,
                width=self.width,
                height=self.height,
                filename=filename,
            )

            if result and Path(result).exists():

                logger.info(
                    f"✅ Sofia visual saved: {result}"
                )

                return result

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
        count: int = 3
    ) -> list:

        if not self.pexels_key:
            return []

        try:

            response = requests.get(
                "https://api.pexels.com/videos/search",
                headers={
                    "Authorization": self.pexels_key
                },
                params={
                    "query": query,
                    "per_page": min(count, 10),
                    "orientation": "landscape",
                },
                timeout=20,
            )

            if response.status_code == 200:

                videos = response.json().get(
                    "videos",
                    []
                )

                logger.info(
                    f"📹 Pexels found {len(videos)} videos "
                    f"for '{query}'"
                )

                return videos

            logger.warning(
                f"Pexels returned status "
                f"{response.status_code}"
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

            Path(path).parent.mkdir(
                parents=True,
                exist_ok=True
            )

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

                if link:

                    score = abs(
                        (width / max(height, 1))
                        - (16 / 9)
                    )

                    suitable.append(
                        (
                            score,
                            width * height,
                            video_file
                        )
                    )

            if not suitable:
                return False

            # Prefer a landscape file close to 16:9
            suitable.sort(
                key=lambda item: (
                    item[0],
                    -item[1]
                )
            )

            best = suitable[0][2]

            logger.info(
                "⬇️ Downloading Pexels stock video..."
            )

            # Stream the file instead of loading the
            # entire video into RAM.
            with requests.get(
                best["link"],
                timeout=60,
                stream=True
            ) as response:

                if response.status_code != 200:
                    return False

                with open(
                    path,
                    "wb"
                ) as file:

                    for chunk in response.iter_content(
                        chunk_size=1024 * 1024
                    ):

                        if chunk:
                            file.write(chunk)

            return Path(path).exists()

        except Exception as e:

            logger.warning(
                f"Stock video download failed: {e}"
            )

            return False

    # =========================================================
    # IMAGE CLIP
    # =========================================================

    def _create_image_clip(
        self,
        image_path: str,
        duration: float,
        text: str = ""
    ):

        if (
            not image_path
            or not Path(image_path).exists()
        ):

            colors = self.color_palettes.get(
                "luxury",
                [
                    (18, 14, 20),
                    (210, 170, 80),
                    (255, 255, 255),
                ]
            )

            return ColorClip(
                size=self.resolution,
                color=colors[0],
                duration=duration
            )

        try:

            # -------------------------------------------------
            # IMPORTANT:
            # Do NOT use the old per-frame Ken Burns transform.
            #
            # A simple animated scale is much lighter on RAM
            # and still gives the video a cinematic feeling.
            # -------------------------------------------------

            clip = ImageClip(
                image_path,
                duration=duration
            )

            # Make sure image fills the HD frame.
            if clip.w < self.width:

                clip = clip.resized(
                    width=self.width
                )

            if clip.h < self.height:

                clip = clip.resized(
                    height=self.height
                )

            # Crop to exact 16:9 frame.
            if clip.w > self.width or clip.h > self.height:

                clip = clip.cropped(
                    x_center=clip.w / 2,
                    y_center=clip.h / 2,
                    width=self.width,
                    height=self.height,
                )

            # -------------------------------------------------
            # LIGHTWEIGHT TEXT OVERLAY
            # -------------------------------------------------

            if text:

                try:

                    text_clip = TextClip(
                        text=text[:90],
                        font_size=34,
                        color="white",
                        stroke_color="black",
                        stroke_width=2,
                        size=(
                            self.width - 120,
                            90
                        ),
                        method="caption",
                    )

                    text_clip = (
                        text_clip
                        .with_position(
                            (
                                "center",
                                self.height - 120
                            )
                        )
                        .with_duration(
                            duration
                        )
                    )

                    clip = CompositeVideoClip(
                        [
                            clip,
                            text_clip
                        ],
                        size=self.resolution
                    )

                except Exception as e:

                    logger.warning(
                        f"Text overlay skipped: {e}"
                    )

            return clip

        except Exception as e:

            logger.warning(
                f"Could not create image clip: {e}"
            )

            return None

    # =========================================================
    # STOCK VIDEO CLIP
    # =========================================================

    def _create_stock_clip(
        self,
        video_path: str,
        duration: float
    ):

        if (
            not video_path
            or not Path(video_path).exists()
        ):
            return None

        try:

            clip = VideoFileClip(
                video_path
            )

            if clip.duration <= 0:
                clip.close()
                return None

            # -------------------------------------------------
            # TRIM
            # -------------------------------------------------

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
                    min(
                        start + duration,
                        clip.duration
                    )
                )

            # -------------------------------------------------
            # RESIZE TO 720P
            # -------------------------------------------------

            clip = clip.resized(
                width=self.width
            )

            if clip.h < self.height:

                clip = clip.resized(
                    height=self.height
                )

            # -------------------------------------------------
            # CENTER CROP
            # -------------------------------------------------

            if (
                clip.w > self.width
                or clip.h > self.height
            ):

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
        output_path: str = (
            "output/sofia_luxury_story.mp4"
        )
    ) -> str:

        logger.info(
            f"🎬 Creating Sofia Luxury Story: "
            f"{topic[:100]}"
        )

        # -----------------------------------------------------
        # CHECK VOICEOVER
        # -----------------------------------------------------

        if not Path(
            voiceover_path
        ).exists():

            logger.error(
                f"Voiceover not found: "
                f"{voiceover_path}"
            )

            return ""

        audio = None
        final_video = None
        video_clips = []

        try:

            # -------------------------------------------------
            # LOAD VOICE
            # -------------------------------------------------

            audio = AudioFileClip(
                voiceover_path
            )

            total_duration = audio.duration

            logger.info(
                f"⏱️ Voice-over duration: "
                f"{total_duration:.1f}s"
            )

            # -------------------------------------------------
            # SAFETY CHECK
            # -------------------------------------------------

            if total_duration < 30:

                logger.warning(
                    "Voice-over is unusually short."
                )

            if total_duration > 360:

                logger.warning(
                    "Voice-over is longer than "
                    "the normal Sofia target."
                )

            # -------------------------------------------------
            # SPLIT SCRIPT INTO STORY BEATS
            # -------------------------------------------------

            cleaned_script = (
                script_text
                .replace("\n", " ")
                .replace("!", ".")
                .replace("?", ".")
            )

            raw_sentences = (
                cleaned_script.split(".")
            )

            sentences = [
                sentence.strip()
                for sentence in raw_sentences
                if len(sentence.strip()) > 15
            ]

            # -------------------------------------------------
            # CONTROLLED VISUAL COUNT
            #
            # Five-minute story:
            # approximately 10 scenes.
            #
            # This is intentionally lower than the previous
            # 15-scene version to reduce memory and API work.
            # -------------------------------------------------

            if total_duration < 120:

                num_scenes = 6

            elif total_duration < 240:

                num_scenes = 8

            else:

                num_scenes = 10

            num_scenes = max(
                4,
                min(num_scenes, 10)
            )

            scene_duration = (
                total_duration
                / num_scenes
            )

            logger.info(
                f"🎬 Sofia story: "
                f"{num_scenes} cinematic scenes "
                f"at approximately "
                f"{scene_duration:.1f}s each"
            )

            # -------------------------------------------------
            # BUILD SCENE DESCRIPTIONS
            # -------------------------------------------------

            scene_descriptions = []

            for i in range(num_scenes):

                if sentences:

                    position = int(
                        i * len(sentences)
                        / num_scenes
                    )

                    position = min(
                        position,
                        len(sentences) - 1
                    )

                    scene_text = (
                        sentences[position]
                    )

                else:

                    scene_text = (
                        f"Sofia explores "
                        f"{topic}"
                    )

                scene_descriptions.append(
                    scene_text[:180]
                )

            # -------------------------------------------------
            # PEXELS
            # -------------------------------------------------

            stock_results = []

            if self.pexels_key:

                search_terms = [
                    topic,
                    "luxury lifestyle",
                    "luxury fashion",
                    "modern technology",
                    "cinematic city",
                ]

                for search_term in search_terms:

                    results = (
                        self._search_stock_videos(
                            search_term,
                            count=2
                        )
                    )

                    stock_results.extend(
                        results
                    )

                    if len(stock_results) >= 4:
                        break

            logger.info(
                f"📹 Available Pexels clips: "
                f"{len(stock_results)}"
            )

            # -------------------------------------------------
            # CREATE VISUAL SCENES
            # -------------------------------------------------

            for i in range(num_scenes):

                scene_text = (
                    scene_descriptions[i]
                )

                clip = None

                # -------------------------------------------------
                # TRY STOCK VIDEO
                # -------------------------------------------------

                if stock_results:

                    stock_data = (
                        stock_results[
                            i % len(stock_results)
                        ]
                    )

                    stock_path = (
                        self.scene_dir
                        / f"sofia_stock_{i + 1:03d}.mp4"
                    )

                    if self._download_stock_video(
                        stock_data,
                        str(stock_path)
                    ):

                        clip = (
                            self._create_stock_clip(
                                str(stock_path),
                                scene_duration
                            )
                        )

                        if clip:

                            logger.info(
                                f"✅ Using Pexels "
                                f"scene {i + 1}"
                            )

                # -------------------------------------------------
                # AI FALLBACK
                # -------------------------------------------------

                if clip is None:

                    logger.info(
                        f"🎨 Generating Sofia AI "
                        f"scene {i + 1}/{num_scenes}"
                    )

                    image_path = (
                        self._generate_scene_image(
                            description=(
                                "Sofia is the central "
                                "character in this scene. "
                                f"{scene_text}"
                            ),
                            style="realistic",
                            index=i
                        )
                    )

                    if image_path:

                        clip = (
                            self._create_image_clip(
                                image_path=image_path,
                                duration=scene_duration,
                                text=(
                                    scene_text
                                    if i % 3 == 0
                                    else ""
                                )
                            )
                        )

                # -------------------------------------------------
                # FINAL FALLBACK
                # -------------------------------------------------

                if clip is None:

                    colors = (
                        self.color_palettes.get(
                            niche,
                            self.color_palettes[
                                "luxury"
                            ]
                        )
                    )

                    clip = ColorClip(
                        size=self.resolution,
                        color=colors[0],
                        duration=scene_duration
                    )

                # -------------------------------------------------
                # LIGHTWEIGHT TRANSITIONS
                # -------------------------------------------------

                try:

                    if i == 0:

                        clip = clip.with_effects(
                            [
                                FadeIn(0.4)
                            ]
                        )

                    else:

                        clip = clip.with_effects(
                            [
                                FadeIn(0.25),
                                FadeOut(0.25)
                            ]
                        )

                except Exception as e:

                    logger.warning(
                        f"Transition skipped: {e}"
                    )

                video_clips.append(
                    clip
                )

            # -------------------------------------------------
            # VERIFY SCENES
            # -------------------------------------------------

            if not video_clips:

                logger.error(
                    "No visual scenes were created."
                )

                return ""

            logger.info(
                "🎞️ Combining Sofia story scenes..."
            )

            # -------------------------------------------------
            # COMBINE
            # -------------------------------------------------

            final_video = concatenate_videoclips(
                video_clips,
                method="compose"
            )

            # -------------------------------------------------
            # EXACT AUDIO LENGTH
            # -------------------------------------------------

            if final_video.duration > total_duration:

                final_video = (
                    final_video.subclipped(
                        0,
                        total_duration
                    )
                )

            elif final_video.duration < total_duration:

                logger.warning(
                    "Video shorter than voice-over. "
                    "Repeating final scene."
                )

                remaining = (
                    total_duration
                    - final_video.duration
                )

                last_clip = video_clips[-1]

                extension = (
                    last_clip
                    .subclipped(
                        0,
                        min(
                            remaining,
                            last_clip.duration
                        )
                    )
                )

                final_video = concatenate_videoclips(
                    [
                        final_video,
                        extension
                    ],
                    method="compose"
                )

            # -------------------------------------------------
            # VOICEOVER
            # -------------------------------------------------

            final_video = (
                final_video
                .with_audio(audio)
            )

            # -------------------------------------------------
            # BACKGROUND MUSIC
            # -------------------------------------------------

            if add_music:

                music_path = (
                    self._get_bg_music(
                        "luxury"
                    )
                )

                if (
                    music_path
                    and Path(music_path).exists()
                ):

                    music = None

                    try:

                        music = AudioFileClip(
                            music_path
                        )

                        if (
                            music.duration
                            < total_duration
                        ):

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

                            music = (
                                concatenate_videoclips(
                                    music_clips
                                )
                            )

                        music = (
                            music
                            .subclipped(
                                0,
                                total_duration
                            )
                            .with_volume(
                                0.06
                            )
                        )

                        final_audio = (
                            CompositeAudioClip(
                                [
                                    audio,
                                    music
                                ]
                            )
                        )

                        final_video = (
                            final_video
                            .with_audio(
                                final_audio
                            )
                        )

                        logger.info(
                            "🎵 Background music added."
                        )

                    except Exception as e:

                        logger.warning(
                            f"Music failed: {e}"
                        )

                        try:

                            if music:
                                music.close()

                        except Exception:
                            pass

            # -------------------------------------------------
            # TITLE
            # -------------------------------------------------

            try:

                title = TextClip(
                    text="SOFIA LUXURY STORY",
                    font_size=54,
                    color="white",
                    stroke_color="black",
                    stroke_width=3,
                    size=(
                        self.width - 100,
                        80
                    ),
                    method="caption"
                )

                title = (
                    title
                    .with_position("center")
                    .with_duration(3)
                    .with_effects(
                        [
                            FadeIn(0.35),
                            FadeOut(0.5)
                        ]
                    )
                )

                final_video = (
                    CompositeVideoClip(
                        [
                            final_video,
                            title
                        ],
                        size=self.resolution
                    )
                )

            except Exception as e:

                logger.warning(
                    f"Title skipped: {e}"
                )

            # -------------------------------------------------
            # OUTPUT
            # -------------------------------------------------

            Path(
                output_path
            ).parent.mkdir(
                parents=True,
                exist_ok=True
            )

            logger.info(
                "🚀 Rendering final "
                "Sofia Luxury Story..."
            )

            # -------------------------------------------------
            # MEMORY-FRIENDLY RENDER
            # -------------------------------------------------

            final_video.write_videofile(
                output_path,
                fps=self.fps,
                codec="libx264",
                audio_codec="aac",
                bitrate="4500k",
                preset="veryfast",
                threads=2,
                logger="bar",
            )

            # -------------------------------------------------
            # CHECK RESULT
            # -------------------------------------------------

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
                    f"{output_path} "
                    f"({size_mb:.1f} MB)"
                )

                return output_path

            logger.error(
                "❌ Final Sofia video was not created."
            )

            return ""

        except Exception as e:

            logger.exception(
                f"❌ Sofia video rendering failed: {e}"
            )

            return ""

        finally:

            # -------------------------------------------------
            # CLEANUP
            # -------------------------------------------------

            try:

                if final_video:
                    final_video.close()

            except Exception:
                pass

            try:

                if audio:
                    audio.close()

            except Exception:
                pass

            for clip in video_clips:

                try:
                    clip.close()

                except Exception:
                    pass


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("SOFIA LUXURY STORY VIDEO CREATOR TEST")
    print("=" * 60)

    creator = ProfessionalVideoCreator(
        resolution=(1280, 720),
        fps=24
    )

    test_topic = (
        "Sofia discovers the future "
        "of luxury technology"
    )

    test_script = """
    Sofia takes us inside the future
    of luxury technology.
    The world of luxury is changing
    faster than ever.
    New technology is transforming
    fashion and lifestyle.
    Sofia explores the most fascinating
    innovations around the world.
    From intelligent cars to futuristic homes.
    From smart fashion to incredible
    new experiences.
    Sofia shows us why luxury is no longer
    just about price.
    It is about experience, design,
    technology and imagination.
    The next generation of luxury
    will feel completely different.
    Sofia explores what this means
    for the future.
    And the journey is only beginning.
    """

    voice_file = None

    for vf in Path(
        "output"
    ).glob(
        "*.mp3"
    ):

        voice_file = str(vf)
        break

    if voice_file:

        result = (
            creator.create_professional_video(
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
        )

        if result:

            print()
            print(
                "✅ Sofia Luxury Story created:"
            )
            print(result)

        else:

            print()
            print(
                "❌ Sofia video creation failed."
            )

    else:

        print()
        print(
            "No voice-over found in output folder."
        )

    print()
    print("=" * 60)
    print(
        "Sofia Luxury Story test complete."
    )
    print("=" * 60)
