"""
⏰ SOFIA LUXURY STORY AUTO-SCHEDULER

The automation controller for Sofia Luxury.

Creates approximately 5-minute Sofia Luxury Stories with:
- Trending topic discovery
- Sofia-centered AI scripts
- Female AI voice-over
- Cinematic video creation
- AI visual generation
- Pexels stock-video support
- Background music
- Professional transitions
- Thumbnails
- SEO metadata
- Content history
- Automatic scheduling

Sofia is the central storyteller and creative character.
"""

import sys
import asyncio
import json
import time
import os
from pathlib import Path
from datetime import datetime

from loguru import logger
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from schedule import every, repeat, run_pending
from dotenv import load_dotenv


# ---------------------------------------------------------
# PATH SETUP
# ---------------------------------------------------------

BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

load_dotenv()


# ---------------------------------------------------------
# IMPORTS
# ---------------------------------------------------------

from research.trend_finder import TrendFinder
from content.script_generator import ScriptGenerator
from content.voiceover_gen import VoiceoverGenerator
from content.thumbnail_maker import ThumbnailMaker
from seo.seo_engine import SEOEngine
from platforms.facebook_publisher import FacebookPublisher


# ---------------------------------------------------------
# VIDEO CREATOR
# ---------------------------------------------------------

try:
    sys.path.insert(0, str(BASE_DIR / "content"))
    from video_creator_pro import ProfessionalVideoCreator
except Exception:
    from content.video_creator import VideoCreator as ProfessionalVideoCreator


# ---------------------------------------------------------
# CONSOLE
# ---------------------------------------------------------

console = Console()


# ---------------------------------------------------------
# SOFIA LUXURY STORY SETTINGS
# ---------------------------------------------------------

STORY_DURATION_MINUTES = 5

DEFAULT_LANGUAGE = "english"
DEFAULT_NICHE = "luxury"

SOFIA_BRAND = "Sofia Luxury"

DEFAULT_TOPIC = (
    "The latest luxury technology, lifestyle, travel, fashion, "
    "business or entertainment trend"
)


# ---------------------------------------------------------
# AUTO SCHEDULER
# ---------------------------------------------------------

class AutoScheduler:
    """
    Complete Sofia Luxury Story content factory.

    Every generated story is designed around Sofia as the
    central AI storyteller and creative character.
    """

    def __init__(
        self,
        language=DEFAULT_LANGUAGE,
        niche=DEFAULT_NICHE,
        post_to_youtube=False,
        post_to_facebook=False
    ):

        self.language = language
        self.niche = niche

        self.post_to_youtube = post_to_youtube
        self.post_to_facebook = post_to_facebook

        # -------------------------------------------------
        # CORE AI SERVICES
        # -------------------------------------------------

        self.trend_finder = TrendFinder(
            niche=niche,
            language=language
        )

        self.script_gen = ScriptGenerator(
            language=language,
            niche=niche
        )

        self.voice_gen = VoiceoverGenerator(
            language=language,
            gender="female"
        )

        self.video_creator = ProfessionalVideoCreator()

        self.thumbnail_maker = ThumbnailMaker()

        self.seo_engine = SEOEngine(
            language=language,
            niche=niche
        )

        self.fb_publisher = FacebookPublisher()

        # -------------------------------------------------
        # STATISTICS
        # -------------------------------------------------

        self.stats = {
            "videos_created": 0,
            "posts_made": 0,
            "last_run": None,
            "errors": 0
        }

        self._load_stats()

        logger.info(
            f"🚀 {SOFIA_BRAND} AutoScheduler "
            f"| language={language} "
            f"| niche={niche} "
            f"| duration={STORY_DURATION_MINUTES} minutes"
        )


    # =====================================================
    # STATISTICS
    # =====================================================

    def _load_stats(self):
        """Load previous scheduler statistics."""

        stats_path = BASE_DIR / "data" / "stats.json"

        try:
            if stats_path.exists():

                with open(
                    stats_path,
                    "r",
                    encoding="utf-8"
                ) as f:

                    loaded = json.load(f)

                    if isinstance(loaded, dict):
                        self.stats.update(loaded)

        except Exception as e:

            logger.warning(
                f"Could not load statistics: {e}"
            )


    def _save_stats(self):
        """Save scheduler statistics."""

        stats_path = BASE_DIR / "data" / "stats.json"

        try:

            stats_path.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            with open(
                stats_path,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    self.stats,
                    f,
                    indent=2,
                    ensure_ascii=False
                )

        except Exception as e:

            logger.warning(
                f"Could not save statistics: {e}"
            )


    # =====================================================
    # TOPIC DISCOVERY
    # =====================================================

    def find_story_topic(self):

        console.print(
            "[yellow]🔍 Finding a trending Sofia Luxury topic...[/yellow]"
        )

        try:

            trends = self.trend_finder.find_trends(1)

            if trends:

                topic = trends[0].get("topic")

                if topic:
                    return topic

        except Exception as e:

            logger.warning(
                f"Trend search failed: {e}"
            )

        return DEFAULT_TOPIC


    # =====================================================
    # CREATE CONTENT
    # =====================================================

    async def create_content(self, topic=None):

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        console.print(
            Panel(
                f"[bold cyan]"
                f"🎬 SOFIA LUXURY STORY"
                f"[/bold cyan]\n\n"
                f"Target duration: "
                f"{STORY_DURATION_MINUTES} minutes\n"
                f"Language: {self.language}\n"
                f"Niche: {self.niche}\n"
                f"Time: {timestamp}"
            )
        )

        try:

            # -------------------------------------------------
            # 1. FIND TOPIC
            # -------------------------------------------------

            if not topic:

                topic = self.find_story_topic()

            topic = str(topic).strip()

            if not topic:

                topic = DEFAULT_TOPIC

            console.print(
                f"[green]✅ Story topic:[/green] "
                f"{topic[:120]}"
            )


            # -------------------------------------------------
            # 2. GENERATE SOFIA STORY SCRIPT
            # -------------------------------------------------

            console.print(
                "[yellow]"
                f"✍️ Writing approximately "
                f"{STORY_DURATION_MINUTES}-minute Sofia story..."
                "[/yellow]"
            )

            script_data = self.script_gen.generate_script(
                {
                    "topic": topic,
                    "brand": SOFIA_BRAND,
                    "character": "Sofia"
                },
                duration_minutes=STORY_DURATION_MINUTES
            )

            if not script_data:

                raise RuntimeError(
                    "Script generator returned no data."
                )

            script_text = script_data.get(
                "script",
                ""
            )

            if not script_text.strip():

                raise RuntimeError(
                    "Generated script is empty."
                )

            console.print(
                "[green]✅ Sofia story script created.[/green]"
            )


            # -------------------------------------------------
            # 3. CREATE VOICEOVER
            # -------------------------------------------------

            console.print(
                "[yellow]"
                "🎙️ Creating Sofia voice-over..."
                "[/yellow]"
            )

            output_dir = BASE_DIR / "output"

            output_dir.mkdir(
                parents=True,
                exist_ok=True
            )

            voice_path = (
                output_dir /
                f"sofia_story_voice_{timestamp}.mp3"
            )

            await self.voice_gen.generate(
                script_text,
                str(voice_path)
            )

            if not voice_path.exists():

                raise RuntimeError(
                    "Voice-over file was not created."
                )

            console.print(
                "[green]✅ Voice-over created.[/green]"
            )


            # -------------------------------------------------
            # 4. CREATE CINEMATIC VIDEO
            # -------------------------------------------------

            console.print(
                "[yellow]"
                "🎬 Creating Sofia Luxury Story video..."
                "[/yellow]"
            )

            video_path = (
                output_dir /
                f"sofia_luxury_story_{timestamp}.mp4"
            )

            self.video_creator.create_professional_video(
                voiceover_path=str(voice_path),
                topic=topic,
                script_text=script_text,
                niche=self.niche,
                add_music=True,
                output_path=str(video_path)
            )

            if not video_path.exists():

                raise RuntimeError(
                    "Video file was not created."
                )

            console.print(
                "[green]✅ Sofia Luxury Story video created.[/green]"
            )


            # -------------------------------------------------
            # 5. CREATE THUMBNAIL
            # -------------------------------------------------

            console.print(
                "[yellow]"
                "🖼️ Creating thumbnail..."
                "[/yellow]"
            )

            thumb_path = self.thumbnail_maker.create_thumbnail(
                topic,
                niche=self.niche
            )

            console.print(
                "[green]✅ Thumbnail created.[/green]"
            )


            # -------------------------------------------------
            # 6. GENERATE SEO
            # -------------------------------------------------

            console.print(
                "[yellow]"
                "📈 Generating title, description, tags and SEO..."
                "[/yellow]"
            )

            seo_data = self.seo_engine.generate_all_metadata(
                topic,
                script_text
            )

            console.print(
                "[green]✅ SEO package created.[/green]"
            )


            # -------------------------------------------------
            # 7. SAVE STORY HISTORY
            # -------------------------------------------------

            history_dir = (
                BASE_DIR /
                "data" /
                "history"
            )

            history_dir.mkdir(
                parents=True,
                exist_ok=True
            )

            result = {
                "brand": SOFIA_BRAND,
                "character": "Sofia",
                "timestamp": timestamp,
                "duration_minutes": STORY_DURATION_MINUTES,
                "language": self.language,
                "niche": self.niche,
                "topic": topic,
                "script": script_text,
                "video": str(video_path),
                "voiceover": str(voice_path),
                "thumbnail": str(thumb_path),
                "seo": seo_data
            }

            history_file = (
                history_dir /
                f"sofia_story_{timestamp}.json"
            )

            with open(
                history_file,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    result,
                    f,
                    indent=2,
                    ensure_ascii=False,
                    default=str
                )


            # -------------------------------------------------
            # 8. UPDATE STATISTICS
            # -------------------------------------------------

            self.stats["videos_created"] += 1

            self.stats["last_run"] = timestamp

            self._save_stats()


            # -------------------------------------------------
            # 9. SUCCESS
            # -------------------------------------------------

            console.print(
                Panel(
                    "[bold green]"
                    "✅ SOFIA LUXURY STORY CREATED!"
                    "[/bold green]\n\n"
                    f"🎬 Topic: {topic}\n"
                    f"⏱️ Target: {STORY_DURATION_MINUTES} minutes\n"
                    f"🎙️ Voice: {voice_path}\n"
                    f"🎥 Video: {video_path}\n"
                    f"🖼️ Thumbnail: {thumb_path}\n"
                    f"📄 History: {history_file}"
                )
            )

            return result


        except Exception as e:

            self.stats["errors"] += 1

            self._save_stats()

            logger.exception(
                "Sofia Luxury Story creation failed."
            )

            console.print(
                Panel(
                    f"[bold red]"
                    f"❌ SOFIA LUXURY STORY FAILED"
                    f"[/bold red]\n\n"
                    f"{e}"
                )
            )

            return None


    # =====================================================
    # STATUS
    # =====================================================

    def show_status(self):

        table = Table(
            title="📊 SOFIA LUXURY STORY STATUS"
        )

        table.add_column(
            "Metric",
            style="cyan"
        )

        table.add_column(
            "Value",
            style="green"
        )

        table.add_row(
            "Brand",
            SOFIA_BRAND
        )

        table.add_row(
            "Character",
            "Sofia"
        )

        table.add_row(
            "Language",
            self.language
        )

        table.add_row(
            "Niche",
            self.niche
        )

        table.add_row(
            "Target Duration",
            f"{STORY_DURATION_MINUTES} minutes"
        )

        table.add_row(
            "Videos Created",
            str(
                self.stats.get(
                    "videos_created",
                    0
                )
            )
        )

        table.add_row(
            "Last Run",
            str(
                self.stats.get(
                    "last_run",
                    "Never"
                )
            )
        )

        table.add_row(
            "Errors",
            str(
                self.stats.get(
                    "errors",
                    0
                )
            )
        )

        console.print(table)


    # =====================================================
    # DAILY AUTOMATION
    # =====================================================

    def run_forever(self):

        console.print(
            Panel.fit(
                "[bold green]"
                "🚀 SOFIA LUXURY STORY AUTOMATION RUNNING"
                "[/bold green]"
            )
        )

        post_time = os.getenv(
            "POSTING_TIME",
            "10:00"
        )


        @repeat(
            every().day.at(post_time)
        )
        def scheduled_run():

            asyncio.run(
                self.create_content()
            )


        console.print(
            f"⏰ Daily story creation: {post_time}"
        )

        try:

            while True:

                run_pending()

                time.sleep(30)

        except KeyboardInterrupt:

            console.print(
                "\n[green]"
                "👋 Sofia Luxury automation stopped."
                "[/green]"
            )


# =========================================================
# COMMAND-LINE ENTRY
# =========================================================

async def main():

    console.print(
        """
╔══════════════════════════════════════════╗
║       ✨ SOFIA LUXURY STORY ✨           ║
║        AI CONTENT AUTOMATION             ║
╚══════════════════════════════════════════╝
        """
    )

    scheduler = AutoScheduler(
        language="english",
        niche="luxury"
    )

    scheduler.show_status()


    while True:

        console.print(
            "\n📋 "
            "1. Create Story NOW"
            " | 2. Auto-Schedule"
            " | 3. Status"
            " | 4. Exit"
        )

        choice = input(
            "👉 "
        ).strip()


        if choice == "1":

            topic = input(
                "Story topic "
                "(press Enter for automatic trend): "
            ).strip()

            await scheduler.create_content(
                topic if topic else None
            )


        elif choice == "2":

            scheduler.run_forever()


        elif choice == "3":

            scheduler.show_status()


        elif choice == "4":

            console.print(
                "[green]"
                "Goodbye from Sofia Luxury."
                "[/green]"
            )

            break


        else:

            console.print(
                "[yellow]"
                "Please choose 1, 2, 3 or 4."
                "[/yellow]"
            )


# =========================================================
# START
# =========================================================

if __name__ == "__main__":

    asyncio.run(main())
