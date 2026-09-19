"""
🎙️ VOICEOVER GENERATOR
Uses Microsoft Edge TTS (FREE)

Supports:
- English
- Urdu
- Hindi
- Punjabi

Designed for:
- Sofia Luxury videos
- Natural cinematic narration
- Approximately 5-minute stories
- Reliable GitHub Actions execution
"""

import asyncio
import os
from pathlib import Path
from typing import Dict

import edge_tts
from loguru import logger


class VoiceoverGenerator:
    """Generate natural voiceovers using Microsoft Edge TTS."""

    # Verified Edge TTS voices
    VOICES: Dict[str, Dict[str, str]] = {
        "english": {
            "male": "en-US-GuyNeural",
            "female": "en-US-JennyNeural",
        },
        "urdu": {
            "male": "ur-PK-AsadNeural",
            "female": "ur-PK-UzmaNeural",
        },
        "hindi": {
            "male": "hi-IN-MadhurNeural",
            "female": "hi-IN-SwaraNeural",
        },
        "punjabi": {
            # Punjabi fallback voices
            "male": "hi-IN-MadhurNeural",
            "female": "hi-IN-SwaraNeural",
        },
    }

    def __init__(
        self,
        language: str = "english",
        gender: str = "female",
    ):
        self.language = language.lower().strip()
        self.gender = gender.lower().strip()

        lang_voices = self.VOICES.get(
            self.language,
            self.VOICES["english"],
        )

        self.voice = lang_voices.get(
            self.gender,
            lang_voices["female"],
        )

        # Slightly slower narration gives the story more room
        # while keeping the voice natural.
        self.rate = "-5%"

        logger.info(
            f"🎙️ Voice: {self.voice} "
            f"({self.language}/{self.gender})"
        )

    async def generate(
        self,
        script: str,
        output_path: str,
    ) -> str:
        """
        Convert script to speech.

        The public interface is intentionally kept compatible
        with auto_scheduler.py.
        """

        if not script or not script.strip():
            raise ValueError(
                "Voiceover generation received an empty script."
            )

        script = script.strip()

        word_count = len(script.split())

        logger.info(
            f"🎙️ Generating voiceover: "
            f"{word_count} words → {output_path}"
        )

        Path(output_path).parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        try:
            communicate = edge_tts.Communicate(
                text=script,
                voice=self.voice,
                rate=self.rate,
            )

            await communicate.save(output_path)

        except Exception as exc:
            logger.error(
                f"❌ Edge TTS generation failed: {exc}"
            )
            raise

        if not os.path.exists(output_path):
            raise RuntimeError(
                "Edge TTS completed but the output file "
                "was not created."
            )

        size_kb = (
            os.path.getsize(output_path) / 1024
        )

        if size_kb <= 1:
            raise RuntimeError(
                "Generated voiceover file is empty or invalid."
            )

        logger.info(
            f"✅ Voiceover saved: "
            f"{size_kb:.1f} KB"
        )

        return output_path


# ============================================
# TEST
# ============================================

if __name__ == "__main__":

    print("\n" + "=" * 60)
    print("🎙️ SOFIA VOICEOVER GENERATOR TEST")
    print("=" * 60)

    async def test():

        # ----------------------------------------
        # English
        # ----------------------------------------

        print(
            "\n🔊 English "
            "(Female - Jenny)..."
        )

        gen_en = VoiceoverGenerator(
            language="english",
            gender="female",
        )

        script_en = """
        Tonight, Sofia stepped into a world where luxury
        was hiding a secret.

        The city glittered below her as she entered the
        private penthouse. Everything looked perfect,
        but something felt wrong.

        On the table was a small black envelope with her
        name written across it.

        Sofia opened it carefully.

        Inside was a single message.

        You have one hour to discover who is watching you.

        She looked toward the windows.

        The lights of the city stretched endlessly into
        the distance.

        Then her phone vibrated.

        Someone had just sent her a photograph taken
        from inside the room.

        Sofia realized she was not alone.

        She took a breath, picked up the photograph,
        and began searching for the truth.
        """

        await gen_en.generate(
            script_en,
            "output/test_english.mp3",
        )

        # ----------------------------------------
        # Urdu
        # ----------------------------------------

        print(
            "\n🔊 Urdu "
            "(Female - Uzma)..."
        )

        gen_ur = VoiceoverGenerator(
            language="urdu",
            gender="female",
        )

        script_ur = """
        آج ہم ایک ایسی کہانی کے بارے میں بات کریں گے
        جہاں ایک خوبصورت شہر کے درمیان ایک راز چھپا ہوا تھا۔
        """

        await gen_ur.generate(
            script_ur,
            "output/test_urdu.mp3",
        )

        # ----------------------------------------
        # Hindi
        # ----------------------------------------

        print(
            "\n🔊 Hindi "
            "(Female - Swara)..."
        )

        gen_hi = VoiceoverGenerator(
            language="hindi",
            gender="female",
        )

        script_hi = """
        आज हम एक ऐसी कहानी के बारे में बात करेंगे
        जिसमें एक खूबसूरत शहर के बीच एक रहस्य छिपा हुआ था।
        """

        await gen_hi.generate(
            script_hi,
            "output/test_hindi.mp3",
        )

        print("\n" + "=" * 60)
        print("✅ ALL VOICEOVER TESTS COMPLETE!")
        print("📁 Check the output folder for MP3 files.")
        print("=" * 60)

    asyncio.run(test())
