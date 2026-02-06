#!/bin/bash

# Share With Friends - Creates Public Link
# This runs the app and creates a public URL you can share

echo "🌍 Creating public share link..."
echo ""
echo "This will:"
echo "  1. Start the video generator on YOUR computer"
echo "  2. Create a public https://xxxxx.gradio.live link"
echo "  3. You share that link with friends"
echo "  4. They can use it while your computer runs it"
echo ""
echo "⚠️  Your computer must stay on and running!"
echo ""

# Enable share mode
export GRADIO_SHARE=true

# Run the app
python app.py

# Link expires when you stop the script (Ctrl+C)
