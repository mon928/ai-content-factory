"""
Luxury Music Video Studio
Builds a user's photo + luxury references + song into cinematic LTX jobs.

Generation is self-hosted through ComfyUI. No commercial or leaked API keys are
used. The workflow is an API-format LTX-2.3 workflow with audio conditioning.
"""
from __future__ import annotations

import copy
import json
import os
import time
import uuid
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

import requests


DEFAULT_COMFY_URL = os.getenv("COMFYUI_URL", "http://127.0.0.1:8188").rstrip("/")
DEFAULT_WORKFLOW = os.getenv(
    "LUXURY_WORKFLOW_JSON",
    "workflows/luxury_music_video_api.json",
)


class LuxuryVideoError(RuntimeError):
    pass


class ComfyUIClient:
    """Small client for the self-hosted ComfyUI HTTP API."""

    def __init__(self, base_url: str = DEFAULT_COMFY_URL, timeout: int = 60):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def health(self) -> bool:
        try:
            r = requests.get(f"{self.base_url}/system_stats", timeout=10)
            return r.ok
        except requests.RequestException:
            return False

    def upload_file(self, path: str | Path, kind: str = "image") -> str:
        path = Path(path)
        if not path.exists():
            raise LuxuryVideoError(f"Input file not found: {path}")
        # ComfyUI's upload endpoint accepts images; audio is also accepted by
        # the same multipart input route on current ComfyUI builds.
        with path.open("rb") as fh:
            files = {"image": (path.name, fh)}
            data = {"type": "input", "overwrite": "true"}
            r = requests.post(
                f"{self.base_url}/upload/image",
                files=files,
                data=data,
                timeout=self.timeout,
            )
        if not r.ok:
            raise LuxuryVideoError(
                f"ComfyUI upload failed: {r.status_code} {r.text[:500]}"
            )
        payload = r.json()
        return payload.get("name", path.name)

    def queue(self, workflow: Dict[str, Any]) -> str:
        client_id = str(uuid.uuid4())
        r = requests.post(
            f"{self.base_url}/prompt",
            json={"prompt": workflow, "client_id": client_id},
            timeout=self.timeout,
        )
        if not r.ok:
            raise LuxuryVideoError(
                f"ComfyUI queue failed: {r.status_code} {r.text[:1000]}"
            )
        payload = r.json()
        if payload.get("error"):
            raise LuxuryVideoError(json.dumps(payload, indent=2))
        prompt_id = payload.get("prompt_id")
        if not prompt_id:
            raise LuxuryVideoError(f"ComfyUI returned no prompt_id: {payload}")
        return prompt_id

    def wait_for_history(
        self, prompt_id: str, poll_seconds: float = 2.0, timeout: int = 3600
    ) -> Dict[str, Any]:
        started = time.time()
        while time.time() - started < timeout:
            r = requests.get(
                f"{self.base_url}/history/{prompt_id}", timeout=self.timeout
            )
            if r.ok:
                history = r.json()
                if prompt_id in history:
                    item = history[prompt_id]
                    status = item.get("status", {})
                    if status.get("status_str") == "error":
                        raise LuxuryVideoError(
                            f"ComfyUI generation failed: {json.dumps(item, indent=2)[:3000]}"
                        )
                    return item
            time.sleep(poll_seconds)
        raise LuxuryVideoError(f"Timed out waiting for ComfyUI job {prompt_id}")

    def output_url(
        self, filename: str, subfolder: str = "", folder_type: str = "output"
    ) -> str:
        from urllib.parse import urlencode

        query = urlencode(
            {"filename": filename, "subfolder": subfolder, "type": folder_type}
        )
        return f"{self.base_url}/view?{query}"

    def download_url(self, url: str, destination: str | Path) -> Path:
        destination = Path(destination)
        with requests.get(url, stream=True, timeout=120) as r:
            r.raise_for_status()
            with destination.open("wb") as fh:
                for chunk in r.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        fh.write(chunk)
        return destination


def load_workflow(path: str | Path = DEFAULT_WORKFLOW) -> Dict[str, Any]:
    path = Path(path)
    if not path.exists():
        raise LuxuryVideoError(
            f"Workflow not found: {path}. The repository should contain "
            "workflows/luxury_music_video_api.json."
        )
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _class_nodes(
    workflow: Dict[str, Any], class_name: str
) -> Iterable[tuple[str, Dict[str, Any]]]:
    for node_id, node in workflow.items():
        if node.get("class_type") == class_name:
            yield node_id, node


def _set_first_input(
    workflow: Dict[str, Any], class_name: str, key: str, value: Any
) -> bool:
    for _, node in _class_nodes(workflow, class_name):
        node.setdefault("inputs", {})[key] = value
        return True
    return False


def prepare_workflow(
    workflow: Dict[str, Any],
    *,
    subject_image: str,
    reference_images: list[str],
    music_file: str,
    prompt: str,
    seed: Optional[int] = None,
    width: int = 832,
    height: int = 480,
    frames: int = 105,
    audio_duration: float = 20.0,
) -> Dict[str, Any]:
    """
    Adapt the checked-in LTX-2.3 API workflow for one cinematic shot.

    The model generates a short shot. The application repeats the shot with
    different seeds and then FFmpeg assembles the shots into the requested
    1/2/3-minute master while replacing generated audio with the user's
    original music.
    """
    wf = copy.deepcopy(workflow)

    _set_first_input(wf, "LoadImage", "image", subject_image)
    _set_first_input(wf, "LoadAudio", "audio", music_file)

    # Fill any additional image inputs if a future workflow exposes them.
    loaders = list(_class_nodes(wf, "LoadImage"))
    for index, (_, node) in enumerate(loaders[1:], start=0):
        if index < len(reference_images):
            node.setdefault("inputs", {})["image"] = reference_images[index]

    text_nodes = list(_class_nodes(wf, "CLIPTextEncode"))
    for index, (_, node) in enumerate(text_nodes):
        if index == 0:
            node.setdefault("inputs", {})["text"] = prompt

    if seed is not None:
        for _, node in _class_nodes(wf, "RandomNoise"):
            node.setdefault("inputs", {})["noise_seed"] = int(seed)

    # Keep every stage synchronized to the same shot length.
    for _, node in _class_nodes(wf, "EmptyLTXVLatentVideo"):
        node.setdefault("inputs", {})["width"] = int(width)
        node.setdefault("inputs", {})["height"] = int(height)
        node.setdefault("inputs", {})["length"] = int(frames)
    for _, node in _class_nodes(wf, "LTXVEmptyLatentAudio"):
        node.setdefault("inputs", {})["frames_number"] = int(frames)
    for _, node in _class_nodes(wf, "TrimAudioDuration"):
        node.setdefault("inputs", {})["duration"] = float(audio_duration)

    return wf


def create_job_manifest(
    subject_image: str,
    reference_images: list[str],
    music_file: str,
    duration_seconds: int,
    prompt: str,
) -> Dict[str, Any]:
    shots = max(1, (int(duration_seconds) + 3) // 4)
    return {
        "project": "Luxury Music Video Studio",
        "duration_seconds": int(duration_seconds),
        "planned_shots": shots,
        "subject_image": subject_image,
        "reference_images": reference_images,
        "music_file": music_file,
        "prompt": prompt,
        "generation": {
            "strategy": "short LTX cinematic shots with varied seeds, then FFmpeg assembly",
            "identity": "preserve the supplied subject identity",
            "style": "photorealistic, premium luxury, cinematic",
            "performance": "audio-conditioned singing/lip-sync attempt from the supplied track",
            "final_audio": "replace generated audio with the user's original music track",
        },
    }


def find_video_outputs(history: Dict[str, Any]) -> list[Dict[str, str]]:
    """Extract video-like ComfyUI output records from a completed history item."""
    found: list[Dict[str, str]] = []
    outputs = history.get("outputs", {})
    for node_output in outputs.values():
        for key in ("gifs", "videos", "video", "files"):
            items = node_output.get(key, [])
            if isinstance(items, dict):
                items = [items]
            if not isinstance(items, list):
                continue
            for item in items:
                if not isinstance(item, dict):
                    continue
                filename = item.get("filename")
                if filename:
                    found.append(
                        {
                            "filename": filename,
                            "subfolder": item.get("subfolder", ""),
                            "type": item.get("type", "output"),
                        }
                    )
    return found
