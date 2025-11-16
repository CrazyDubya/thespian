"""
Consolidated playwright module for generating theatrical productions.

This module provides a consolidated implementation of the playwright functionality
with modular capabilities including memory enhancement, iterative refinement, and 
advanced story structure awareness.
"""

from typing import Dict, Any, List, Optional, Callable, Union, TypeVar, cast
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum
import logging
import time
import json
import uuid
from datetime import datetime
import os
from pathlib import Path

from thespian.llm import LLMManager
from thespian.llm.theatrical_memory import TheatricalMemory, CharacterProfile, StoryOutline
from thespian.llm.enhanced_memory import EnhancedTheatricalMemory
from thespian.llm.theatrical_advisors import TheatricalAdvisor, AdvisorFeedback, AdvisorManager
from thespian.llm.quality_control import TheatricalQualityControl
from thespian.llm.dialogue_system import DialogueSystem
from thespian.llm.iterative_refinement import IterativeRefinementSystem
from thespian.llm.character_analyzer import CharacterTracker, SceneCharacterAnalysis
from thespian.config.prompts import PROMPT_TEMPLATES
from thespian.config.enhanced_prompts import ENHANCED_PROMPT_TEMPLATES
from thespian.processors.scene_processor import SceneProcessor
from thespian.processors.act_processor import ActProcessor
from thespian.checkpoints.checkpoint_manager import CheckpointManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

T = TypeVar('T')

class IterationMetrics(BaseModel):
    """Metrics for a single iteration of scene enhancement."""
    iteration_number: int
    timestamp: datetime = Field(default_factory=datetime.now)
    quality_scores: Dict[str, float]
    significant_changes: bool
    advisor_dialogues: int
    enhancement_time: float


class SceneRequirements(BaseModel):
    """Requirements for scene generation."""
    model_config = ConfigDict(arbitrary_types_allowed=True, protected_namespaces=())
    
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

    premise: Optional[str] = Field(default=None, description="The premise or a brief summary of the scene")
    pacing: Optional[str] = Field(default=None, description="The desired pacing of the scene (e.g., Slow Burn, Fast-paced)")
    tone: Optional[str] = Field(default=None, description="The desired tone of the scene (e.g., Suspenseful, Comedic)")
    emotional_arc: Optional[str] = Field(default=None, description="The emotional arc or progression within the scene")
    key_conflict: Optional[str] = Field(default=None, description="The key conflict or goal within the scene") 
    resolution: Optional[str] = Field(default=None, description="The desired resolution or outcome of the scene, if any")
    generation_directives: Optional[str] = Field(default=None, description="Specific directives or constraints for content generation")
    llm_model_type: Optional[str] = Field(default=None, alias="model_type", description="The type of language model to be used.")

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        if not self.characters or not isinstance(self.characters, list) or len(self.characters) < 1:
            raise ValueError("At least one character is required.")


class CheckpointData(BaseModel):
    """Data structure for scene generation checkpoint."""
    scene_id: str = Field(..., min_length=1, max_length=100)
    current_scene: str = Field(..., min_length=1, max_length=100000)  # Reasonable max length for scene content
    iteration: int = Field(..., ge=0, le=100)  # Reasonable max iterations
    feedback: Dict[str, Any] = Field(default_factory=dict)
    timing_metrics: Dict[str, float] = Field(default_factory=dict)
    iteration_metrics: List[Dict[str, Any]] = Field(default_factory=list)
    requirements: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)
    error: Optional[str] = None

    @classmethod
    def from_llm_response(cls, scene_id: str, response: Any, **kwargs: Any) -> 'CheckpointData':
        """Create checkpoint data from LLM response with validation."""
        if not scene_id or not isinstance(scene_id, str):
            raise ValueError("scene_id must be a non-empty string")
            
        if response is None:
            raise ValueError("response cannot be None")
            
        try:
            # Handle different response types
            if hasattr(response, 'content'):
                content = str(response.content)
            elif isinstance(response, (str, bytes)):
                content = str(response)
            else:
                content = str(response)
                
            # Validate content
            if not content.strip():
                raise ValueError("response content is empty")
                
            # Check content length
            if len(content) > 100000:  # 100KB limit
                content = content[:100000] + "... [truncated]"
                
            # Validate kwargs
            if 'feedback' in kwargs and not isinstance(kwargs['feedback'], dict):
                kwargs['feedback'] = {}
            if 'timing_metrics' in kwargs and not isinstance(kwargs['timing_metrics'], dict):
                kwargs['timing_metrics'] = {}
            if 'iteration_metrics' in kwargs and not isinstance(kwargs['iteration_metrics'], list):
                kwargs['iteration_metrics'] = []
            if 'requirements' in kwargs and not isinstance(kwargs['requirements'], dict):
                kwargs['requirements'] = {}
                
            return cls(
                scene_id=scene_id,
                current_scene=content,
                **kwargs
            )
        except Exception as e:
            raise ValueError(f"Failed to create checkpoint data: {str(e)}")


class PlaywrightCapability(str, Enum):
    """Capabilities that can be enabled in the playwright."""
    BASIC = "basic"
    ITERATIVE_REFINEMENT = "iterative_refinement"
    MEMORY_ENHANCEMENT = "memory_enhancement"
    NARRATIVE_STRUCTURE = "narrative_structure"
    CHARACTER_TRACKING = "character_tracking"
    COLLABORATIVE = "collaborative"


class Playwright(BaseModel):
    """
    Consolidated playwright for generating theatrical productions.
    
    This class integrates all capabilities from the previous separate implementations
    into a single modular implementation, using composition rather than inheritance.
    """
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    # Core components
    name: str = Field(..., description="Name of the playwright")
    llm_manager: LLMManager
    memory: TheatricalMemory
    advisor_manager: Optional[AdvisorManager] = None
    quality_control: Optional[TheatricalQualityControl] = None
    scene_processor: Optional[SceneProcessor] = None
    act_processor: Optional[ActProcessor] = None
    checkpoint_manager: Optional[CheckpointManager] = None
    dialogue_system: Optional[DialogueSystem] = None
    
    # Memory and character tracking components
    enhanced_memory: Optional[EnhancedTheatricalMemory] = None
    character_tracker: Optional[CharacterTracker] = None
    
    # Capability configuration
    enabled_capabilities: List[PlaywrightCapability] = Field(
        default_factory=lambda: [PlaywrightCapability.BASIC]
    )
    model_type: str = "ollama"
    
    # Generation parameters
    max_iterations: int = Field(default=5, ge=1, le=10)
    quality_threshold: float = Field(default=0.8, ge=0.0, le=1.0)
    character_arcs: Dict[str, List[str]] = Field(default_factory=dict)
    plot_points: List[str] = Field(default_factory=list)
    previous_scenes: List[str] = Field(default_factory=list)
    story_outline: Optional[StoryOutline] = None
    use_enhanced_prompts: bool = Field(default=True)
    
    # Iterative refinement parameters
    refinement_system: Optional[IterativeRefinementSystem] = None
    refinement_max_iterations: int = Field(default=5)
    refinement_quality_threshold: float = Field(default=0.85)
    refinement_improvement_threshold: float = Field(default=0.02)
    target_scene_length: int = Field(default=5000)
    
    # Memory enhancement parameters
    track_characters: bool = Field(default=True)
    track_narrative: bool = Field(default=True)
    memory_integration_level: int = Field(default=2, ge=1, le=3)  # 1=basic, 2=standard, 3=deep

    # Generation control
    _generation_cancelled: bool = Field(default=False, exclude=True)

    def __init__(self, **data: Any) -> None:
        """Initialize the playwright with appropriate components."""
        super().__init__(**data)
        
        # Initialize components if not provided
        if not self.scene_processor:
            self.scene_processor = SceneProcessor()
        if not self.act_processor:
            self.act_processor = ActProcessor()
        if not self.quality_control:
            self.quality_control = TheatricalQualityControl()
        if not self.checkpoint_manager:
            self.checkpoint_manager = CheckpointManager()
            
        # Initialize enhanced memory if needed
        if PlaywrightCapability.MEMORY_ENHANCEMENT in self.enabled_capabilities and not self.enhanced_memory:
            if isinstance(self.memory, EnhancedTheatricalMemory):
                self.enhanced_memory = self.memory
            else:
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
        
        # Initialize character tracker if needed
        if PlaywrightCapability.CHARACTER_TRACKING in self.enabled_capabilities and not self.character_tracker and self.enhanced_memory:
            self.character_tracker = CharacterTracker(memory=self.enhanced_memory)
        
        # Initialize refinement system if needed
        if PlaywrightCapability.ITERATIVE_REFINEMENT in self.enabled_capabilities and not self.refinement_system and self.quality_control:
            self.refinement_system = IterativeRefinementSystem(
                quality_control=self.quality_control,
                max_iterations=self.refinement_max_iterations,
                quality_threshold=self.refinement_quality_threshold,
                improvement_threshold=self.refinement_improvement_threshold
            )
    
    def get_llm(self) -> Any:
        """Get the LLM instance."""
        return self.llm_manager.get_llm(self.model_type)

    def stop_generation(self) -> None:
        """Request to stop the current scene generation."""
        logger.info("Stop generation requested")
        self._generation_cancelled = True

    def reset_cancellation(self) -> None:
        """Reset the cancellation flag."""
        self._generation_cancelled = False

    def is_generation_cancelled(self) -> bool:
        """Check if generation has been cancelled."""
        return self._generation_cancelled

    def _construct_scene_prompt(
        self,
        requirements: SceneRequirements,
        previous_scene: Optional[str] = None,
        previous_feedback: Optional[Dict[str, Any]] = None
    ) -> str:
        """Construct the prompt for scene generation."""
        # Use enhanced prompts if enabled
        if self.use_enhanced_prompts:
            prompt_template = ENHANCED_PROMPT_TEMPLATES["enhanced_scene_generation"]
        else:
            prompt_template = PROMPT_TEMPLATES["scene_generation"]
            
        if not self.story_outline:
            raise ValueError("story_outline is not initialized")
            
        current_act = self.story_outline.get_act_outline(requirements.act_number)
        if not current_act:
            raise ValueError(f"No outline found for Act {requirements.act_number}")
            
        current_scene_outline = current_act["key_events"][requirements.scene_number - 1]
        
        # Get all previously generated scenes for uniqueness validation
        previous_scenes = self._get_all_previous_scenes(requirements.act_number, requirements.scene_number)
        
        # Format previous scene
        previous_scene_content = "This is the first scene"
        if previous_scene:
            if isinstance(previous_scene, dict):
                if "scene" in previous_scene:
                    previous_scene_content = str(previous_scene["scene"])
                elif "scene_content" in previous_scene:
                    previous_scene_content = str(previous_scene["scene_content"])
            elif isinstance(previous_scene, str):
                previous_scene_content = previous_scene
            else:
                logger.warning(f"Unexpected previous scene format: {type(previous_scene)}")
        
        # Format previous feedback
        previous_feedback_content = "No previous feedback"
        if previous_feedback:
            if isinstance(previous_feedback, dict):
                previous_feedback_content = json.dumps(previous_feedback)
            elif isinstance(previous_feedback, str):
                previous_feedback_content = previous_feedback
            else:
                logger.warning(f"Unexpected previous feedback format: {type(previous_feedback)}")
        
        # Get memory context if available
        memory_context = ""
        if PlaywrightCapability.MEMORY_ENHANCEMENT in self.enabled_capabilities and self.enhanced_memory:
            try:
                context = self._get_memory_context(requirements.act_number, requirements.scene_number)
                if context:
                    memory_context = f"\n\nMEMORY CONTEXT:\n{json.dumps(context, indent=2)}"
            except Exception as e:
                logger.error("Error getting memory context: " + str(e))
        
        # Get narrative structure context if available
        narrative_context = ""
        if PlaywrightCapability.NARRATIVE_STRUCTURE in self.enabled_capabilities:
            try:
                from .advanced_story_structure import AdvancedStoryPlanner, DynamicScenePlanner
                # This would be added in actual implementation
                narrative_context = "\n\nNARRATIVE STRUCTURE:\nStandard three-act structure"
            except (ImportError, Exception) as e:
                logger.error("Error loading narrative structure components: " + str(e))
        
        # Build uniqueness constraint
        uniqueness_constraint = self._build_uniqueness_constraint(previous_scenes, requirements)
        
        # Build scene-specific directive based on generation context
        scene_directive = self._build_scene_specific_directive(requirements, current_scene_outline)
        
        return prompt_template.format(
            title=self.story_outline.title,
            act_number=requirements.act_number,
            act_description=current_act['description'],
            scene_number=requirements.scene_number,
            scene_outline=current_scene_outline,
            setting=requirements.setting,
            characters=', '.join(requirements.characters),
            props=', '.join(requirements.props),
            lighting=requirements.lighting,
            sound=requirements.sound,
            style=requirements.style,
            period=requirements.period,
            target_audience=requirements.target_audience,
            previous_scene=previous_scene_content,
            previous_feedback=previous_feedback_content,
            min_length=self.scene_processor.min_length if self.scene_processor else 2000,
            max_length=self.scene_processor.max_length if self.scene_processor else 8000,
            memory_context=memory_context,
            narrative_context=narrative_context,
            uniqueness_constraint=uniqueness_constraint,
            scene_directive=scene_directive
        )
    
    def generate_scene(
        self,
        requirements: SceneRequirements,
        previous_scene: Optional[str] = None,
        previous_feedback: Optional[Dict[str, Any]] = None,
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
        use_refinement: Optional[bool] = None,
        generation_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a scene based on requirements.

        Args:
            requirements: Scene requirements
            previous_scene: Optional previous scene content
            previous_feedback: Optional feedback from previous generation
            progress_callback: Optional callback for reporting progress
            use_refinement: Whether to use iterative refinement (overrides capability setting)

        Returns:
            Dict containing the generated scene and metadata
        """
        # Reset cancellation flag at the start
        self.reset_cancellation()

        # Set generation type for directive building
        self._current_generation_type = generation_type or "basic"

        # Determine if refinement should be used
        should_use_refinement = use_refinement if use_refinement is not None else (
            PlaywrightCapability.ITERATIVE_REFINEMENT in self.enabled_capabilities
        )

        # Enhance requirements with memory if applicable
        if PlaywrightCapability.MEMORY_ENHANCEMENT in self.enabled_capabilities and self.memory_integration_level >= 2:
            enhanced_requirements = self._enhance_requirements_with_memory(requirements)
        else:
            enhanced_requirements = requirements

        # Create a unique scene ID
        scene_id = str(uuid.uuid4())

        # Start timing
        start_time = time.time()

        # Report initial progress
        if progress_callback:
            progress_callback({
                "phase": "initial_generation",
                "current_step": 1,
                "total_steps": 3 if should_use_refinement else 1,
                "message": "Generating initial scene draft"
            })

        try:
            # Check for cancellation before initial generation
            if self.is_generation_cancelled():
                logger.info("Generation cancelled before initial scene generation")
                raise InterruptedError("Scene generation was cancelled by user")

            # Generate initial scene
            initial_scene_result = self._generate_initial_scene(
                enhanced_requirements, previous_scene, previous_feedback
            )
            initial_scene = initial_scene_result["scene"]
            initial_evaluation = initial_scene_result["evaluation"]

            # Check for cancellation after initial generation
            if self.is_generation_cancelled():
                logger.info("Generation cancelled after initial scene generation")
                raise InterruptedError("Scene generation was cancelled by user")
            
            # Stop here if refinement is disabled
            if not should_use_refinement:
                result = initial_scene_result
                result["scene_id"] = scene_id
                
                # Update memory if applicable
                if (PlaywrightCapability.MEMORY_ENHANCEMENT in self.enabled_capabilities or 
                    PlaywrightCapability.CHARACTER_TRACKING in self.enabled_capabilities):
                    self._update_memory_from_scene(scene_id, initial_scene)
                
                # Add scene to previous scenes
                self.previous_scenes.append(initial_scene)
                
                return result
            
            # Perform refinement
            if progress_callback:
                progress_callback({
                    "phase": "refinement",
                    "current_step": 2,
                    "total_steps": 3,
                    "message": "Refining scene content"
                })

            # Check for cancellation before refinement
            if self.is_generation_cancelled():
                logger.info("Generation cancelled before refinement")
                raise InterruptedError("Scene generation was cancelled by user")

            if self.refinement_system:
                refinement_result = self.refinement_system.refine_scene_iteratively(
                    initial_scene,
                    lambda prompt: self.get_llm().invoke(prompt),
                    {**(enhanced_requirements.model_dump() if hasattr(enhanced_requirements, 'model_dump') else enhanced_requirements.dict()), "scene_id": scene_id},
                    progress_callback
                )

                # Check for cancellation after refinement
                if self.is_generation_cancelled():
                    logger.info("Generation cancelled after refinement")
                    raise InterruptedError("Scene generation was cancelled by user")

                final_scene = refinement_result["refined_scene"]
                final_evaluation = refinement_result["final_evaluation"]
                
                # Report expansion progress if needed
                if progress_callback and len(final_scene) < self.target_scene_length:
                    progress_callback({
                        "phase": "expansion",
                        "current_step": 3,
                        "total_steps": 3,
                        "message": "Expanding scene with details"
                    })
                
                # Expand scene if it's too short
                current_length = len(final_scene)
                if current_length < self.target_scene_length:
                    expansion_result = self.refinement_system.expand_scene_content(
                        final_scene,
                        lambda prompt: self.get_llm().invoke(prompt),
                        self.target_scene_length,
                        progress_callback
                    )
                    final_scene = expansion_result["expanded_scene"]
                else:
                    expansion_result = {
                        "original_length": current_length,
                        "final_length": current_length,
                        "expansion_ratio": 1.0
                    }
            else:
                final_scene = initial_scene
                final_evaluation = initial_evaluation
                refinement_result = {
                    "iterations_performed": 0,
                    "overall_improvement": 0.0
                }
                expansion_result = {
                    "original_length": len(initial_scene),
                    "final_length": len(initial_scene),
                    "expansion_ratio": 1.0
                }
            
            # Update memory if applicable
            if (PlaywrightCapability.MEMORY_ENHANCEMENT in self.enabled_capabilities or 
                PlaywrightCapability.CHARACTER_TRACKING in self.enabled_capabilities):
                self._update_memory_from_scene(scene_id, final_scene)
            
            # Add scene to previous scenes
            self.previous_scenes.append(final_scene)
            
            # Calculate total time
            total_time = time.time() - start_time
            
            # Return the final result
            result = {
                "scene": final_scene,
                "evaluation": final_evaluation,
                "initial_evaluation": initial_evaluation,
                "timing_metrics": {
                    "initial_generation": initial_scene_result.get("timing_metrics", {}).get("total_time", 0),
                    "refinement_iterations": refinement_result.get("iterations_performed", 0),
                    "expansion_ratio": expansion_result.get("expansion_ratio", 1.0),
                    "total_time": total_time
                },
                "iterations": refinement_result.get("iterations_performed", 0) + 1,
                "iteration_metrics": refinement_result.get("iteration_metrics", []),
                "quality_improvement": refinement_result.get("overall_improvement", 0.0),
                "scene_id": scene_id
            }
            
            # Add memory context if applicable
            if PlaywrightCapability.MEMORY_ENHANCEMENT in self.enabled_capabilities and self.enhanced_memory:
                result["memory_context"] = self._get_memory_context(
                    enhanced_requirements.act_number, 
                    enhanced_requirements.scene_number
                )
            
            return result

        except Exception as e:
            logger.error("Error in scene generation: " + str(e))
            raise

    async def generate_scene_content(
        self,
        requirements: SceneRequirements,
        story_outline: Optional[StoryOutline] = None,
        previous_scenes: Optional[str] = None,
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
        use_refinement: Optional[bool] = None,
        generation_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Async wrapper for generate_scene that matches TUI expectations.

        This method provides backwards compatibility with the TUI which expects:
        - An async method
        - Return dict with "text", "quality_score", and "critique" keys
        - Parameters for story_outline and previous_scenes

        Args:
            requirements: Scene requirements
            story_outline: Optional story outline (will update self.story_outline)
            previous_scenes: Optional previous scene content
            progress_callback: Optional callback for reporting progress
            use_refinement: Whether to use iterative refinement
            generation_type: Type of generation to perform

        Returns:
            Dict with keys: text, quality_score, critique, timing_metrics, iterations
        """
        # Update story outline if provided
        if story_outline:
            self.story_outline = story_outline

        # Call the sync generate_scene method
        import asyncio
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: self.generate_scene(
                requirements=requirements,
                previous_scene=previous_scenes,
                previous_feedback=None,
                progress_callback=progress_callback,
                use_refinement=use_refinement,
                generation_type=generation_type
            )
        )

        # Map the result to TUI-expected format
        evaluation = result.get("evaluation", {})

        # Extract quality score from evaluation
        quality_score = None
        if isinstance(evaluation, dict):
            quality_score = evaluation.get("overall_score") or evaluation.get("quality_score")

        # Extract critique from evaluation
        critique = None
        if isinstance(evaluation, dict):
            critique = evaluation.get("critique") or evaluation.get("summary")

        return {
            "text": result.get("scene", ""),
            "quality_score": quality_score,
            "critique": critique,
            "timing_metrics": result.get("timing_metrics", {}),
            "iterations": result.get("iterations", 1),
            "scene_id": result.get("scene_id"),
            "evaluation": evaluation,  # Include full evaluation for reference
        }

    def _generate_initial_scene(
        self, 
        requirements: SceneRequirements, 
        previous_scene: Optional[str] = None,
        previous_feedback: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate the initial scene draft."""
        start_time = time.time()
        
        # Get previous scenes for uniqueness validation
        previous_scenes = self._get_all_previous_scenes(requirements.act_number, requirements.scene_number)
        
        max_retries = 3
        for attempt in range(max_retries):
            # Construct the prompt
            prompt = self._construct_scene_prompt(requirements, previous_scene, previous_feedback)
            
            # Generate the scene with self-correction
            max_scene_retries = 2
            for scene_attempt in range(max_scene_retries + 1):
                if scene_attempt > 0:
                    # Add corrective feedback for retry
                    correction_prompt = f"""CORRECTION NEEDED: Your previous response was inadequate for scene generation.

Previous response that failed:
{scene_content[:1000]}...

Please provide a complete scene with:
- Character names in ALL CAPS
- Stage directions in (parentheses)
- Technical cues in [brackets]
- Minimum 2000 characters
- Proper theatrical formatting
- Clear dramatic structure

{prompt}"""
                    response = self.get_llm().invoke(correction_prompt)
                else:
                    response = self.get_llm().invoke(prompt)
                    
                scene_content = str(response.content)
                
                # Basic validation - check if content is substantial
                if len(scene_content) > 1500:  # Minimum content threshold
                    break
                else:
                    logger.warning(f"Scene generation attempt {scene_attempt + 1} produced insufficient content ({len(scene_content)} chars)")
                    if scene_attempt == max_scene_retries:
                        logger.error("All scene generation attempts failed - using what we have")
            
            # Process the scene
            if not self.scene_processor:
                raise ValueError("scene_processor is not initialized")
                
            processed_content = self.scene_processor.process_scene_content(scene_content)
            
            # Validate uniqueness
            if self._validate_scene_uniqueness(processed_content["scene"], previous_scenes):
                logger.info(f"Scene uniqueness validated on attempt {attempt + 1}")
                break
            elif attempt < max_retries - 1:
                logger.warning(f"Scene similarity detected, retrying (attempt {attempt + 1}/{max_retries})")
                # Add feedback for next attempt
                previous_feedback = {
                    "retry_reason": "scene_similarity",
                    "message": "The generated scene was too similar to previous scenes. Generate a completely different scene."
                }
                continue
            else:
                logger.error("Failed to generate unique scene after maximum retries")
                # Continue with the last attempt despite similarity
        
        # Evaluate the scene
        if not self.quality_control:
            raise ValueError("quality_control is not initialized")
            
        evaluation = self.quality_control.evaluate_scene(processed_content["scene"], requirements)
        
        # Calculate timing metrics
        end_time = time.time()
        timing_metrics = {
            "start_time": start_time,
            "end_time": end_time,
            "total_time": end_time - start_time,
            "attempts": attempt + 1
        }
        
        return {
            "scene": processed_content["scene"],
            "narrative_analysis": processed_content.get("narrative_analysis", ""),
            "evaluation": evaluation,
            "timing_metrics": timing_metrics,
            "raw_content": processed_content.get("raw_content", ""),
            "uniqueness_validated": True
        }
    
    def _enhance_requirements_with_memory(self, requirements: SceneRequirements) -> SceneRequirements:
        """Enhance scene requirements with memory context."""
        if not PlaywrightCapability.MEMORY_ENHANCEMENT in self.enabled_capabilities or not self.enhanced_memory:
            return requirements
            
        # Get memory context
        memory_context = self._get_memory_context(requirements.act_number, requirements.scene_number)
        
        # Create a copy of the requirements with memory enhancements
        req_dict = requirements.model_dump() if hasattr(requirements, 'model_dump') else requirements.dict()
        
        # Add character information if available
        if memory_context.get("character_states") and len(memory_context["character_states"]) > 0:
            # Enhanced character information for the prompt
            character_contexts = []
            for char_id, state in memory_context["character_states"].items():
                if state["name"] in requirements.characters:
                    profile = self.enhanced_memory.get_character_profile(char_id)
                    if profile:
                        detailed_info = f"{state['name']}: {profile.background}"
                        if state.get("current_stage"):
                            detailed_info += f" | Current Arc: {state['current_stage']}"
                        if state.get("current_emotion"):
                            detailed_info += f" | Current Emotion: {state['current_emotion']}"
                        character_contexts.append(detailed_info)
            
            # Add generation directives for character continuity
            if len(character_contexts) > 0:
                char_directive = "Maintain character continuity:\n" + "\n".join(character_contexts)
                
                if req_dict.get("generation_directives"):
                    req_dict["generation_directives"] += "\n\n" + char_directive
                else:
                    req_dict["generation_directives"] = char_directive
        
        # Add plot continuity if available
        if self.memory_integration_level >= 2:
            plot_directives = []
            
            # Add unresolved plots
            if memory_context.get("unresolved_plots") and len(memory_context["unresolved_plots"]) > 0:
                plot_directives.append("Unresolved plot points to address:")
                for i, plot in enumerate(memory_context["unresolved_plots"][:3]):  # Top 3 plots
                    plot_directives.append(f"- {plot['description'] if isinstance(plot, dict) else str(plot)}")
            
            # Add pending foreshadowing
            if memory_context.get("pending_foreshadowing") and len(memory_context["pending_foreshadowing"]) > 0:
                plot_directives.append("\nForeshadowing elements to pay off:")
                for i, foreshadow in enumerate(memory_context["pending_foreshadowing"][:2]):  # Top 2 foreshadowings
                    if isinstance(foreshadow, dict):
                        plot_directives.append(f"- {foreshadow.get('foreshadowing', '')} → {foreshadow.get('payoff', '')}")
                    else:
                        plot_directives.append(f"- {str(foreshadow)}")
            
            # Add thematic status
            if memory_context.get("thematic_status") and len(memory_context["thematic_status"]) > 0:
                plot_directives.append("\nThematic elements to develop:")
                for theme, development in memory_context["thematic_status"].items():
                    plot_directives.append(f"- {theme}: {development}")
            
            if len(plot_directives) > 0:
                plot_directive = "\n".join(plot_directives)
                
                if req_dict.get("generation_directives"):
                    req_dict["generation_directives"] += "\n\n" + plot_directive
                else:
                    req_dict["generation_directives"] = plot_directive
        
        # Update special fields that aren't direct dictionary keys
        if self.memory_integration_level == 3 and not req_dict.get("emotional_arc") and memory_context.get("character_states"):
            # Generate an emotional arc based on character states
            chars = list(memory_context["character_states"].values())
            if len(chars) > 0:
                emotions = [c.get("current_emotion", "") for c in chars if c.get("current_emotion")]
                if emotions:
                    from_emotion = " & ".join(emotions[:2])
                    # Simple emotional progression
                    progressions = {
                        "fear": "courage",
                        "anger": "resolution",
                        "joy": "confidence",
                        "sadness": "acceptance",
                        "confusion": "clarity",
                        "hope": "determination",
                        "despair": "hope"
                    }
                    to_emotion = next((progressions[e] for e in emotions[:1] if e in progressions), "determination")
                    req_dict["emotional_arc"] = f"From {from_emotion} to {to_emotion}"
        
        # Return enhanced requirements
        return SceneRequirements(**req_dict)
    
    def _get_all_previous_scenes(self, current_act: int, current_scene: int) -> List[str]:
        """Get all previously generated scenes for uniqueness validation."""
        previous_scenes = []
        
        # Get scenes from run manager if available
        if hasattr(self, 'run_manager') and self.run_manager and hasattr(self, 'run_id'):
            try:
                for act in range(1, current_act + 1):
                    max_scene = 5 if act < current_act else current_scene - 1
                    for scene in range(1, max_scene + 1):
                        scene_data = self.run_manager.get_scene(self.run_id, act, scene)
                        if scene_data and 'scene' in scene_data:
                            previous_scenes.append(scene_data['scene'])
            except Exception as e:
                logger.warning(f"Could not retrieve previous scenes from run manager: {str(e)}")
        
        return previous_scenes
    
    def _build_uniqueness_constraint(self, previous_scenes: List[str], requirements: SceneRequirements) -> str:
        """Build uniqueness constraint for scene generation."""
        if not previous_scenes:
            return "This is the first scene of the play."
        
        # Extract key elements from previous scenes for comparison
        previous_summaries = []
        for i, scene in enumerate(previous_scenes[-3:]):  # Only check last 3 scenes to avoid overly long prompts
            # Extract first few lines for setting/dialogue comparison
            lines = scene.split('\n')[:5]
            summary = ' '.join(lines).strip()[:200]  # First 200 chars
            previous_summaries.append(f"Previous scene {len(previous_scenes) - 3 + i + 1}: {summary}...")
        
        constraint = "CRITICAL UNIQUENESS REQUIREMENT:\n"
        constraint += "This scene MUST be completely different from all previous scenes.\n"
        constraint += "DO NOT repeat any of these previous scene patterns:\n"
        constraint += "\n".join(previous_summaries)
        constraint += f"\n\nThis is Act {requirements.act_number}, Scene {requirements.scene_number}. "
        constraint += "Generate a UNIQUE scene that advances the story in a NEW way."
        
        return constraint
    
    def _build_scene_specific_directive(self, requirements: SceneRequirements, scene_outline: str) -> str:
        """Build scene-specific directive based on context."""
        scene_key = f"act{requirements.act_number}_scene{requirements.scene_number}"
        
        # Scene-specific directives for dramatic progression
        directives = {
            "act1_scene1": "OPENING SCENE: Establish the world, introduce main characters, set the premise",
            "act1_scene2": "INCITING INCIDENT: Introduce the central conflict or challenge",
            "act1_scene3": "FIRST PLOT POINT: Deepen the conflict, reveal character motivations",
            "act1_scene4": "RISING ACTION: Escalate tensions, introduce complications",
            "act1_scene5": "ACT ONE CLIMAX: Major revelation or turning point that propels us into Act 2",
            "act2_scene1": "NEW CIRCUMSTANCES: Characters adapt to changed situation from Act 1",
            "act2_scene2": "MIDPOINT BUILD: Increasing pressure and stakes",
            "act2_scene3": "MIDPOINT: Major reversal, revelation, or point of no return",
            "act2_scene4": "CRISIS ESCALATION: Everything falls apart, lowest point",
            "act2_scene5": "SECOND PLOT POINT: Final push toward resolution, characters commit to final action",
            "act3_scene1": "FINAL BATTLE: Climactic confrontation begins",
            "act3_scene2": "CLIMAX: Peak of dramatic tension and conflict",
            "act3_scene3": "FALLING ACTION: Immediate consequences of climax",
            "act3_scene4": "RESOLUTION: Tying up loose ends, character arcs conclude",
            "act3_scene5": "DENOUEMENT: Final state, new equilibrium, thematic statement"
        }
        
        base_directive = directives.get(scene_key, f"Continue the story progression for {scene_key}")
        
        # Add generation type specific directive if available
        generation_type_directive = self._get_generation_type_directive()
        
        directive = f"SCENE DIRECTIVE: {base_directive}\nSCENE OUTLINE: {scene_outline}\n"
        if generation_type_directive:
            directive += f"\nGENERATION APPROACH: {generation_type_directive}\n"
        
        return directive
    
    def _get_generation_type_directive(self) -> str:
        """Get generation-type specific directive based on current context."""
        # This would be set by different generation methods
        if hasattr(self, '_current_generation_type'):
            generation_directives = {
                "basic": "Focus on clear, straightforward narrative progression with strong dialogue and action.",
                "collaborative": "Emphasize dynamic character interactions and layered dialogue that reveals multiple perspectives.",
                "character_focused": "Prioritize deep character development, internal monologue, and character-driven conflict.",
                "memory_enhanced": "Incorporate rich continuity details, character history callbacks, and plot thread connections.",
                "iterative_refinement": "Create sophisticated, nuanced scenes with complex subtext and artistic flourishes."
            }
            return generation_directives.get(self._current_generation_type, "")
        return ""
    
    def _validate_scene_uniqueness(self, new_scene: str, previous_scenes: List[str], similarity_threshold: float = 0.6) -> bool:
        """Validate that the new scene is unique compared to previous scenes."""
        if not previous_scenes:
            return True
        
        # Simple similarity check based on first few lines and dialogue patterns
        new_scene_start = new_scene.split('\n')[:10]  # First 10 lines
        new_scene_signature = ' '.join(new_scene_start).lower()
        
        for prev_scene in previous_scenes:
            prev_scene_start = prev_scene.split('\n')[:10]  # First 10 lines
            prev_scene_signature = ' '.join(prev_scene_start).lower()
            
            # Check for very similar openings
            if len(new_scene_signature) > 100 and len(prev_scene_signature) > 100:
                # Simple Jaccard similarity on words
                new_words = set(new_scene_signature.split())
                prev_words = set(prev_scene_signature.split())
                intersection = len(new_words.intersection(prev_words))
                union = len(new_words.union(prev_words))
                similarity = intersection / union if union > 0 else 0
                
                if similarity > similarity_threshold:
                    logger.warning(f"Scene similarity detected: {similarity:.2f} > {similarity_threshold}")
                    return False
        
        return True
    
    def _update_memory_from_scene(self, scene_id: str, scene_content: str) -> None:
        """Update memory based on generated scene content."""
        if not scene_content:
            return
            
        # Update character tracking
        if (PlaywrightCapability.CHARACTER_TRACKING in self.enabled_capabilities and 
            self.track_characters and self.character_tracker):
            try:
                character_analysis = self.character_tracker.analyze_scene_characters(
                    scene_id, 
                    scene_content,
                    lambda prompt: self.get_llm().invoke(prompt)
                )
                logger.info(f"Character analysis completed for scene {scene_id}: {len(character_analysis.character_references)} characters analyzed")
            except Exception as e:
                logger.error(f"Error in character analysis: {str(e)}")
        
        # Update narrative tracking
        if (PlaywrightCapability.MEMORY_ENHANCEMENT in self.enabled_capabilities and 
            self.track_narrative and self.enhanced_memory):
            try:
                self.enhanced_memory.update_narrative_from_scene(
                    scene_id,
                    scene_content,
                    lambda prompt: self.get_llm().invoke(prompt)
                )
                logger.info(f"Narrative analysis completed for scene {scene_id}")
            except Exception as e:
                logger.error("Error in narrative analysis: " + str(e))
    
    def _get_memory_context(self, act_number: int, scene_number: int) -> Dict[str, Any]:
        """Get memory context for scene generation."""
        if not PlaywrightCapability.MEMORY_ENHANCEMENT in self.enabled_capabilities or not self.enhanced_memory:
            return {}
            
        try:
            return self.enhanced_memory.get_scene_context(act_number, scene_number)
        except Exception as e:
            logger.error("Error getting memory context: " + str(e))
            return {}
    
    def collaborate_on_scene(
        self,
        other_playwright: 'Playwright',
        requirements: SceneRequirements,
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ) -> Dict[str, Any]:
        """
        Collaborate with another playwright on scene generation.
        
        Args:
            other_playwright: The other playwright to collaborate with
            requirements: Scene requirements
            progress_callback: Optional callback for reporting progress
            
        Returns:
            Dict containing the generated scene and metadata
        """
        if not PlaywrightCapability.COLLABORATIVE in self.enabled_capabilities:
            logger.warning("Collaborative capability not enabled, falling back to standard generation")
            return self.generate_scene(requirements, progress_callback=progress_callback)
            
        try:
            # Generate a shared scene ID for the collaboration
            scene_id = str(uuid.uuid4())
            logger.info(f"Starting collaboration between {self.name} and {other_playwright.name}")
            
            # First playwright generates opening scene
            if progress_callback:
                progress_callback({
                    "phase": "collaboration_initial",
                    "current_step": 1, 
                    "total_steps": 4,
                    "message": f"{self.name} generating initial scene"
                })
                
            opening_result = self.generate_scene(
                requirements,
                progress_callback=lambda data: progress_callback({**data, "phase": f"collaboration_initial_{data['phase']}"}) if progress_callback else None,
                use_refinement=False,  # Skip refinement for initial draft
                generation_type="collaborative"
            )
            
            # Second playwright enhances the scene
            if progress_callback:
                progress_callback({
                    "phase": "collaboration_enhancement",
                    "current_step": 2,
                    "total_steps": 4,
                    "message": f"{other_playwright.name} enhancing scene"
                })
                
            enhanced_result = other_playwright.generate_scene(
                requirements,
                previous_scene=opening_result["scene"],
                previous_feedback=opening_result["evaluation"],
                progress_callback=lambda data: progress_callback({**data, "phase": f"collaboration_enhancement_{data['phase']}"}) if progress_callback else None,
                use_refinement=False,  # Skip refinement for enhancement
                generation_type="collaborative"
            )
            
            # Collaboratively refine the scene
            if progress_callback:
                progress_callback({
                    "phase": "collaboration_synthesis",
                    "current_step": 3,
                    "total_steps": 4,
                    "message": "Synthesizing collaborative contributions"
                })
                
            synthesis_prompt = ENHANCED_PROMPT_TEMPLATES["collaborative_synthesis"].format(
                dialogue_content=opening_result["scene"],
                narrative_content=enhanced_result["scene"],
                technical_content="",  # Could be expanded with more collaborators
                emotional_content="",  # Could be expanded with more collaborators
                requirements=json.dumps(requirements.model_dump() if hasattr(requirements, 'model_dump') else requirements.dict())
            )
            
            synthesis_response = self.get_llm().invoke(synthesis_prompt)
            synthesized_scene = self._extract_synthesized_scene(synthesis_response)
            
            # Final refinement pass
            if progress_callback:
                progress_callback({
                    "phase": "collaboration_refinement",
                    "current_step": 4,
                    "total_steps": 4,
                    "message": "Performing final collaborative refinement"
                })
                
            if PlaywrightCapability.ITERATIVE_REFINEMENT in self.enabled_capabilities and self.refinement_system:
                refinement_result = self.refinement_system.refine_scene_iteratively(
                    synthesized_scene,
                    lambda prompt: self.get_llm().invoke(prompt),
                    {**(requirements.model_dump() if hasattr(requirements, 'model_dump') else requirements.dict()), "scene_id": scene_id},
                    lambda data: progress_callback({**data, "phase": f"collaboration_refinement_{data['phase']}"}) if progress_callback else None
                )
                final_scene = refinement_result["refined_scene"]
                final_evaluation = refinement_result["final_evaluation"]
            else:
                final_scene = synthesized_scene
                final_evaluation = self.quality_control.evaluate_scene(synthesized_scene, requirements)
                refinement_result = {
                    "iterations_performed": 0,
                    "overall_improvement": 0.0
                }
            
            # Clean up both checkpoints after successful completion
            if self.checkpoint_manager:
                self.checkpoint_manager.cleanup_checkpoint(f"{scene_id}_opening")
            if other_playwright.checkpoint_manager:
                other_playwright.checkpoint_manager.cleanup_checkpoint(f"{scene_id}_enhancement")
            
            # Add scene to previous scenes
            self.previous_scenes.append(final_scene)
            
            # Update memory if applicable
            if (PlaywrightCapability.MEMORY_ENHANCEMENT in self.enabled_capabilities or 
                PlaywrightCapability.CHARACTER_TRACKING in self.enabled_capabilities):
                self._update_memory_from_scene(scene_id, final_scene)
            
            return {
                "scene": final_scene,
                "evaluation": final_evaluation,
                "timing_metrics": {
                    "opening_generation": sum(opening_result["timing_metrics"].values()),
                    "scene_enhancement": sum(enhanced_result["timing_metrics"].values()),
                    "collaboration_refinement": refinement_result.get("iterations_performed", 0),
                    "total_time": sum(opening_result["timing_metrics"].values()) + 
                                sum(enhanced_result["timing_metrics"].values())
                },
                "dialogue_history": {
                    **opening_result.get("dialogue_history", {}),
                    **enhanced_result.get("dialogue_history", {})
                },
                "iterations": opening_result.get("iterations", 1) + enhanced_result.get("iterations", 1) + 
                            refinement_result.get("iterations_performed", 0),
                "iteration_metrics": opening_result.get("iteration_metrics", []) + 
                                    enhanced_result.get("iteration_metrics", []) +
                                    refinement_result.get("iteration_metrics", []),
                "scene_id": scene_id,
                "collaboration_data": {
                    "opening_playwright": self.name,
                    "enhancing_playwright": other_playwright.name,
                    "opening_scene": opening_result.get("scene", ""),
                    "enhanced_scene": enhanced_result.get("scene", ""),
                    "synthesized_scene": synthesized_scene
                }
            }
                
        except Exception as e:
            logger.error(f"Fatal error in collaborative scene generation: {str(e)}")
            raise
    
    def _extract_synthesized_scene(self, llm_response: Any) -> str:
        """Extract synthesized scene content from LLM response."""
        response_text = str(llm_response.content if hasattr(llm_response, "content") else llm_response)
        
        # Try to extract content between SYNTHESIZED SCENE: and SYNTHESIS ANALYSIS:
        synthesized_scene_marker = "SYNTHESIZED SCENE:"
        analysis_marker = "SYNTHESIS ANALYSIS:"
        
        if synthesized_scene_marker in response_text and analysis_marker in response_text:
            start_idx = response_text.find(synthesized_scene_marker) + len(synthesized_scene_marker)
            end_idx = response_text.find(analysis_marker)
            if start_idx < end_idx:
                return response_text[start_idx:end_idx].strip()
        
        # Fallback: return the whole response if markers not found
        return response_text
    
    def plan_act(self, act_number: int) -> Dict[str, Any]:
        """
        Plan an act with advisor input.
        
        Args:
            act_number: The act number to plan
            
        Returns:
            Dict containing the act plan and metadata
        """
        try:
            # Validate act number
            if not 1 <= act_number <= 5:
                raise ValueError(f"Act number must be between 1 and 5, got {act_number}")
                
            if not self.story_outline:
                raise ValueError("story_outline is not initialized")
                
            # Check dependencies with detailed validation
            dependencies = self.story_outline.get_act_dependencies(act_number)
            for dep in dependencies:
                dep_act = self.story_outline.get_act_outline(dep)
                if not dep_act:
                    raise ValueError(f"Required Act {dep} not found in story outline")
                if dep_act["status"] != "completed":
                    raise ValueError(f"Act {dep} must be completed before planning Act {act_number}")
                    
            if not self.advisor_manager:
                raise ValueError("advisor_manager is not initialized")
                
            if not self.act_processor:
                raise ValueError("act_processor is not initialized")
                
            # Get input from each advisor with improved error handling
            advisor_suggestions: Dict[str, Any] = {}
            advisor_errors: Dict[str, str] = {}
            
            for advisor_type, advisor in self.advisor_manager.advisors.items():
                retry_count = 0
                last_error = None
                
                while retry_count < self.act_processor.max_advisor_retries:
                    try:
                        # Format advisor prompt
                        advisor_prompt = PROMPT_TEMPLATES["act_planning_advisor"].format(
                            advisor_type=advisor_type,
                            act_number=act_number,
                            title=self.story_outline.title,
                            previous_acts=self.act_processor.get_previous_acts_summary(
                                [act for act in self.story_outline.acts if act['act_number'] < act_number]
                            ),
                            previous_scenes=self.act_processor.get_previous_scenes_summary(self.previous_scenes),
                            corrective_feedback=""
                        )
                        
                        if retry_count > 0:
                            # Re-format the prompt with corrective feedback
                            advisor_prompt = PROMPT_TEMPLATES["act_planning_advisor"].format(
                                advisor_type=advisor_type,
                                act_number=act_number,
                                title=self.story_outline.title,
                                previous_acts=self.act_processor.get_previous_acts_summary(
                                    [act for act in self.story_outline.acts if act['act_number'] < act_number]
                                ),
                                previous_scenes=self.act_processor.get_previous_scenes_summary(self.previous_scenes),
                                corrective_feedback=f"PREVIOUS ATTEMPT FAILED: {last_error}\n\nPlease ensure your response includes all required sections and follows the format exactly. Remember to write the section headers in ALL CAPS and separate sections with blank lines."
                            )
                            
                        response = self.get_llm().invoke(advisor_prompt)
                        suggestion = str(response.content)
                        
                        # Process and validate the suggestion
                        processed_suggestion = self.act_processor.process_advisor_suggestion(suggestion)
                        advisor_suggestions[advisor_type] = processed_suggestion
                        
                        # Add to planning discussions
                        self.story_outline.add_planning_discussion(
                            participant=f"{advisor_type}_advisor",
                            suggestion=suggestion,
                            reasoning=f"Based on {advisor_type} considerations"
                        )
                        
                        break
                        
                    except Exception as e:
                        last_error = str(e)
                        retry_count += 1
                        logger.warning(f"Attempt {retry_count} failed for {advisor_type} advisor: {str(e)}")
                        
                        if retry_count >= self.act_processor.max_advisor_retries:
                            logger.error(f"Error getting suggestion from {advisor_type} advisor: {str(e)}")
                            advisor_errors[advisor_type] = str(e)
                            break
                            
                        time.sleep(1)  # Add delay between retries
                        
            if not advisor_suggestions:
                raise ValueError("No valid suggestions from any advisor")
                
            # Synthesize suggestions with improved validation
            synthesis_retry_count = 0
            last_synthesis_error = None
            
            while synthesis_retry_count < self.act_processor.max_synthesis_retries:
                try:
                    # Format synthesis prompt
                    synthesis_prompt = PROMPT_TEMPLATES["act_planning_synthesis"].format(
                        act_number=act_number,
                        advisor_suggestions=json.dumps(advisor_suggestions, indent=2),
                        previous_acts=self.act_processor.get_previous_acts_summary(
                            [act for act in self.story_outline.acts if act['act_number'] < act_number]
                        ),
                        previous_scenes=self.act_processor.get_previous_scenes_summary(self.previous_scenes)
                    )
                    
                    if synthesis_retry_count > 0:
                        synthesis_prompt += f"\n\nCORRECTIVE FEEDBACK FROM PREVIOUS ATTEMPT:\n{last_synthesis_error}\n\nPlease ensure your response includes all required sections and follows the format exactly. Remember to write the section headers in ALL CAPS and separate sections with blank lines."
                        
                    act_outline = self.get_llm().invoke(synthesis_prompt)
                    outline_str = str(act_outline.content)
                    
                    # Process and validate the outline
                    processed_outline = self.act_processor.process_synthesis(outline_str)
                    
                    # Commit the act
                    self.story_outline.commit_act(
                        act_number=act_number,
                        description=processed_outline["description"],
                        key_events=processed_outline["key_events"]
                    )
                    
                    return {
                        "act_number": act_number,
                        "planning_discussions": self.story_outline.planning_discussions,
                        "committed_outline": self.story_outline.get_act_outline(act_number),
                        "character_development": processed_outline["character_development"],
                        "thematic_elements": processed_outline["thematic_elements"],
                        "advisor_suggestions": advisor_suggestions,
                        "advisor_errors": advisor_errors
                    }
                    
                except Exception as e:
                    last_synthesis_error = str(e)
                    synthesis_retry_count += 1
                    logger.warning(f"Synthesis attempt {synthesis_retry_count} failed: {str(e)}")
                    
                    if synthesis_retry_count >= self.act_processor.max_synthesis_retries:
                        logger.error(f"Error in act synthesis: {str(e)}")
                        raise ValueError(f"Failed to synthesize act outline: {str(e)}")
                        
                    time.sleep(1)  # Add delay between retries
                    
        except Exception as e:
            logger.error(f"Error in act planning: {str(e)}")
            raise
    
    def create_story_outline(self, theme: str, requirements: Dict[str, Any]) -> StoryOutline:
        """
        Create a story outline with enhanced character and plot development.
        
        Args:
            theme: The central theme of the story
            requirements: Additional requirements for the story
            
        Returns:
            StoryOutline: The generated story outline
        """
        prompt = f"""Create a detailed story outline for a theatrical production with the following requirements:
        Theme: {theme}
        Setting: {requirements.get('setting', 'Modern day')}
        Style: {requirements.get('style', 'Drama')}
        Period: {requirements.get('period', 'Present')}
        Target Audience: {requirements.get('target_audience', 'General')}

        The outline should include:
        1. A clear three-act structure
        2. Five scenes per act
        3. Detailed character descriptions and arcs
        4. Major plot points and their development
        5. Thematic elements
        6. Technical requirements

        Format the response as:
        TITLE: [Title]
        ACTS:
        Act 1: [Description]
        - Key Event 1
        - Key Event 2
        - Key Event 3
        - Key Event 4
        - Key Event 5

        Act 2: [Description]
        - Key Event 1
        - Key Event 2
        - Key Event 3
        - Key Event 4
        - Key Event 5

        Act 3: [Description]
        - Key Event 1
        - Key Event 2
        - Key Event 3
        - Key Event 4
        - Key Event 5

        CHARACTERS:
        [Character Name]: [Description]
        [Character Name]: [Description]
        ...

        THEMES:
        - [Theme 1]
        - [Theme 2]
        ...

        TECHNICAL NOTES:
        - [Note 1]
        - [Note 2]
        ...
        """

        response = self.get_llm().invoke(prompt)
        outline = StoryOutline.from_text(str(response.content))
        self.story_outline = outline
        
        return outline
    
    # MEMORY-ENHANCED METHODS
    
    def get_character_summary(self, char_id: str) -> Dict[str, Any]:
        """Get a summary of a character's development."""
        if not PlaywrightCapability.CHARACTER_TRACKING in self.enabled_capabilities or not self.character_tracker:
            return {"error": "Character tracker not initialized"}
            
        return self.character_tracker.get_character_summary(char_id)
    
    def get_all_characters(self) -> List[Dict[str, Any]]:
        """Get summaries of all characters."""
        if not PlaywrightCapability.CHARACTER_TRACKING in self.enabled_capabilities or not self.character_tracker:
            return []
            
        char_ids = self.character_tracker.get_all_character_ids()
        return [self.get_character_summary(char_id) for char_id in char_ids]
    
    def get_scene_character_summary(self, scene_id: str) -> Dict[str, Any]:
        """Get a summary of characters in a specific scene."""
        if not PlaywrightCapability.CHARACTER_TRACKING in self.enabled_capabilities or not self.character_tracker:
            return {"error": "Character tracker not initialized"}
            
        return self.character_tracker.get_scene_character_summary(scene_id)
    
    def create_scene_with_character_focus(
        self,
        requirements: SceneRequirements,
        focus_character: str,
        character_development: Dict[str, Any],
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ) -> Dict[str, Any]:
        """
        Create a scene focused on developing a specific character.
        
        Args:
            requirements: Base scene requirements
            focus_character: ID of the character to focus on
            character_development: Development specifications for the character
            progress_callback: Optional callback for reporting progress
            
        Returns:
            Dict containing the generated scene and metadata
        """
        if not PlaywrightCapability.CHARACTER_TRACKING in self.enabled_capabilities or not self.enhanced_memory:
            return self.generate_scene(requirements, progress_callback=progress_callback)
            
        # Get character profile
        profile = self.enhanced_memory.get_character_profile(focus_character)
        if not profile:
            raise ValueError(f"Character profile not found for {focus_character}")
        
        # Update requirements with character focus
        char_name = profile.name.upper()  # Convert to uppercase for character name in script
        
        # Ensure the character is in the scene
        req_dict = requirements.model_dump() if hasattr(requirements, 'model_dump') else requirements.dict()
        if char_name not in req_dict["characters"]:
            req_dict["characters"].append(char_name)
        
        # Add character development directives
        dev_directives = f"""CHARACTER DEVELOPMENT FOCUS:
        Character: {profile.name}
        Background: {profile.background}
        Current Arc Stage: {getattr(profile, 'development_arc', [])[-1].stage if getattr(profile, 'development_arc', []) and isinstance(getattr(profile, 'development_arc', []), list) else "Not started"}
        Current Arc Description: {getattr(profile, 'development_arc', [])[-1].description if getattr(profile, 'development_arc', []) and isinstance(getattr(profile, 'development_arc', []), list) else "No development yet"}
        Current Emotional State: {profile.get_current_emotional_state().emotion if profile.get_current_emotional_state() else "Unknown"}
        
        Development Goals:
        - Show {profile.name}'s {character_development.get("aspect", "character")} development
        - Create a moment of {character_development.get("moment_type", "revelation")} for {profile.name}
        - Develop {profile.name}'s relationship with {character_development.get("relationship_with", req_dict["characters"][0] if len(req_dict["characters"]) > 0 and req_dict["characters"][0] != char_name else req_dict["characters"][1] if len(req_dict["characters"]) > 1 else "another character")}
        - Reveal more about {profile.name}'s {character_development.get("reveal_aspect", "motivation")}
        - Create {character_development.get("conflict_type", "internal conflict")} for {profile.name}
        """
        
        if req_dict.get("generation_directives"):
            req_dict["generation_directives"] += "\n\n" + dev_directives
        else:
            req_dict["generation_directives"] = dev_directives
        
        # Update emotional arc if provided
        if character_development.get("emotional_journey"):
            req_dict["emotional_arc"] = character_development["emotional_journey"]
        
        # Generate scene with character focus
        enhanced_requirements = SceneRequirements(**req_dict)
        result = self.generate_scene(enhanced_requirements, progress_callback=progress_callback, generation_type="character_focused")
        
        # Add character focus information to result
        result["character_focus"] = {
            "character_id": focus_character,
            "character_name": profile.name,
            "development_goals": character_development
        }
        
        return result


# Factory function to create playwrights with specific capabilities
def create_playwright(
    name: str,
    llm_manager: LLMManager,
    memory: TheatricalMemory,
    capabilities: List[PlaywrightCapability] = [PlaywrightCapability.BASIC],
    **kwargs
) -> Playwright:
    """
    Create a playwright with specific capabilities.
    
    Args:
        name: Name of the playwright
        llm_manager: LLM manager for language model interactions
        memory: Theatrical memory system
        capabilities: List of playwright capabilities to enable
        **kwargs: Additional parameters for the playwright
        
    Returns:
        Playwright: A configured playwright instance
    """
    # Ensure consistent memory type if memory enhancement is requested
    if PlaywrightCapability.MEMORY_ENHANCEMENT in capabilities and not isinstance(memory, EnhancedTheatricalMemory):
        memory = EnhancedTheatricalMemory(
            character_profiles=getattr(memory, "character_profiles", {}),
            db_path=getattr(memory, "db_path", None)
        )
    
    # Create advisor manager if needed
    if "advisor_manager" not in kwargs and any(cap in capabilities for cap in [PlaywrightCapability.BASIC, PlaywrightCapability.COLLABORATIVE]):
        kwargs["advisor_manager"] = AdvisorManager(llm_manager=llm_manager, memory=memory)
    
    # Create playwright with specified capabilities
    return Playwright(
        name=name,
        llm_manager=llm_manager,
        memory=memory,
        enabled_capabilities=capabilities,
        **kwargs
    )