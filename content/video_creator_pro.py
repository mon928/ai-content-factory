"""
SOFIA LUXURY STORY
FAST CINEMATIC VERTICAL MOVIE CREATOR

Designed for:
- Sofia visible throughout the movie
- Luxury cinematic storytelling
- Faster visual pacing
- Multiple shots from each Sofia image
- 720x1280 vertical video
- 24 FPS
- Voice-over
- Subtitles
- Background music
- Lightweight FFmpeg rendering
- Sofia AI/reference images
- Local Sofia fallback support

IMPORTANT DESIGN:

One Sofia image is generated for each major story scene.

That image is then turned into several cinematic
micro-shots using different framing/crops.

This gives the viewer frequent visual changes without
requiring a large number of expensive AI image generations.
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

from moviepy.video.fx import FadeIn

from content.ai_image_gen import AIImageGenerator

load_dotenv()


class ProfessionalVideoCreator:
    """
    Fast cinematic Sofia luxury movie creator.
    """

    DEFAULT_RESOLUTION = (720, 1280)
    DEFAULT_FPS = 24

    # The story generator now creates 8 major scenes.
    MIN_SCENES = 8
    MAX_SCENES = 8

    # Each Sofia image becomes multiple visual shots.
    SHOTS_PER_SCENE = 4

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

        # -----------------------------------------------------
        # SOFIA IDENTITY
        # -----------------------------------------------------

        self.sofia_identity = (
            "Sofia is the central female protagonist "
            "of a premium cinematic luxury movie. "
            "Elegant intelligent modern woman, "
            "consistent recognizable facial identity, "
            "natural realistic skin, expressive eyes, "
            "luxury fashion, sophisticated appearance, "
            "photorealistic, cinematic lighting, "
            "high-end movie production. "
            "Keep Sofia's facial identity consistent "
            "throughout the entire story."
        )

        logger.info(
            f"SOFIA FAST CINEMATIC MOVIE CREATOR READY: "
            f"{self.width}x{self.height} "
            f"{self.fps}fps"
        )

    # =========================================================
    # MUSIC
    # =========================================================

    def _get_bg_music(
        self,
        mood="luxury"
    ) -> str:

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

                shot_type = str(
                    scene.get(
                        "shot_type",
                        ""
                    )
                ).strip()

                appearance = str(
                    scene.get(
                        "sofia_appearance",
                        ""
                    )
                ).strip()

                luxury_detail = str(
                    scene.get(
                        "luxury_detail",
                        ""
                    )
                ).strip()

                continuity = str(
                    scene.get(
                        "continuity",
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
                    "shot_type": shot_type,
                    "sofia_appearance": appearance,
                    "luxury_detail": luxury_detail,
                    "continuity": continuity,
                    "sofia_visible": True,
                })

        # -----------------------------------------------------
        # FALLBACK FROM SCRIPT
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

            # Split the script into approximately 8 groups.
            group_size = max(
                1,
                len(sentences) //
                self.MIN_SCENES
            )

            for index in range(
                self.MIN_SCENES
            ):

                start = index * group_size

                if index == self.MIN_SCENES - 1:
                    group = sentences[start:]
                else:
                    group = sentences[
                        start:start + group_size
                    ]

                if not group:
                    group = [
                        sentences[-1]
                    ]

                text = " ".join(group)

                prepared.append({
                    "scene_number": index + 1,
                    "location": "luxury cinematic location",
                    "action": text,
                    "emotion": "determined",
                    "visual_prompt": text,
                    "narration": text,
                    "dialogue": "",
                    "shot_type": "",
                    "sofia_appearance": "",
                    "luxury_detail": "",
                    "continuity": "",
                    "sofia_visible": True,
                })

        # -----------------------------------------------------
        # SAFETY
        # -----------------------------------------------------

        if not prepared:

            prepared = [{
                "scene_number": 1,
                "location": "luxury mansion",
                "action": "Sofia begins her journey.",
                "emotion": "determined",
                "visual_prompt": (
                    "Sofia inside a magnificent "
                    "luxury mansion."
                ),
                "narration": "",
                "dialogue": "",
                "shot_type": "wide",
                "sofia_appearance": "",
                "luxury_detail": "",
                "continuity": "",
                "sofia_visible": True,
            }]

        prepared = prepared[
            :self.MAX_SCENES
        ]

        # -----------------------------------------------------
        # CALCULATE SCENE DURATION FROM SPOKEN WORDS
        #
        # This is important.
        #
        # A scene with more narration gets more time.
        # A short action scene gets less time.
        # -----------------------------------------------------

        word_counts = []

        for scene in prepared:

            spoken = (
                str(
                    scene.get(
                        "narration",
                        ""
                    )
                )
                + " "
                + str(
                    scene.get(
                        "dialogue",
                        ""
                    )
                )
            ).strip()

            count = len(
                spoken.split()
            )

            word_counts.append(
                max(1, count)
            )

        total_words = sum(
            word_counts
        )

        # Minimum visual time per scene.
        minimum_scene_time = 12.0

        minimum_total = (
            minimum_scene_time *
            len(prepared)
        )

        available_duration = max(
            total_duration,
            minimum_total
        )

        remaining_duration = (
            available_duration -
            minimum_total
        )

        for index, scene in enumerate(
            prepared
        ):

            share = (
                word_counts[index]
                /
                max(1, total_words)
            )

            duration = (
                minimum_scene_time
                +
                remaining_duration * share
            )

            scene["duration"] = float(
                duration
            )

        # Correct rounding drift.
        calculated_total = sum(
            scene["duration"]
            for scene in prepared
        )

        correction = (
            total_duration -
            calculated_total
        )

        prepared[-1]["duration"] += correction

        # Never allow an invalid final scene.
        prepared[-1]["duration"] = max(
            8.0,
            prepared[-1]["duration"]
        )

        return prepared

    # =========================================================
    # VISUAL QUERY
    # =========================================================

    def _make_visual_query(
        self,
        scene: Dict[str, Any]
    ) -> str:

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

        visual = str(
            scene.get(
                "visual_prompt",
                ""
            )
        )

        combined = (
            f"{location} "
            f"{action} "
            f"{visual}"
        )

        words = combined.split()

        query = " ".join(
            words[:14]
        )

        query = re.sub(
            r"[^a-zA-Z0-9\s-]",
            " ",
            query
        )

        query = " ".join(
            query.split()
        )

        if not query:
            query = (
                "luxury hotel city "
                "cinematic lifestyle"
            )

        return query[:120]

    # =========================================================
    # PEXELS SUPPORTING PHOTO
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
                timeout=12,
            )

            if response.status_code != 200:
                return ""

            data = response.json()

            photos = data.get(
                "photos",
                []
            )

            if not photos:
                return ""

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
                f"movie_support_{index + 1:03d}.jpg"
            )

            image_response = requests.get(
                image_url,
                timeout=15
            )

            if image_response.status_code != 200:
                return ""

            output_file.write_bytes(
                image_response.content
            )

            if (
                output_file.exists()
                and
                output_file.stat().st_size > 5000
            ):

                return str(
                    output_file
                )

        except Exception as e:

            logger.warning(
                f"Pexels support failed: {e}"
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

        appearance = str(
            scene.get(
                "sofia_appearance",
                ""
            )
        )

        luxury_detail = str(
            scene.get(
                "luxury_detail",
                ""
            )
        )

        shot_type = str(
            scene.get(
                "shot_type",
                ""
            )
        )

        continuity = str(
            scene.get(
                "continuity",
                ""
            )
        )

        prompt = (
            f"{self.sofia_identity} "

            f"IMPORTANT: Sofia must be clearly visible "
            f"and must be the main subject. "

            f"Location: {location}. "

            f"Time and atmosphere: "
            f"{scene.get('time', 'cinematic lighting')}. "

            f"Sofia action: {action}. "

            f"Sofia emotion: {emotion}. "

            f"Sofia appearance: {appearance}. "

            f"Primary shot framing: {shot_type}. "

            f"Luxury detail: {luxury_detail}. "

            f"Story continuity: {continuity}. "

            f"Visual direction: {visual}. "

            "Create a photorealistic frame from an "
            "expensive luxury movie. "

            "Sofia must not be replaced by another woman. "

            "Keep her face recognizable and consistent. "

            "Natural anatomy. "
            "Natural hands. "
            "Natural posture. "
            "Realistic environment. "
            "Premium cinematic lighting. "
            "Sophisticated wardrobe. "
            "Strong composition. "
            "No text. "
            "No watermark. "
            "Portrait 9:16."
        )

        filename = (
            f"sofia_cinematic_"
            f"{index + 1:03d}.jpg"
        )

        try:

            logger.info(
                f"Generating Sofia visual "
                f"{index + 1}/"
                f"{len(scene.get('_all_scenes', [])) or 8}"
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
    # CHOOSE SCENE VISUAL
    # =========================================================

    def _get_scene_visual(
        self,
        scene: Dict[str, Any],
        index: int,
        previous_sofia_image: str = ""
    ) -> str:

        # -----------------------------------------------------
        # IMPORTANT:
        #
        # Sofia is ALWAYS attempted first.
        #
        # This is different from the previous version,
        # where many scenes were allowed to use Pexels first.
        # -----------------------------------------------------

        sofia = self._generate_sofia_image(
            scene,
            index
        )

        if sofia:
            return sofia

        # If generation fails, reuse the previous Sofia image.
        # This keeps Sofia visible instead of replacing her
        # with a random stock woman/location.
        if previous_sofia_image:
            logger.warning(
                "New Sofia image unavailable. "
                "Reusing previous Sofia image."
            )

            return previous_sofia_image

        # Pexels is now only an emergency fallback.
        supporting = (
            self._download_pexels_photo(
                scene,
                index
            )
        )

        if supporting:
            return supporting

        return ""

    # =========================================================
    # IMAGE CLIP
    # =========================================================

    def _create_image_clip(
        self,
        image_path: str,
        duration: float,
        zoom: float = 1.0,
        horizontal_focus: float = 0.5,
        vertical_focus: float = 0.5
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

            # Add controlled cinematic crop.
            scale *= zoom

            clip = clip.resized(
                scale
            )

            # Clamp crop position.
            horizontal_focus = max(
                0.0,
                min(
                    1.0,
                    horizontal_focus
                )
            )

            vertical_focus = max(
                0.0,
                min(
                    1.0,
                    vertical_focus
                )
            )

            x_center = (
                clip.w *
                horizontal_focus
            )

            y_center = (
                clip.h *
                vertical_focus
            )

            # Keep crop center inside image bounds.
            x_center = max(
                self.width / 2,
                min(
                    clip.w - self.width / 2,
                    x_center
                )
            )

            y_center = max(
                self.height / 2,
                min(
                    clip.h - self.height / 2,
                    y_center
                )
            )

            clip = clip.cropped(
                x_center=x_center,
                y_center=y_center,
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
    # CINEMATIC MICRO-SHOTS
    # =========================================================

    def _create_scene_shots(
        self,
        image_path: str,
        scene: Dict[str, Any],
        scene_duration: float,
        scene_index: int
    ) -> List[Any]:

        shots = []

        # -----------------------------------------------------
        # Four visual changes from ONE Sofia image.
        #
        # This is much faster than generating four AI images.
        # -----------------------------------------------------

        base = scene_duration

        durations = [
            base * 0.24,
            base * 0.25,
            base * 0.25,
            base * 0.26,
        ]

        shot_profiles = [
            {
                "zoom": 1.00,
                "x": 0.50,
                "y": 0.50,
            },
            {
                "zoom": 1.08,
                "x": 0.46,
                "y": 0.48,
            },
            {
                "zoom": 1.16,
                "x": 0.54,
                "y": 0.46,
            },
            {
                "zoom": 1.10,
                "x": 0.50,
                "y": 0.53,
            },
        ]

        for shot_index in range(
            self.SHOTS_PER_SCENE
        ):

            duration = max(
                2.2,
                durations[shot_index]
            )

            profile = shot_profiles[
                shot_index
            ]

            clip = (
                self._create_image_clip(
                    image_path=image_path,
                    duration=duration,
                    zoom=profile["zoom"],
                    horizontal_focus=profile["x"],
                    vertical_focus=profile["y"],
                )
            )

            if clip is None:
                continue

            # -------------------------------------------------
            # Very short fade on the first shot only.
            #
            # We intentionally avoid long fades because long
            # fades make a video feel slower.
            # -------------------------------------------------

            try:

                if shot_index == 0:

                    clip = clip.with_effects([
                        FadeIn(0.25)
                    ])

            except Exception:
                pass

            shots.append(
                clip
            )

        return shots

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

            text = str(
                text
            ).strip()

            if not text:
                return None

            # Keep subtitles short enough to read.
            if len(text) > 140:

                text = (
                    text[:137]
                    + "..."
                )

            subtitle = TextClip(
                text=text,
                font_size=30,
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
            "SOFIA LUXURY FAST CINEMATIC MOVIE"
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
                f"{len(story_scenes)} major scenes."
            )

            # -------------------------------------------------
            # CREATE ONE SOFIA IMAGE PER SCENE
            # -------------------------------------------------

            previous_sofia_image = ""

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
                    f"🎬 MAJOR SCENE "
                    f"{index + 1}/"
                    f"{len(story_scenes)}"
                )

                logger.info(
                    f"Location: "
                    f"{scene.get('location', '')}"
                )

                logger.info(
                    f"Action: "
                    f"{scene.get('action', '')[:140]}"
                )

                logger.info(
                    f"Duration: "
                    f"{duration:.1f}s"
                )

                # -------------------------------------------------
                # SOFIA IMAGE
                # -------------------------------------------------

                image_path = (
                    self._get_scene_visual(
                        scene,
                        index,
                        previous_sofia_image
                    )
                )

                if image_path:

                    # Once we have a successful Sofia image,
                    # retain it as the emergency continuity image.
                    previous_sofia_image = image_path

                # -------------------------------------------------
                # VISUAL FALLBACK
                # -------------------------------------------------

                if not image_path:

                    logger.warning(
                        "No visual available. "
                        "Using cinematic fallback."
                    )

                    fallback = ColorClip(
                        size=self.resolution,
                        color=(
                            12,
                            12,
                            18
                        ),
                        duration=duration
                    )

                    video_clips.append(
                        fallback
                    )

                    continue

                # -------------------------------------------------
                # MICRO-SHOT SEQUENCE
                # -------------------------------------------------

                shots = (
                    self._create_scene_shots(
                        image_path=image_path,
                        scene=scene,
                        scene_duration=duration,
                        scene_index=index
                    )
                )

                if not shots:

                    fallback = ColorClip(
                        size=self.resolution,
                        color=(
                            12,
                            12,
                            18
                        ),
                        duration=duration
                    )

                    video_clips.append(
                        fallback
                    )

                    continue

                # -------------------------------------------------
                # SUBTITLE
                #
                # Attach it to the first shot of the scene.
                # This keeps the screen clean while the image
                # changes underneath the narration.
                # -------------------------------------------------

                subtitle_text = (
                    scene.get("dialogue")
                    or scene.get("narration")
                    or ""
                )

                if subtitle_text:

                    subtitle = (
                        self._make_subtitle(
                            subtitle_text,
                            shots[0].duration
                        )
                    )

                    if subtitle:

                        shots[0] = (
                            CompositeVideoClip(
                                [
                                    shots[0],
                                    subtitle
                                ],
                                size=self.resolution
                            )
                        )

                video_clips.extend(
                    shots
                )

                logger.info(
                    f"SCENE {index + 1} READY "
                    f"with {len(shots)} visual shots."
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
                "Combining cinematic shots..."
            )

            final_video = (
                concatenate_videoclips(
                    video_clips,
                    method="compose"
                )
            )

            # -------------------------------------------------
            # EXACT VOICE DURATION
            # -------------------------------------------------

            if final_video.duration > total_duration:

                final_video = (
                    final_video.subclipped(
                        0,
                        total_duration
                    )
                )

            elif final_video.duration < total_duration:

                missing = (
                    total_duration -
                    final_video.duration
                )

                if video_clips:

                    last_clip = (
                        video_clips[-1]
                    )

                    extension = (
                        last_clip
                        .subclipped(
                            0,
                            min(
                                missing,
                                last_clip.duration
                            )
                        )
                    )

                    final_video = (
                        concatenate_videoclips(
                            [
                                final_video,
                                extension
                            ],
                            method="compose"
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

                        music = AudioFileClip(
                            music_path
                        )

                        if (
                            music.duration
                            <
                            total_duration
                        ):

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
                "🎥 RENDERING FINAL SOFIA MOVIE"
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


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    print("=" * 60)
    print(
        "SOFIA LUXURY FAST CINEMATIC MOVIE CREATOR"
    )
    print("=" * 60)

    creator = ProfessionalVideoCreator()

    print(
        f"Resolution: "
        f"{creator.width}x{creator.height}"
    )

    print(
        f"FPS: "
        f"{creator.fps}"
    )

    print(
        f"Major scenes: "
        f"{creator.MIN_SCENES}"
    )

    print(
        f"Shots per scene: "
        f"{creator.SHOTS_PER_SCENE}"
    )

    print(
        "Sofia visible in every scene: YES"
    )

    print(
        "Ready."
    )
