"""
Model Manager - Handle downloading and caching of AI models
"""

import os
import torch
from pathlib import Path
from typing import Optional, Dict, Any
from huggingface_hub import hf_hub_download, snapshot_download
import logging

logger = logging.getLogger(__name__)


class ModelManager:
    """
    Manages downloading, caching, and loading of AI models
    All models are downloaded from Hugging Face
    """
    
    # Model repository IDs
    MODELS = {
        "sdxl": "stabilityai/stable-diffusion-xl-base-1.0",
        "svd": "stabilityai/stable-video-diffusion-img2vid-xt",
        "animatediff": "guoyww/animatediff-motion-adapter-v1-5-2",
        "controlnet": "lllyasviel/control_v11p_sd15_canny",
        "upscaler": "ai-forever/Real-ESRGAN",
    }
    
    def __init__(self, cache_dir: str = "./models"):
        """
        Args:
            cache_dir: Directory to cache downloaded models
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.loaded_models: Dict[str, Any] = {}
        
        # Set HuggingFace cache directory
        os.environ["HF_HOME"] = str(self.cache_dir)
        os.environ["TRANSFORMERS_CACHE"] = str(self.cache_dir / "transformers")
        os.environ["DIFFUSERS_CACHE"] = str(self.cache_dir / "diffusers")
    
    def download_model(
        self,
        model_name: str,
        force_download: bool = False
    ) -> Path:
        """
        Download a model from Hugging Face if not already cached
        
        Args:
            model_name: Name of model (key from MODELS dict)
            force_download: Force re-download even if cached
            
        Returns:
            Path to model directory
        """
        if model_name not in self.MODELS:
            raise ValueError(
                f"Unknown model: {model_name}. "
                f"Available models: {list(self.MODELS.keys())}"
            )
        
        repo_id = self.MODELS[model_name]
        model_path = self.cache_dir / model_name
        
        if model_path.exists() and not force_download:
            logger.info(f"✅ Model {model_name} already cached at {model_path}")
            return model_path
        
        logger.info(f"📥 Downloading {model_name} from {repo_id}...")
        logger.info("   This may take a while for the first run...")
        
        try:
            # Download entire model repository
            snapshot_download(
                repo_id=repo_id,
                cache_dir=self.cache_dir,
                resume_download=True,
                local_dir=model_path,
                local_dir_use_symlinks=False
            )
            logger.info(f"✅ Downloaded {model_name}")
            return model_path
        except Exception as e:
            logger.error(f"❌ Failed to download {model_name}: {e}")
            raise
    
    def load_sdxl_pipeline(self, device: torch.device):
        """Load Stable Diffusion XL pipeline for keyframe generation"""
        if "sdxl_pipeline" in self.loaded_models:
            return self.loaded_models["sdxl_pipeline"]
        
        from diffusers import StableDiffusionXLPipeline
        
        logger.info("Loading Stable Diffusion XL pipeline...")
        model_path = self.download_model("sdxl")
        
        pipeline = StableDiffusionXLPipeline.from_pretrained(
            str(model_path),
            torch_dtype=torch.float16 if device.type == "cuda" else torch.float32,
            use_safetensors=True,
            variant="fp16" if device.type == "cuda" else None
        )
        
        pipeline = pipeline.to(device)
        
        # Enable memory optimizations
        if device.type == "cuda":
            pipeline.enable_attention_slicing()
            pipeline.enable_vae_slicing()
            # pipeline.enable_xformers_memory_efficient_attention()  # Requires xformers
        
        self.loaded_models["sdxl_pipeline"] = pipeline
        logger.info("✅ SDXL pipeline loaded")
        return pipeline
    
    def load_svd_pipeline(self, device: torch.device):
        """Load Stable Video Diffusion pipeline"""
        if "svd_pipeline" in self.loaded_models:
            return self.loaded_models["svd_pipeline"]
        
        from diffusers import StableVideoDiffusionPipeline
        
        logger.info("Loading Stable Video Diffusion pipeline...")
        model_path = self.download_model("svd")
        
        pipeline = StableVideoDiffusionPipeline.from_pretrained(
            str(model_path),
            torch_dtype=torch.float16 if device.type == "cuda" else torch.float32,
            variant="fp16" if device.type == "cuda" else None
        )
        
        pipeline = pipeline.to(device)
        
        if device.type == "cuda":
            pipeline.enable_attention_slicing()
            pipeline.enable_vae_slicing()
        
        self.loaded_models["svd_pipeline"] = pipeline
        logger.info("✅ SVD pipeline loaded")
        return pipeline
    
    def load_animatediff_pipeline(self, device: torch.device):
        """Load AnimateDiff pipeline for temporal consistency"""
        if "animatediff_pipeline" in self.loaded_models:
            return self.loaded_models["animatediff_pipeline"]
        
        # Note: AnimateDiff requires additional setup
        # This is a placeholder - actual implementation would be more complex
        logger.warning("⚠️  AnimateDiff integration is simplified in this version")
        logger.info("   Using SVD as primary video generation method")
        
        # For now, fall back to SVD
        return self.load_svd_pipeline(device)
    
    def unload_model(self, model_name: str):
        """Unload a model from memory to free up resources"""
        if model_name in self.loaded_models:
            del self.loaded_models[model_name]
            torch.cuda.empty_cache() if torch.cuda.is_available() else None
            logger.info(f"✅ Unloaded {model_name}")
    
    def unload_all(self):
        """Unload all models from memory"""
        self.loaded_models.clear()
        torch.cuda.empty_cache() if torch.cuda.is_available() else None
        logger.info("✅ All models unloaded")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about available and loaded models"""
        return {
            "available_models": list(self.MODELS.keys()),
            "loaded_models": list(self.loaded_models.keys()),
            "cache_dir": str(self.cache_dir),
            "cache_size_mb": self._get_cache_size() / 1024 / 1024
        }
    
    def _get_cache_size(self) -> int:
        """Calculate total size of cached models"""
        total_size = 0
        for root, dirs, files in os.walk(self.cache_dir):
            for file in files:
                file_path = os.path.join(root, file)
                if os.path.exists(file_path):
                    total_size += os.path.getsize(file_path)
        return total_size
    
    def __repr__(self) -> str:
        return f"<ModelManager cache_dir='{self.cache_dir}' loaded={len(self.loaded_models)}>"
