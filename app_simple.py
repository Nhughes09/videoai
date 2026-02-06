#!/usr/bin/env python3
"""
SIMPLE Text-to-Video Generator
Uses Zeroscope - the most reliable open-source text-to-video model
"""

import os
import sys
from datetime import datetime
import gradio as gr
import torch


def get_device():
    if torch.cuda.is_available():
        return "cuda"
    elif torch.backends.mps.is_available():
        return "mps"
    return "cpu"


# Global
pipe = None


def generate_video(
    prompt: str,
    num_frames: int = 24,
    num_steps: int = 30,
    progress=gr.Progress()
):
    global pipe
    
    try:
        if not prompt or len(prompt.strip()) < 3:
            return None, "❌ Enter a prompt first!"
        
        device = get_device()
        dtype = torch.float16 if device != "cpu" else torch.float32
        
        progress(0.1, desc="⏳ Loading model (first time: ~3GB download)...")
        print(f"\n{'='*60}")
        print(f"🎬 GENERATING VIDEO")
        print(f"   Prompt: {prompt}")
        print(f"   Frames: {num_frames}")
        print(f"   Device: {device}")
        print(f"{'='*60}")
        
        if pipe is None:
            print("📥 Downloading Zeroscope model...")
            from diffusers import DiffusionPipeline
            
            pipe = DiffusionPipeline.from_pretrained(
                "cerspense/zeroscope_v2_576w",
                torch_dtype=dtype,
            )
            pipe.to(device)
            
            # Memory optimizations
            pipe.enable_attention_slicing()
            if hasattr(pipe, 'enable_vae_slicing'):
                pipe.enable_vae_slicing()
            
            print("✅ Model loaded!")
        
        progress(0.2, desc="🎨 Generating frames...")
        print(f"⏳ Generating {num_frames} frames with {num_steps} steps...")
        
        # Generate with progress callback
        def callback(step, timestep, latents):
            pct = 0.2 + (step / num_steps) * 0.6
            progress(pct, desc=f"🎨 Step {step}/{num_steps}")
            print(f"   Step {step}/{num_steps}")
        
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
        print(f"✅ Generated {len(frames)} frames!")
        
        progress(0.85, desc="💾 Saving video...")
        
        # Save video
        os.makedirs("outputs", exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = f"outputs/video_{ts}.mp4"
        
        from diffusers.utils import export_to_video
        export_to_video(frames, out_path, fps=8)
        
        print(f"✅ Saved: {out_path}")
        progress(1.0, desc="✅ Done!")
        
        return out_path, f"""✅ **Video Created!**

**Prompt:** {prompt}
**Frames:** {num_frames}
**File:** `{out_path}`
**Device:** {device}

🎉 Check the `outputs/` folder!
"""
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return None, f"❌ Error: {str(e)}\n\nCheck terminal for details."


def build_ui():
    with gr.Blocks(title="AI Video Generator") as demo:
        gr.Markdown("""
# 🎬 AI Video Generator
**Type text → Get video!** Free, local, no API keys.
---
        """)
        
        with gr.Row():
            with gr.Column():
                prompt = gr.Textbox(
                    label="What do you want to see?",
                    placeholder="Example: A rocket launching into space with stars in background",
                    lines=3,
                )
                
                with gr.Row():
                    frames = gr.Slider(8, 36, value=24, step=4, label="Frames (more = longer)")
                    steps = gr.Slider(15, 50, value=30, step=5, label="Quality")
                
                btn = gr.Button("🎬 Generate Video", variant="primary", size="lg")
                
                gr.Markdown("""
### 💡 Tips
- First run downloads ~3GB model (one time)
- More frames = longer video (~3 frames per second)
- Higher quality = slower generation
- Generation takes 2-5 minutes
                """)
            
            with gr.Column():
                video = gr.Video(label="Your Video")
                status = gr.Markdown("Ready! Enter a prompt and click Generate.")
        
        btn.click(generate_video, [prompt, frames, steps], [video, status])
        
        gr.Markdown("""
---
**GitHub:** [github.com/Nhughes09/videoai](https://github.com/Nhughes09/videoai)
        """)
    
    return demo


if __name__ == "__main__":
    print("=" * 60)
    print("🎬 AI VIDEO GENERATOR")
    print("=" * 60)
    print(f"Device: {get_device()}")
    print()
    
    demo = build_ui()
    
    share = os.getenv("GRADIO_SHARE", "false").lower() == "true"
    
    print("🌐 Starting server...")
    if share:
        print("🔗 Creating public link...")
    print("📍 Local: http://localhost:7860")
    print()
    
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=share,
    )
