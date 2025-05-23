"""
QuantumPlaywright: Enhanced playwright with quantum narrative exploration capabilities.

This module extends the base Playwright class with quantum narrative functionality,
allowing exploration of multiple story possibilities before committing to a single path.
"""

from typing import Dict, Any, List, Optional, Callable, Union, Tuple
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum
import logging
import json
import time
from datetime import datetime

from thespian.llm.consolidated_playwright import Playwright, PlaywrightCapability, SceneRequirements
from thespian.llm.quantum_narrative import (
    QuantumNarrativeTree, 
    NarrativeQuantumState, 
    DivergenceType,
    CollapseTrigger,
    CollapseTriggerType,
    QuantumBranchGenerator
)
from thespian.llm.enhanced_memory import EnhancedTheatricalMemory
from thespian.llm import LLMManager

logger = logging.getLogger(__name__)

class QuantumExplorationMode(str, Enum):
    """Modes of quantum narrative exploration."""
    DISABLED = "disabled"               # Standard linear generation
    CHARACTER_FOCUSED = "character_focused"     # Explore character psychology branches
    THEMATIC_FOCUSED = "thematic_focused"       # Explore thematic variations
    STRUCTURAL_FOCUSED = "structural_focused"   # Explore dramatic structure alternatives
    FULL_EXPLORATION = "full_exploration"       # Explore all branch types

class QuantumPlaywright(Playwright):
    """Enhanced playwright with quantum narrative exploration capabilities."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    # Quantum narrative components
    quantum_tree: Optional[QuantumNarrativeTree] = None
    branch_generator: Optional[QuantumBranchGenerator] = None
    
    # Exploration configuration
    exploration_mode: QuantumExplorationMode = QuantumExplorationMode.DISABLED
    auto_collapse_enabled: bool = Field(default=True)
    max_exploration_depth: int = Field(default=3, ge=1, le=25)  # Allow ultra-deep exploration
    exploration_breadth: int = Field(default=4, ge=2, le=50)  # Allow ultra-wide exploration
    
    # LLM call tracking
    llm_call_count: int = Field(default=0)
    quantum_enabled: bool = Field(default=False)
    
    # Quality thresholds
    min_branch_quality: float = Field(default=0.3, ge=0.0, le=1.0)
    collapse_quality_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    
    # Performance settings
    quantum_enabled: bool = Field(default=False)
    exploration_timeout: float = Field(default=30.0)  # Seconds
    
    def __init__(self, **data: Any) -> None:
        """Initialize quantum playwright."""
        super().__init__(**data)
        
        # Initialize quantum components if memory enhancement is enabled
        if (PlaywrightCapability.MEMORY_ENHANCEMENT in self.enabled_capabilities and 
            isinstance(self.memory, EnhancedTheatricalMemory)):
            self.branch_generator = QuantumBranchGenerator(self.memory)
            logger.info("Quantum narrative capabilities initialized")
        else:
            logger.warning("Quantum capabilities require MEMORY_ENHANCEMENT and EnhancedTheatricalMemory")
    
    def enable_quantum_exploration(self, 
                                  mode: QuantumExplorationMode = QuantumExplorationMode.FULL_EXPLORATION,
                                  max_depth: int = 3,
                                  max_breadth: int = 4) -> None:
        """Enable quantum narrative exploration."""
        if not self.branch_generator:
            logger.error("Cannot enable quantum exploration without proper initialization")
            return
        
        self.quantum_enabled = True
        self.exploration_mode = mode
        self.max_exploration_depth = max_depth
        self.exploration_breadth = max_breadth
        
        logger.info(f"Quantum exploration enabled in {mode} mode")
    
    def disable_quantum_exploration(self) -> None:
        """Disable quantum narrative exploration."""
        self.quantum_enabled = False
        self.exploration_mode = QuantumExplorationMode.DISABLED
        
        if self.quantum_tree:
            # Store final state before disabling
            final_summary = self.quantum_tree.get_exploration_summary()
            logger.info(f"Quantum exploration disabled. Final state: {final_summary}")
    
    def tracked_llm_invoke(self, prompt: str):
        """Invoke LLM with call tracking."""
        self.llm_call_count += 1
        logger.info(f"LLM call #{self.llm_call_count} for quantum exploration")
        return self.get_llm().invoke(prompt)
    
    def generate_scene_with_quantum_exploration(self,
                                               requirements: SceneRequirements,
                                               explore_alternatives: bool = True,
                                               force_collapse: bool = False,
                                               exploration_focus: Optional[str] = None,
                                               progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None) -> Dict[str, Any]:
        """
        Generate scene with quantum narrative exploration.
        
        Args:
            requirements: Scene requirements
            explore_alternatives: Whether to explore alternative narrative paths
            force_collapse: Whether to immediately collapse to single path
            exploration_focus: Specific focus for exploration (character name, theme, etc.)
            progress_callback: Optional callback for progress updates
            
        Returns:
            Dict containing scene content and quantum exploration metadata
        """
        start_time = time.time()
        
        # Check if quantum exploration is enabled and appropriate
        if not (self.quantum_enabled and explore_alternatives and self.branch_generator):
            # Fall back to standard scene generation
            return self._generate_standard_scene_with_metadata(requirements, progress_callback)
        
        try:
            # Initialize quantum tree if needed
            if not self.quantum_tree:
                initial_state = self._create_initial_quantum_state(requirements)
                self.quantum_tree = QuantumNarrativeTree(
                    root_state=initial_state,
                    max_active_branches=self.exploration_breadth,
                    max_exploration_depth=self.max_exploration_depth,
                    min_quality_threshold=self.min_branch_quality
                )
                
                if progress_callback:
                    progress_callback({
                        "phase": "quantum_initialization",
                        "message": "Initializing quantum narrative exploration"
                    })
            
            # Generate and explore narrative branches
            exploration_result = self._explore_narrative_branches(
                requirements, 
                exploration_focus, 
                progress_callback
            )
            
            # Determine if collapse is needed
            collapse_trigger = None
            if force_collapse or self.auto_collapse_enabled:
                collapse_context = self._build_collapse_context(requirements)
                collapse_trigger = self.quantum_tree.evaluate_collapse_triggers(collapse_context)
            
            # Handle collapse or return superposition
            if collapse_trigger or force_collapse:
                if progress_callback:
                    progress_callback({
                        "phase": "quantum_collapse",
                        "message": f"Collapsing quantum state: {collapse_trigger.reason if collapse_trigger else 'forced'}"
                    })
                
                selected_branch = self.quantum_tree.collapse_to_path(collapse_trigger)
                final_scene = selected_branch.narrative_content
                timeline_state = "collapsed"
                
                # Process final scene through standard pipeline
                processed_scene = self._process_collapsed_scene(selected_branch, requirements)
                final_scene = processed_scene["scene"]
                
            else:
                # Return superposition summary
                final_scene = self._create_superposition_summary()
                timeline_state = "superposition"
            
            # Calculate exploration time
            exploration_time = time.time() - start_time
            
            # Create comprehensive result
            result = {
                "scene": final_scene,
                "quantum_metadata": {
                    "exploration_mode": self.exploration_mode,
                    "timeline_state": timeline_state,
                    "exploration_time": exploration_time,
                    "branches_explored": len(self.quantum_tree.active_branches),
                    "total_llm_calls": self.llm_call_count,
                    "collapse_trigger": collapse_trigger.dict() if collapse_trigger else None,
                    "exploration_summary": self.quantum_tree.get_exploration_summary(),
                    "alternative_paths": self._get_alternative_paths_summary()
                },
                "evaluation": exploration_result.get("best_branch_evaluation", {}),
                "timing_metrics": {
                    "quantum_exploration": exploration_time,
                    "total_time": exploration_time
                }
            }
            
            # Add standard scene metadata if collapsed
            if timeline_state == "collapsed":
                result.update({
                    "scene_id": selected_branch.branch_id,
                    "narrative_analysis": self._analyze_final_narrative(selected_branch),
                    "character_development": self._extract_character_development(selected_branch),
                    "thematic_elements": self._extract_thematic_elements(selected_branch)
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error in quantum scene generation: {str(e)}")
            # Fall back to standard generation
            return self._generate_standard_scene_with_metadata(requirements, progress_callback)
    
    def _create_initial_quantum_state(self, requirements: SceneRequirements) -> NarrativeQuantumState:
        """Create initial quantum state for scene generation."""
        # Generate initial scene content
        initial_scene_result = self._generate_initial_scene(requirements, None, None)
        
        # Create quantum state
        initial_state = NarrativeQuantumState(
            narrative_content=initial_scene_result["scene"],
            scene_outline=f"Act {requirements.act_number}, Scene {requirements.scene_number}",
            divergence_point="story_beginning",
            divergence_type=DivergenceType.DRAMATIC_STRUCTURE,
            divergence_description="Initial scene generation",
            depth_level=0
        )
        
        # Set initial character states
        for character in requirements.characters:
            char_id = character.lower().replace(" ", "_")
            profile = self.memory.get_character_profile(char_id) if hasattr(self.memory, 'get_character_profile') else None
            
            initial_state.character_states[char_id] = {
                "name": character,
                "present_in_scene": True,
                "emotional_state": "initial",
                "character_arc_stage": "beginning",
                "profile": profile.dict() if profile and hasattr(profile, 'dict') else None
            }
        
        # Set initial world state
        initial_state.world_state = {
            "act_number": requirements.act_number,
            "scene_number": requirements.scene_number,
            "setting": requirements.setting,
            "central_conflict": getattr(requirements, 'key_conflict', ''),
            "thematic_tension": getattr(requirements, 'emotional_arc', ''),
            "style": requirements.style,
            "period": requirements.period
        }
        
        # Calculate initial quality metrics
        if self.quality_control:
            evaluation = self.quality_control.evaluate_scene(initial_state.narrative_content, requirements)
            initial_state.character_consistency = evaluation.get("character_consistency", 0.5)
            initial_state.thematic_alignment = evaluation.get("thematic_coherence", 0.5)
            initial_state.dramatic_tension = evaluation.get("dramatic_impact", 0.5)
            initial_state.emotional_resonance = evaluation.get("dialogue_quality", 0.5)
            initial_state.narrative_coherence = evaluation.get("stage_direction_quality", 0.5)
        
        initial_state.add_exploration_note("Initial quantum state created from scene requirements")
        
        return initial_state
    
    def _explore_narrative_branches(self,
                                   requirements: SceneRequirements,
                                   exploration_focus: Optional[str],
                                   progress_callback: Optional[Callable[[Dict[str, Any]], None]]) -> Dict[str, Any]:
        """Explore narrative branches based on exploration mode."""
        if not self.quantum_tree or not self.branch_generator:
            return {"error": "Quantum components not initialized"}
        
        exploration_results = {
            "branches_generated": 0,
            "best_branch_quality": 0.0,
            "best_branch_evaluation": {},
            "exploration_notes": []
        }
        
        # Get current active branches to explore from
        branches_to_explore = list(self.quantum_tree.active_branches.values())
        
        for current_branch in branches_to_explore:
            if current_branch.depth_level >= self.max_exploration_depth:
                continue
            
            # Generate branches based on exploration mode
            new_branches = []
            
            if self.exploration_mode in [QuantumExplorationMode.CHARACTER_FOCUSED, QuantumExplorationMode.FULL_EXPLORATION]:
                new_branches.extend(self._generate_character_branches(current_branch, requirements, exploration_focus))
            
            if self.exploration_mode in [QuantumExplorationMode.THEMATIC_FOCUSED, QuantumExplorationMode.FULL_EXPLORATION]:
                new_branches.extend(self._generate_thematic_branches(current_branch, requirements))
            
            if self.exploration_mode in [QuantumExplorationMode.STRUCTURAL_FOCUSED, QuantumExplorationMode.FULL_EXPLORATION]:
                new_branches.extend(self._generate_structural_branches(current_branch, requirements))
            
            # Add viable branches to quantum tree
            for branch in new_branches:
                if self.quantum_tree.add_branch(current_branch.branch_id, branch):
                    exploration_results["branches_generated"] += 1
                    
                    # Track best branch
                    branch_quality = branch.calculate_overall_quality()
                    if branch_quality > exploration_results["best_branch_quality"]:
                        exploration_results["best_branch_quality"] = branch_quality
                        exploration_results["best_branch_evaluation"] = {
                            "character_consistency": branch.character_consistency,
                            "thematic_alignment": branch.thematic_alignment,
                            "dramatic_tension": branch.dramatic_tension,
                            "emotional_resonance": branch.emotional_resonance,
                            "narrative_coherence": branch.narrative_coherence,
                            "overall_quality": branch_quality
                        }
            
            # Update progress
            if progress_callback:
                progress_callback({
                    "phase": "quantum_exploration",
                    "message": f"Explored {exploration_results['branches_generated']} branches",
                    "branches_active": len(self.quantum_tree.active_branches)
                })
        
        exploration_results["exploration_notes"] = [
            f"Generated {exploration_results['branches_generated']} branches",
            f"Best branch quality: {exploration_results['best_branch_quality']:.3f}",
            f"Final active branches: {len(self.quantum_tree.active_branches)}"
        ]
        
        return exploration_results
    
    def _generate_character_branches(self,
                                    current_branch: NarrativeQuantumState,
                                    requirements: SceneRequirements,
                                    focus_character: Optional[str]) -> List[NarrativeQuantumState]:
        """Generate branches focused on character psychology."""
        if not self.branch_generator:
            return []
        
        branches = []
        
        # Determine which characters to explore
        characters_to_explore = [focus_character] if focus_character else requirements.characters[:2]  # Limit to 2 for performance
        
        for character in characters_to_explore:
            if character not in current_branch.character_states:
                continue
            
            # Create decision context
            decision_context = self._extract_decision_context(current_branch, character, requirements)
            
            # Generate psychology-based branches
            char_branches = self.branch_generator.generate_character_psychology_branches(
                character_name=character,
                decision_context=decision_context,
                current_state=current_branch,
                llm_invoke_func=self.tracked_llm_invoke
            )
            
            branches.extend(char_branches)
        
        return branches
    
    def _generate_thematic_branches(self,
                                   current_branch: NarrativeQuantumState,
                                   requirements: SceneRequirements) -> List[NarrativeQuantumState]:
        """Generate branches focused on thematic exploration."""
        if not self.branch_generator:
            return []
        
        # Extract thematic tension
        thematic_tension = (
            current_branch.world_state.get("thematic_tension") or
            getattr(requirements, 'emotional_arc', '') or
            "individual desires vs collective needs"  # Default tension
        )
        
        return self.branch_generator.generate_thematic_exploration_branches(
            thematic_tension=thematic_tension,
            current_state=current_branch,
            llm_invoke_func=self.tracked_llm_invoke
        )
    
    def _generate_structural_branches(self,
                                     current_branch: NarrativeQuantumState,
                                     requirements: SceneRequirements) -> List[NarrativeQuantumState]:
        """Generate branches focused on dramatic structure alternatives."""
        # This is a simplified implementation - could be expanded significantly
        branches = []
        
        # Determine structural context
        act_number = requirements.act_number
        scene_number = requirements.scene_number
        
        # Generate structure-based alternatives
        structural_alternatives = {
            "tension_escalation": "Focus on building tension and conflict",
            "emotional_revelation": "Focus on character emotional discovery",
            "relationship_shift": "Focus on changing character relationships",
            "plot_advancement": "Focus on advancing the main plot"
        }
        
        for structure_type, description in structural_alternatives.items():
            prompt = f"""Based on this current scene context:
{current_branch.narrative_content[:300]}...

Generate a continuation that emphasizes {description}. This is Act {act_number}, Scene {scene_number}.

Create 300-400 words that:
- {description}
- Maintains character consistency
- Advances the story meaningfully
- Uses theatrical formatting (character names in CAPS, stage directions in parentheses)
"""
            
            try:
                response = self.tracked_llm_invoke(prompt)
                response_text = str(response.content if hasattr(response, "content") else response)
                
                # Create structural branch
                structural_branch = NarrativeQuantumState(
                    narrative_content=response_text,
                    divergence_point=f"Structural focus: {structure_type}",
                    divergence_type=DivergenceType.DRAMATIC_STRUCTURE,
                    divergence_description=description,
                    parent_branch=current_branch.branch_id,
                    depth_level=current_branch.depth_level + 1
                )
                
                # Copy and update world state
                structural_branch.world_state = current_branch.world_state.copy()
                structural_branch.world_state["structural_focus"] = structure_type
                
                # Set quality metrics
                structural_branch.dramatic_tension = 0.7 if "tension" in structure_type else 0.5
                structural_branch.emotional_resonance = 0.7 if "emotional" in structure_type else 0.5
                structural_branch.narrative_coherence = 0.6  # Structural branches generally coherent
                
                branches.append(structural_branch)
                
            except Exception as e:
                logger.error(f"Error generating structural branch {structure_type}: {str(e)}")
        
        return branches
    
    def _extract_decision_context(self,
                                 current_branch: NarrativeQuantumState,
                                 character: str,
                                 requirements: SceneRequirements) -> str:
        """Extract decision context for character from current branch."""
        # Analyze the current scene for decision points
        content = current_branch.narrative_content
        
        # Simple heuristic: look for questions, conflicts, or choices
        decision_indicators = [
            "should", "could", "must", "what if", "either", "or",
            "choose", "decide", "question", "dilemma", "conflict"
        ]
        
        # Extract relevant context
        sentences = content.split('.')
        decision_sentences = [
            sentence.strip() for sentence in sentences
            if any(indicator in sentence.lower() for indicator in decision_indicators)
        ]
        
        if decision_sentences:
            decision_context = ". ".join(decision_sentences[:2])  # First 2 relevant sentences
        else:
            # Fallback: use scene outline or general context
            decision_context = (
                getattr(requirements, 'key_conflict', '') or
                f"responding to the events in Act {requirements.act_number}, Scene {requirements.scene_number}"
            )
        
        return decision_context
    
    def _build_collapse_context(self, requirements: SceneRequirements) -> Dict[str, Any]:
        """Build context for evaluating collapse triggers."""
        return {
            "act_number": requirements.act_number,
            "scene_number": requirements.scene_number,
            "act_ending_approaches": requirements.scene_number >= 4,
            "climax_approaching": requirements.act_number == 3 and requirements.scene_number >= 3,
            "character_makes_irreversible_choice": False,  # Would need content analysis
            "theme_needs_resolution": requirements.act_number == 3,
            "branch_count": len(self.quantum_tree.active_branches) if self.quantum_tree else 0,
            "max_branches": self.exploration_breadth
        }
    
    def _process_collapsed_scene(self,
                                selected_branch: NarrativeQuantumState,
                                requirements: SceneRequirements) -> Dict[str, Any]:
        """Process collapsed scene through standard pipeline."""
        if not self.scene_processor:
            return {"scene": selected_branch.narrative_content}
        
        # Process through scene processor
        processed_content = self.scene_processor.process_scene_content(selected_branch.narrative_content)
        
        return {
            "scene": processed_content["scene"],
            "narrative_analysis": processed_content.get("narrative_analysis", ""),
            "raw_content": selected_branch.narrative_content,
            "quantum_branch_id": selected_branch.branch_id
        }
    
    def _create_superposition_summary(self) -> str:
        """Create summary of current quantum superposition state."""
        if not self.quantum_tree:
            return "No quantum exploration active"
        
        summary_lines = [
            "=== QUANTUM NARRATIVE SUPERPOSITION ===",
            f"Active Branches: {len(self.quantum_tree.active_branches)}",
            f"Exploration Depth: {max(b.depth_level for b in self.quantum_tree.active_branches.values())}",
            "",
            "Branch Possibilities:"
        ]
        
        # Sort branches by quality
        sorted_branches = sorted(
            self.quantum_tree.active_branches.values(),
            key=lambda b: b.calculate_overall_quality(),
            reverse=True
        )
        
        for i, branch in enumerate(sorted_branches[:5]):  # Top 5 branches
            quality = branch.calculate_overall_quality()
            summary_lines.append(
                f"{i+1}. {branch.divergence_point} (Quality: {quality:.2f})"
            )
            summary_lines.append(
                f"   Preview: {branch.narrative_content[:100]}..."
            )
            summary_lines.append("")
        
        summary_lines.extend([
            "=== COLLAPSE REQUIRED FOR FINAL SCENE ===",
            "Use force_collapse=True to select final narrative path"
        ])
        
        return "\n".join(summary_lines)
    
    def _get_alternative_paths_summary(self) -> List[Dict[str, Any]]:
        """Get summary of alternative narrative paths."""
        if not self.quantum_tree:
            return []
        
        alternatives = []
        for branch_id, branch in self.quantum_tree.active_branches.items():
            alternatives.append({
                "branch_id": branch_id,
                "divergence_point": branch.divergence_point,
                "divergence_type": branch.divergence_type,
                "quality_score": branch.calculate_overall_quality(),
                "content_preview": branch.narrative_content[:150] + "..." if len(branch.narrative_content) > 150 else branch.narrative_content,
                "depth_level": branch.depth_level,
                "exploration_notes": branch.exploration_notes[-1] if branch.exploration_notes else ""
            })
        
        # Sort by quality
        alternatives.sort(key=lambda x: x["quality_score"], reverse=True)
        
        return alternatives
    
    def _generate_standard_scene_with_metadata(self,
                                             requirements: SceneRequirements,
                                             progress_callback: Optional[Callable[[Dict[str, Any]], None]]) -> Dict[str, Any]:
        """Generate scene using standard method with quantum metadata."""
        if progress_callback:
            progress_callback({
                "phase": "standard_generation",
                "message": "Generating scene using standard linear method"
            })
        
        # Use parent class method
        standard_result = self.generate_scene(requirements, progress_callback=progress_callback)
        
        # Add quantum metadata indicating no exploration
        standard_result["quantum_metadata"] = {
            "exploration_mode": "disabled",
            "timeline_state": "linear",
            "branches_explored": 1,
            "exploration_summary": {"mode": "standard_generation"}
        }
        
        return standard_result
    
    def _analyze_final_narrative(self, branch: NarrativeQuantumState) -> str:
        """Analyze final narrative for metadata."""
        analysis_lines = [
            f"Quantum Branch Analysis (ID: {branch.branch_id})",
            f"Divergence: {branch.divergence_point}",
            f"Type: {branch.divergence_type}",
            f"Depth: {branch.depth_level}",
            f"Quality Score: {branch.calculate_overall_quality():.3f}"
        ]
        
        if branch.exploration_notes:
            analysis_lines.append(f"Exploration Notes: {'; '.join(branch.exploration_notes[-3:])}")
        
        return "\n".join(analysis_lines)
    
    def _extract_character_development(self, branch: NarrativeQuantumState) -> Dict[str, Any]:
        """Extract character development from quantum branch."""
        development = {}
        
        for char_id, char_state in branch.character_states.items():
            development[char_id] = {
                "emotional_journey": char_state.get("emotional_state", "unknown"),
                "character_growth": char_state.get("character_growth", "no specific growth noted"),
                "psychological_state": char_state.get("psychological_state", "normal"),
                "decision_rationale": char_state.get("decision_rationale", "no major decisions")
            }
        
        return development
    
    def _extract_thematic_elements(self, branch: NarrativeQuantumState) -> Dict[str, Any]:
        """Extract thematic elements from quantum branch."""
        return {
            "dominant_theme": branch.world_state.get("dominant_theme", "not specified"),
            "thematic_tension": branch.world_state.get("thematic_tension", "not specified"),
            "philosophical_stance": branch.world_state.get("philosophical_stance", "not specified"),
            "thematic_development": branch.world_state.get("thematic_development", "not specified"),
            "alignment_score": branch.thematic_alignment
        }
    
    def get_quantum_visualization_data(self) -> Optional[Dict[str, Any]]:
        """Get data for visualizing quantum narrative tree."""
        if not self.quantum_tree:
            return None
        
        return self.quantum_tree.export_tree_visualization()
    
    def collapse_quantum_state(self, 
                               trigger_reason: str = "manual_collapse") -> Optional[Dict[str, Any]]:
        """Manually collapse quantum state to single path."""
        if not self.quantum_tree:
            return None
        
        # Create manual trigger
        manual_trigger = CollapseTrigger(
            trigger_type=CollapseTriggerType.HUMAN_DECISION,
            urgency=1.0,
            scope="immediate",
            condition="manual_collapse_requested",
            reason=trigger_reason
        )
        
        # Collapse
        selected_branch = self.quantum_tree.collapse_to_path(manual_trigger)
        
        return {
            "selected_branch_id": selected_branch.branch_id,
            "final_content": selected_branch.narrative_content,
            "collapse_reason": trigger_reason,
            "quality_score": selected_branch.calculate_overall_quality(),
            "exploration_summary": self.quantum_tree.get_exploration_summary()
        }