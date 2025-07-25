"""
Modular scene generation system extracted from consolidated playwright.

This module breaks down the large consolidated playwright into focused,
reusable components for better maintainability and testing.
"""

from typing import Dict, Any, List, Optional, Callable, Union
from pydantic import BaseModel, Field
import logging
import time
from datetime import datetime

from thespian.llm import LLMManager
from thespian.llm.theatrical_memory import TheatricalMemory
from thespian.llm.enhanced_memory import EnhancedTheatricalMemory
from thespian.llm.quality_control import TheatricalQualityControl
from thespian.llm.iterative_refinement import IterativeRefinementSystem
from thespian.llm.playwright_optimizations import SceneOptimizer, ContentValidator
from thespian.llm.error_handling import (
    with_error_handling, 
    PlaywrightError, 
    global_error_handler,
    ErrorSeverity
)
from thespian.config_manager import get_config

logger = logging.getLogger(__name__)


class SceneRequirements(BaseModel):
    """Requirements for scene generation (extracted from consolidated playwright)."""
    
    setting: str = Field(..., min_length=1, description="The setting of the scene")
    characters: List[str] = Field(..., description="List of characters in the scene")
    props: List[str] = Field(default_factory=list, description="List of props needed for the scene")
    lighting: str = Field(..., min_length=1, description="Lighting requirements for the scene")
    sound: str = Field(..., min_length=1, description="Sound requirements for the scene")
    style: str = Field(..., min_length=1, description="The style of the scene")
    period: str = Field(..., min_length=1, description="The time period of the scene")
    target_audience: str = Field(..., min_length=1, description="The target audience for the scene")
    act_number: Optional[int] = None
    scene_number: Optional[int] = None
    premise: Optional[str] = Field(default=None, description="The premise or brief summary of the scene")
    pacing: Optional[str] = Field(default=None, description="The desired pacing of the scene")
    tone: Optional[str] = Field(default=None, description="The desired tone of the scene")
    emotional_arc: Optional[str] = Field(default=None, description="The emotional arc within the scene")
    key_conflict: Optional[str] = Field(default=None, description="The key conflict or goal within the scene")


class SceneGenerationResult(BaseModel):
    """Result of scene generation process."""
    
    scene_content: str = Field(..., description="Generated scene content")
    scene_id: str = Field(..., description="Unique scene identifier")
    requirements: SceneRequirements = Field(..., description="Original requirements")
    quality_scores: Dict[str, float] = Field(default_factory=dict, description="Quality evaluation scores")
    generation_metadata: Dict[str, Any] = Field(default_factory=dict, description="Generation metadata")
    iterations_performed: int = Field(default=1, description="Number of refinement iterations")
    total_generation_time: float = Field(default=0.0, description="Total time taken for generation")


class SceneGenerator:
    """
    Modular scene generation system.
    
    This class extracts the core scene generation logic from the consolidated
    playwright for better maintainability and reusability.
    """
    
    def __init__(
        self,
        llm_manager: LLMManager,
        memory: Optional[TheatricalMemory] = None,
        quality_control: Optional[TheatricalQualityControl] = None,
        refinement_system: Optional[IterativeRefinementSystem] = None,
        model_type: str = "ollama"
    ):
        """Initialize the scene generator."""
        self.llm_manager = llm_manager
        self.memory = memory
        self.quality_control = quality_control
        self.refinement_system = refinement_system
        self.model_type = model_type
        self.config = get_config()
        
        # Initialize components if not provided
        if not self.quality_control:
            self.quality_control = TheatricalQualityControl()
    
    @with_error_handling(global_error_handler, severity=ErrorSeverity.HIGH)
    def generate_scene(
        self,
        requirements: SceneRequirements,
        scene_id: Optional[str] = None,
        previous_scenes: Optional[List[str]] = None,
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ) -> SceneGenerationResult:
        """
        Generate a theatrical scene based on requirements.
        
        Args:
            requirements: Scene generation requirements
            scene_id: Optional scene identifier
            previous_scenes: List of previously generated scenes for uniqueness checking
            progress_callback: Optional callback for progress updates
            
        Returns:
            SceneGenerationResult with generated content and metadata
        """
        start_time = time.time()
        scene_id = scene_id or f"scene_{int(time.time())}"
        
        try:
            # Validate requirements
            validation_result = ContentValidator.validate_scene_content(
                f"Requirements: {requirements.model_dump()}", 
                requirements.model_dump()
            )
            
            if not validation_result["valid"]:
                raise PlaywrightError(f"Invalid requirements: {validation_result['errors']}")
            
            # Generate initial scene
            if progress_callback:
                progress_callback({"phase": "initial_generation", "progress": 0.2})
            
            scene_content = self._generate_initial_scene(requirements)
            
            # Check uniqueness if previous scenes provided
            if previous_scenes:
                if not SceneOptimizer.is_scene_unique(
                    scene_content, 
                    previous_scenes, 
                    self.config.quality.similarity_threshold
                ):
                    logger.warning("Generated scene too similar to previous scenes, regenerating...")
                    scene_content = self._generate_initial_scene(requirements, variation=True)
            
            # Apply iterative refinement if enabled
            iterations_performed = 1
            if self.refinement_system and self.config.quality.enable_iterative_refinement:
                if progress_callback:
                    progress_callback({"phase": "refinement", "progress": 0.6})
                
                refinement_result = self.refinement_system.refine_scene_iteratively(
                    scene_content,
                    lambda prompt: self.llm_manager.get_llm(self.model_type).invoke(prompt),
                    requirements.model_dump(),
                    progress_callback
                )
                
                scene_content = refinement_result["refined_scene"]
                iterations_performed = refinement_result["iterations_performed"]
            
            # Final quality evaluation
            if progress_callback:
                progress_callback({"phase": "quality_evaluation", "progress": 0.9})
            
            quality_scores = {}
            if self.quality_control:
                evaluation = self.quality_control.evaluate_scene(scene_content, requirements)
                quality_scores = evaluation.get("scores", {})
            
            # Update memory if available
            if self.memory:
                try:
                    self._update_memory_from_scene(scene_id, scene_content, requirements)
                except Exception as e:
                    logger.warning(f"Failed to update memory: {e}")
            
            total_time = time.time() - start_time
            
            if progress_callback:
                progress_callback({"phase": "complete", "progress": 1.0})
            
            return SceneGenerationResult(
                scene_content=scene_content,
                scene_id=scene_id,
                requirements=requirements,
                quality_scores=quality_scores,
                generation_metadata={
                    "model_type": self.model_type,
                    "timestamp": datetime.now().isoformat(),
                    "config_version": "1.0"
                },
                iterations_performed=iterations_performed,
                total_generation_time=total_time
            )
            
        except Exception as e:
            total_time = time.time() - start_time
            logger.error(f"Scene generation failed after {total_time:.2f}s: {e}")
            raise PlaywrightError(f"Scene generation failed: {str(e)}")
    
    @with_error_handling(global_error_handler, severity=ErrorSeverity.MEDIUM)
    def _generate_initial_scene(
        self, 
        requirements: SceneRequirements, 
        variation: bool = False
    ) -> str:
        """Generate the initial scene content."""
        prompt = self._construct_scene_prompt(requirements, variation)
        
        try:
            llm = self.llm_manager.get_llm(self.model_type)
            response = llm.invoke(prompt)
            
            # Extract content
            if hasattr(response, 'content'):
                content = str(response.content)
            else:
                content = str(response)
            
            if not content.strip():
                raise PlaywrightError("Empty response from LLM")
            
            # Basic length validation
            if len(content) < 100:
                logger.warning("Generated scene is very short, may need refinement")
            
            return content
            
        except Exception as e:
            raise PlaywrightError(f"Failed to generate initial scene: {str(e)}")
    
    def _construct_scene_prompt(
        self, 
        requirements: SceneRequirements, 
        variation: bool = False
    ) -> str:
        """Construct the prompt for scene generation."""
        variation_text = "\n\nIMPORTANT: Generate a unique variation different from previous attempts." if variation else ""
        
        characters_str = ", ".join(requirements.characters)
        
        prompt = f"""Generate a theatrical scene with the following requirements:

Setting: {requirements.setting}
Characters: {characters_str}
Style: {requirements.style}
Period: {requirements.period}
Target Audience: {requirements.target_audience}

Technical Requirements:
- Lighting: {requirements.lighting}
- Sound: {requirements.sound}
- Props: {', '.join(requirements.props) if requirements.props else 'Minimal props'}

Narrative Requirements:"""
        
        if requirements.premise:
            prompt += f"\n- Premise: {requirements.premise}"
        if requirements.pacing:
            prompt += f"\n- Pacing: {requirements.pacing}"
        if requirements.tone:
            prompt += f"\n- Tone: {requirements.tone}"
        if requirements.emotional_arc:
            prompt += f"\n- Emotional Arc: {requirements.emotional_arc}"
        if requirements.key_conflict:
            prompt += f"\n- Key Conflict: {requirements.key_conflict}"
        
        prompt += f"""

Create a complete scene with:
1. Detailed stage directions in [brackets]
2. Natural, character-appropriate dialogue
3. Clear emotional progression and character development
4. Proper theatrical formatting
5. Rich sensory details and atmosphere
6. Scene length: approximately {self.config.quality.max_iterations * 1000} words

Format as a professional theatrical script with proper spacing and stage direction formatting.{variation_text}"""
        
        return prompt
    
    def _update_memory_from_scene(
        self, 
        scene_id: str, 
        scene_content: str, 
        requirements: SceneRequirements
    ) -> None:
        """Update memory with information from the generated scene."""
        if not self.memory:
            return
        
        try:
            # Extract character information from the scene
            for character in requirements.characters:
                # Simple character presence tracking
                if character.lower() in scene_content.lower():
                    # Update character profile if using enhanced memory
                    if isinstance(self.memory, EnhancedTheatricalMemory):
                        self.memory.update_character_from_scene(
                            character,
                            scene_content,
                            lambda prompt: self.llm_manager.get_llm(self.model_type).invoke(prompt)
                        )
            
            # Store scene metadata
            scene_metadata = {
                "scene_id": scene_id,
                "setting": requirements.setting,
                "characters": requirements.characters,
                "timestamp": datetime.now().isoformat(),
                "length": len(scene_content)
            }
            
            # Store in memory if method exists
            if hasattr(self.memory, 'store_scene_metadata'):
                self.memory.store_scene_metadata(scene_id, scene_metadata)
                
        except Exception as e:
            logger.warning(f"Failed to update memory from scene {scene_id}: {e}")


class BatchSceneGenerator:
    """Batch scene generation for improved performance."""
    
    def __init__(self, scene_generator: SceneGenerator):
        self.scene_generator = scene_generator
        self.config = get_config()
    
    @with_error_handling(global_error_handler, severity=ErrorSeverity.MEDIUM)
    def generate_multiple_scenes(
        self,
        requirements_list: List[SceneRequirements],
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ) -> List[SceneGenerationResult]:
        """Generate multiple scenes with batch optimization."""
        results = []
        total_scenes = len(requirements_list)
        
        for i, requirements in enumerate(requirements_list):
            try:
                # Update progress
                if progress_callback:
                    progress_callback({
                        "batch_progress": i / total_scenes,
                        "current_scene": i + 1,
                        "total_scenes": total_scenes
                    })
                
                # Generate individual scene
                scene_id = f"batch_scene_{i+1}_{int(time.time())}"
                previous_scenes = [result.scene_content for result in results]
                
                result = self.scene_generator.generate_scene(
                    requirements,
                    scene_id,
                    previous_scenes,
                    lambda data: progress_callback({**data, "scene_index": i}) if progress_callback else None
                )
                
                results.append(result)
                
            except Exception as e:
                logger.error(f"Failed to generate scene {i+1}: {e}")
                # Create placeholder result for failed generation
                results.append(SceneGenerationResult(
                    scene_content=f"[Scene generation failed: {str(e)}]",
                    scene_id=f"failed_scene_{i+1}",
                    requirements=requirements,
                    quality_scores={"error": 0.0},
                    generation_metadata={"error": str(e)},
                    iterations_performed=0,
                    total_generation_time=0.0
                ))
        
        if progress_callback:
            progress_callback({"batch_progress": 1.0, "completed": True})
        
        return results