"""
Utility functions for video generation pipeline
"""

import os
import json
import yaml
import torch
import psutil
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
import numpy as np
from PIL import Image


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """Set up logging configuration"""
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('video_generation.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


def get_device() -> torch.device:
    """
    Determine the best available device (CUDA > MPS > CPU)
    MPS is for Apple Silicon Macs
    """
    if torch.cuda.is_available():
        device = torch.device("cuda")
        print(f"✅ Using CUDA GPU: {torch.cuda.get_device_name(0)}")
        print(f"   VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
    elif torch.backends.mps.is_available():
        device = torch.device("mps")
        print("✅ Using Apple Silicon GPU (MPS)")
    else:
        device = torch.device("cpu")
        print("⚠️  Using CPU (this will be slow)")
    
    return device


def get_system_info() -> Dict[str, Any]:
    """Get system information for optimization"""
    info = {
        "cpu_count": psutil.cpu_count(),
        "ram_gb": psutil.virtual_memory().total / 1024**3,
        "available_ram_gb": psutil.virtual_memory().available / 1024**3,
        "device": str(get_device()),
    }
    
    if torch.cuda.is_available():
        info["gpu_name"] = torch.cuda.get_device_name(0)
        info["gpu_memory_gb"] = torch.cuda.get_device_properties(0).total_memory / 1024**3
    
    return info


def load_config(config_path: str) -> Dict[str, Any]:
    """Load YAML configuration file"""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def save_config(config: Dict[str, Any], config_path: str):
    """Save configuration to YAML file"""
    with open(config_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)


def estimate_generation_time(
    duration: int,
    resolution: tuple,
    fps: int,
    device: torch.device
) -> float:
    """
    Estimate video generation time in minutes
    Based on empirical benchmarks
    """
    total_frames = duration * fps
    pixels_per_frame = resolution[0] * resolution[1]
    
    # Base time per frame (seconds)
    if device.type == "cuda":
        base_time = 0.5  # Fast GPU
    elif device.type == "mps":
        base_time = 1.5  # Apple Silicon
    else:
        base_time = 5.0  # CPU
    
    # Adjust for resolution (1080p baseline)
    resolution_factor = pixels_per_frame / (1920 * 1080)
    
    total_seconds = total_frames * base_time * resolution_factor
    return total_seconds / 60  # Convert to minutes


def create_progress_bar(total: int, desc: str = "Processing"):
    """Create a progress bar with tqdm"""
    from tqdm import tqdm
    return tqdm(total=total, desc=desc, unit="frame")


def save_frames_as_video(
    frames: List[np.ndarray],
    output_path: str,
    fps: int = 30,
    codec: str = "libx264",
    crf: int = 18
):
    """
    Save list of frames as video using OpenCV
    CRF 18 is near-lossless quality
    """
    import cv2
    
    if not frames:
        raise ValueError("No frames to save")
    
    height, width = frames[0].shape[:2]
    
    # Use high-quality codec
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    for frame in frames:
        # Convert RGB to BGR for OpenCV
        if len(frame.shape) == 3 and frame.shape[2] == 3:
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        out.write(frame)
    
    out.release()
    print(f"✅ Video saved: {output_path}")


def frames_to_video_ffmpeg(
    frames: List[np.ndarray],
    output_path: str,
    fps: int = 30,
    crf: int = 18
):
    """
    Save frames as video using FFmpeg (higher quality)
    """
    import imageio
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    
    writer = imageio.get_writer(
        output_path,
        fps=fps,
        codec='libx264',
        quality=10,  # High quality
        pixelformat='yuv420p',
        macro_block_size=1
    )
    
    for frame in frames:
        writer.append_data(frame)
    
    writer.close()
    print(f"✅ Video saved: {output_path}")


def pil_to_numpy(image: Image.Image) -> np.ndarray:
    """Convert PIL Image to numpy array"""
    return np.array(image)


def numpy_to_pil(array: np.ndarray) -> Image.Image:
    """Convert numpy array to PIL Image"""
    return Image.fromarray(array.astype('uint8'))


def resize_frame(frame: np.ndarray, target_size: tuple) -> np.ndarray:
    """Resize frame to target size maintaining aspect ratio"""
    from PIL import Image
    img = Image.fromarray(frame)
    img = img.resize(target_size, Image.Resampling.LANCZOS)
    return np.array(img)


def clear_gpu_cache():
    """Clear GPU cache to free memory"""
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.synchronize()
    elif torch.backends.mps.is_available():
        torch.mps.empty_cache()


def calculate_optimal_batch_size(
    device: torch.device,
    resolution: tuple,
    safety_factor: float = 0.7
) -> int:
    """
    Calculate optimal batch size based on available memory
    """
    if device.type == "cpu":
        return 1
    
    if device.type == "cuda":
        total_memory = torch.cuda.get_device_properties(0).total_memory
        available_memory = total_memory * safety_factor
    elif device.type == "mps":
        # Conservative estimate for Apple Silicon
        available_memory = 8 * 1024**3 * safety_factor
    else:
        return 1
    
    # Rough estimate: 1080p frame uses ~500MB in diffusion pipeline
    pixels = resolution[0] * resolution[1]
    memory_per_frame = (pixels / (1920 * 1080)) * 500 * 1024**2
    
    batch_size = int(available_memory / memory_per_frame)
    return max(1, min(batch_size, 8))  # Cap at 8


def validate_prompt(prompt: str) -> bool:
    """Validate that prompt is reasonable"""
    if not prompt or len(prompt.strip()) < 5:
        return False
    if len(prompt) > 1000:
        return False
    return True


def sanitize_filename(filename: str) -> str:
    """Remove invalid characters from filename"""
    import re
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    # Limit length
    return filename[:100]


class VideoGenerationError(Exception):
    """Custom exception for video generation errors"""
    pass


def ensure_dir(path: str):
    """Ensure directory exists"""
    os.makedirs(path, exist_ok=True)
