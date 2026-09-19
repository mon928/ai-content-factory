"""
📤 YOUTUBE UPLOADER
Auto-upload videos with safe YouTube metadata
Uses YouTube Data API v3
"""

import os
import json
from pathlib import Path
from typing import Dict, Any

from loguru import logger
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from dotenv import load_dotenv

load_dotenv()


class YouTubeUploader:
    """Upload videos to YouTube with validated metadata."""

    SCOPES = [
        "https://www.googleapis.com/auth/youtube.upload"
    ]

    API_SERVICE_NAME = "youtube"
    API_VERSION = "v3"

    def __init__(self):
        self.youtube = None
        self.authenticated = False

    # ============================================================
    # AUTHENTICATION
    # ============================================================

    def authenticate(self, client_secrets_file: str = None) -> bool:
        """Authenticate with YouTube using OAuth 2.0."""

        logger.info("🔐 Authenticating with YouTube...")

        try:
            token_json = os.getenv("YOUTUBE_TOKEN_JSON")

            if token_json:
                info = json.loads(token_json)

                credentials = Credentials.from_authorized_user_info(
                    info,
                    self.SCOPES
                )

                if credentials.expired and credentials.refresh_token:
                    logger.info("🔄 Refreshing YouTube OAuth token...")
                    credentials.refresh(Request())

                if not credentials.valid:
                    logger.error(
                        "❌ YouTube OAuth credentials are invalid"
                    )
                    return False

                self.youtube = build(
                    self.API_SERVICE_NAME,
                    self.API_VERSION,
                    credentials=credentials
                )

                self.authenticated = True

                logger.info(
                    "✅ Authenticated with YouTube OAuth"
                )

                return True

            if (
                client_secrets_file
                and Path(client_secrets_file).exists()
            ):
                flow = InstalledAppFlow.from_client_secrets_file(
                    client_secrets_file,
                    self.SCOPES
                )

                credentials = flow.run_local_server(
                    port=0
                )

                self.youtube = build(
                    self.API_SERVICE_NAME,
                    self.API_VERSION,
                    credentials=credentials
                )

                self.authenticated = True

                logger.info(
                    "✅ Authenticated with YouTube OAuth"
                )

                return True

            logger.error(
                "❌ No YouTube OAuth credentials found"
            )

            return False

        except Exception as e:
            logger.error(
                f"❌ YouTube authentication failed: {e}"
            )
            return False

    # ============================================================
    # SAFE TEXT HELPERS
    # ============================================================

    @staticmethod
    def _safe_string(value: Any, default: str = "") -> str:
        """
        Convert AI-generated metadata into a normal string.
        Handles strings, lists, dictionaries and other values.
        """

        if value is None:
            return default

        if isinstance(value, str):
            return value.strip()

        if isinstance(value, list):
            for item in value:
                if isinstance(item, str) and item.strip():
                    return item.strip()

                if isinstance(item, dict):
                    for key in (
                        "title",
                        "text",
                        "value",
                        "name"
                    ):
                        candidate = item.get(key)

                        if (
                            isinstance(candidate, str)
                            and candidate.strip()
                        ):
                            return candidate.strip()

            return default

        if isinstance(value, dict):
            for key in (
                "title",
                "text",
                "value",
                "name"
            ):
                candidate = value.get(key)

                if (
                    isinstance(candidate, str)
                    and candidate.strip()
                ):
                    return candidate.strip()

            return default

        return str(value).strip()

    @staticmethod
    def _limit_utf8(text: str, max_bytes: int) -> str:
        """
        Limit text by UTF-8 byte length rather than character count.
        """

        if not text:
            return ""

        encoded = text.encode(
            "utf-8",
            errors="ignore"
        )

        if len(encoded) <= max_bytes:
            return text

        encoded = encoded[:max_bytes]

        while True:
            try:
                return encoded.decode(
                    "utf-8",
                    errors="strict"
                )
            except UnicodeDecodeError:
                encoded = encoded[:-1]

    @staticmethod
    def _clean_title(value: Any) -> str:
        """Create a safe YouTube title."""

        title = YouTubeUploader._safe_string(
            value,
            "Sofia Luxury Technology & Lifestyle"
        )

        title = title.replace("\n", " ")
        title = title.replace("\r", " ")
        title = " ".join(title.split())

        # Remove characters that can cause malformed metadata.
        title = title.replace("<", "")
        title = title.replace(">", "")

        title = title.strip()

        if not title:
            title = "Sofia Luxury Technology & Lifestyle"

        return YouTubeUploader._limit_utf8(
            title,
            100
        )

    @staticmethod
    def _clean_description(value: Any) -> str:
        """Create a safe YouTube description."""

        description = YouTubeUploader._safe_string(
            value,
            "Welcome to Sofia Luxury — technology, lifestyle and luxury stories."
        )

        description = description.replace(
            "\x00",
            ""
        )

        description = description.replace(
            "\r\n",
            "\n"
        )

        description = description.replace(
            "\r",
            "\n"
        )

        # Remove null/control characters except normal newlines/tabs.
        description = "".join(
            char
            for char in description
            if char in ("\n", "\t")
            or ord(char) >= 32
        )

        description = description.replace(
            "\x00",
            ""
        )

        description = YouTubeUploader._limit_utf8(
            description,
            5000
        )

        return description.strip()

    @staticmethod
    def _clean_tags(value: Any) -> list:
        """
        Convert AI-generated tags into safe simple strings.

        YouTube can reject invalid tags, so only clean strings
        are allowed through.
        """

        if not isinstance(value, list):
            return []

        cleaned = []

        for item in value:
            if isinstance(item, dict):
                item = (
                    item.get("tag")
                    or item.get("name")
                    or item.get("value")
                    or ""
                )

            if not isinstance(item, str):
                continue

            tag = item.strip()

            if not tag:
                continue

            # Remove hashtag marker.
            if tag.startswith("#"):
                tag = tag[1:].strip()

            # Remove line breaks.
            tag = tag.replace("\n", " ")
            tag = tag.replace("\r", " ")

            # Remove control characters.
            tag = "".join(
                char
                for char in tag
                if ord(char) >= 32
            )

            tag = " ".join(tag.split())

            if not tag:
                continue

            # Individual tags should stay reasonably short.
            tag = YouTubeUploader._limit_utf8(
                tag,
                100
            ).strip()

            if not tag:
                continue

            # Avoid duplicates.
            if tag.lower() not in {
                existing.lower()
                for existing in cleaned
            }:
                cleaned.append(tag)

        # Keep metadata conservative.
        cleaned = cleaned[:15]

        # YouTube's tag metadata has a total character limit.
        final_tags = []
        total_bytes = 0

        for tag in cleaned:
            tag_bytes = len(
                tag.encode("utf-8")
            )

            # Account for commas between tags.
            extra = 1 if final_tags else 0

            if total_bytes + extra + tag_bytes > 450:
                break

            final_tags.append(tag)

            total_bytes += extra + tag_bytes

        return final_tags

    @staticmethod
    def _safe_privacy(value: Any) -> str:
        """Return a valid YouTube privacy value."""

        privacy = str(
            value or "private"
        ).lower().strip()

        if privacy not in (
            "private",
            "unlisted",
            "public"
        ):
            return "private"

        return privacy

    # ============================================================
    # UPLOAD
    # ============================================================

    def upload_video(
        self,
        video_path: str,
        metadata: Dict,
        privacy: str = "private"
    ) -> Dict:
        """Upload a video to YouTube with validated metadata."""

        if not self.authenticated:
            if not self.authenticate():
                return {
                    "error": "YouTube authentication failed"
                }

        if not self.youtube:
            logger.error("❌ Not authenticated")
            return {
                "error": "Not authenticated"
            }

        video_file = Path(video_path)

        if not video_file.exists():
            logger.error(
                f"❌ Video not found: {video_path}"
            )

            return {
                "error": "Video file not found"
            }

        if video_file.stat().st_size == 0:
            logger.error(
                "❌ Video file is empty"
            )

            return {
                "error": "Video file is empty"
            }

        logger.info(
            f"📤 Uploading: {video_file.name}..."
        )

        # --------------------------------------------------------
        # CLEAN AI-GENERATED SEO DATA
        # --------------------------------------------------------

        if not isinstance(metadata, dict):
            metadata = {}

        title = self._clean_title(
            metadata.get("best_title")
            or metadata.get("title")
            or metadata.get("topic")
        )

        description = self._clean_description(
            metadata.get("description")
        )

        tags = self._clean_tags(
            metadata.get("tags")
        )

        privacy_status = self._safe_privacy(
            privacy
        )

        # Use a known YouTube category.
        # 28 = Science & Technology.
        category_id = "28"

        # --------------------------------------------------------
        # BUILD SAFE REQUEST
        # --------------------------------------------------------

        snippet = {
            "title": title,
            "description": description,
            "categoryId": category_id,
            "defaultLanguage": "en",
        }

        # Only add tags if there are actually valid tags.
        # This prevents empty/invalid tag metadata from breaking
        # the entire upload.
        if tags:
            snippet["tags"] = tags

        body = {
            "snippet": snippet,
            "status": {
                "privacyStatus": privacy_status,
                "selfDeclaredMadeForKids": False,
            }
        }

        logger.info(
            "📋 YouTube metadata validated:"
        )

        logger.info(
            f"   Title: {title}"
        )

        logger.info(
            f"   Category: {category_id}"
        )

        logger.info(
            f"   Language: en"
        )

        logger.info(
            f"   Tags: {len(tags)}"
        )

        logger.info(
            f"   Privacy: {privacy_status}"
        )

        try:
            # ----------------------------------------------------
            # CREATE MEDIA UPLOAD
            # ----------------------------------------------------

            media = MediaFileUpload(
                str(video_file),
                mimetype="video/mp4",
                resumable=True
            )

            # ----------------------------------------------------
            # INSERT VIDEO
            # ----------------------------------------------------

            request = self.youtube.videos().insert(
                part="snippet,status",
                body=body,
                media_body=media
            )

            logger.info(
                "⏳ Uploading video to YouTube..."
            )

            response = None

            while response is None:
                status, response = request.next_chunk()

                if status:
                    progress = int(
                        status.progress() * 100
                    )

                    logger.info(
                        f"   Upload progress: {progress}%"
                    )

            video_id = response.get("id")

            if not video_id:
                logger.error(
                    f"❌ YouTube returned no video ID: {response}"
                )

                return {
                    "error": "YouTube returned no video ID"
                }

            video_url = (
                f"https://youtube.com/watch?v={video_id}"
            )

            logger.info(
                "✅ Upload complete!"
            )

            logger.info(
                f"   Video ID: {video_id}"
            )

            logger.info(
                f"   URL: {video_url}"
            )

            return {
                "success": True,
                "video_id": video_id,
                "url": video_url,
                "title": title
            }

        except Exception as e:
            logger.error(
                f"❌ Upload failed: {e}"
            )

            return {
                "error": str(e)
            }

    # ============================================================
    # THUMBNAIL
    # ============================================================

    def set_thumbnail(
        self,
        video_id: str,
        thumbnail_path: str
    ) -> bool:
        """Set custom thumbnail for a video."""

        if not self.youtube:
            logger.error(
                "❌ Not authenticated"
            )
            return False

        thumbnail = Path(thumbnail_path)

        if not thumbnail.exists():
            logger.error(
                f"❌ Thumbnail not found: {thumbnail_path}"
            )
            return False

        try:
            self.youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(
                    str(thumbnail)
                )
            ).execute()

            logger.info(
                f"🖼️ Thumbnail set for video: {video_id}"
            )

            return True

        except Exception as e:
            logger.error(
                f"❌ Thumbnail upload failed: {e}"
            )

            return False

    # ============================================================
    # CHANNEL INFO
    # ============================================================

    def get_channel_info(self) -> Dict:
        """Get YouTube channel statistics."""

        if not self.authenticated:
            if not self.authenticate():
                return {
                    "title": "Unknown",
                    "subscribers": "N/A"
                }

        try:
            request = self.youtube.channels().list(
                part="snippet,statistics",
                mine=True
            )

            response = request.execute()

            if response.get("items"):
                channel = response["items"][0]

                return {
                    "title": channel["snippet"]["title"],
                    "subscribers": channel[
                        "statistics"
                    ].get(
                        "subscriberCount",
                        "Hidden"
                    ),
                    "views": channel[
                        "statistics"
                    ].get(
                        "viewCount",
                        "0"
                    ),
                    "videos": channel[
                        "statistics"
                    ].get(
                        "videoCount",
                        "0"
                    ),
                }

        except Exception as e:
            logger.error(
                f"❌ Could not get channel info: {e}"
            )

        return {
            "title": "Unknown",
            "subscribers": "N/A"
        }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("\n" + "=" * 60)
    print("📤  YOUTUBE UPLOADER TEST")
    print("=" * 60)

    uploader = YouTubeUploader()

    print("\n🔐 Testing authentication...")

    if uploader.authenticate():

        print(
            "✅ Authentication successful!"
        )

        test_video = (
            "output/test_video.mp4"
        )

        if Path(test_video).exists():

            print(
                f"\n✅ Found test video: {test_video}"
            )

            metadata = {
                "topic": (
                    "Latest luxury technology "
                    "and lifestyle trends"
                ),
                "best_title": (
                    "Latest Luxury Technology "
                    "and Lifestyle Trends"
                ),
                "description": (
                    "Discover the latest luxury "
                    "technology and lifestyle trends."
                ),
                "tags": [
                    "luxury technology",
                    "technology",
                    "lifestyle",
                    "luxury"
                ],
                "language": "en"
            }

            print("\n📋 Ready to upload:")

            print(
                f"   Title: "
                f"{metadata['best_title']}"
            )

            print(
                f"   Tags: "
                f"{len(metadata['tags'])}"
            )

            choice = input(
                "\nUpload test video? (y/n): "
            ).strip().lower()

            if choice == "y":

                result = uploader.upload_video(
                    video_path=test_video,
                    metadata=metadata,
                    privacy="private"
                )

                if result.get("success"):

                    print(
                        "\n🎉 Video uploaded successfully!"
                    )

                    print(
                        f"   URL: "
                        f"{result.get('url')}"
                    )

                else:

                    print(
                        "\n❌ Upload failed:"
                    )

                    print(
                        result.get("error")
                    )

            else:
                print(
                    "\n❌ Upload cancelled"
                )

        else:

            print(
                f"\n⚠️ Test video not found: "
                f"{test_video}"
            )

    else:

        print(
            "❌ Authentication failed"
        )

    print(
        "\n" + "=" * 60
    )
