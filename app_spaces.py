#!/usr/bin/env python3
"""
AI Video Generator - HuggingFace Spaces Version
Runs on HuggingFace's FREE GPU!
"""

import os
import gradio as gr
import torch
from datetime import datetime
import time

# For Spaces, use CUDA
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Device: {DEVICE}")

# Global
pipe = None


def load_model():
    global pipe
    if pipe is not None:
        return pipe
    
    print("Loading model...")
    from diffusers import DiffusionPipeline, DPMSolverMultistepScheduler
    
    pipe = DiffusionPipeline.from_pretrained(
        "cerspense/zeroscope_v2_576w",
        torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32,
    )
    pipe.to(DEVICE)
    pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
    
    if DEVICE == "cuda":
        pipe.enable_attention_slicing()
        pipe.enable_vae_slicing()
    
    print("Model ready!")
    return pipe


def generate(prompt, frames=16, steps=20, progress=gr.Progress()):
    if not prompt:
        return None, "❌ Enter a prompt!"
    
    progress(0.1, desc="Loading model...")
    model = load_model()
    
    progress(0.2, desc="Generating...")
    start = time.time()
    
    output = model(
        prompt=prompt,
        num_frames=frames,
        num_inference_steps=steps,
        width=576,
        height=320,
    )
    
    gen_time = time.time() - start
    progress(0.9, desc="Saving...")
    
    os.makedirs("outputs", exist_ok=True)
    out_path = f"outputs/video_{datetime.now().strftime('%H%M%S')}.mp4"
    
    from diffusers.utils import export_to_video
    export_to_video(output.frames[0], out_path, fps=8)
    
    progress(1.0, desc="Done!")
    
    return out_path, f"✅ Done in {gen_time:.1f}s!"


# UI
with gr.Blocks(title="AI Video Generator") as demo:
    gr.Markdown("# 🎬 AI Video Generator\nType text → Get video! Free on HuggingFace!")
    
    with gr.Row():
        with gr.Column():
            prompt = gr.Textbox(label="Prompt", placeholder="A sunset over the ocean")
            with gr.Row():
                frames = gr.Slider(8, 24, 16, step=4, label="Frames")
                steps = gr.Slider(10, 30, 20, step=5, label="Quality")
            btn = gr.Button("🎬 Generate", variant="primary")
        
        with gr.Column():
            video = gr.Video(label="Video")
            status = gr.Markdown("Ready!")
    
    btn.click(generate, [prompt, frames, steps], [video, status])


demo.launch()
