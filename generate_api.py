#!/usr/bin/env python3
"""
API-First Video Generator
Uses FREE HuggingFace API - NO GPU NEEDED!
"""

import os
import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.api_generator import HybridVideoGenerator
from src.utils import setup_logging, ensure_dir


def main():
    parser = argparse.ArgumentParser(
        description="Generate videos using FREE APIs (no GPU needed!)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Quick start (uses FREE HuggingFace API)
  %(prog)s --prompt "Ocean waves at sunset"
  
  # Specify method
  %(prog)s --prompt "City at night" --method hf
  %(prog)s --prompt "Mountain landscape" --method replicate
  %(prog)s --prompt "DNA helix" --method local

Setup:
  1. Get FREE HuggingFace token: https://huggingface.co/settings/tokens
  2. Set environment variable: export HF_TOKEN=your_token_here
  3. Run: python generate_api.py --prompt "your prompt"
        """
    )
    
    parser.add_argument(
        "--prompt",
        type=str,
        required=True,
        help="Text description of video"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output path (default: outputs/video_TIMESTAMP.mp4)"
    )
    
    parser.add_argument(
        "--duration",
        type=int,
        default=10,
        help="Duration in seconds (default: 10)"
    )
    
    parser.add_argument(
        "--method",
        type=str,
        default="auto",
        choices=["auto", "hf", "replicate", "local"],
        help="Generation method (default: auto - tries HF first)"
    )
    
    parser.add_argument(
        "--hf-token",
        type=str,
        default=None,
        help="HuggingFace token (or set HF_TOKEN env var)"
    )
    
    parser.add_argument(
        "--replicate-token",
        type=str,
        default=None,
        help="Replicate token (or set REPLICATE_API_TOKEN env var)"
    )
    
    parser.add_argument(
        "--prefer-local",
        action="store_true",
        help="Prefer local generation over APIs"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging("INFO")
    logger.info("=" * 70)
    logger.info("🌐 API-BASED VIDEO GENERATOR")
    logger.info("=" * 70)
    
    # Check for tokens
    hf_token = args.hf_token or os.getenv("HF_TOKEN")
    replicate_token = args.replicate_token or os.getenv("REPLICATE_API_TOKEN")
    
    if not hf_token and args.method in ["auto", "hf"]:
        logger.warning("\n⚠️  No HuggingFace token found!")
        logger.warning("   Get a FREE token at: https://huggingface.co/settings/tokens")
        logger.warning("   Then set: export HF_TOKEN=your_token_here")
        
        if args.method == "hf":
            logger.error("\n❌ HF method requires token. Exiting.")
            sys.exit(1)
        else:
            logger.info("\n   Will try other methods...")
    
    if not replicate_token and args.method == "replicate":
        logger.error("\n❌ Replicate method requires token")
        logger.error("   Get $10 free credits at: https://replicate.com")
        logger.error("   Then set: export REPLICATE_API_TOKEN=your_token")
        sys.exit(1)
    
    # Setup output path
    if args.output is None:
        from datetime import datetime
        from src.utils import sanitize_filename
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_prompt = sanitize_filename(args.prompt[:30])
        output_path = f"outputs/video_{safe_prompt}_{timestamp}.mp4"
    else:
        output_path = args.output
    
    ensure_dir(os.path.dirname(output_path) or "outputs")
    
    # Generate video
    try:
        logger.info(f"\n📝 Prompt: {args.prompt}")
        logger.info(f"⏱️  Duration: {args.duration}s")
        logger.info(f"🔧 Method: {args.method}")
        logger.info(f"📁 Output: {output_path}\n")
        
        generator = HybridVideoGenerator(
            hf_token=hf_token,
            replicate_token=replicate_token,
            prefer_local=args.prefer_local
        )
        
        result = generator.generate(
            prompt=args.prompt,
            duration=args.duration,
            output_path=output_path,
            method=args.method
        )
        
        logger.info("\n" + "=" * 70)
        logger.info("✅ VIDEO GENERATION COMPLETE!")
        logger.info(f"📁 Output: {result}")
        logger.info("=" * 70)
        
    except KeyboardInterrupt:
        logger.info("\n\n⚠️  Generation cancelled")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n\n❌ Error: {e}")
        logger.exception(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
