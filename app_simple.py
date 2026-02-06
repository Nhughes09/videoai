#!/usr/bin/env python3
"""
SIMPLE Text-to-Video Generator with REAL progress updates
"""

import os
import sys
from datetime import datetime
import gradio as gr
import torch
import threading
import time


def get_device():
    if torch.cuda.is_available():
        return "cuda"
    elif torch.backends.mps.is_available():
        return "mps"
    return "cpu"


# Global state
pipe = None
current_status = "Ready"


def update_status(msg):
    global current_status
    current_status = msg
    print(f"📢 {msg}")


def generate_video(
    prompt: str,
    num_frames: int = 24,
    num_steps: int = 30,
):
    """Generate video with real status updates"""
    global pipe
    
    if not prompt or len(prompt.strip()) < 3:
        yield None, "❌ Enter a prompt first!"
        return
    
    device = get_device()
    dtype = torch.float16 if device != "cpu" else torch.float32
    
    print(f"\n{'='*60}")
    print(f"🎬 STARTING VIDEO GENERATION")
    print(f"   Prompt: {prompt}")
    print(f"   Frames: {num_frames}")
    print(f"   Steps: {num_steps}")
    print(f"   Device: {device}")
    print(f"{'='*60}\n")
    
    try:
        # PHASE 1: Load model
        if pipe is None:
            yield None, "📥 **Downloading AI model...**\n\n⏳ First time only (~3GB)\n\nThis takes 2-5 minutes.\nCheck your terminal for download progress!\n\n*The model is downloading in the background...*"
            
            print("📥 PHASE 1: Downloading model...")
            print("   This is a ~3GB download, please wait...")
            
            from diffusers import DiffusionPipeline
            
            # Show download is happening
            start_time = time.time()
            
            pipe = DiffusionPipeline.from_pretrained(
                "cerspense/zeroscope_v2_576w",
                torch_dtype=dtype,
            )
            
            download_time = time.time() - start_time
            print(f"✅ Download complete! Took {download_time:.1f} seconds")
            
            yield None, f"✅ **Model downloaded!** ({download_time:.0f}s)\n\n🔧 Moving to GPU..."
            
            print("🔧 Moving model to GPU...")
            pipe.to(device)
            
            # Memory optimizations
            pipe.enable_attention_slicing()
            if hasattr(pipe, 'enable_vae_slicing'):
                pipe.enable_vae_slicing()
            
            print("✅ Model ready!")
            yield None, "✅ **Model loaded!**\n\n🎨 Starting frame generation..."
        else:
            yield None, "🎨 **Starting generation...**"
        
        # PHASE 2: Generate frames
        print(f"\n⏳ PHASE 2: Generating {num_frames} frames...")
        
        current_step = [0]  # Use list to allow modification in callback
        
        def progress_callback(step, timestep, latents):
            current_step[0] = step
            pct = int((step / num_steps) * 100)
            print(f"   Step {step}/{num_steps} ({pct}%)")
        
        # Run generation with periodic status updates
        generation_done = [False]
        result = [None]
        error = [None]
        
        def run_generation():
            try:
                output = pipe(
                    prompt=prompt,
                    num_frames=num_frames,
                    num_inference_steps=num_steps,
                    width=576,
                    height=320,
                    callback=progress_callback,
                    callback_steps=1,
                )
                result[0] = output.frames[0]
            except Exception as e:
                error[0] = str(e)
            finally:
                generation_done[0] = True
        
        # Start generation in background thread
        thread = threading.Thread(target=run_generation)
        thread.start()
        
        # Update progress while generating
        while not generation_done[0]:
            step = current_step[0]
            pct = int((step / num_steps) * 100)
            status = f"""🎨 **Generating frames...**

**Progress:** Step {step} / {num_steps} ({pct}%)

**Prompt:** {prompt}
**Frames:** {num_frames}
**Device:** {device}

⏳ Please wait, this takes 2-5 minutes...
"""
            yield None, status
            time.sleep(1)  # Update every second
        
        thread.join()
        
        if error[0]:
            yield None, f"❌ **Error:** {error[0]}"
            return
        
        frames = result[0]
        print(f"✅ Generated {len(frames)} frames!")
        
        # PHASE 3: Save video
        yield None, "💾 **Saving video...**"
        print("\n💾 PHASE 3: Saving video...")
        
        os.makedirs("outputs", exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = f"outputs/video_{ts}.mp4"
        
        from diffusers.utils import export_to_video
        export_to_video(frames, out_path, fps=8)
        
        print(f"✅ Saved: {out_path}")
        
        # Done!
        final_status = f"""✅ **Video Created!**

🎬 **Prompt:** {prompt}
📊 **Frames:** {num_frames}
💾 **File:** `{out_path}`
🖥️ **Device:** {device}

---
Video saved to `outputs/` folder.
"""
        yield out_path, final_status
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        yield None, f"❌ **Error:** {str(e)}\n\nCheck terminal for details."


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
                    placeholder="Example: A rocket launching into space",
                    lines=2,
                )
                
                with gr.Row():
                    frames = gr.Slider(8, 36, value=24, step=4, label="Frames")
                    steps = gr.Slider(15, 50, value=25, step=5, label="Quality")
                
                btn = gr.Button("🎬 Generate Video", variant="primary", size="lg")
                
                gr.Markdown("""
### ⚡ What to expect:
1. **First run**: Downloads ~3GB model (2-5 min)
2. **Generation**: 2-5 minutes per video
3. **Watch terminal** for detailed progress
                """)
            
            with gr.Column():
                video = gr.Video(label="Your Video", height=350)
                status = gr.Markdown("Ready! Enter a prompt and click Generate.")
        
        btn.click(
            generate_video, 
            [prompt, frames, steps], 
            [video, status],
        )
        
        gr.Markdown("""
---
**GitHub:** [github.com/Nhughes09/videoai](https://github.com/Nhughes09/videoai) | Clone and use free!
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
