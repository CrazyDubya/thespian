"""
Memory-enhanced playwright with character tracking and narrative continuity.
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
from thespian.llm.enhanced_playwright import EnhancedPlaywright
from thespian.llm.enhanced_memory import EnhancedTheatricalMemory, EnhancedCharacterProfile
from thespian.llm.character_analyzer import CharacterTracker, SceneCharacterAnalysis
from thespian.llm.playwright import SceneRequirements
from thespian.config.enhanced_prompts import ENHANCED_PROMPT_TEMPLATES

logger = logging.getLogger(__name__)

class MemoryEnhancedPlaywright(EnhancedPlaywright):
    """Playwright with enhanced memory and character tracking."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    enhanced_memory: EnhancedTheatricalMemory = Field(...)
    character_tracker: Optional[CharacterTracker] = None
    track_characters: bool = Field(default=True)
    track_narrative: bool = Field(default=True)
    memory_integration_level: int = Field(default=2, ge=1, le=3)  # 1=basic, 2=standard, 3=deep
    
    def __init__(self, **data: Any) -> None:
        """Initialize the memory-enhanced playwright."""
        # Ensure enhanced memory is provided
        if "memory" in data and not isinstance(data["memory"], EnhancedTheatricalMemory):
            if "enhanced_memory" not in data:
                # Convert standard memory to enhanced
                data["enhanced_memory"] = EnhancedTheatricalMemory(
                    db_path=getattr(data["memory"], "db_path", None)
                )
                
                # Copy existing character profiles
                if hasattr(data["memory"], "character_profiles"):
                    for char_id, profile in data["memory"].character_profiles.items():
                        data["enhanced_memory"].update_character_profile(char_id, profile)
                
                # Use enhanced memory as the base memory
                data["memory"] = data["enhanced_memory"]
        
        super().__init__(**data)
        
        # Initialize character tracker if not provided
        if not self.character_tracker and self.enhanced_memory:
            self.character_tracker = CharacterTracker(memory=self.enhanced_memory)
    
    def generate_scene(
        self, 
        requirements: SceneRequirements, 
        previous_scene: Optional[str] = None,
        previous_feedback: Optional[Dict[str, Any]] = None,
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
        use_refinement: bool = True
    ) -> Dict[str, Any]:
        """
        Generate a scene with memory enhancement.
        
        This extends the standard generation with memory context and character tracking.
        """
        # Enhance requirements with memory context
        if self.memory_integration_level >= 2:
            enhanced_requirements = self._enhance_requirements_with_memory(requirements)
        else:
            enhanced_requirements = requirements
            
        # Generate scene with the enhanced playwright's method
        result = super().generate_scene(
            requirements=enhanced_requirements,
            previous_scene=previous_scene,
            previous_feedback=previous_feedback,
            progress_callback=progress_callback,
            use_refinement=use_refinement
        )
        
        # Update memory from generated scene
        if self.track_characters or self.track_narrative:
            scene_id = result.get("scene_id", f"scene_{int(time.time())}")
            scene_content = result.get("scene", "")
            
            if progress_callback:
                progress_callback({
                    "phase": "memory_update",
                    "current_step": 1,
                    "total_steps": 1,
                    "message": "Updating memory with scene information"
                })
                
            self._update_memory_from_scene(scene_id, scene_content)
            
            # Add memory context to the result
            result["memory_context"] = self._get_memory_context(requirements.act_number, requirements.scene_number)
        
        return result
    
    def _enhance_requirements_with_memory(self, requirements: SceneRequirements) -> SceneRequirements:
        """Enhance scene requirements with memory context."""
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
                    plot_directives.append(f"- {plot['description']}")
            
            # Add pending foreshadowing
            if memory_context.get("pending_foreshadowing") and len(memory_context["pending_foreshadowing"]) > 0:
                plot_directives.append("\nForeshadowing elements to pay off:")
                for i, foreshadow in enumerate(memory_context["pending_foreshadowing"][:2]):  # Top 2 foreshadowings
                    plot_directives.append(f"- {foreshadow['foreshadowing']} → {foreshadow['payoff']}")
            
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
    
    def _update_memory_from_scene(self, scene_id: str, scene_content: str) -> None:
        """Update memory based on generated scene content."""
        if not scene_content:
            return
            
        # Update character tracking
        if self.track_characters and self.character_tracker:
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
        if self.track_narrative and self.enhanced_memory:
            try:
                self.enhanced_memory.update_narrative_from_scene(
                    scene_id,
                    scene_content,
                    lambda prompt: self.get_llm().invoke(prompt)
                )
                logger.info(f"Narrative analysis completed for scene {scene_id}")
            except Exception as e:
                logger.error(f"Error in narrative analysis: {str(e)}")
    
    def _get_memory_context(self, act_number: int, scene_number: int) -> Dict[str, Any]:
        """Get memory context for scene generation."""
        if not self.enhanced_memory:
            return {}
            
        try:
            return self.enhanced_memory.get_scene_context(act_number, scene_number)
        except Exception as e:
            logger.error(f"Error getting memory context: {str(e)}")
            return {}
    
    def get_character_summary(self, char_id: str) -> Dict[str, Any]:
        """Get a summary of a character's development."""
        if not self.character_tracker:
            return {"error": "Character tracker not initialized"}
            
        return self.character_tracker.get_character_summary(char_id)
    
    def get_all_characters(self) -> List[Dict[str, Any]]:
        """Get summaries of all characters."""
        if not self.character_tracker:
            return []
            
        char_ids = self.character_tracker.get_all_character_ids()
        return [self.get_character_summary(char_id) for char_id in char_ids]
    
    def get_scene_character_summary(self, scene_id: str) -> Dict[str, Any]:
        """Get a summary of characters in a specific scene."""
        if not self.character_tracker:
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
        result = self.generate_scene(enhanced_requirements, progress_callback=progress_callback)
        
        # Add character focus information to result
        result["character_focus"] = {
            "character_id": focus_character,
            "character_name": profile.name,
            "development_goals": character_development
        }
        
        return result
    
    def generate_character_arc_scene(
        self,
        act_number: int,
        scene_number: int,
        character_id: str,
        arc_stage: str,
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ) -> Dict[str, Any]:
        """
        Generate a scene focused on a specific character arc stage.
        
        Args:
            act_number: Act number for the scene
            scene_number: Scene number within the act
            character_id: ID of the character to focus on
            arc_stage: Stage of character development (e.g., "call_to_adventure", "refusal", "mentor")
            progress_callback: Optional callback for reporting progress
            
        Returns:
            Dict containing the generated scene and metadata
        """
        # Get character profile
        profile = self.enhanced_memory.get_character_profile(character_id)
        if not profile:
            raise ValueError(f"Character profile not found for {character_id}")
        
        # Define character arc stages and their descriptions
        arc_stages = {
            "ordinary_world": {
                "description": "The character's normal life before the adventure begins",
                "development": "Shows the character's baseline, everyday existence"
            },
            "call_to_adventure": {
                "description": "The character receives a challenge or call to change",
                "development": "Presents a challenge, opportunity, or problem that disrupts the status quo"
            },
            "refusal": {
                "description": "The character initially refuses or is reluctant to change",
                "development": "Shows resistance, fear, or uncertainty about the new path"
            },
            "meeting_mentor": {
                "description": "The character encounters a mentor figure",
                "development": "Introduces guidance, wisdom, or a catalyst that helps the character move forward"
            },
            "crossing_threshold": {
                "description": "The character commits to the adventure or change",
                "development": "Shows the decision point where the character commits to a new course"
            },
            "tests_allies_enemies": {
                "description": "The character faces initial challenges and meets allies and enemies",
                "development": "Develops the character through challenges and relationship building"
            },
            "approach": {
                "description": "The character prepares for the major challenge",
                "development": "Shows preparation, planning, and increased determination"
            },
            "ordeal": {
                "description": "The character faces their greatest challenge",
                "development": "Creates a moment of crisis that forces growth or revelation"
            },
            "reward": {
                "description": "The character achieves their goal, but challenges remain",
                "development": "Shows achievement, relief, or celebration, but with complications"
            },
            "road_back": {
                "description": "The character must deal with the consequences of their actions",
                "development": "Shows the character dealing with fallout and attempting to return to normality"
            },
            "resurrection": {
                "description": "The character faces a final test applying what they've learned",
                "development": "Creates a final crisis that requires the character to demonstrate growth"
            },
            "return": {
                "description": "The character returns to their ordinary world, transformed",
                "development": "Shows how the character has changed and the new equilibrium"
            },
            "catalyst": {
                "description": "An event that upsets the status quo of the character's life",
                "development": "Creates disruption that forces the character to respond"
            },
            "debate": {
                "description": "The character questions whether to pursue the new goal",
                "development": "Shows internal conflict about whether to change"
            },
            "breakthrough": {
                "description": "The character commits to a new path or goal",
                "development": "Creates a moment of decision and commitment"
            },
            "midpoint": {
                "description": "The character has a major revelation or change of perspective",
                "development": "Shows a shift in understanding that alters the character's approach"
            },
            "fall": {
                "description": "The character experiences failure or setback",
                "development": "Creates doubt, fear, or disillusionment"
            },
            "darknight": {
                "description": "The character reaches their lowest point",
                "development": "Shows the character at their most vulnerable or hopeless"
            },
            "climax": {
                "description": "The character makes their final push toward their goal",
                "development": "Shows the culmination of the character's journey"
            },
            "resolution": {
                "description": "The character establishes a new equilibrium",
                "development": "Shows how the character and their world have changed"
            }
        }
        
        # Get arc stage information
        stage_info = arc_stages.get(arc_stage, {
            "description": f"Stage: {arc_stage}",
            "development": f"Development for {arc_stage} stage"
        })
        
        # Create base requirements from story outline
        if not self.story_outline:
            raise ValueError("story_outline is not initialized")
            
        current_act = self.story_outline.get_act_outline(act_number)
        if not current_act:
            raise ValueError(f"No outline found for Act {act_number}")
            
        # Default scene requirements
        default_requirements = SceneRequirements(
            setting="Scene setting",
            characters=[profile.name.upper()],
            props=[],
            lighting="Scene lighting",
            sound="Scene sound effects",
            style=self.story_outline.style if hasattr(self.story_outline, "style") else "Drama",
            period=self.story_outline.period if hasattr(self.story_outline, "period") else "Present day",
            target_audience=self.story_outline.target_audience if hasattr(self.story_outline, "target_audience") else "General audience",
            act_number=act_number,
            scene_number=scene_number
        )
        
        # Enhance with character arc focus
        char_arc_directives = f"""CHARACTER ARC DEVELOPMENT:
Character: {profile.name}
Arc Stage: {arc_stage.replace('_', ' ').title()}
Description: {stage_info['description']}
Development Focus: {stage_info['development']}

Requirements:
1. Show {profile.name} experiencing the "{arc_stage.replace('_', ' ').title()}" stage of their character arc
2. Create a scene that clearly demonstrates {stage_info['development']}
3. Show the character's internal and external reactions to this stage
4. Establish clear emotional stakes related to this development
5. Set up the next stage in the character's arc
"""
        
        character_development = {
            "aspect": arc_stage.replace('_', ' '),
            "moment_type": arc_stage.replace('_', ' '),
            "reveal_aspect": "character transformation",
            "conflict_type": "transformative conflict"
        }
        
        # Generate scene with character arc focus
        return self.create_scene_with_character_focus(
            default_requirements,
            character_id,
            character_development,
            progress_callback
        )