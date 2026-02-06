"""
Sora-Inspired AI Video Generator
Core package initialization
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__license__ = "MIT"

from .prompt_analyzer import PromptAnalyzer
from .keyframe_generator import KeyframeGenerator
from .video_interpolator import VideoInterpolator
from .post_processor import PostProcessor
from .model_manager import ModelManager

__all__ = [
    "PromptAnalyzer",
    "KeyframeGenerator",
    "VideoInterpolator",
    "PostProcessor",
    "ModelManager",
]
