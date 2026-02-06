#!/usr/bin/env python3
"""
Lightweight Web Interface - API Only (No Local Models Required)
Uses HuggingFace/Replicate APIs - No GPU Needed!
"""

import os
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

import gradio as gr


def generate_video_api(
    prompt: str,
    duration: int,
    method: str,
    progress=gr.Progress()
):
    """Generate video using APIs"""
    try:
        if not prompt or len(prompt.strip()) < 5:
            return None, "❌ Error: Prompt must be at least 5 characters"
        
        progress(0.1, desc="Initializing...")
        
        hf_token = os.getenv("HF_TOKEN")
        replicate_token = os.getenv("REPLICATE_API_TOKEN")
        
        # Determine which API to use
        if method == "HuggingFace (Free)":
            if not hf_token:
                return None, """❌ HuggingFace token not set!

**To fix:**
1. Get free token: https://huggingface.co/settings/tokens
2. Stop this server (Ctrl+C)
3. Run: `export HF_TOKEN=your_token_here`
4. Start again: `python3 app_lite.py`
"""
            return _generate_hf(prompt, duration, hf_token, progress)
            
        elif method == "Replicate ($10 free)":
            if not replicate_token:
                return None, """❌ Replicate token not set!

**To fix:**
1. Get $10 free credits: https://replicate.com
2. Stop this server (Ctrl+C)
3. Run: `export REPLICATE_API_TOKEN=your_token_here`
4. Start again: `python3 app_lite.py`
"""
            return _generate_replicate(prompt, duration, replicate_token, progress)
        
        else:
            return None, "❌ Please select a generation method"
            
    except Exception as e:
        return None, f"❌ Error: {str(e)}"


def _generate_hf(prompt, duration, token, progress):
    """Generate using HuggingFace Inference API"""
    try:
        from huggingface_hub import InferenceClient
        
        progress(0.2, desc="Connecting to HuggingFace...")
        client = InferenceClient(token=token)
        
        progress(0.3, desc="Generating video (this may take 2-5 minutes)...")
        
        # Use text-to-video endpoint
        # Note: This uses experimental HF inference API
        result = client.text_to_video(
            prompt=prompt,
            model="Wan-AI/Wan2.1-T2V-14B-Diffusers"
        )
        
        progress(0.9, desc="Saving video...")
        
        # Save result
        os.makedirs("outputs", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"outputs/video_{timestamp}.mp4"
        
        with open(output_path, 'wb') as f:
            f.write(result)
        
        progress(1.0, desc="Complete!")
        
        status = f"""✅ **Video Generated!**

- Prompt: {prompt}
- Duration: ~{duration}s
- Method: HuggingFace API
- File: {output_path}
"""
        return output_path, status
        
    except Exception as e:
        # If HF inference fails, return helpful message
        return None, f"""⚠️ HuggingFace API returned error: {str(e)}

**Possible reasons:**
- Model is still loading (try again in 1-2 minutes)
- API rate limit reached (wait a few minutes)
- Model not available (try Replicate instead)

**Alternative:** Try Replicate API (has $10 free credits)
"""


def _generate_replicate(prompt, duration, token, progress):
    """Generate using Replicate API"""
    try:
        import replicate
        import requests
        
        progress(0.2, desc="Connecting to Replicate...")
        
        progress(0.3, desc="Generating video (1-3 minutes)...")
        
        # Use Wan 2.1 on Replicate
        output = replicate.run(
            "fofr/wan-2.1:latest",
            input={
                "prompt": prompt,
            }
        )
        
        progress(0.8, desc="Downloading video...")
        
        # Get video URL
        if isinstance(output, str):
            video_url = output
        elif isinstance(output, list) and len(output) > 0:
            video_url = output[0]
        else:
            return None, f"❌ Unexpected output format: {output}"
        
        # Download video
        response = requests.get(video_url)
        
        os.makedirs("outputs", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"outputs/video_{timestamp}.mp4"
        
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        progress(1.0, desc="Complete!")
        
        status = f"""✅ **Video Generated!**

- Prompt: {prompt}
- Duration: ~{duration}s
- Method: Replicate API
- File: {output_path}
"""
        return output_path, status
        
    except Exception as e:
        return None, f"❌ Replicate error: {str(e)}"


def create_interface():
    """Create Gradio interface"""
    
    with gr.Blocks(
        title="AI Video Generator",
        theme=gr.themes.Soft(primary_hue="blue")
    ) as demo:
        gr.Markdown("""
# 🎬 AI Video Generator
### Text-to-Video using Free APIs

Generate videos from text descriptions using cloud APIs. **No GPU required!**

---
        """)
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### ⚙️ Settings")
                
                prompt = gr.Textbox(
                    label="Video Prompt",
                    placeholder="Describe the video you want...\nExample: Ocean waves crashing on beach at sunset",
                    lines=4
                )
                
                with gr.Row():
                    duration = gr.Slider(
                        minimum=5,
                        maximum=30,
                        value=10,
                        step=5,
                        label="Duration (seconds)"
                    )
                    
                    method = gr.Dropdown(
                        choices=[
                            "HuggingFace (Free)",
                            "Replicate ($10 free)"
                        ],
                        value="HuggingFace (Free)",
                        label="Generation Method"
                    )
                
                generate_btn = gr.Button(
                    "🎬 Generate Video",
                    variant="primary",
                    size="lg"
                )
                
                gr.Markdown("""
### 📋 Example Prompts
- "Ocean waves crashing on beach at golden hour"
- "Futuristic city at night with flying cars"
- "Flower blooming in timelapse"
- "Astronaut walking on Mars surface"
                """)
                
                gr.Markdown("""
### 🔑 Setup (First Time Only)

**HuggingFace (Free):**
1. Get token: https://huggingface.co/settings/tokens
2. Set: `export HF_TOKEN=your_token`

**Replicate ($10 free credits):**
1. Sign up: https://replicate.com
2. Set: `export REPLICATE_API_TOKEN=your_token`
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
            fn=generate_video_api,
            inputs=[prompt, duration, method],
            outputs=[video_output, status_output]
        )
        
        gr.Markdown("""
---
### 💡 Tips
- Be specific in your prompt for better results
- Generation takes 2-5 minutes (cloud processing)
- Videos are saved to `outputs/` folder
- Share this link with friends!

**Built with** Gradio • HuggingFace • Replicate
        """)
    
    return demo


def main():
    print("=" * 70)
    print("🎬 AI VIDEO GENERATOR - LITE (API Only)")
    print("=" * 70)
    print()
    
    # Check for tokens
    hf_token = os.getenv("HF_TOKEN")
    replicate_token = os.getenv("REPLICATE_API_TOKEN")
    
    if hf_token:
        print("✅ HuggingFace token found")
    else:
        print("⚠️  No HF_TOKEN set - get free token at huggingface.co/settings/tokens")
    
    if replicate_token:
        print("✅ Replicate token found")
    else:
        print("⚠️  No REPLICATE_API_TOKEN set - get $10 free at replicate.com")
    
    print()
    
    # Create interface
    demo = create_interface()
    
    # Check share mode
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
