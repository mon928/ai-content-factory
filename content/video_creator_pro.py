"""
SOFIA LUXURY STORY
FAST CINEMATIC VERTICAL MOVIE CREATOR

Purpose
-------
Creates a fast, cinematic vertical Sofia movie from:

    - Sofia AI/reference images
    - 8 connected story scenes
    - voice-over narration
    - dialogue
    - subtitles
    - luxury background music
    - cinematic micro-shots
    - controlled zoom/framing
    - lightweight FFmpeg rendering

Important
---------
Sofia should remain the central visual character.

The image generator is responsible for using:

    assets/sofia/sofia_reference.jpg

when AI image generation is unavailable.

This file therefore does NOT depend on Pollinations being
available for the video pipeline to continue.
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


# =========================================================
# PROFESSIONAL VIDEO CREATOR
# =========================================================

class ProfessionalVideoCreator:
    """
    Fast cinematic Sofia luxury movie creator.

    Design goals:

        1. Sofia remains central.
        2. Eight connected story scenes.
        3. Four visual shots per scene.
        4. Fast visual pacing.
        5. No unnecessarily expensive AI generation.
        6. Vertical 9:16 output.
        7. Voice-over determines total movie duration.
        8. Emergency fallback always keeps the movie moving.
    """

    # -----------------------------------------------------
    # VIDEO SETTINGS
    # -----------------------------------------------------

    DEFAULT_RESOLUTION = (720, 1280)
    DEFAULT_FPS = 24

    MIN_SCENES = 8
    MAX_SCENES = 8

    SHOTS_PER_SCENE = 4

    # -----------------------------------------------------
    # CINEMATIC SETTINGS
    # -----------------------------------------------------

    MIN_SCENE_DURATION = 8.0

    MIN_SHOT_DURATION = 2.0

    SUBTITLE_FONT_SIZE = 30

    SUBTITLE_BOTTOM_OFFSET = 220

    MUSIC_VOLUME = 0.045

    # -----------------------------------------------------
    # OUTPUT SETTINGS
    # -----------------------------------------------------

    VIDEO_BITRATE = "3000k"

    VIDEO_PRESET = "ultrafast"

    VIDEO_THREADS = 2

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(
        self,
        resolution=(720, 1280),
        fps=24
    ):

        self.resolution = resolution

        self.fps = fps

        self.width, self.height = resolution

        # -------------------------------------------------
        # Always force vertical video.
        # -------------------------------------------------

        if self.width >= self.height:

            self.resolution = (
                self.DEFAULT_RESOLUTION
            )

            self.width, self.height = (
                self.resolution
            )

        # -------------------------------------------------
        # Sofia image generator.
        # -------------------------------------------------

        self.ai_image_gen = (
            AIImageGenerator()
        )

        # -------------------------------------------------
        # Pexels is only emergency support.
        # -------------------------------------------------

        self.pexels_key = os.getenv(
            "PEXELS_API_KEY",
            ""
        )

        # -------------------------------------------------
        # Sofia identity description.
        # -------------------------------------------------

        self.sofia_identity = (
            "Sofia is the central female protagonist "
            "of a premium cinematic luxury movie. "
            "She is elegant, intelligent, modern and "
            "confident. Keep her recognizable facial "
            "identity consistent throughout the story. "
            "Use natural realistic skin, expressive eyes, "
            "realistic anatomy, sophisticated fashion, "
            "photorealistic detail and cinematic lighting."
        )

        logger.info(
            "================================================"
        )

        logger.info(
            "SOFIA FAST CINEMATIC MOVIE CREATOR READY"
        )

        logger.info(
            f"Resolution: "
            f"{self.width}x{self.height}"
        )

        logger.info(
            f"FPS: {self.fps}"
        )

        logger.info(
            "Sofia visible throughout: YES"
        )

        logger.info(
            "================================================"
        )

    # =====================================================
    # BACKGROUND MUSIC
    # =====================================================

    def _get_bg_music(
        self,
        mood="luxury"
    ) -> str:

        """
        Find available background music.

        Luxury is preferred, but other existing tracks
        can be used as a fallback.
        """

        moods = [
            mood,
            "luxury",
            "tech",
            "action",
            "drama",
        ]

        checked = set()

        for selected in moods:

            if selected in checked:
                continue

            checked.add(selected)

            path = Path(
                f"data/assets/bg_music_{selected}.mp3"
            )

            if path.exists():

                logger.info(
                    f"Background music found: {path}"
                )

                return str(path)

        logger.info(
            "No background music file found."
        )

        return ""

    # =====================================================
    # STORY SCENES
    # =====================================================

    def _prepare_story_scenes(
        self,
        script_text: str,
        scenes: Optional[List[Dict[str, Any]]],
        total_duration: float,
        topic: str,
    ) -> List[Dict[str, Any]]:

        """
        Prepare the story scenes.

        The script generator should normally provide
        eight scenes.

        If it doesn't, this method safely constructs
        scenes from the available script.
        """

        prepared = []

        # -------------------------------------------------
        # USE GENERATED SCENES
        # -------------------------------------------------

        if scenes:

            for index, scene in enumerate(
                scenes
            ):

                if not isinstance(
                    scene,
                    dict
                ):
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

                scene_time = str(
                    scene.get(
                        "time",
                        "cinematic lighting"
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
                    "scene_number": (
                        len(prepared) + 1
                    ),

                    "location": location,

                    "time": scene_time,

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

                if len(prepared) >= (
                    self.MAX_SCENES
                ):
                    break

        # =================================================
        # FALLBACK FROM SCRIPT
        # =================================================

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
                if len(s.strip()) > 15
            ]

            if not sentences:

                sentences = [
                    (
                        f"Sofia enters a luxurious world "
                        f"connected to {topic}."
                    )
                ]

            # -------------------------------------------------
            # Divide the available script into eight sections.
            # -------------------------------------------------

            scene_count = self.MIN_SCENES

            total_sentences = len(
                sentences
            )

            for index in range(
                scene_count
            ):

                start = int(
                    index
                    * total_sentences
                    / scene_count
                )

                end = int(
                    (index + 1)
                    * total_sentences
                    / scene_count
                )

                group = sentences[
                    start:end
                ]

                if not group:

                    group = [
                        sentences[
                            min(
                                index,
                                total_sentences - 1
                            )
                        ]
                    ]

                text = " ".join(
                    group
                )

                prepared.append({
                    "scene_number": index + 1,

                    "location": (
                        "luxury cinematic location"
                    ),

                    "time": (
                        "premium cinematic lighting"
                    ),

                    "action": text,

                    "emotion": (
                        "determined"
                    ),

                    "visual_prompt": text,

                    "narration": text,

                    "dialogue": "",

                    "shot_type": (
                        "cinematic medium shot"
                    ),

                    "sofia_appearance": "",

                    "luxury_detail": "",

                    "continuity": "",

                    "sofia_visible": True,
                })

        # =================================================
        # SAFETY FALLBACK
        # =================================================

        if not prepared:

            prepared = [{
                "scene_number": 1,

                "location": (
                    "luxury penthouse"
                ),

                "time": (
                    "golden cinematic lighting"
                ),

                "action": (
                    "Sofia begins her journey."
                ),

                "emotion": (
                    "determined"
                ),

                "visual_prompt": (
                    "Sofia inside a magnificent "
                    "luxury penthouse."
                ),

                "narration": (
                    "Sofia begins her journey."
                ),

                "dialogue": "",

                "shot_type": (
                    "cinematic portrait"
                ),

                "sofia_appearance": "",

                "luxury_detail": (
                    "marble, glass and "
                    "premium interior design"
                ),

                "continuity": "",

                "sofia_visible": True,
            }]

        # -------------------------------------------------
        # Limit to eight.
        # -------------------------------------------------

        prepared = prepared[
            :self.MAX_SCENES
        ]

        # =================================================
        # SCENE DURATIONS
        # =================================================

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
                max(
                    1,
                    count
                )
            )

        total_words = max(
            1,
            sum(word_counts)
        )

        # -------------------------------------------------
        # Do not make scenes too short.
        # -------------------------------------------------

        minimum_scene_time = (
            self.MIN_SCENE_DURATION
        )

        minimum_total = (
            minimum_scene_time
            * len(prepared)
        )

        # -------------------------------------------------
        # Normally total_duration is the exact voice
        # duration.
        #
        # If the voice is unusually short, we still keep
        # enough time for all story scenes.
        # -------------------------------------------------

        target_duration = max(
            float(total_duration),
            float(minimum_total)
        )

        extra_duration = (
            target_duration
            -
            minimum_total
        )

        for index, scene in enumerate(
            prepared
        ):

            share = (
                word_counts[index]
                /
                total_words
            )

            duration = (
                minimum_scene_time
                +
                extra_duration
                * share
            )

            scene["duration"] = max(
                minimum_scene_time,
                float(duration)
            )

        # -------------------------------------------------
        # Correct tiny floating point differences.
        # -------------------------------------------------

        calculated_total = sum(
            float(
                scene["duration"]
            )
            for scene in prepared
        )

        difference = (
            target_duration
            -
            calculated_total
        )

        prepared[-1]["duration"] += (
            difference
        )

        prepared[-1]["duration"] = max(
            minimum_scene_time,
            prepared[-1]["duration"]
        )

        # -------------------------------------------------
        # Scene continuity information.
        # -------------------------------------------------

        for index, scene in enumerate(
            prepared
        ):

            scene["scene_number"] = (
                index + 1
            )

            scene["_all_scenes"] = (
                prepared
            )

        logger.info(
            f"Prepared {len(prepared)} "
            f"story scenes."
        )

        logger.info(
            f"Target visual duration: "
            f"{target_duration:.1f}s"
        )

        return prepared

    # =====================================================
    # VISUAL QUERY
    # =====================================================

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

    # =====================================================
    # PEXELS SUPPORT
    # =====================================================

    def _download_pexels_photo(
        self,
        scene: Dict[str, Any],
        index: int
    ) -> str:

        """
        Emergency supporting visual.

        Pexels is NOT preferred for Sofia scenes.
        """

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
                f"movie_support_"
                f"{index + 1:03d}.jpg"
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

    # =====================================================
    # SOFIA AI IMAGE
    # =====================================================

    def _generate_sofia_image(
        self,
        scene: Dict[str, Any],
        index: int
    ) -> str:

        """
        Generate one main Sofia visual for the scene.

        The actual reference handling is performed by
        AIImageGenerator.
        """

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

        scene_time = str(
            scene.get(
                "time",
                "cinematic lighting"
            )
        )

        # -------------------------------------------------
        # Strong Sofia prompt.
        # -------------------------------------------------

        prompt = f"""

{self.sofia_identity}

Sofia must be clearly visible.

Sofia is the main subject of this frame.

Never replace Sofia with another woman.

Preserve Sofia's recognizable face and identity
from the supplied reference image.

STORY LOCATION:
{location}

TIME / ATMOSPHERE:
{scene_time}

SOFIA'S ACTION:
{action}

SOFIA'S EMOTION:
{emotion}

SOFIA'S APPEARANCE:
{appearance}

PRIMARY SHOT:
{shot_type}

LUXURY DETAIL:
{luxury_detail}

STORY CONTINUITY:
{continuity}

VISUAL DIRECTION:
{visual}

Create a photorealistic frame from a premium
luxury movie.

Sofia should be clearly recognizable.

Natural facial proportions.

Natural hands.

Natural anatomy.

Natural posture.

Realistic environment.

Premium cinematic lighting.

Elegant luxury styling.

Strong movie composition.

Portrait 9:16.

No text.

No captions.

No watermark.
"""

        filename = (
            f"sofia_cinematic_"
            f"{index + 1:03d}.jpg"
        )

        try:

            total_scenes = (
                len(
                    scene.get(
                        "_all_scenes",
                        []
                    )
                )
                or self.MAX_SCENES
            )

            logger.info(
                f"Generating Sofia visual "
                f"{index + 1}/{total_scenes}"
            )

            result = (
                self.ai_image_gen.generate_image(
                    prompt=prompt,
                    style="cinematic",
                    width=self.width,
                    height=self.height,
                    filename=filename,
                    use_reference=True,
                    scene_number=index + 1,
                )
            )

            if result:

                return result

        except TypeError:

            # -------------------------------------------------
            # Compatibility with older AIImageGenerator
            # versions that don't accept scene_number.
            # -------------------------------------------------

            try:

                result = (
                    self.ai_image_gen.generate_image(
                        prompt=prompt,
                        style="cinematic",
                        width=self.width,
                        height=self.height,
                        filename=filename,
                        use_reference=True,
                    )
                )

                if result:

                    return result

            except Exception as e:

                logger.warning(
                    "Sofia image compatibility "
                    f"fallback failed: {e}"
                )

        except Exception as e:

            logger.warning(
                "Sofia image generation failed: "
                f"{e}"
            )

        return ""

    # =====================================================
    # CHOOSE SCENE VISUAL
    # =====================================================

    def _get_scene_visual(
        self,
        scene: Dict[str, Any],
        index: int,
        previous_sofia_image: str = ""
    ) -> str:

        """
        Sofia is always attempted first.

        Previous Sofia image is second.

        Pexels is last emergency support.
        """

        sofia = (
            self._generate_sofia_image(
                scene,
                index
            )
        )

        if sofia:

            return sofia

        # -------------------------------------------------
        # Keep Sofia visible if a new generation fails.
        # -------------------------------------------------

        if previous_sofia_image:

            logger.warning(
                "New Sofia image unavailable."
            )

            logger.warning(
                "Reusing previous Sofia image "
                "for visual continuity."
            )

            return previous_sofia_image

        # -------------------------------------------------
        # Emergency Pexels support.
        # -------------------------------------------------

        supporting = (
            self._download_pexels_photo(
                scene,
                index
            )
        )

        if supporting:

            return supporting

        return ""

    # =====================================================
    # IMAGE CLIP
    # =====================================================

    def _create_image_clip(
        self,
        image_path: str,
        duration: float,
        zoom: float = 1.0,
        horizontal_focus: float = 0.5,
        vertical_focus: float = 0.5
    ):

        """
        Convert a still image into a correctly framed
        vertical video clip.

        The crop is conservative because the new Sofia
        reference image is already vertical.
        """

        try:

            clip = ImageClip(
                image_path,
                duration=duration
            )

            # -------------------------------------------------
            # Scale image to completely cover the video.
            # -------------------------------------------------

            scale = max(
                self.width / clip.w,
                self.height / clip.h
            )

            scale *= zoom

            clip = clip.resized(
                scale
            )

            # -------------------------------------------------
            # Clamp focus values.
            # -------------------------------------------------

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

            # -------------------------------------------------
            # Calculate crop center.
            # -------------------------------------------------

            x_center = (
                clip.w
                *
                horizontal_focus
            )

            y_center = (
                clip.h
                *
                vertical_focus
            )

            # -------------------------------------------------
            # Never let crop go outside image.
            # -------------------------------------------------

            x_center = max(
                self.width / 2,
                min(
                    clip.w
                    -
                    self.width / 2,
                    x_center
                )
            )

            y_center = max(
                self.height / 2,
                min(
                    clip.h
                    -
                    self.height / 2,
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

    # =====================================================
    # CINEMATIC MICRO-SHOTS
    # =====================================================

    def _create_scene_shots(
        self,
        image_path: str,
        scene: Dict[str, Any],
        scene_duration: float,
        scene_index: int
    ) -> List[Any]:

        """
        Turn one Sofia image into four fast cinematic
        compositions.

        Sequence:

            1. Establishing/full Sofia
            2. Medium Sofia
            3. Emotional face/upper-body
            4. Return to wider Sofia

        This prevents the previous problem where the video
        repeatedly showed almost exactly the same crop.
        """

        shots = []

        # -------------------------------------------------
        # Shot timing.
        # -------------------------------------------------

        durations = [
            scene_duration * 0.28,
            scene_duration * 0.22,
            scene_duration * 0.22,
            scene_duration * 0.28,
        ]

        # -------------------------------------------------
        # Conservative framing.
        #
        # Sofia's face remains visible.
        # -------------------------------------------------

        shot_profiles = [

            # 1. Full cinematic composition
            {
                "zoom": 1.00,
                "x": 0.50,
                "y": 0.50,
            },

            # 2. Medium shot
            {
                "zoom": 1.06,
                "x": 0.50,
                "y": 0.43,
            },

            # 3. Emotional closer shot
            {
                "zoom": 1.13,
                "x": 0.50,
                "y": 0.34,
            },

            # 4. Return to wider composition
            {
                "zoom": 1.03,
                "x": 0.50,
                "y": 0.48,
            },
        ]

        for shot_index in range(
            self.SHOTS_PER_SCENE
        ):

            duration = max(
                self.MIN_SHOT_DURATION,
                durations[
                    shot_index
                ]
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
            # Very short first-shot fade.
            # -------------------------------------------------

            try:

                if shot_index == 0:

                    clip = clip.with_effects([
                        FadeIn(0.20)
                    ])

            except Exception:

                pass

            shots.append(
                clip
            )

        return shots

    # =====================================================
    # SUBTITLES
    # =====================================================

    def _make_subtitle(
        self,
        text: str,
        duration: float
    ):

        """
        Create a readable subtitle overlay.

        Subtitles are intentionally modest so they don't
        cover Sofia's face.
        """

        if not text:

            return None

        try:

            text = str(
                text
            ).strip()

            if not text:

                return None

            # -------------------------------------------------
            # Prevent enormous subtitle blocks.
            # -------------------------------------------------

            if len(text) > 140:

                text = (
                    text[:137]
                    + "..."
                )

            subtitle = TextClip(
                text=text,
                font_size=(
                    self.SUBTITLE_FONT_SIZE
                ),
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
                        self.height
                        -
                        self.SUBTITLE_BOTTOM_OFFSET
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

    # =====================================================
    # MAIN VIDEO CREATOR
    # =====================================================

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

        # -------------------------------------------------
        # Verify voice.
        # -------------------------------------------------

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

            # =================================================
            # LOAD VOICEOVER
            # =================================================

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

            # =================================================
            # PREPARE STORY
            # =================================================

            story_scenes = (
                self._prepare_story_scenes(
                    script_text=script_text,
                    scenes=scenes,
                    total_duration=total_duration,
                    topic=str(topic),
                )
            )

            if not story_scenes:

                logger.error(
                    "No story scenes available."
                )

                return ""

            logger.info(
                f"Story contains "
                f"{len(story_scenes)} "
                f"major scenes."
            )

            # =================================================
            # CREATE SCENE VISUALS
            # =================================================

            previous_sofia_image = ""

            for index, scene in enumerate(
                story_scenes
            ):

                duration = float(
                    scene.get(
                        "duration",
                        total_duration
                        /
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
                    f"{str(scene.get('action', ''))[:160]}"
                )

                logger.info(
                    f"Duration: "
                    f"{duration:.1f}s"
                )

                # -------------------------------------------------
                # Generate/find Sofia visual.
                # -------------------------------------------------

                image_path = (
                    self._get_scene_visual(
                        scene=scene,
                        index=index,
                        previous_sofia_image=(
                            previous_sofia_image
                        )
                    )
                )

                if image_path:

                    previous_sofia_image = (
                        image_path
                    )

                # =================================================
                # VISUAL FALLBACK
                # =================================================

                if not image_path:

                    logger.warning(
                        "No visual available."
                    )

                    logger.warning(
                        "Using cinematic dark fallback."
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

                # =================================================
                # MICRO SHOTS
                # =================================================

                shots = (
                    self._create_scene_shots(
                        image_path=image_path,
                        scene=scene,
                        scene_duration=duration,
                        scene_index=index
                    )
                )

                if not shots:

                    logger.warning(
                        "Could not create visual shots."
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

                # =================================================
                # SUBTITLE
                # =================================================

                subtitle_text = (
                    scene.get(
                        "dialogue"
                    )
                    or
                    scene.get(
                        "narration"
                    )
                    or
                    ""
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

                # -------------------------------------------------
                # Add all shots.
                # -------------------------------------------------

                video_clips.extend(
                    shots
                )

                logger.info(
                    f"SCENE {index + 1} READY "
                    f"with {len(shots)} "
                    f"visual shots."
                )

            # =================================================
            # CHECK VISUALS
            # =================================================

            if not video_clips:

                logger.error(
                    "No visual scenes were created."
                )

                return ""

            # =================================================
            # CONCATENATE
            # =================================================

            logger.info(
                "Combining cinematic shots..."
            )

            final_video = (
                concatenate_videoclips(
                    video_clips,
                    method="compose"
                )
            )

            # =================================================
            # MATCH VOICEOVER LENGTH
            # =================================================

            if (
                final_video.duration
                >
                total_duration
            ):

                logger.info(
                    "Trimming visual video to "
                    "voice-over duration."
                )

                final_video = (
                    final_video.subclipped(
                        0,
                        total_duration
                    )
                )

            elif (
                final_video.duration
                <
                total_duration
            ):

                missing = (
                    total_duration
                    -
                    final_video.duration
                )

                logger.info(
                    f"Visual video is "
                    f"{missing:.2f}s short."
                )

                # -------------------------------------------------
                # Extend the final visual instead of leaving
                # black frames.
                # -------------------------------------------------

                if video_clips:

                    last_clip = (
                        video_clips[-1]
                    )

                    extension_duration = min(
                        missing,
                        max(
                            0.5,
                            last_clip.duration
                        )
                    )

                    extension = (
                        last_clip.subclipped(
                            0,
                            extension_duration
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

            # =================================================
            # ATTACH VOICE
            # =================================================

            final_video = (
                final_video.with_audio(
                    audio
                )
            )

            # =================================================
            # BACKGROUND MUSIC
            # =================================================

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

                        # -------------------------------------------------
                        # Repeat music if necessary.
                        # -------------------------------------------------

                        if (
                            music.duration
                            <
                            total_duration
                        ):

                            repeat_count = (
                                int(
                                    total_duration
                                    /
                                    music.duration
                                )
                                + 1
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
                                self.MUSIC_VOLUME
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

            # =================================================
            # RENDER
            # =================================================

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
                f"{self.width}x{self.height} / "
                f"{self.fps} FPS / FAST MODE"
            )

            logger.info(
                f"Expected duration: "
                f"{total_duration:.1f}s"
            )

            logger.info(
                "================================================"
            )

            final_video.write_videofile(
                str(output),
                fps=self.fps,
                codec="libx264",
                audio_codec="aac",
                bitrate=self.VIDEO_BITRATE,
                preset=self.VIDEO_PRESET,
                threads=self.VIDEO_THREADS,
                logger=None,
            )

            # =================================================
            # VERIFY OUTPUT
            # =================================================

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
                    f"Duration target: "
                    f"{total_duration:.1f}s"
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

            # -------------------------------------------------
            # Close final video.
            # -------------------------------------------------

            try:

                if final_video:

                    final_video.close()

            except Exception:

                pass

            # -------------------------------------------------
            # Close music.
            # -------------------------------------------------

            try:

                if music:

                    music.close()

            except Exception:

                pass

            # -------------------------------------------------
            # Close voice.
            # -------------------------------------------------

            try:

                if audio:

                    audio.close()

            except Exception:

                pass

            # -------------------------------------------------
            # Close individual clips.
            # -------------------------------------------------

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
        "Sofia visible throughout: YES"
    )

    print(
        "Vertical cinematic format: YES"
    )

    print(
        "Fast rendering mode: YES"
    )

    print(
        "Ready."
    )
