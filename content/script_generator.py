"""
SOFIA LUXURY STORY
CINEMATIC 5-MINUTE STORY GENERATOR

Creates original Sofia-centered vertical mini-movies.

Designed for:
- Luxury drama
- Romance
- Mystery
- Action
- Adventure
- Billionaire stories
- Royal stories
- Fantasy
- Time travel
- Crime/thriller
- Supernatural stories

The generator creates:
- One connected story
- Approximately 820-900 spoken words
- Exactly 8 major story scenes
- Detailed visual direction
- Sofia visible in every scene
- Different shot types
- Luxury environments
- Emotional progression
- Mid-story twist
- Climax
- Resolution or cliffhanger

IMPORTANT:

The spoken story length is validated after generation.

If the first AI response is too short or structurally
incorrect, the generator asks the AI to repair the story
before sending it to the video creator.
"""

import os
import json
import re
from typing import Dict, List, Any, Optional

from loguru import logger

try:
    from groq import Groq
except ImportError:
    import groq
    Groq = groq.Groq

from dotenv import load_dotenv


load_dotenv()


class ScriptGenerator:

    # =====================================================
    # MODEL
    # =====================================================

    MODEL = "openai/gpt-oss-120b"

    # =====================================================
    # SPOKEN STORY LENGTH
    #
    # Around 850 words gives the voice generator enough
    # material for a much more reliable five-minute movie.
    # =====================================================

    TARGET_WORDS_MIN = 820
    TARGET_WORDS_MAX = 900
    TARGET_WORDS_IDEAL = 860

    # =====================================================
    # STORY STRUCTURE
    # =====================================================

    SCENE_COUNT = 8

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(
        self,
        language: str = "english",
        niche: str = "luxury_story"
    ):

        self.language = language
        self.niche = niche

        api_key = os.getenv(
            "GROQ_API_KEY"
        )

        if not api_key:

            raise RuntimeError(
                "GROQ_API_KEY is missing. "
                "Add it to your environment "
                "or GitHub Actions secrets."
            )

        self.client = Groq(
            api_key=api_key
        )

        logger.info(
            "================================================"
        )

        logger.info(
            "SOFIA CINEMATIC STORY GENERATOR INITIALIZED"
        )

        logger.info(
            f"Language: {self.language}"
        )

        logger.info(
            f"Niche: {self.niche}"
        )

        logger.info(
            f"Target spoken words: "
            f"{self.TARGET_WORDS_MIN}-"
            f"{self.TARGET_WORDS_MAX}"
        )

        logger.info(
            f"Target scenes: {self.SCENE_COUNT}"
        )

        logger.info(
            "================================================"
        )

    # =====================================================
    # MAIN GENERATOR
    # =====================================================

    def generate_script(
        self,
        topic: Any,
        duration_minutes: int = 5
    ) -> Dict[str, Any]:

        topic_text = self._normalize_topic(
            topic
        )

        logger.info(
            "🎬 Creating cinematic Sofia story..."
        )

        logger.info(
            f"Topic: {topic_text[:160]}"
        )

        prompt = self._build_story_prompt(
            topic_text,
            duration_minutes
        )

        try:

            response = (
                self.client.chat.completions.create(
                    model=self.MODEL,

                    messages=[
                        {
                            "role": "system",
                            "content": (
                                self._system_prompt()
                            )
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],

                    temperature=0.82,

                    max_tokens=6000
                )
            )

            raw = (
                response
                .choices[0]
                .message
                .content
                or ""
            )

            result = self._parse_response(
                raw,
                topic_text,
                duration_minutes
            )

            # =================================================
            # VALIDATE THE STORY
            # =================================================

            needs_repair = (
                self._story_needs_repair(
                    result
                )
            )

            if needs_repair:

                logger.warning(
                    "⚠️ First story did not meet "
                    "the cinematic requirements."
                )

                logger.warning(
                    f"Words: "
                    f"{result.get('word_count', 0)}"
                )

                logger.warning(
                    f"Scenes: "
                    f"{len(result.get('scenes', []))}"
                )

                logger.info(
                    "🔧 Asking Groq to repair "
                    "the story..."
                )

                repaired = (
                    self._repair_story(
                        result,
                        topic_text,
                        duration_minutes
                    )
                )

                if repaired:

                    result = repaired

            # =================================================
            # FINAL NORMALIZATION
            # =================================================

            result = (
                self._finalize_result(
                    result,
                    topic_text
                )
            )

            logger.info(
                "================================================"
            )

            logger.info(
                "✅ SOFIA STORY READY"
            )

            logger.info(
                f"Title: "
                f"{result.get('title', 'Untitled')}"
            )

            logger.info(
                f"Words: "
                f"{result.get('word_count', 0)}"
            )

            logger.info(
                f"Scenes: "
                f"{len(result.get('scenes', []))}"
            )

            logger.info(
                f"Estimated duration: "
                f"{result.get('estimated_duration_min', 0)} "
                f"minutes"
            )

            logger.info(
                "================================================"
            )

            return result

        except Exception as e:

            logger.exception(
                f"❌ Sofia story generation failed: {e}"
            )

            return {
                "topic": topic_text,
                "title": "Sofia Luxury Story",
                "genre": "Luxury Drama",
                "logline": "",
                "hook": "",
                "script": "",
                "scenes": [],
                "word_count": 0,
                "estimated_duration_min": 0,
                "language": self.language,
                "niche": self.niche,
                "error": str(e)
            }

    # =====================================================
    # SYSTEM PROMPT
    # =====================================================

    def _system_prompt(self) -> str:

        return """
You are the head writer and visual story director
for SOFIA LUXURY STORY.

You create ORIGINAL cinematic vertical mini-movies.

Sofia is ALWAYS the protagonist.

She is not a presenter.

She is not a narrator standing outside the story.

She is the person living through the story.

Every story must feel like a real short movie.

=========================================================
CORE STORY RULES
=========================================================

1. Sofia must be central in EVERY scene.

2. Sofia must perform meaningful actions.

3. Sofia must have a clear goal.

4. Sofia must have something important to lose.

5. Sofia must discover something important.

6. Sofia must make a difficult decision.

7. Sofia must drive the story forward.

8. Every scene must cause or lead naturally to the next.

9. Never create eight unrelated luxury pictures.

10. Never make the story feel like a lecture.

11. Never repeatedly show Sofia simply standing,
smiling, posing, or walking.

12. Sofia must interact with:
- people
- objects
- technology
- vehicles
- buildings
- environments
- important story clues

13. Sofia must remain recognizable as the same woman.

14. Her clothing can change only when the story
provides a believable reason.

15. Her facial identity must remain consistent.

16. Start with a strong hook.

17. Build escalating tension.

18. Include a meaningful mid-story twist.

19. Give Sofia a difficult decision.

20. Give Sofia a strong climax.

21. Finish with emotional payoff or a compelling
cliffhanger.

=========================================================
VISUAL STORY RULES
=========================================================

Every scene must have a strong visual idea.

Use varied compositions:

- wide establishing shot
- medium character shot
- close-up
- extreme close-up
- over-the-shoulder
- side profile
- low angle
- high angle
- point of view
- tracking-style composition
- environmental detail

Do not repeat the same visual idea eight times.

Sofia should be visible in most of every scene.

Luxury environments must feel believable.

Use:

- realistic architecture
- realistic lighting
- realistic clothing
- realistic objects
- natural expressions
- cinematic atmosphere
- rich textures

Avoid generic AI-looking descriptions.

=========================================================
VISUAL PROMPT REQUIREMENTS
=========================================================

Every visual_prompt MUST describe:

- Sofia
- Sofia's action
- Sofia's emotion
- location
- lighting
- camera framing
- important story objects
- atmosphere

The visual prompt must make Sofia the central
visible subject.

=========================================================
STORY CONTINUITY
=========================================================

If Sofia enters a hotel in scene 2,
scene 3 must logically continue from that hotel.

If Sofia discovers an object,
that object may return later.

If another character appears,
that character must have a consistent role.

If Sofia wears a particular outfit,
do not randomly change it without a story reason.

Every scene must connect to the previous scene.

=========================================================
DIALOGUE
=========================================================

Dialogue must be short and natural.

Avoid theatrical speeches.

Avoid long explanations.

Characters should speak like real people.

=========================================================
NARRATION
=========================================================

Narration must advance the story.

Do not simply describe what the audience can see.

Bad:

"Sofia is standing in a beautiful hotel."

Better:

"Sofia realized the message had been sent
from inside the hotel."

The audience must always have a reason to continue watching.

=========================================================
SPOKEN STORY LENGTH
=========================================================

The complete spoken story MUST contain approximately:

820-900 words.

Aim for approximately:

860 words.

Do NOT produce a 400-word story.

Do NOT produce a 500-word story.

Do NOT produce a 600-word story.

The story needs enough spoken material for a genuine
five-minute cinematic video.

=========================================================
SPOKEN TEXT
=========================================================

Do not include:

[pause]
[music]
[sound effect]
[camera]
[zoom]
[cut]
[scene]
[fade]
or other production instructions.

Do not include channel introductions.

Do not say:

"Welcome back to my channel."

The first sentence must create curiosity.

The story must be ORIGINAL.

Do not copy existing movies, books,
television shows or social-media stories.
"""

    # =====================================================
    # STORY PROMPT
    # =====================================================

    def _build_story_prompt(
        self,
        topic: str,
        duration: int
    ) -> str:

        return f"""
Create an ORIGINAL SOFIA LUXURY STORY based on:

{topic}

TARGET LENGTH:

Approximately {duration} minutes.

SPOKEN WORD TARGET:

820-900 words.

IDEAL:

Approximately 860 words.

NUMBER OF MAJOR SCENES:

Exactly 8.

The eight scenes MUST form one continuous movie.

Do not create eight disconnected scenes.

=========================================================
SCENE 1 — HOOK
=========================================================

Open immediately with something:

- mysterious
- dangerous
- surprising
- beautiful
- emotionally important

Sofia must be visible.

The audience should immediately wonder:

"What is happening?"

=========================================================
SCENE 2 — SETUP
=========================================================

Show Sofia's world.

Establish:

- who Sofia is
- what she wants
- what matters to her
- what she could lose

Make the audience care about the outcome.

=========================================================
SCENE 3 — PROBLEM
=========================================================

Something unexpected happens.

The problem must directly affect Sofia.

Sofia must react.

The problem must create a clear question.

=========================================================
SCENE 4 — ESCALATION
=========================================================

Sofia investigates, follows someone,
discovers something, escapes,
travels somewhere or takes action.

The situation becomes more dangerous
or emotionally important.

=========================================================
SCENE 5 — TWIST
=========================================================

Reveal something that changes the meaning
of earlier events.

The twist must connect to scenes 1-4.

Do not introduce a random unrelated twist.

=========================================================
SCENE 6 — DECISION
=========================================================

Sofia must make a difficult choice.

Sofia must drive the action.

Do not let another character solve the story for her.

Her choice must lead directly to the climax.

=========================================================
SCENE 7 — CLIMAX
=========================================================

Sofia confronts the central problem.

This must be the most intense or emotional scene.

Give Sofia a meaningful action.

=========================================================
SCENE 8 — ENDING
=========================================================

Give the audience one of:

- emotional payoff
- beautiful final moment
- powerful revelation
- satisfying resolution
- compelling cliffhanger

End with a memorable Sofia moment.

=========================================================
LUXURY WORLD
=========================================================

Use luxury naturally.

Possible environments:

- luxury hotels
- penthouses
- private jets
- supercars
- yachts
- exclusive restaurants
- designer boutiques
- private islands
- royal palaces
- luxury trains
- private clubs
- billionaire estates
- futuristic architecture
- exclusive events

Luxury must SUPPORT the story.

Do not simply list expensive objects.

=========================================================
SOFIA CONTINUITY
=========================================================

Sofia is the SAME recognizable woman throughout.

Every scene MUST contain:

"sofia_visible": true

Every scene MUST describe:

- Sofia's appearance
- Sofia's action
- Sofia's emotion
- location
- time
- lighting
- camera framing
- important objects
- atmosphere

=========================================================
SHOT DESIGN
=========================================================

Use different primary shot types.

Recommended progression:

1. wide cinematic establishing shot
2. medium character shot
3. close-up
4. over-the-shoulder
5. low-angle or dynamic shot
6. emotional reaction close-up
7. dramatic action shot
8. beautiful final cinematic shot

Do not make every scene visually identical.

=========================================================
PACING
=========================================================

The story must have changing energy.

Quiet scenes can breathe.

Discovery scenes should feel tense.

Danger scenes should feel fast.

The climax should feel strongest.

=========================================================
DIALOGUE
=========================================================

Use short natural dialogue.

Do not turn the story into a conversation.

Dialogue should support the action.

=========================================================
OUTPUT
=========================================================

Return ONLY valid JSON.

Use this exact structure:

{{
  "title": "Original title",
  "genre": "Genre",
  "logline": "One sentence",
  "hook": "Opening hook",
  "scenes": [
    {{
      "scene_number": 1,
      "scene_purpose": "Purpose",
      "location": "Specific location",
      "time": "Time of day",
      "duration_hint": "medium",
      "shot_type": "wide",
      "sofia_visible": true,
      "sofia_appearance": "Consistent Sofia appearance",
      "action": "What Sofia does",
      "emotion": "Her emotion",
      "continuity": "Connection to story",
      "luxury_detail": "Important luxury detail",
      "visual_prompt": "Detailed cinematic visual",
      "dialogue": "Short dialogue",
      "narration": "Narration"
    }}
  ],
  "script": "Complete spoken story"
}}

STRICT REQUIREMENTS:

- Exactly 8 scenes.
- Sofia visible in all 8 scenes.
- 820-900 spoken words.
- Aim for 860 words.
- One connected story.
- Strong beginning.
- Escalating middle.
- Meaningful twist.
- Difficult decision.
- Strong climax.
- Emotional ending or cliffhanger.
- No markdown.
- No commentary outside JSON.
"""

    # =====================================================
    # TOPIC NORMALIZER
    # =====================================================

    def _normalize_topic(
        self,
        topic: Any
    ) -> str:

        if isinstance(
            topic,
            dict
        ):

            value = (
                topic.get("topic")
                or topic.get("title")
                or topic.get("idea")
                or (
                    "Sofia discovers a dangerous "
                    "secret inside a luxury empire."
                )
            )

            return str(
                value
            ).strip()

        if topic is None:

            return (
                "Sofia discovers a dangerous "
                "secret inside a luxury empire."
            )

        value = str(
            topic
        ).strip()

        return (
            value
            or
            "Sofia Luxury Story"
        )

    # =====================================================
    # RESPONSE PARSER
    # =====================================================

    def _parse_response(
        self,
        raw: str,
        topic: str,
        duration_minutes: int
    ) -> Dict[str, Any]:

        cleaned = (
            raw
            .strip()
        )

        # -------------------------------------------------
        # Remove markdown fences.
        # -------------------------------------------------

        cleaned = re.sub(
            r"^```(?:json)?\s*",
            "",
            cleaned,
            flags=re.IGNORECASE
        )

        cleaned = re.sub(
            r"\s*```$",
            "",
            cleaned
        )

        data = None

        # -------------------------------------------------
        # First attempt: entire response.
        # -------------------------------------------------

        try:

            data = json.loads(
                cleaned
            )

        except json.JSONDecodeError:

            data = None

        # -------------------------------------------------
        # Second attempt: extract JSON object.
        # -------------------------------------------------

        if not isinstance(
            data,
            dict
        ):

            start = cleaned.find(
                "{"
            )

            end = cleaned.rfind(
                "}"
            )

            if (
                start >= 0
                and
                end > start
            ):

                candidate = (
                    cleaned[
                        start:end + 1
                    ]
                )

                try:

                    data = json.loads(
                        candidate
                    )

                except json.JSONDecodeError:

                    data = None

        # -------------------------------------------------
        # Invalid response.
        # -------------------------------------------------

        if not isinstance(
            data,
            dict
        ):

            logger.warning(
                "⚠️ Groq returned invalid JSON."
            )

            return self._fallback_story(
                topic,
                duration_minutes
            )

        title = str(
            data.get(
                "title",
                "Sofia Luxury Story"
            )
        ).strip()

        genre = str(
            data.get(
                "genre",
                "Luxury Drama"
            )
        ).strip()

        logline = str(
            data.get(
                "logline",
                ""
            )
        ).strip()

        hook = str(
            data.get(
                "hook",
                ""
            )
        ).strip()

        raw_scenes = data.get(
            "scenes",
            []
        )

        if not isinstance(
            raw_scenes,
            list
        ):

            raw_scenes = []

        scenes = (
            self._normalize_scenes(
                raw_scenes
            )
        )

        # -------------------------------------------------
        # Prefer the AI's script.
        # -------------------------------------------------

        script = self._clean_script(
            str(
                data.get(
                    "script",
                    ""
                )
            )
        )

        # -------------------------------------------------
        # If script is missing/too short, construct it
        # from scene narration and dialogue.
        # -------------------------------------------------

        if len(
            script.split()
        ) < 300:

            script = (
                self._build_script_from_scenes(
                    scenes
                )
            )

        word_count = len(
            script.split()
        )

        return {
            "topic": topic,
            "title": title,
            "genre": genre,
            "logline": logline,
            "hook": hook,
            "script": script,
            "scenes": scenes,
            "word_count": word_count,
            "estimated_duration_min": round(
                word_count / 165.0,
                1
            ),
            "language": self.language,
            "niche": self.niche
        }

    # =====================================================
    # STORY VALIDATION
    # =====================================================

    def _story_needs_repair(
        self,
        result: Dict[str, Any]
    ) -> bool:

        if not result:

            return True

        script = str(
            result.get(
                "script",
                ""
            )
        )

        words = len(
            script.split()
        )

        scenes = result.get(
            "scenes",
            []
        )

        # -------------------------------------------------
        # Too short.
        # -------------------------------------------------

        if words < self.TARGET_WORDS_MIN:

            return True

        # -------------------------------------------------
        # Too long.
        # -------------------------------------------------

        if words > 1000:

            return True

        # -------------------------------------------------
        # Wrong scene count.
        # -------------------------------------------------

        if len(scenes) != self.SCENE_COUNT:

            return True

        # -------------------------------------------------
        # Check that every scene contains Sofia.
        # -------------------------------------------------

        for scene in scenes:

            if not scene.get(
                "sofia_visible",
                False
            ):

                return True

            if not str(
                scene.get(
                    "visual_prompt",
                    ""
                )
            ).strip():

                return True

            if not str(
                scene.get(
                    "action",
                    ""
                )
            ).strip():

                return True

        return False

    # =====================================================
    # STORY REPAIR
    # =====================================================

    def _repair_story(
        self,
        result: Dict[str, Any],
        topic: str,
        duration_minutes: int
    ) -> Optional[Dict[str, Any]]:

        old_script = str(
            result.get(
                "script",
                ""
            )
        )

        old_scenes = result.get(
            "scenes",
            []
        )

        repair_prompt = f"""
You are repairing a cinematic Sofia mini-movie.

TOPIC:

{topic}

The previous version did not satisfy the requirements.

PREVIOUS STORY:

{old_script}

PREVIOUS SCENES:

{json.dumps(
    old_scenes,
    ensure_ascii=False,
    indent=2
)}

Rewrite the entire story.

STRICT REQUIREMENTS:

1. Exactly 8 scenes.

2. Approximately 820-900 spoken words.

3. Aim for approximately 860 words.

4. Sofia must be the protagonist.

5. Sofia must be visible in every scene.

6. Sofia must perform meaningful actions.

7. One continuous connected story.

8. Strong hook.

9. Escalating problem.

10. Meaningful twist.

11. Difficult decision.

12. Strong climax.

13. Emotional ending or cliffhanger.

14. Different visual compositions.

15. Luxury environment must support the story.

16. No repeated generic scenes.

17. Natural short dialogue.

18. Narration must advance the story.

19. No production instructions in spoken text.

20. Return ONLY valid JSON.

Use exactly this structure:

{{
  "title": "Title",
  "genre": "Genre",
  "logline": "Logline",
  "hook": "Hook",
  "scenes": [
    {{
      "scene_number": 1,
      "scene_purpose": "Purpose",
      "location": "Location",
      "time": "Time",
      "duration_hint": "medium",
      "shot_type": "wide",
      "sofia_visible": true,
      "sofia_appearance": "Sofia appearance",
      "action": "Sofia action",
      "emotion": "Emotion",
      "continuity": "Continuity",
      "luxury_detail": "Luxury detail",
      "visual_prompt": "Detailed visual prompt",
      "dialogue": "Short dialogue",
      "narration": "Narration"
    }}
  ],
  "script": "Complete spoken story"
}}
"""

        try:

            response = (
                self.client.chat.completions.create(
                    model=self.MODEL,

                    messages=[
                        {
                            "role": "system",
                            "content": (
                                self._system_prompt()
                            )
                        },
                        {
                            "role": "user",
                            "content": repair_prompt
                        }
                    ],

                    temperature=0.78,

                    max_tokens=6500
                )
            )

            raw = (
                response
                .choices[0]
                .message
                .content
                or ""
            )

            repaired = (
                self._parse_response(
                    raw,
                    topic,
                    duration_minutes
                )
            )

            # -------------------------------------------------
            # Accept repaired version only if structurally
            # better than the original.
            # -------------------------------------------------

            if not repaired:

                return None

            repaired_words = len(
                str(
                    repaired.get(
                        "script",
                        ""
                    )
                ).split()
            )

            repaired_scenes = len(
                repaired.get(
                    "scenes",
                    []
                )
            )

            logger.info(
                f"🔧 Repaired story: "
                f"{repaired_words} words / "
                f"{repaired_scenes} scenes"
            )

            if (
                repaired_scenes
                ==
                self.SCENE_COUNT
                and
                repaired_words
                >=
                self.TARGET_WORDS_MIN
            ):

                return repaired

            # -------------------------------------------------
            # If repair is still imperfect, keep the original
            # rather than replacing a good story with a worse
            # one.
            # -------------------------------------------------

            original_words = len(
                old_script.split()
            )

            original_scenes = len(
                old_scenes
            )

            if (
                repaired_words
                >
                original_words
                and
                repaired_scenes
                >=
                original_scenes
            ):

                return repaired

            return None

        except Exception as e:

            logger.warning(
                f"Story repair failed: {e}"
            )

            return None

    # =====================================================
    # SCENE NORMALIZER
    # =====================================================

    def _normalize_scenes(
        self,
        scenes: List[Any]
    ) -> List[Dict[str, Any]]:

        normalized = []

        shot_types = [
            "wide cinematic establishing shot",
            "medium character shot",
            "close-up",
            "over-the-shoulder",
            "low-angle dynamic shot",
            "emotional reaction close-up",
            "dramatic action shot",
            "final cinematic shot"
        ]

        for index, scene in enumerate(
            scenes[:self.SCENE_COUNT]
        ):

            if not isinstance(
                scene,
                dict
            ):

                continue

            number = index + 1

            visual_prompt = str(
                scene.get(
                    "visual_prompt",
                    ""
                )
            ).strip()

            # -------------------------------------------------
            # Guarantee Sofia is mentioned in the visual
            # direction.
            # -------------------------------------------------

            if (
                "sofia"
                not in
                visual_prompt.lower()
            ):

                visual_prompt = (
                    "Sofia is clearly visible as "
                    "the central protagonist. "
                    +
                    visual_prompt
                )

            normalized_scene = {

                "scene_number": number,

                "scene_purpose": str(
                    scene.get(
                        "scene_purpose",
                        ""
                    )
                ).strip(),

                "location": str(
                    scene.get(
                        "location",
                        "Luxury location"
                    )
                ).strip(),

                "time": str(
                    scene.get(
                        "time",
                        "Cinematic lighting"
                    )
                ).strip(),

                "duration_hint": str(
                    scene.get(
                        "duration_hint",
                        "medium"
                    )
                ).strip(),

                "shot_type": str(
                    scene.get(
                        "shot_type",
                        shot_types[index]
                    )
                ).strip(),

                "sofia_visible": True,

                "sofia_appearance": str(
                    scene.get(
                        "sofia_appearance",
                        "Sofia with consistent recognizable facial identity"
                    )
                ).strip(),

                "action": str(
                    scene.get(
                        "action",
                        "Sofia takes meaningful action."
                    )
                ).strip(),

                "emotion": str(
                    scene.get(
                        "emotion",
                        "determined"
                    )
                ).strip(),

                "continuity": str(
                    scene.get(
                        "continuity",
                        ""
                    )
                ).strip(),

                "luxury_detail": str(
                    scene.get(
                        "luxury_detail",
                        ""
                    )
                ).strip(),

                "visual_prompt": visual_prompt,

                "dialogue": str(
                    scene.get(
                        "dialogue",
                        ""
                    )
                ).strip(),

                "narration": str(
                    scene.get(
                        "narration",
                        ""
                    )
                ).strip()
            }

            normalized.append(
                normalized_scene
            )

        return normalized

    # =====================================================
    # BUILD SCRIPT FROM SCENES
    # =====================================================

    def _build_script_from_scenes(
        self,
        scenes: List[Dict[str, Any]]
    ) -> str:

        parts = []

        for scene in scenes:

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

            if narration:

                parts.append(
                    narration
                )

            if dialogue:

                parts.append(
                    dialogue
                )

        return self._clean_script(
            "\n\n".join(
                parts
            )
        )

    # =====================================================
    # FINALIZE
    # =====================================================

    def _finalize_result(
        self,
        result: Dict[str, Any],
        topic: str
    ) -> Dict[str, Any]:

        if not result:

            return self._fallback_story(
                topic,
                5
            )

        script = self._clean_script(
            str(
                result.get(
                    "script",
                    ""
                )
            )
        )

        scenes = result.get(
            "scenes",
            []
        )

        # -------------------------------------------------
        # If scene script is longer/better, use it.
        # -------------------------------------------------

        scene_script = (
            self._build_script_from_scenes(
                scenes
            )
        )

        if len(
            scene_script.split()
        ) > len(
            script.split()
        ):

            script = scene_script

        # -------------------------------------------------
        # If everything is too short, use fallback.
        # -------------------------------------------------

        if len(
            script.split()
        ) < 500:

            logger.warning(
                "⚠️ Final story is extremely short."
            )

            fallback = (
                self._fallback_story(
                    topic,
                    5
                )
            )

            # Keep the AI result if it somehow has more
            # content than the fallback.
            if len(
                fallback["script"].split()
            ) > len(
                script.split()
            ):

                return fallback

        word_count = len(
            script.split()
        )

        result["topic"] = topic

        result["script"] = script

        result["scenes"] = scenes

        result["word_count"] = word_count

        result[
            "estimated_duration_min"
        ] = round(
            word_count / 165.0,
            1
        )

        result["language"] = (
            self.language
        )

        result["niche"] = (
            self.niche
        )

        return result

    # =====================================================
    # SCRIPT CLEANER
    # =====================================================

    def _clean_script(
        self,
        script: str
    ) -> str:

        if not script:

            return ""

        patterns = [

            r"\[pause\]",

            r"\[music\]",

            r"\[laughs?\]",

            r"\[chuckles?\]",

            r"\[sound effect[s]?\]",

            r"\[sfx\]",

            r"\[camera[^\]]*\]",

            r"\[zoom[^\]]*\]",

            r"\[cut[^\]]*\]",

            r"\[fade[^\]]*\]",

            r"\[scene[^\]]*\]",

            r"\[shot[^\]]*\]",

            r"\[transition[^\]]*\]",
        ]

        cleaned = script

        for pattern in patterns:

            cleaned = re.sub(
                pattern,
                "",
                cleaned,
                flags=re.IGNORECASE
            )

        # -------------------------------------------------
        # Remove accidental markdown fences.
        # -------------------------------------------------

        cleaned = re.sub(
            r"```(?:text|markdown)?",
            "",
            cleaned,
            flags=re.IGNORECASE
        )

        cleaned = cleaned.replace(
            "```",
            ""
        )

        cleaned = cleaned.replace(
            "\\n",
            "\n"
        )

        # -------------------------------------------------
        # Normalize spaces.
        # -------------------------------------------------

        cleaned = re.sub(
            r"[ \t]+",
            " ",
            cleaned
        )

        cleaned = re.sub(
            r"\n{3,}",
            "\n\n",
            cleaned
        )

        return cleaned.strip()

    # =====================================================
    # FALLBACK STORY
    # =====================================================

    def _fallback_story(
        self,
        topic: str,
        duration_minutes: int
    ) -> Dict[str, Any]:

        title = (
            "Sofia and the Hidden Empire"
        )

        script = """
Sofia thought the invitation was simply another luxury event.

The black car stopped beneath the golden lights of the most
exclusive hotel in the city. Sofia stepped onto the red carpet,
but something immediately felt wrong.

She had been invited to a private room upstairs.

She just didn't know why.

Inside, crystal chandeliers reflected across hundreds of glasses.
Everyone was celebrating, yet Sofia noticed one man watching her
from across the ballroom.

Then her phone vibrated.

Do not trust anyone here.

Sofia looked up.

The man was gone.

She followed him through a private corridor and discovered an
elevator hidden behind an enormous painting.

There was no button for the basement.

Instead, there was a fingerprint scanner.

Sofia placed her hand against it.

The doors opened.

Beneath the hotel was a secret facility filled with screens,
maps and photographs of luxury properties around the world.

Then Sofia saw something that made her stop.

Her own name was on the main screen.

A voice came from behind her.

“You were never invited here by accident.”

Sofia turned.

The stranger from the ballroom stood in the doorway.

He told her the hotel belonged to a secret organization that had
controlled powerful businesses for decades.

Now someone inside the organization wanted Sofia dead.

Sofia stared at him.

“Why me?”

He looked at the screen.

“Because your family built this empire.”

Everything Sofia believed about her life suddenly changed.

Her family's wealth had never been just wealth.

It had been a doorway into a hidden world.

Then the lights went out.

An alarm screamed through the facility.

“They found us,” the stranger whispered.

Sofia ran.

Security doors slammed behind her as footsteps echoed through
the underground corridors.

She reached a private garage.

A black supercar was waiting.

Sofia jumped inside and drove into the night.

But then her phone rang.

The caller ID displayed her own number.

She answered.

A woman's voice whispered,

“You should never have opened that door.”

The call ended.

Sofia stared through the windshield.

For the first time that night, she smiled.

Now she knew where the empire was hiding.

And she knew exactly what she had to do next.

She turned the car around.

Sofia was going back.
"""

        script = self._clean_script(
            script
        )

        scenes = [

            {
                "scene_number": 1,
                "scene_purpose": "Hook",
                "location": "Ultra-luxury hotel entrance",
                "time": "Night",
                "duration_hint": "short",
                "shot_type": "wide cinematic establishing shot",
                "sofia_visible": True,
                "sofia_appearance": "Elegant Sofia in a luxurious evening outfit.",
                "action": "Sofia steps from a black luxury car onto a golden-lit red carpet.",
                "emotion": "Confident but uneasy",
                "continuity": "Begins the mystery.",
                "luxury_detail": "Black luxury car, golden hotel entrance and red carpet.",
                "visual_prompt": "Sofia clearly visible stepping from a black luxury car outside an ultra-luxury hotel at night, golden architectural lighting, elegant red carpet, cinematic wide composition, sophisticated evening fashion, realistic face and luxurious atmosphere.",
                "dialogue": "",
                "narration": "Sofia thought the invitation was simply another luxury event."
            },

            {
                "scene_number": 2,
                "scene_purpose": "Establish Sofia's world",
                "location": "Luxury ballroom",
                "time": "Night",
                "duration_hint": "medium",
                "shot_type": "medium character shot",
                "sofia_visible": True,
                "sofia_appearance": "Same Sofia with consistent recognizable facial identity.",
                "action": "Sofia studies the guests while holding a glass.",
                "emotion": "Suspicious",
                "continuity": "She notices a mysterious man watching her.",
                "luxury_detail": "Crystal chandeliers, designer clothing and elegant guests.",
                "visual_prompt": "Sofia clearly visible in an extravagant billionaire ballroom, crystal chandeliers, elegant guests and champagne glasses, Sofia looking suspiciously across the room, cinematic medium shot and rich warm lighting.",
                "dialogue": "",
                "narration": "Inside, everything looked perfect. But Sofia noticed one man watching her."
            },

            {
                "scene_number": 3,
                "scene_purpose": "Discovery",
                "location": "Hidden hotel elevator",
                "time": "Night",
                "duration_hint": "medium",
                "shot_type": "close-up",
                "sofia_visible": True,
                "sofia_appearance": "Same Sofia.",
                "action": "Sofia places her hand against a hidden fingerprint scanner.",
                "emotion": "Shocked curiosity",
                "continuity": "The hidden elevator leads underground.",
                "luxury_detail": "Ornate painting and secret mechanism.",
                "visual_prompt": "Close-up of Sofia placing her hand against a mysterious fingerprint scanner hidden behind an ornate luxury hotel painting, her shocked expression clearly visible, dramatic cinematic lighting.",
                "dialogue": "",
                "narration": "Sofia placed her hand against the scanner, and the hidden doors opened."
            },

            {
                "scene_number": 4,
                "scene_purpose": "Escalation",
                "location": "Secret underground facility",
                "time": "Night",
                "duration_hint": "short",
                "shot_type": "over-the-shoulder",
                "sofia_visible": True,
                "sofia_appearance": "Same Sofia.",
                "action": "Sofia discovers her name on a massive screen.",
                "emotion": "Fear and disbelief",
                "continuity": "She learns her family is connected to the secret empire.",
                "luxury_detail": "Advanced screens, global maps and a hidden control room.",
                "visual_prompt": "Over-the-shoulder cinematic shot with Sofia clearly visible in the foreground staring at a huge futuristic screen displaying her name, secret underground luxury facility, dramatic blue lighting and tense atmosphere.",
                "dialogue": "\"Why me?\"",
                "narration": "Then Sofia saw her own name on the main screen."
            },

            {
                "scene_number": 5,
                "scene_purpose": "Major twist",
                "location": "Secret control room",
                "time": "Night",
                "duration_hint": "medium",
                "shot_type": "emotional reaction close-up",
                "sofia_visible": True,
                "sofia_appearance": "Same Sofia with consistent recognizable face.",
                "action": "Sofia realizes her family built the hidden empire.",
                "emotion": "Shock and betrayal",
                "continuity": "The revelation changes everything she believed about her life.",
                "luxury_detail": "Global property maps and sophisticated control systems.",
                "visual_prompt": "Cinematic close-up of Sofia reacting in disbelief inside a secret billionaire control room, glowing global maps behind her, sophisticated luxury technology and emotional realistic facial expression.",
                "dialogue": "\"My family built this?\"",
                "narration": "Everything Sofia believed about her family's wealth suddenly changed."
            },

            {
                "scene_number": 6,
                "scene_purpose": "Decision and escape",
                "location": "Underground private garage",
                "time": "Night",
                "duration_hint": "short",
                "shot_type": "dynamic dramatic shot",
                "sofia_visible": True,
                "sofia_appearance": "Same Sofia in the same evening outfit.",
                "action": "Sofia runs toward a waiting black supercar.",
                "emotion": "Determined and afraid",
                "continuity": "She chooses to escape and uncover the truth.",
                "luxury_detail": "Black supercar and polished underground garage.",
                "visual_prompt": "Sofia running toward a black luxury supercar inside a secret underground garage, dramatic lighting, determined expression, cinematic dynamic composition, luxurious architecture and strong sense of urgency.",
                "dialogue": "",
                "narration": "Sofia knew she had seconds to escape."
            },

            {
                "scene_number": 7,
                "scene_purpose": "Climax",
                "location": "Luxury city highway",
                "time": "Night",
                "duration_hint": "short",
                "shot_type": "low-angle dynamic shot",
                "sofia_visible": True,
                "sofia_appearance": "Same Sofia with consistent recognizable identity.",
                "action": "Sofia drives through the city while receiving a mysterious call.",
                "emotion": "Focused and fearless",
                "continuity": "The mysterious caller reveals that the danger is not over.",
                "luxury_detail": "Supercar, illuminated skyscrapers and city lights.",
                "visual_prompt": "Sofia clearly visible driving a black luxury supercar through a spectacular city at night, illuminated skyscrapers reflected on the windshield, intense focused expression and cinematic low-angle perspective.",
                "dialogue": "\"Who are you?\"",
                "narration": "Then her phone rang. The caller ID displayed her own number."
            },

            {
                "scene_number": 8,
                "scene_purpose": "Resolution and cliffhanger",
                "location": "City overlook",
                "time": "Night",
                "duration_hint": "medium",
                "shot_type": "final cinematic shot",
                "sofia_visible": True,
                "sofia_appearance": "Same Sofia, elegant and confident.",
                "action": "Sofia looks across the city and turns the car around.",
                "emotion": "Calm determination",
                "continuity": "She decides to return and confront the hidden empire.",
                "luxury_detail": "Luxury car overlooking a glowing city skyline.",
                "visual_prompt": "Beautiful cinematic final shot of Sofia standing beside her black luxury car overlooking a breathtaking city skyline at night, elegant fashion, calm determined expression, glowing skyscrapers and premium luxury movie aesthetic.",
                "dialogue": "\"I'm going back.\"",
                "narration": "Now Sofia knew where the empire was hiding. And she knew exactly what she had to do next."
            }
        ]

        word_count = len(
            script.split()
        )

        return {
            "topic": topic,
            "title": title,
            "genre": "Luxury Mystery Action",
            "logline": (
                "Sofia discovers that her family's "
                "luxury empire hides a dangerous secret."
            ),
            "hook": (
                "Sofia enters a luxury hotel and "
                "discovers someone has been waiting for her."
            ),
            "script": script,
            "scenes": scenes,
            "word_count": word_count,
            "estimated_duration_min": round(
                word_count / 165.0,
                1
            ),
            "language": self.language,
            "niche": self.niche
        }

    # =====================================================
    # MULTIPLE STORIES
    # =====================================================

    def generate_multiple(
        self,
        topics: List[Any],
        count: int = 3
    ) -> List[Dict[str, Any]]:

        stories = []

        for topic in topics[:count]:

            story = self.generate_script(
                topic,
                duration_minutes=5
            )

            if (
                story
                and
                not story.get("error")
            ):

                stories.append(
                    story
                )

        return stories


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    print(
        "=" * 70
    )

    print(
        "🎬 SOFIA LUXURY STORY GENERATOR TEST"
    )

    print(
        "=" * 70
    )

    generator = ScriptGenerator(
        language="english",
        niche="luxury_story"
    )

    test_topic = {
        "topic": (
            "Sofia discovers a secret hidden "
            "inside a billionaire's luxury empire"
        ),
        "source": "Sofia Luxury Story"
    }

    result = generator.generate_script(
        test_topic,
        duration_minutes=5
    )

    if result.get("script"):

        print(
            f"\n🎬 TITLE: "
            f"{result.get('title')}"
        )

        print(
            f"🎭 GENRE: "
            f"{result.get('genre')}"
        )

        print(
            f"📝 WORDS: "
            f"{result.get('word_count')}"
        )

        print(
            f"⏱️ ESTIMATED LENGTH: "
            f"{result.get('estimated_duration_min')} minutes"
        )

        print(
            f"🎞️ SCENES: "
            f"{len(result.get('scenes', []))}"
        )

        print(
            "\n" + "-" * 70
        )

        print(
            result["script"][:3000]
        )

        print(
            "\n" + "-" * 70
        )

        print(
            "\n✅ Cinematic Sofia story generated."
        )

    else:

        print(
            f"\n❌ ERROR: "
            f"{result.get('error')}"
        )
