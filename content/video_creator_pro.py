"""
SOFIA LUXURY STORY
MEDIA-DRIVEN CINEMATIC VERTICAL MOVIE CREATOR

No AI image generation.

Visual priority is handled by AIImageGenerator/media resolver:

1. User library assets
2. Sofia reference when Sofia is required
3. Pexels videos
4. Pexels photos

The video creator turns those real media assets into a
cinematic vertical movie with:

- 8 connected story scenes
- cinematic image/video movement
- voice-over
- subtitles
- background music
- 9:16 output
- YouTube-ready MP4
"""

import os
import re

from pathlib import Path
from typing import Optional, List, Dict, Any

from loguru import logger
from dotenv import load_dotenv

from moviepy import (
    AudioFileClip,
    ImageClip,
    VideoFileClip,
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

    DEFAULT_RESOLUTION = (720, 1280)
    DEFAULT_FPS = 24

    MIN_SCENES = 8
    MAX_SCENES = 8

    SHOTS_PER_SCENE = 4

    MIN_SCENE_DURATION = 8.0
    MIN_SHOT_DURATION = 2.0

    SUBTITLE_FONT_SIZE = 30
    SUBTITLE_BOTTOM_OFFSET = 220

    MUSIC_VOLUME = 0.045

    VIDEO_BITRATE = "3000k"
    VIDEO_PRESET = "ultrafast"
    VIDEO_THREADS = 2

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

        # -------------------------------------------------
        # NEW MEDIA RESOLVER
        # -------------------------------------------------

        self.media_resolver = AIImageGenerator()

        self.sofia_reference = (
            Path("assets/sofia/sofia_reference.jpg")
        )

        self.library_dir = Path("library")

        logger.info(
            "================================================"
        )
        logger.info(
            "SOFIA LUXURY STORY MEDIA VIDEO CREATOR"
        )
        logger.info(
            f"Resolution: {self.width}x{self.height}"
        )
        logger.info(
            f"FPS: {self.fps}"
        )
        logger.info(
            "AI image generation: DISABLED"
        )
        logger.info(
            "User library: ENABLED"
        )
        logger.info(
            "Sofia reference: ENABLED"
        )
        logger.info(
            "Pexels support: ENABLED"
        )
        logger.info(
            "================================================"
        )

    # =====================================================
    # BACKGROUND MUSIC
    # =====================================================

    def _get_bg_music(self, mood="luxury") -> str:

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
    # STORY PREPARATION
    # =====================================================

    def _prepare_story_scenes(
        self,
        script_text: str,
        scenes: Optional[List[Dict[str, Any]]],
        total_duration: float,
        topic: str,
    ) -> List[Dict[str, Any]]:

        prepared = []

        # -------------------------------------------------
        # Use generated scenes
        # -------------------------------------------------

        if scenes:

            for scene in scenes:

                if not isinstance(scene, dict):
                    continue

                narration = str(
                    scene.get("narration", "")
                ).strip()

                dialogue = str(
                    scene.get("dialogue", "")
                ).strip()

                location = str(
                    scene.get(
                        "location",
                        "luxury location"
                    )
                ).strip()

                action = str(
                    scene.get("action", "")
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

                # -------------------------------------------------
                # Sofia visibility.
                #
                # If explicitly supplied, respect it.
                # Otherwise Sofia remains central.
                # -------------------------------------------------

                sofia_value = scene.get(
                    "sofia_visible",
                    True
                )

                if isinstance(
                    sofia_value,
                    str
                ):
                    sofia_visible = (
                        sofia_value.lower()
                        not in {
                            "false",
                            "no",
                            "0",
                            "none"
                        }
                    )
                else:
                    sofia_visible = bool(
                        sofia_value
                    )

                if not (
                    narration
                    or dialogue
                    or action
                    or visual_prompt
                ):
                    continue

                prepared.append({
                    "scene_number":
                        len(prepared) + 1,

                    "location": location,

                    "time": scene_time,

                    "action": action,

                    "emotion": emotion,

                    "visual_prompt":
                        visual_prompt,

                    "narration": narration,

                    "dialogue": dialogue,

                    "shot_type": shot_type,

                    "sofia_appearance":
                        appearance,

                    "luxury_detail":
                        luxury_detail,

                    "continuity":
                        continuity,

                    "sofia_visible":
                        sofia_visible,
                })

                if len(prepared) >= self.MAX_SCENES:
                    break

        # =================================================
        # SCRIPT FALLBACK
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
                        f"Sofia enters a luxurious "
                        f"world connected to {topic}."
                    )
                ]

            scene_count = self.MIN_SCENES

            total_sentences = len(sentences)

            for index in range(scene_count):

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

                group = sentences[start:end]

                if not group:
                    group = [
                        sentences[
                            min(
                                index,
                                total_sentences - 1
                            )
                        ]
                    ]

                text = " ".join(group)

                prepared.append({
                    "scene_number":
                        index + 1,

                    "location":
                        "luxury cinematic location",

                    "time":
                        "premium cinematic lighting",

                    "action":
                        text,

                    "emotion":
                        "determined",

                    "visual_prompt":
                        text,

                    "narration":
                        text,

                    "dialogue":
                        "",

                    "shot_type":
                        "cinematic medium shot",

                    "sofia_appearance":
                        "",

                    "luxury_detail":
                        "",

                    "continuity":
                        "",

                    "sofia_visible":
                        True,
                })

        # =================================================
        # FINAL SAFETY FALLBACK
        # =================================================

        if not prepared:

            prepared = [{
                "scene_number": 1,
                "location": "luxury penthouse",
                "time": "cinematic lighting",
                "action": "Sofia begins her journey.",
                "emotion": "determined",
                "visual_prompt":
                    "Sofia inside a magnificent "
                    "luxury penthouse.",
                "narration":
                    "Sofia begins her journey.",
                "dialogue": "",
                "shot_type":
                    "cinematic portrait",
                "sofia_appearance": "",
                "luxury_detail":
                    "marble, glass and premium "
                    "interior design",
                "continuity": "",
                "sofia_visible": True,
            }]

        prepared = prepared[:self.MAX_SCENES]

        # =================================================
        # DURATIONS
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

            word_counts.append(
                max(
                    1,
                    len(spoken.split())
                )
            )

        total_words = max(
            1,
            sum(word_counts)
        )

        minimum_total = (
            self.MIN_SCENE_DURATION
            * len(prepared)
        )

        target_duration = max(
            float(total_duration),
            float(minimum_total)
        )

        extra_duration = (
            target_duration
            - minimum_total
        )

        for index, scene in enumerate(
            prepared
        ):

            share = (
                word_counts[index]
                / total_words
            )

            duration = (
                self.MIN_SCENE_DURATION
                + extra_duration * share
            )

            scene["duration"] = max(
                self.MIN_SCENE_DURATION,
                float(duration)
            )

        calculated_total = sum(
            float(scene["duration"])
            for scene in prepared
        )

        difference = (
            target_duration
            - calculated_total
        )

        prepared[-1]["duration"] += difference

        for index, scene in enumerate(
            prepared
        ):

            scene["scene_number"] = index + 1
            scene["_all_scenes"] = prepared

        logger.info(
            f"Prepared {len(prepared)} story scenes."
        )

        logger.info(
            f"Target duration: {target_duration:.1f}s"
        )

        return prepared

    # =====================================================
    # BUILD MEDIA PROMPT
    # =====================================================

    def _build_media_prompt(
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

        emotion = str(
            scene.get("emotion", "")
        )

        luxury = str(
            scene.get("luxury_detail", "")
        )

        continuity = str(
            scene.get("continuity", "")
        )

        shot = str(
            scene.get("shot_type", "")
        )

        sofia_visible = scene.get(
            "sofia_visible",
            True
        )

        subject = (
            "Sofia is the central subject. "
            if sofia_visible
            else
            "Use supporting cinematic visuals; "
            "Sofia does not need to be visible."
        )

        return f"""
SOFIA LUXURY STORY

{subject}

LOCATION:
{location}

ACTION:
{action}

VISUAL:
{visual}

EMOTION:
{emotion}

SHOT:
{shot}

LUXURY DETAIL:
{luxury}

CONTINUITY:
{continuity}

Create/select a suitable real visual asset
for this movie scene.

Prefer an existing user library asset when it
matches the scene.

If Sofia is required, use the supplied Sofia
reference image.

Otherwise use a suitable real Pexels visual.

Do NOT generate a new AI image.

No text graphics.
No motivational quotes.
No fake social-media overlays.
No watermark.
Premium cinematic luxury style.
Vertical 9:16 composition.
"""

    # =====================================================
    # RESOLVE MEDIA
    # =====================================================

    def _resolve_scene_media(
        self,
        scene: Dict[str, Any],
        index: int
    ) -> str:

        """
        Ask the new media resolver for the actual asset.

        The resolver is responsible for:

        1. library
        2. Sofia reference
        3. Pexels video
        4. Pexels photo
        """

        prompt = self._build_media_prompt(scene)

        filename = (
            f"scene_media_{index + 1:03d}.jpg"
        )

        try:

            result = (
                self.media_resolver.generate_image(
                    prompt=prompt,
                    style="cinematic",
                    width=self.width,
                    height=self.height,
                    filename=filename,
                    use_reference=bool(
                        scene.get(
                            "sofia_visible",
                            True
                        )
                    ),
                    scene_number=index + 1,
                )
            )

            if result:

                result_path = Path(result)

                if result_path.exists():

                    logger.info(
                        f"MEDIA SELECTED: {result_path}"
                    )

                    return str(result_path)

        except TypeError:

            # Compatibility with an older resolver.
            try:

                result = (
                    self.media_resolver.generate_image(
                        prompt=prompt,
                        style="cinematic",
                        width=self.width,
                        height=self.height,
                        filename=filename,
                        use_reference=bool(
                            scene.get(
                                "sofia_visible",
                                True
                            )
                        ),
                    )
                )

                if result and Path(result).exists():

                    logger.info(
                        f"MEDIA SELECTED: {result}"
                    )

                    return str(result)

            except Exception as e:

                logger.warning(
                    f"Media resolver fallback failed: {e}"
                )

        except Exception as e:

            logger.warning(
                f"Media resolver failed: {e}"
            )

        return ""

    # =====================================================
    # LOCAL LIBRARY FALLBACK
    # =====================================================

    def _get_library_fallback(
        self,
        index: int
    ) -> str:

        if not self.library_dir.exists():
            return ""

        allowed = {
            ".jpg",
            ".jpeg",
            ".png",
            ".webp",
            ".mp4",
            ".mov",
            ".webm",
        }

        files = sorted(
            [
                p
                for p in self.library_dir.rglob("*")
                if p.is_file()
                and p.suffix.lower() in allowed
            ]
        )

        if not files:
            return ""

        selected = files[
            index % len(files)
        ]

        logger.info(
            f"Library fallback selected: {selected}"
        )

        return str(selected)

    # =====================================================
    # SOFIA FALLBACK
    # =====================================================

    def _get_sofia_fallback(self) -> str:

        if self.sofia_reference.exists():

            logger.info(
                "Using Sofia reference fallback."
            )

            return str(
                self.sofia_reference
            )

        return ""

    # =====================================================
    # FINAL MEDIA SELECTION
    # =====================================================

    def _get_scene_media(
        self,
        scene: Dict[str, Any],
        index: int
    ) -> str:

        # -------------------------------------------------
        # First: new resolver.
        # -------------------------------------------------

        media = self._resolve_scene_media(
            scene,
            index
        )

        if media:
            return media

        # -------------------------------------------------
        # Second: user's library.
        # -------------------------------------------------

        library_media = (
            self._get_library_fallback(
                index
            )
        )

        if library_media:
            return library_media

        # -------------------------------------------------
        # Third: Sofia reference.
        # -------------------------------------------------

        if scene.get(
            "sofia_visible",
            True
        ):

            sofia = self._get_sofia_fallback()

            if sofia:
                return sofia

        return ""

    # =====================================================
    # CREATE IMAGE CLIP
    # =====================================================

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

            scale *= zoom

            clip = clip.resized(scale)

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
                clip.w
                * horizontal_focus
            )

            y_center = (
                clip.h
                * vertical_focus
            )

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

    # =====================================================
    # CREATE VIDEO CLIP
    # =====================================================

    def _create_video_clip(
        self,
        video_path: str,
        duration: float,
        zoom: float = 1.0,
        horizontal_focus: float = 0.5,
        vertical_focus: float = 0.5
    ):

        try:

            clip = VideoFileClip(
                video_path,
                audio=False
            )

            if clip.duration <= 0:
                clip.close()
                return None

            # -------------------------------------------------
            # Loop/trim to requested scene duration.
            # -------------------------------------------------

            if clip.duration < duration:

                pieces = []

                remaining = duration

                while remaining > 0:

                    piece_duration = min(
                        remaining,
                        clip.duration
                    )

                    pieces.append(
                        clip.subclipped(
                            0,
                            piece_duration
                        )
                    )

                    remaining -= piece_duration

                clip = concatenate_videoclips(
                    pieces,
                    method="compose"
                )

            else:

                clip = clip.subclipped(
                    0,
                    duration
                )

            scale = max(
                self.width / clip.w,
                self.height / clip.h
            )

            scale *= zoom

            clip = clip.resized(scale)

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
                clip.w
                * horizontal_focus
            )

            y_center = (
                clip.h
                * vertical_focus
            )

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
                f"Video clip failed: {e}"
            )

            return None

    # =====================================================
    # MEDIA TYPE
    # =====================================================

    def _create_media_clip(
        self,
        media_path: str,
        duration: float,
        zoom: float = 1.0,
        x: float = 0.5,
        y: float = 0.5
    ):

        suffix = (
            Path(media_path)
            .suffix
            .lower()
        )

        video_extensions = {
            ".mp4",
            ".mov",
            ".webm",
            ".m4v",
            ".avi",
        }

        if suffix in video_extensions:

            return self._create_video_clip(
                media_path,
                duration,
                zoom,
                x,
                y
            )

        return self._create_image_clip(
            media_path,
            duration,
            zoom,
            x,
            y
        )

    # =====================================================
    # CINEMATIC SHOTS
    # =====================================================

    def _create_scene_shots(
        self,
        media_path: str,
        scene: Dict[str, Any],
        scene_duration: float,
        scene_index: int
    ) -> List[Any]:

        shots = []

        durations = [
            scene_duration * 0.28,
            scene_duration * 0.22,
            scene_duration * 0.22,
            scene_duration * 0.28,
        ]

        profiles = [
            {
                "zoom": 1.00,
                "x": 0.50,
                "y": 0.50,
            },
            {
                "zoom": 1.06,
                "x": 0.50,
                "y": 0.45,
            },
            {
                "zoom": 1.12,
                "x": 0.50,
                "y": 0.40,
            },
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
                durations[shot_index]
            )

            profile = profiles[
                shot_index
            ]

            clip = self._create_media_clip(
                media_path=media_path,
                duration=duration,
                zoom=profile["zoom"],
                x=profile["x"],
                y=profile["y"],
            )

            if clip is None:
                continue

            try:

                if shot_index == 0:

                    clip = clip.with_effects([
                        FadeIn(0.20)
                    ])

            except Exception:
                pass

            shots.append(clip)

        return shots

    # =====================================================
    # SUBTITLE
    # =====================================================

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

            if len(text) > 140:

                text = (
                    text[:137]
                    + "..."
                )

            subtitle = TextClip(
                text=text,
                font_size=self.SUBTITLE_FONT_SIZE,
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
                        - self.SUBTITLE_BOTTOM_OFFSET
                    )
                )
                .with_duration(duration)
            )

        except Exception as e:

            logger.warning(
                f"Subtitle skipped: {e}"
            )

            return None

    # =====================================================
    # CREATE FINAL VIDEO
    # =====================================================

    def create_professional_video(
        self,
        voiceover_path: str,
        topic: str,
        script_text: str = "",
        niche: str = "luxury",
        style: str = "cinematic",
        add_music: bool = True,
        output_path: str =
            "output/sofia_luxury_story.mp4",
        scenes: Optional[
            List[Dict[str, Any]]
        ] = None,
    ) -> str:

        logger.info(
            "================================================"
        )

        logger.info(
            "SOFIA LUXURY STORY VIDEO CREATION"
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

            # =================================================
            # VOICE
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
            # STORY
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

            # =================================================
            # VISUALS
            # =================================================

            for index, scene in enumerate(
                story_scenes
            ):

                duration = float(
                    scene.get(
                        "duration",
                        total_duration
                        / len(story_scenes)
                    )
                )

                logger.info(
                    "----------------------------------------"
                )

                logger.info(
                    f"🎬 SCENE "
                    f"{index + 1}/"
                    f"{len(story_scenes)}"
                )

                logger.info(
                    f"Location: "
                    f"{scene.get('location', '')}"
                )

                logger.info(
                    f"Duration: "
                    f"{duration:.1f}s"
                )

                logger.info(
                    f"Sofia required: "
                    f"{scene.get('sofia_visible', True)}"
                )

                # -------------------------------------------------
                # Resolve real media.
                # -------------------------------------------------

                media_path = (
                    self._get_scene_media(
                        scene,
                        index
                    )
                )

                if not media_path:

                    logger.warning(
                        "No media available."
                    )

                    fallback = ColorClip(
                        size=self.resolution,
                        color=(12, 12, 18),
                        duration=duration
                    )

                    video_clips.append(
                        fallback
                    )

                    continue

                logger.info(
                    f"Using media: {media_path}"
                )

                # -------------------------------------------------
                # Create cinematic shots.
                # -------------------------------------------------

                shots = (
                    self._create_scene_shots(
                        media_path=media_path,
                        scene=scene,
                        scene_duration=duration,
                        scene_index=index
                    )
                )

                if not shots:

                    logger.warning(
                        "Could not create shots."
                    )

                    fallback = ColorClip(
                        size=self.resolution,
                        color=(12, 12, 18),
                        duration=duration
                    )

                    video_clips.append(
                        fallback
                    )

                    continue

                # -------------------------------------------------
                # Subtitle.
                # -------------------------------------------------

                subtitle_text = (
                    scene.get("dialogue")
                    or
                    scene.get("narration")
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

                video_clips.extend(
                    shots
                )

                logger.info(
                    f"SCENE {index + 1} READY "
                    f"with {len(shots)} shots."
                )

            # =================================================
            # CHECK
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
                "Combining cinematic scenes..."
            )

            final_video = (
                concatenate_videoclips(
                    video_clips,
                    method="compose"
                )
            )

            # =================================================
            # MATCH VOICE LENGTH
            # =================================================

            if final_video.duration > total_duration:

                final_video = (
                    final_video.subclipped(
                        0,
                        total_duration
                    )
                )

            elif final_video.duration < total_duration:

                missing = (
                    total_duration
                    - final_video.duration
                )

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
            # VOICE
            # =================================================

            final_video = (
                final_video.with_audio(
                    audio
                )
            )

            # =================================================
            # MUSIC
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

                        if music.duration < total_duration:

                            repeat_count = (
                                int(
                                    total_duration
                                    / music.duration
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
                f"{self.fps} FPS"
            )

            logger.info(
                f"Duration: {total_duration:.1f}s"
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
            # VERIFY
            # =================================================

            if output.exists():

                size_mb = (
                    output.stat().st_size
                    / (1024 * 1024)
                )

                logger.info(
                    "================================================"
                )

                logger.info(
                    "🎬 SOFIA LUXURY STORY COMPLETE"
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
                f"Video creation failed: {e}"
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
        "SOFIA LUXURY STORY VIDEO CREATOR"
    )

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
        f"Major scenes: "
        f"{creator.MAX_SCENES}"
    )

    print(
        f"Shots per scene: "
        f"{creator.SHOTS_PER_SCENE}"
    )

    print(
        "AI image generation: NO"
    )

    print(
        "User library: YES"
    )

    print(
        "Sofia reference: YES"
    )

    print(
        "Pexels: YES"
    )

    print(
        "Vertical cinematic format: YES"
    )

    print(
        "Ready."
    )
