"""
🌐 AI CONTENT FACTORY - Web Dashboard v2.0
Complete GUI: Standard Video | Cartoon Studio | Auto-Scheduler
Run: streamlit run app.py
"""
import streamlit as st
import sys
import asyncio
import json
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="AI Content Factory v2.0",
    page_icon="🤖",
    layout="wide"
)

sys.path.insert(0, str(Path(__file__).parent))

# Custom CSS
st.markdown("""
<style>
.main-header { font-size: 3rem; font-weight: bold; text-align: center;
    background: linear-gradient(135deg, #667eea, #764ba2);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 1rem; }
.stats-card { padding: 1.5rem; border-radius: 15px; background: linear-gradient(135deg, #1e1e2e, #2d2d44);
    color: white; text-align: center; margin-bottom: 0.5rem; }
.success-box { padding: 1rem; border-radius: 10px; background: #d4edda; border: 2px solid #28a745; }
</style>
""", unsafe_allow_html=True)

if 'history' not in st.session_state:
    st.session_state.history = []

def main():
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/artificial-intelligence.png", width=80)
        st.title("🤖 AI Factory v2.0")
        st.markdown("---")
        
        page = st.radio("📋 Navigation", [
            "🏠 Dashboard",
            "💎 Luxury Music Video",
            "🎬 Standard Video",
            "🎨 Cartoon Studio",
            "⏰ Auto-Scheduler",
            "📊 History",
            "⚙️ Settings"
        ])
        
        st.markdown("---")
        st.markdown("### 📊 API Status")
        apis = {
            "Groq AI": os.getenv("GROQ_API_KEY", ""),
            "Gemini": os.getenv("GEMINI_API_KEY", ""),
            "YouTube": os.getenv("YOUTUBE_API_KEY", ""),
            "Pexels": os.getenv("PEXELS_API_KEY", ""),
        }
        for name, key in apis.items():
            if key and "your_" not in key:
                st.success(f"✅ {name}")
            else:
                st.warning(f"⚠️ {name}")
    
    if page == "🏠 Dashboard":
        dashboard_page()
    elif page == "💎 Luxury Music Video":
        luxury_music_video_page()
    elif page == "🎬 Standard Video":
        standard_video_page()
    elif page == "🎨 Cartoon Studio":
        cartoon_page()
    elif page == "⏰ Auto-Scheduler":
        scheduler_page()
    elif page == "📊 History":
        history_page()
    elif page == "⚙️ Settings":
        settings_page()

def dashboard_page():
    st.markdown('<p class="main-header">🤖 AI Content Factory v2.0</p>', unsafe_allow_html=True)
    st.markdown("### Complete YouTube & Facebook Automation System")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="stats-card">', unsafe_allow_html=True)
        st.metric("📹 Videos", len(st.session_state.history))
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="stats-card">', unsafe_allow_html=True)
        cartoons = len(list(Path("output/cartoon_studio").glob("*.mp4")))
        st.metric("🎨 Cartoons", cartoons)
        st.markdown('</div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="stats-card">', unsafe_allow_html=True)
        thumbs = len(list(Path("output/thumbnails").glob("*.jpg")))
        st.metric("🖼️ Thumbnails", thumbs)
        st.markdown('</div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="stats-card">', unsafe_allow_html=True)
        seo_count = len(list(Path("output").glob("seo_*.json")))
        st.metric("📈 SEO Packs", seo_count)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 🚀 Features")
    st.markdown("""
    - **🎬 Standard Video** - News, Tech Reviews, Tutorials with AI voice & stock footage
    - **🎨 Cartoon Studio** - Animated cartoon series with AI characters & stories
    - **⏰ Auto-Scheduler** - Hands-free daily content creation & posting
    - **📈 SEO Engine** - High-CTR titles, tags & descriptions
    - **🌐 4 Languages** - English, Urdu, Hindi, Punjabi
    """)

def luxury_music_video_page():
    """Luxury music-video studio using a self-hosted ComfyUI/LTX workflow."""
    from content.luxury_music_video import (
        ComfyUIClient,
        LuxuryVideoError,
        load_workflow,
        prepare_workflow,
        create_job_manifest,
        find_video_outputs,
        DEFAULT_COMFY_URL,
        DEFAULT_WORKFLOW,
    )

    st.markdown("## 💎 Luxury Music Video Studio")
    st.caption("Your photo + luxury references + your music → cinematic music video")

    comfy_url = st.text_input(
        "🖥️ Self-hosted ComfyUI URL",
        os.getenv("COMFYUI_URL", DEFAULT_COMFY_URL),
    )
    duration = st.selectbox(
        "⏱️ Target length",
        [60, 120, 180],
        format_func=lambda x: f"{x // 60} minute" if x % 60 == 0 else f"{x} seconds",
    )
    aspect = st.selectbox("📐 Format", ["9:16 vertical", "16:9 landscape", "1:1 square"])
    quality = st.selectbox("🎥 Quality", ["HD", "Full HD"])

    subject = st.file_uploader(
        "👤 Upload your main photo",
        type=["jpg", "jpeg", "png", "webp"],
        key="lux_subject",
    )
    refs = st.file_uploader(
        "🏰 Upload mansion / car / luxury reference photos (optional)",
        type=["jpg", "jpeg", "png", "webp"],
        accept_multiple_files=True,
        key="lux_refs",
    )
    music = st.file_uploader(
        "🎵 Upload your music",
        type=["mp3", "wav", "m4a", "aac", "flac"],
        key="lux_music",
    )

    prompt = st.text_area(
        "🎬 Describe the performance",
        value=(
            "Photorealistic cinematic luxury music video. Keep the supplied person "
            "recognizable and consistent. The performer confidently sings to camera "
            "and moves naturally through an ultra-luxury mansion and beside premium "
            "exotic cars. Elegant wardrobe, realistic skin, dramatic cinematic "
            "lighting, smooth camera movement, shallow depth of field, premium "
            "music-video look. Vary camera angles and movement between shots."
        ),
        height=130,
    )

    if st.button("🚀 Generate Luxury Music Video", type="primary", use_container_width=True):
        if not subject:
            st.error("Please upload your main photo first.")
            return
        if not music:
            st.error("Please upload your music first.")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        job_dir = Path("data/luxury_jobs") / timestamp
        job_dir.mkdir(parents=True, exist_ok=True)

        subject_path = job_dir / subject.name
        subject_path.write_bytes(subject.getbuffer())

        ref_paths = []
        for item in refs or []:
            p = job_dir / item.name
            p.write_bytes(item.getbuffer())
            ref_paths.append(str(p))

        music_path = job_dir / music.name
        music_path.write_bytes(music.getbuffer())

        manifest = create_job_manifest(
            str(subject_path), ref_paths, str(music_path), duration, prompt
        )
        manifest["format"] = aspect
        manifest["quality"] = quality
        manifest_path = job_dir / "job.json"
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

        client = ComfyUIClient(comfy_url)
        if not client.health():
            st.warning(
                "Your project files are saved, but the self-hosted ComfyUI GPU "
                "server is not connected. Start ComfyUI on your GPU machine and "
                "run this job again."
            )
            st.info(f"Job manifest: {manifest_path}")
            return

        try:
            import shutil
            import subprocess

            if not shutil.which("ffmpeg"):
                st.error(
                    "FFmpeg is required to assemble the final 1–3 minute MP4. "
                    "Install FFmpeg on the machine running this app."
                )
                return

            workflow = load_workflow(DEFAULT_WORKFLOW)
            uploaded_subject = client.upload_file(subject_path, "image")
            uploaded_refs = [client.upload_file(p, "image") for p in ref_paths]
            uploaded_music = client.upload_file(music_path, "audio")

            # Each LTX shot is about 4.2 seconds (105 frames at 25 FPS).
            shot_seconds = 105 / 25
            shot_count = max(1, int((duration + shot_seconds - 0.01) // shot_seconds))

            st.info(
                f"Generating {shot_count} cinematic shots. This uses your own "
                "ComfyUI GPU rather than a commercial video API credit system."
            )

            downloaded_clips = []
            progress = st.progress(0)
            status = st.empty()

            for index in range(shot_count):
                shot_prompt = (
                    f"{prompt} Shot {index + 1} of {shot_count}. "
                    "Create a distinct cinematic composition and camera movement "
                    "while preserving the exact performer identity."
                )
                prepared = prepare_workflow(
                    workflow,
                    subject_image=uploaded_subject,
                    reference_images=uploaded_refs,
                    music_file=uploaded_music,
                    prompt=shot_prompt,
                    seed=int(datetime.now().timestamp()) + index * 7919,
                )
                prompt_id = client.queue(prepared)
                status.write(f"🎬 Rendering shot {index + 1}/{shot_count}…")

                history = client.wait_for_history(
                    prompt_id,
                    poll_seconds=2.0,
                    timeout=7200,
                )
                outputs = find_video_outputs(history)
                if not outputs:
                    raise LuxuryVideoError(
                        f"Shot {index + 1} completed but ComfyUI returned no video output."
                    )

                chosen = outputs[0]
                clip_path = job_dir / f"shot_{index + 1:03d}.mp4"
                client.download_url(
                    client.output_url(
                        chosen["filename"],
                        chosen.get("subfolder", ""),
                        chosen.get("type", "output"),
                    ),
                    clip_path,
                )
                downloaded_clips.append(clip_path)
                progress.progress((index + 1) / shot_count)

            concat_file = job_dir / "concat.txt"
            concat_file.write_text(
                "".join(f"file '{p.resolve().as_posix()}'\n" for p in downloaded_clips),
                encoding="utf-8",
            )
            assembled = job_dir / "assembled.mp4"

            subprocess.run(
                [
                    "ffmpeg", "-y", "-f", "concat", "-safe", "0",
                    "-i", str(concat_file),
                    "-c", "copy", str(assembled),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            final_path = job_dir / "luxury_music_video.mp4"
            subprocess.run(
                [
                    "ffmpeg", "-y",
                    "-i", str(assembled),
                    "-i", str(music_path),
                    "-map", "0:v:0",
                    "-map", "1:a:0",
                    "-c:v", "copy",
                    "-c:a", "aac",
                    "-b:a", "192k",
                    "-shortest",
                    str(final_path),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            status.empty()
            progress.empty()
            st.success("✅ Luxury music video completed!")
            st.video(str(final_path))
            st.download_button(
                "⬇️ Download final MP4",
                data=final_path.read_bytes(),
                file_name="luxury_music_video.mp4",
                mime="video/mp4",
                use_container_width=True,
            )
            st.info(
                "The generated visuals are assembled from short shots and the "
                "original uploaded music is used as the final soundtrack."
            )

        except subprocess.CalledProcessError as exc:
            st.error(f"FFmpeg failed: {exc.stderr[-2000:] if exc.stderr else exc}")
        except LuxuryVideoError as exc:
            st.error(str(exc))

    st.markdown("---")
    st.markdown("### 🧩 Current architecture")
    st.write(
        "Phone/browser → this GitHub app → self-hosted ComfyUI/LTX → "
        "short cinematic shots → FFmpeg → final MP4"
    )
    st.caption(
        "The video model is self-hosted. There is no leaked API key and no "
        "commercial video-API credit counter; generation is limited by the GPU "
        "available to your own server."
    )

def standard_video_page():
    st.markdown("## 🎬 Create Standard Video")
    
    col1, col2 = st.columns(2)
    with col1:
        language = st.selectbox("🌐 Language", ["english", "urdu", "hindi", "punjabi"])
        niche = st.selectbox("🎯 Niche", ["tech", "motivation", "educational", "gaming"])
    with col2:
        format_type = st.selectbox("📐 Format", ["landscape", "shorts", "square"])
    
    topic = st.text_input("📝 Topic (leave blank for auto-trend)", 
                          placeholder="e.g., Latest AI tools, iPhone review...")
    
    if st.button("🚀 Create Video", type="primary", use_container_width=True):
        from auto_scheduler import AutoScheduler
        scheduler = AutoScheduler(language=language, niche=niche)
        
        with st.spinner("🔍 Researching & Creating..."):
            result = asyncio.run(scheduler.create_content(topic if topic else None))
        
        if result:
            st.success("✅ Video Created Successfully!")
            video_path = result.get("video", "")
            if video_path and Path(video_path).exists():
                st.video(video_path)
            thumb_path = result.get("thumbnail", "")
            if thumb_path and Path(thumb_path).exists():
                st.image(thumb_path, caption="Thumbnail", width=400)
            
            seo = result.get("seo", {})
            if seo:
                st.markdown(f"**📈 Best Title:** {seo.get('best_title', 'N/A')}")
                st.markdown(f"**🎯 CTR Score:** {seo.get('estimated_ctr', {}).get('score', 'N/A')}/100")
            
            st.session_state.history.append(result)

def cartoon_page():
    st.markdown("## 🎨 Cartoon Studio")
    st.markdown("Create animated cartoon episodes with AI characters & stories!")
    
    col1, col2 = st.columns(2)
    with col1:
        topic = st.text_input("📝 Story Topic", "A brave cat who saves the village from a dragon")
        language = st.selectbox("🌐 Language", ["english", "urdu", "hindi"])
    with col2:
        scenes = st.slider("🎬 Number of Scenes", 5, 30, 10)
    
    if st.button("🎬 Create Cartoon Episode", type="primary", use_container_width=True):
        from create_cartoon_episode import create_episode
        
        with st.spinner("🎨 Creating cartoon episode..."):
            result = asyncio.run(create_episode(topic, language, scenes))
        
        if result and Path(result).exists():
            st.success("✅ Cartoon Episode Created!")
            st.video(result)
            size_mb = Path(result).stat().st_size / (1024*1024)
            st.info(f"📦 Size: {size_mb:.1f} MB")
            st.session_state.history.append({"type": "cartoon", "video": result, "topic": topic})

def scheduler_page():
    st.markdown("## ⏰ Auto-Scheduler")
    st.markdown("Hands-free automation - create & post content daily!")
    
    st.markdown("### 📊 Stats")
    stats_path = Path("data/stats.json")
    if stats_path.exists():
        with open(stats_path) as f:
            stats = json.load(f)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Videos Created", stats.get("videos_created", 0))
        c2.metric("Posts Made", stats.get("posts_made", 0))
        c3.metric("Errors", stats.get("errors", 0))
    
    if st.button("▶️ Create Content NOW", use_container_width=True):
        from auto_scheduler import AutoScheduler
        scheduler = AutoScheduler()
        with st.spinner("Creating..."):
            asyncio.run(scheduler.create_content())
        st.success("✅ Done!")

def history_page():
    st.markdown("## 📊 Content History")
    
    history_dir = Path("data/history")
    if history_dir.exists():
        files = sorted(history_dir.glob("*.json"), reverse=True)[:20]
        for f in files:
            with open(f) as fp:
                data = json.load(fp)
            with st.expander(f"📹 {data.get('topic', 'Unknown')[:80]} - {f.stem}"):
                st.json(data)
    else:
        st.info("No content created yet. Create your first video!")

def settings_page():
    st.markdown("## ⚙️ Settings")
    
    st.markdown("### 🔑 API Keys Status")
    keys = {
        "GROQ_API_KEY": "Groq AI (Script Writing)",
        "GEMINI_API_KEY": "Google Gemini (Research)",
        "YOUTUBE_API_KEY": "YouTube Data API",
        "PEXELS_API_KEY": "Pexels (Stock Media)",
    }
    for key, desc in keys.items():
        val = os.getenv(key, "")
        if val and "your_" not in val:
            st.success(f"✅ {desc}")
        else:
            st.warning(f"⚠️ {desc}")
    
    st.markdown("---")
    st.markdown("### 💡 About")
    st.markdown("""
    **AI Content Factory v2.0**
    - 100% FREE APIs
    - 4 Languages supported
    - Standard videos + Cartoon studio
    - Auto-scheduler for hands-free operation
    - Professional web dashboard
    """)

if __name__ == "__main__":
    main()