"""
Post Processor - Final video enhancement and encoding
"""

import cv2
import numpy as np
from PIL import Image, ImageEnhance
from typing import List, Optional, Tuple
import logging
from .utils import frames_to_video_ffmpeg

logger = logging.getLogger(__name__)


class PostProcessor:
    """
    Handles final video processing:
    - Upscaling to target resolution
    - Color grading
    - Stabilization
    - Encoding to final format
    """
    
    def __init__(
        self,
        target_resolution: Tuple[int, int] = (1920, 1080),
        target_fps: int = 30,
    ):
        """
        Args:
            target_resolution: (width, height) for final video
            target_fps: Target frames per second
        """
        self.target_resolution = target_resolution
        self.target_fps = target_fps
    
    def process_video(
        self,
        frames: List[np.ndarray],
        apply_upscaling: bool = True,
        apply_color_grading: bool = True,
        apply_stabilization: bool = False,
        apply_sharpening: bool = True,
    ) -> List[np.ndarray]:
        """
        Apply full post-processing pipeline
        
        Args:
            frames: List of frames as numpy arrays
            apply_upscaling: Upscale to target resolution
            apply_color_grading: Enhance colors and contrast
            apply_stabilization: Stabilize video motion
            apply_sharpening: Sharpen details
            
        Returns:
            Processed frames
        """
        logger.info("Starting post-processing pipeline...")
        
        processed = frames
        
        # 1. Upscaling
        if apply_upscaling:
            processed = self.upscale_frames(processed)
        
        # 2. Color grading
        if apply_color_grading:
            processed = self.apply_color_grading(processed)
        
        # 3. Sharpening
        if apply_sharpening:
            processed = self.sharpen_frames(processed)
        
        # 4. Stabilization (computationally expensive)
        if apply_stabilization:
            processed = self.stabilize_video(processed)
        
        logger.info("✅ Post-processing complete")
        return processed
    
    def upscale_frames(self, frames: List[np.ndarray]) -> List[np.ndarray]:
        """
        Upscale frames to target resolution
        Uses high-quality Lanczos interpolation
        """
        logger.info(f"Upscaling to {self.target_resolution}...")
        
        upscaled = []
        target_w, target_h = self.target_resolution
        
        for i, frame in enumerate(frames):
            if i % 30 == 0:
                logger.info(f"  Upscaling frame {i+1}/{len(frames)}...")
            
            # Convert to PIL for high-quality resizing
            img = Image.fromarray(frame)
            img = img.resize((target_w, target_h), Image.Resampling.LANCZOS)
            upscaled.append(np.array(img))
        
        logger.info(f"✅ Upscaled {len(frames)} frames")
        return upscaled
    
    def apply_color_grading(self, frames: List[np.ndarray]) -> List[np.ndarray]:
        """
        Apply cinematic color grading
        - Adjust contrast, saturation, brightness
        """
        logger.info("Applying color grading...")
        
        graded = []
        
        for frame in frames:
            # Convert to PIL for easier enhancement
            img = Image.fromarray(frame)
            
            # Increase contrast slightly
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.15)
            
            # Increase color saturation
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(1.1)
            
            # Adjust brightness slightly
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(1.05)
            
            graded.append(np.array(img))
        
        logger.info("✅ Color grading applied")
        return graded
    
    def sharpen_frames(self, frames: List[np.ndarray]) -> List[np.ndarray]:
        """
        Sharpen frames for better detail
        """
        logger.info("Sharpening frames...")
        
        sharpened = []
        
        # Sharpening kernel
        kernel = np.array([
            [0, -1, 0],
            [-1, 5, -1],
            [0, -1, 0]
        ])
        
        for frame in frames:
            # Apply sharpening
            sharp = cv2.filter2D(frame, -1, kernel)
            
            # Blend with original (50% sharp, 50% original)
            blended = cv2.addWeighted(frame, 0.5, sharp, 0.5, 0)
            sharpened.append(blended)
        
        logger.info("✅ Sharpening applied")
        return sharpened
    
    def stabilize_video(self, frames: List[np.ndarray]) -> List[np.ndarray]:
        """
        Apply video stabilization using optical flow
        """
        logger.info("Stabilizing video...")
        
        if len(frames) < 2:
            return frames
        
        stabilized = [frames[0]]
        
        # Initialize
        prev_gray = cv2.cvtColor(frames[0], cv2.COLOR_RGB2GRAY)
        
        # Accumulated transform
        transforms = []
        
        for i in range(1, len(frames)):
            curr_gray = cv2.cvtColor(frames[i], cv2.COLOR_RGB2GRAY)
            
            # Detect features in previous frame
            prev_pts = cv2.goodFeaturesToTrack(
                prev_gray,
                maxCorners=200,
                qualityLevel=0.01,
                minDistance=30,
                blockSize=3
            )
            
            if prev_pts is not None and len(prev_pts) > 0:
                # Calculate optical flow
                curr_pts, status, err = cv2.calcOpticalFlowPyrLK(
                    prev_gray, curr_gray, prev_pts, None
                )
                
                # Filter valid points
                idx = np.where(status == 1)[0]
                prev_pts = prev_pts[idx]
                curr_pts = curr_pts[idx]
                
                if len(prev_pts) >= 4:
                    # Estimate affine transform
                    transform = cv2.estimateAffinePartial2D(prev_pts, curr_pts)[0]
                    
                    if transform is not None:
                        # Apply transform
                        h, w = frames[i].shape[:2]
                        stabilized_frame = cv2.warpAffine(
                            frames[i], transform, (w, h)
                        )
                        stabilized.append(stabilized_frame)
                    else:
                        stabilized.append(frames[i])
                else:
                    stabilized.append(frames[i])
            else:
                stabilized.append(frames[i])
            
            prev_gray = curr_gray
        
        logger.info("✅ Stabilization applied")
        return stabilized
    
    def apply_cinematic_bars(
        self, frames: List[np.ndarray], aspect_ratio: str = "2.39:1"
    ) -> List[np.ndarray]:
        """
        Add black bars for cinematic aspect ratio
        """
        logger.info(f"Adding cinematic bars ({aspect_ratio})...")
        
        barred = []
        
        for frame in frames:
            h, w = frame.shape[:2]
            
            if aspect_ratio == "2.39:1":
                # Anamorphic widescreen
                bar_height = int(h * 0.1)
            elif aspect_ratio == "21:9":
                bar_height = int(h * 0.08)
            else:
                bar_height = 0
            
            if bar_height > 0:
                # Add black bars
                top_bar = np.zeros((bar_height, w, 3), dtype=np.uint8)
                bottom_bar = np.zeros((bar_height, w, 3), dtype=np.uint8)
                
                # Crop middle section
                middle_h = h - 2 * bar_height
                cropped = frame[bar_height:bar_height + middle_h, :]
                
                # Combine
                result = np.vstack([top_bar, cropped, bottom_bar])
                barred.append(result)
            else:
                barred.append(frame)
        
        return barred
    
    def save_video(
        self,
        frames: List[np.ndarray],
        output_path: str,
        fps: Optional[int] = None,
        crf: int = 18,
    ):
        """
        Save frames as final video file
        
        Args:
            frames: Processed frames
            output_path: Output file path
            fps: Frames per second (defaults to self.target_fps)
            crf: Quality (0-51, lower is better, 18 is visually lossless)
        """
        fps = fps or self.target_fps
        
        logger.info(f"Encoding video to {output_path}...")
        logger.info(f"  Total frames: {len(frames)}")
        logger.info(f"  FPS: {fps}")
        logger.info(f"  Duration: {len(frames) / fps:.2f}s")
        logger.info(f"  CRF: {crf} (lower = better quality)")
        
        frames_to_video_ffmpeg(frames, output_path, fps=fps, crf=crf)
        
        logger.info(f"✅ Video saved: {output_path}")
    
    def create_preview(
        self, frames: List[np.ndarray], num_preview_frames: int = 10
    ) -> List[np.ndarray]:
        """
        Create a preview with evenly spaced frames
        """
        if len(frames) <= num_preview_frames:
            return frames
        
        indices = np.linspace(0, len(frames) - 1, num_preview_frames, dtype=int)
        return [frames[i] for i in indices]
    
    def __repr__(self) -> str:
        return (
            f"<PostProcessor resolution={self.target_resolution} "
            f"fps={self.target_fps}>"
        )
