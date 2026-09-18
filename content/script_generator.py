"""
SOFIA LUXURY STORY
CINEMATIC 5-MINUTE STORY GENERATOR

Creates original short-drama stories where Sofia is always
the central character.

Designed for:
- Luxury drama
- Action
- Romance
- Mystery
- Fantasy
- Adventure
- Billionaire stories
- Time travel
- Royal stories
- Crime/thriller
- Supernatural stories

Target:
- Approximately 5 minutes
- 700-800 spoken words
- Strong opening hook
- Connected scenes
- Sofia appears throughout
- Cinematic storytelling
- Emotional progression
- Mid-story twist
- Strong climax
- Memorable ending/cliffhanger

Model:
Groq openai/gpt-oss-120b
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
    """
    Sofia Luxury Story cinematic story generator.
    """

    MODEL = "openai/gpt-oss-120b"

    TARGET_WORDS_MIN = 700
    TARGET_WORDS_MAX = 800

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
                "GROQ_API_KEY is missing. Add it to your environment or "
                "Streamlit/GitHub Actions secrets."
            )

        self.client = Groq(api_key=api_key)

        logger.info(
            f"🎬 Sofia Luxury Story Generator initialized: "
            f"{self.language}/{self.niche}"
        )

    # ---------------------------------------------------------
    # MAIN GENERATOR
    # ---------------------------------------------------------

    def generate_script(
        self,
        topic: Any,
        duration_minutes: int = 5
    ) -> Dict[str, Any]:

        topic_text = self._normalize_topic(topic)

        logger.info(
            f"🎬 Creating Sofia Luxury Story: {topic_text[:100]}"
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
                temperature=0.85,
                max_tokens=4500
            )

            raw = response.choices[0].message.content or ""

            result = self._parse_response(
                raw,
                topic_text,
                duration_minutes
            )

            logger.info(
                f"✅ Sofia story created: "
                f"{result.get('title', 'Untitled')} | "
                f"{result.get('word_count', 0)} words | "
                f"~{result.get('estimated_duration_min', 0)} min"
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

    # ---------------------------------------------------------
    # SYSTEM PROMPT
    # ---------------------------------------------------------

    def _system_prompt(self) -> str:

        return """
You are the head writer and cinematic story director for
SOFIA LUXURY STORY.

Your job is to create ORIGINAL five-minute vertical mini-movies.

Sofia is ALWAYS the central character.

Sofia must never become a background character.

Every story must make the audience care about Sofia,
wonder what happens next, and want to watch until the ending.

IMPORTANT:

1. Sofia must appear in the story from beginning to end.

2. Sofia must be the person who drives the important actions.

3. Never write a generic story where Sofia could be replaced
   by another character.

4. The story must have a clear beginning, escalation, climax,
   and ending.

5. Every scene must connect naturally to the previous scene.

6. Avoid random disconnected images.

7. Use cinematic visual descriptions that can later be converted
   into AI-generated images.

8. Make locations visually rich:
   luxury hotels, private jets, mansions, skyscrapers,
   yachts, exotic cities, royal palaces, private islands,
   underground clubs, futuristic cities, expensive restaurants,
   mysterious estates, etc.

9. Characters should have strong emotions:
   fear, confidence, suspicion, love, anger, determination,
   surprise, grief, relief, excitement.

10. Use twists carefully. The twist should change what the
    audience thinks is happening.

11. Build toward a strong climax.

12. End with either:
    - a satisfying emotional ending,
    - a powerful reveal,
    - or a cliffhanger for another Sofia story.

13. Do not copy existing movies, dramas, books, or NetShort stories.

14. Create ORIGINAL characters, situations, dialogue,
    locations, and plot events.

15. The final story should feel like a miniature movie,
    not a YouTube lecture.

16. Do NOT include:
    [pause]
    [music]
    [laughs]
    [sound effect]
    [camera]
    or other production instructions inside the spoken script.

17. Write natural spoken English.

18. The narration/dialogue should sound emotional and cinematic.

19. Do not waste words on introductions such as
    "Welcome back to my channel."

20. Start with something that makes the viewer immediately
    curious.

Sofia's identity must remain visually consistent:
same woman, same recognizable facial identity,
even when her clothes, hairstyle, location, or genre changes.

The result must be suitable for a vertical 9:16 short drama.
"""

    # ---------------------------------------------------------
    # STORY PROMPT
    # ---------------------------------------------------------

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

TARGET SPOKEN WORD COUNT:
700-800 words.

GENRE:
Choose the genre that best fits the idea.
It may be luxury action, romance, mystery, fantasy,
adventure, billionaire drama, time travel, royal drama,
crime thriller, supernatural drama, or a combination.

IMPORTANT:

This is NOT a normal YouTube information video.

It is a MINIATURE CINEMATIC MOVIE.

Sofia is the protagonist.

Create approximately 10-14 connected story beats.

STORY STRUCTURE:

ACT 1 — THE HOOK
Open with an intriguing or dangerous moment involving Sofia.

ACT 2 — THE WORLD
Show Sofia's luxurious or unusual world and establish
what she wants.

ACT 3 — THE PROBLEM
Something unexpected threatens Sofia or someone she cares about.

ACT 4 — ESCALATION
The danger or mystery becomes much bigger.

ACT 5 — THE TWIST
Reveal information that changes the audience's understanding
of what is happening.

ACT 6 — THE CLIMAX
Sofia must make an important decision or take decisive action.

ACT 7 — THE ENDING
Give the audience an emotional payoff or a powerful cliffhanger.

VISUAL STORYTELLING:

Every beat should give us a clear visual idea.

Examples:

- Sofia walking through a luxury hotel at night.
- Sofia stepping from a black luxury car.
- Sofia looking across a city from a penthouse.
- Sofia running through a rain-soaked street.
- Sofia discovering a hidden room.
- Sofia confronting an unknown enemy.
- Sofia aboard a private jet.
- Sofia standing on a yacht at sunset.
- Sofia entering an ancient palace.
- Sofia facing danger while remaining calm.

Do not simply list these examples.
Create a completely original story.

DIALOGUE:

Use short, natural dialogue when it makes the story stronger.

Do not turn the story into a wall of dialogue.

NARRATION:

Use cinematic narration to connect scenes.

OUTPUT FORMAT:

Return ONLY valid JSON.

Use exactly this structure:

{{
  "title": "Original Sofia story title",
  "genre": "Story genre",
  "logline": "One sentence describing the story",
  "hook": "The opening hook",
  "scenes": [
    {{
      "scene_number": 1,
      "location": "Specific visual location",
      "time": "Time of day",
      "action": "What Sofia is doing",
      "emotion": "Sofia's emotion",
      "visual_prompt": "Detailed cinematic visual description",
      "dialogue": "Optional short dialogue",
      "narration": "Narration for this scene"
    }}
  ],
  "script": "Complete spoken narration and dialogue for the entire story"
}}

The "script" must contain approximately 700-800 words.

The scenes must form ONE continuous story.

Sofia must be present or central in every scene.

Do not include markdown fences.

Do not add commentary outside the JSON.
"""

    # ---------------------------------------------------------
    # TOPIC NORMALIZER
    # ---------------------------------------------------------

    def _normalize_topic(self, topic: Any) -> str:

        if isinstance(topic, dict):

            value = (
                topic.get("topic")
                or topic.get("title")
                or topic.get("idea")
                or "Sofia Luxury Story"
            )

            return str(value).strip()

        if topic is None:
            return "Sofia discovers a dangerous secret inside a luxury empire."

        return str(topic).strip()

    # ---------------------------------------------------------
    # RESPONSE PARSER
    # ---------------------------------------------------------

    def _parse_response(
        self,
        raw: str,
        topic: str,
        duration_minutes: int
    ) -> Dict[str, Any]:

        cleaned = raw.strip()

        # Remove accidental markdown fences.
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

        # First attempt: direct JSON.
        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError:

            # Second attempt: find JSON object.
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
                "⚠️ Model returned invalid JSON. "
                "Using safe fallback story."
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

        script = str(
            data.get(
                "script",
                ""
            )
        ).strip()

        scenes = data.get("scenes", [])

        if not isinstance(scenes, list):
            scenes = []

        script = self._clean_script(script)

        # If the model somehow returned an empty script,
        # construct one from the scene narration.
        if len(script.split()) < 100:

            scene_parts = []

            for scene in scenes:

                if not isinstance(scene, dict):
                    continue

                narration = str(
                    scene.get("narration", "")
                ).strip()

                dialogue = str(
                    scene.get("dialogue", "")
                ).strip()

                if narration:
                    scene_parts.append(narration)

                if dialogue:
                    scene_parts.append(dialogue)

            script = "\n\n".join(scene_parts)

        # Final safety fallback.
        if len(script.split()) < 100:

            fallback = self._fallback_story(
                topic,
                duration_minutes
            )

            return fallback

        word_count = len(script.split())

        estimated_duration = word_count / 150.0

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

    # ---------------------------------------------------------
    # SCRIPT CLEANER
    # ---------------------------------------------------------

    def _clean_script(self, script: str) -> str:

        if not script:
            return ""

        # Remove production directions that should never
        # be spoken by the voice generator.
        patterns = [
            r"\[pause\]",
            r"\[music\]",
            r"\[laughs?\]",
            r"\[chuckles?\]",
            r"\[sound effect[s]?\]",
            r"\[sfx\]",
            r"\[camera[^\]]*\]",
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

        # Remove obvious JSON artifacts if they accidentally
        # appear inside the spoken script.
        cleaned = cleaned.replace(
            "\\n",
            "\n"
        )

        # Normalize excessive whitespace.
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

    # ---------------------------------------------------------
    # FALLBACK STORY
    # ---------------------------------------------------------

    def _fallback_story(
        self,
        topic: str,
        duration_minutes: int
    ) -> Dict[str, Any]:

        title = "Sofia and the Secret Empire"

        script = """
Sofia thought the invitation was simply another luxury event.

The black car stopped beneath the golden lights of the most
exclusive hotel in the city. Cameras flashed as Sofia stepped
onto the red carpet, wearing a calm expression that made everyone
turn to look.

But she had no idea why she had been invited.

Inside the hotel, everything looked perfect. Crystal chandeliers.
Private elevators. Guards standing silently beside doors that
ordinary guests were never allowed to enter.

Then Sofia received a message.

Do not trust anyone in this building.

She looked around the ballroom.

Hundreds of people were laughing and celebrating, but suddenly
Sofia noticed something strange. One of the guests was watching
her from across the room.

The man disappeared before she could reach him.

Sofia followed.

She passed through a private corridor and discovered an elevator
hidden behind a painting. There was no button for the basement.

Instead, there was a fingerprint scanner.

Sofia placed her hand against it.

The doors opened.

Beneath the luxury hotel was an enormous secret facility.

Screens covered the walls. Maps showed private islands, banks,
airports, and companies across the world.

Then Sofia saw her own name.

She stepped closer.

A voice came from behind her.

“You were never invited here by accident.”

Sofia turned.

The stranger from the ballroom was standing in the doorway.

He told her that the hotel belonged to a secret organization
that had controlled powerful businesses for decades.

And now someone inside the organization wanted Sofia dead.

Sofia did not run.

She asked one question.

“Why me?”

The stranger looked at the screen behind her.

“Because your family built this empire.”

Sofia froze.

She had spent her entire life believing her family had simply
been wealthy.

Now she discovered that there was an entire world hidden behind
the luxury she knew.

Suddenly the lights went out.

An alarm began to scream.

The stranger grabbed Sofia's hand.

“They found us.”

Security doors slammed shut throughout the facility.

Sofia ran through the underground corridors as footsteps
approached from behind.

She reached a private garage.

A black car was waiting.

She jumped inside and drove into the night.

But the danger was not over.

Her phone suddenly rang.

It was her own number.

Sofia answered.

A woman's voice whispered,

“You should never have opened that door.”

Then the call ended.

Sofia looked at the road ahead.

For the first time that night, she smiled.

Because now she knew something the people chasing her did not.

They had made one mistake.

They had taught Sofia exactly where their empire was hiding.

And Sofia was coming back for it.
"""

        script = self._clean_script(script)

        scenes = [
            {
                "scene_number": 1,
                "location": "Luxury hotel entrance",
                "time": "Night",
                "action": "Sofia arrives at an exclusive event.",
                "emotion": "Confident but curious",
                "visual_prompt": (
                    "Sofia arriving at an ultra-luxury hotel at night, "
                    "black luxury car, golden lights, cinematic atmosphere"
                ),
                "narration": "Sofia thought the invitation was simply another luxury event."
            },
            {
                "scene_number": 2,
                "location": "Luxury ballroom",
                "time": "Night",
                "action": "Sofia notices someone watching her.",
                "emotion": "Suspicious",
                "visual_prompt": (
                    "Sofia inside an elegant billionaire ballroom, "
                    "crystal chandeliers, guests in formal clothing, "
                    "mysterious man watching from distance"
                ),
                "narration": "Inside the hotel, everything looked perfect."
            },
            {
                "scene_number": 3,
                "location": "Secret elevator",
                "time": "Night",
                "action": "Sofia discovers a hidden elevator.",
                "emotion": "Intrigued",
                "visual_prompt": (
                    "Sofia discovering a hidden elevator behind an ornate "
                    "painting inside a luxury hotel"
                ),
                "narration": "Sofia followed the stranger and discovered something impossible."
            }
        ]

        word_count = len(script.split())

        return {
            "topic": topic,
            "title": title,
            "genre": "Luxury Mystery Action",
            "logline": (
                "Sofia discovers that her family's luxury empire "
                "hides a dangerous secret."
            ),
            "hook": (
                "Sofia enters a luxury hotel and discovers "
                "someone has been waiting for her."
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

    # ---------------------------------------------------------
    # MULTIPLE STORIES
    # ---------------------------------------------------------

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


# ---------------------------------------------------------
# TEST
# ---------------------------------------------------------

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

        print(f"\n🎬 TITLE: {result.get('title')}")
        print(f"🎭 GENRE: {result.get('genre')}")
        print(f"📝 WORDS: {result.get('word_count')}")
        print(
            f"⏱️ ESTIMATED LENGTH: "
            f"{result.get('estimated_duration_min')} minutes"
        )

        print("\n" + "-" * 70)
        print(result["script"][:2000])
        print("\n" + "-" * 70)

        print(
            f"\n✅ Scenes generated: "
            f"{len(result.get('scenes', []))}"
        )

    else:

        print(
            f"\n❌ ERROR: "
            f"{result.get('error')}"
        )
