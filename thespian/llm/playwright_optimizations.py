"""
Performance and architecture optimizations for the consolidated playwright.

This module contains extracted utility functions and optimizations from the main
consolidated playwright to improve maintainability and performance.
"""

from typing import Dict, Any, List, Optional, Set
import logging
from functools import lru_cache
import time

logger = logging.getLogger(__name__)


class SceneOptimizer:
    """Optimized scene processing utilities."""
    
    @staticmethod
    @lru_cache(maxsize=128)
    def calculate_scene_similarity(scene1: str, scene2: str, threshold: float = 0.5) -> float:
        """Calculate similarity between two scenes using optimized Jaccard similarity.
        
        Args:
            scene1: First scene content
            scene2: Second scene content  
            threshold: Similarity threshold
            
        Returns:
            Similarity score between 0.0 and 1.0
        """
        if not scene1 or not scene2:
            return 0.0
            
        # Extract meaningful tokens (skip very short words)
        words1 = {word.lower() for word in scene1.split() if len(word) > 2}
        words2 = {word.lower() for word in scene2.split() if len(word) > 2}
        
        if not words1 or not words2:
            return 0.0
            
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    @staticmethod
    def is_scene_unique(new_scene: str, previous_scenes: List[str], 
                       similarity_threshold: float = 0.5) -> bool:
        """Check if a scene is unique compared to previous scenes.
        
        Optimized version with early exit and caching.
        """
        if not new_scene or not previous_scenes:
            return True
            
        # Use only first significant portion for comparison
        new_scene_sample = new_scene[:1000] if len(new_scene) > 1000 else new_scene
        
        for prev_scene in previous_scenes:
            prev_scene_sample = prev_scene[:1000] if len(prev_scene) > 1000 else prev_scene
            
            similarity = SceneOptimizer.calculate_scene_similarity(
                new_scene_sample, prev_scene_sample, similarity_threshold
            )
            
            if similarity > similarity_threshold:
                logger.warning(f"Scene similarity detected: {similarity:.2f} > {similarity_threshold}")
                return False
                
        return True


class MemoryOptimizer:
    """Optimized memory management utilities."""
    
    @staticmethod
    def batch_update_characters(character_tracker, scene_data: List[Dict[str, Any]], 
                               llm_callable) -> Dict[str, Any]:
        """Batch update multiple character analyses for better performance."""
        if not character_tracker or not scene_data:
            return {}
            
        results = {}
        start_time = time.time()
        
        try:
            # Process scenes in batch
            for scene_info in scene_data:
                scene_id = scene_info.get('scene_id')
                scene_content = scene_info.get('content')
                
                if scene_id and scene_content:
                    analysis = character_tracker.analyze_scene_characters(
                        scene_id, scene_content, llm_callable
                    )
                    results[scene_id] = analysis
                    
        except Exception as e:
            logger.error(f"Error in batch character update: {str(e)}")
        finally:
            elapsed = time.time() - start_time
            logger.info(f"Batch character update completed in {elapsed:.2f}s for {len(scene_data)} scenes")
            
        return results


class ContentValidator:
    """Optimized content validation utilities."""
    
    @staticmethod
    def validate_scene_content(content: str, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Fast validation of scene content against requirements."""
        if not content:
            return {"valid": False, "errors": ["Empty content"]}
            
        errors = []
        warnings = []
        
        # Length checks
        if len(content) < 100:
            warnings.append("Scene content is very short")
        elif len(content) > 50000:
            warnings.append("Scene content is very long")
            
        # Required characters check (optimized)
        required_chars = requirements.get('characters', [])
        if required_chars:
            content_lower = content.lower()
            missing_chars = [char for char in required_chars 
                           if char.lower() not in content_lower]
            if missing_chars:
                errors.append(f"Missing characters: {missing_chars}")
                
        # Setting validation
        required_setting = requirements.get('setting')
        if required_setting and required_setting.lower() not in content.lower():
            warnings.append("Setting may not be properly established")
            
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "length": len(content),
            "character_count": len(content.split())
        }


class PromptOptimizer:
    """Optimized prompt construction utilities."""
    
    @staticmethod
    @lru_cache(maxsize=64)
    def build_scene_prompt_cached(setting: str, characters_str: str, style: str, 
                                 period: str, tone: str = None) -> str:
        """Build scene prompt with caching for common combinations."""
        base_prompt = f"""Generate a theatrical scene with the following requirements:

Setting: {setting}
Characters: {characters_str}
Style: {style}
Period: {period}"""
        
        if tone:
            base_prompt += f"\nTone: {tone}"
            
        base_prompt += """

Create a complete scene with:
1. Detailed stage directions
2. Natural, character-appropriate dialogue
3. Clear emotional progression
4. Proper formatting for theatrical production
"""
        return base_prompt