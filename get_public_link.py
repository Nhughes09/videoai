#!/usr/bin/env python3
"""
ONE-CLICK PUBLIC LINK GENERATOR
Run this to get a public URL you can share
"""

import os
import sys

def main():
    print("=" * 70)
    print("🌍 CREATING PUBLIC VIDEO GENERATOR LINK")
    print("=" * 70)
    print()
    print("This will:")
    print("  1. Start the video generator")
    print("  2. Create a public https://xxxxx.gradio.live link")
    print("  3. You can share this link with anyone!")
    print()
    print("⚠️  IMPORTANT:")
    print("  - Keep this terminal window open")
    print("  - Your computer must stay on")
    print("  - Press Ctrl+C to stop")
    print()
    
    # Check if dependencies installed
    try:
        import gradio
        print("✅ Gradio installed")
    except ImportError:
        print("⚠️  Installing Gradio (this may take a minute)...")
        os.system(f"{sys.executable} -m pip install gradio huggingface-hub replicate")
    
    print()
    print("🚀 Starting public server...")
    print()
    print("-" * 70)
    print()
    
    # Enable share mode
    os.environ["GRADIO_SHARE"] = "true"
    
    # Run the app
    import subprocess
    subprocess.call([sys.executable, "app.py"])

if __name__ == "__main__":
    main()
