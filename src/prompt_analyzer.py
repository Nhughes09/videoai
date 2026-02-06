"""
Prompt Analyzer - Parse text prompts into structured scene descriptions
"""

import re
from typing import Dict, List, Any
from dataclasses import dataclass, field


@dataclass
class SceneDescription:
    """Structured representation of a scene"""
    raw_prompt: str
    subject: str = ""
    action: str = ""
    setting: str = ""
    time_of_day: str = "day"
    weather: str = "clear"
    camera_movement: str = "static"
    style: str = "photorealistic"
    mood: str = "neutral"
    lighting: str = "natural"
    duration_seconds: int = 60
    additional_details: List[str] = field(default_factory=list)


class PromptAnalyzer:
    """
    Analyzes text prompts and extracts structured information
    for better video generation control
    """
    
    def __init__(self):
        # Keywords for different categories
        self.camera_keywords = {
            "pan": ["pan", "panning", "sweep", "sweeping"],
            "zoom": ["zoom", "zooming", "close-up", "closeup"],
            "dolly": ["dolly", "track", "tracking"],
            "orbit": ["orbit", "orbiting", "around", "circling"],
            "static": ["static", "still", "fixed"],
        }
        
        self.style_keywords = {
            "cinematic": ["cinematic", "film", "movie"],
            "documentary": ["documentary", "realistic", "real"],
            "animated": ["animated", "cartoon", "anime"],
            "artistic": ["artistic", "painting", "impressionist"],
            "photorealistic": ["photorealistic", "photo", "realistic"],
        }
        
        self.lighting_keywords = {
            "golden_hour": ["golden hour", "sunset", "sunrise", "dusk", "dawn"],
            "night": ["night", "dark", "moonlight"],
            "studio": ["studio", "professional lighting"],
            "natural": ["natural", "daylight", "sunlight"],
            "dramatic": ["dramatic", "high contrast", "moody"],
        }
        
        self.weather_keywords = {
            "clear": ["clear", "sunny"],
            "cloudy": ["cloudy", "overcast"],
            "rainy": ["rain", "rainy", "storm"],
            "foggy": ["fog", "foggy", "mist"],
            "snowy": ["snow", "snowy", "winter"],
        }
        
        self.time_keywords = {
            "day": ["day", "daytime", "afternoon"],
            "night": ["night", "nighttime", "evening"],
            "dawn": ["dawn", "sunrise", "early morning"],
            "dusk": ["dusk", "sunset", "twilight"],
        }
    
    def analyze(self, prompt: str, duration: int = 60) -> SceneDescription:
        """
        Analyze prompt and return structured scene description
        
        Args:
            prompt: Raw text prompt
            duration: Video duration in seconds
            
        Returns:
            SceneDescription object
        """
        prompt_lower = prompt.lower()
        
        scene = SceneDescription(
            raw_prompt=prompt,
            duration_seconds=duration
        )
        
        # Extract main subject (simplified - first noun phrase)
        scene.subject = self._extract_subject(prompt)
        
        # Extract action (verbs and verb phrases)
        scene.action = self._extract_action(prompt)
        
        # Extract setting/location
        scene.setting = self._extract_setting(prompt)
        
        # Detect camera movement
        scene.camera_movement = self._detect_keyword(
            prompt_lower, self.camera_keywords, default="static"
        )
        
        # Detect style
        scene.style = self._detect_keyword(
            prompt_lower, self.style_keywords, default="photorealistic"
        )
        
        # Detect lighting
        scene.lighting = self._detect_keyword(
            prompt_lower, self.lighting_keywords, default="natural"
        )
        
        # Detect weather
        scene.weather = self._detect_keyword(
            prompt_lower, self.weather_keywords, default="clear"
        )
        
        # Detect time of day
        scene.time_of_day = self._detect_keyword(
            prompt_lower, self.time_keywords, default="day"
        )
        
        # Extract mood
        scene.mood = self._detect_mood(prompt_lower)
        
        return scene
    
    def _detect_keyword(
        self, text: str, keyword_dict: Dict[str, List[str]], default: str
    ) -> str:
        """Detect which category a text belongs to based on keywords"""
        for category, keywords in keyword_dict.items():
            for keyword in keywords:
                if keyword in text:
                    return category
        return default
    
    def _extract_subject(self, prompt: str) -> str:
        """Extract main subject (simplified)"""
        # Simple heuristic: first few words often contain the subject
        words = prompt.split()
        if len(words) >= 3:
            return " ".join(words[:3])
        return prompt
    
    def _extract_action(self, prompt: str) -> str:
        """Extract action verbs"""
        action_verbs = [
            "flying", "walking", "running", "rotating", "spinning",
            "exploding", "growing", "shrinking", "moving", "flowing",
            "crashing", "blooming", "dividing", "dancing", "falling"
        ]
        
        prompt_lower = prompt.lower()
        for verb in action_verbs:
            if verb in prompt_lower:
                return verb
        
        return "existing"  # Default action
    
    def _extract_setting(self, prompt: str) -> str:
        """Extract setting/location"""
        location_keywords = [
            "city", "forest", "ocean", "beach", "space", "lab",
            "street", "room", "sky", "underwater", "desert", "mountain"
        ]
        
        prompt_lower = prompt.lower()
        for location in location_keywords:
            if location in prompt_lower:
                return location
        
        return "generic"
    
    def _detect_mood(self, prompt_lower: str) -> str:
        """Detect emotional mood"""
        mood_keywords = {
            "peaceful": ["peaceful", "calm", "serene", "tranquil"],
            "exciting": ["exciting", "dynamic", "energetic", "fast"],
            "mysterious": ["mysterious", "dark", "unknown", "eerie"],
            "dramatic": ["dramatic", "intense", "powerful"],
            "happy": ["happy", "cheerful", "bright", "joyful"],
        }
        
        for mood, keywords in mood_keywords.items():
            for keyword in keywords:
                if keyword in prompt_lower:
                    return mood
        
        return "neutral"
    
    def create_enhanced_prompt(self, scene: SceneDescription) -> str:
        """
        Create an enhanced prompt for SD XL with more details
        This improves generation quality
        """
        quality_suffix = (
            ", highly detailed, 8k resolution, professional photography, "
            "sharp focus, vivid colors, masterpiece"
        )
        
        style_prefix = {
            "cinematic": "Cinematic shot, ",
            "documentary": "Documentary footage, ",
            "animated": "Beautiful animation, ",
            "artistic": "Artistic rendering, ",
            "photorealistic": "Photorealistic, ",
        }.get(scene.style, "")
        
        lighting_desc = {
            "golden_hour": " during golden hour lighting",
            "night": " at night with dramatic lighting",
            "studio": " with professional studio lighting",
            "natural": " with natural lighting",
            "dramatic": " with dramatic high-contrast lighting",
        }.get(scene.lighting, "")
        
        enhanced = (
            f"{style_prefix}{scene.raw_prompt}{lighting_desc}{quality_suffix}"
        )
        
        return enhanced
    
    def split_into_scenes(
        self, scene: SceneDescription, scene_duration: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Split long video into multiple scenes
        Each scene lasts scene_duration seconds
        """
        total_duration = scene.duration_seconds
        num_scenes = max(1, total_duration // scene_duration)
        
        scenes = []
        for i in range(num_scenes):
            scene_data = {
                "scene_number": i,
                "start_time": i * scene_duration,
                "end_time": min((i + 1) * scene_duration, total_duration),
                "description": scene.raw_prompt,
                "camera_movement": scene.camera_movement,
                "style": scene.style,
            }
            scenes.append(scene_data)
        
        return scenes
    
    def __repr__(self) -> str:
        return "<PromptAnalyzer>"
