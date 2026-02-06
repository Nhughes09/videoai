#!/usr/bin/env python3
"""
INSTANT START - Minimal dependencies test
Run this first to verify Python and basic setup
"""

import sys
import subprocess

def check_python():
    """Check Python version"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    print(f"   Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("   ❌ Python 3.8+ required")
        return False
    print("   ✅ Python version OK")
    return True

def check_pip():
    """Check pip is installed"""
    print("\n📦 Checking pip...")
    try:
        import pip
        print(f"   pip {pip.__version__}")
        print("   ✅ pip installed")
        return True
    except ImportError:
        print("   ❌ pip not found")
        return False

def install_dependencies():
    """Offer to install dependencies"""
    print("\n" + "="*70)
    print("📥 INSTALLATION")
    print("="*70)
    
    response = input("\nInstall all dependencies now? (y/n): ").lower().strip()
    
    if response == 'y':
        print("\n⏳ Installing dependencies (this will take 5-10 minutes)...")
        print("   Downloading PyTorch, Diffusers, and other packages...")
        
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
            ])
            print("\n✅ Installation complete!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"\n❌ Installation failed: {e}")
            return False
    else:
        print("\nℹ️  To install later, run:")
        print("   pip install -r requirements.txt")
        return False

def main():
    print("="*70)
    print("🚀 SORA AI VIDEO GENERATOR - QUICK START CHECK")
    print("="*70)
    print()
    
    # Check Python
    if not check_python():
        print("\n❌ Please install Python 3.8 or higher")
        sys.exit(1)
    
    # Check pip
    if not check_pip():
        print("\n❌ Please install pip")
        sys.exit(1)
    
    # Try importing key packages
    print("\n📚 Checking for required packages...")
    
    missing = []
    packages = {
        'torch': 'PyTorch',
        'diffusers': 'Diffusers',
        'PIL': 'Pillow',
        'gradio': 'Gradio',
    }
    
    for module, name in packages.items():
        try:
            __import__(module)
            print(f"   ✅ {name} installed")
        except ImportError:
            print(f"   ❌ {name} missing")
            missing.append(name)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        installed = install_dependencies()
        
        if not installed:
            print("\n" + "="*70)
            print("📋 NEXT STEPS")
            print("="*70)
            print("\n1. Install dependencies:")
            print("   pip install -r requirements.txt")
            print("\n2. Run this script again:")
            print("   python instant_start.py")
            sys.exit(0)
    
    # All good!
    print("\n" + "="*70)
    print("✅ SYSTEM READY!")
    print("="*70)
    print("\n🎬 You can now generate videos!")
    print("\nChoose an option:")
    print()
    print("  A) Web Interface (Recommended)")
    print("     python app.py")
    print()
    print("  B) Command Line")
    print("     python generate_video.py --prompt 'your text here'")
    print()
    print("  C) Run full system test")
    print("     python test_system.py")
    print()
    
    choice = input("Start now? (A/B/C/N): ").upper().strip()
    
    if choice == 'A':
        print("\n🌐 Starting web interface...")
        subprocess.call([sys.executable, "app.py"])
    elif choice == 'B':
        prompt = input("\nEnter your prompt: ")
        print(f"\n🎬 Generating video for: '{prompt}'")
        subprocess.call([
            sys.executable, "generate_video.py",
            "--prompt", prompt,
            "--duration", "10",
            "--resolution", "1080p"
        ])
    elif choice == 'C':
        print("\n🧪 Running system tests...")
        subprocess.call([sys.executable, "test_system.py"])
    else:
        print("\n👍 Ready when you are! Use the commands above to start.")

if __name__ == "__main__":
    main()
