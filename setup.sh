#!/bin/bash

# Quick setup script for Sora AI Video Generator

echo "🚀 Setting up Sora AI Video Generator..."
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

if [ $? -ne 0 ]; then
    echo "❌ Python 3 not found. Please install Python 3.10 or higher."
    exit 1
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo ""
echo "Installing dependencies (this may take a while)..."
pip install -r requirements.txt

# Create necessary directories
echo ""
echo "Creating directories..."
mkdir -p models outputs config

# Run system test
echo ""
echo "Running system tests..."
python test_system.py

echo ""
echo "=" * 70
echo "✅ Setup complete!"
echo "=" * 70
echo ""
echo "Next steps:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Test with: python test_system.py"
echo "  3. Generate video: python generate_video.py --prompt 'your prompt'"
echo "  4. Or run web UI: python app.py"
echo ""
echo "Happy creating! 🎬"
