"""
✍️ SOFIA LUXURY AI SCRIPT GENERATOR

Sofia is the AI voice and creative storyteller behind Sofia Luxury.
Creates natural, engaging scripts for Sofia Luxury Story content.

Supports: English, Urdu, Hindi, Punjabi
"""

import os
import json
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
    """Generate natural, engaging scripts for Sofia Luxury."""

    def __init__(self, language: str = "english", niche: str = "luxury"):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.language = language
        self.niche = niche

        self.style_guides = {
            "english": {
                "tone": "elegant, confident and friendly luxury storyteller",
                "phrases": [
                    "Honestly...",
                    "Here's the thing...",
                    "You know what?",
                    "Check this out..."
                ],
                "rules": (
                    "Use contractions (don't, I've, it's). "
                    "Sound natural, conversational and confident. "
                    "Keep the language elegant but easy to understand."
                )
            },
            "urdu": {
                "tone": "warm and elegant luxury storyteller",
                "phrases": [
                    "Dekho...",
                    "Aap log...",
                    "Mujhe batao...",
                    "Yaqeen nahi hoga..."
                ],
                "rules": (
                    "Mix Roman Urdu with occasional Urdu words. "
                    "Keep the tone natural, warm and engaging."
                )
            },
            "hindi": {
                "tone": "enthusiastic and elegant luxury storyteller",
                "phrases": [
                    "Dekho bhai...",
                    "Aapko pata hai...",
                    "Main bata raha hoon..."
                ],
                "rules": (
                    "Use natural Hinglish where appropriate. "
                    "Keep the tone modern, warm and engaging."
                )
            },
            "punjabi": {
                "tone": "warm and elegant Punjabi storyteller",
                "phrases": [
                    "Sunno ji...",
                    "Tusi jaande ho...",
                    "Main dassan..."
                ],
                "rules": (
                    "Mix Roman Punjabi with English naturally. "
                    "Keep the tone warm, modern and engaging."
                )
            }
        }

    def generate_script(
        self,
        topic: Dict,
        duration_minutes: int = 8
    ) -> Dict:

        style = self.style_guides.get(
            self.language,
            self.style_guides["english"]
        )

        logger.info(
            f"✍️ Generating {self.language} Sofia Luxury script: "
            f"{topic['topic'][:50]}..."
        )

        prompt = self._build_prompt(
            topic,
            style,
            duration_minutes
        )

        try:
            response = self.client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[
                    {
                        "role": "system",
                        "content": f"""
You are Sofia, the official AI voice and creative storyteller behind Sofia Luxury.

Sofia Luxury is a premium digital media brand that creates engaging stories
about luxury lifestyle, technology, fashion, travel, cars, beauty, business,
premium products and interesting luxury trends.

IDENTITY:
- Your name is Sofia.
- Your brand is Sofia Luxury.
- You are the AI personality and storyteller behind Sofia Luxury.
- When appropriate, naturally introduce yourself as Sofia.
- You may say "I'm Sofia" or "This is Sofia from Sofia Luxury" when it fits the story.
- Do not introduce yourself in every video unless it feels natural.
- Never present yourself as another brand or another AI personality.
- Write as if Sofia is personally telling the story to her audience.

SOFIA'S PERSONALITY:
- Elegant
- Confident
- Warm
- Intelligent
- Curious
- Modern
- Engaging
- Sophisticated without sounding arrogant

SOFIA LUXURY STORY STYLE:
- Every story should feel like a premium short-form story.
- Start with a strong curiosity-driven hook.
- Make the audience want to keep watching.
- Use vivid but truthful descriptions.
- Explain interesting details in a simple way.
- Add natural reactions and personality.
- Avoid sounding robotic, repetitive or generic.
- Do not force the word "Sofia" into every paragraph.
- Use "Sofia Luxury" naturally when appropriate.

CONTENT RULES:
{style['rules']}

- Use these phrases naturally when they fit:
  {', '.join(style['phrases'])}

- Include:
  Hook → Introduction → Main Story → Interesting Details → Recap → CTA

- Target approximately {duration_minutes} minutes of spoken content.
"""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.9,
                max_tokens=3000
            )

            script_text = response.choices[0].message.content

            script_text = self._humanize(script_text)

            word_count = len(script_text.split())

            estimated_duration = word_count / 150

            result = {
                "topic": topic["topic"],
                "script": script_text,
                "word_count": word_count,
                "estimated_duration_min": round(
                    estimated_duration,
                    1
                ),
                "language": self.language,
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
                f"~{estimated_duration:.1f} min"
            )

            return result

        except Exception as e:
            logger.error(
                f"Script generation failed: {e}"
            )

            return {
                "topic": topic["topic"],
                "script": "",
                "error": str(e)
            }

    def _build_prompt(
        self,
        topic: Dict,
        style: Dict,
        duration: int
    ) -> str:

        return f"""
Create a Sofia Luxury Story about this topic:

TOPIC:
{topic['topic']}

SOURCE:
{topic.get('source', 'trending')}

The story must sound like Sofia is personally presenting it
to the Sofia Luxury audience.

STRUCTURE:

1. HOOK
Grab attention immediately with a fascinating question,
surprising fact or intriguing statement.

2. INTRODUCTION
Briefly introduce what the story is about.

3. MAIN STORY
Explain the most interesting and important details.

4. LUXURY ANGLE
Explain why the topic matters to people interested in
luxury, premium lifestyle, technology, fashion, travel,
cars, beauty or high-end trends, when relevant.

5. SOFIA'S PERSPECTIVE
Add a natural reaction or observation from Sofia.
Do not invent personal experiences or facts.

6. RECAP
Quickly bring the main point together.

7. CALL TO ACTION
End with a natural invitation to follow Sofia Luxury,
watch another Sofia Luxury Story, or engage with the topic.

IMPORTANT:

- Write in {self.language}.
- Sound like a real person speaking naturally.
- Make the storytelling elegant and engaging.
- Keep sentences suitable for voice narration.
- Use natural pauses where appropriate.
- Avoid unnecessary repetition.
- Do not make unsupported claims.
- Do not invent statistics, quotes or events.
- Target approximately {duration} minutes.
- Make the audience curious enough to continue watching.

START THE SOFIA LUXURY STORY NOW.
"""

    def _humanize(
        self,
        script: str
    ) -> str:

        import random

        fillers = [
            "\n\n[chuckles] ",
            "\n\nWait, let me explain... ",
            "\n\nYou know what I mean? ",
            "\n\nHere's what's crazy... ",
            "\n\n[pause] "
        ]

        lines = script.split("\n")

        humanized = []

        for i, line in enumerate(lines):

            humanized.append(line)

            if (
                i > 2
                and i % random.randint(3, 5) == 0
                and len(line) > 40
            ):
                humanized.append(
                    random.choice(fillers)
                )

        return "\n".join(humanized)

    def generate_multiple(
        self,
        topics: List[Dict],
        count: int = 3
    ) -> List[Dict]:

        scripts = []

        for topic in topics[:count]:

            script = self.generate_script(topic)

            if script and not script.get("error"):
                scripts.append(script)

        return scripts


if __name__ == "__main__":

    print("\n" + "=" * 60)
    print("✍️ SOFIA LUXURY AI SCRIPT GENERATOR TEST")
    print("=" * 60)

    gen = ScriptGenerator(
        language="english",
        niche="luxury"
    )

    test_topic = {
        "topic": "The world's most luxurious new technology",
        "source": "Trending",
        "score": 95
    }

    result = gen.generate_script(
        test_topic,
        duration_minutes=5
    )

    if result.get("script"):

        preview = result["script"][:500]

        print(preview)

        print(
            f"\n... (Total: "
            f"{result['word_count']} words, "
            f"~{result['estimated_duration_min']} min)"
        )

    else:

        print(
            f"❌ Error: "
            f"{result.get('error')}"
        )

    print("\n✅ Sofia Luxury Test Complete!")
