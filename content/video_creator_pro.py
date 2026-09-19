"""
SOFIA LUXURY STORY
FAST / RELIABLE CINEMATIC VERTICAL VIDEO CREATOR

Purpose:
Create approximately 5-minute Sofia luxury story videos
for GitHub Actions without unnecessary processing.

Output:
720 x 1280
9:16 vertical
24 FPS

Production strategy:
- 8 cinematic scenes
- Sofia AI images
- Voice-over
- Optional background music
- Lightweight subtitles
- Fast FFmpeg rendering
- No Pexels video downloading during production
- No expensive animated image movement
"""

import os
from pathlib import Path
from typing import Optional, List, Dict, Any

from loguru import logger
from dotenv import load_dotenv

from moviepy import (
    AudioFileClip,
    ImageClip,
    CompositeVideoClip,
    CompositeAudioClip,
    concatenate_videoclips,
    concatenate_audioclips,
    TextClip,
)

from moviepy.video.fx import FadeIn, FadeOut

from content.ai_image_gen import AIImageGenerator

load_dotenv()


class ProfessionalVideoCreator:
    """
    Fast and reliable Sofia Luxury Story video creator.
    """

    # ---------------------------------------------------------
    # PRODUCTION SETTINGS
    # ---------------------------------------------------------

    DEFAULT_RESOLUTION = (720, 1280)
    DEFAULT_FPS = 24

    # Exactly 8 scenes for approximately 5 minutes.
    MAX_SCENES = 8
    MIN_SCENES = 8

    # ---------------------------------------------------------
    # INITIALIZATION
    # ---------------------------------------------------------

    def __init__(
        self,
        resolution=(720, 1280),
        fps=24
    ):
        self.resolution = resolution
        self.fps = fps

        self.width, self.height = resolution

        # Always force portrait.
        if self.width >= self.height:
            logger.warning(
                "Landscape resolution detected. "
                "Switching to 720x1280 portrait."
            )

            self.resolution = self.DEFAULT_RESOLUTION
            self.width, self.height = self.resolution

        self.ai_image_gen = AIImageGenerator()

        self.sofia_identity = (
            "Sofia Luxury Story. "
            "Sofia is the central female protagonist. "
            "Keep Sofia visually recognizable throughout the movie. "
            "Elegant intelligent modern woman, "
            "consistent facial identity, "
            "cinematic realistic appearance, "
            "premium luxury aesthetic, "
            "high-end fashion, "
            "expressive eyes, "
            "natural skin texture, "
            "professional cinematic lighting, "
            "photorealistic movie still."
        )

        logger.info(
            f"SOFIA FAST RENDERER READY: "
            f"{self.width}x{self.height} "
            f"{self.fps}fps"
        )

    # =========================================================
    # BACKGROUND MUSIC
    # =========================================================

    def _get_bg_music(
        self,
        mood: str = "luxury"
    ) -> str:

        possible = [
            mood,
            "luxury",
            "tech",
            "action",
            "drama",
        ]

        for selected in possible:

            path = Path(
                f"data/assets/bg_music_{selected}.mp3"
            )

            if path.exists():
                return str(path)

        return ""

    # =========================================================
    # SCENE COUNT
    # =========================================================

    def _calculate_scene_count(
        self,
        duration: float
    ) -> int:

        # Reliability is more important than many scenes.
        # Eight scenes are enough for a five-minute story.
        return 8

    # =========================================================
    # PREPARE STORY SCENES
    # =========================================================

    def _prepare_story_scenes(
        self,
        script_text: str,
        scenes: Optional[List[Dict[str, Any]]],
        total_duration: float,
        topic: str,
    ) -> List[Dict[str, Any]]:

        prepared = []

        # -----------------------------------------------------
        # USE AI STRUCTURED SCENES WHEN AVAILABLE
        # -----------------------------------------------------

        if scenes:

            for index, scene in enumerate(
                scenes[:self.MAX_SCENES]
            ):

                if not isinstance(scene, dict):
                    continue

                location = str(
                    scene.get(
                        "location",
                        "luxury cinematic location"
                    )
                )

                action = str(
                    scene.get(
                        "action",
                        ""
                    )
                )

                emotion = str(
                    scene.get(
                        "emotion",
                        "determined"
                    )
                )

                visual_prompt = str(
                    scene.get(
                        "visual_prompt",
                        ""
                    )
                )

                narration = str(
                    scene.get(
                        "narration",
                        ""
                    )
                )

                dialogue = str(
                    scene.get(
                        "dialogue",
                        ""
                    )
                )

                description = " ".join(
                    [
                        location,
                        action,
                        emotion,
                        visual_prompt,
                    ]
                ).strip()

                prepared.append(
                    {
                        "scene_number": index + 1,
                        "location": location,
                        "action": action,
                        "emotion": emotion,
                        "visual_prompt": description,
                        "narration": narration,
                        "dialogue": dialogue,
                    }
                )

        # -----------------------------------------------------
        # FALLBACK FROM SCRIPT
        # -----------------------------------------------------

        if not prepared:

            sentences = [
                s.strip()
                for s in script_text.replace(
                    "\n",
                    " "
                ).split(".")
                if len(s.strip()) > 20
            ]

            if not sentences:
                sentences = [
                    (
                        "Sofia enters a luxurious cinematic "
                        f"world connected to {topic}"
                    )
                ]

            for index in range(8):

                sentence = sentences[
                    index % len(sentences)
                ]

                prepared.append(
                    {
                        "scene_number": index + 1,
                        "location": (
                            "cinematic luxury location"
                        ),
                        "action": sentence,
                        "emotion": "determined",
                        "visual_prompt": sentence,
                        "narration": sentence,
                        "dialogue": "",
                    }
                )

        # -----------------------------------------------------
        # FORCE EXACTLY 8 SCENES
        # -----------------------------------------------------

        if not prepared:
            prepared = [
                {
                    "scene_number": 1,
                    "location": "luxury mansion",
                    "action": "Sofia begins her journey",
                    "emotion": "determined",
                    "visual_prompt": (
                        "Sofia standing inside a "
                        "beautiful luxury mansion"
                    ),
                    "narration": "",
                    "dialogue": "",
                }
            ]

        original = list(prepared)

        while len(prepared) < self.MIN_SCENES:

            source = original[
                len(prepared) % len(original)
            ]

            duplicate = dict(source)

            duplicate[
                "scene_number"
            ] = len(prepared) + 1

            prepared.append(duplicate)

        prepared = prepared[:self.MAX_SCENES]

        # -----------------------------------------------------
        # DISTRIBUTE ENTIRE VOICEOVER
        # -----------------------------------------------------

        scene_duration = (
            total_duration / len(prepared)
        )

        for scene in prepared:

            scene["duration"] = max(
                5.0,
                scene_duration
            )

        return prepared

    # =========================================================
    # GENERATE SOFIA IMAGE
    # =========================================================

    def _generate_scene_image(
        self,
        scene: Dict[str, Any],
        index: int,
    ) -> str:

        output_dir = Path(
            "output/scene_images"
        )

        output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        visual = str(
            scene.get(
                "visual_prompt",
                ""
            )
        )

        location = str(
            scene.get(
                "location",
                ""
            )
        )

        action = str(
            scene.get(
                "action",
                ""
            )
        )

        emotion = str(
            scene.get(
                "emotion",
                ""
            )
        )

        prompt = (
            f"{self.sofia_identity} "
            f"Scene {index + 1}. "
            f"Sofia is actively present. "
            f"Location: {location}. "
            f"Action: {action}. "
            f"Emotion: {emotion}. "
            f"Visual direction: {visual}. "
            "Same Sofia identity as previous scenes. "
            "Cinematic movie frame. "
            "Professional lighting. "
            "Luxury production design. "
            "Realistic environment. "
            "Natural anatomy. "
            "No text. "
            "No watermark. "
            "Vertical 9:16 composition."
        )

        filename = (
            f"sofia_movie_scene_"
            f"{index + 1:03d}.jpg"
        )

        try:

            logger.info(
                f"Generating Sofia scene "
                f"{index + 1}/{self.MAX_SCENES}"
            )

            result = (
                self.ai_image_gen.generate_image(
                    prompt=prompt,
                    style="realistic cinematic",
                    width=self.width,
                    height=self.height,
                    filename=filename,
                    use_reference=True,
                )
            )

            if result:
                return result

        except TypeError:

            # Compatibility with older generator.
            try:

                result = (
                    self.ai_image_gen.generate_image(
                        prompt=prompt,
                        style="realistic cinematic",
                        width=self.width,
                        height=self.height,
                        filename=filename,
                    )
                )

                if result:
                    return result

            except Exception as e:

                logger.warning(
                    f"Fallback image generation failed: {e}"
                )

        except Exception as e:

            logger.warning(
                f"AI image generation failed: {e}"
            )

        return ""

    # =========================================================
    # IMAGE CLIP
    # =========================================================

    def _create_image_clip(
        self,
        image_path: str,
        duration: float,
    ):

        try:

            clip = ImageClip(
                image_path,
                duration=duration
            )

            # Fit image to 9:16.
            scale_w = (
                self.width / clip.w
            )

            scale_h = (
                self.height / clip.h
            )

            scale = max(
                scale_w,
                scale_h
            )

            clip = clip.resized(
                scale
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
                f"Image clip failed: {e}"
            )

            return None

    # =========================================================
    # SUBTITLE
    # =========================================================

    def _make_subtitle(
        self,
        text: str,
        duration: float
    ):

        if not text:
            return None

        try:

            text = str(text).strip()

            if not text:
                return None

            if len(text) > 120:
                text = text[:117] + "..."

            subtitle = TextClip(
                text=text,
                font_size=34,
                color="white",
                stroke_color="black",
                stroke_width=2,
                size=(
                    self.width - 80,
                    150
                ),
                method="caption",
            )

            subtitle = (
                subtitle
                .with_position(
                    (
                        "center",
                        self.height - 210
                    )
                )
                .with_duration(
                    duration
                )
            )

            return subtitle

        except Exception as e:

            logger.warning(
                f"Subtitle skipped: {e}"
            )

            return None

    # =========================================================
    # TRANSITION
    # =========================================================

    def _apply_transition(
        self,
        clip,
        index: int
    ):

        try:

            if index == 0:

                clip = clip.with_effects(
                    [
                        FadeIn(0.35)
                    ]
                )

            elif index < self.MAX_SCENES - 1:

                clip = clip.with_effects(
                    [
                        FadeIn(0.20)
                    ]
                )

            return clip

        except Exception:

            return clip

    # =========================================================
    # MAIN VIDEO CREATOR
    # =========================================================

    def create_professional_video(
        self,
        voiceover_path: str,
        topic: str,
        script_text: str = "",
        niche: str = "luxury",
        style: str = "cinematic",
        add_music: bool = True,
        output_path: str = (
            "output/sofia_luxury_story.mp4"
        ),
        scenes: Optional[
            List[Dict[str, Any]]
        ] = None,
    ) -> str:

        logger.info(
            "================================================"
        )

        logger.info(
            "SOFIA LUXURY STORY - FAST MODE"
        )

        logger.info(
            f"Topic: {str(topic)[:100]}"
        )

        logger.info(
            "================================================"
        )

        voice_path = Path(
            voiceover_path
        )

        if not voice_path.exists():

            logger.error(
                f"Voiceover not found: "
                f"{voiceover_path}"
            )

            return ""

        audio = None
        music = None
        final_video = None
        video_clips = []

        try:

            # -------------------------------------------------
            # AUDIO
            # -------------------------------------------------

            audio = AudioFileClip(
                str(voice_path)
            )

            total_duration = float(
                audio.duration
            )

            logger.info(
                f"Voice-over duration: "
                f"{total_duration:.1f}s"
            )

            # -------------------------------------------------
            # STORY
            # -------------------------------------------------

            story_scenes = (
                self._prepare_story_scenes(
                    script_text=script_text,
                    scenes=scenes,
                    total_duration=total_duration,
                    topic=str(topic),
                )
            )

            logger.info(
                f"Using exactly "
                f"{len(story_scenes)} "
                f"cinematic scenes."
            )

            # -------------------------------------------------
            # IMPORTANT:
            # NO PEXELS VIDEO PROCESSING HERE.
            #
            # This is intentional.
            # It prevents downloading and decoding multiple
            # large MP4 files on the GitHub runner.
            # -------------------------------------------------

            logger.info(
                "Stock video processing disabled "
                "for fast reliable production."
            )

            # -------------------------------------------------
            # CREATE SCENES
            # -------------------------------------------------

            for index, scene in enumerate(
                story_scenes
            ):

                duration = float(
                    scene.get(
                        "duration",
                        total_duration / 8
                    )
                )

                logger.info(
                    "----------------------------------------"
                )

                logger.info(
                    f"SCENE {index + 1}/"
                    f"{len(story_scenes)}"
                )

                clip = None

                # ---------------------------------------------
                # GENERATE SOFIA IMAGE
                # ---------------------------------------------

                image_path = (
                    self._generate_scene_image(
                        scene,
                        index
                    )
                )

                if image_path:

                    clip = (
                        self._create_image_clip(
                            image_path,
                            duration
                        )
                    )

                # ---------------------------------------------
                # FALLBACK TO PREVIOUS SOFIA IMAGE
                # ---------------------------------------------

                if clip is None:

                    previous_images = sorted(
                        Path(
                            "output/scene_images"
                        ).glob(
                            "sofia_movie_scene_*.jpg"
                        )
                    )

                    if previous_images:

                        fallback_image = (
                            str(
                                previous_images[-1]
                            )
                        )

                        logger.warning(
                            "Using previous Sofia "
                            "image as scene fallback."
                        )

                        clip = (
                            self._create_image_clip(
                                fallback_image,
                                duration
                            )
                        )

                # ---------------------------------------------
                # FINAL FALLBACK
                # ---------------------------------------------

                if clip is None:

                    logger.warning(
                        "No image available. "
                        "Using black cinematic frame."
                    )

                    from moviepy import ColorClip

                    clip = ColorClip(
                        size=self.resolution,
                        color=(
                            10,
                            10,
                            14
                        ),
                        duration=duration
                    )

                # ---------------------------------------------
                # LIGHTWEIGHT SUBTITLE
                # ---------------------------------------------

                subtitle_text = (
                    scene.get(
                        "dialogue"
                    )
                    or scene.get(
                        "narration"
                    )
                    or ""
                )

                subtitle = (
                    self._make_subtitle(
                        subtitle_text,
                        duration
                    )
                )

                if subtitle:

                    clip = CompositeVideoClip(
                        [
                            clip,
                            subtitle
                        ],
                        size=self.resolution
                    )

                # ---------------------------------------------
                # LIGHT TRANSITION
                # ---------------------------------------------

                clip = (
                    self._apply_transition(
                        clip,
                        index
                    )
                )

                video_clips.append(
                    clip
                )

                logger.info(
                    f"SCENE {index + 1}/"
                    f"{len(story_scenes)} READY"
                )

            # -------------------------------------------------
            # VERIFY SCENES
            # -------------------------------------------------

            if not video_clips:

                logger.error(
                    "No video scenes were created."
                )

                return ""

            logger.info(
                "================================================"
            )

            logger.info(
                "ALL 8 SCENES READY"
            )

            logger.info(
                "Combining scenes..."
            )

            logger.info(
                "================================================"
            )

            # -------------------------------------------------
            # COMBINE
            # -------------------------------------------------

            final_video = (
                concatenate_videoclips(
                    video_clips,
                    method="compose"
                )
            )

            # -------------------------------------------------
            # EXACT AUDIO LENGTH
            # -------------------------------------------------

            if final_video.duration > total_duration:

                final_video = (
                    final_video
                    .subclipped(
                        0,
                        total_duration
                    )
                )

            elif final_video.duration < total_duration:

                logger.warning(
                    "Video is slightly shorter "
                    "than voice-over. "
                    "Using available duration."
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

                if music_path:

                    try:

                        logger.info(
                            "Adding background music..."
                        )

                        music = AudioFileClip(
                            music_path
                        )

                        if music.duration < total_duration:

                            repeat_count = (
                                int(
                                    total_duration /
                                    music.duration
                                )
                                + 1
                            )

                            music_parts = []

                            for _ in range(
                                repeat_count
                            ):

                                music_parts.append(
                                    AudioFileClip(
                                        music_path
                                    )
                                )

                            music = (
                                concatenate_audioclips(
                                    music_parts
                                )
                            )

                        music = (
                            music
                            .subclipped(
                                0,
                                total_duration
                            )
                            .with_volume_scaled(
                                0.05
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
                            "Background music added."
                        )

                    except Exception as e:

                        logger.warning(
                            f"Music skipped: {e}"
                        )

            # -------------------------------------------------
            # OUTPUT
            # -------------------------------------------------

            output = Path(
                output_path
            )

            output.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            # -------------------------------------------------
            # FINAL RENDER
            # -------------------------------------------------

            logger.info(
                "================================================"
            )

            logger.info(
                "RENDERING FINAL SOFIA VIDEO"
            )

            logger.info(
                "720x1280 / 24 FPS / FAST MODE"
            )

            logger.info(
                "================================================"
            )

            final_video.write_videofile(
                str(output),

                fps=self.fps,

                codec="libx264",

                audio_codec="aac",

                # Smaller and faster than the previous 4500k.
                bitrate="3000k",

                # Fastest practical preset for GitHub runner.
                preset="ultrafast",

                # Do not use excessive CPU threads.
                threads=2,

                # Reduce MoviePy console overhead.
                logger=None,
            )

            # -------------------------------------------------
            # VERIFY OUTPUT
            # -------------------------------------------------

            if output.exists():

                size_mb = (
                    output.stat().st_size
                    /
                    (1024 * 1024)
                )

                logger.info(
                    "================================================"
                )

                logger.info(
                    f"SOFIA VIDEO CREATED SUCCESSFULLY"
                )

                logger.info(
                    f"File: {output}"
                )

                logger.info(
                    f"Size: {size_mb:.1f} MB"
                )

                logger.info(
                    "================================================"
                )

                return str(output)

            logger.error(
                "Final video file was not created."
            )

            return ""

        except Exception as e:

            logger.exception(
                f"Sofia video creation failed: {e}"
            )

            return ""

        finally:

            # -------------------------------------------------
            # CLEANUP
            # -------------------------------------------------

            logger.info(
                "Cleaning video resources..."
            )

            try:

                if final_video:
                    final_video.close()

            except Exception:
                pass

            try:

                if music:
                    music.close()

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

            logger.info(
                "Video resources cleaned."
            )


# =============================================================
# TEST
# =============================================================

if __name__ == "__main__":

    print(
        "\n"
        + "=" * 65
    )

    print(
        "SOFIA LUXURY STORY"
    )

    print(
        "FAST VERTICAL VIDEO CREATOR"
    )

    print(
        "=" * 65
    )

    creator = ProfessionalVideoCreator()

    print(
        f"\nResolution: "
        f"{creator.width}x{creator.height}"
    )

    print(
        f"Aspect ratio: "
        f"{creator.width / creator.height:.3f}"
    )

    print(
        f"FPS: "
        f"{creator.fps}"
    )

    print(
        f"Scenes: "
        f"{creator.MIN_SCENES}"
    )

    print(
        "\nReady for Sofia Luxury Story production."
    )
