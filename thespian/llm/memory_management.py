"""
Memory management utilities for the Thespian framework.

This module provides optimized memory management functionality
extracted from the consolidated playwright for better maintainability.
"""

from typing import Dict, Any, List, Optional, Callable, Union
from pydantic import BaseModel, Field
import logging
import time
from datetime import datetime

from thespian.llm.theatrical_memory import TheatricalMemory, CharacterProfile
from thespian.llm.enhanced_memory import EnhancedTheatricalMemory, EnhancedCharacterProfile
from thespian.llm.character_analyzer import CharacterTracker, SceneCharacterAnalysis
from thespian.llm.playwright_optimizations import MemoryOptimizer
from thespian.llm.error_handling import (
    with_error_handling, 
    MemoryError, 
    global_error_handler,
    ErrorSeverity
)
from thespian.config_manager import get_config

logger = logging.getLogger(__name__)


class MemoryIntegrationLevel:
    """Constants for memory integration levels."""
    BASIC = 1
    STANDARD = 2
    DEEP = 3


class MemoryManager:
    """
    Centralized memory management for theatrical productions.
    
    This class handles character tracking, narrative continuity, and
    memory optimization across all components.
    """
    
    def __init__(
        self,
        memory: Optional[TheatricalMemory] = None,
        enhanced_memory: Optional[EnhancedTheatricalMemory] = None,
        character_tracker: Optional[CharacterTracker] = None,
        integration_level: int = MemoryIntegrationLevel.STANDARD
    ):
        """Initialize the memory manager."""
        self.memory = memory
        self.enhanced_memory = enhanced_memory
        self.character_tracker = character_tracker
        self.integration_level = integration_level
        self.config = get_config()
        
        # Initialize enhanced memory if needed
        self._ensure_enhanced_memory()
        
        # Initialize character tracker if needed and possible
        if not self.character_tracker and self.enhanced_memory:
            self.character_tracker = CharacterTracker(memory=self.enhanced_memory)
    
    def _ensure_enhanced_memory(self) -> None:
        """Ensure enhanced memory is available if needed."""
        if self.integration_level > MemoryIntegrationLevel.BASIC and not self.enhanced_memory:
            if isinstance(self.memory, EnhancedTheatricalMemory):
                self.enhanced_memory = self.memory
            elif self.memory:
                # Convert standard memory to enhanced
                self.enhanced_memory = EnhancedTheatricalMemory(
                    db_path=getattr(self.memory, "db_path", None)
                )
                
                # Copy existing character profiles
                if hasattr(self.memory, "character_profiles"):
                    for char_id, profile in self.memory.character_profiles.items():
                        self.enhanced_memory.update_character_profile(char_id, profile)
                
                # Use enhanced memory as the base memory
                self.memory = self.enhanced_memory
            else:
                # Create new enhanced memory
                self.enhanced_memory = EnhancedTheatricalMemory()
                self.memory = self.enhanced_memory
    
    @with_error_handling(global_error_handler, severity=ErrorSeverity.MEDIUM)
    def update_from_scene(
        self,
        scene_id: str,
        scene_content: str,
        requirements: Dict[str, Any],
        llm_callable: Callable[[str], Any]
    ) -> Dict[str, Any]:
        """
        Update memory from a generated scene.
        
        Args:
            scene_id: Unique scene identifier
            scene_content: Generated scene content
            requirements: Original scene requirements
            llm_callable: Function to call LLM for analysis
            
        Returns:
            Dictionary with update results and metadata
        """
        if not scene_content:
            return {"status": "skipped", "reason": "empty_content"}
        
        update_results = {
            "scene_id": scene_id,
            "timestamp": datetime.now().isoformat(),
            "updates_performed": []
        }
        
        try:
            # Update character tracking
            if (self.config.memory.enable_character_tracking and 
                self.character_tracker and 
                self.integration_level >= MemoryIntegrationLevel.STANDARD):
                
                char_result = self._update_character_tracking(
                    scene_id, scene_content, llm_callable
                )
                update_results["character_tracking"] = char_result
                update_results["updates_performed"].append("character_tracking")
            
            # Update narrative tracking
            if (self.config.memory.enable_narrative_tracking and 
                self.enhanced_memory and 
                self.integration_level >= MemoryIntegrationLevel.STANDARD):
                
                narrative_result = self._update_narrative_tracking(
                    scene_id, scene_content, requirements, llm_callable
                )
                update_results["narrative_tracking"] = narrative_result
                update_results["updates_performed"].append("narrative_tracking")
            
            # Deep memory integration
            if self.integration_level >= MemoryIntegrationLevel.DEEP:
                deep_result = self._perform_deep_memory_integration(
                    scene_id, scene_content, requirements, llm_callable
                )
                update_results["deep_integration"] = deep_result
                update_results["updates_performed"].append("deep_integration")
            
            update_results["status"] = "success"
            
        except Exception as e:
            logger.error(f"Error updating memory from scene {scene_id}: {e}")
            update_results["status"] = "error"
            update_results["error"] = str(e)
        
        return update_results
    
    @with_error_handling(global_error_handler, severity=ErrorSeverity.LOW)
    def _update_character_tracking(
        self,
        scene_id: str,
        scene_content: str,
        llm_callable: Callable[[str], Any]
    ) -> Dict[str, Any]:
        """Update character tracking from scene content."""
        if not self.character_tracker:
            return {"status": "skipped", "reason": "no_character_tracker"}
        
        try:
            start_time = time.time()
            
            character_analysis = self.character_tracker.analyze_scene_characters(
                scene_id, 
                scene_content,
                llm_callable
            )
            
            elapsed_time = time.time() - start_time
            
            return {
                "status": "success",
                "characters_analyzed": len(character_analysis.character_references),
                "analysis_time": elapsed_time,
                "scene_id": scene_id
            }
            
        except Exception as e:
            logger.error(f"Error in character tracking for scene {scene_id}: {e}")
            return {"status": "error", "error": str(e)}
    
    @with_error_handling(global_error_handler, severity=ErrorSeverity.LOW)
    def _update_narrative_tracking(
        self,
        scene_id: str,
        scene_content: str,
        requirements: Dict[str, Any],
        llm_callable: Callable[[str], Any]
    ) -> Dict[str, Any]:
        """Update narrative tracking from scene content."""
        if not self.enhanced_memory:
            return {"status": "skipped", "reason": "no_enhanced_memory"}
        
        try:
            start_time = time.time()
            
            # Update narrative from scene
            self.enhanced_memory.update_narrative_from_scene(
                scene_id,
                scene_content,
                llm_callable
            )
            
            # Update character development if characters provided
            characters = requirements.get('characters', [])
            for character in characters:
                if character.lower() in scene_content.lower():
                    self.enhanced_memory.update_character_from_scene(
                        character,
                        scene_content,
                        llm_callable
                    )
            
            elapsed_time = time.time() - start_time
            
            return {
                "status": "success",
                "characters_updated": len(characters),
                "analysis_time": elapsed_time,
                "scene_id": scene_id
            }
            
        except Exception as e:
            logger.error(f"Error in narrative tracking for scene {scene_id}: {e}")
            return {"status": "error", "error": str(e)}
    
    @with_error_handling(global_error_handler, severity=ErrorSeverity.LOW)
    def _perform_deep_memory_integration(
        self,
        scene_id: str,
        scene_content: str,
        requirements: Dict[str, Any],
        llm_callable: Callable[[str], Any]
    ) -> Dict[str, Any]:
        """Perform deep memory integration analysis."""
        if not self.enhanced_memory:
            return {"status": "skipped", "reason": "no_enhanced_memory"}
        
        try:
            start_time = time.time()
            
            # Analyze thematic elements
            theme_analysis = self._analyze_scene_themes(scene_content, llm_callable)
            
            # Analyze relationship dynamics
            relationship_analysis = self._analyze_relationships(
                scene_content, requirements.get('characters', []), llm_callable
            )
            
            # Store deep analysis results
            deep_analysis = {
                "scene_id": scene_id,
                "themes": theme_analysis,
                "relationships": relationship_analysis,
                "timestamp": datetime.now().isoformat()
            }
            
            # Store in enhanced memory if method exists
            if hasattr(self.enhanced_memory, 'store_deep_analysis'):
                self.enhanced_memory.store_deep_analysis(scene_id, deep_analysis)
            
            elapsed_time = time.time() - start_time
            
            return {
                "status": "success",
                "themes_identified": len(theme_analysis.get("themes", [])),
                "relationships_analyzed": len(relationship_analysis.get("relationships", [])),
                "analysis_time": elapsed_time
            }
            
        except Exception as e:
            logger.error(f"Error in deep memory integration for scene {scene_id}: {e}")
            return {"status": "error", "error": str(e)}
    
    def _analyze_scene_themes(
        self,
        scene_content: str,
        llm_callable: Callable[[str], Any]
    ) -> Dict[str, Any]:
        """Analyze thematic elements in the scene."""
        prompt = f"""Analyze the thematic elements in this theatrical scene:

{scene_content}

Identify:
1. Main themes (3-5 key themes)
2. Symbolic elements
3. Emotional tone progression
4. Dramatic tensions

Format your response as JSON with keys: themes, symbols, emotions, tensions"""
        
        try:
            response = llm_callable(prompt)
            content = str(response.content) if hasattr(response, 'content') else str(response)
            
            # Try to parse as JSON, fallback to text analysis
            try:
                import json
                return json.loads(content)
            except:
                # Fallback: extract themes from text
                themes = []
                if "theme" in content.lower():
                    lines = content.split('\n')
                    for line in lines:
                        if 'theme' in line.lower() and ':' in line:
                            theme = line.split(':', 1)[1].strip()
                            if theme:
                                themes.append(theme)
                
                return {"themes": themes, "raw_analysis": content}
                
        except Exception as e:
            logger.warning(f"Error analyzing themes: {e}")
            return {"themes": [], "error": str(e)}
    
    def _analyze_relationships(
        self,
        scene_content: str,
        characters: List[str],
        llm_callable: Callable[[str], Any]
    ) -> Dict[str, Any]:
        """Analyze character relationships in the scene."""
        if len(characters) < 2:
            return {"relationships": [], "reason": "insufficient_characters"}
        
        prompt = f"""Analyze the character relationships in this scene:

Characters: {', '.join(characters)}

Scene:
{scene_content}

For each pair of characters that interact, describe:
1. Type of relationship (romantic, familial, professional, etc.)
2. Power dynamic
3. Emotional connection level
4. Conflict or harmony present

Format as a list of relationship analyses."""
        
        try:
            response = llm_callable(prompt)
            content = str(response.content) if hasattr(response, 'content') else str(response)
            
            # Extract relationship information
            relationships = []
            for i, char1 in enumerate(characters):
                for char2 in characters[i+1:]:
                    if (char1.lower() in scene_content.lower() and 
                        char2.lower() in scene_content.lower()):
                        relationships.append({
                            "characters": [char1, char2],
                            "interaction_detected": True
                        })
            
            return {
                "relationships": relationships,
                "analysis": content
            }
            
        except Exception as e:
            logger.warning(f"Error analyzing relationships: {e}")
            return {"relationships": [], "error": str(e)}
    
    @with_error_handling(global_error_handler, severity=ErrorSeverity.MEDIUM)
    def batch_update_from_scenes(
        self,
        scene_data: List[Dict[str, Any]],
        llm_callable: Callable[[str], Any],
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ) -> Dict[str, Any]:
        """
        Batch update memory from multiple scenes for better performance.
        
        Args:
            scene_data: List of dictionaries with scene information
            llm_callable: Function to call LLM for analysis
            progress_callback: Optional progress callback
            
        Returns:
            Batch update results
        """
        if not scene_data:
            return {"status": "skipped", "reason": "no_scenes"}
        
        if not self.config.performance.batch_processing:
            # Fall back to individual updates
            results = []
            for i, data in enumerate(scene_data):
                if progress_callback:
                    progress_callback({"progress": i / len(scene_data), "current": i + 1})
                
                result = self.update_from_scene(
                    data['scene_id'],
                    data['content'],
                    data['requirements'],
                    llm_callable
                )
                results.append(result)
            
            return {"status": "completed_individual", "results": results}
        
        # Use optimized batch processing
        try:
            start_time = time.time()
            
            # Batch character updates
            character_results = {}
            if (self.character_tracker and 
                self.config.memory.enable_character_tracking):
                character_results = MemoryOptimizer.batch_update_characters(
                    self.character_tracker, scene_data, llm_callable
                )
            
            # Batch narrative updates
            narrative_results = {}
            if (self.enhanced_memory and 
                self.config.memory.enable_narrative_tracking):
                for data in scene_data:
                    try:
                        result = self._update_narrative_tracking(
                            data['scene_id'],
                            data['content'],
                            data['requirements'],
                            llm_callable
                        )
                        narrative_results[data['scene_id']] = result
                    except Exception as e:
                        logger.warning(f"Failed narrative update for {data['scene_id']}: {e}")
                        narrative_results[data['scene_id']] = {"status": "error", "error": str(e)}
            
            elapsed_time = time.time() - start_time
            
            if progress_callback:
                progress_callback({"progress": 1.0, "completed": True})
            
            return {
                "status": "success",
                "scenes_processed": len(scene_data),
                "character_results": character_results,
                "narrative_results": narrative_results,
                "processing_time": elapsed_time,
                "batch_optimization": True
            }
            
        except Exception as e:
            logger.error(f"Error in batch memory update: {e}")
            return {"status": "error", "error": str(e)}
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about memory usage and performance."""
        stats = {
            "integration_level": self.integration_level,
            "has_basic_memory": self.memory is not None,
            "has_enhanced_memory": self.enhanced_memory is not None,
            "has_character_tracker": self.character_tracker is not None,
            "timestamp": datetime.now().isoformat()
        }
        
        # Add memory-specific stats
        if self.memory and hasattr(self.memory, 'character_profiles'):
            stats["character_count"] = len(self.memory.character_profiles)
        
        if self.enhanced_memory and hasattr(self.enhanced_memory, 'get_stats'):
            stats["enhanced_stats"] = self.enhanced_memory.get_stats()
        
        return stats
    
    def cleanup_old_data(self) -> Dict[str, Any]:
        """Clean up old memory data based on configuration."""
        cleanup_results = {
            "timestamp": datetime.now().isoformat(),
            "cleanup_performed": []
        }
        
        try:
            # Cleanup based on memory limits
            max_items = self.config.memory.max_memory_items
            cleanup_threshold = self.config.memory.cleanup_threshold
            
            if (self.enhanced_memory and 
                hasattr(self.enhanced_memory, 'cleanup_old_data')):
                result = self.enhanced_memory.cleanup_old_data(max_items, cleanup_threshold)
                cleanup_results["enhanced_memory"] = result
                cleanup_results["cleanup_performed"].append("enhanced_memory")
            
            if (self.character_tracker and 
                hasattr(self.character_tracker, 'cleanup_old_analyses')):
                result = self.character_tracker.cleanup_old_analyses(max_items)
                cleanup_results["character_tracker"] = result
                cleanup_results["cleanup_performed"].append("character_tracker")
            
            cleanup_results["status"] = "success"
            
        except Exception as e:
            logger.error(f"Error during memory cleanup: {e}")
            cleanup_results["status"] = "error"
            cleanup_results["error"] = str(e)
        
        return cleanup_results