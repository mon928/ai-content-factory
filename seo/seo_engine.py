"""
📈 SOFIA LUXURY STORY AI SEO ENGINE

Generates high-quality YouTube titles, tags, descriptions
and hashtags for Sofia Luxury Story.

Uses Groq's current production model:
openai/gpt-oss-120b

Supports:
- English
- Urdu
- Hindi
- Punjabi
"""

import os
import json
from pathlib import Path
from typing import Dict, List
from loguru import logger
from groq import Groq
from dotenv import load_dotenv


load_dotenv()


# ============================================================
# GROQ MODEL
# ============================================================

GROQ_SEO_MODEL = "openai/gpt-oss-120b"


class SEOEngine:
    """
    Generate optimized YouTube metadata for Sofia Luxury Story.
    """

    def __init__(
        self,
        language: str = "english",
        niche: str = "tech"
    ):

        api_key = os.getenv(
            "GROQ_API_KEY"
        )

        self.client = Groq(
            api_key=api_key
        )

        self.language = language
        self.niche = niche

        # -----------------------------------------------------
        # POWER WORDS
        # -----------------------------------------------------

        self.power_words = {

            "english": [
                "Ultimate",
                "Secret",
                "Proven",
                "Shocking",
                "Must See",
                "Game Changer",
                "You Won't Believe",
                "Exposed",
                "Truth",
            ],

            "urdu": [
                "Haqeeqat",
                "Raaz",
                "Kamaal",
                "Zabardast",
                "Aakhri",
                "Bilkul Naya",
            ],

            "hindi": [
                "Sach",
                "Raaz",
                "Dhamaal",
                "Zabardast",
                "Aakhri",
                "Naya",
            ],

            "punjabi": [
                "Sach",
                "Raaz",
                "Kamaal",
                "Zabardast",
                "Vadhia",
            ],
        }

    # ========================================================
    # ALL METADATA
    # ========================================================

    def generate_all_metadata(
        self,
        topic: str,
        script: str = "",
        keywords: List[str] = None
    ) -> Dict:

        logger.info(
            f"📈 Generating SEO for: "
            f"{topic[:60]}..."
        )

        titles = self.generate_titles(
            topic
        )

        tags = self.generate_tags(
            topic,
            keywords
        )

        description = self.generate_description(
            topic,
            script
        )

        hashtags = self.generate_hashtags(
            topic
        )

        result = {

            "topic": topic,

            "language": self.language,

            "titles": titles,

            "best_title": (
                titles[0]
                if titles
                else topic
            ),

            "tags": tags,

            "description": description,

            "hashtags": hashtags,

            "estimated_ctr": (
                self._estimate_ctr(
                    titles[0]
                    if titles
                    else topic
                )
            ),
        }

        logger.info(
            f"✅ SEO package generated: "
            f"{len(tags)} tags, "
            f"{len(titles)} titles"
        )

        return result

    # ========================================================
    # TITLES
    # ========================================================

    def generate_titles(
        self,
        topic: str,
        count: int = 5
    ) -> List[str]:

        pw = self.power_words.get(
            self.language,
            self.power_words["english"]
        )

        prompt = f"""
Generate {count} YouTube video titles for:

"{topic}"

This content belongs to Sofia Luxury Story.

Rules:

1. Make the titles highly clickable.
2. Use power words when appropriate:
   {', '.join(pw[:5])}
3. Include numbers when natural.
4. Create curiosity without making false claims.
5. Keep titles under 60 characters when possible.
6. Use emotional interest appropriately.
7. Brackets or parentheses may be used.
8. Language: {self.language}
9. Make the titles relevant to the actual topic.
10. Do not invent facts.

Return ONLY a valid JSON list.

Example:

[
    "Title 1",
    "Title 2",
    "Title 3",
    "Title 4",
    "Title 5"
]
"""

        try:

            response = (
                self.client
                .chat
                .completions
                .create(
                    model=GROQ_SEO_MODEL,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are an expert YouTube "
                                "SEO strategist. "
                                "Always return valid JSON."
                            ),
                        },
                        {
                            "role": "user",
                            "content": prompt,
                        },
                    ],
                    temperature=0.8,
                    max_tokens=500,
                )
            )

            text = (
                response
                .choices[0]
                .message
                .content
                .strip()
            )

            text = self._clean_json_text(
                text
            )

            titles = json.loads(
                text
            )

            if not isinstance(
                titles,
                list
            ):

                raise ValueError(
                    "Titles response is not a list."
                )

            titles = [
                str(title).strip()
                for title in titles
                if str(title).strip()
            ]

            return titles[:count]

        except Exception as e:

            logger.error(
                f"Title generation failed: {e}"
            )

            return [topic]

    # ========================================================
    # TAGS
    # ========================================================

    def generate_tags(
        self,
        topic: str,
        extra_keywords: List[str] = None
    ) -> List[str]:

        keywords = (
            extra_keywords
            or []
        )

        prompt = f"""
Generate 25 YouTube tags for:

"{topic}"

Additional keywords:

{', '.join(keywords[:5]) if keywords else 'none'}

Rules:

1. Mix broad and specific tags.
2. Include long-tail search phrases.
3. Include relevant search terms.
4. Keep every tag relevant.
5. Do not invent unrelated brands.
6. Language: {self.language}.
7. Return ONLY a valid JSON list.

Example:

[
    "luxury technology",
    "future technology",
    "Sofia Luxury Story"
]
"""

        try:

            response = (
                self.client
                .chat
                .completions
                .create(
                    model=GROQ_SEO_MODEL,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a YouTube SEO expert. "
                                "Return valid JSON."
                            ),
                        },
                        {
                            "role": "user",
                            "content": prompt,
                        },
                    ],
                    temperature=0.7,
                    max_tokens=600,
                )
            )

            text = (
                response
                .choices[0]
                .message
                .content
                .strip()
            )

            text = self._clean_json_text(
                text
            )

            tags = json.loads(
                text
            )

            if not isinstance(
                tags,
                list
            ):

                raise ValueError(
                    "Tags response is not a list."
                )

            tags = [
                str(tag).strip()
                for tag in tags
                if str(tag).strip()
            ]

            # Add topic as a tag.
            if topic.lower() not in [
                tag.lower()
                for tag in tags
            ]:

                tags.insert(
                    0,
                    topic
                )

            return tags[:30]

        except Exception as e:

            logger.error(
                f"Tag generation failed: {e}"
            )

            return [
                topic,
                "Sofia Luxury Story",
                self.niche
            ]

    # ========================================================
    # DESCRIPTION
    # ========================================================

    def generate_description(
        self,
        topic: str,
        script: str = ""
    ) -> str:

        script_excerpt = (
            script[:300]
            if script
            else ""
        )

        prompt = f"""
Write a professional YouTube description for:

"{topic}"

This video is part of Sofia Luxury Story.

Structure:

1. Strong opening two lines.
2. Brief summary.
3. Important points from the story.
4. Natural keywords.
5. Call to action.
6. Relevant hashtags at the bottom.

Rules:

- Write in {self.language}.
- Be professional.
- Be engaging.
- Do not make unsupported claims.
- Do not invent statistics.
- Use emojis sparingly.
- Approximately 200-300 words.

Script excerpt:

{script_excerpt[:300]}

Write the description now.
"""

        try:

            response = (
                self.client
                .chat
                .completions
                .create(
                    model=GROQ_SEO_MODEL,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a professional "
                                "YouTube SEO writer."
                            ),
                        },
                        {
                            "role": "user",
                            "content": prompt,
                        },
                    ],
                    temperature=0.7,
                    max_tokens=800,
                )
            )

            return (
                response
                .choices[0]
                .message
                .content
                .strip()
            )

        except Exception as e:

            logger.error(
                f"Description generation failed: {e}"
            )

            return (
                f"Watch Sofia Luxury Story as we explore "
                f"{topic}. "
                f"Subscribe for more luxury, technology "
                f"and lifestyle stories."
            )

    # ========================================================
    # HASHTAGS
    # ========================================================

    def generate_hashtags(
        self,
        topic: str
    ) -> List[str]:

        prompt = f"""
Generate 10 relevant YouTube hashtags for:

"{topic}"

Rules:

1. Mix popular and niche hashtags.
2. Maximum 3 words per hashtag.
3. Keep them relevant to the topic.
4. Include Sofia Luxury Story when appropriate.
5. Language: {self.language}.
6. Return ONLY a valid JSON list.
"""

        try:

            response = (
                self.client
                .chat
                .completions
                .create(
                    model=GROQ_SEO_MODEL,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                    temperature=0.7,
                    max_tokens=200,
                )
            )

            text = (
                response
                .choices[0]
                .message
                .content
                .strip()
            )

            text = self._clean_json_text(
                text
            )

            hashtags = json.loads(
                text
            )

            if not isinstance(
                hashtags,
                list
            ):

                raise ValueError(
                    "Hashtags response is not a list."
                )

            cleaned = []

            for hashtag in hashtags:

                hashtag = str(
                    hashtag
                ).strip()

                if not hashtag:
                    continue

                if not hashtag.startswith(
                    "#"
                ):

                    hashtag = (
                        "#"
                        + hashtag.replace(
                            " ",
                            ""
                        )
                    )

                cleaned.append(
                    hashtag
                )

            # Add Sofia brand hashtag.
            if "#SofiaLuxuryStory" not in cleaned:

                cleaned.append(
                    "#SofiaLuxuryStory"
                )

            if self.niche:

                niche_tag = (
                    "#"
                    + self.niche.replace(
                        "_",
                        ""
                    )
                    .replace(
                        " ",
                        ""
                    )
                )

                if niche_tag not in cleaned:

                    cleaned.append(
                        niche_tag
                    )

            return cleaned[:15]

        except Exception as e:

            logger.error(
                f"Hashtag generation failed: {e}"
            )

            safe_topic = (
                topic
                .replace(
                    " ",
                    ""
                )
                .replace(
                    "#",
                    ""
                )
            )

            return [
                f"#{safe_topic}",
                "#SofiaLuxuryStory",
                "#YouTube",
                "#Luxury",
            ]

    # ========================================================
    # CLEAN JSON
    # ========================================================

    def _clean_json_text(
        self,
        text: str
    ) -> str:

        text = (
            text
            .strip()
        )

        if text.startswith(
            "```"
        ):

            lines = text.split(
                "\n"
            )

            if len(lines) >= 2:

                lines = lines[1:]

            if lines and lines[-1].strip().startswith(
                "```"
            ):

                lines = lines[:-1]

            text = "\n".join(
                lines
            ).strip()

        return text

    # ========================================================
    # CTR ESTIMATE
    # ========================================================

    def _estimate_ctr(
        self,
        title: str
    ) -> Dict:

        score = 50

        # ----------------------------------------------------
        # POWER WORDS
        # ----------------------------------------------------

        for pw_list in (
            self.power_words.values()
        ):

            for word in pw_list:

                if (
                    word.lower()
                    in title.lower()
                ):

                    score += 10

                    break

        # ----------------------------------------------------
        # NUMBERS
        # ----------------------------------------------------

        if any(
            char.isdigit()
            for char in title
        ):

            score += 8

        # ----------------------------------------------------
        # CURIOSITY WORDS
        # ----------------------------------------------------

        curiosity_words = [
            "this",
            "secret",
            "why",
            "how",
            "what",
            "shocking",
            "never",
        ]

        for word in curiosity_words:

            if (
                word.lower()
                in title.lower()
            ):

                score += 5

        # ----------------------------------------------------
        # LENGTH
        # ----------------------------------------------------

        if (
            30
            <= len(title)
            <= 60
        ):

            score += 7

        score = min(
            score,
            100
        )

        return {

            "score": score,

            "rating": (
                "⭐⭐⭐"
                if score > 70
                else "⭐⭐"
                if score > 50
                else "⭐"
            ),
        }

    # ========================================================
    # SAVE METADATA
    # ========================================================

    def save_metadata(
        self,
        metadata: Dict,
        filepath: str = None
    ) -> str:

        if filepath is None:

            safe_name = (
                metadata
                .get(
                    "topic",
                    "video"
                )[:30]
                .replace(
                    " ",
                    "_"
                )
            )

            filepath = (
                f"output/"
                f"seo_{safe_name}.json"
            )

        Path(
            filepath
        ).parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            filepath,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                metadata,
                f,
                indent=2,
                ensure_ascii=False
            )

        logger.info(
            f"💾 SEO metadata saved: "
            f"{filepath}"
        )

        return filepath


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print(
        "\n"
        + "=" * 60
    )

    print(
        "📈 SOFIA LUXURY STORY AI SEO ENGINE TEST"
    )

    print(
        "=" * 60
    )

    # --------------------------------------------------------
    # ENGLISH TEST
    # --------------------------------------------------------

    print(
        "\n📊 Testing English SEO..."
    )

    seo_en = SEOEngine(
        language="english",
        niche="luxury"
    )

    test_topic = (
        "The Future of Luxury Technology"
    )

    result = (
        seo_en.generate_all_metadata(
            test_topic
        )
    )

    print(
        f"\n✅ Best Title: "
        f"{result['best_title']}"
    )

    print(
        f"📊 CTR Score: "
        f"{result['estimated_ctr']['score']}/100 "
        f"{result['estimated_ctr']['rating']}"
    )

    print(
        f"\n🏷️ Tags "
        f"({len(result['tags'])}):"
    )

    for tag in result["tags"][:5]:

        print(
            f"   - {tag}"
        )

    print(
        f"   ... and "
        f"{len(result['tags']) - 5} more"
    )

    print(
        "\n📝 Description Preview:"
    )

    desc = (
        result["description"]
    )

    print(
        f"   {desc[:200]}..."
    )

    print(
        "\n#️⃣ Hashtags:"
    )

    for hashtag in (
        result["hashtags"][:5]
    ):

        print(
            f"   {hashtag}"
        )

    seo_en.save_metadata(
        result,
        "output/seo_test.json"
    )

    # --------------------------------------------------------
    # URDU TEST
    # --------------------------------------------------------

    print(
        "\n"
        + "-" * 40
    )

    print(
        "\n📊 Testing Urdu SEO..."
    )

    seo_ur = SEOEngine(
        language="urdu",
        niche="tech"
    )

    test_topic_ur = (
        "Pakistan 5G Technology - Latest Updates"
    )

    result_ur = (
        seo_ur.generate_all_metadata(
            test_topic_ur
        )
    )

    print(
        f"\n✅ Best Title (UR): "
        f"{result_ur['best_title']}"
    )

    print(
        f"📊 CTR Score: "
        f"{result_ur['estimated_ctr']['score']}/100"
    )

    print(
        f"\n🏷️ Tags "
        f"({len(result_ur['tags'])}):"
    )

    for tag in (
        result_ur["tags"][:5]
    ):

        print(
            f"   - {tag}"
        )

    seo_en.save_metadata(
        result_ur,
        "output/seo_test_ur.json"
    )

    print(
        "\n"
        + "=" * 60
    )

    print(
        "✅ SEO Engine Test Complete!"
    )

    print(
        "📁 Check output/ folder for JSON files"
    )

    print(
        "=" * 60
    )
