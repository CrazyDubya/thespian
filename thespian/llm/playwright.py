"""
Enhanced playwright module for generating full theatrical productions.
"""

from typing import Dict, Any, List, Optional, Callable, Union, TypeVar, cast
from pydantic import BaseModel, Field, ConfigDict
from thespian.llm import LLMManager
from thespian.llm.theatrical_memory import TheatricalMemory, CharacterProfile, StoryOutline
from thespian.llm.theatrical_advisors import TheatricalAdvisor, AdvisorFeedback, AdvisorManager
from thespian.llm.quality_control import TheatricalQualityControl
from thespian.llm.dialogue_system import DialogueSystem
from thespian.llm.manager import LLMResponseEncoder
from thespian.config.prompts import PROMPT_TEMPLATES
from thespian.processors.scene_processor import SceneProcessor
from thespian.processors.act_processor import ActProcessor
from thespian.checkpoints.checkpoint_manager import CheckpointManager
import time
import uuid
import logging
from datetime import datetime, timedelta
import os
import json
from pathlib import Path

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


class EnhancedPlaywright(BaseModel):
    """Enhanced playwright for generating full theatrical productions."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    name: str = Field(..., description="Name of the playwright")
    llm_manager: LLMManager
    memory: TheatricalMemory
    advisor_manager: AdvisorManager
    quality_control: TheatricalQualityControl
    dialogue_system: Optional[DialogueSystem] = None
    model_type: str = "ollama"
    max_iterations: int = Field(default=5, ge=1, le=10)
    quality_threshold: float = Field(default=0.8, ge=0.0, le=1.0)
    character_arcs: Dict[str, List[str]] = Field(default_factory=dict)
    plot_points: List[str] = Field(default_factory=list)
    previous_scenes: List[str] = Field(default_factory=list)
    story_outline: Optional[StoryOutline] = None
    scene_processor: Optional[SceneProcessor] = None
    act_processor: Optional[ActProcessor] = None
    checkpoint_manager: Optional[CheckpointManager] = None
    
    def __init__(self, **data: Any) -> None:
        """Initialize the enhanced playwright."""
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
    
    def get_llm(self) -> Any:
        """Get the LLM instance."""
        return self.llm_manager.get_llm(self.model_type)
    
    def _construct_scene_prompt(
        self,
        requirements: SceneRequirements,
        previous_scene: Optional[str] = None,
        previous_feedback: Optional[Dict[str, Any]] = None
    ) -> str:
        """Construct the prompt for scene generation."""
        if not self.story_outline:
            raise ValueError("story_outline is not initialized")
            
        current_act = self.story_outline.get_act_outline(requirements.act_number)
        if not current_act:
            raise ValueError(f"No outline found for Act {requirements.act_number}")
            
        current_scene_outline = current_act["key_events"][requirements.scene_number - 1]
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
                
        previous_feedback_content = "No previous feedback"
        if previous_feedback:
            if isinstance(previous_feedback, dict):
                previous_feedback_content = json.dumps(previous_feedback)
            elif isinstance(previous_feedback, str):
                previous_feedback_content = previous_feedback
            else:
                logger.warning(f"Unexpected previous feedback format: {type(previous_feedback)}")
                
        if not self.scene_processor:
            raise ValueError("scene_processor is not initialized")
            
        return PROMPT_TEMPLATES["scene_generation"].format(
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
            min_length=self.scene_processor.min_length,
            max_length=self.scene_processor.max_length
        )
    
    def generate_scene(
        self, 
        requirements: SceneRequirements, 
        previous_scene: Optional[str] = None,
        previous_feedback: Optional[Dict[str, Any]] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> Dict[str, Any]:
        """Generate a scene based on requirements."""
        retry_count = 0
        scene_id = str(uuid.uuid4())
        while retry_count < self.max_iterations:
            try:
                prompt = self._construct_scene_prompt(requirements, previous_scene, previous_feedback)
                response = self.get_llm().invoke(prompt)
                scene_content = str(response.content)
                if not self.scene_processor:
                    raise ValueError("scene_processor is not initialized")
                processed_content = self.scene_processor.process_scene_content(scene_content)
                if not self.quality_control:
                    raise ValueError("quality_control is not initialized")
                evaluation = self.quality_control.evaluate_scene(processed_content["scene"], requirements)
                if evaluation["quality_score"] >= self.quality_threshold:
                    self.previous_scenes.append(scene_content)
                    if not self.checkpoint_manager:
                        raise ValueError("checkpoint_manager is not initialized")
                    self.checkpoint_manager.cleanup_checkpoint(scene_id)
                    logger.info(f"Completed scene generation for Act {requirements.act_number}, Scene {requirements.scene_number}")
                    return {
                        "scene": scene_content,
                        "narrative_analysis": processed_content["narrative_analysis"],
                        "evaluation": evaluation,
                        "timing_metrics": self._get_timing_metrics(),
                        "iterations": retry_count + 1,
                        "iteration_metrics": [],
                        "scene_id": scene_id,
                        "raw_content": processed_content["raw_content"]
                    }
                improved_content = self._improve_scene(processed_content["scene"], evaluation)
                if improved_content:
                    improved_evaluation = self.quality_control.evaluate_scene(improved_content, requirements)
                    improved_scores = improved_evaluation.get("quality_scores")
                    if improved_scores and isinstance(improved_scores, dict) and len(improved_scores) > 0:
                        improved_avg = sum(improved_scores.values()) / len(improved_scores)
                    else:
                        improved_avg = 0.0
                    if improved_avg > evaluation.get("quality_score", 0.0):
                        scene_content = improved_content
                        evaluation = improved_evaluation
                        logger.info(f"Scene improved (quality: {improved_avg:.2f})")
                    else:
                        logger.warning(f"Improvement attempt failed (quality: {improved_avg:.2f})")
                self.previous_scenes.append(scene_content)
                if not self.checkpoint_manager:
                    raise ValueError("checkpoint_manager is not initialized")
                self.checkpoint_manager.cleanup_checkpoint(scene_id)
                logger.info(f"Completed scene generation for Act {requirements.act_number}, Scene {requirements.scene_number}")
                return {
                    "scene": scene_content,
                    "narrative_analysis": processed_content["narrative_analysis"],
                    "evaluation": evaluation,
                    "timing_metrics": self._get_timing_metrics(),
                    "iterations": retry_count + 1,
                    "iteration_metrics": [],
                    "scene_id": scene_id,
                    "raw_content": processed_content["raw_content"]
                }
            except Exception as e:
                retry_count += 1
                if retry_count == self.max_iterations:
                    logger.error(f"Failed to generate scene after {self.max_iterations} attempts: {str(e)}")
                    raise
                logger.warning(f"Retry {retry_count}/{self.max_iterations} for scene generation")
                time.sleep(1)
                continue
        raise RuntimeError(f"Failed to generate scene after {self.max_iterations} attempts")
    
    def _get_timing_metrics(self) -> Dict[str, float]:
        """Get timing metrics for the current generation."""
        try:
            metrics = {
                "start_time": time.time(),
                "end_time": time.time(),
                "total_time": 0.0
            }
            # Validate metrics
            if not all(isinstance(v, (int, float)) for v in metrics.values()):
                raise ValueError("Invalid timing metrics")
            # Calculate total time
            metrics["total_time"] = metrics["end_time"] - metrics["start_time"]
            # Validate total time
            if metrics["total_time"] < 0:
                raise ValueError("Invalid total time")
            return metrics
        except Exception as e:
            logger.error(f"Error getting timing metrics: {str(e)}")
            return {
                "start_time": time.time(),
                "end_time": time.time(),
                "total_time": 0.0
            }
    
    def _improve_scene(self, scene: str, evaluation: Dict[str, Any]) -> Optional[str]:
        """Improve a scene based on evaluation feedback."""
        if not scene or not evaluation:
            return None
        try:
            if not self.advisor_manager:
                return None
            improvement_prompt = PROMPT_TEMPLATES["scene_improvement"].format(
                scene=scene,
                evaluation=json.dumps(evaluation, indent=2)
            )
            response = self.get_llm().invoke(improvement_prompt)
            improved_scene = str(response.content)
            if not improved_scene or improved_scene == scene:
                return None
            return improved_scene
        except Exception as e:
            logger.error(f"Error improving scene: {str(e)}")
            return None

    def update_character_profile(self, char_id: str, profile: CharacterProfile) -> None:
        """Update a character's profile in the memory system."""
        self.memory.update_character_profile(char_id, profile)
        logger.info(f"Updated character profile for {char_id}")

    def collaborate_on_scene(
        self,
        other_playwright: 'EnhancedPlaywright',
        requirements: SceneRequirements,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> Dict[str, Any]:
        """Collaborate with another playwright on scene generation."""
        try:
            # Generate a shared scene ID for the collaboration
            scene_id = str(uuid.uuid4())
            logger.info(f"Starting collaboration between {self.name} and {other_playwright.name}")
            logger.info(f"Using shared scene ID for collaboration: {scene_id}")

            # First playwright generates opening scene
            opening_scene_id = f"{scene_id}_opening"
            opening_result = self.generate_scene(
                requirements,
                progress_callback=lambda current, total: progress_callback(current, total) if progress_callback else None
            )

            # Second playwright enhances the scene
            enhancement_scene_id = f"{scene_id}_enhancement"
            enhanced_result = other_playwright.generate_scene(
                requirements,
                previous_scene=opening_result["scene"],
                previous_feedback=opening_result["evaluation"],
                progress_callback=lambda current, total: progress_callback(current + 2, total) if progress_callback else None
            )

            # Calculate total times
            opening_total_time = sum(opening_result["timing_metrics"].values())
            enhancement_total_time = sum(enhanced_result["timing_metrics"].values())

            # Clean up both checkpoints after successful completion
            if self.checkpoint_manager:
                self.checkpoint_manager.cleanup_checkpoint(opening_scene_id)
            if other_playwright.checkpoint_manager:
                other_playwright.checkpoint_manager.cleanup_checkpoint(enhancement_scene_id)

            return {
                "scene": enhanced_result["scene"],
                "evaluation": enhanced_result["evaluation"],
                "timing_metrics": {
                    "opening_generation": opening_total_time,
                    "scene_enhancement": enhancement_total_time,
                    "total_time": opening_total_time + enhancement_total_time
                },
                "dialogue_history": {
                    **opening_result.get("dialogue_history", {}),
                    **enhanced_result.get("dialogue_history", {})
                },
                "iterations": opening_result["iterations"] + enhanced_result["iterations"],
                "iteration_metrics": opening_result["iteration_metrics"] + enhanced_result["iteration_metrics"],
                "scene_id": scene_id
            }
            
        except Exception as e:
            logger.error(f"Fatal error in scene generation: {str(e)}")
            # Try to save final checkpoints for both phases
            try:
                if 'opening_result' in locals() and self.checkpoint_manager:
                    self.checkpoint_manager.save_checkpoint(opening_scene_id, CheckpointData(
                        scene_id=opening_scene_id,
                        current_scene=opening_result["scene"],
                        iteration=opening_result["iterations"],
                        feedback=opening_result["evaluation"],
                        timing_metrics=opening_result["timing_metrics"],
                        iteration_metrics=opening_result["iteration_metrics"],
                        requirements=requirements.model_dump() if hasattr(requirements, 'model_dump') else requirements.dict()
                    ))
                if 'enhanced_result' in locals() and other_playwright.checkpoint_manager:
                    other_playwright.checkpoint_manager.save_checkpoint(enhancement_scene_id, CheckpointData(
                        scene_id=enhancement_scene_id,
                        current_scene=enhanced_result["scene"],
                        iteration=enhanced_result["iterations"],
                        feedback=enhanced_result["evaluation"],
                        timing_metrics=enhanced_result["timing_metrics"],
                        iteration_metrics=enhanced_result["iteration_metrics"],
                        requirements=requirements.model_dump() if hasattr(requirements, 'model_dump') else requirements.dict()
                    ))
            except Exception as checkpoint_error:
                logger.error(f"Failed to save final checkpoints: {str(checkpoint_error)}")
            raise
    
    def plan_act(self, act_number: int) -> Dict[str, Any]:
        """Plan an act with advisor input."""
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
                            previous_scenes=self.act_processor.get_previous_scenes_summary(self.previous_scenes)
                        )
                        
                        if retry_count > 0:
                            advisor_prompt += f"\n\nCORRECTIVE FEEDBACK FROM PREVIOUS ATTEMPT:\n{last_error}\n\nPlease ensure your response includes all required sections and follows the format exactly. Remember to write the section headers in ALL CAPS and separate sections with blank lines."
                            
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
        """Create a story outline with enhanced character and plot development."""
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

        response = self.llm_manager.generate(prompt)
        outline = StoryOutline.from_text(response)
        
        # Store character information for continuity
        self.current_characters = outline.characters
        self.current_plot_points = outline.plot_points
        self.current_technical_requirements = outline.technical_requirements
        
        return outline

    def _generate_act(self, act_number: int, requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate an act with enhanced scene development and continuity."""
        scenes = []
        for scene_number in range(1, 6):
            # Create scene requirements with character and plot continuity
            scene_requirements = {
                **requirements,
                'act_number': act_number,
                'scene_number': scene_number,
                'characters': self.current_characters,
                'previous_scenes': scenes,
                'plot_points': self.current_plot_points,
                'technical_requirements': self.current_technical_requirements
            }
            
            # Generate scene with quality control
            scene = self._generate_scene(scene_requirements)
            passed, feedback = self.quality_control.check_scene_quality(scene)
            
            # Regenerate scene if it doesn't meet quality standards
            attempts = 0
            while not passed and attempts < 3:
                scene = self._generate_scene(scene_requirements, feedback)
                passed, feedback = self.quality_control.check_scene_quality(scene)
                attempts += 1
            
            if not passed:
                raise ValueError(f"Failed to generate quality scene after {attempts} attempts: {feedback}")
            
            scenes.append({
                'scene_number': scene_number,
                'scene': scene
            })
        
        return scenes

    def _generate_scene(self, requirements: Dict[str, Any], feedback: Optional[str] = None) -> str:
        """Generate a scene with enhanced character development and technical details."""
        prompt = f"""Generate a theatrical scene with the following requirements:
        Act: {requirements['act_number']}
        Scene: {requirements['scene_number']}
        Setting: {requirements.get('setting', 'Modern day')}
        Style: {requirements.get('style', 'Drama')}
        Period: {requirements.get('period', 'Present')}

        Characters:
        {self._format_characters(requirements['characters'])}

        Previous Scenes:
        {self._format_previous_scenes(requirements['previous_scenes'])}

        Plot Points:
        {self._format_plot_points(requirements['plot_points'])}

        Technical Requirements:
        {self._format_technical_requirements(requirements['technical_requirements'])}

        {f'Feedback from previous attempt: {feedback}' if feedback else ''}

        Generate a complete scene with:
        1. Clear scene header
        2. Detailed stage directions
        3. Character dialogue with emotional depth
        4. Technical notes for lighting, sound, and props
        5. Proper scene transitions
        6. Minimum 20 lines of content
        7. Character consistency
        8. Plot continuity

        Format the scene as:
        SCENE [NUMBER]: [TITLE]

        (Stage directions and character movements)

        CHARACTER: (Emotional state) Dialogue

        [Technical Notes]

        END OF SCENE
        """

        return self.llm_manager.generate(prompt)

    def _format_characters(self, characters: Dict[str, Dict[str, Any]]) -> str:
        """Format character information for the prompt."""
        return "\n".join(f"{name}: {data.get('description', '')}" for name, data in characters.items())

    def _format_previous_scenes(self, scenes: List[Dict[str, Any]]) -> str:
        """Format previous scenes for continuity."""
        if not scenes:
            return "No previous scenes"
        return "\n".join(f"Scene {s['scene_number']}: {s['scene'][:100]}..." for s in scenes)

    def _format_plot_points(self, plot_points: List[str]) -> str:
        """Format plot points for the prompt."""
        return "\n".join(f"- {point}" for point in plot_points)

    def _format_technical_requirements(self, requirements: Dict[str, Any]) -> str:
        """Format technical requirements for the prompt."""
        return "\n".join(f"- {key}: {value}" for key, value in requirements.items())

    def generate_full_production(
        self,
        theme: str,
        requirements: Dict[str, Any],
        run_manager: Any,
        run_id: str
    ) -> Any:
        """Generate a complete theatrical production."""
        try:
            # Generate acts sequentially
            all_scenes = []
            for act_number in range(1, 4):
                logger.info(f"Generating Act {act_number}")
                
                # Create act-specific requirements
                act_requirements = SceneRequirements(
                    **requirements,
                    act_number=act_number,
                    scene_number=1
                )
                
                # Generate act
                act_scenes = self._generate_act(
                    act_number=act_number,
                    requirements=act_requirements,
                    run_manager=run_manager,
                    run_id=run_id
                )
                all_scenes.extend(act_scenes)
            
            # Create production from generated content
            production = self._create_production(
                theme=theme,
                scenes=all_scenes,
                requirements=requirements
            )
            
            return production
            
        except Exception as e:
            logger.error(f"Error generating production: {str(e)}")
            raise
    
    def _create_production(
        self,
        theme: str,
        scenes: List[Dict[str, Any]],
        requirements: Dict[str, Any]
    ) -> Any:
        """Create a production object from generated content."""
        from ..production import Production
        
        production = Production(theme=theme)
        
        # Organize scenes by act
        acts = {}
        for scene in scenes:
            act_num = scene["act_number"]
            if act_num not in acts:
                acts[act_num] = []
            acts[act_num].append(scene)
        
        # Create script with acts and scenes
        script = {
            "title": self.story_outline.title,
            "acts": acts,
            "requirements": requirements
        }
        
        production.update_script(script)
        return production 