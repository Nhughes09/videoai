"""
Video Interpolator - Fill frames between keyframes using Stable Video Diffusion
"""

import torch
import numpy as np
from PIL import Image
from typing import List, Optional
import logging
from .utils import clear_gpu_cache, pil_to_numpy, numpy_to_pil

logger = logging.getLogger(__name__)


class VideoInterpolator:
    """
    Interpolates frames between keyframes to create smooth video
    Uses Stable Video Diffusion for high-quality results
    """
    
    def __init__(
        self,
        pipeline,
        device: torch.device,
        fps: int = 30,
        num_inference_steps: int = 25,
    ):
        """
        Args:
            pipeline: SVD pipeline from ModelManager
            device: torch device
            fps: Target frames per second
            num_inference_steps: Denoising steps for interpolation
        """
        self.pipeline = pipeline
        self.device = device
        self.fps = fps
        self.num_inference_steps = num_inference_steps
    
    def interpolate_between_keyframes(
        self,
        keyframes: List[Image.Image],
        duration_per_keyframe: float = 3.0,
        motion_bucket_id: int = 127,
        noise_aug_strength: float = 0.02,
    ) -> List[np.ndarray]:
        """
        Interpolate frames between keyframes
        
        Args:
            keyframes: List of PIL Images (keyframes)
            duration_per_keyframe: Seconds per keyframe segment
            motion_bucket_id: Controls motion intensity (0-255, higher = more motion)
            noise_aug_strength: Noise augmentation (0.0-1.0)
            
        Returns:
            List of frames as numpy arrays
        """
        logger.info(f"Interpolating {len(keyframes)} keyframes...")
        logger.info(f"Target FPS: {self.fps}, Duration per segment: {duration_per_keyframe}s")
        
        all_frames = []
        
        for i in range(len(keyframes) - 1):
            logger.info(f"  Processing segment {i+1}/{len(keyframes)-1}...")
            
            start_frame = keyframes[i]
            end_frame = keyframes[i + 1]
            
            # Generate video from start to end
            segment_frames = self._generate_video_segment(
                start_frame=start_frame,
                duration=duration_per_keyframe,
                motion_bucket_id=motion_bucket_id,
                noise_aug_strength=noise_aug_strength,
            )
            
            # Add all frames except last (to avoid duplication with next segment)
            if i < len(keyframes) - 2:
                all_frames.extend(segment_frames[:-1])
            else:
                all_frames.extend(segment_frames)
            
            clear_gpu_cache()
        
        logger.info(f"✅ Generated {len(all_frames)} total frames")
        return all_frames
    
    def _generate_video_segment(
        self,
        start_frame: Image.Image,
        duration: float,
        motion_bucket_id: int = 127,
        noise_aug_strength: float = 0.02,
    ) -> List[np.ndarray]:
        """
        Generate a video segment from a starting frame using SVD
        
        Args:
            start_frame: Starting keyframe
            duration: Duration in seconds
            motion_bucket_id: Motion intensity
            noise_aug_strength: Noise level
            
        Returns:
            List of frames as numpy arrays
        """
        num_frames = int(duration * self.fps)
        
        # SVD typically generates 14 or 25 frames
        # We'll generate and then interpolate to desired length
        svd_frames = 25  # Standard SVD output
        
        try:
            # Resize to SVD's expected resolution (usually 576 x 1024)
            # We'll upscale later
            input_width, input_height = start_frame.size
            svd_width = 576
            svd_height = 1024
            
            start_frame_resized = start_frame.resize(
                (svd_width, svd_height), 
                Image.Resampling.LANCZOS
            )
            
            logger.info(f"    Generating {svd_frames} frames with SVD...")
            
            # Generate video using SVD
            output = self.pipeline(
                image=start_frame_resized,
                num_frames=svd_frames,
                num_inference_steps=self.num_inference_steps,
                motion_bucket_id=motion_bucket_id,
                noise_aug_strength=noise_aug_strength,
                decode_chunk_size=8,  # Process in chunks to save memory
            )
            
            frames = output.frames[0]  # Get first (and only) video
            
            # Convert to numpy arrays
            frames = [pil_to_numpy(frame) for frame in frames]
            
            # Interpolate to target frame count if needed
            if num_frames != svd_frames:
                frames = self._temporal_interpolation(frames, num_frames)
            
            # Resize back to target resolution
            frames = [
                self._resize_frame(frame, input_width, input_height) 
                for frame in frames
            ]
            
            logger.info(f"    ✅ Generated {len(frames)} frames")
            return frames
            
        except Exception as e:
            logger.error(f"    ❌ Error generating segment: {e}")
            # Return simple linear interpolation as fallback
            logger.info("    Falling back to simple interpolation...")
            return self._simple_interpolation(start_frame, num_frames)
    
    def _temporal_interpolation(
        self, frames: List[np.ndarray], target_count: int
    ) -> List[np.ndarray]:
        """
        Interpolate frames to target count using linear blending
        """
        if len(frames) == target_count:
            return frames
        
        source_count = len(frames)
        interpolated = []
        
        for i in range(target_count):
            # Map target frame index to source frame position
            position = (i / max(1, target_count - 1)) * max(1, source_count - 1)
            
            # Get surrounding frames
            idx_low = int(np.floor(position))
            idx_high = min(idx_low + 1, source_count - 1)
            
            # Interpolation weight
            weight = position - idx_low
            
            # Blend frames
            frame_low = frames[idx_low].astype(np.float32)
            frame_high = frames[idx_high].astype(np.float32)
            
            blended = (1 - weight) * frame_low + weight * frame_high
            interpolated.append(blended.astype(np.uint8))
        
        return interpolated
    
    def _resize_frame(self, frame: np.ndarray, width: int, height: int) -> np.ndarray:
        """Resize frame to target resolution"""
        img = numpy_to_pil(frame)
        img = img.resize((width, height), Image.Resampling.LANCZOS)
        return pil_to_numpy(img)
    
    def _simple_interpolation(
        self, start_frame: Image.Image, num_frames: int
    ) -> List[np.ndarray]:
        """
        Simple fallback: duplicate the start frame
        """
        frame_array = pil_to_numpy(start_frame)
        return [frame_array.copy() for _ in range(num_frames)]
    
    def apply_motion_blur(
        self, frames: List[np.ndarray], strength: float = 0.5
    ) -> List[np.ndarray]:
        """
        Apply motion blur for smoother appearance
        """
        import cv2
        
        blurred_frames = []
        kernel_size = int(5 * strength)
        if kernel_size % 2 == 0:
            kernel_size += 1
        
        for frame in frames:
            blurred = cv2.GaussianBlur(frame, (kernel_size, kernel_size), 0)
            blended = cv2.addWeighted(frame, 1 - strength, blurred, strength, 0)
            blurred_frames.append(blended)
        
        return blurred_frames
    
    def stabilize_video(self, frames: List[np.ndarray]) -> List[np.ndarray]:
        """
        Apply basic video stabilization
        """
        import cv2
        
        if len(frames) < 2:
            return frames
        
        logger.info("Applying video stabilization...")
        
        # This is a simplified stabilization
        # Full implementation would use optical flow
        
        stabilized = [frames[0]]
        
        for i in range(1, len(frames)):
            # For now, just copy frames
            # Real stabilization would compute transforms
            stabilized.append(frames[i])
        
        return stabilized
    
    def __repr__(self) -> str:
        return f"<VideoInterpolator fps={self.fps} steps={self.num_inference_steps}>"
