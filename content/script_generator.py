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
- Approximately 700-800 spoken words
- Exactly 8 major story scenes
- Strong story progression
- Sofia visible in every scene
- Different visual compositions
- Luxury environments
- Emotional progression
- Mid-story twist
- Climax
- Resolution or cliffhanger

The output is consumed by:
- auto_scheduler.py
- video_creator_pro.py
- voiceover generation
"""

import os
import json
import re
from typing import Dict, List, Any

from loguru import logger
from dotenv import load_dotenv

try:
    from groq import Groq
except ImportError:
    import groq
    Groq = groq.Groq


load_dotenv()


class ScriptGenerator:

    # =========================================================
    # CORE SETTINGS
    # =========================================================

    MODEL = "openai/gpt-oss-120b"

    TARGET_WORDS_MIN = 700
    TARGET_WORDS_MAX = 800
    TARGET_WORDS = 760

    SCENE_COUNT = 8

    WORDS_PER_MINUTE = 150.0

    MAX_TOKENS = 6000

    # =========================================================
    # INITIALIZATION
    # =========================================================

    def __init__(
        self,
        language: str = "english",
        niche: str = "luxury_story"
    ):
        self.language = language
        self.niche = niche

        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY is missing. "
                "Add it to your environment or GitHub Actions secrets."
            )

        self.client = Groq(api_key=api_key)

        logger.info(
            "🎬 Sofia Story Generator initialized: "
            f"{self.language}/{self.niche}"
        )

    # =========================================================
    # MAIN GENERATOR
    # =========================================================

    def generate_script(
        self,
        topic: Any,
        duration_minutes: int = 5
    ) -> Dict[str, Any]:

        topic_text = self._normalize_topic(topic)

        logger.info(
            "🎬 Creating Sofia cinematic story: "
            f"{topic_text[:120]}"
        )

        prompt = self._build_story_prompt(
            topic_text,
            duration_minutes
        )

        try:

            raw = self._request_story(
                prompt
            )

            result = self._parse_response(
                raw,
                topic_text,
                duration_minutes
            )

            # -------------------------------------------------
            # If the model returned too few spoken words,
            # ask Groq once to repair/expand the story.
            # -------------------------------------------------

            word_count = result.get(
                "word_count",
                0
            )

            if (
                word_count < self.TARGET_WORDS_MIN
                or word_count > self.TARGET_WORDS_MAX
            ):

                logger.warning(
                    "⚠️ Story word count outside target: "
                    f"{word_count}. Attempting repair."
                )

                repaired = self._repair_story(
                    result,
                    topic_text,
                    duration_minutes
                )

                if repaired:
                    result = repaired

            # -------------------------------------------------
            # Final normalization.
            # -------------------------------------------------

            result = self._finalize_result(
                result,
                topic_text,
                duration_minutes
            )

            logger.info(
                "✅ Sofia cinematic story created: "
                f"{result.get('title', 'Untitled')} | "
                f"{result.get('word_count', 0)} words | "
                f"{len(result.get('scenes', []))} scenes | "
                f"{result.get('estimated_duration_min', 0)} min"
            )

            return result

        except Exception as e:

            logger.exception(
                f"❌ Sofia story generation failed: {e}"
            )

            logger.warning(
                "⚠️ Using built-in cinematic fallback story."
            )

            return self._fallback_story(
                topic_text,
                duration_minutes
            )

    # =========================================================
    # GROQ REQUEST
    # =========================================================

    def _request_story(
        self,
        prompt: str
    ) -> str:

        response = self.client.chat.completions.create(
            model=self.MODEL,
            messages=[
                {
                    "role": "system",
                    "content": self._system_prompt()
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.82,
            max_tokens=self.MAX_TOKENS
        )

        return (
            response.choices[0].message.content
            or ""
        )

    # =========================================================
    # SYSTEM PROMPT
    # =========================================================

    def _system_prompt(self) -> str:

        return """
You are the head writer and visual story director for
SOFIA LUXURY STORY.

Create original vertical mini-movies in which Sofia is
the main protagonist.

Sofia is a real character inside the story.

She is NOT a presenter.

She is NOT simply standing around looking beautiful.

She must make decisions, take actions, discover things,
face consequences and drive the story.

=========================================================
ABSOLUTE STORY RULES
=========================================================

1. Sofia is the protagonist.

2. Sofia must be visible in every scene.

3. Sofia must perform meaningful actions.

4. Sofia must have a clear goal.

5. Sofia must face a problem.

6. Sofia must have something important to lose.

7. Sofia must discover something.

8. Sofia must make a difficult decision.

9. Sofia must personally drive the climax.

10. The ending must come from Sofia's actions.

11. Every scene must connect logically to the next.

12. Do not create eight unrelated luxury scenes.

13. Do not repeat the same event in different words.

14. Do not repeatedly describe Sofia standing,
smiling, walking or looking beautiful.

15. Sofia should interact with:
- people
- vehicles
- technology
- buildings
- objects
- locations
- important story props

16. Keep Sofia's facial identity consistent.

17. Clothing changes must have a story reason.

18. Important objects should remain consistent.

19. Supporting characters must have consistent roles.

20. The story must feel like a real short movie.

=========================================================
STORY ARC
=========================================================

Scene 1:
HOOK.

Start immediately with something interesting.

Scene 2:
SETUP.

Show Sofia's world and establish her goal.

Scene 3:
PROBLEM.

Something directly threatens Sofia or her goal.

Scene 4:
ESCALATION.

Sofia investigates or takes action.

Scene 5:
TWIST.

Reveal information that changes the meaning of
earlier events.

Scene 6:
DECISION.

Sofia must choose what to do.

Scene 7:
CLIMAX.

Sofia personally confronts the main problem.

Scene 8:
ENDING.

Give emotional payoff, resolution or a strong
cliffhanger.

=========================================================
VISUAL RULES
=========================================================

Every scene must have a different visual purpose.

Use different compositions such as:

wide establishing shot
medium character shot
close-up
extreme close-up
over-the-shoulder
side profile
low angle
high angle
tracking-style composition
point of view
environmental detail

Sofia must remain visually recognizable.

Every visual prompt must contain:

- Sofia
- Sofia's action
- Sofia's emotion
- location
- lighting
- camera framing
- important objects
- atmosphere
- luxury detail when appropriate

Do not make every scene look like the same photograph.

The visual prompt should describe what is actually
happening in the story.

=========================================================
LUXURY WORLD
=========================================================

Luxury may include:

luxury hotels
penthouse apartments
private jets
supercars
yachts
exclusive restaurants
designer boutiques
private islands
royal palaces
luxury trains
private clubs
beautiful estates
futuristic architecture
exclusive events

Luxury must support the story.

Do not simply list expensive objects.

=========================================================
DIALOGUE
=========================================================

Dialogue must be short and natural.

Avoid theatrical speeches.

Good example:

"I knew you would come."

Sofia looked at him.

"Then tell me the truth."

=========================================================
NARRATION
=========================================================

Narration must move the story forward.

Do not describe obvious things like:

"Sofia is standing in a hotel."

Instead explain what is happening,
what Sofia discovers,
what changes,
or what she decides.

=========================================================
SPOKEN AUDIO
=========================================================

The final spoken story should be approximately
700-800 words.

Target approximately 760 words.

Do not include:

[pause]
[music]
[sound effect]
[camera]
[zoom]
[cut]
[scene]
[fade]
[SFX]

Do not include channel introductions.

Do not say:

"Welcome back to my channel."

The first sentence must create curiosity.

=========================================================
OUTPUT
=========================================================

Return ONLY valid JSON.

No markdown.

No explanation outside JSON.
"""

    # =========================================================
    # STORY PROMPT
    # =========================================================

    def _build_story_prompt(
        self,
        topic: str,
        duration: int
    ) -> str:

        return f"""
Create an ORIGINAL Sofia-centered cinematic story.

TOPIC:

{topic}

TARGET LENGTH:

Approximately {duration} minutes.

TARGET SPOKEN WORD COUNT:

{self.TARGET_WORDS_MIN}-{self.TARGET_WORDS_MAX} words.

Ideal target:

{self.TARGET_WORDS} words.

FORMAT:

Vertical 9:16 cinematic mini-movie.

NUMBER OF SCENES:

Exactly {self.SCENE_COUNT}.

=========================================================
STORY STRUCTURE
=========================================================

SCENE 1 — HOOK

Open with something unusual, dangerous,
beautiful or mysterious.

Sofia must already be involved.

The audience should immediately wonder:

"What is happening?"

SCENE 2 — SETUP

Show Sofia's world.

Establish her goal.

Make the audience understand why the situation
matters to her.

SCENE 3 — PROBLEM

Introduce a serious problem.

The problem must directly affect Sofia.

SCENE 4 — ESCALATION

Sofia investigates, follows someone,
discovers evidence, travels somewhere,
escapes danger or takes another meaningful action.

SCENE 5 — TWIST

Reveal information that changes what the audience
thought was happening.

The twist must connect to earlier scenes.

SCENE 6 — DECISION

Sofia must make a difficult choice.

Do not allow another character to solve the problem.

Sofia drives the story.

SCENE 7 — CLIMAX

Sofia confronts the main problem.

This should contain the highest emotional tension.

SCENE 8 — ENDING

Give emotional payoff, resolution or a compelling
cliffhanger.

End with a memorable Sofia moment.

=========================================================
CONTINUITY
=========================================================

Every scene must connect to the previous scene.

If Sofia enters a hotel, continue from that hotel.

If Sofia discovers an object, remember it.

If Sofia is wearing a particular outfit,
keep it consistent until a story reason changes it.

If another character appears,
keep that character's role consistent.

=========================================================
VISUAL CONTINUITY
=========================================================

Sofia must be visible in EVERY scene.

Every scene must contain:

"sofia_visible": true

Describe Sofia consistently.

Every visual prompt must explicitly mention Sofia.

Every scene should have a different primary shot type.

=========================================================
SCENE PACING
=========================================================

Do not make every scene equally slow.

Danger, discovery, escape and confrontation
should feel energetic.

Emotional scenes can breathe.

=========================================================
OUTPUT JSON
=========================================================

Return exactly this structure:

{{
  "title": "Original title",
  "genre": "Genre",
  "logline": "One sentence describing the story",
  "hook": "Opening hook",
  "scenes": [
    {{
      "scene_number": 1,
      "scene_purpose": "Purpose of this scene",
      "location": "Specific location",
      "time": "Time of day",
      "duration_hint": "short",
      "shot_type": "wide",
      "sofia_visible": true,
      "sofia_appearance": "Consistent description of Sofia",
      "action": "Meaningful action Sofia performs",
      "emotion": "Sofia's emotional state",
      "continuity": "How this connects to the story",
      "luxury_detail": "Important environmental detail",
      "visual_prompt": "Detailed cinematic image prompt",
      "dialogue": "Short natural dialogue",
      "narration": "Story narration"
    }}
  ],
  "script": "Complete spoken story"
}}

FINAL RULES:

- Exactly 8 scenes.
- Sofia visible in all 8.
- Approximately 700-800 spoken words.
- One connected story.
- Strong opening.
- Clear problem.
- Escalation.
- Meaningful twist.
- Sofia makes the key decision.
- Sofia drives the climax.
- Memorable ending.
- No markdown.
- No commentary outside JSON.
"""

    # =========================================================
    # TOPIC NORMALIZER
    # =========================================================

    def _normalize_topic(
        self,
        topic: Any
    ) -> str:

        if isinstance(topic, dict):

            value = (
                topic.get("topic")
                or topic.get("title")
                or topic.get("idea")
                or "Sofia discovers a dangerous secret "
                   "inside a luxury empire."
            )

            return str(value).strip()

        if topic is None:

            return (
                "Sofia discovers a dangerous secret "
                "inside a luxury empire."
            )

        value = str(topic).strip()

        if not value:
            return "Sofia Luxury Story"

        return value

    # =========================================================
    # RESPONSE PARSER
    # =========================================================

    def _parse_response(
        self,
        raw: str,
        topic: str,
        duration_minutes: int
    ) -> Dict[str, Any]:

        cleaned = self._clean_json_text(
            raw
        )

        data = self._load_json(
            cleaned
        )

        if not isinstance(data, dict):

            logger.warning(
                "⚠️ Groq did not return valid JSON."
            )

            return self._fallback_story(
                topic,
                duration_minutes
            )

        title = self._safe_text(
            data.get(
                "title",
                "Sofia Luxury Story"
            )
        )

        genre = self._safe_text(
            data.get(
                "genre",
                "Luxury Drama"
            )
        )

        logline = self._safe_text(
            data.get(
                "logline",
                ""
            )
        )

        hook = self._safe_text(
            data.get(
                "hook",
                ""
            )
        )

        raw_scenes = data.get(
            "scenes",
            []
        )

        if not isinstance(raw_scenes, list):
            raw_scenes = []

        scenes = self._normalize_scenes(
            raw_scenes
        )

        script = self._clean_script(
            self._safe_text(
                data.get(
                    "script",
                    ""
                )
            )
        )

        # -----------------------------------------------------
        # Build the spoken script from scenes if the model
        # returned an unusable script field.
        # -----------------------------------------------------

        if len(script.split()) < 250:

            script = self._build_script_from_scenes(
                scenes
            )

        # -----------------------------------------------------
        # If the model completely failed, use fallback.
        # -----------------------------------------------------

        if len(script.split()) < 250:

            logger.warning(
                "⚠️ Generated story was too short. "
                "Using cinematic fallback."
            )

            return self._fallback_story(
                topic,
                duration_minutes
            )

        return {
            "topic": topic,
            "title": title,
            "genre": genre,
            "logline": logline,
            "hook": hook,
            "script": script,
            "scenes": scenes,
            "word_count": len(script.split()),
            "estimated_duration_min": round(
                len(script.split())
                / self.WORDS_PER_MINUTE,
                1
            ),
            "language": self.language,
            "niche": self.niche
        }

    # =========================================================
    # JSON CLEANER
    # =========================================================

    def _clean_json_text(
        self,
        text: str
    ) -> str:

        if not text:
            return ""

        cleaned = text.strip()

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

        return cleaned.strip()

    # =========================================================
    # JSON LOADER
    # =========================================================

    def _load_json(
        self,
        text: str
    ):

        if not text:
            return None

        try:
            return json.loads(text)

        except json.JSONDecodeError:
            pass

        start = text.find("{")
        end = text.rfind("}")

        if start < 0 or end <= start:
            return None

        possible_json = text[
            start:end + 1
        ]

        try:
            return json.loads(
                possible_json
            )

        except json.JSONDecodeError:

            # Try removing common control characters.
            possible_json = re.sub(
                r"[\x00-\x08\x0b\x0c\x0e-\x1f]",
                "",
                possible_json
            )

            try:
                return json.loads(
                    possible_json
                )

            except json.JSONDecodeError:
                return None

    # =========================================================
    # SCENE NORMALIZER
    # =========================================================

    def _normalize_scenes(
        self,
        scenes: List[Any]
    ) -> List[Dict[str, Any]]:

        shot_types = [
            "wide cinematic establishing shot",
            "medium character shot",
            "close-up",
            "over-the-shoulder",
            "low-angle dramatic shot",
            "emotional reaction close-up",
            "dynamic cinematic shot",
            "beautiful final cinematic shot"
        ]

        normalized = []

        for index in range(
            min(
                len(scenes),
                self.SCENE_COUNT
            )
        ):

            scene = scenes[index]

            if not isinstance(scene, dict):
                continue

            scene_number = index + 1

            shot_type = self._safe_text(
                scene.get(
                    "shot_type",
                    ""
                )
            )

            if not shot_type:
                shot_type = shot_types[
                    index
                ]

            sofia_appearance = self._safe_text(
                scene.get(
                    "sofia_appearance",
                    ""
                )
            )

            if not sofia_appearance:
                sofia_appearance = (
                    "Sofia, the same recognizable "
                    "female protagonist with consistent "
                    "facial identity."
                )

            action = self._safe_text(
                scene.get(
                    "action",
                    ""
                )
            )

            if not action:
                action = (
                    "Sofia takes meaningful action "
                    "that advances the story."
                )

            emotion = self._safe_text(
                scene.get(
                    "emotion",
                    ""
                )
            )

            if not emotion:
                emotion = "determined"

            location = self._safe_text(
                scene.get(
                    "location",
                    ""
                )
            )

            if not location:
                location = "Luxury cinematic location"

            time = self._safe_text(
                scene.get(
                    "time",
                    ""
                )
            )

            if not time:
                time = "Night"

            visual_prompt = self._safe_text(
                scene.get(
                    "visual_prompt",
                    ""
                )
            )

            # -------------------------------------------------
            # Force Sofia into every visual prompt.
            # -------------------------------------------------

            if not re.search(
                r"\bsofia\b",
                visual_prompt,
                flags=re.IGNORECASE
            ):

                visual_prompt = (
                    "Sofia is clearly visible as the "
                    "central protagonist. "
                    + visual_prompt
                )

            # -------------------------------------------------
            # Strengthen empty visual prompts.
            # -------------------------------------------------

            if len(visual_prompt) < 40:

                visual_prompt = (
                    f"Cinematic {shot_type} of Sofia "
                    f"in {location} during {time}. "
                    f"Sofia is {action} while feeling "
                    f"{emotion}. "
                    f"{sofia_appearance}. "
                    "Photorealistic cinematic lighting, "
                    "realistic environment, detailed "
                    "luxury production design, natural "
                    "human expression, premium movie "
                    "aesthetic, Sofia clearly visible."
                )

            normalized_scene = {
                "scene_number": scene_number,

                "scene_purpose": self._safe_text(
                    scene.get(
                        "scene_purpose",
                        ""
                    )
                ),

                "location": location,

                "time": time,

                "duration_hint": self._safe_text(
                    scene.get(
                        "duration_hint",
                        "medium"
                    )
                ),

                "shot_type": shot_type,

                "sofia_visible": True,

                "sofia_appearance":
                    sofia_appearance,

                "action": action,

                "emotion": emotion,

                "continuity": self._safe_text(
                    scene.get(
                        "continuity",
                        ""
                    )
                ),

                "luxury_detail": self._safe_text(
                    scene.get(
                        "luxury_detail",
                        ""
                    )
                ),

                "visual_prompt":
                    visual_prompt,

                "dialogue": self._clean_script(
                    self._safe_text(
                        scene.get(
                            "dialogue",
                            ""
                        )
                    )
                ),

                "narration": self._clean_script(
                    self._safe_text(
                        scene.get(
                            "narration",
                            ""
                        )
                    )
                )
            }

            normalized.append(
                normalized_scene
            )

        # -----------------------------------------------------
        # If Groq returns fewer than 8 scenes, fill missing
        # scenes with purposeful structural scenes rather
        # than blindly duplicating one image/story beat.
        # -----------------------------------------------------

        while len(normalized) < self.SCENE_COUNT:

            index = len(normalized)

            normalized.append(
                self._make_structural_scene(
                    index
                )
            )

        return normalized[
            :self.SCENE_COUNT
        ]

    # =========================================================
    # STRUCTURAL SCENE FALLBACK
    # =========================================================

    def _make_structural_scene(
        self,
        index: int
    ) -> Dict[str, Any]:

        scene_number = index + 1

        shot_types = [
            "wide cinematic establishing shot",
            "medium character shot",
            "close-up",
            "over-the-shoulder",
            "low-angle dramatic shot",
            "emotional reaction close-up",
            "dynamic cinematic shot",
            "beautiful final cinematic shot"
        ]

        actions = [
            "Sofia enters the location and notices something unusual.",
            "Sofia examines the surroundings while searching for answers.",
            "Sofia discovers an important clue.",
            "Sofia follows the clue into a more dangerous situation.",
            "Sofia realizes that someone has been hiding the truth from her.",
            "Sofia makes a difficult decision and takes control.",
            "Sofia confronts the danger directly.",
            "Sofia looks toward the future after everything has changed."
        ]

        emotions = [
            "curious and uneasy",
            "suspicious",
            "shocked",
            "tense",
            "deeply surprised",
            "determined",
            "fearless",
            "calm and powerful"
        ]

        locations = [
            "ultra-luxury hotel entrance",
            "private penthouse",
            "exclusive luxury lounge",
            "hidden corridor",
            "secret private facility",
            "underground luxury garage",
            "city skyline at night",
            "luxury rooftop overlooking the city"
        ]

        return {
            "scene_number": scene_number,
            "scene_purpose":
                "Structural continuation of Sofia's story.",
            "location":
                locations[index],
            "time":
                "Night",
            "duration_hint":
                "medium",
            "shot_type":
                shot_types[index],
            "sofia_visible":
                True,
            "sofia_appearance":
                "Sofia, the same recognizable woman with consistent facial identity.",
            "action":
                actions[index],
            "emotion":
                emotions[index],
            "continuity":
                "This scene continues directly from the previous story event.",
            "luxury_detail":
                "Elegant architecture, premium materials and cinematic luxury production design.",
            "visual_prompt":
                (
                    f"Cinematic {shot_types[index]} of Sofia "
                    f"in {locations[index]} at night. "
                    f"Sofia is clearly visible while "
                    f"{actions[index]} "
                    f"Her expression shows {emotions[index]}. "
                    "Photorealistic realistic skin, "
                    "cinematic lighting, detailed luxury "
                    "environment, natural expression, "
                    "premium movie production."
                ),
            "dialogue":
                "",
            "narration":
                ""
        }

    # =========================================================
    # BUILD SPOKEN SCRIPT FROM SCENES
    # =========================================================

    def _build_script_from_scenes(
        self,
        scenes: List[Dict[str, Any]]
    ) -> str:

        parts = []

        for scene in scenes:

            narration = self._clean_script(
                scene.get(
                    "narration",
                    ""
                )
            )

            dialogue = self._clean_script(
                scene.get(
                    "dialogue",
                    ""
                )
            )

            if narration:
                parts.append(
                    narration
                )

            if dialogue:
                parts.append(
                    dialogue
                )

        return "\n\n".join(
            parts
        ).strip()

    # =========================================================
    # SCRIPT CLEANER
    # =========================================================

    def _clean_script(
        self,
        script: str
    ) -> str:

        if not script:
            return ""

        cleaned = str(
            script
        )

        patterns = [
            r"\[pause[^\]]*\]",
            r"\[music[^\]]*\]",
            r"\[laughs?[^\]]*\]",
            r"\[chuckles?[^\]]*\]",
            r"\[sound effect[^\]]*\]",
            r"\[sfx[^\]]*\]",
            r"\[camera[^\]]*\]",
            r"\[zoom[^\]]*\]",
            r"\[cut[^\]]*\]",
            r"\[fade[^\]]*\]",
            r"\[scene[^\]]*\]",
            r"\[transition[^\]]*\]"
        ]

        for pattern in patterns:

            cleaned = re.sub(
                pattern,
                "",
                cleaned,
                flags=re.IGNORECASE
            )

        cleaned = cleaned.replace(
            "\\n",
            "\n"
        )

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

    # =========================================================
    # SAFE TEXT
    # =========================================================

    def _safe_text(
        self,
        value: Any
    ) -> str:

        if value is None:
            return ""

        if isinstance(value, str):
            return value.strip()

        return str(value).strip()

    # =========================================================
    # STORY REPAIR
    # =========================================================

    def _repair_story(
        self,
        result: Dict[str, Any],
        topic: str,
        duration_minutes: int
    ):

        try:

            current_script = self._clean_script(
                result.get(
                    "script",
                    ""
                )
            )

            current_words = len(
                current_script.split()
            )

            repair_prompt = f"""
Rewrite and improve this Sofia cinematic story.

TOPIC:
{topic}

CURRENT STORY:
{current_script}

CURRENT WORD COUNT:
{current_words}

The new spoken story MUST contain
approximately 700-800 words.

Target approximately 760 words.

Keep the same core story idea but improve:

- pacing
- continuity
- emotional progression
- Sofia's actions
- conflict
- twist
- climax
- ending

Sofia must remain the protagonist.

Create exactly 8 connected scenes.

Do not create unrelated scenes.

Return ONLY valid JSON using:

{{
  "title": "Title",
  "genre": "Genre",
  "logline": "Logline",
  "hook": "Hook",
  "scenes": [
    {{
      "scene_number": 1,
      "scene_purpose": "",
      "location": "",
      "time": "",
      "duration_hint": "",
      "shot_type": "",
      "sofia_visible": true,
      "sofia_appearance": "",
      "action": "",
      "emotion": "",
      "continuity": "",
      "luxury_detail": "",
      "visual_prompt": "",
      "dialogue": "",
      "narration": ""
    }}
  ],
  "script": "700-800 word spoken story"
}}
"""

            raw = self._request_story(
                repair_prompt
            )

            cleaned = self._clean_json_text(
                raw
            )

            data = self._load_json(
                cleaned
            )

            if not isinstance(
                data,
                dict
            ):
                return None

            scenes = self._normalize_scenes(
                data.get(
                    "scenes",
                    []
                )
            )

            script = self._clean_script(
                self._safe_text(
                    data.get(
                        "script",
                        ""
                    )
                )
            )

            if len(script.split()) < 250:

                script = self._build_script_from_scenes(
                    scenes
                )

            if len(script.split()) < 250:
                return None

            return {
                "topic": topic,
                "title": self._safe_text(
                    data.get(
                        "title",
                        result.get(
                            "title",
                            "Sofia Luxury Story"
                        )
                    )
                ),
                "genre": self._safe_text(
                    data.get(
                        "genre",
                        result.get(
                            "genre",
                            "Luxury Drama"
                        )
                    )
                ),
                "logline": self._safe_text(
                    data.get(
                        "logline",
                        result.get(
                            "logline",
                            ""
                        )
                    )
                ),
                "hook": self._safe_text(
                    data.get(
                        "hook",
                        result.get(
                            "hook",
                            ""
                        )
                    )
                ),
                "script": script,
                "scenes": scenes,
                "word_count": len(
                    script.split()
                ),
                "estimated_duration_min": round(
                    len(script.split())
                    / self.WORDS_PER_MINUTE,
                    1
                ),
                "language": self.language,
                "niche": self.niche
            }

        except Exception as e:

            logger.warning(
                f"⚠️ Story repair failed: {e}"
            )

            return None

    # =========================================================
    # FINAL RESULT NORMALIZER
    # =========================================================

    def _finalize_result(
        self,
        result: Dict[str, Any],
        topic: str,
        duration_minutes: int
    ) -> Dict[str, Any]:

        if not isinstance(
            result,
            dict
        ):
            return self._fallback_story(
                topic,
                duration_minutes
            )

        scenes = result.get(
            "scenes",
            []
        )

        if not isinstance(
            scenes,
            list
        ):
            scenes = []

        scenes = self._normalize_scenes(
            scenes
        )

        script = self._clean_script(
            result.get(
                "script",
                ""
            )
        )

        if len(script.split()) < 250:

            script = self._build_script_from_scenes(
                scenes
            )

        if len(script.split()) < 250:

            return self._fallback_story(
                topic,
                duration_minutes
            )

        word_count = len(
            script.split()
        )

        return {
            "topic":
                topic,

            "title":
                self._safe_text(
                    result.get(
                        "title",
                        "Sofia Luxury Story"
                    )
                ),

            "genre":
                self._safe_text(
                    result.get(
                        "genre",
                        "Luxury Drama"
                    )
                ),

            "logline":
                self._safe_text(
                    result.get(
                        "logline",
                        ""
                    )
                ),

            "hook":
                self._safe_text(
                    result.get(
                        "hook",
                        ""
                    )
                ),

            "script":
                script,

            "scenes":
                scenes,

            "word_count":
                word_count,

            "estimated_duration_min":
                round(
                    word_count
                    / self.WORDS_PER_MINUTE,
                    1
                ),

            "language":
                self.language,

            "niche":
                self.niche
        }

    # =========================================================
    # FALLBACK STORY
    # =========================================================

    def _fallback_story(
        self,
        topic: str,
        duration_minutes: int
    ) -> Dict[str, Any]:

        title = "Sofia and the Hidden Empire"

        script = """
Sofia thought the invitation was simply another luxury event,
but the moment her black car stopped outside the hotel, she
knew something was wrong.

The entrance was glowing with golden light. Cameras flashed
across the red carpet, expensive cars lined the street, and
wealthy guests moved toward the ballroom as if nothing unusual
was happening.

Sofia stepped from the car and looked toward the upper floors.

One window was completely dark.

Her phone vibrated.

Do not go upstairs alone.

There was no name attached to the message.

Sofia entered the ballroom anyway.

Crystal chandeliers covered the ceiling. A string orchestra
played softly while guests celebrated around her. Yet Sofia
could not shake the feeling that someone was watching.

Then she saw him.

A man standing near the private elevators was staring directly
at her.

Before Sofia could reach him, he disappeared through a side
door.

She followed.

The corridor was empty.

Then she noticed something strange.

A painting on the wall had been moved.

Behind it was a small metal panel.

Sofia touched the scanner.

The wall opened.

An elevator waited behind it.

There was no button for the basement.

Sofia stepped inside.

The doors closed.

When they opened again, she found herself beneath the hotel
inside a secret facility filled with enormous screens.

Maps covered one wall.

Photographs covered another.

Luxury hotels, private islands, yachts, aircraft and estates
appeared on dozens of screens.

Then Sofia stopped.

Her own photograph was displayed in the center.

Underneath it was her full name.

A voice came from behind her.

“You finally found it.”

Sofia turned.

The mysterious man stood in the doorway.

She demanded to know who he was.

He told her the hotel was only one part of a hidden empire
that had controlled powerful businesses for decades.

Sofia stared at the screens.

Then she noticed something that frightened her even more.

Her family name appeared beside the organization's symbol.

“You knew about my family?”

The man shook his head.

“Your family created it.”

Sofia could barely speak.

Everything she believed about her family's wealth had suddenly
changed.

The private jets, the estates, the companies and the fortune
were not the beginning of the story.

They were the cover.

Before Sofia could ask another question, every light in the
facility went black.

An alarm exploded through the underground rooms.

The man grabbed a security card.

“They found us.”

Sofia heard footsteps approaching from the corridor.

She refused to hide.

Instead, she grabbed the access card and ran toward the private
garage.

A black supercar waited behind the security doors.

Sofia opened the driver's door and started the engine.

The garage gates opened.

She accelerated into the city.

Behind her, black vehicles emerged from the underground
entrance.

Sofia drove through the illuminated streets, trying to understand
what had happened.

Then her phone rang.

She looked at the screen.

The caller ID showed her own number.

Sofia answered.

For several seconds, nobody spoke.

Then a woman's voice whispered,

“You should never have opened that door.”

The call ended.

Sofia slowed the car.

She looked at the city through the windshield.

For the first time that night, she understood the truth.

Someone had been protecting the secret.

Someone had been hiding the empire.

And someone had been waiting for Sofia to discover it.

She turned the steering wheel.

The car changed direction.

She was not running anymore.

She was going back.

Because now Sofia knew the secret existed.

And she intended to find out who had built the empire,
who had betrayed her family, and why they had chosen her.

The city disappeared behind her as she drove toward the
darkest part of the night.

Sofia had entered the hidden world by accident.

But she would return to it by choice.
"""

        script = self._clean_script(
            script
        )

        scenes = [
            {
                "scene_number": 1,
                "scene_purpose": "Hook and mystery",
                "location": "Ultra-luxury hotel entrance",
                "time": "Night",
                "duration_hint": "short",
                "shot_type": "wide cinematic establishing shot",
                "sofia_visible": True,
                "sofia_appearance": "Sofia with a consistent recognizable face, elegant evening fashion.",
                "action": "Sofia steps from a black luxury car and notices a dark window high above the hotel.",
                "emotion": "Confident but uneasy",
                "continuity": "The strange invitation begins the mystery.",
                "luxury_detail": "Golden hotel entrance, black luxury car, red carpet and wealthy guests.",
                "visual_prompt": "Wide cinematic establishing shot of Sofia clearly visible stepping from a black luxury car outside an ultra-luxury hotel at night, golden architectural lighting, elegant red carpet, wealthy guests, sophisticated evening fashion, Sofia looking toward a mysterious dark upper-floor window, photorealistic face, premium cinematic movie lighting.",
                "dialogue": "",
                "narration": "Sofia thought the invitation was simply another luxury event, but the moment her black car stopped outside the hotel, she knew something was wrong."
            },
            {
                "scene_number": 2,
                "scene_purpose": "Establish Sofia's world and introduce the watcher",
                "location": "Luxury hotel ballroom",
                "time": "Night",
                "duration_hint": "medium",
                "shot_type": "medium character shot",
                "sofia_visible": True,
                "sofia_appearance": "Same Sofia and same recognizable facial identity, elegant evening outfit.",
                "action": "Sofia studies the ballroom and notices a mysterious man near the private elevators.",
                "emotion": "Suspicious and alert",
                "continuity": "The mysterious man leads Sofia toward the hidden corridor.",
                "luxury_detail": "Crystal chandeliers, orchestra, luxury tables and elegant guests.",
                "visual_prompt": "Medium cinematic character shot of Sofia clearly visible inside an extravagant billionaire ballroom, crystal chandeliers, elegant guests, orchestra, luxury tables, Sofia watching a mysterious man near private elevators, warm cinematic lighting, realistic facial expression, premium movie aesthetic.",
                "dialogue": "",
                "narration": "Crystal chandeliers covered the ceiling, yet Sofia could not shake the feeling that someone was watching."
            },
            {
                "scene_number": 3,
                "scene_purpose": "Discover the hidden entrance",
                "location": "Secret corridor behind the ballroom",
                "time": "Night",
                "duration_hint": "medium",
                "shot_type": "close-up",
                "sofia_visible": True,
                "sofia_appearance": "Same Sofia with consistent facial identity and evening clothing.",
                "action": "Sofia discovers a hidden scanner behind an ornate painting and activates it.",
                "emotion": "Curious and shocked",
                "continuity": "The scanner opens a hidden elevator.",
                "luxury_detail": "Ornate artwork, polished marble and concealed technology.",
                "visual_prompt": "Cinematic close-up of Sofia clearly visible beside an ornate luxury painting, placing her hand against a hidden biometric scanner, shocked curious expression, polished marble corridor, concealed technology glowing beside her, dramatic realistic lighting, detailed premium movie production.",
                "dialogue": "",
                "narration": "Behind the painting was a small metal panel. Sofia touched the scanner, and the wall opened."
            },
            {
                "scene_number": 4,
                "scene_purpose": "Reveal the secret facility",
                "location": "Underground secret control facility",
                "time": "Night",
                "duration_hint": "medium",
                "shot_type": "over-the-shoulder",
                "sofia_visible": True,
                "sofia_appearance": "Same Sofia, same evening outfit and recognizable face.",
                "action": "Sofia stares at a massive screen displaying her photograph and family name.",
                "emotion": "Fear and disbelief",
                "continuity": "Sofia learns her family is connected to the hidden empire.",
                "luxury_detail": "Advanced control screens, global property maps and secret technology.",
                "visual_prompt": "Over-the-shoulder cinematic composition with Sofia clearly visible in the foreground staring at a massive futuristic screen displaying her photograph and family name, underground billionaire control facility, glowing global maps, sophisticated technology, dramatic blue lighting, tense realistic atmosphere.",
                "dialogue": "\"Why is my name here?\"",
                "narration": "Then Sofia stopped. Her own photograph was displayed in the center of the secret facility."
            },
            {
                "scene_number": 5,
                "scene_purpose": "Major twist",
                "location": "Secret control room",
                "time": "Night",
                "duration_hint": "medium",
                "shot_type": "emotional reaction close-up",
                "sofia_visible": True,
                "sofia_appearance": "Same Sofia with consistent facial identity.",
                "action": "Sofia realizes her family created the hidden empire.",
                "emotion": "Deep shock",
                "continuity": "The revelation changes everything Sofia believed about her wealth.",
                "luxury_detail": "Global maps, private aircraft records and luxury property networks.",
                "visual_prompt": "Emotional cinematic close-up of Sofia clearly visible reacting in disbelief inside a secret billionaire control room, glowing global maps and luxury property records behind her, realistic expressive eyes, dramatic lighting, sophisticated technology, premium movie aesthetic.",
                "dialogue": "\"My family created this?\"",
                "narration": "Everything Sofia believed about her family's wealth suddenly changed."
            },
            {
                "scene_number": 6,
                "scene_purpose": "Decision and escape",
                "location": "Secret underground luxury garage",
                "time": "Night",
                "duration_hint": "short",
                "shot_type": "dynamic cinematic shot",
                "sofia_visible": True,
                "sofia_appearance": "Same Sofia, consistent face and evening outfit.",
                "action": "Sofia grabs an access card, runs through the garage and starts a black supercar.",
                "emotion": "Determined and urgent",
                "continuity": "Sofia chooses to escape rather than remain hidden.",
                "luxury_detail": "Private underground garage and high-performance black supercar.",
                "visual_prompt": "Dynamic cinematic shot of Sofia clearly visible running through a secret underground luxury garage toward a black supercar, access card in her hand, determined expression, dramatic overhead lights, polished floors, urgent action, photorealistic premium action movie style.",
                "dialogue": "\"I'm not hiding.\"",
                "narration": "Sofia refused to hide. She grabbed the access card and ran toward the private garage."
            },
            {
                "scene_number": 7,
                "scene_purpose": "Climax",
                "location": "Illuminated city highway",
                "time": "Night",
                "duration_hint": "short",
                "shot_type": "low-angle dramatic shot",
                "sofia_visible": True,
                "sofia_appearance": "Same Sofia with consistent recognizable facial identity.",
                "action": "Sofia drives through the city while receiving a call from her own number.",
                "emotion": "Focused and fearless",
                "continuity": "The mysterious call confirms that someone is still watching her.",
                "luxury_detail": "Black supercar, illuminated skyscrapers and reflections across the windshield.",
                "visual_prompt": "Low-angle dramatic cinematic view of Sofia clearly visible driving a black luxury supercar through a spectacular city at night, illuminated skyscrapers reflected across the windshield, Sofia focused and fearless, phone glowing beside her, realistic facial identity, intense premium movie lighting.",
                "dialogue": "\"Who are you?\"",
                "narration": "Then her phone rang. The caller ID showed her own number."
            },
            {
                "scene_number": 8,
                "scene_purpose": "Resolution and cliffhanger",
                "location": "Luxury city overlook",
                "time": "Late night",
                "duration_hint": "medium",
                "shot_type": "beautiful final cinematic shot",
                "sofia_visible": True,
                "sofia_appearance": "Same Sofia, elegant and confident with the same recognizable facial identity.",
                "action": "Sofia turns the supercar around and heads back toward the hidden empire.",
                "emotion": "Calm determination",
                "continuity": "Sofia chooses to return and uncover the truth.",
                "luxury_detail": "Black supercar overlooking a glowing city skyline.",
                "visual_prompt": "Beautiful final cinematic shot of Sofia clearly visible beside her black luxury car overlooking a breathtaking city skyline at night, calm determined expression, elegant fashion, glowing skyscrapers, premium luxury atmosphere, realistic face, dramatic cinematic lighting, memorable movie ending.",
                "dialogue": "\"I'm going back.\"",
                "narration": "Sofia had entered the hidden world by accident. But she would return to it by choice."
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
                "Sofia enters an exclusive luxury hotel "
                "and discovers someone has been waiting for her."
            ),
            "script": script,
            "scenes": scenes,
            "word_count": word_count,
            "estimated_duration_min": round(
                word_count
                / self.WORDS_PER_MINUTE,
                1
            ),
            "language": self.language,
            "niche": self.niche
        }

    # =========================================================
    # MULTIPLE STORIES
    # =========================================================

    def generate_multiple(
        self,
        topics: List[Any],
        count: int = 3
    ) -> List[Dict[str, Any]]:

        stories = []

        for topic in topics[:count]:

            try:

                story = self.generate_script(
                    topic,
                    duration_minutes=5
                )

                if (
                    story
                    and not story.get("error")
                ):
                    stories.append(
                        story
                    )

            except Exception as e:

                logger.warning(
                    f"⚠️ Failed to create story "
                    f"for topic: {e}"
                )

        return stories


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    print("=" * 70)
    print("🎬 SOFIA LUXURY STORY GENERATOR TEST")
    print("=" * 70)

    generator = ScriptGenerator(
        language="english",
        niche="luxury_story"
    )

    test_topic = {
        "topic": (
            "Sofia discovers a secret hidden inside "
            "a billionaire's luxury empire"
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

        print("\n" + "-" * 70)

        print(
            result["script"][:3000]
        )

        print("\n" + "-" * 70)

        print(
            "\n✅ Cinematic Sofia story generated successfully."
        )

    else:

        print(
            f"\n❌ ERROR: "
            f"{result.get('error')}"
        )
