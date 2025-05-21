"""
Enhanced memory system for theatrical productions with better character and narrative tracking.
"""

from typing import Dict, Any, List, Optional, Union, Set
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
import logging
import json
import os
from pathlib import Path

from thespian.llm.theatrical_memory import TheatricalMemory, CharacterProfile, StoryOutline

logger = logging.getLogger(__name__)

class CharacterArcPoint(BaseModel):
    """A point in a character's development arc."""
    
    stage: str = Field(..., description="The stage of development (e.g., 'introduction', 'transformation')")
    description: str = Field(..., description="Description of the character at this stage")
    scene_id: str = Field(..., description="ID of the scene where this development occurred")
    trigger: str = Field(..., description="What triggered this development")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class EmotionalState(BaseModel):
    """An emotional state experienced by a character."""
    
    emotion: str = Field(..., description="The primary emotion felt")
    cause: str = Field(..., description="What caused this emotion")
    intensity: float = Field(default=0.5, ge=0.0, le=1.0, description="Intensity of the emotion (0.0-1.0)")
    scene_id: str = Field(..., description="ID of the scene where this emotion occurred")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class RelationshipChange(BaseModel):
    """A change in a character's relationship with another character."""
    
    other_character: str = Field(..., description="Name of the other character")
    status: str = Field(..., description="Current relationship status")
    change: str = Field(..., description="How the relationship changed")
    scene_id: str = Field(..., description="ID of the scene where the change occurred")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class KeyExperience(BaseModel):
    """A key experience in a character's life."""
    
    description: str = Field(..., description="Description of the experience")
    impact: str = Field(..., description="Impact on the character")
    scene_id: Optional[str] = Field(None, description="ID of the scene where this occurred (None if backstory)")
    is_backstory: bool = Field(default=False, description="Whether this is backstory or occurred in the story")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class EnhancedCharacterProfile(CharacterProfile):
    """Enhanced character profile with evolution tracking."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    # Evolution tracking
    development_arc: List[CharacterArcPoint] = Field(default_factory=list)
    emotional_states: List[EmotionalState] = Field(default_factory=list)
    belief_changes: List[Dict[str, Any]] = Field(default_factory=list)
    relationship_developments: Dict[str, List[RelationshipChange]] = Field(default_factory=dict)
    
    # Memory tracking
    key_experiences: List[KeyExperience] = Field(default_factory=list)
    recurring_patterns: List[Dict[str, Any]] = Field(default_factory=dict)
    evolution_trigger_scenes: List[str] = Field(default_factory=list)
    
    # Psychological attributes
    fears: List[str] = Field(default_factory=list)
    desires: List[str] = Field(default_factory=list)
    flaws: List[str] = Field(default_factory=list)
    strengths: List[str] = Field(default_factory=list)
    values: List[str] = Field(default_factory=list)
    
    def add_arc_point(self, stage: str, description: str, scene_id: str, trigger: str) -> None:
        """Add a development arc point."""
        arc_point = CharacterArcPoint(
            stage=stage,
            description=description,
            scene_id=scene_id,
            trigger=trigger
        )
        self.development_arc.append(arc_point)
        self.evolution_trigger_scenes.append(scene_id)
        
    def add_emotional_state(self, emotion: str, cause: str, intensity: float, scene_id: str) -> None:
        """Add an emotional state point."""
        state = EmotionalState(
            emotion=emotion,
            cause=cause,
            intensity=intensity,
            scene_id=scene_id
        )
        self.emotional_states.append(state)
        
    def update_relationship(self, other_character: str, status: str, change: str, scene_id: str) -> None:
        """Update a relationship status."""
        if other_character not in self.relationship_developments:
            self.relationship_developments[other_character] = []
            
        change = RelationshipChange(
            other_character=other_character,
            status=status,
            change=change,
            scene_id=scene_id
        )
        self.relationship_developments[other_character].append(change)
        
        # Update main relationship status
        self.relationships[other_character] = status
        
    def add_key_experience(self, description: str, impact: str, scene_id: Optional[str] = None, is_backstory: bool = False) -> None:
        """Add a key experience."""
        experience = KeyExperience(
            description=description,
            impact=impact,
            scene_id=scene_id,
            is_backstory=is_backstory
        )
        self.key_experiences.append(experience)
        
    def add_belief_change(self, old_belief: str, new_belief: str, cause: str, scene_id: str) -> None:
        """Add a belief change."""
        self.belief_changes.append({
            "old_belief": old_belief,
            "new_belief": new_belief,
            "cause": cause,
            "scene_id": scene_id,
            "timestamp": datetime.now().isoformat()
        })
        
    def get_current_emotional_state(self) -> Optional[EmotionalState]:
        """Get the character's current emotional state."""
        if not self.emotional_states:
            return None
        return self.emotional_states[-1]
    
    def get_relationship_with(self, other_character: str) -> Optional[str]:
        """Get the current relationship status with another character."""
        return self.relationships.get(other_character)
    
    def get_relationship_history_with(self, other_character: str) -> List[RelationshipChange]:
        """Get the history of relationship changes with another character."""
        return self.relationship_developments.get(other_character, [])
    
    def get_arc_summary(self) -> Dict[str, Any]:
        """Get a summary of the character's development arc."""
        if not self.development_arc:
            return {"status": "not_started", "summary": "Character development has not yet begun."}
        
        current_stage = self.development_arc[-1].stage
        stages = [point.stage for point in self.development_arc]
        
        return {
            "status": "in_progress",
            "current_stage": current_stage,
            "stages_completed": stages,
            "summary": self.development_arc[-1].description
        }


class PlotPoint(BaseModel):
    """A significant point in the plot."""
    
    description: str = Field(..., description="Description of the plot point")
    significance: str = Field(..., description="Significance to the overall story")
    scene_id: str = Field(..., description="ID of the scene where this occurred")
    characters_involved: List[str] = Field(default_factory=list, description="Characters involved in this plot point")
    resolution_status: str = Field(default="unresolved", description="Status of this plot point's resolution")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class ThematicDevelopment(BaseModel):
    """Development of a thematic element."""
    
    theme: str = Field(..., description="The theme being developed")
    development: str = Field(..., description="How the theme is developed")
    scene_id: str = Field(..., description="ID of the scene where this occurred")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class CausalConnection(BaseModel):
    """A cause-effect relationship between events."""
    
    cause: str = Field(..., description="The cause")
    effect: str = Field(..., description="The effect")
    cause_scene_id: str = Field(..., description="ID of the scene containing the cause")
    effect_scene_id: Optional[str] = Field(None, description="ID of the scene containing the effect")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class ForeshadowingElement(BaseModel):
    """A foreshadowing element and its payoff."""
    
    foreshadowing: str = Field(..., description="The foreshadowing element")
    payoff: str = Field(..., description="The payoff for the foreshadowing")
    foreshadow_scene_id: str = Field(..., description="ID of the scene containing the foreshadowing")
    payoff_scene_id: Optional[str] = Field(None, description="ID of the scene containing the payoff")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class NarrativeContinuityTracker(BaseModel):
    """Tracks narrative continuity across scenes and acts."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    plot_points: List[PlotPoint] = Field(default_factory=list)
    thematic_developments: Dict[str, List[ThematicDevelopment]] = Field(default_factory=dict)
    causal_chains: List[CausalConnection] = Field(default_factory=list)
    foreshadowing_elements: List[ForeshadowingElement] = Field(default_factory=list)
    scene_connections: Dict[str, List[str]] = Field(default_factory=dict)
    
    def add_plot_point(self, description: str, significance: str, scene_id: str, characters_involved: List[str]) -> None:
        """Add a plot point to the continuity tracker."""
        plot_point = PlotPoint(
            description=description,
            significance=significance,
            scene_id=scene_id,
            characters_involved=characters_involved
        )
        self.plot_points.append(plot_point)
        
    def add_thematic_development(self, theme: str, development: str, scene_id: str) -> None:
        """Add a thematic development to the continuity tracker."""
        if theme not in self.thematic_developments:
            self.thematic_developments[theme] = []
            
        thematic_dev = ThematicDevelopment(
            theme=theme,
            development=development,
            scene_id=scene_id
        )
        self.thematic_developments[theme].append(thematic_dev)
        
    def add_causal_connection(self, cause: str, effect: str, cause_scene_id: str, effect_scene_id: Optional[str] = None) -> None:
        """Add a cause-effect relationship between scenes."""
        connection = CausalConnection(
            cause=cause,
            effect=effect,
            cause_scene_id=cause_scene_id,
            effect_scene_id=effect_scene_id
        )
        self.causal_chains.append(connection)
        
        # Update scene connections
        if cause_scene_id not in self.scene_connections:
            self.scene_connections[cause_scene_id] = []
            
        if effect_scene_id:
            self.scene_connections[cause_scene_id].append(effect_scene_id)
        
    def add_foreshadowing(self, foreshadowing: str, payoff: str, foreshadow_scene_id: str, payoff_scene_id: Optional[str] = None) -> None:
        """Add a foreshadowing element to the continuity tracker."""
        element = ForeshadowingElement(
            foreshadowing=foreshadowing,
            payoff=payoff,
            foreshadow_scene_id=foreshadow_scene_id,
            payoff_scene_id=payoff_scene_id
        )
        self.foreshadowing_elements.append(element)
        
    def update_foreshadowing_payoff(self, foreshadowing: str, payoff_scene_id: str) -> bool:
        """Update a foreshadowing element with its payoff scene."""
        for element in self.foreshadowing_elements:
            if element.foreshadowing == foreshadowing and not element.payoff_scene_id:
                element.payoff_scene_id = payoff_scene_id
                return True
        return False
    
    def get_related_scenes(self, scene_id: str) -> List[Dict[str, Any]]:
        """Get all scenes related to the given scene."""
        related_scenes = []
        
        # Check causal connections
        for chain in self.causal_chains:
            if chain.cause_scene_id == scene_id:
                if chain.effect_scene_id:
                    related_scenes.append({
                        "relationship": "causes",
                        "scene_id": chain.effect_scene_id,
                        "description": f"Causes: {chain.effect}"
                    })
            elif chain.effect_scene_id == scene_id:
                related_scenes.append({
                    "relationship": "caused_by",
                    "scene_id": chain.cause_scene_id,
                    "description": f"Caused by: {chain.cause}"
                })
                
        # Check foreshadowing
        for element in self.foreshadowing_elements:
            if element.foreshadow_scene_id == scene_id:
                if element.payoff_scene_id:
                    related_scenes.append({
                        "relationship": "foreshadows",
                        "scene_id": element.payoff_scene_id,
                        "description": f"Foreshadows: {element.payoff}"
                    })
            elif element.payoff_scene_id == scene_id:
                related_scenes.append({
                    "relationship": "payoff_of",
                    "scene_id": element.foreshadow_scene_id,
                    "description": f"Payoff of: {element.foreshadowing}"
                })
                
        return related_scenes
    
    def get_unresolved_plot_points(self) -> List[PlotPoint]:
        """Get all unresolved plot points."""
        return [point for point in self.plot_points if point.resolution_status == "unresolved"]
    
    def get_pending_foreshadowing(self) -> List[ForeshadowingElement]:
        """Get all foreshadowing elements without payoffs."""
        return [element for element in self.foreshadowing_elements if not element.payoff_scene_id]
    
    def get_character_involvement(self, character_name: str) -> List[PlotPoint]:
        """Get all plot points involving a character."""
        return [point for point in self.plot_points if character_name in point.characters_involved]
    
    def get_theme_development(self, theme: str) -> List[ThematicDevelopment]:
        """Get the development of a specific theme."""
        return self.thematic_developments.get(theme, [])


class EnhancedTheatricalMemory(TheatricalMemory):
    """Enhanced memory system with better character and narrative tracking."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    character_profiles: Dict[str, EnhancedCharacterProfile] = Field(default_factory=dict)
    continuity_tracker: NarrativeContinuityTracker = Field(default_factory=NarrativeContinuityTracker)
    story_arcs: Dict[str, List[Dict[str, Any]]] = Field(default_factory=dict)
    scene_analysis: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    character_db_path: Optional[str] = Field(default=None)
    
    def __init__(self, **data):
        """Initialize the memory system."""
        super().__init__(**data)
        self.continuity_tracker = NarrativeContinuityTracker()
        
        # If using the default file path, convert to enhanced profiles
        if self.db_path and os.path.exists(self.db_path):
            self._upgrade_profiles()
            
    def _upgrade_profiles(self) -> None:
        """Upgrade existing basic profiles to enhanced profiles."""
        for char_id, profile in self.character_profiles.items():
            if not isinstance(profile, EnhancedCharacterProfile):
                enhanced_profile = EnhancedCharacterProfile(
                    id=profile.id,
                    name=profile.name,
                    background=profile.background,
                    relationships=profile.relationships,
                    goals=profile.goals,
                    conflicts=profile.conflicts,
                    motivations=profile.motivations,
                    development_arc=[]
                )
                self.character_profiles[char_id] = enhanced_profile
    
    def update_character_profile(self, char_id: str, profile: Union[CharacterProfile, Dict[str, Any]]) -> None:
        """Update a character's profile in memory."""
        if isinstance(profile, dict):
            # Convert dict to EnhancedCharacterProfile if needed
            if char_id in self.character_profiles:
                # Update existing profile
                existing_profile = self.character_profiles[char_id]
                if isinstance(existing_profile, EnhancedCharacterProfile):
                    for key, value in profile.items():
                        setattr(existing_profile, key, value)
                else:
                    # Convert basic profile to enhanced
                    enhanced_profile = EnhancedCharacterProfile(**profile)
                    self.character_profiles[char_id] = enhanced_profile
            else:
                # Create new enhanced profile
                self.character_profiles[char_id] = EnhancedCharacterProfile(**profile)
        elif isinstance(profile, CharacterProfile):
            # Upgrade basic profile to enhanced if needed
            if not isinstance(profile, EnhancedCharacterProfile):
                enhanced_profile = EnhancedCharacterProfile(
                    id=profile.id,
                    name=profile.name,
                    background=profile.background,
                    relationships=profile.relationships,
                    goals=profile.goals,
                    conflicts=profile.conflicts,
                    motivations=profile.motivations,
                    development_arc=[]
                )
                self.character_profiles[char_id] = enhanced_profile
            else:
                self.character_profiles[char_id] = profile
        
        # Save to disk if path provided
        if self.db_path:
            self._save_profiles()
    
    def get_character_profile(self, char_id: str) -> Optional[EnhancedCharacterProfile]:
        """Get a character's profile from memory."""
        profile = self.character_profiles.get(char_id)
        if profile and not isinstance(profile, EnhancedCharacterProfile):
            # Upgrade on the fly if needed
            enhanced_profile = EnhancedCharacterProfile(
                id=profile.id,
                name=profile.name,
                background=profile.background,
                relationships=profile.relationships,
                goals=profile.goals,
                conflicts=profile.conflicts,
                motivations=profile.motivations,
                development_arc=[]
            )
            self.character_profiles[char_id] = enhanced_profile
            return enhanced_profile
        return profile
    
    def update_character_from_scene(self, char_id: str, scene_id: str, scene_content: str, llm_invoke_func: callable) -> None:
        """Update a character's profile based on a scene."""
        profile = self.get_character_profile(char_id)
        if not profile:
            logger.warning(f"Character profile not found for {char_id}")
            return
        
        # Create prompt for character analysis
        prompt = f"""Analyze how the character {profile.name} has developed in this scene.
        
        SCENE CONTENT:
        {scene_content}
        
        CURRENT CHARACTER STATE:
        Name: {profile.name}
        Background: {profile.background}
        Current Arc Stage: {profile.development_arc[-1].stage if profile.development_arc else "Not started"}
        Current Arc Description: {profile.development_arc[-1].description if profile.development_arc else "No development yet"}
        Current Emotional State: {profile.get_current_emotional_state().emotion if profile.get_current_emotional_state() else "Unknown"}
        
        ANALYSIS INSTRUCTIONS:
        1. Identify any character development for {profile.name}
        2. Detect emotional state changes
        3. Find relationship developments with other characters
        4. Identify new beliefs or values
        5. Detect any key experiences
        6. Identify recurring patterns
        
        Format your response as JSON with these keys:
        - "arc_development": {"stage": "stage_name", "description": "description", "trigger": "what_caused_it"}
        - "emotional_state": {"emotion": "emotion_name", "cause": "what_caused_it", "intensity": 0.0-1.0}
        - "relationship_changes": [{"other_character": "name", "status": "status", "change": "description"}]
        - "belief_changes": [{"old_belief": "description", "new_belief": "description", "cause": "what_caused_it"}]
        - "key_experiences": [{"description": "description", "impact": "impact"}]
        - "recurring_patterns": [{"pattern": "description", "significance": "significance"}]
        """
        
        # Invoke LLM for analysis
        response = llm_invoke_func(prompt)
        response_text = str(response.content if hasattr(response, "content") else response)
        
        # Extract JSON data
        try:
            data = json.loads(response_text)
            
            # Update character profile
            if "arc_development" in data:
                arc_dev = data["arc_development"]
                profile.add_arc_point(
                    stage=arc_dev.get("stage", "unknown"),
                    description=arc_dev.get("description", ""),
                    scene_id=scene_id,
                    trigger=arc_dev.get("trigger", "")
                )
                
            if "emotional_state" in data:
                emo_state = data["emotional_state"]
                profile.add_emotional_state(
                    emotion=emo_state.get("emotion", ""),
                    cause=emo_state.get("cause", ""),
                    intensity=emo_state.get("intensity", 0.5),
                    scene_id=scene_id
                )
                
            if "relationship_changes" in data:
                for rel_change in data["relationship_changes"]:
                    profile.update_relationship(
                        other_character=rel_change.get("other_character", ""),
                        status=rel_change.get("status", ""),
                        change=rel_change.get("change", ""),
                        scene_id=scene_id
                    )
                    
            if "belief_changes" in data:
                for belief_change in data["belief_changes"]:
                    profile.add_belief_change(
                        old_belief=belief_change.get("old_belief", ""),
                        new_belief=belief_change.get("new_belief", ""),
                        cause=belief_change.get("cause", ""),
                        scene_id=scene_id
                    )
                    
            if "key_experiences" in data:
                for exp in data["key_experiences"]:
                    profile.add_key_experience(
                        description=exp.get("description", ""),
                        impact=exp.get("impact", ""),
                        scene_id=scene_id
                    )
            
            # Save updated profile
            self.update_character_profile(char_id, profile)
            
        except json.JSONDecodeError:
            logger.error("Failed to decode JSON from character analysis")
        except Exception as e:
            logger.error(f"Error updating character from scene: {str(e)}")
    
    def update_narrative_from_scene(self, scene_id: str, scene_content: str, llm_invoke_func: callable) -> None:
        """Update narrative continuity based on a scene."""
        # Create prompt for narrative analysis
        prompt = f"""Analyze the narrative elements in this scene.
        
        SCENE CONTENT:
        {scene_content}
        
        ANALYSIS INSTRUCTIONS:
        1. Identify major plot points and their significance
        2. Identify thematic developments
        3. Identify cause-effect relationships
        4. Identify foreshadowing elements
        5. Identify any plot resolutions
        
        Format your response as JSON with these keys:
        - "plot_points": [{"description": "description", "significance": "significance", "characters_involved": ["name1", "name2"]}]
        - "thematic_developments": [{"theme": "theme_name", "development": "how_it_developed"}]
        - "causal_connections": [{"cause": "cause_description", "effect": "effect_description"}]
        - "foreshadowing": [{"foreshadowing": "element_description", "payoff": "expected_payoff"}]
        - "plot_resolutions": [{"plot_point": "plot_point_description", "resolution": "resolution_description"}]
        """
        
        # Invoke LLM for analysis
        response = llm_invoke_func(prompt)
        response_text = str(response.content if hasattr(response, "content") else response)
        
        # Extract JSON data
        try:
            data = json.loads(response_text)
            
            # Update narrative tracker
            if "plot_points" in data:
                for point in data["plot_points"]:
                    self.continuity_tracker.add_plot_point(
                        description=point.get("description", ""),
                        significance=point.get("significance", ""),
                        scene_id=scene_id,
                        characters_involved=point.get("characters_involved", [])
                    )
                    
            if "thematic_developments" in data:
                for dev in data["thematic_developments"]:
                    self.continuity_tracker.add_thematic_development(
                        theme=dev.get("theme", ""),
                        development=dev.get("development", ""),
                        scene_id=scene_id
                    )
                    
            if "causal_connections" in data:
                for conn in data["causal_connections"]:
                    self.continuity_tracker.add_causal_connection(
                        cause=conn.get("cause", ""),
                        effect=conn.get("effect", ""),
                        cause_scene_id=scene_id
                    )
                    
            if "foreshadowing" in data:
                for fore in data["foreshadowing"]:
                    self.continuity_tracker.add_foreshadowing(
                        foreshadowing=fore.get("foreshadowing", ""),
                        payoff=fore.get("payoff", ""),
                        foreshadow_scene_id=scene_id
                    )
                    
            if "plot_resolutions" in data:
                # Update resolution status for matching plot points
                for res in data["plot_resolutions"]:
                    plot_desc = res.get("plot_point", "")
                    for plot_point in self.continuity_tracker.plot_points:
                        if plot_point.description == plot_desc:
                            plot_point.resolution_status = "resolved"
            
            # Save analysis to scene analysis dict
            self.scene_analysis[scene_id] = data
            
        except json.JSONDecodeError:
            logger.error("Failed to decode JSON from narrative analysis")
        except Exception as e:
            logger.error(f"Error updating narrative from scene: {str(e)}")
    
    def get_narrative_continuity(self) -> NarrativeContinuityTracker:
        """Get the narrative continuity tracker."""
        return self.continuity_tracker
    
    def get_scene_context(self, act_number: int, scene_number: int) -> Dict[str, Any]:
        """Get contextual information for a scene."""
        # Gather relevant context based on act and scene number
        character_states = {}
        for char_id, profile in self.character_profiles.items():
            arc_summary = profile.get_arc_summary()
            emotional_state = profile.get_current_emotional_state()
            
            character_states[char_id] = {
                "name": profile.name,
                "arc_status": arc_summary["status"],
                "current_stage": arc_summary.get("current_stage", ""),
                "current_emotion": emotional_state.emotion if emotional_state else "",
                "relationships": profile.relationships
            }
        
        # Get relevant plot points
        unresolved_plots = self.continuity_tracker.get_unresolved_plot_points()
        pending_foreshadowing = self.continuity_tracker.get_pending_foreshadowing()
        
        # Get thematic developments
        themes = {}
        for theme, developments in self.continuity_tracker.thematic_developments.items():
            if developments:
                themes[theme] = developments[-1].development
        
        return {
            "act_number": act_number,
            "scene_number": scene_number,
            "character_states": character_states,
            "unresolved_plots": [point.dict() for point in unresolved_plots],
            "pending_foreshadowing": [element.dict() for element in pending_foreshadowing],
            "thematic_status": themes
        }
    
    def store_character_analysis(self, scene_id: str, character_name: str, analysis: Dict[str, Any]) -> None:
        """Store character analysis for a scene."""
        if scene_id not in self.scene_analysis:
            self.scene_analysis[scene_id] = {}
            
        if "character_analysis" not in self.scene_analysis[scene_id]:
            self.scene_analysis[scene_id]["character_analysis"] = {}
            
        self.scene_analysis[scene_id]["character_analysis"][character_name] = analysis
    
    def store_transition_analysis(self, act_number: int, analysis: str) -> None:
        """Store analysis of transition between acts."""
        if "act_transitions" not in self.story_arcs:
            self.story_arcs["act_transitions"] = []
            
        self.story_arcs["act_transitions"].append({
            "from_act": act_number,
            "to_act": act_number + 1,
            "analysis": analysis,
            "timestamp": datetime.now().isoformat()
        })