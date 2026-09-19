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
- 700-800 spoken words
- 8 major story scenes
- Detailed visual direction
- Sofia visible in every scene
- Different shot types
- Luxury environments
- Emotional progression
- Mid-story twist
- Climax
- Resolution or cliffhanger

The video renderer can use the scene information to
create a faster, more cinematic sequence.
"""

import os
import json
import re
from typing import Dict, List, Any

from loguru import logger

try:
    from groq import Groq
except ImportError:
    import groq
    Groq = groq.Groq

from dotenv import load_dotenv

load_dotenv()


class ScriptGenerator:

    MODEL = "openai/gpt-oss-120b"

    TARGET_WORDS_MIN = 700
    TARGET_WORDS_MAX = 800

    SCENE_COUNT = 8

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
                "GROQ_API_KEY is missing. Add it to your environment "
                "or GitHub Actions secrets."
            )

        self.client = Groq(api_key=api_key)

        logger.info(
            f"🎬 Sofia Luxury Story Generator initialized: "
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
            f"🎬 Creating cinematic Sofia story: "
            f"{topic_text[:120]}"
        )

        prompt = self._build_story_prompt(
            topic_text,
            duration_minutes
        )

        try:

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
                max_tokens=5000
            )

            raw = response.choices[0].message.content or ""

            result = self._parse_response(
                raw,
                topic_text,
                duration_minutes
            )

            logger.info(
                f"✅ Sofia cinematic story created: "
                f"{result.get('title', 'Untitled')} | "
                f"{result.get('word_count', 0)} words | "
                f"{len(result.get('scenes', []))} scenes"
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
                "script": "",
                "scenes": [],
                "word_count": 0,
                "estimated_duration_min": 0,
                "error": str(e)
            }

    # =========================================================
    # SYSTEM PROMPT
    # =========================================================

    def _system_prompt(self) -> str:

        return """
You are the head writer and visual story director for
SOFIA LUXURY STORY.

You create original vertical mini-movies.

Sofia is ALWAYS the protagonist.

She is not a presenter.
She is not a narrator standing outside the story.
She is the person living through the story.

Every story must feel like a real short movie.

IMPORTANT STORY RULES:

1. Sofia must be central in EVERY scene.

2. Sofia must perform meaningful actions.

3. Sofia must have a clear goal.

4. Give Sofia something to lose.

5. Give Sofia something to discover.

6. Give Sofia a difficult decision.

7. The story must progress naturally.

8. Each scene must cause or lead to the next scene.

9. Never create eight unrelated luxury pictures.

10. Never make the story feel like a lecture.

11. Never repeatedly describe Sofia simply standing,
smiling, looking beautiful, or walking.

12. Sofia should interact with objects, locations,
vehicles, technology and other characters.

13. Keep Sofia visually recognizable as the same woman.

14. Her clothing may change when the story requires it,
but her facial identity must remain consistent.

15. Use realistic emotional progression.

16. Include a strong opening hook.

17. Include escalating tension.

18. Include a meaningful twist.

19. Include a strong climax.

20. Finish with emotional payoff or a compelling cliffhanger.

VISUAL RULES:

Every scene must contain a strong visual idea.

Use a mixture of:

- wide shot
- medium shot
- close-up
- extreme close-up
- over-the-shoulder
- side profile
- low angle
- high angle
- point of view
- environmental detail

Do not use the same shot type repeatedly.

Sofia should be visible in most frames.

Luxury environments should feel believable and detailed.

Use cinematic lighting, realistic environments,
rich textures and natural human expressions.

Avoid generic AI-looking descriptions.

Every visual prompt must describe:
- Sofia
- her action
- her emotion
- the environment
- lighting
- camera framing
- important story objects

STORY CONTINUITY:

If Sofia enters a hotel in scene 2,
scene 3 must logically continue inside or immediately
after that hotel.

If Sofia has a black dress and evening setting,
do not randomly change her into casual daytime clothes
without a story reason.

If Sofia discovers an object, that object can return later.

If another character appears, give that character a
consistent role.

DIALOGUE:

Use short natural dialogue.

Dialogue should sound like real people.

Avoid long speeches.

NARRATION:

Narration should advance the story.

Do not repeat what the viewer can already see.

Do not write:
"Here we can see Sofia standing in a hotel."

Instead write something that advances the story.

The audience should always have a reason to keep watching.

Do not include:

[pause]
[music]
[sound effect]
[camera]
[zoom]
[cut]
[scene]
or other production instructions inside spoken text.

Do not include channel introductions.

Do not say:
"Welcome back to my channel."

The first sentence should create curiosity.

The story must be ORIGINAL.

Do not copy movies, books, dramas or existing social-media stories.
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
Create an ORIGINAL SOFIA LUXURY STORY based on:

{topic}

TARGET:
Approximately {duration} minutes.

SPOKEN WORD COUNT:
700-800 words.

FORMAT:
Vertical 9:16 cinematic mini-movie.

NUMBER OF MAJOR SCENES:
Exactly {self.SCENE_COUNT}.

The eight scenes must form ONE continuous story.

=========================================================
STORY STRUCTURE
=========================================================

SCENE 1 — HOOK

Start immediately with something unusual,
dangerous, beautiful or mysterious.

Sofia must be visible.

The viewer should immediately ask:

"What is happening?"

=========================================================

SCENE 2 — SETUP

Show Sofia's luxurious world.

Establish what Sofia wants
and why it matters.

Give the audience a reason to care about her.

=========================================================

SCENE 3 — PROBLEM

Something unexpected happens.

Sofia must react.

The problem must directly affect her.

=========================================================

SCENE 4 — ESCALATION

Sofia investigates, escapes, follows someone,
discovers something, travels somewhere,
or takes action.

The story should become more intense.

=========================================================

SCENE 5 — TWIST

Reveal something that changes the meaning
of what happened earlier.

The twist must connect to previous scenes.

=========================================================

SCENE 6 — DECISION

Sofia must make a difficult choice.

Do not let another character solve the story for her.

Sofia drives the action.

=========================================================

SCENE 7 — CLIMAX

Sofia confronts the main problem.

This should be the most emotionally powerful
part of the story.

=========================================================

SCENE 8 — ENDING

Give the audience:

- emotional payoff,
OR
- a beautiful final moment,
OR
- a powerful reveal,
OR
- a strong cliffhanger.

End with a memorable Sofia moment.

=========================================================
LUXURY VISUAL WORLD
=========================================================

Use luxury naturally when appropriate:

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
high-rise city views
private clubs
beautiful estates
futuristic architecture
exclusive events

But luxury must support the story.

Do not simply list expensive objects.

=========================================================
SOFIA VISUAL CONTINUITY
=========================================================

Sofia is the same recognizable woman throughout the story.

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
- visual atmosphere

=========================================================
SHOT DESIGN
=========================================================

Each scene must have a different primary shot type.

Use this progression where appropriate:

1. wide cinematic establishing shot
2. medium character shot
3. close-up
4. over-the-shoulder
5. low-angle or tracking-style composition
6. close-up reaction
7. dynamic dramatic shot
8. beautiful final wide/close shot

The shot type is descriptive information for the image generator.
Do not put camera instructions inside the spoken narration.

=========================================================
PACING
=========================================================

Do NOT make every scene feel equally slow.

Scenes containing:
- danger
- discovery
- confrontation
- escape
- surprise

should have energetic visual descriptions.

Quiet emotional scenes can breathe slightly longer.

=========================================================
DIALOGUE
=========================================================

Use short dialogue.

Example style:

"I knew you would come."

Sofia looked at him.

"Then you already know why I'm here."

Do not make dialogue sound theatrical or artificial.

=========================================================
OUTPUT
=========================================================

Return ONLY valid JSON.

Use exactly:

{{
  "title": "Original title",
  "genre": "Genre",
  "logline": "One sentence",
  "hook": "Opening hook",
  "scenes": [
    {{
      "scene_number": 1,
      "scene_purpose": "What this scene accomplishes",
      "location": "Specific location",
      "time": "Time of day",
      "duration_hint": "short",
      "shot_type": "wide",
      "sofia_visible": true,
      "sofia_appearance": "Consistent description of Sofia",
      "action": "What Sofia is doing",
      "emotion": "Her emotional state",
      "continuity": "Connection to previous/next scene",
      "luxury_detail": "Important luxury/environment detail",
      "visual_prompt": "Detailed cinematic image prompt",
      "dialogue": "Short natural dialogue",
      "narration": "Narration for this scene"
    }}
  ],
  "script": "Complete spoken story"
}}

RULES:

- Exactly 8 scenes.
- Sofia visible in every scene.
- Approximately 700-800 words.
- One connected story.
- No markdown.
- No commentary outside JSON.
"""

    # =========================================================
    # TOPIC NORMALIZER
    # =========================================================

    def _normalize_topic(self, topic: Any) -> str:

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

        return value or "Sofia Luxury Story"

    # =========================================================
    # RESPONSE PARSER
    # =========================================================

    def _parse_response(
        self,
        raw: str,
        topic: str,
        duration_minutes: int
    ) -> Dict[str, Any]:

        cleaned = raw.strip()

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

        try:

            data = json.loads(cleaned)

        except json.JSONDecodeError:

            start = cleaned.find("{")
            end = cleaned.rfind("}")

            if start >= 0 and end > start:

                try:

                    data = json.loads(
                        cleaned[start:end + 1]
                    )

                except json.JSONDecodeError:

                    data = None

        if not isinstance(data, dict):

            logger.warning(
                "⚠️ Invalid JSON returned. "
                "Using fallback story."
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

        script = self._clean_script(
            str(
                data.get(
                    "script",
                    ""
                )
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

        # -----------------------------------------------------
        # Build spoken script from scenes if necessary.
        # -----------------------------------------------------

        if len(script.split()) < 100:

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
                    parts.append(narration)

                if dialogue:
                    parts.append(dialogue)

            script = "\n\n".join(parts)

        # -----------------------------------------------------
        # Final fallback.
        # -----------------------------------------------------

        if len(script.split()) < 100:

            return self._fallback_story(
                topic,
                duration_minutes
            )

        word_count = len(
            script.split()
        )

        estimated_duration = (
            word_count / 150.0
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
                estimated_duration,
                1
            ),
            "language": self.language,
            "niche": self.niche
        }

    # =========================================================
    # SCENE NORMALIZER
    # =========================================================

    def _normalize_scenes(
        self,
        scenes: List[Any]
    ) -> List[Dict[str, Any]]:

        normalized = []

        shot_types = [
            "wide",
            "medium",
            "close-up",
            "over-the-shoulder",
            "low-angle",
            "reaction close-up",
            "dynamic dramatic",
            "final cinematic"
        ]

        for index, scene in enumerate(
            scenes[:self.SCENE_COUNT]
        ):

            if not isinstance(scene, dict):
                continue

            number = index + 1

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
                        "Night"
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
                        "Sofia, consistent recognizable appearance"
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

                "visual_prompt": str(
                    scene.get(
                        "visual_prompt",
                        ""
                    )
                ).strip(),

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

            # Make sure the image prompt explicitly
            # tells the image generator that Sofia must
            # be the visible protagonist.
            if "Sofia" not in normalized_scene[
                "visual_prompt"
            ]:

                normalized_scene[
                    "visual_prompt"
                ] = (
                    "Sofia is clearly visible as the central "
                    "character. "
                    + normalized_scene["visual_prompt"]
                )

            normalized.append(
                normalized_scene
            )

        # If the AI returned fewer than 8 scenes,
        # duplicate the final valid scene only as a
        # structural fallback.
        while len(normalized) < self.SCENE_COUNT:

            if normalized:

                source = dict(
                    normalized[-1]
                )

                source[
                    "scene_number"
                ] = len(normalized) + 1

                source[
                    "scene_purpose"
                ] = (
                    "Continuation of Sofia's story."
                )

                normalized.append(
                    source
                )

            else:

                normalized.append({
                    "scene_number": len(normalized) + 1,
                    "scene_purpose": "Sofia's story.",
                    "location": "Luxury interior",
                    "time": "Night",
                    "duration_hint": "medium",
                    "shot_type": shot_types[
                        len(normalized)
                    ],
                    "sofia_visible": True,
                    "sofia_appearance": (
                        "Sofia, consistent recognizable "
                        "facial identity"
                    ),
                    "action": (
                        "Sofia moves forward with "
                        "determination."
                    ),
                    "emotion": "determined",
                    "continuity": "",
                    "luxury_detail": (
                        "Elegant luxury architecture."
                    ),
                    "visual_prompt": (
                        "Sofia clearly visible as the "
                        "central character in a cinematic "
                        "luxury environment."
                    ),
                    "dialogue": "",
                    "narration": (
                        "Sofia knew she could not "
                        "turn back."
                    )
                })

        return normalized[:self.SCENE_COUNT]

    # =========================================================
    # SCRIPT CLEANER
    # =========================================================

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
        ]

        cleaned = script

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
    # FALLBACK STORY
    # =========================================================

    def _fallback_story(
        self,
        topic: str,
        duration_minutes: int
    ) -> Dict[str, Any]:

        title = "Sofia and the Hidden Empire"

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

        script = self._clean_script(script)

        scenes = [
            {
                "scene_number": 1,
                "scene_purpose": "Hook",
                "location": "Ultra-luxury hotel entrance",
                "time": "Night",
                "duration_hint": "short",
                "shot_type": "wide",
                "sofia_visible": True,
                "sofia_appearance": "Elegant Sofia in a luxurious evening outfit.",
                "action": "Sofia steps from a black luxury car onto a golden-lit red carpet.",
                "emotion": "Confident but uneasy",
                "continuity": "Begins the mystery.",
                "luxury_detail": "Black luxury car, golden hotel entrance, photographers.",
                "visual_prompt": "Sofia clearly visible stepping from a black luxury car outside an ultra-luxury hotel at night, golden architectural lighting, elegant red carpet, cinematic wide composition, sophisticated evening fashion, realistic face, luxurious atmosphere.",
                "dialogue": "",
                "narration": "Sofia thought the invitation was simply another luxury event."
            },
            {
                "scene_number": 2,
                "scene_purpose": "Establish the world",
                "location": "Luxury ballroom",
                "time": "Night",
                "duration_hint": "medium",
                "shot_type": "medium",
                "sofia_visible": True,
                "sofia_appearance": "Same Sofia, same recognizable facial identity.",
                "action": "Sofia studies the guests while holding a glass.",
                "emotion": "Suspicious",
                "continuity": "She notices a mysterious man.",
                "luxury_detail": "Crystal chandeliers and elegant guests.",
                "visual_prompt": "Sofia clearly visible in an extravagant billionaire ballroom, crystal chandeliers, elegant guests, champagne glasses, Sofia looking suspiciously across the room, cinematic medium shot, rich warm lighting.",
                "dialogue": "",
                "narration": "Inside, everything looked perfect. But Sofia noticed one man watching her."
            },
            {
                "scene_number": 3,
                "scene_purpose": "Discovery",
                "location": "Hidden elevator",
                "time": "Night",
                "duration_hint": "medium",
                "shot_type": "close-up",
                "sofia_visible": True,
                "sofia_appearance": "Same Sofia.",
                "action": "Sofia places her hand against a hidden fingerprint scanner.",
                "emotion": "Shocked curiosity",
                "continuity": "The hidden elevator leads underground.",
                "luxury_detail": "Ornate painting and secret mechanism.",
                "visual_prompt": "Close-up of Sofia placing her hand against a mysterious fingerprint scanner hidden behind an ornate luxury hotel painting, her shocked expression visible, dramatic cinematic lighting.",
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
                "luxury_detail": "Advanced screens and hidden control room.",
                "visual_prompt": "Over-the-shoulder cinematic shot with Sofia clearly visible in the foreground staring at a huge futuristic screen displaying her name, secret underground luxury facility, dramatic blue lighting, tense atmosphere.",
                "dialogue": "\"Why me?\"",
                "narration": "Then Sofia saw her own name on the main screen."
            },
            {
                "scene_number": 5,
                "scene_purpose": "Twist",
                "location": "Secret control room",
                "time": "Night",
                "duration_hint": "medium",
                "shot_type": "reaction close-up",
                "sofia_visible": True,
                "sofia_appearance": "Same Sofia.",
                "action": "Sofia realizes her family built the hidden empire.",
                "emotion": "Shock",
                "continuity": "The revelation changes everything she believed.",
                "luxury_detail": "Global property maps and sophisticated control systems.",
                "visual_prompt": "Cinematic close-up of Sofia reacting in disbelief inside a secret billionaire control room, glowing global maps behind her, sophisticated luxury technology, emotional realistic facial expression.",
                "dialogue": "\"My family built this?\"",
                "narration": "Everything Sofia believed about her family's wealth suddenly changed."
            },
            {
                "scene_number": 6,
                "scene_purpose": "Decision",
                "location": "Underground private garage",
                "time": "Night",
                "duration_hint": "short",
                "shot_type": "dynamic dramatic",
                "sofia_visible": True,
                "sofia_appearance": "Same Sofia.",
                "action": "Sofia runs toward a waiting black supercar.",
                "emotion": "Determined",
                "continuity": "She escapes the facility.",
                "luxury_detail": "Black supercar in a private underground garage.",
                "visual_prompt": "Sofia running toward a black luxury supercar inside a secret underground garage, dramatic lighting, determined expression, cinematic dynamic composition, luxurious architecture, sense of urgency.",
                "dialogue": "",
                "narration": "Sofia knew she had seconds to escape."
            },
            {
                "scene_number": 7,
                "scene_purpose": "Climax",
                "location": "Luxury city highway",
                "time": "Night",
                "duration_hint": "short",
                "shot_type": "low-angle",
                "sofia_visible": True,
                "sofia_appearance": "Same Sofia.",
                "action": "Sofia drives through the city while receiving a mysterious call.",
                "emotion": "Focused and fearless",
                "continuity": "The mysterious caller reveals that the danger is not over.",
                "luxury_detail": "Supercar, illuminated skyscrapers and city lights.",
                "visual_prompt": "Sofia clearly visible driving a black luxury supercar through a spectacular city at night, illuminated skyscrapers reflected on the windshield, intense focused expression, cinematic low-angle perspective.",
                "dialogue": "\"Who are you?\"",
                "narration": "Then her phone rang. The caller ID displayed her own number."
            },
            {
                "scene_number": 8,
                "scene_purpose": "Ending",
                "location": "City overlook",
                "time": "Night",
                "duration_hint": "medium",
                "shot_type": "final cinematic",
                "sofia_visible": True,
                "sofia_appearance": "Same Sofia, elegant and confident.",
                "action": "Sofia looks across the city and turns the car around.",
                "emotion": "Calm determination",
                "continuity": "She decides to return and confront the hidden empire.",
                "luxury_detail": "Luxury car overlooking a glowing city skyline.",
                "visual_prompt": "Beautiful cinematic final shot of Sofia standing beside her black luxury car overlooking a breathtaking city skyline at night, elegant fashion, calm determined expression, glowing skyscrapers, premium luxury movie aesthetic.",
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
                word_count / 150.0,
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

            story = self.generate_script(
                topic,
                duration_minutes=5
            )

            if story and not story.get("error"):
                stories.append(story)

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
            result["script"][:2000]
        )

        print("\n" + "-" * 70)

        print(
            "\n✅ Cinematic Sofia story generated."
        )

    else:

        print(
            f"\n❌ ERROR: "
            f"{result.get('error')}"
        )
