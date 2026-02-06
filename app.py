#!/usr/bin/env python3
"""
Gradio Web Interface for AI Video Generation
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

import gradio as gr
import torch

from src.utils import (
    get_device,
    get_system_info,
    estimate_generation_time,
    sanitize_filename,
    ensure_dir,
)
from src.prompt_analyzer import PromptAnalyzer
from src.model_manager import ModelManager
from src.keyframe_generator import KeyframeGenerator
from src.video_interpolator import VideoInterpolator
from src.post_processor import PostProcessor


# Global state
device = None
model_manager = None
sdxl_pipeline = None
svd_pipeline = None


def initialize_models():
    """Initialize models on startup"""
    global device, model_manager, sdxl_pipeline, svd_pipeline
    
    print("🚀 Initializing AI Video Generator...")
    
    device = get_device()
    system_info = get_system_info()
    
    print("\n📊 System Information:")
    for key, value in system_info.items():
        print(f"  {key}: {value}")
    
    model_manager = ModelManager(cache_dir="./models")
    
    print("\n📥 Loading models (this may take a while on first run)...")
    sdxl_pipeline = model_manager.load_sdxl_pipeline(device)
    svd_pipeline = model_manager.load_svd_pipeline(device)
    
    print("✅ Models loaded and ready!\n")


def generate_video_gradio(
    prompt: str,
    duration: int,
    fps: int,
    resolution: str,
    style: str,
    num_keyframes: int,
    seed: int,
    apply_color_grading: bool,
    progress=gr.Progress()
):
    """
    Generate video from Gradio interface
    """
    try:
        progress(0, desc="Starting generation...")
        
        # Validate inputs
        if not prompt or len(prompt.strip()) < 5:
            return None, "❌ Error: Prompt must be at least 5 characters"
        
        if duration < 1 or duration > 60:
            return None, "❌ Error: Duration must be between 1 and 60 seconds"
        
        # Parse resolution
        resolution_map = {
            "720p (1280x720)": (1280, 720),
            "1080p (1920x1080)": (1920, 1080),
            "4K (3840x2160)": (3840, 2160),
        }
        target_resolution = resolution_map[resolution]
        
        progress(0.05, desc="Analyzing prompt...")
        
        # Analyze prompt
        analyzer = PromptAnalyzer()
        scene = analyzer.analyze(prompt, duration=duration)
        enhanced_prompt = analyzer.create_enhanced_prompt(scene)
        
        status = f"""
📝 **Prompt Analysis:**
- Subject: {scene.subject}
- Action: {scene.action}
- Style: {scene.style}
- Camera: {scene.camera_movement}
- Lighting: {scene.lighting}

🔧 **Enhanced Prompt:** {enhanced_prompt}
"""
        
        progress(0.1, desc="Generating keyframes...")
        
        # Initialize generators
        keyframe_gen = KeyframeGenerator(sdxl_pipeline, device)
        video_interp = VideoInterpolator(svd_pipeline, device, fps=fps)
        post_proc = PostProcessor(target_resolution, fps)
        
        # Generate keyframes
        keyframes = keyframe_gen.generate_keyframes(
            prompt=enhanced_prompt,
            num_keyframes=num_keyframes,
            seed=seed if seed > 0 else None,
        )
        
        progress(0.4, desc="Upscaling keyframes...")
        
        # Upscale keyframes
        keyframes = [
            keyframe_gen.upscale_keyframe(kf, target_resolution[0], target_resolution[1])
            for kf in keyframes
        ]
        
        progress(0.5, desc="Interpolating frames (this may take a while)...")
        
        # Interpolate frames
        duration_per_keyframe = duration / max(1, num_keyframes - 1)
        frames = video_interp.interpolate_between_keyframes(
            keyframes,
            duration_per_keyframe=duration_per_keyframe,
        )
        
        progress(0.8, desc="Post-processing...")
        
        # Post-process
        frames = post_proc.process_video(
            frames,
            apply_upscaling=True,
            apply_color_grading=apply_color_grading,
            apply_stabilization=False,
        )
        
        progress(0.9, desc="Encoding video...")
        
        # Save video
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_prompt = sanitize_filename(prompt[:30])
        output_path = f"outputs/video_{safe_prompt}_{timestamp}.mp4"
        
        ensure_dir("outputs")
        post_proc.save_video(frames, output_path, crf=18)
        
        progress(1.0, desc="Complete!")
        
        status += f"""

✅ **Video Generated Successfully!**
- Duration: {len(frames) / fps:.2f}s
- Frames: {len(frames)}
- Resolution: {target_resolution[0]}x{target_resolution[1]}
- File: {output_path}
"""
        
        return output_path, status
        
    except Exception as e:
        error_msg = f"❌ **Error:** {str(e)}"
        print(f"\n{error_msg}\n")
        import traceback
        traceback.print_exc()
        return None, error_msg


def create_interface():
    """Create Gradio interface"""
    
    with gr.Blocks(
        title="AI Video Generator",
        theme=gr.themes.Soft(primary_hue="blue")
    ) as demo:
        gr.Markdown("""
# 🎬 AI Video Generator
### Sora-Inspired Text-to-Video System

Generate high-quality videos from text descriptions using open-source AI models.
**Free, unlimited, no watermarks.**

---
        """)
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### ⚙️ Settings")
                
                prompt = gr.Textbox(
                    label="Video Prompt",
                    placeholder="Describe the video you want to generate...\nExample: A futuristic city at sunset with flying cars",
                    lines=4
                )
                
                with gr.Row():
                    duration = gr.Slider(
                        minimum=1,
                        maximum=60,
                        value=10,
                        step=1,
                        label="Duration (seconds)"
                    )
                    
                    fps = gr.Dropdown(
                        choices=[24, 30, 60],
                        value=30,
                        label="FPS"
                    )
                
                resolution = gr.Dropdown(
                    choices=[
                        "720p (1280x720)",
                        "1080p (1920x1080)",
                        "4K (3840x2160)"
                    ],
                    value="1080p (1920x1080)",
                    label="Resolution"
                )
                
                style = gr.Dropdown(
                    choices=[
                        "photorealistic",
                        "cinematic",
                        "documentary",
                        "animated",
                        "artistic"
                    ],
                    value="photorealistic",
                    label="Style"
                )
                
                with gr.Accordion("Advanced Options", open=False):
                    num_keyframes = gr.Slider(
                        minimum=2,
                        maximum=10,
                        value=5,
                        step=1,
                        label="Number of Keyframes"
                    )
                    
                    seed = gr.Number(
                        value=42,
                        label="Random Seed (0 for random)"
                    )
                    
                    apply_color_grading = gr.Checkbox(
                        value=True,
                        label="Apply Color Grading"
                    )
                
                generate_btn = gr.Button(
                    "🎬 Generate Video",
                    variant="primary",
                    size="lg"
                )
                
                gr.Markdown("""
### 📋 Example Prompts
- "Ocean waves crashing on a beach at golden hour"
- "Microscopic view of cells dividing with DNA visible"
- "Time-lapse of a flower blooming from bud to full bloom"
- "A futuristic city at sunset with flying cars and neon lights"
                """)
            
            with gr.Column(scale=1):
                gr.Markdown("### 🎥 Output")
                
                video_output = gr.Video(
                    label="Generated Video",
                    height=400
                )
                
                status_output = gr.Markdown(
                    value="Ready to generate. Configure settings and click Generate Video.",
                    label="Status"
                )
        
        # Event handlers
        generate_btn.click(
            fn=generate_video_gradio,
            inputs=[
                prompt,
                duration,
                fps,
                resolution,
                style,
                num_keyframes,
                seed,
                apply_color_grading,
            ],
            outputs=[video_output, status_output]
        )
        
        gr.Markdown("""
---
### 💡 Tips
- **First run**: Model download may take 10-20 minutes (one-time only)
- **Generation time**: Depends on your hardware (5-30 minutes typical)
- **Quality**: Higher keyframes = better but slower
- **Resolution**: Start with 720p for testing, then try 1080p
- **Seed**: Use same seed for reproducible results

### ⚡ System Requirements
- **Minimum**: 16GB RAM, CPU only (slow)
- **Recommended**: NVIDIA GPU with 8GB+ VRAM
- **Optimal**: RTX 4090 or better

---
**Built with**: Stable Diffusion XL • Stable Video Diffusion • Diffusers • Gradio
        """)
    
    return demo


def main():
    """Main entry point"""
    print("=" * 70)
    print("🎬 AI VIDEO GENERATOR - WEB INTERFACE")
    print("=" * 70)
    print()
    
    # Initialize models
    initialize_models()
    
    # Create and launch interface
    demo = create_interface()
    
    print("\n🌐 Starting web interface...")
    print("📍 Access the app at: http://localhost:7860")
    print("🛑 Press Ctrl+C to stop the server\n")
    
    # Enable share mode for public URL
    share_mode = os.getenv("GRADIO_SHARE", "false").lower() == "true"
    
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=share_mode,  # Creates public gradio.live link
        show_error=True,
    )


if __name__ == "__main__":
    main()
