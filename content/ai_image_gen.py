"""
SOFIA LUXURY STORY
MEDIA RESOLVER

No AI image generation.

Priority:
1. User library assets
2. Sofia reference
3. Pexels videos
4. Pexels photos
"""

import os
import re
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any

import requests
from loguru import logger


PROJECT_ROOT = Path(__file__).resolve().parents[1]

SOFIA_REFERENCE = (
    PROJECT_ROOT
    / "assets"
    / "sofia"
    / "sofia_reference.jpg"
)

LOCAL_LIBRARY = (
    PROJECT_ROOT
    / "assets"
    / "library"
)

OUTPUT_MEDIA = (
    PROJECT_ROOT
    / "output"
    / "media"
)

PEXELS_API_KEY = os.getenv(
    "PEXELS_API_KEY",
    ""
)

PEXELS_PHOTO_SEARCH = (
    "https://api.pexels.com/v1/search"
)

PEXELS_VIDEO_SEARCH = (
    "https://api.pexels.com/v1/videos/search"
)

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
}

VIDEO_EXTENSIONS = {
    ".mp4",
    ".mov",
    ".m4v",
    ".webm",
}


class AIImageGenerator:

    def __init__(
        self,
        output_dir: str = "output/images"
    ):

        self.output_dir = Path(
            output_dir
        )

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        LOCAL_LIBRARY.mkdir(
            parents=True,
            exist_ok=True
        )

        OUTPUT_MEDIA.mkdir(
            parents=True,
            exist_ok=True
        )

        self.pexels_key = (
            os.getenv("PEXELS_API_KEY")
            or PEXELS_API_KEY
            or ""
        )

        self.local_assets = (
            self._scan_local_assets()
        )

        logger.info(
            "SOFIA MEDIA RESOLVER INITIALIZED"
        )

        logger.info(
            f"Local library assets: "
            f"{len(self.local_assets)}"
        )

        if SOFIA_REFERENCE.exists():

            logger.info(
                "Sofia reference found."
            )

        else:

            logger.warning(
                "Sofia reference not found."
            )

        if self.pexels_key:

            logger.info(
                "Pexels API available."
            )

        else:

            logger.warning(
                "PEXELS_API_KEY not available."
            )

    # =========================================================
    # LOCAL ASSETS
    # =========================================================

    def _scan_local_assets(
        self
    ) -> List[Path]:

        assets = []

        if not LOCAL_LIBRARY.exists():
            return assets

        for path in LOCAL_LIBRARY.rglob("*"):

            if not path.is_file():
                continue

            if path.suffix.lower() in (
                IMAGE_EXTENSIONS
                | VIDEO_EXTENSIONS
            ):

                assets.append(path)

        return sorted(
            assets,
            key=lambda p:
                p.name.lower()
        )

    # =========================================================
    # TEXT HELPERS
    # =========================================================

    def _text(
        self,
        value: Any
    ) -> str:

        if value is None:
            return ""

        return str(value).strip()

    def _clean_query(
        self,
        text: str
    ) -> str:

        text = re.sub(
            r"[^a-zA-Z0-9\s-]",
            " ",
            text
        )

        text = " ".join(
            text.split()
        )

        return text[:120]

    # =========================================================
    # SEARCH QUERY
    # =========================================================

    def make_search_query(
        self,
        scene: Dict[str, Any]
    ) -> str:

        explicit = (
            scene.get("pexels_query")
            or scene.get("visual_search")
            or scene.get("search_keywords")
        )

        if explicit:

            query = self._text(
                explicit
            )

            if query:
                return self._clean_query(
                    query
                )

        parts = [
            self._text(
                scene.get("location")
            ),
            self._text(
                scene.get("action")
            ),
            self._text(
                scene.get("luxury_detail")
            ),
        ]

        combined = " ".join(
            part
            for part in parts
            if part
        )

        words = combined.split()

        query = " ".join(
            words[:14]
        )

        query = self._clean_query(
            query
        )

        if not query:

            query = (
                "luxury lifestyle "
                "cinematic"
            )

        return query

    # =========================================================
    # SOFIA DETECTION
    # =========================================================

    def scene_needs_sofia(
        self,
        scene: Dict[str, Any]
    ) -> bool:

        explicit = scene.get(
            "sofia_visible"
        )

        if explicit is not None:
            return bool(explicit)

        visual_type = self._text(
            scene.get("visual_type")
        ).lower()

        if visual_type == "sofia":
            return True

        text = " ".join([
            self._text(
                scene.get("action")
            ),
            self._text(
                scene.get("visual_prompt")
            ),
            self._text(
                scene.get("narration")
            ),
        ]).lower()

        return any(
            word in text
            for word in [
                "sofia",
                "she",
                "her",
                "woman",
            ]
        )

    # =========================================================
    # LOCAL ASSET MATCHING
    # =========================================================

    def _asset_score(
        self,
        path: Path,
        query: str
    ) -> int:

        filename = path.stem.lower()

        query_words = {
            word.lower()
            for word in query.split()
            if len(word) >= 4
        }

        score = 0

        for word in query_words:

            if word in filename:
                score += 3

        return score

    def find_local_asset(
        self,
        scene: Dict[str, Any]
    ) -> str:

        if not self.local_assets:
            return ""

        query = self.make_search_query(
            scene
        )

        ranked = []

        for path in self.local_assets:

            score = self._asset_score(
                path,
                query
            )

            ranked.append(
                (
                    score,
                    path
                )
            )

        ranked.sort(
            key=lambda item: (
                item[0],
                item[1].name.lower()
            ),
            reverse=True
        )

        best_score, best_path = ranked[0]

        if best_score <= 0:
            return ""

        logger.info(
            f"Local asset selected: "
            f"{best_path.name}"
        )

        return str(best_path)

    # =========================================================
    # SOFIA REFERENCE
    # =========================================================

    def get_sofia_reference(
        self
    ) -> str:

        if SOFIA_REFERENCE.exists():

            return str(
                SOFIA_REFERENCE
            )

        return ""

    # =========================================================
    # PEXELS HEADERS
    # =========================================================

    def _pexels_headers(
        self
    ) -> Dict[str, str]:

        return {
            "Authorization":
                self.pexels_key,
            "User-Agent":
                "Sofia-Luxury-Story/1.0",
        }

    # =========================================================
    # SAFE FILE NAME
    # =========================================================

    def _safe_filename(
        self,
        prefix: str,
        query: str,
        extension: str
    ) -> str:

        digest = hashlib.md5(
            query.encode("utf-8")
        ).hexdigest()[:12]

        return (
            f"{prefix}_{digest}"
            f"{extension}"
        )

    # =========================================================
    # DOWNLOAD
    # =========================================================

    def _download(
        self,
        url: str,
        destination: Path
    ) -> bool:

        try:

            response = requests.get(
                url,
                timeout=30,
                stream=True
            )

            if response.status_code != 200:

                logger.warning(
                    "Media download failed: "
                    f"{response.status_code}"
                )

                return False

            destination.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            with open(
                destination,
                "wb"
            ) as output:

                for chunk in response.iter_content(
                    chunk_size=1024 * 1024
                ):

                    if chunk:
                        output.write(chunk)

            return (
                destination.exists()
                and destination.stat().st_size
                > 5000
            )

        except Exception as exc:

            logger.warning(
                f"Download failed: {exc}"
            )

            return False

    # =========================================================
    # PEXELS PHOTO
    # =========================================================

    def search_pexels_photo(
        self,
        query: str,
        index: int = 0
    ) -> str:

        if not self.pexels_key:
            return ""

        query = self._clean_query(
            query
        )

        try:

            response = requests.get(
                PEXELS_PHOTO_SEARCH,
                headers=self._pexels_headers(),
                params={
                    "query": query,
                    "orientation": "portrait",
                    "size": "medium",
                    "per_page": 8,
                    "page": 1,
                },
                timeout=15
            )

            if response.status_code != 200:

                logger.warning(
                    "Pexels photo search failed: "
                    f"{response.status_code}"
                )

                return ""

            data = response.json()

            photos = data.get(
                "photos",
                []
            )

            if not photos:
                return ""

            photo = photos[
                index % len(photos)
            ]

            src = photo.get(
                "src",
                {}
            )

            image_url = (
                src.get("portrait")
                or src.get("large")
                or src.get("medium")
            )

            if not image_url:
                return ""

            filename = self._safe_filename(
                "pexels_photo",
                f"{query}_{index}",
                ".jpg"
            )

            destination = (
                OUTPUT_MEDIA
                / filename
            )

            if not destination.exists():

                if not self._download(
                    image_url,
                    destination
                ):
                    return ""

            self._save_attribution(
                photo=photo,
                media_type="photo"
            )

            logger.info(
                "Pexels photo selected: "
                f"{photo.get('id')}"
            )

            return str(destination)

        except Exception as exc:

            logger.warning(
                f"Pexels photo search error: "
                f"{exc}"
            )

            return ""

    # =========================================================
    # PEXELS VIDEO
    # =========================================================

    def search_pexels_video(
        self,
        query: str,
        index: int = 0
    ) -> str:

        if not self.pexels_key:
            return ""

        query = self._clean_query(
            query
        )

        try:

            response = requests.get(
                PEXELS_VIDEO_SEARCH,
                headers=self._pexels_headers(),
                params={
                    "query": query,
                    "orientation": "portrait",
                    "size": "medium",
                    "per_page": 8,
                    "page": 1,
                },
                timeout=15
            )

            if response.status_code != 200:

                logger.warning(
                    "Pexels video search failed: "
                    f"{response.status_code}"
                )

                return ""

            data = response.json()

            videos = data.get(
                "videos",
                []
            )

            if not videos:
                return ""

            video = videos[
                index % len(videos)
            ]

            files = video.get(
                "video_files",
                []
            )

            if not files:
                return ""

            portrait_files = [
                item
                for item in files
                if (
                    item.get("width", 0)
                    < item.get("height", 0)
                )
            ]

            candidates = (
                portrait_files
                or files
            )

            candidates.sort(
                key=lambda item:
                    item.get(
                        "width",
                        0
                    ),
                reverse=True
            )

            video_file = candidates[0]

            video_url = video_file.get(
                "link"
            )

            if not video_url:
                return ""

            filename = self._safe_filename(
                "pexels_video",
                f"{query}_{index}",
                ".mp4"
            )

            destination = (
                OUTPUT_MEDIA
                / filename
            )

            if not destination.exists():

                if not self._download(
                    video_url,
                    destination
                ):
                    return ""

            self._save_attribution(
                video=video,
                media_type="video"
            )

            logger.info(
                "Pexels video selected: "
                f"{video.get('id')}"
            )

            return str(destination)

        except Exception as exc:

            logger.warning(
                f"Pexels video search error: "
                f"{exc}"
            )

            return ""

    # =========================================================
    # ATTRIBUTION
    # =========================================================

    def _save_attribution(
        self,
        photo: Optional[Dict[str, Any]] = None,
        video: Optional[Dict[str, Any]] = None,
        media_type: str = ""
    ):

        attribution_file = (
            OUTPUT_MEDIA
            / "pexels_attribution.json"
        )

        try:

            if attribution_file.exists():

                existing = json.loads(
                    attribution_file.read_text(
                        encoding="utf-8"
                    )
                )

            else:

                existing = []

            item = {
                "type": media_type
            }

            if photo:

                item.update({
                    "id":
                        photo.get("id"),
                    "url":
                        photo.get("url"),
                    "photographer":
                        photo.get(
                            "photographer"
                        ),
                    "photographer_url":
                        photo.get(
                            "photographer_url"
                        ),
                })

            if video:

                item.update({
                    "id":
                        video.get("id"),
                    "url":
                        video.get("url"),
                })

            existing.append(item)

            unique = []

            seen = set()

            for entry in existing:

                key = (
                    entry.get("type"),
                    entry.get("id")
                )

                if key in seen:
                    continue

                seen.add(key)
                unique.append(entry)

            attribution_file.write_text(
                json.dumps(
                    unique,
                    indent=2,
                    ensure_ascii=False
                ),
                encoding="utf-8"
            )

        except Exception as exc:

            logger.warning(
                f"Attribution save failed: "
                f"{exc}"
            )

    # =========================================================
    # MAIN MEDIA RESOLVER
    # =========================================================

    def resolve_scene_media(
        self,
        scene: Dict[str, Any],
        index: int = 0
    ) -> Dict[str, Any]:

        query = self.make_search_query(
            scene
        )

        needs_sofia = (
            self.scene_needs_sofia(
                scene
            )
        )

        # -----------------------------------------------------
        # 1. USER LIBRARY
        # -----------------------------------------------------

        local_asset = (
            self.find_local_asset(
                scene
            )
        )

        if local_asset:

            asset_type = (
                "video"
                if Path(
                    local_asset
                ).suffix.lower()
                in VIDEO_EXTENSIONS
                else "image"
            )

            return {
                "path":
                    local_asset,
                "type":
                    asset_type,
                "source":
                    "local",
                "query":
                    query,
            }

        # -----------------------------------------------------
        # 2. SOFIA REFERENCE
        # -----------------------------------------------------

        if needs_sofia:

            sofia = (
                self.get_sofia_reference()
            )

            if sofia:

                return {
                    "path":
                        sofia,
                    "type":
                        "image",
                    "source":
                        "sofia_reference",
                    "query":
                        query,
                }

        # -----------------------------------------------------
        # 3. PEXELS VIDEO
        # -----------------------------------------------------

        video = (
            self.search_pexels_video(
                query,
                index
            )
        )

        if video:

            return {
                "path":
                    video,
                "type":
                    "video",
                "source":
                    "pexels",
                "query":
                    query,
            }

        # -----------------------------------------------------
        # 4. PEXELS PHOTO
        # -----------------------------------------------------

        photo = (
            self.search_pexels_photo(
                query,
                index
            )
        )

        if photo:

            return {
                "path":
                    photo,
                "type":
                    "image",
                "source":
                    "pexels",
                "query":
                    query,
            }

        return {
            "path": "",
            "type": "",
            "source": "",
            "query": query,
        }

    # =========================================================
    # COMPATIBILITY METHOD
    # =========================================================

    def generate_image(
        self,
        prompt: str = "",
        style: str = "",
        width: int = 720,
        height: int = 1280,
        filename: str = "",
        use_reference: bool = False,
        scene_number: int = 0,
        **kwargs
    ) -> str:

        if use_reference:

            return self.get_sofia_reference()

        return ""
