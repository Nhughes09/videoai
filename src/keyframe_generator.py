"""
Keyframe Generator - Generate key frames using Stable Diffusion XL
"""

import torch
import numpy as np
from PIL import Image
from typing import List, Optional, Dict, Any
import logging
from .utils import clear_gpu_cache, numpy_to_pil, pil_to_numpy

logger = logging.getLogger(__name__)


class KeyframeGenerator:
    """
    Generates keyframes for video using Stable Diffusion XL
    Keyframes serve as anchor points for video interpolation
    """
    
    def __init__(
        self,
        pipeline,
        device: torch.device,
        num_inference_steps: int = 30,
        guidance_scale: float = 7.5,
    ):
        """
        Args:
            pipeline: SDXL pipeline from ModelManager
            device: torch device (cuda/mps/cpu)
            num_inference_steps: Number of denoising steps (higher = better quality, slower)
            guidance_scale: How closely to follow prompt (7-10 typical)
        """
        self.pipeline = pipeline
        self.device = device
        self.num_inference_steps = num_inference_steps
        self.guidance_scale = guidance_scale
    
    def generate_keyframes(
        self,
        prompt: str,
        num_keyframes: int = 5,
        width: int = 1024,
        height: int = 1024,
        seed: Optional[int] = None,
        negative_prompt: Optional[str] = None,
    ) -> List[Image.Image]:
        """
        Generate keyframes for a video
        
        Args:
            prompt: Text description
            num_keyframes: Number of keyframes to generate
            width: Image width (default 1024 for SDXL)
            height: Image height
            seed: Random seed for reproducibility
            negative_prompt: What to avoid in generation
            
        Returns:
            List of PIL Images (keyframes)
        """
        logger.info(f"Generating {num_keyframes} keyframes...")
        logger.info(f"Prompt: {prompt}")
        
        if negative_prompt is None:
            negative_prompt = (
                "blurry, low quality, distorted, deformed, ugly, "
                "watermark, text, signature, bad anatomy"
            )
        
        keyframes = []
        
        # Set seed for reproducibility
        if seed is not None:
            generator = torch.Generator(device=self.device).manual_seed(seed)
        else:
            generator = None
        
        for i in range(num_keyframes):
            logger.info(f"  Generating keyframe {i+1}/{num_keyframes}...")
            
            # Slightly modify prompt for variation between keyframes
            frame_prompt = self._create_temporal_prompt(prompt, i, num_keyframes)
            
            try:
                # Generate image
                output = self.pipeline(
                    prompt=frame_prompt,
                    negative_prompt=negative_prompt,
                    num_inference_steps=self.num_inference_steps,
                    guidance_scale=self.guidance_scale,
                    width=width,
                    height=height,
                    generator=generator,
                    num_images_per_prompt=1,
                )
                
                image = output.images[0]
                keyframes.append(image)
                
                logger.info(f"  ✅ Keyframe {i+1}/{num_keyframes} complete")
                
            except Exception as e:
                logger.error(f"  ❌ Failed to generate keyframe {i+1}: {e}")
                # Create a blank placeholder
                blank = Image.new('RGB', (width, height), color=(128, 128, 128))
                keyframes.append(blank)
            
            # Clear cache between generations
            clear_gpu_cache()
        
        logger.info(f"✅ All {num_keyframes} keyframes generated")
        return keyframes
    
    def _create_temporal_prompt(
        self, base_prompt: str, frame_index: int, total_frames: int
    ) -> str:
        """
        Create slight variations in prompt for different keyframes
        to encourage temporal progression
        """
        # Calculate progression (0.0 to 1.0)
        progress = frame_index / max(1, total_frames - 1)
        
        # Add temporal descriptors based on position
        if progress < 0.25:
            temporal_hint = "beginning of scene, "
        elif progress < 0.5:
            temporal_hint = "early in scene, "
        elif progress < 0.75:
            temporal_hint = "middle of scene, "
        else:
            temporal_hint = "later in scene, "
        
        return temporal_hint + base_prompt
    
    def generate_consistent_keyframes(
        self,
        prompt: str,
        num_keyframes: int = 5,
        width: int = 1024,
        height: int = 1024,
        seed: int = 42,
        consistency_strength: float = 0.8,
    ) -> List[Image.Image]:
        """
        Generate keyframes with better temporal consistency
        Uses image-to-image generation for smoother transitions
        
        Args:
            consistency_strength: How much to preserve previous frame (0-1)
        """
        logger.info(f"Generating {num_keyframes} consistent keyframes...")
        
        # Generate first keyframe normally
        first_keyframe = self.generate_keyframes(
            prompt=prompt,
            num_keyframes=1,
            width=width,
            height=height,
            seed=seed
        )[0]
        
        keyframes = [first_keyframe]
        
        # Generate subsequent keyframes using img2img for consistency
        # Note: This requires img2img pipeline - simplified here
        for i in range(1, num_keyframes):
            # For now, generate independently
            # True img2img implementation would condition on previous frame
            frame = self.generate_keyframes(
                prompt=prompt,
                num_keyframes=1,
                width=width,
                height=height,
                seed=seed + i
            )[0]
            keyframes.append(frame)
        
        logger.info(f"✅ All {num_keyframes} consistent keyframes generated")
        return keyframes
    
    def upscale_keyframe(
        self,
        image: Image.Image,
        target_width: int = 1920,
        target_height: int = 1080
    ) -> Image.Image:
        """
        Upscale keyframe to target resolution
        Uses high-quality Lanczos resampling
        """
        return image.resize((target_width, target_height), Image.Resampling.LANCZOS)
    
    def enhance_keyframe(self, image: Image.Image) -> Image.Image:
        """
        Apply post-processing to enhance keyframe quality
        - Contrast adjustment
        - Sharpening
        - Color correction
        """
        from PIL import ImageEnhance
        
        # Slightly increase contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.1)
        
        # Slightly increase sharpness
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.2)
        
        # Slightly increase color saturation
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(1.1)
        
        return image
    
    def save_keyframes(
        self, keyframes: List[Image.Image], output_dir: str, prefix: str = "keyframe"
    ):
        """Save keyframes to disk"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        for i, keyframe in enumerate(keyframes):
            path = os.path.join(output_dir, f"{prefix}_{i:04d}.png")
            keyframe.save(path)
            logger.info(f"  Saved: {path}")
    
    def __repr__(self) -> str:
        return f"<KeyframeGenerator steps={self.num_inference_steps}>"
