#!/usr/bin/env python3
"""
AI Video Generator - FULL LIVE LOGGING
Shows percentage for EVERYTHING!
"""

import os
import sys
from datetime import datetime
import gradio as gr
import torch
import time

print("=" * 60)
print("🎬 AI VIDEO GENERATOR")
print("=" * 60)
print()

def get_device():
    if torch.cuda.is_available():
        return "cuda"
    elif torch.backends.mps.is_available():
        return "mps"
    return "cpu"

DEVICE = get_device()
print(f"✅ Device: {DEVICE}")
print()

# ============================================================
# DOWNLOAD & LOAD MODEL
# ============================================================
print("=" * 60)
print("📥 DOWNLOADING & LOADING MODEL")
print("   This is ~3GB, takes 3-5 minutes first time")
print("   Watch the progress bars below!")
print("=" * 60)
print()

from diffusers import DiffusionPipeline, DPMSolverMultistepScheduler

MODEL_ID = "cerspense/zeroscope_v2_576w"
DTYPE = torch.float32  # More stable on MPS/CPU

load_start = time.time()

# Download and load (HuggingFace shows progress automatically)
pipe = DiffusionPipeline.from_pretrained(
    MODEL_ID,
    torch_dtype=DTYPE,
)

download_time = time.time() - load_start
print()
print(f"✅ Downloaded & loaded in {download_time:.1f}s")

# Move to device
print(f"🔧 Moving to {DEVICE}...")
move_start = time.time()
pipe.to(DEVICE)
print(f"   Done in {time.time()-move_start:.1f}s")

# Optimize
pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
pipe.enable_attention_slicing(1)
if hasattr(pipe, 'enable_vae_slicing'):
    pipe.enable_vae_slicing()

print()
print("=" * 60)
print("✅ MODEL READY - YOU CAN START GENERATING!")
print("=" * 60)
print()


def generate_video(prompt: str, num_frames: int = 16, num_steps: int = 20):
    """Generate with LIVE progress"""
    
    if not prompt or len(prompt.strip()) < 3:
        yield None, "❌ Enter a prompt!"
        return
    
    print()
    print("=" * 60)
    print(f"🎬 GENERATING: {prompt}")
    print(f"   Frames: {num_frames}, Steps: {num_steps}")
    print("=" * 60)
    
    try:
        start = time.time()
        current_step = [0]
        
        def callback(step, timestep, latents):
            current_step[0] = step
            pct = int((step / num_steps) * 100)
            elapsed = time.time() - start
            eta = (elapsed / max(step, 1)) * (num_steps - step) if step > 0 else 0
            print(f"   Step {step}/{num_steps} | {pct}% | Time: {elapsed:.1f}s | ETA: {eta:.1f}s")
        
        yield None, f"""🎨 **GENERATING...**

**Prompt:** {prompt}
**Frames:** {num_frames} | **Steps:** {num_steps}

⏳ Check terminal for LIVE step-by-step progress!
"""
        
        output = pipe(
            prompt=prompt,
            num_frames=num_frames,
            num_inference_steps=num_steps,
            width=576,
            height=320,
            callback=callback,
            callback_steps=1,
        )
        
        frames = output.frames[0]
        gen_time = time.time() - start
        
        print(f"\n✅ Done! {len(frames)} frames in {gen_time:.1f}s")
        
        # Save
        os.makedirs("outputs", exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = f"outputs/video_{ts}.mp4"
        
        from diffusers.utils import export_to_video
        export_to_video(frames, out_path, fps=8)
        
        size_kb = os.path.getsize(out_path) / 1024
        print(f"💾 Saved: {out_path} ({size_kb:.0f} KB)")
        
        yield out_path, f"""✅ **DONE!**

| | |
|---|---|
| **Prompt** | {prompt} |
| **Frames** | {len(frames)} |
| **Time** | {gen_time:.1f}s |
| **File** | `{out_path}` |
"""
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        yield None, f"❌ Error: {str(e)}"


# UI
with gr.Blocks(title="AI Video Generator") as demo:
    gr.Markdown("# 🎬 AI Video Generator\n**Text → Video** | Free | Local")
    
    with gr.Row():
        with gr.Column():
            prompt = gr.Textbox(label="Prompt", placeholder="A sunset over the ocean", lines=2)
            with gr.Row():
                frames = gr.Slider(8, 24, 16, step=4, label="Frames")
                steps = gr.Slider(10, 30, 20, step=5, label="Quality")
            btn = gr.Button("🎬 Generate", variant="primary", size="lg")
            gr.Markdown("📊 Watch terminal for LIVE progress!")
        
        with gr.Column():
            video = gr.Video(label="Video", height=350)
            status = gr.Markdown("Ready!")
    
    btn.click(generate_video, [prompt, frames, steps], [video, status])
    gr.Markdown("[GitHub](https://github.com/Nhughes09/videoai)")

# Launch
print("🌐 Starting server...")
share = os.getenv("GRADIO_SHARE", "false").lower() == "true"
if share: print("🔗 Creating public link...")
print("📍 http://localhost:7860\n")

demo.launch(server_name="0.0.0.0", server_port=7860, share=share)
