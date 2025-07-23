"""
Refactored consolidated playwright using modular components.

This is a simplified, more maintainable version of the consolidated playwright
that uses the extracted modular components for better separation of concerns.
"""

from typing import Dict, Any, List, Optional, Callable, Union
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum
import logging
import time
from datetime import datetime

from thespian.llm import LLMManager
from thespian.llm.theatrical_memory import TheatricalMemory
from thespian.llm.enhanced_memory import EnhancedTheatricalMemory
from thespian.llm.quality_control import TheatricalQualityControl
from thespian.llm.iterative_refinement import IterativeRefinementSystem
from thespian.llm.scene_generation import SceneGenerator, SceneRequirements, SceneGenerationResult, BatchSceneGenerator
from thespian.llm.memory_management import MemoryManager, MemoryIntegrationLevel
from thespian.llm.error_handling import (
    with_error_handling, 
    PlaywrightError, 
    global_error_handler,
    ErrorSeverity
)
from thespian.config_manager import get_config

logger = logging.getLogger(__name__)


class PlaywrightCapability(str, Enum):
    """Capabilities that can be enabled in the playwright."""
    BASIC = "basic"
    ITERATIVE_REFINEMENT = "iterative_refinement"
    MEMORY_ENHANCEMENT = "memory_enhancement"
    NARRATIVE_STRUCTURE = "narrative_structure"
    CHARACTER_TRACKING = "character_tracking"
    COLLABORATIVE = "collaborative"


class RefactoredPlaywright(BaseModel):
    """
    Refactored playwright using modular components.
    
    This version breaks down the large consolidated playwright into
    focused, reusable components for better maintainability and testing.
    """
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    # Core identification
    name: str = Field(default="Refactored Playwright", description="Name of the playwright")
    
    # Core components
    llm_manager: LLMManager
    scene_generator: Optional[SceneGenerator] = None
    memory_manager: Optional[MemoryManager] = None
    batch_generator: Optional[BatchSceneGenerator] = None
    
    # Configuration
    enabled_capabilities: List[PlaywrightCapability] = Field(
        default_factory=lambda: [PlaywrightCapability.BASIC]
    )
    model_type: str = Field(default="ollama", description="LLM model type to use")
    
    # Performance settings
    max_iterations: int = Field(default=5, ge=1, le=10)
    quality_threshold: float = Field(default=0.8, ge=0.0, le=1.0)
    
    def __init__(self, **data: Any) -> None:
        """Initialize the refactored playwright."""
        super().__init__(**data)
        
        config = get_config()
        
        # Initialize memory if memory capabilities are enabled
        memory = None
        if (PlaywrightCapability.MEMORY_ENHANCEMENT in self.enabled_capabilities or
            PlaywrightCapability.CHARACTER_TRACKING in self.enabled_capabilities):
            memory = EnhancedTheatricalMemory()
        
        # Initialize quality control
        quality_control = TheatricalQualityControl()
        
        # Initialize refinement system if needed
        refinement_system = None
        if PlaywrightCapability.ITERATIVE_REFINEMENT in self.enabled_capabilities:
            refinement_system = IterativeRefinementSystem(
                quality_control=quality_control,
                max_iterations=self.max_iterations,
                quality_threshold=self.quality_threshold,
                improvement_threshold=config.quality.improvement_threshold
            )
        
        # Initialize scene generator
        self.scene_generator = SceneGenerator(
            llm_manager=self.llm_manager,
            memory=memory,
            quality_control=quality_control,
            refinement_system=refinement_system,
            model_type=self.model_type
        )
        
        # Initialize memory manager
        if memory:
            integration_level = MemoryIntegrationLevel.BASIC
            if PlaywrightCapability.MEMORY_ENHANCEMENT in self.enabled_capabilities:
                integration_level = MemoryIntegrationLevel.STANDARD
            if PlaywrightCapability.CHARACTER_TRACKING in self.enabled_capabilities:
                integration_level = MemoryIntegrationLevel.DEEP
            
            self.memory_manager = MemoryManager(
                memory=memory,
                enhanced_memory=memory if isinstance(memory, EnhancedTheatricalMemory) else None,
                integration_level=integration_level
            )
        
        # Initialize batch generator
        if config.performance.batch_processing:
            self.batch_generator = BatchSceneGenerator(self.scene_generator)
    
    @with_error_handling(global_error_handler, severity=ErrorSeverity.HIGH)
    def generate_scene(
        self,
        requirements: Union[SceneRequirements, Dict[str, Any]],
        scene_id: Optional[str] = None,
        previous_scenes: Optional[List[str]] = None,
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ) -> SceneGenerationResult:
        """
        Generate a theatrical scene with the specified requirements.
        
        This is the main public interface for scene generation.
        """
        if not self.scene_generator:
            raise PlaywrightError("Scene generator not initialized")
        
        # Convert dict to SceneRequirements if needed
        if isinstance(requirements, dict):
            requirements = SceneRequirements(**requirements)
        
        try:
            result = self.scene_generator.generate_scene(
                requirements=requirements,
                scene_id=scene_id,
                previous_scenes=previous_scenes,
                progress_callback=progress_callback
            )
            
            # Update memory if available
            if self.memory_manager:
                memory_update = self.memory_manager.update_from_scene(
                    result.scene_id,
                    result.scene_content,
                    requirements.model_dump(),
                    lambda prompt: self.llm_manager.get_llm(self.model_type).invoke(prompt)
                )
                
                # Add memory update info to metadata
                result.generation_metadata["memory_update"] = memory_update
            
            return result
            
        except Exception as e:
            raise PlaywrightError(f"Scene generation failed: {str(e)}")
    
    @with_error_handling(global_error_handler, severity=ErrorSeverity.MEDIUM)
    def generate_multiple_scenes(
        self,
        requirements_list: List[Union[SceneRequirements, Dict[str, Any]]],
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ) -> List[SceneGenerationResult]:
        """
        Generate multiple scenes with batch optimization.
        
        Args:
            requirements_list: List of scene requirements
            progress_callback: Optional progress callback
            
        Returns:
            List of scene generation results
        """
        if not requirements_list:
            return []
        
        # Convert dicts to SceneRequirements if needed
        processed_requirements = []
        for req in requirements_list:
            if isinstance(req, dict):
                processed_requirements.append(SceneRequirements(**req))
            else:
                processed_requirements.append(req)
        
        # Use batch generator if available
        if self.batch_generator:
            results = self.batch_generator.generate_multiple_scenes(
                processed_requirements,
                progress_callback
            )
        else:
            # Fall back to individual generation
            results = []
            total_scenes = len(processed_requirements)
            
            for i, req in enumerate(processed_requirements):
                if progress_callback:
                    progress_callback({
                        "batch_progress": i / total_scenes,
                        "current_scene": i + 1,
                        "total_scenes": total_scenes
                    })
                
                previous_scenes = [r.scene_content for r in results]
                result = self.generate_scene(req, previous_scenes=previous_scenes)
                results.append(result)
        
        # Batch update memory if available
        if self.memory_manager and results:
            scene_data = [
                {
                    "scene_id": result.scene_id,
                    "content": result.scene_content,
                    "requirements": result.requirements.model_dump()
                }
                for result in results if result.scene_content
            ]
            
            if scene_data:
                memory_update = self.memory_manager.batch_update_from_scenes(
                    scene_data,
                    lambda prompt: self.llm_manager.get_llm(self.model_type).invoke(prompt),
                    progress_callback
                )
                
                # Add memory update info to the last result's metadata
                if results:
                    results[-1].generation_metadata["batch_memory_update"] = memory_update
        
        return results
    
    def get_capabilities(self) -> List[str]:
        """Get list of enabled capabilities."""
        return [cap.value for cap in self.enabled_capabilities]
    
    def add_capability(self, capability: PlaywrightCapability) -> None:
        """Add a capability to the playwright."""
        if capability not in self.enabled_capabilities:
            self.enabled_capabilities.append(capability)
            # Re-initialize components if needed
            self.__init__(**self.model_dump())
    
    def remove_capability(self, capability: PlaywrightCapability) -> None:
        """Remove a capability from the playwright."""
        if capability in self.enabled_capabilities:
            self.enabled_capabilities.remove(capability)
            # Re-initialize components if needed
            self.__init__(**self.model_dump())
    
    @with_error_handling(global_error_handler, severity=ErrorSeverity.LOW)
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for the playwright."""
        stats = {
            "name": self.name,
            "model_type": self.model_type,
            "capabilities": self.get_capabilities(),
            "timestamp": datetime.now().isoformat()
        }
        
        # Add memory stats if available
        if self.memory_manager:
            stats["memory"] = self.memory_manager.get_memory_stats()
        
        # Add configuration info
        config = get_config()
        stats["configuration"] = {
            "quality_threshold": self.quality_threshold,
            "max_iterations": self.max_iterations,
            "batch_processing": config.performance.batch_processing,
            "cache_enabled": config.performance.cache_enabled
        }
        
        return stats
    
    @with_error_handling(global_error_handler, severity=ErrorSeverity.LOW)
    def cleanup_resources(self) -> Dict[str, Any]:
        """Clean up resources and optimize performance."""
        cleanup_results = {
            "timestamp": datetime.now().isoformat(),
            "actions_performed": []
        }
        
        # Clean up memory if available
        if self.memory_manager:
            memory_cleanup = self.memory_manager.cleanup_old_data()
            cleanup_results["memory_cleanup"] = memory_cleanup
            cleanup_results["actions_performed"].append("memory_cleanup")
        
        # Clear any caches in optimizers
        try:
            from thespian.llm.playwright_optimizations import SceneOptimizer
            # Clear LRU caches
            SceneOptimizer.calculate_scene_similarity.cache_clear()
            cleanup_results["actions_performed"].append("cache_cleanup")
        except Exception as e:
            logger.warning(f"Failed to clear caches: {e}")
        
        cleanup_results["status"] = "success"
        return cleanup_results
    
    def validate_configuration(self) -> List[str]:
        """Validate the current configuration and return any issues."""
        issues = []
        
        if not self.llm_manager:
            issues.append("LLM manager is required")
        
        if not self.scene_generator:
            issues.append("Scene generator not initialized")
        
        if (PlaywrightCapability.MEMORY_ENHANCEMENT in self.enabled_capabilities and 
            not self.memory_manager):
            issues.append("Memory enhancement enabled but memory manager not available")
        
        if self.quality_threshold < 0 or self.quality_threshold > 1:
            issues.append("Quality threshold must be between 0 and 1")
        
        if self.max_iterations < 1:
            issues.append("Max iterations must be at least 1")
        
        # Validate configuration
        config = get_config()
        config_issues = config.validate()
        issues.extend([f"Config: {issue}" for issue in config_issues])
        
        return issues


# Factory function for easy playwright creation
@with_error_handling(global_error_handler, severity=ErrorSeverity.HIGH)
def create_playwright(
    name: str = "Default Playwright",
    capabilities: Optional[List[PlaywrightCapability]] = None,
    model_type: str = "ollama",
    **kwargs
) -> RefactoredPlaywright:
    """
    Factory function to create a properly configured playwright.
    
    Args:
        name: Name for the playwright
        capabilities: List of capabilities to enable
        model_type: LLM model type to use
        **kwargs: Additional configuration options
        
    Returns:
        Configured RefactoredPlaywright instance
    """
    if capabilities is None:
        capabilities = [PlaywrightCapability.BASIC, PlaywrightCapability.ITERATIVE_REFINEMENT]
    
    llm_manager = LLMManager()
    
    playwright = RefactoredPlaywright(
        name=name,
        llm_manager=llm_manager,
        enabled_capabilities=capabilities,
        model_type=model_type,
        **kwargs
    )
    
    # Validate configuration
    issues = playwright.validate_configuration()
    if issues:
        logger.warning(f"Configuration issues detected: {issues}")
    
    logger.info(f"Created playwright '{name}' with capabilities: {[c.value for c in capabilities]}")
    
    return playwright


# Backward compatibility alias
Playwright = RefactoredPlaywright