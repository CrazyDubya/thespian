"""
Iterative refinement system for enhancing theatrical scenes.
"""

from typing import Dict, Any, List, Optional, Callable, Tuple, Union
from pydantic import BaseModel, Field, ConfigDict
import logging
import time
import json
from datetime import datetime

from thespian.config.enhanced_prompts import ENHANCED_PROMPT_TEMPLATES
from thespian.llm.quality_control import TheatricalQualityControl

logger = logging.getLogger(__name__)

class IterationMetrics(BaseModel):
    """Metrics for a single iteration of scene enhancement."""
    
    iteration_number: int
    scene_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    quality_scores: Dict[str, float]
    previous_scores: Dict[str, float]
    improvement: Dict[str, float]
    overall_improvement: float
    focus_areas: List[str]
    processing_time: float
    
    @property
    def significant_improvement(self) -> bool:
        """Check if the iteration produced significant improvement."""
        return self.overall_improvement >= 0.02  # 2% improvement threshold
    
    def get_focus_areas_for_next_iteration(self) -> List[str]:
        """Determine focus areas for the next iteration."""
        # Find metrics that improved the least
        improvement_items = sorted(self.improvement.items(), key=lambda x: x[1])
        return [item[0] for item in improvement_items[:3]]  # Return 3 areas with least improvement


class IterativeRefinementSystem(BaseModel):
    """System for iteratively refining and enhancing theatrical scenes."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    quality_control: TheatricalQualityControl
    max_iterations: int = 5
    improvement_threshold: float = 0.02  # Minimum improvement to continue iterations
    quality_threshold: float = 0.85  # Quality score to consider refinement complete
    
    def refine_scene_iteratively(
        self, 
        scene: str, 
        llm_invoke_func: Callable,
        requirements: Dict[str, Any],
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ) -> Dict[str, Any]:
        """
        Refine a scene through multiple iterations of improvement.
        
        Args:
            scene: Initial scene content
            llm_invoke_func: Function to invoke LLM with a prompt
            requirements: Scene requirements
            progress_callback: Optional callback for reporting progress
            
        Returns:
            Dict containing the refined scene and iteration metrics
        """
        scene_id = requirements.get("scene_id", f"scene_{int(time.time())}")
        current_scene = scene
        iteration_metrics: List[IterationMetrics] = []
        
        # Initial evaluation
        initial_evaluation = self.quality_control.evaluate_scene(current_scene, requirements)
        initial_scores = {k: v for k, v in initial_evaluation.items() if isinstance(v, (int, float))}
        
        # If initial quality is already high enough, skip refinement
        overall_initial_quality = sum(initial_scores.values()) / len(initial_scores) if initial_scores else 0
        if overall_initial_quality >= self.quality_threshold:
            logger.info(f"Scene {scene_id} already meets quality threshold ({overall_initial_quality:.2f}). Skipping refinement.")
            return {
                "refined_scene": current_scene,
                "initial_evaluation": initial_evaluation,
                "final_evaluation": initial_evaluation,
                "iteration_metrics": [],
                "iterations_performed": 0,
                "overall_improvement": 0.0
            }
        
        # Determine initial focus areas
        initial_focus_areas = self._determine_focus_areas(initial_scores)
        
        # Perform iterations
        for i in range(self.max_iterations):
            iteration_number = i + 1
            logger.info(f"Starting refinement iteration {iteration_number} for scene {scene_id}")
            
            # Report progress if callback provided
            if progress_callback:
                progress_callback({
                    "phase": "refining",
                    "current_step": iteration_number,
                    "total_steps": self.max_iterations,
                    "message": f"Refining scene (iteration {iteration_number}/{self.max_iterations})"
                })
            
            # Determine focus areas for this iteration
            focus_areas = initial_focus_areas if i == 0 else iteration_metrics[-1].get_focus_areas_for_next_iteration()
            
            # Create refinement prompt
            start_time = time.time()
            refinement_prompt = self._create_refinement_prompt(
                current_scene, 
                initial_evaluation if i == 0 else latest_evaluation,
                iteration_number,
                focus_areas,
                iteration_metrics,
                requirements
            )
            
            # Get refined scene from LLM with self-correction
            max_retry_attempts = 2
            refined_scene = None
            for retry_attempt in range(max_retry_attempts + 1):
                if retry_attempt > 0:
                    # Add corrective feedback for retry
                    correction_prompt = f"""CORRECTION NEEDED: Your previous response failed to generate a proper scene.

Previous response that failed:
{str(response)[:1000]}...

Please provide a complete refined scene with:
- Clear scene structure
- Proper formatting with character names, stage directions, and technical cues
- Substantive content that improves upon the original

{refinement_prompt}"""
                    response = llm_invoke_func(correction_prompt)
                else:
                    response = llm_invoke_func(refinement_prompt)
                    
                refined_scene = self._extract_scene_content(response)
                
                if refined_scene:
                    break
                else:
                    logger.warning(f"Scene refinement attempt {retry_attempt + 1} failed to extract content")
                    if retry_attempt == max_retry_attempts:
                        logger.warning(f"Failed to extract scene content from LLM response in iteration {iteration_number}")
                        continue  # Skip this iteration if all extraction attempts fail
                
            # Evaluate refined scene
            latest_evaluation = self.quality_control.evaluate_scene(refined_scene, requirements)
            latest_scores = {k: v for k, v in latest_evaluation.items() if isinstance(v, (int, float))}
            
            # Calculate improvement
            previous_scores = initial_scores if i == 0 else {k: v for k, v in iteration_metrics[-1].quality_scores.items()}
            improvements = {k: latest_scores.get(k, 0) - previous_scores.get(k, 0) for k in latest_scores}
            overall_improvement = sum(improvements.values()) / len(improvements) if improvements else 0
            
            # Record processing time
            processing_time = time.time() - start_time
            
            # Create metrics for this iteration
            metrics = IterationMetrics(
                iteration_number=iteration_number,
                scene_id=scene_id,
                quality_scores=latest_scores,
                previous_scores=previous_scores,
                improvement=improvements,
                overall_improvement=overall_improvement,
                focus_areas=focus_areas,
                processing_time=processing_time
            )
            iteration_metrics.append(metrics)
            
            # Update current scene
            current_scene = refined_scene
            
            # Check termination conditions
            overall_quality = sum(latest_scores.values()) / len(latest_scores) if latest_scores else 0
            logger.info(f"Iteration {iteration_number} complete. Quality: {overall_quality:.2f}, Improvement: {overall_improvement:.2f}")
            
            if overall_quality >= self.quality_threshold:
                logger.info(f"Quality threshold reached ({overall_quality:.2f}). Stopping refinement.")
                break
                
            if i > 0 and overall_improvement < self.improvement_threshold:
                logger.info(f"Improvement below threshold ({overall_improvement:.2f}). Stopping refinement.")
                break
        
        # Calculate total improvement from initial to final scene
        total_improvement = self._calculate_total_improvement(initial_scores, latest_scores)
        
        return {
            "refined_scene": current_scene,
            "initial_evaluation": initial_evaluation,
            "final_evaluation": latest_evaluation,
            "iteration_metrics": [m.model_dump() if hasattr(m, 'model_dump') else m.dict() for m in iteration_metrics],
            "iterations_performed": len(iteration_metrics),
            "overall_improvement": total_improvement
        }
    
    def _create_refinement_prompt(
        self, 
        scene: str, 
        evaluation: Dict[str, Any],
        iteration_number: int,
        focus_areas: List[str],
        previous_iterations: List[IterationMetrics],
        requirements: Dict[str, Any]
    ) -> str:
        """Create the prompt for scene refinement."""
        # Format previous iterations summary
        iterations_summary = ""
        if previous_iterations:
            iterations_summary = "\n".join([
                f"Iteration {m.iteration_number}: "
                f"Quality={sum(m.quality_scores.values())/len(m.quality_scores):.2f}, "
                f"Improvement={m.overall_improvement:.2f}, "
                f"Focus Areas: {', '.join(m.focus_areas)}"
                for m in previous_iterations
            ])
        
        # Format evaluation data
        evaluation_formatted = json.dumps(evaluation, indent=2)
        
        # Format focus areas for this iteration
        focus_areas_formatted = "\n".join([f"- {area}" for area in focus_areas])
        
        # Get scene length requirements
        min_length = requirements.get("min_length", 3000)
        max_length = requirements.get("max_length", 10000)
        
        return ENHANCED_PROMPT_TEMPLATES["iterative_scene_refinement"].format(
            iteration_number=iteration_number,
            scene_content=scene,
            evaluation=evaluation_formatted,
            previous_iterations=iterations_summary,
            focus_areas=focus_areas_formatted,
            min_length=min_length,
            max_length=max_length
        )
    
    def _extract_scene_content(self, llm_response: Any) -> str:
        """Extract scene content from LLM response."""
        response_text = str(llm_response.content if hasattr(llm_response, "content") else llm_response)
        
        # Try to extract content between REFINED SCENE: and REFINEMENT ANALYSIS:
        refined_scene_marker = "REFINED SCENE:"
        analysis_marker = "REFINEMENT ANALYSIS:"
        
        if refined_scene_marker in response_text and analysis_marker in response_text:
            start_idx = response_text.find(refined_scene_marker) + len(refined_scene_marker)
            end_idx = response_text.find(analysis_marker)
            if start_idx < end_idx:
                return response_text[start_idx:end_idx].strip()
        
        # Fallback: return the whole response if markers not found
        return response_text
    
    def _determine_focus_areas(self, scores: Dict[str, float]) -> List[str]:
        """Determine focus areas for refinement based on scores."""
        # Sort metrics by score, ascending
        sorted_metrics = sorted(scores.items(), key=lambda x: x[1])
        
        # Return the three lowest scoring areas
        return [metric[0] for metric in sorted_metrics[:3]]
    
    def _calculate_total_improvement(self, initial_scores: Dict[str, float], final_scores: Dict[str, float]) -> float:
        """Calculate total improvement from initial to final scores."""
        improvements = []
        for key in set(initial_scores.keys()) & set(final_scores.keys()):
            improvements.append(final_scores[key] - initial_scores[key])
        
        return sum(improvements) / len(improvements) if improvements else 0.0
    
    def expand_scene_content(
        self, 
        scene: str, 
        llm_invoke_func: Callable,
        target_length: int = 5000,
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ) -> Dict[str, Any]:
        """
        Expand a scene with more detailed content.
        
        Args:
            scene: Scene content to expand
            llm_invoke_func: Function to invoke LLM with a prompt
            target_length: Target character length for expanded scene
            progress_callback: Optional callback for reporting progress
            
        Returns:
            Dict containing the expanded scene and analysis
        """
        current_length = len(scene)
        
        # Skip if already at or above target length
        if current_length >= target_length:
            logger.info(f"Scene already meets target length ({current_length} >= {target_length}). Skipping expansion.")
            return {
                "expanded_scene": scene,
                "original_length": current_length,
                "final_length": current_length,
                "expansion_ratio": 1.0
            }
        
        # Report progress if callback provided
        if progress_callback:
            progress_callback({
                "phase": "expanding",
                "message": f"Expanding scene from {current_length} to {target_length} characters"
            })
        
        # Create expansion prompt
        expansion_prompt = ENHANCED_PROMPT_TEMPLATES["scene_expansion"].format(
            scene=scene,
            current_length=current_length,
            target_length=target_length
        )
        
        # Get expanded scene from LLM with self-correction
        max_retry_attempts = 2
        expanded_scene = None
        for retry_attempt in range(max_retry_attempts + 1):
            if retry_attempt > 0:
                # Add corrective feedback for retry
                correction_prompt = f"""CORRECTION NEEDED: Your previous response failed to expand the scene properly.

Previous response that failed:
{str(response)[:1000]}...

Please provide a properly expanded scene that:
- Includes all content from the original scene
- Adds substantial new content to reach {target_length} characters
- Maintains narrative integrity and character consistency
- Uses proper theatrical formatting

{expansion_prompt}"""
                response = llm_invoke_func(correction_prompt)
            else:
                response = llm_invoke_func(expansion_prompt)
                
            expanded_scene = self._extract_expanded_content(response)
            
            if expanded_scene and len(expanded_scene) > current_length:
                break
            else:
                logger.warning(f"Scene expansion attempt {retry_attempt + 1} failed")
                if retry_attempt == max_retry_attempts:
                    logger.warning("Failed to extract expanded scene content from LLM response")
                    return {
                        "expanded_scene": scene,
                        "original_length": current_length,
                        "final_length": current_length,
                        "expansion_ratio": 1.0,
                        "error": "Failed to extract expanded content"
                    }
        
        expanded_length = len(expanded_scene)
        expansion_ratio = expanded_length / current_length if current_length > 0 else 1.0
        
        # Validate the expanded scene maintains narrative integrity
        if not self._validate_expanded_scene(scene, expanded_scene):
            logger.warning("Expanded scene failed validation, reverting to original")
            return {
                "expanded_scene": scene,
                "original_length": current_length,
                "final_length": current_length,
                "expansion_ratio": 1.0,
                "error": "Expanded scene failed validation"
            }
        
        logger.info(f"Scene expanded from {current_length} to {expanded_length} characters (ratio: {expansion_ratio:.2f})")
        
        return {
            "expanded_scene": expanded_scene,
            "original_length": current_length,
            "final_length": expanded_length,
            "expansion_ratio": expansion_ratio
        }
    
    def _extract_expanded_content(self, llm_response: Any) -> str:
        """Extract expanded scene content from LLM response."""
        response_text = str(llm_response.content if hasattr(llm_response, "content") else llm_response)
        
        # Try to extract content between EXPANDED SCENE: and EXPANSION ANALYSIS:
        expanded_scene_marker = "EXPANDED SCENE:"
        analysis_marker = "EXPANSION ANALYSIS:"
        
        if expanded_scene_marker in response_text and analysis_marker in response_text:
            start_idx = response_text.find(expanded_scene_marker) + len(expanded_scene_marker)
            end_idx = response_text.find(analysis_marker)
            if start_idx < end_idx:
                return response_text[start_idx:end_idx].strip()
        
        # Fallback: return the whole response if markers not found
        return response_text
    
    def _validate_expanded_scene(self, original_scene: str, expanded_scene: str) -> bool:
        """
        Validate that the expanded scene maintains narrative integrity.
        
        Basic validation to ensure the expanded scene contains key elements 
        from the original scene.
        """
        # Extract character names from original scene
        import re
        character_pattern = r'\b([A-Z]{2,})\b'
        original_characters = set(re.findall(character_pattern, original_scene))
        expanded_characters = set(re.findall(character_pattern, expanded_scene))
        
        # Check that all original characters are present in expanded scene
        if not original_characters.issubset(expanded_characters):
            missing_chars = original_characters - expanded_characters
            logger.warning(f"Expanded scene is missing characters: {missing_chars}")
            return False
            
        # Check that expanded scene is longer than original
        if len(expanded_scene) <= len(original_scene):
            logger.warning("Expanded scene is not longer than original")
            return False
            
        # Check that expanded scene contains key plot elements
        # This is a simple check that looks for significant sentences from the original
        sentences = [s.strip() for s in original_scene.split(".") if len(s.strip()) > 40]
        if sentences:
            # Test a sample of significant sentences (at least 25% of them)
            sample_size = max(1, len(sentences) // 4)
            sample_sentences = sentences[:sample_size]
            
            # For each sample sentence, check if its essence appears in expanded scene
            for sentence in sample_sentences:
                words = set(word.lower() for word in sentence.split() if len(word) > 5)
                significant_words = [word for word in words if len(word) > 5][:5]
                
                # Check if at least 3 significant words appear in the expanded scene
                matches = sum(1 for word in significant_words if word in expanded_scene.lower())
                if matches < min(3, len(significant_words)):
                    logger.warning(f"Expanded scene may be missing key plot elements from: '{sentence}'")
                    return False
        
        return True