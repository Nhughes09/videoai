#!/usr/bin/env python3
"""
Quick test script to verify system is working
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.utils import get_device, get_system_info
from src.prompt_analyzer import PromptAnalyzer


def test_device():
    """Test device detection"""
    print("🔍 Testing device detection...")
    device = get_device()
    print(f"✅ Device: {device}\n")
    return device


def test_system_info():
    """Test system info"""
    print("📊 Testing system info...")
    info = get_system_info()
    for key, value in info.items():
        print(f"  {key}: {value}")
    print("✅ System info retrieved\n")
    return info


def test_prompt_analyzer():
    """Test prompt analyzer"""
    print("📝 Testing prompt analyzer...")
    
    analyzer = PromptAnalyzer()
    
    test_prompts = [
        "A futuristic city at sunset with flying cars",
        "Ocean waves crashing on a beach at golden hour",
        "Microscopic view of cells dividing with DNA visible",
    ]
    
    for prompt in test_prompts:
        scene = analyzer.analyze(prompt)
        enhanced = analyzer.create_enhanced_prompt(scene)
        
        print(f"\nPrompt: {prompt}")
        print(f"  Subject: {scene.subject}")
        print(f"  Action: {scene.action}")
        print(f"  Style: {scene.style}")
        print(f"  Enhanced: {enhanced[:100]}...")
    
    print("\n✅ Prompt analyzer working\n")


def test_model_download():
    """Test model downloading (doesn't actually download, just checks)"""
    print("📦 Testing model manager...")
    
    from src.model_manager import ModelManager
    
    manager = ModelManager(cache_dir="./models")
    info = manager.get_model_info()
    
    print(f"  Available models: {info['available_models']}")
    print(f"  Cache directory: {info['cache_dir']}")
    
    print("✅ Model manager working\n")


def main():
    """Run all tests"""
    print("=" * 70)
    print("🧪 RUNNING SYSTEM TESTS")
    print("=" * 70)
    print()
    
    try:
        test_device()
        test_system_info()
        test_prompt_analyzer()
        test_model_download()
        
        print("=" * 70)
        print("✅ ALL TESTS PASSED!")
        print("=" * 70)
        print()
        print("🎉 Your system is ready to generate videos!")
        print()
        print("Next steps:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Run CLI: python generate_video.py --prompt 'your prompt'")
        print("  3. Or run web UI: python app.py")
        print()
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
