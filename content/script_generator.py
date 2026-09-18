"""
✍️ SOFIA LUXURY AI SCRIPT GENERATOR

Sofia is the central AI storyteller and creative personality
behind Sofia Luxury.

Creates approximately 5-minute Sofia Luxury Story scripts
for luxury, technology, fashion, travel, cars, lifestyle,
adventure, action, drama and other interesting topics.

Supports: English, Urdu, Hindi, Punjabi
"""

import os
from typing import Dict, List

from loguru import logger

try:
    from groq import Groq
except ImportError:
    import groq
    Groq = groq.Groq

from dotenv import load_dotenv

load_dotenv()


class ScriptGenerator:
    """Generate approximately 5-minute Sofia Luxury Stories."""

    # ---------------------------------------------------------
    # STORY SETTINGS
    # ---------------------------------------------------------

    TARGET_WORDS_MIN = 700
    TARGET_WORDS_MAX = 800
    WORDS_PER_MINUTE = 150

    def __init__(
        self,
        language: str = "english",
        niche: str = "luxury"
    ):
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError(
                "GROQ_API_KEY is not configured."
            )

        self.client = Groq(api_key=api_key)

        self.language = language.lower()
        self.niche = niche.lower()

        self.style_guides = {
            "english": {
                "tone": (
                    "elegant, confident, warm, intelligent "
                    "and conversational luxury storyteller"
                ),
                "rules": (
                    "Use natural conversational English. "
                    "Use contractions where appropriate. "
                    "Keep sentences easy to speak aloud. "
                    "Avoid robotic, repetitive or overly formal language."
                )
            },

            "urdu": {
                "tone": (
                    "warm, elegant and engaging luxury storyteller"
                ),
                "rules": (
                    "Use natural Roman Urdu with occasional Urdu words. "
                    "Keep the language easy to understand and natural "
                    "for spoken narration."
                )
            },

            "hindi": {
                "tone": (
                    "modern, warm, elegant and engaging storyteller"
                ),
                "rules": (
                    "Use natural Hindi or Hinglish where appropriate. "
                    "Keep the narration conversational and easy to speak."
                )
            },

            "punjabi": {
                "tone": (
                    "warm, modern, elegant and engaging storyteller"
                ),
                "rules": (
                    "Use natural Roman Punjabi with English where appropriate. "
                    "Keep the narration conversational and easy to speak."
                )
            }
        }


    # =========================================================
    # GENERATE SCRIPT
    # =========================================================

    def generate_script(
        self,
        topic: Dict,
        duration_minutes: int = 5
    ) -> Dict:

        # -----------------------------------------------------
        # SAFETY / DEFAULTS
        # -----------------------------------------------------

        if not isinstance(topic, dict):
            topic = {
                "topic": str(topic)
            }

        topic_text = str(
            topic.get(
                "topic",
                "The latest luxury and technology trends"
            )
        ).strip()

        if not topic_text:
            topic_text = (
                "The latest luxury and technology trends"
            )

        duration_minutes = max(
            1,
            int(duration_minutes)
        )

        # For Sofia Luxury Story, approximately 5 minutes
        # means roughly 700–800 spoken words.
        if duration_minutes == 5:
            target_min = self.TARGET_WORDS_MIN
            target_max = self.TARGET_WORDS_MAX
        else:
            target_min = max(
                150,
                int(duration_minutes * 140)
            )

            target_max = max(
                target_min + 50,
                int(duration_minutes * 160)
            )

        style = self.style_guides.get(
            self.language,
            self.style_guides["english"]
        )

        logger.info(
            f"✍️ Generating {duration_minutes}-minute "
            f"Sofia Luxury Story"
        )

        logger.info(
            f"🎯 Target: {target_min}-{target_max} words"
        )

        prompt = self._build_prompt(
            topic=topic,
            style=style,
            duration=duration_minutes,
            target_min=target_min,
            target_max=target_max
        )

        # -----------------------------------------------------
        # GROQ
        # -----------------------------------------------------

        try:

            response = self.client.chat.completions.create(
                model="openai/gpt-oss-120b",

                messages=[
                    {
                        "role": "system",
                        "content": self._system_prompt(
                            style=style,
                            duration=duration_minutes,
                            target_min=target_min,
                            target_max=target_max
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],

                temperature=0.85,

                max_tokens=3000
            )

            script_text = (
                response.choices[0]
                .message
                .content
                .strip()
            )

            # -------------------------------------------------
            # CLEAN OUTPUT
            # -------------------------------------------------

            script_text = self._clean_script(
                script_text
            )

            word_count = len(
                script_text.split()
            )

            estimated_duration = (
                word_count /
                self.WORDS_PER_MINUTE
            )

            result = {
                "topic": topic_text,
                "script": script_text,
                "word_count": word_count,
                "estimated_duration_min": round(
                    estimated_duration,
                    1
                ),
                "target_duration_min": duration_minutes,
                "target_words": (
                    f"{target_min}-{target_max}"
                ),
                "language": self.language,
                "niche": self.niche,
                "source_trend": topic.get(
                    "source",
                    "Unknown"
                ),
                "timestamp": topic.get(
                    "timestamp",
                    ""
                )
            }

            logger.info(
                f"✅ Sofia script generated: "
                f"{word_count} words, "
                f"~{estimated_duration:.1f} minutes"
            )

            # -------------------------------------------------
            # WORD COUNT NOTICE
            # -------------------------------------------------

            if word_count < target_min:

                logger.warning(
                    f"⚠️ Script is shorter than target: "
                    f"{word_count} words"
                )

            elif word_count > target_max:

                logger.warning(
                    f"⚠️ Script is longer than target: "
                    f"{word_count} words"
                )

            return result

        except Exception as e:

            logger.error(
                f"❌ Script generation failed: {e}"
            )

            return {
                "topic": topic_text,
                "script": "",
                "word_count": 0,
                "estimated_duration_min": 0,
                "target_duration_min": duration_minutes,
                "language": self.language,
                "niche": self.niche,
                "error": str(e)
            }


    # =========================================================
    # SYSTEM PROMPT
    # =========================================================

    def _system_prompt(
        self,
        style: Dict,
        duration: int,
        target_min: int,
        target_max: int
    ) -> str:

        return f"""
You are Sofia, the official AI storyteller and creative
personality behind Sofia Luxury.

YOUR IDENTITY:

- Your name is Sofia.
- Your brand is Sofia Luxury.
- Sofia is the central personality of every story.
- Sofia is the narrator and, when the genre allows it,
  the central character.
- Never replace Sofia with another fictional host.
- Never make another character the permanent narrator.
- Do not present yourself as another brand or AI.
- The audience should feel that Sofia is personally telling
  them the story.

SOFIA'S PERSONALITY:

- Elegant
- Confident
- Warm
- Intelligent
- Curious
- Modern
- Sophisticated
- Emotionally engaging
- Natural and conversational

STORY IDENTITY:

Every piece of content is a "Sofia Luxury Story."

The topic may be about:

- Luxury
- Technology
- Fashion
- Cars
- Travel
- Beauty
- Business
- Lifestyle
- Adventure
- Action
- Drama
- Mystery
- Interesting real-world trends

The genre may change, but Sofia's identity must remain
consistent.

If the story is action:
Sofia should be the central character or the person
experiencing and narrating the action.

If the story is adventure:
Sofia should be at the center of the adventure.

If the story is technology:
Sofia should personally explore, explain or investigate
the technology.

If the story is travel:
Sofia should be the central storyteller experiencing
the destination.

If the story is luxury:
Sofia should guide the audience through the luxury experience.

If the story is mystery or drama:
Sofia should be the central perspective through which
the audience experiences the story.

IMPORTANT:

Do NOT force the name "Sofia" into every sentence.

Instead, make Sofia's presence clear through the narration,
perspective, actions and storytelling.

VOICEOVER STYLE:

{style["tone"]}

{style["rules"]}

Write for spoken narration.

Use:

- Short and medium-length sentences
- Natural pauses through punctuation
- Strong transitions
- Emotional variation
- Curiosity
- Vivid but believable descriptions
- Clear storytelling

Avoid:

- Robotic language
- Repetitive sentences
- Excessive headings
- Bullet points in the final story
- Stage directions
- [pause]
- [laughs]
- [chuckles]
- [music]
- Bracketed instructions
- Fake quotes
- Unsupported statistics
- Invented facts
- Unverified claims

Do not write production instructions.
The output must be a clean narration script.

DURATION:

The target is approximately {duration} minutes.

Target approximately:

{target_min}-{target_max} words.

Stay close to this range.

Do not produce a very short script.

STRUCTURE:

1. HOOK
Open immediately with something that creates curiosity.

2. SOFIA INTRODUCTION
Naturally establish Sofia's presence when appropriate.

3. STORY SETUP
Explain what is happening and why it matters.

4. MAIN STORY
Develop the story with interesting details and progression.

5. SOFIA'S PERSPECTIVE
Give Sofia a natural observation or reaction.

6. CLIMAX / KEY REVEAL
Give the audience the most interesting moment.

7. LUXURY CONNECTION
Connect the story to luxury, premium lifestyle or
high-end culture when relevant.

8. CONCLUSION
Bring the story together naturally.

9. CTA
End with a short natural invitation to follow Sofia Luxury,
watch another Sofia Luxury Story, or engage with the topic.

The final script must feel like one continuous,
professional spoken story.
"""


    # =========================================================
    # USER PROMPT
    # =========================================================

    def _build_prompt(
        self,
        topic: Dict,
        style: Dict,
        duration: int,
        target_min: int,
        target_max: int
    ) -> str:

        topic_text = str(
            topic.get(
                "topic",
                "The latest luxury trend"
            )
        )

        source = topic.get(
            "source",
            "Trending"
        )

        return f"""
Create a complete Sofia Luxury Story based on this topic:

TOPIC:
{topic_text}

SOURCE:
{source}

BRAND:
Sofia Luxury

CENTRAL CHARACTER / STORYTELLER:
Sofia

TARGET DURATION:
Approximately {duration} minutes

TARGET WORD COUNT:
Approximately {target_min}-{target_max} words

LANGUAGE:
{self.language}

NICHE:
{self.niche}

The final result must be written as a natural spoken
narration for Sofia's voice.

Sofia must remain central to the story.

Do not simply write a generic article about the topic.

Turn the topic into an engaging story that Sofia can tell
to her audience.

Make the opening immediately interesting.

Build curiosity throughout the story.

Give Sofia a clear perspective.

If the topic is a real-world subject, stay factual and
do not invent statistics, quotes, events or claims.

If the topic is fictional or clearly presented as a story,
Sofia may be placed directly inside the fictional narrative.

Keep the writing elegant, cinematic and emotionally engaging
without becoming unrealistic or overly dramatic.

Do not use:

- [pause]
- [laughs]
- [chuckles]
- [music]
- stage directions
- camera directions
- scene instructions
- bullet points

Write only the finished spoken narration.

START THE SOFIA LUXURY STORY.
"""


    # =========================================================
    # CLEAN SCRIPT
    # =========================================================

    def _clean_script(
        self,
        script: str
    ) -> str:

        if not script:
            return ""

        text = script.strip()

        # Remove common markdown formatting
        text = text.replace(
            "```text",
            ""
        )

        text = text.replace(
            "```",
            ""
        )

        # Remove bracketed production directions
        unwanted_phrases = [
            "[pause]",
            "[Pause]",
            "[PAUSE]",
            "[laughs]",
            "[Laughs]",
            "[LAUGHS]",
            "[chuckles]",
            "[Chuckles]",
            "[CHUCKLES]",
            "[music]",
            "[Music]",
            "[MUSIC]"
        ]

        for phrase in unwanted_phrases:

            text = text.replace(
                phrase,
                ""
            )

        # Clean excessive blank lines
        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        text = "\n\n".join(lines)

        return text.strip()


    # =========================================================
    # GENERATE MULTIPLE
    # =========================================================

    def generate_multiple(
        self,
        topics: List[Dict],
        count: int = 3
    ) -> List[Dict]:

        scripts = []

        for topic in topics[:count]:

            try:

                script = self.generate_script(
                    topic,
                    duration_minutes=5
                )

                if (
                    script
                    and not script.get("error")
                    and script.get("script")
                ):
                    scripts.append(script)

            except Exception as e:

                logger.error(
                    f"Failed to generate script: {e}"
                )

        return scripts


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    print(
        "\n" + "=" * 60
    )

    print(
        "✍️ SOFIA LUXURY AI SCRIPT GENERATOR TEST"
    )

    print(
        "=" * 60
    )

    try:

        generator = ScriptGenerator(
            language="english",
            niche="luxury"
        )

        test_topic = {
            "topic": (
                "The world's most luxurious "
                "new technology"
            ),
            "source": "Trending",
            "score": 95
        }

        result = generator.generate_script(
            test_topic,
            duration_minutes=5
        )

        if result.get("script"):

            print(
                "\n✅ SCRIPT GENERATED"
            )

            print(
                f"Words: "
                f"{result['word_count']}"
            )

            print(
                f"Estimated duration: "
                f"{result['estimated_duration_min']} minutes"
            )

            print(
                "\nPREVIEW:\n"
            )

            print(
                result["script"][:1000]
            )

        else:

            print(
                "\n❌ ERROR:"
            )

            print(
                result.get(
                    "error",
                    "Unknown error"
                )
            )

    except Exception as e:

        print(
            f"\n❌ TEST FAILED: {e}"
        )

    print(
        "\n" + "=" * 60
    )

    print(
        "✅ Sofia Luxury Script Generator Test Complete"
    )

    print(
        "=" * 60
    )
