# Luxury Music Video Workflow

The repository now includes:

`workflows/luxury_music_video_api.json`

It is an API-format ComfyUI graph based on an open LTX-2.3 image-to-video/audio workflow. It is designed for short cinematic shots that the app assembles into a 1–3 minute master.

## What it does

- Uses the uploaded main photo as the identity/start frame.
- Conditions the LTX generation with the uploaded music.
- Generates short cinematic shots with different seeds.
- The app repeats the workflow for the requested duration.
- FFmpeg joins the shots and replaces generated audio with the user's original music.
- No commercial video API key is embedded.

## GPU server requirements

The GPU machine must have:

1. ComfyUI installed and reachable by HTTP.
2. The LTX-2.3 compatible nodes/custom nodes required by the workflow.
3. The LTX-2.3 model files referenced by the workflow.
4. FFmpeg installed on the same machine running this Streamlit app.
5. Enough GPU VRAM and disk space for the selected LTX workflow.

The exact model/node requirements can change with the installed ComfyUI/LTX version, so use the matching official LTX workflow files rather than mixing versions.

## ComfyUI URL

Set:

`COMFYUI_URL=http://127.0.0.1:8188`

when the app and ComfyUI run on the same machine.

If ComfyUI runs on another GPU machine, enter that machine's reachable ComfyUI URL in the app.

## Important

This is self-hosted generation. GitHub itself does not provide a free GPU for the video model. The GitHub repository contains the application and workflow; the actual model inference runs on the GPU server you connect to it.
