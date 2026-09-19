"""
SOFIA LUXURY STORY
CINEMATIC VERTICAL MOVIE CREATOR

Creates a connected luxury-story video with:
- 12 cinematic story beats
- Sofia as the central character
- Different visuals for different story beats
- Pexels supporting visuals when available
- Sofia AI visuals when available
- Voice-over
- Subtitles
- Background music
- 720x1280 vertical output
- 24 FPS
"""

import os
import re
import requests
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
    ColorClip,
)

from moviepy.video.fx import FadeIn, FadeOut

from content.ai_image_gen import AIImageGenerator

load_dotenv()


class ProfessionalVideoCreator:
    """
    Cinematic Sofia luxury-story creator.
    """

    DEFAULT_RESOLUTION = (720, 1280)
    DEFAULT_FPS = 24

    # More story beats = more visual changes.
    MIN_SCENES = 12
    MAX_SCENES = 12

    def __init__(
        self,
        resolution=(720, 1280),
        fps=24
    ):
        self.resolution = resolution
        self.fps = fps

        self.width, self.height = resolution

        if self.width >= self.height:
            self.resolution = self.DEFAULT_RESOLUTION
            self.width, self.height = self.resolution

        self.ai_image_gen = AIImageGenerator()

        self.pexels_key = os.getenv(
            "PEXELS_API_KEY",
            ""
        )

        self.sofia_identity = (
            "Sofia is the central female protagonist "
            "of a premium cinematic luxury movie. "
            "Elegant intelligent modern woman, "
            "consistent recognizable facial identity, "
            "natural realistic skin, expressive eyes, "
            "luxury fashion, sophisticated appearance, "
            "photorealistic, cinematic lighting, "
            "high-end movie production."
        )

        logger.info(
            f"SOFIA CINEMATIC MOVIE CREATOR READY: "
            f"{self.width}x{self.height} "
            f"{self.fps}fps"
        )

    # =========================================================
    # MUSIC
    # =========================================================

    def _get_bg_music(self, mood="luxury") -> str:

        for selected in (
            mood,
            "luxury",
            "tech",
            "action",
            "drama"
        ):
            path = Path(
                f"data/assets/bg_music_{selected}.mp3"
            )

            if path.exists():
                return str(path)

        return ""

    # =========================================================
    # STORY SCENES
    # =========================================================

    def _prepare_story_scenes(
        self,
        script_text: str,
        scenes: Optional[List[Dict[str, Any]]],
        total_duration: float,
        topic: str,
    ) -> List[Dict[str, Any]]:

        prepared = []

        if scenes:

            for index, scene in enumerate(scenes):

                if not isinstance(scene, dict):
                    continue

                narration = str(
                    scene.get(
                        "narration",
                        ""
                    )
                ).strip()

                dialogue = str(
                    scene.get(
                        "dialogue",
                        ""
                    )
                ).strip()

                location = str(
                    scene.get(
                        "location",
                        "luxury location"
                    )
                ).strip()

                action = str(
                    scene.get(
                        "action",
                        ""
                    )
                ).strip()

                emotion = str(
                    scene.get(
                        "emotion",
                        "determined"
                    )
                ).strip()

                visual_prompt = str(
                    scene.get(
                        "visual_prompt",
                        ""
                    )
                ).strip()

                if not (
                    narration
                    or dialogue
                    or action
                    or visual_prompt
                ):
                    continue

                prepared.append({
                    "scene_number": index + 1,
                    "location": location,
                    "action": action,
                    "emotion": emotion,
                    "visual_prompt": visual_prompt,
                    "narration": narration,
                    "dialogue": dialogue,
                })

        # -----------------------------------------------------
        # FALLBACK IF STRUCTURED SCENES ARE NOT AVAILABLE
        # -----------------------------------------------------

        if not prepared:

            sentences = [
                s.strip()
                for s in re.split(
                    r"(?<=[.!?])\s+",
                    script_text.replace(
                        "\n",
                        " "
                    )
                )
                if len(s.strip()) > 20
            ]

            if not sentences:
                sentences = [
                    (
                        f"Sofia enters a luxurious world "
                        f"connected to {topic}."
                    )
                ]

            for index, sentence in enumerate(
                sentences[:self.MAX_SCENES]
            ):

                prepared.append({
                    "scene_number": index + 1,
                    "location": "luxury cinematic location",
                    "action": sentence,
                    "emotion": "determined",
                    "visual_prompt": sentence,
                    "narration": sentence,
                    "dialogue": "",
                })

        if not prepared:
            prepared = [{
                "scene_number": 1,
                "location": "luxury mansion",
                "action": "Sofia begins her journey.",
                "emotion": "determined",
                "visual_prompt": (
                    "Sofia standing inside "
                    "a magnificent luxury mansion."
                ),
                "narration": "",
                "dialogue": "",
            }]

        # -----------------------------------------------------
        # DO NOT INVENT NEW STORY CONTENT.
        #
        # If the story generator gives fewer than 12 scenes,
        # distribute those scenes across the movie rather than
        # blindly repeating the same image.
        # -----------------------------------------------------

        if len(prepared) > self.MAX_SCENES:
            prepared = prepared[:self.MAX_SCENES]

        scene_duration = (
            total_duration / len(prepared)
        )

        for scene in prepared:
            scene["duration"] = max(
                4.0,
                scene_duration
            )

        return prepared

    # =========================================================
    # CLEAN SEARCH QUERY
    # =========================================================

    def _make_visual_query(
        self,
        scene: Dict[str, Any]
    ) -> str:

        location = str(
            scene.get("location", "")
        )

        action = str(
            scene.get("action", "")
        )

        visual = str(
            scene.get("visual_prompt", "")
        )

        combined = (
            f"{location} {action} {visual}"
        )

        # Remove excessively long AI prompts.
        words = combined.split()

        query = " ".join(
            words[:12]
        )

        # Remove punctuation that can make poor searches.
        query = re.sub(
            r"[^a-zA-Z0-9\s-]",
            " ",
            query
        )

        query = " ".join(
            query.split()
        )

        if not query:
            query = "luxury lifestyle technology"

        return query[:120]

    # =========================================================
    # PEXELS PHOTO
    # =========================================================

    def _download_pexels_photo(
        self,
        scene: Dict[str, Any],
        index: int
    ) -> str:

        if not self.pexels_key:
            return ""

        query = self._make_visual_query(
            scene
        )

        logger.info(
            f"Searching supporting visual: {query}"
        )

        try:

            response = requests.get(
                "https://api.pexels.com/v1/search",
                headers={
                    "Authorization":
                        self.pexels_key
                },
                params={
                    "query": query,
                    "orientation": "portrait",
                    "size": "medium",
                    "per_page": 5,
                },
                timeout=15,
            )

            if response.status_code != 200:
                logger.warning(
                    f"Pexels returned "
                    f"{response.status_code}"
                )
                return ""

            data = response.json()

            photos = data.get(
                "photos",
                []
            )

            if not photos:
                logger.warning(
                    "No Pexels visual found."
                )
                return ""

            # Pick a different result when possible.
            photo = photos[
                index % len(photos)
            ]

            src = photo.get(
                "src",
                {}
            )

            image_url = (
                src.get("portrait")
                or src.get("large")
                or src.get("medium")
            )

            if not image_url:
                return ""

            output_dir = Path(
                "output/supporting_visuals"
            )

            output_dir.mkdir(
                parents=True,
                exist_ok=True
            )

            output_file = (
                output_dir
                /
                f"movie_visual_{index + 1:03d}.jpg"
            )

            image_response = requests.get(
                image_url,
                timeout=20
            )

            if image_response.status_code != 200:
                return ""

            output_file.write_bytes(
                image_response.content
            )

            if output_file.exists() and (
                output_file.stat().st_size > 5000
            ):
                logger.info(
                    f"Supporting visual ready: "
                    f"{output_file}"
                )

                return str(output_file)

        except Exception as e:

            logger.warning(
                f"Pexels visual failed: {e}"
            )

        return ""

    # =========================================================
    # SOFIA AI IMAGE
    # =========================================================

    def _generate_sofia_image(
        self,
        scene: Dict[str, Any],
        index: int
    ) -> str:

        output_dir = Path(
            "output/scene_images"
        )

        output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        location = str(
            scene.get(
                "location",
                "luxury location"
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

        visual = str(
            scene.get(
                "visual_prompt",
                ""
            )
        )

        prompt = (
            f"{self.sofia_identity} "
            f"Sofia is actively involved in this scene. "
            f"Location: {location}. "
            f"Action: {action}. "
            f"Emotion: {emotion}. "
            f"Visual direction: {visual}. "
            "Make the image look like a frame from "
            "an expensive Hollywood luxury thriller. "
            "Strong cinematic composition. "
            "Natural body position. "
            "Sophisticated wardrobe. "
            "Realistic environment. "
            "No text. No watermark. "
            "Portrait 9:16 composition."
        )

        filename = (
            f"sofia_cinematic_"
            f"{index + 1:03d}.jpg"
        )

        try:

            logger.info(
                f"Generating Sofia cinematic visual "
                f"{index + 1}"
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
                    f"Sofia image fallback failed: {e}"
                )

        except Exception as e:

            logger.warning(
                f"Sofia image generation failed: {e}"
            )

        return ""

    # =========================================================
    # CHOOSE VISUAL
    # =========================================================

    def _get_scene_visual(
        self,
        scene: Dict[str, Any],
        index: int
    ) -> str:

        # Every third scene tries to make Sofia the focus.
        # Other scenes prioritize story-supporting visuals.
        use_sofia = (
            index % 3 == 0
            or index == 1
            or index == 2
        )

        if use_sofia:

            sofia = self._generate_sofia_image(
                scene,
                index
            )

            if sofia:
                return sofia

        supporting = (
            self._download_pexels_photo(
                scene,
                index
            )
        )

        if supporting:
            return supporting

        sofia = self._generate_sofia_image(
            scene,
            index
        )

        if sofia:
            return sofia

        return ""

    # =========================================================
    # IMAGE CLIP
    # =========================================================

    def _create_image_clip(
        self,
        image_path: str,
        duration: float
    ):

        try:

            clip = ImageClip(
                image_path,
                duration=duration
            )

            scale = max(
                self.width / clip.w,
                self.height / clip.h
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
    # SUBTITLES
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

            # Keep subtitles readable.
            if len(text) > 140:
                text = text[:137] + "..."

            subtitle = TextClip(
                text=text,
                font_size=32,
                color="white",
                stroke_color="black",
                stroke_width=2,
                size=(
                    self.width - 70,
                    170
                ),
                method="caption",
            )

            return (
                subtitle
                .with_position(
                    (
                        "center",
                        self.height - 220
                    )
                )
                .with_duration(
                    duration
                )
            )

        except Exception as e:

            logger.warning(
                f"Subtitle skipped: {e}"
            )

            return None

    # =========================================================
    # MAIN CREATOR
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
            "SOFIA LUXURY CINEMATIC MOVIE"
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
                f"Voiceover not found: {voiceover_path}"
            )
            return ""

        audio = None
        music = None
        final_video = None
        video_clips = []

        try:

            # -------------------------------------------------
            # VOICE
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
                f"Story contains "
                f"{len(story_scenes)} visual beats."
            )

            # -------------------------------------------------
            # CREATE VISUALS
            # -------------------------------------------------

            for index, scene in enumerate(
                story_scenes
            ):

                duration = float(
                    scene.get(
                        "duration",
                        total_duration /
                        len(story_scenes)
                    )
                )

                logger.info(
                    "----------------------------------------"
                )

                logger.info(
                    f"🎬 STORY BEAT "
                    f"{index + 1}/"
                    f"{len(story_scenes)}"
                )

                logger.info(
                    f"Location: "
                    f"{scene.get('location', '')}"
                )

                logger.info(
                    f"Action: "
                    f"{scene.get('action', '')[:120]}"
                )

                image_path = (
                    self._get_scene_visual(
                        scene,
                        index
                    )
                )

                clip = None

                if image_path:

                    clip = (
                        self._create_image_clip(
                            image_path,
                            duration
                        )
                    )

                if clip is None:

                    logger.warning(
                        "Visual unavailable. "
                        "Using cinematic fallback."
                    )

                    clip = ColorClip(
                        size=self.resolution,
                        color=(
                            12,
                            12,
                            18
                        ),
                        duration=duration
                    )

                # -------------------------------------------------
                # SUBTITLE
                # -------------------------------------------------

                subtitle_text = (
                    scene.get("dialogue")
                    or scene.get("narration")
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

                # -------------------------------------------------
                # TRANSITIONS
                # -------------------------------------------------

                try:

                    effects = []

                    if index == 0:
                        effects.append(
                            FadeIn(0.4)
                        )

                    if index > 0:
                        effects.append(
                            FadeIn(0.2)
                        )

                    if effects:
                        clip = clip.with_effects(
                            effects
                        )

                except Exception:
                    pass

                video_clips.append(
                    clip
                )

                logger.info(
                    f"STORY BEAT "
                    f"{index + 1}/"
                    f"{len(story_scenes)} READY"
                )

            if not video_clips:
                logger.error(
                    "No visual scenes created."
                )
                return ""

            # -------------------------------------------------
            # COMBINE
            # -------------------------------------------------

            logger.info(
                "Combining cinematic scenes..."
            )

            final_video = (
                concatenate_videoclips(
                    video_clips,
                    method="compose"
                )
            )

            # Match voice duration.
            if final_video.duration > total_duration:

                final_video = (
                    final_video.subclipped(
                        0,
                        total_duration
                    )
                )

            # -------------------------------------------------
            # VOICE
            # -------------------------------------------------

            final_video = (
                final_video.with_audio(
                    audio
                )
            )

            # -------------------------------------------------
            # MUSIC
            # -------------------------------------------------

            if add_music:

                music_path = (
                    self._get_bg_music(
                        "luxury"
                    )
                )

                if music_path:

                    try:

                        music = AudioFileClip(
                            music_path
                        )

                        if music.duration < total_duration:

                            repeat_count = (
                                int(
                                    total_duration /
                                    music.duration
                                ) + 1
                            )

                            pieces = []

                            for _ in range(
                                repeat_count
                            ):
                                pieces.append(
                                    AudioFileClip(
                                        music_path
                                    )
                                )

                            music = (
                                concatenate_audioclips(
                                    pieces
                                )
                            )

                        music = (
                            music
                            .subclipped(
                                0,
                                total_duration
                            )
                            .with_volume_scaled(
                                0.045
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
                            final_video.with_audio(
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
            # RENDER
            # -------------------------------------------------

            output = Path(
                output_path
            )

            output.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            logger.info(
                "================================================"
            )

            logger.info(
                "🎥 RENDERING FINAL CINEMATIC MOVIE"
            )

            logger.info(
                "720x1280 / 24 FPS"
            )

            logger.info(
                "================================================"
            )

            final_video.write_videofile(
                str(output),
                fps=self.fps,
                codec="libx264",
                audio_codec="aac",
                bitrate="3000k",
                preset="ultrafast",
                threads=2,
                logger=None,
            )

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
                    "🎬 SOFIA CINEMATIC MOVIE COMPLETE"
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
                "Video file was not created."
            )

            return ""

        except Exception as e:

            logger.exception(
                f"Cinematic video creation failed: {e}"
            )

            return ""

        finally:

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


if __name__ == "__main__":

    print("=" * 60)
    print("SOFIA LUXURY CINEMATIC MOVIE CREATOR")
    print("=" * 60)

    creator = ProfessionalVideoCreator()

    print(
        f"Resolution: "
        f"{creator.width}x{creator.height}"
    )

    print(
        f"FPS: {creator.fps}"
    )

    print(
        f"Story beats: {creator.MIN_SCENES}"
    )

    print("Ready.")
