"""
Luxury Music Video Studio
Builds a user's photo + luxury references + song into a ComfyUI/LTX job.

This module deliberately does NOT contain commercial or leaked API keys.
It talks to a self-hosted ComfyUI instance, so generation is controlled by
the owner of this repository.
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
        endpoint = "image" if kind == "image" else "mask"
        with path.open("rb") as fh:
            files = {"image": (path.name, fh)}
            data = {"type": "input", "overwrite": "true"}
            r = requests.post(
                f"{self.base_url}/upload/{endpoint}",
                files=files,
                data=data,
                timeout=self.timeout,
            )
        if not r.ok:
            raise LuxuryVideoError(f"ComfyUI upload failed: {r.status_code} {r.text[:500]}")
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
            raise LuxuryVideoError(f"ComfyUI queue failed: {r.status_code} {r.text[:1000]}")
        payload = r.json()
        if payload.get("error"):
            raise LuxuryVideoError(json.dumps(payload, indent=2))
        prompt_id = payload.get("prompt_id")
        if not prompt_id:
            raise LuxuryVideoError(f"ComfyUI returned no prompt_id: {payload}")
        return prompt_id

    def wait_for_history(self, prompt_id: str, poll_seconds: float = 2.0, timeout: int = 3600) -> Dict[str, Any]:
        started = time.time()
        while time.time() - started < timeout:
            r = requests.get(f"{self.base_url}/history/{prompt_id}", timeout=self.timeout)
            if r.ok:
                history = r.json()
                if prompt_id in history:
                    return history[prompt_id]
            time.sleep(poll_seconds)
        raise LuxuryVideoError(f"Timed out waiting for ComfyUI job {prompt_id}")

    def output_url(self, filename: str, subfolder: str = "", folder_type: str = "output") -> str:
        from urllib.parse import urlencode
        query = urlencode({"filename": filename, "subfolder": subfolder, "type": folder_type})
        return f"{self.base_url}/view?{query}"


def load_workflow(path: str | Path = DEFAULT_WORKFLOW) -> Dict[str, Any]:
    path = Path(path)
    if not path.exists():
        raise LuxuryVideoError(
            f"Workflow not found: {path}. Export an API-format ComfyUI workflow "
            "and save it at this path."
        )
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _class_nodes(workflow: Dict[str, Any], class_name: str) -> Iterable[tuple[str, Dict[str, Any]]]:
    for node_id, node in workflow.items():
        if node.get("class_type") == class_name:
            yield node_id, node


def _set_first_input(workflow: Dict[str, Any], class_name: str, key: str, value: Any) -> bool:
    for _, node in _class_nodes(workflow, class_name):
        node.setdefault("inputs", {})[key] = value
        return True
    return False


def prepare_workflow(
    workflow: Dict[str, Any],
    *,
    subject_image: str,
    reference_images: list[str],
    prompt: str,
    seed: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Adapt a user-exported ComfyUI API workflow.

    The exact node graph is intentionally supplied by the user's installed
    LTX/ComfyUI workflow; this adapter only changes common LoadImage/text/seed
    fields when those nodes exist.
    """
    wf = copy.deepcopy(workflow)
    _set_first_input(wf, "LoadImage", "image", subject_image)

    # If the exported workflow has multiple LoadImage nodes, fill the remaining
    # ones with the provided luxury references.
    loaders = list(_class_nodes(wf, "LoadImage"))
    for index, (_, node) in enumerate(loaders[1:], start=0):
        if index < len(reference_images):
            node.setdefault("inputs", {})["image"] = reference_images[index]

    for text_node in ("CLIPTextEncode", "CLIPTextEncodeSDXL", "CLIPTextEncodeFlux"):
        for _, node in _class_nodes(wf, text_node):
            text = str(node.get("inputs", {}).get("text", ""))
            if text == "" or "luxury music video" in text.lower():
                node.setdefault("inputs", {})["text"] = prompt

    if seed is not None:
        for _, node in _class_nodes(wf, "KSampler"):
            node.setdefault("inputs", {})["seed"] = int(seed)

    return wf


def create_job_manifest(
    subject_image: str,
    reference_images: list[str],
    music_file: str,
    duration_seconds: int,
    prompt: str,
) -> Dict[str, Any]:
    return {
        "project": "Luxury Music Video Studio",
        "duration_seconds": int(duration_seconds),
        "subject_image": subject_image,
        "reference_images": reference_images,
        "music_file": music_file,
        "prompt": prompt,
        "generation": {
            "strategy": "short cinematic shots assembled into one music video",
            "identity": "preserve the supplied subject identity",
            "style": "photorealistic, premium luxury, cinematic",
            "audio": "use the supplied music as the final soundtrack",
        },
    }
