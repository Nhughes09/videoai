#!/usr/bin/env python3
"""
AI Video Generator - Uses FREE HuggingFace Inference API
NO model download needed! Works immediately!
"""

import os
import gradio as gr
from datetime import datetime
import time
import requests
import tempfile

print("=" * 60)
print("🎬 AI VIDEO GENERATOR - API MODE")
print("=" * 60)
print()

# Get HF token from environment
HF_TOKEN = os.getenv("HF_TOKEN", "")

if not HF_TOKEN:
    print("⚠️  No HF_TOKEN set. Get one free at:")
    print("   https://huggingface.co/settings/tokens")
    print()
    print("   Then run: export HF_TOKEN=your_token_here")
    print()


def generate_video_api(prompt: str, progress=gr.Progress()):
    """Generate video using HuggingFace Inference API"""
    
    if not prompt:
        return None, "❌ Enter a prompt!"
    
    if not HF_TOKEN:
        return None, """❌ **No HuggingFace Token!**

1. Go to https://huggingface.co/settings/tokens
2. Create a free token
3. Run: `export HF_TOKEN=your_token`
4. Restart this app
"""
    
    print(f"\n🎬 Generating: {prompt}")
    progress(0.1, desc="Sending to HuggingFace...")
    
    # Use HF Inference API
    API_URL = "https://api-inference.huggingface.co/models/ali-vilab/text-to-video-ms-1.7b"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    
    try:
        start = time.time()
        
        progress(0.2, desc="Waiting for GPU...")
        response = requests.post(
            API_URL,
            headers=headers,
            json={"inputs": prompt},
            timeout=300,  # 5 min timeout
        )
        
        if response.status_code == 503:
            return None, "⏳ Model is loading on HuggingFace servers. Try again in 1-2 minutes!"
        
        if response.status_code != 200:
            return None, f"❌ API Error: {response.status_code}\n{response.text}"
        
        progress(0.8, desc="Saving video...")
        
        # Save video
        os.makedirs("outputs", exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = f"outputs/video_{ts}.mp4"
        
        with open(out_path, "wb") as f:
            f.write(response.content)
        
        gen_time = time.time() - start
        print(f"✅ Done in {gen_time:.1f}s: {out_path}")
        
        progress(1.0, desc="Done!")
        
        return out_path, f"✅ **Done!** Generated in {gen_time:.1f}s"
        
    except requests.exceptions.Timeout:
        return None, "⏳ Request timed out. The model might be loading - try again!"
    except Exception as e:
        return None, f"❌ Error: {str(e)}"


# UI
with gr.Blocks(title="AI Video Generator") as demo:
    gr.Markdown("""
# 🎬 AI Video Generator (API Mode)
**Uses HuggingFace's FREE cloud GPUs - no local download needed!**

Get your free token at [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
    """)
    
    with gr.Row():
        with gr.Column():
            prompt = gr.Textbox(
                label="Prompt",
                placeholder="A sunset over the ocean with gentle waves",
                lines=2,
            )
            btn = gr.Button("🎬 Generate", variant="primary", size="lg")
            
            gr.Markdown("""
**Notes:**
- First request may take 2-3 min (model loading)
- Subsequent requests are faster (~30s)
- 100% free with HuggingFace account
            """)
        
        with gr.Column():
            video = gr.Video(label="Video")
            status = gr.Markdown("Ready! Enter a prompt and click Generate.")
    
    btn.click(generate_video_api, [prompt], [video, status])
    
    gr.Markdown("[GitHub](https://github.com/Nhughes09/videoai)")


print("🌐 Starting server...")
share = os.getenv("GRADIO_SHARE", "false").lower() == "true"
if share: print("🔗 Creating public link...")
print("📍 http://localhost:7860\n")

demo.launch(server_name="0.0.0.0", server_port=7860, share=share)
