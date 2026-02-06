#!/usr/bin/env python3
"""
Lightweight Local Video Generator
Uses smaller models that work on 8GB RAM Macs
"""

import os
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

import gradio as gr
import torch
import numpy as np
from PIL import Image


def get_device():
    """Get best available device"""
    if torch.cuda.is_available():
        return torch.device("cuda")
    elif torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


# Global pipeline
pipeline = None
device = None


def load_pipeline():
    """Load lightweight text-to-video pipeline"""
    global pipeline, device
    
    if pipeline is not None:
        return pipeline
    
    device = get_device()
    print(f"✅ Using device: {device}")
    
    from diffusers import DiffusionPipeline, DPMSolverMultistepScheduler
    
    print("📥 Loading text-to-video model...")
    print("   (First time downloads ~4GB, please wait)")
    
    # Use ModelScope text-to-video - smaller and works on 8GB RAM
    pipeline = DiffusionPipeline.from_pretrained(
        "damo-vilab/text-to-video-ms-1.7b",
        torch_dtype=torch.float16 if device.type != "cpu" else torch.float32,
        variant="fp16" if device.type != "cpu" else None,
    )
    
    # Use faster scheduler
    pipeline.scheduler = DPMSolverMultistepScheduler.from_config(
        pipeline.scheduler.config
    )
    
    # Move to device
    pipeline = pipeline.to(device)
    
    # Enable memory optimizations
    if device.type == "cuda":
        pipeline.enable_attention_slicing()
        pipeline.enable_vae_slicing()
    
    print("✅ Model loaded!")
    return pipeline


def generate_video(
    prompt: str,
    num_frames: int,
    num_inference_steps: int,
    guidance_scale: float,
    progress=gr.Progress()
):
    """Generate video from text prompt"""
    try:
        if not prompt or len(prompt.strip()) < 3:
            return None, "❌ Please enter a prompt (at least 3 characters)"
        
        progress(0.1, desc="Loading model...")
        pipe = load_pipeline()
        
        progress(0.2, desc=f"Generating {num_frames} frames...")
        print(f"🎬 Generating video for: {prompt}")
        
        # Generate video frames
        output = pipe(
            prompt=prompt,
            num_frames=num_frames,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
        )
        
        frames = output.frames[0]  # List of PIL Images
        
        progress(0.8, desc="Saving video...")
        
        # Save as video
        os.makedirs("outputs", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"outputs/video_{timestamp}.mp4"
        
        # Export frames to video
        from diffusers.utils import export_to_video
        export_to_video(frames, output_path, fps=8)
        
        progress(1.0, desc="Complete!")
        
        status = f"""✅ **Video Generated!**

- **Prompt**: {prompt}
- **Frames**: {num_frames}
- **File**: {output_path}
- **Device**: {device}

🎬 Video saved to `outputs/` folder
"""
        return output_path, status
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return None, f"❌ Error: {str(e)}"


def create_interface():
    """Create Gradio interface"""
    
    with gr.Blocks(
        title="AI Video Generator",
        theme=gr.themes.Soft(primary_hue="purple")
    ) as demo:
        gr.Markdown("""
# 🎬 AI Video Generator
### Free Text-to-Video using Local Models

Type a description → Get a video. **No API needed, runs locally!**

---
        """)
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### ⚙️ Settings")
                
                prompt = gr.Textbox(
                    label="Video Prompt",
                    placeholder="Describe the video you want...\n\nExamples:\n• A cat playing with yarn\n• Sunset over the ocean\n• Astronaut on Mars",
                    lines=4
                )
                
                with gr.Row():
                    num_frames = gr.Slider(
                        minimum=8,
                        maximum=32,
                        value=16,
                        step=4,
                        label="Frames (more = longer video)"
                    )
                    
                    steps = gr.Slider(
                        minimum=10,
                        maximum=50,
                        value=25,
                        step=5,
                        label="Quality Steps"
                    )
                
                guidance = gr.Slider(
                    minimum=5.0,
                    maximum=15.0,
                    value=9.0,
                    step=0.5,
                    label="Prompt Strength"
                )
                
                generate_btn = gr.Button(
                    "🎬 Generate Video",
                    variant="primary",
                    size="lg"
                )
                
                gr.Markdown("""
### 📋 Tips
- **16 frames** = ~2 second video
- **Higher steps** = better quality but slower
- Be specific in your prompts
- First generation downloads the model (~4GB)
                """)
            
            with gr.Column(scale=1):
                gr.Markdown("### 🎥 Output")
                
                video_output = gr.Video(
                    label="Generated Video",
                    height=400
                )
                
                status_output = gr.Markdown(
                    value="Ready! Enter a prompt and click Generate.",
                    label="Status"
                )
        
        generate_btn.click(
            fn=generate_video,
            inputs=[prompt, num_frames, steps, guidance],
            outputs=[video_output, status_output]
        )
        
        gr.Markdown("""
---
### 🚀 How It Works
1. Uses **ModelScope Text-to-Video** model (runs locally)
2. Your **Apple Silicon GPU** accelerates generation
3. Videos saved to `outputs/` folder
4. **100% free**, no API keys needed

### 📦 GitHub
Clone this repo: `git clone https://github.com/Nhughes09/videoai.git`

---
**Built with** PyTorch • Diffusers • Gradio
        """)
    
    return demo


def main():
    print("=" * 70)
    print("🎬 AI VIDEO GENERATOR - LOCAL")
    print("=" * 70)
    print()
    print(f"Device: {get_device()}")
    print()
    
    demo = create_interface()
    
    share_mode = os.getenv("GRADIO_SHARE", "false").lower() == "true"
    
    print("🌐 Starting web interface...")
    if share_mode:
        print("🔗 Creating PUBLIC share link...")
    print("📍 Local: http://localhost:7860")
    print("🛑 Press Ctrl+C to stop")
    print()
    
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=share_mode,
        show_error=True,
    )


if __name__ == "__main__":
    main()
