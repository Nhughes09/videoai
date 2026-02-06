#!/usr/bin/env python3
"""
Main CLI for video generation
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils import (
    setup_logging,
    get_device,
    get_system_info,
    estimate_generation_time,
    validate_prompt,
    sanitize_filename,
    ensure_dir,
)
from src.prompt_analyzer import PromptAnalyzer
from src.model_manager import ModelManager
from src.keyframe_generator import KeyframeGenerator
from src.video_interpolator import VideoInterpolator
from src.post_processor import PostProcessor


def main():
    parser = argparse.ArgumentParser(
        description="Generate AI videos from text prompts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --prompt "A futuristic city at sunset with flying cars"
  %(prog)s --prompt "Ocean waves crashing" --duration 30 --style cinematic
  %(prog)s --prompt "DNA helix rotating" --resolution 720p --fps 24
        """
    )
    
    # Required arguments
    parser.add_argument(
        "--prompt",
        type=str,
        required=True,
        help="Text description of the video to generate"
    )
    
    # Optional arguments
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output video path (default: outputs/video_TIMESTAMP.mp4)"
    )
    
    parser.add_argument(
        "--duration",
        type=int,
        default=10,
        help="Video duration in seconds (default: 10, max: 60)"
    )
    
    parser.add_argument(
        "--fps",
        type=int,
        default=30,
        choices=[24, 30, 60],
        help="Frames per second (default: 30)"
    )
    
    parser.add_argument(
        "--resolution",
        type=str,
        default="1080p",
        choices=["720p", "1080p", "4k"],
        help="Output resolution (default: 1080p)"
    )
    
    parser.add_argument(
        "--style",
        type=str,
        default="photorealistic",
        choices=["cinematic", "documentary", "animated", "artistic", "photorealistic"],
        help="Visual style (default: photorealistic)"
    )
    
    parser.add_argument(
        "--keyframes",
        type=int,
        default=5,
        help="Number of keyframes to generate (default: 5)"
    )
    
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducibility"
    )
    
    parser.add_argument(
        "--no-upscale",
        action="store_true",
        help="Skip upscaling step"
    )
    
    parser.add_argument(
        "--no-color-grade",
        action="store_true",
        help="Skip color grading step"
    )
    
    parser.add_argument(
        "--model-dir",
        type=str,
        default="./models",
        help="Directory for model cache (default: ./models)"
    )
    
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level (default: INFO)"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging(args.log_level)
    logger.info("=" * 70)
    logger.info("🎬 SORA-INSPIRED AI VIDEO GENERATOR")
    logger.info("=" * 70)
    
    # Validate inputs
    if not validate_prompt(args.prompt):
        logger.error("❌ Invalid prompt. Must be 5-1000 characters.")
        sys.exit(1)
    
    if args.duration < 1 or args.duration > 60:
        logger.error("❌ Duration must be between 1 and 60 seconds")
        sys.exit(1)
    
    # Get device info
    device = get_device()
    system_info = get_system_info()
    logger.info("\n📊 System Information:")
    for key, value in system_info.items():
        logger.info(f"  {key}: {value}")
    
    # Parse resolution
    resolution_map = {
        "720p": (1280, 720),
        "1080p": (1920, 1080),
        "4k": (3840, 2160),
    }
    target_resolution = resolution_map[args.resolution]
    
    # Estimate generation time
    estimated_time = estimate_generation_time(
        args.duration, target_resolution, args.fps, device
    )
    logger.info(f"\n⏱️  Estimated generation time: {estimated_time:.1f} minutes")
    logger.info("   (First run will be slower due to model downloads)")
    
    # Analyze prompt
    logger.info(f"\n📝 Analyzing prompt...")
    logger.info(f"   Prompt: \"{args.prompt}\"")
    
    analyzer = PromptAnalyzer()
    scene = analyzer.analyze(args.prompt, duration=args.duration)
    
    logger.info(f"   Subject: {scene.subject}")
    logger.info(f"   Action: {scene.action}")
    logger.info(f"   Setting: {scene.setting}")
    logger.info(f"   Style: {scene.style}")
    logger.info(f"   Camera: {scene.camera_movement}")
    logger.info(f"   Lighting: {scene.lighting}")
    
    # Initialize model manager
    logger.info(f"\n🤖 Initializing models...")
    model_manager = ModelManager(cache_dir=args.model_dir)
    
    try:
        # Load models
        logger.info("   Loading SDXL for keyframe generation...")
        sdxl_pipeline = model_manager.load_sdxl_pipeline(device)
        
        logger.info("   Loading SVD for video interpolation...")
        svd_pipeline = model_manager.load_svd_pipeline(device)
        
        # Initialize generators
        keyframe_gen = KeyframeGenerator(sdxl_pipeline, device)
        video_interp = VideoInterpolator(svd_pipeline, device, fps=args.fps)
        post_proc = PostProcessor(target_resolution, args.fps)
        
        # Generate keyframes
        logger.info(f"\n🎨 Generating {args.keyframes} keyframes...")
        enhanced_prompt = analyzer.create_enhanced_prompt(scene)
        logger.info(f"   Enhanced prompt: \"{enhanced_prompt}\"")
        
        keyframes = keyframe_gen.generate_keyframes(
            prompt=enhanced_prompt,
            num_keyframes=args.keyframes,
            seed=args.seed,
        )
        
        # Upscale keyframes to target resolution
        logger.info(f"\n📐 Upscaling keyframes to {target_resolution}...")
        keyframes = [
            keyframe_gen.upscale_keyframe(kf, target_resolution[0], target_resolution[1])
            for kf in keyframes
        ]
        
        # Interpolate frames
        logger.info(f"\n🎞️  Interpolating frames...")
        duration_per_keyframe = args.duration / max(1, args.keyframes - 1)
        frames = video_interp.interpolate_between_keyframes(
            keyframes,
            duration_per_keyframe=duration_per_keyframe,
        )
        
        # Post-process
        logger.info(f"\n✨ Post-processing...")
        frames = post_proc.process_video(
            frames,
            apply_upscaling=not args.no_upscale,
            apply_color_grading=not args.no_color_grade,
            apply_stabilization=False,  # Too slow for default
        )
        
        # Save video
        if args.output is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_prompt = sanitize_filename(args.prompt[:30])
            output_path = f"outputs/video_{safe_prompt}_{timestamp}.mp4"
        else:
            output_path = args.output
        
        ensure_dir(os.path.dirname(output_path) or "outputs")
        
        post_proc.save_video(frames, output_path, crf=18)
        
        logger.info("\n" + "=" * 70)
        logger.info("✅ VIDEO GENERATION COMPLETE!")
        logger.info(f"📁 Output: {output_path}")
        logger.info(f"⏱️  Duration: {len(frames) / args.fps:.2f}s")
        logger.info(f"🎞️  Frames: {len(frames)}")
        logger.info(f"📐 Resolution: {target_resolution[0]}x{target_resolution[1]}")
        logger.info("=" * 70)
        
    except KeyboardInterrupt:
        logger.info("\n\n⚠️  Generation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n\n❌ Error during generation: {e}")
        logger.exception(e)
        sys.exit(1)
    finally:
        # Cleanup
        model_manager.unload_all()


if __name__ == "__main__":
    main()
