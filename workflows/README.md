# Luxury Music Video Workflow

This directory is reserved for the **API-format ComfyUI workflow** used by the Luxury Music Video Studio.

## Required file

Save the exported ComfyUI API workflow as:

`workflows/luxury_music_video_api.json`

In ComfyUI, build/import the LTX image-to-video workflow and use **File → Export (API)**. The project then submits that JSON to the owner's self-hosted ComfyUI instance.

The application deliberately does not embed a commercial or leaked API key.

The workflow should contain the image-conditioning and video-generation nodes needed by the installed LTX/ComfyUI setup. The adapter looks for common `LoadImage`, text-encoding and `KSampler` nodes and fills their inputs when present.

Official ComfyUI examples document the `/prompt` API and API-format workflow export. The official LTX-Video project recommends its ComfyUI workflow for best output fidelity.
