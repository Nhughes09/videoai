"""
API-Based Video Generation
Uses Hugging Face Inference API and Replicate as alternatives to local generation
"""

import os
import requests
from typing import Optional, List
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class HuggingFaceVideoAPI:
    """
    Generate videos using Hugging Face's FREE Inference API
    Models: Wan-2.1, Open-Sora, CogVideoX
    """
    
    # Available free models
    MODELS = {
        "wan": "Wan-AI/Wan2.1-T2V-14B-Diffusers",
        "opensora": "hpcai-tech/Open-Sora",
        "cogvideox": "THUDM/CogVideoX-5b",
    }
    
    def __init__(self, token: Optional[str] = None):
        """
        Args:
            token: HuggingFace API token (get free at huggingface.co/settings/tokens)
        """
        self.token = token or os.getenv("HF_TOKEN")
        
        if not self.token:
            logger.warning(
                "⚠️  No HuggingFace token found. "
                "Get a free token at: https://huggingface.co/settings/tokens"
            )
    
    def generate_video(
        self,
        prompt: str,
        duration: int = 10,
        model: str = "wan",
        output_path: str = "output.mp4"
    ) -> str:
        """
        Generate video using HuggingFace Inference API
        
        Args:
            prompt: Text description
            duration: Duration in seconds (API typically generates 10-14s clips)
            model: Model to use ("wan", "opensora", "cogvideox")
            output_path: Where to save video
            
        Returns:
            Path to generated video
        """
        if not self.token:
            raise ValueError(
                "HuggingFace token required. "
                "Set HF_TOKEN environment variable or pass token parameter. "
                "Get free token at: https://huggingface.co/settings/tokens"
            )
        
        model_id = self.MODELS.get(model, self.MODELS["wan"])
        
        logger.info(f"🌐 Generating video via HuggingFace API...")
        logger.info(f"   Model: {model_id}")
        logger.info(f"   Prompt: {prompt}")
        
        # For long videos, generate multiple clips
        if duration > 14:
            return self._generate_long_video(prompt, duration, model, output_path)
        
        # Generate single clip
        return self._generate_clip(prompt, model_id, output_path)
    
    def _generate_clip(
        self, prompt: str, model_id: str, output_path: str
    ) -> str:
        """Generate a single video clip via API"""
        
        try:
            from huggingface_hub import InferenceClient
            
            client = InferenceClient(token=self.token)
            
            logger.info("   Calling API...")
            
            # Note: text_to_video API is still experimental
            # This is a placeholder - actual implementation depends on HF API updates
            result = client.text_to_video(
                prompt=prompt,
                model=model_id
            )
            
            # Save result
            with open(output_path, 'wb') as f:
                f.write(result)
            
            logger.info(f"✅ Video saved: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"❌ API generation failed: {e}")
            raise
    
    def _generate_long_video(
        self, prompt: str, duration: int, model: str, output_path: str
    ) -> str:
        """Generate long video by stitching multiple clips"""
        
        num_clips = (duration + 13) // 14  # 14s per clip
        clips = []
        
        logger.info(f"   Generating {num_clips} clips to reach {duration}s...")
        
        for i in range(num_clips):
            clip_prompt = f"{prompt} (scene {i+1}/{num_clips})"
            clip_path = f"temp_clip_{i}.mp4"
            
            try:
                self._generate_clip(clip_prompt, self.MODELS[model], clip_path)
                clips.append(clip_path)
            except Exception as e:
                logger.warning(f"   Clip {i+1} failed: {e}")
        
        if not clips:
            raise RuntimeError("Failed to generate any clips")
        
        # Stitch clips together
        logger.info("   Stitching clips...")
        final_path = self._stitch_clips(clips, output_path)
        
        # Cleanup temp files
        for clip in clips:
            try:
                os.remove(clip)
            except:
                pass
        
        return final_path
    
    def _stitch_clips(self, clips: List[str], output_path: str) -> str:
        """Stitch video clips using FFmpeg"""
        import subprocess
        
        # Create concat file
        concat_file = "concat_list.txt"
        with open(concat_file, 'w') as f:
            for clip in clips:
                f.write(f"file '{clip}'\n")
        
        # Run FFmpeg
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_file,
            "-c", "copy",
            output_path
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        os.remove(concat_file)
        
        return output_path


class ReplicateVideoAPI:
    """
    Generate videos using Replicate API
    $10 free credits, then pay-per-use (~$0.002-0.004/second)
    """
    
    def __init__(self, token: Optional[str] = None):
        """
        Args:
            token: Replicate API token (get at replicate.com)
        """
        self.token = token or os.getenv("REPLICATE_API_TOKEN")
        
        if not self.token:
            logger.warning(
                "⚠️  No Replicate token found. "
                "Get token at: https://replicate.com/account/api-tokens"
            )
    
    def generate_video(
        self,
        prompt: str,
        duration: int = 10,
        model: str = "wan",
        output_path: str = "output.mp4"
    ) -> str:
        """
        Generate video using Replicate API
        
        Args:
            prompt: Text description
            duration: Duration in seconds
            model: Model name
            output_path: Where to save
            
        Returns:
            Path to generated video
        """
        if not self.token:
            raise ValueError(
                "Replicate token required. "
                "Set REPLICATE_API_TOKEN environment variable. "
                "Get free $10 credits at: https://replicate.com"
            )
        
        try:
            import replicate
            
            logger.info(f"🌐 Generating video via Replicate API...")
            logger.info(f"   Prompt: {prompt}")
            logger.info(f"   Duration: {duration}s")
            
            # Use Wan 2.1 (best quality on Replicate)
            output = replicate.run(
                "fofr/wan-2.1:latest",
                input={
                    "prompt": prompt,
                    "duration": duration,
                }
            )
            
            # Download result
            if isinstance(output, str):
                video_url = output
            else:
                video_url = output[0]
            
            logger.info("   Downloading video...")
            response = requests.get(video_url)
            
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"✅ Video saved: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"❌ Replicate generation failed: {e}")
            raise


class HybridVideoGenerator:
    """
    Hybrid generator that tries APIs first, falls back to local
    """
    
    def __init__(
        self,
        hf_token: Optional[str] = None,
        replicate_token: Optional[str] = None,
        prefer_local: bool = False
    ):
        """
        Args:
            hf_token: HuggingFace token
            replicate_token: Replicate token
            prefer_local: If True, use local first; if False, use APIs first
        """
        self.hf_api = HuggingFaceVideoAPI(hf_token)
        self.replicate_api = ReplicateVideoAPI(replicate_token)
        self.prefer_local = prefer_local
    
    def generate(
        self,
        prompt: str,
        duration: int = 10,
        output_path: str = "output.mp4",
        method: str = "auto"
    ) -> str:
        """
        Generate video using best available method
        
        Args:
            prompt: Text description
            duration: Duration in seconds
            output_path: Output file
            method: "auto", "hf", "replicate", or "local"
            
        Returns:
            Path to generated video
        """
        if method == "hf":
            return self.hf_api.generate_video(prompt, duration, output_path=output_path)
        
        elif method == "replicate":
            return self.replicate_api.generate_video(prompt, duration, output_path=output_path)
        
        elif method == "local":
            return self._generate_local(prompt, duration, output_path)
        
        else:  # auto
            # Try methods in order based on preference
            methods = (
                ["local", "hf", "replicate"] if self.prefer_local
                else ["hf", "replicate", "local"]
            )
            
            for attempt_method in methods:
                try:
                    logger.info(f"Trying method: {attempt_method}")
                    return self.generate(prompt, duration, output_path, method=attempt_method)
                except Exception as e:
                    logger.warning(f"{attempt_method} failed: {e}")
                    continue
            
            raise RuntimeError("All generation methods failed")
    
    def _generate_local(self, prompt: str, duration: int, output_path: str) -> str:
        """Generate using local models"""
        logger.info("📍 Generating locally (may be slow on first run)...")
        
        # Import local generation (from main pipeline)
        from src.utils import get_device
        from src.model_manager import ModelManager
        from src.prompt_analyzer import PromptAnalyzer
        from src.keyframe_generator import KeyframeGenerator
        from src.video_interpolator import VideoInterpolator
        from src.post_processor import PostProcessor
        
        device = get_device()
        manager = ModelManager()
        
        # Load models
        sdxl = manager.load_sdxl_pipeline(device)
        svd = manager.load_svd_pipeline(device)
        
        # Generate
        analyzer = PromptAnalyzer()
        scene = analyzer.analyze(prompt, duration)
        enhanced_prompt = analyzer.create_enhanced_prompt(scene)
        
        keyframe_gen = KeyframeGenerator(sdxl, device)
        keyframes = keyframe_gen.generate_keyframes(enhanced_prompt, num_keyframes=5)
        
        video_interp = VideoInterpolator(svd, device)
        frames = video_interp.interpolate_between_keyframes(keyframes)
        
        post_proc = PostProcessor((1920, 1080), 30)
        frames = post_proc.process_video(frames)
        post_proc.save_video(frames, output_path)
        
        return output_path
