"""
Enhanced playwright module with iterative refinement for theatrical productions.
"""

from typing import Dict, Any, List, Optional, Callable, Union, TypeVar, cast
from pydantic import BaseModel, Field, ConfigDict
import logging
import time
import json
from datetime import datetime
import os
from pathlib import Path

from thespian.llm import LLMManager
from thespian.llm.playwright import EnhancedPlaywright as BasePlaywright, SceneRequirements
from thespian.llm.theatrical_memory import TheatricalMemory, CharacterProfile
from thespian.llm.theatrical_advisors import AdvisorManager
from thespian.llm.quality_control import TheatricalQualityControl
from thespian.llm.iterative_refinement import IterativeRefinementSystem
from thespian.config.enhanced_prompts import ENHANCED_PROMPT_TEMPLATES

logger = logging.getLogger(__name__)

class EnhancedPlaywright(BasePlaywright):
    """Enhanced playwright with iterative refinement capabilities."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    refinement_system: Optional[IterativeRefinementSystem] = None
    use_enhanced_prompts: bool = Field(default=True)
    refinement_max_iterations: int = Field(default=5)
    refinement_quality_threshold: float = Field(default=0.85)
    refinement_improvement_threshold: float = Field(default=0.02)
    target_scene_length: int = Field(default=5000)
    
    def __init__(self, **data: Any) -> None:
        """Initialize the enhanced playwright."""
        super().__init__(**data)
        
        # Initialize refinement system if not provided
        if not self.refinement_system and self.quality_control:
            self.refinement_system = IterativeRefinementSystem(
                quality_control=self.quality_control,
                max_iterations=self.refinement_max_iterations,
                quality_threshold=self.refinement_quality_threshold,
                improvement_threshold=self.refinement_improvement_threshold
            )
    
    def _construct_scene_prompt(
        self, 
        requirements: SceneRequirements,
        previous_scene: Optional[str] = None,
        previous_feedback: Optional[Dict[str, Any]] = None
    ) -> str:
        """Construct the prompt for scene generation using enhanced prompts if enabled."""
        if self.use_enhanced_prompts:
            return self._construct_enhanced_scene_prompt(requirements, previous_scene, previous_feedback)
        else:
            return super()._construct_scene_prompt(requirements, previous_scene, previous_feedback)
    
    def _construct_enhanced_scene_prompt(
        self,
        requirements: SceneRequirements,
        previous_scene: Optional[str] = None,
        previous_feedback: Optional[Dict[str, Any]] = None
    ) -> str:
        """Construct an enhanced prompt for scene generation."""
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
            
        return ENHANCED_PROMPT_TEMPLATES["enhanced_scene_generation"].format(
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
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
        use_refinement: bool = True
    ) -> Dict[str, Any]:
        """
        Generate a scene with iterative refinement.
        
        Args:
            requirements: Scene requirements
            previous_scene: Optional previous scene content
            previous_feedback: Optional feedback from previous generation
            progress_callback: Optional callback for reporting progress
            use_refinement: Whether to use iterative refinement
            
        Returns:
            Dict containing the generated scene and metadata
        """
        # Create a unique scene ID
        import uuid
        scene_id = str(uuid.uuid4())
        
        # Start timing
        start_time = time.time()
        
        # Report initial progress
        if progress_callback:
            progress_callback({
                "phase": "initial_generation",
                "current_step": 1,
                "total_steps": 3 if use_refinement else 1,
                "message": "Generating initial scene draft"
            })
        
        try:
            # Generate initial scene
            initial_scene_result = self._generate_initial_scene(
                requirements, previous_scene, previous_feedback
            )
            initial_scene = initial_scene_result["scene"]
            initial_evaluation = initial_scene_result["evaluation"]
            
            # Stop here if refinement is disabled
            if not use_refinement:
                return initial_scene_result
            
            # Report expansion progress
            if progress_callback:
                progress_callback({
                    "phase": "expansion",
                    "current_step": 2,
                    "total_steps": 3,
                    "message": "Expanding scene with details"
                })
            
            # Expand scene if it's too short
            current_length = len(initial_scene)
            if current_length < self.target_scene_length and self.refinement_system:
                expansion_result = self.refinement_system.expand_scene_content(
                    initial_scene,
                    lambda prompt: self.get_llm().invoke(prompt),
                    self.target_scene_length,
                    progress_callback
                )
                expanded_scene = expansion_result["expanded_scene"]
            else:
                expanded_scene = initial_scene
                expansion_result = {
                    "original_length": current_length,
                    "final_length": current_length,
                    "expansion_ratio": 1.0
                }
            
            # Report refinement progress
            if progress_callback:
                progress_callback({
                    "phase": "refinement",
                    "current_step": 3,
                    "total_steps": 3,
                    "message": "Refining scene quality"
                })
            
            # Refine the scene
            if self.refinement_system:
                req_dict = requirements.model_dump() if hasattr(requirements, 'model_dump') else requirements.dict()
                req_dict["scene_id"] = scene_id
                refinement_result = self.refinement_system.refine_scene_iteratively(
                    expanded_scene,
                    lambda prompt: self.get_llm().invoke(prompt),
                    req_dict,
                    progress_callback
                )
                final_scene = refinement_result["refined_scene"]
                final_evaluation = refinement_result["final_evaluation"]
            else:
                final_scene = expanded_scene
                final_evaluation = self.quality_control.evaluate_scene(expanded_scene, requirements)
                refinement_result = {
                    "iterations_performed": 0,
                    "overall_improvement": 0.0
                }
            
            # Record the refined scene in previous scenes
            self.previous_scenes.append(final_scene)
            
            # Calculate total time
            total_time = time.time() - start_time
            
            # Return the final result
            return {
                "scene": final_scene,
                "evaluation": final_evaluation,
                "initial_evaluation": initial_evaluation,
                "timing_metrics": {
                    "initial_generation": initial_scene_result.get("timing_metrics", {}).get("total_time", 0),
                    "expansion": expansion_result.get("expansion_ratio", 1.0),
                    "refinement_iterations": refinement_result.get("iterations_performed", 0),
                    "total_time": total_time
                },
                "iterations": refinement_result.get("iterations_performed", 0) + 1,
                "iteration_metrics": refinement_result.get("iteration_metrics", []),
                "quality_improvement": refinement_result.get("overall_improvement", 0.0),
                "scene_id": scene_id
            }
                
        except Exception as e:
            logger.error(f"Error in scene generation: {str(e)}")
            raise
    
    def _generate_initial_scene(
        self, 
        requirements: SceneRequirements, 
        previous_scene: Optional[str] = None,
        previous_feedback: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate the initial scene draft."""
        start_time = time.time()
        
        # Construct the prompt
        prompt = self._construct_scene_prompt(requirements, previous_scene, previous_feedback)
        
        # Generate the scene
        response = self.get_llm().invoke(prompt)
        scene_content = str(response.content)
        
        # Process the scene
        if not self.scene_processor:
            raise ValueError("scene_processor is not initialized")
            
        processed_content = self.scene_processor.process_scene_content(scene_content)
        
        # Evaluate the scene
        if not self.quality_control:
            raise ValueError("quality_control is not initialized")
            
        evaluation = self.quality_control.evaluate_scene(processed_content["scene"], requirements)
        
        # Calculate timing metrics
        end_time = time.time()
        timing_metrics = {
            "start_time": start_time,
            "end_time": end_time,
            "total_time": end_time - start_time
        }
        
        return {
            "scene": processed_content["scene"],
            "narrative_analysis": processed_content.get("narrative_analysis", ""),
            "evaluation": evaluation,
            "timing_metrics": timing_metrics,
            "raw_content": processed_content.get("raw_content", "")
        }
    
    def collaborate_on_scene(
        self,
        other_playwright: 'EnhancedPlaywright',
        requirements: SceneRequirements,
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ) -> Dict[str, Any]:
        """
        Enhanced collaboration with another playwright on scene generation.
        
        This version adds iterative refinement to the collaborative process.
        """
        try:
            # Generate a shared scene ID for the collaboration
            import uuid
            scene_id = str(uuid.uuid4())
            logger.info(f"Starting enhanced collaboration between {self.name} and {other_playwright.name}")
            
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
                use_refinement=False  # Skip refinement for initial draft
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
                use_refinement=False  # Skip refinement for enhancement
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
                
            if self.refinement_system:
                refinement_result = self.refinement_system.refine_scene_iteratively(
                    synthesized_scene,
                    lambda prompt: self.get_llm().invoke(prompt),
                    {**requirements.model_dump() if hasattr(requirements, 'model_dump') else requirements.dict(), "scene_id": scene_id},
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
                "iterations": opening_result["iterations"] + enhanced_result["iterations"] + 
                            refinement_result.get("iterations_performed", 0),
                "iteration_metrics": opening_result.get("iteration_metrics", []) + 
                                    enhanced_result.get("iteration_metrics", []) +
                                    refinement_result.get("iteration_metrics", []),
                "scene_id": scene_id,
                "collaboration_data": {
                    "opening_playwright": self.name,
                    "enhancing_playwright": other_playwright.name,
                    "opening_scene": opening_result["scene"],
                    "enhanced_scene": enhanced_result["scene"],
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