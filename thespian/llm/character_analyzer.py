"""
Character analyzer module for tracking and developing characters across scenes.
"""

from typing import Dict, Any, List, Optional, Callable, Union, Set
from pydantic import BaseModel, Field, ConfigDict
import logging
import json
import re

from thespian.llm.enhanced_memory import EnhancedCharacterProfile, EnhancedTheatricalMemory

logger = logging.getLogger(__name__)

class CharacterReference(BaseModel):
    """Character reference detected in a scene."""
    
    name: str
    mention_count: int = 0
    dialogue_lines: int = 0
    actions: List[str] = Field(default_factory=list)
    emotions: List[str] = Field(default_factory=list)
    relations: Dict[str, List[str]] = Field(default_factory=dict)  # Other character -> interactions
    importance: float = 0.0  # 0.0-1.0 scale of character importance in scene


class SceneCharacterAnalysis(BaseModel):
    """Analysis of character presence and development in a scene."""
    
    scene_id: str
    character_references: Dict[str, CharacterReference] = Field(default_factory=dict)
    primary_characters: List[str] = Field(default_factory=list)
    secondary_characters: List[str] = Field(default_factory=list)
    relationships_developed: List[Dict[str, Any]] = Field(default_factory=list)
    character_arcs_advanced: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    

class CharacterTracker(BaseModel):
    """Tracks characters and their development across scenes."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    memory: EnhancedTheatricalMemory
    character_references: Dict[str, Dict[str, CharacterReference]] = Field(default_factory=dict)  # scene_id -> char_name -> reference
    scene_analyses: Dict[str, SceneCharacterAnalysis] = Field(default_factory=dict)
    
    def analyze_scene_characters(
        self, 
        scene_id: str, 
        scene_content: str,
        llm_invoke_func: Callable
    ) -> SceneCharacterAnalysis:
        """
        Analyze character presence and development in a scene.
        
        Args:
            scene_id: Unique identifier for the scene
            scene_content: Content of the scene to analyze
            llm_invoke_func: Function to invoke the LLM for analysis
            
        Returns:
            SceneCharacterAnalysis: Analysis of character presence in the scene
        """
        # First do a basic text analysis to extract character names
        character_names = self._extract_character_names(scene_content)
        
        # Then use LLM for deeper analysis
        character_analysis = self._analyze_characters_with_llm(
            scene_id, scene_content, character_names, llm_invoke_func
        )
        
        # Store the analysis
        self.scene_analyses[scene_id] = character_analysis
        
        # Update character references
        if scene_id not in self.character_references:
            self.character_references[scene_id] = {}
            
        self.character_references[scene_id] = {
            char.name: char for char in character_analysis.character_references.values()
        }
        
        # Update character profiles in memory
        self._update_character_profiles(scene_id, character_analysis, scene_content, llm_invoke_func)
        
        return character_analysis
    
    def _extract_character_names(self, scene_content: str) -> List[str]:
        """Extract character names from scene content using regex patterns."""
        # Pattern for character dialogue format: CHARACTER NAME: dialogue
        dialogue_pattern = r'([A-Z][A-Z\s]+):'
        
        # Pattern for character in stage directions: (CHARACTER NAME action)
        direction_pattern = r'\(([A-Z][A-Z\s]+)\s'
        
        # Combine matches from both patterns
        dialogue_matches = re.findall(dialogue_pattern, scene_content)
        direction_matches = re.findall(direction_pattern, scene_content)
        
        # Combine and deduplicate
        all_matches = dialogue_matches + direction_matches
        character_names = list(set([name.strip() for name in all_matches if len(name.strip()) > 1]))
        
        return character_names
    
    def _analyze_characters_with_llm(
        self,
        scene_id: str,
        scene_content: str,
        character_names: List[str],
        llm_invoke_func: Callable
    ) -> SceneCharacterAnalysis:
        """Use LLM to perform deeper character analysis."""
        # Get existing character profiles
        existing_profiles = {}
        for char_name in character_names:
            char_id = char_name.lower().replace(" ", "_")
            profile = self.memory.get_character_profile(char_id)
            if profile:
                existing_profiles[char_name] = {
                    "background": profile.background,
                    "current_arc": profile.development_arc[-1].description if profile.development_arc else "Not started",
                    "current_emotion": profile.get_current_emotional_state().emotion if profile.get_current_emotional_state() else "Unknown"
                }
            else:
                existing_profiles[char_name] = {"background": "Unknown", "current_arc": "Not started", "current_emotion": "Unknown"}
        
        # Create prompt for LLM analysis
        prompt = f"""Analyze the characters in this theatrical scene.

SCENE CONTENT:
{scene_content}

DETECTED CHARACTERS:
{', '.join(character_names)}

EXISTING CHARACTER PROFILES:
{json.dumps(existing_profiles, indent=2)}

ANALYSIS INSTRUCTIONS:
1. For each character, analyze their presence and development in the scene
2. Identify primary and secondary characters
3. Identify relationship developments between characters
4. Identify advancement in character arcs
5. Analyze emotional states and changes

Format your response as JSON with these keys:
- "character_references": A dictionary mapping character names to their analysis
  - Each character analysis should include: mention_count, dialogue_lines, actions, emotions, relations, importance (0.0-1.0)
- "primary_characters": List of primary character names
- "secondary_characters": List of secondary character names
- "relationships_developed": List of relationship developments with character pairs and descriptions
- "character_arcs_advanced": Dictionary mapping character names to arc developments
"""
        
        # Invoke LLM for analysis
        response = llm_invoke_func(prompt)
        response_text = str(response.content if hasattr(response, "content") else response)
        
        # Extract JSON data
        try:
            data = json.loads(response_text)
            
            # Convert to CharacterReference objects
            character_refs = {}
            for char_name, char_data in data.get("character_references", {}).items():
                character_refs[char_name] = CharacterReference(
                    name=char_name,
                    mention_count=char_data.get("mention_count", 0),
                    dialogue_lines=char_data.get("dialogue_lines", 0),
                    actions=char_data.get("actions", []),
                    emotions=char_data.get("emotions", []),
                    relations=char_data.get("relations", {}),
                    importance=char_data.get("importance", 0.0)
                )
            
            # Create scene analysis
            analysis = SceneCharacterAnalysis(
                scene_id=scene_id,
                character_references=character_refs,
                primary_characters=data.get("primary_characters", []),
                secondary_characters=data.get("secondary_characters", []),
                relationships_developed=data.get("relationships_developed", []),
                character_arcs_advanced=data.get("character_arcs_advanced", {})
            )
            
            return analysis
            
        except json.JSONDecodeError:
            logger.error("Failed to decode JSON from character LLM analysis")
            # Return a basic analysis if LLM fails
            char_refs = {
                name: CharacterReference(name=name, mention_count=1) 
                for name in character_names
            }
            return SceneCharacterAnalysis(
                scene_id=scene_id,
                character_references=char_refs,
                primary_characters=character_names[:2] if len(character_names) > 1 else character_names,
                secondary_characters=character_names[2:] if len(character_names) > 2 else []
            )
    
    def _update_character_profiles(
        self,
        scene_id: str,
        analysis: SceneCharacterAnalysis,
        scene_content: str,
        llm_invoke_func: Callable
    ) -> None:
        """Update character profiles based on scene analysis."""
        # Process each character in the analysis
        for char_name, char_ref in analysis.character_references.items():
            # Convert name to ID format
            char_id = char_name.lower().replace(" ", "_")
            
            # Get or create profile
            profile = self.memory.get_character_profile(char_id)
            if not profile:
                # Create new profile if character doesn't exist
                profile = self._create_character_profile(char_id, char_name, scene_content, llm_invoke_func)
                if not profile:
                    continue
            
            # Update profile with scene analysis
            arc_advanced = analysis.character_arcs_advanced.get(char_name, {})
            if arc_advanced:
                profile.add_arc_point(
                    stage=arc_advanced.get("stage", "development"),
                    description=arc_advanced.get("description", "Character developed in this scene"),
                    scene_id=scene_id,
                    trigger=arc_advanced.get("trigger", "Scene events")
                )
            
            # Add emotional state if found
            if char_ref.emotions:
                primary_emotion = char_ref.emotions[0]
                profile.add_emotional_state(
                    emotion=primary_emotion,
                    cause="Scene events",
                    intensity=char_ref.importance,
                    scene_id=scene_id
                )
            
            # Add relationship developments
            for rel_dev in analysis.relationships_developed:
                if rel_dev.get("character1") == char_name:
                    other_char = rel_dev.get("character2", "")
                    change = rel_dev.get("description", "")
                    status = rel_dev.get("status", "")
                    
                    if other_char and change and status:
                        profile.update_relationship(
                            other_character=other_char,
                            status=status,
                            change=change,
                            scene_id=scene_id
                        )
            
            # Save updated profile
            self.memory.update_character_profile(char_id, profile)
    
    def _create_character_profile(
        self,
        char_id: str,
        char_name: str,
        scene_content: str,
        llm_invoke_func: Callable
    ) -> Optional[EnhancedCharacterProfile]:
        """Create a new character profile based on scene content."""
        # Create prompt for character profile generation
        prompt = f"""Create a character profile for {char_name} based on this scene.

SCENE CONTENT:
{scene_content}

ANALYSIS INSTRUCTIONS:
1. Extract background information for {char_name}
2. Identify motivations and goals
3. Identify key traits and qualities
4. Identify relationships with other characters
5. Identify fears, desires, and values

Format your response as JSON with these keys:
- "name": Full character name
- "background": Character background and history
- "motivations": List of character motivations
- "goals": List of character goals
- "traits": List of character traits
- "relationships": Dictionary mapping other character names to relationship descriptions
- "fears": List of character fears
- "desires": List of character desires
- "values": List of character values
- "strengths": List of character strengths
- "flaws": List of character flaws
"""
        
        # Invoke LLM for profile generation
        try:
            response = llm_invoke_func(prompt)
            response_text = str(response.content if hasattr(response, "content") else response)
            
            # Extract JSON data
            data = json.loads(response_text)
            
            # Create profile
            profile = EnhancedCharacterProfile(
                id=char_id,
                name=data.get("name", char_name),
                background=data.get("background", "Unknown"),
                motivations=data.get("motivations", []),
                goals=data.get("goals", []),
                conflicts=[],  # Not included in profile generation
                relationships=data.get("relationships", {}),
                fears=data.get("fears", []),
                desires=data.get("desires", []),
                values=data.get("values", []),
                strengths=data.get("strengths", []),
                flaws=data.get("flaws", [])
            )
            
            return profile
            
        except (json.JSONDecodeError, Exception) as e:
            logger.error(f"Failed to create character profile for {char_name}: {str(e)}")
            return None
    
    def get_character_summary(self, char_id: str) -> Dict[str, Any]:
        """Get a summary of a character's development across all scenes."""
        profile = self.memory.get_character_profile(char_id)
        if not profile:
            return {"error": f"Character profile not found for {char_id}"}
        
        # Collect scene presence
        scene_presence = []
        for scene_id, char_refs in self.character_references.items():
            if profile.name in char_refs:
                ref = char_refs[profile.name]
                scene_presence.append({
                    "scene_id": scene_id,
                    "importance": ref.importance,
                    "dialogue_lines": ref.dialogue_lines,
                    "primary_emotions": ref.emotions[:2] if ref.emotions else []
                })
        
        # Get arc summary
        arc_summary = profile.get_arc_summary()
        
        # Get relationship summary
        relationship_summary = {}
        for other_char, status in profile.relationships.items():
            history = profile.get_relationship_history_with(other_char)
            relationship_summary[other_char] = {
                "current_status": status,
                "history": [h.dict() for h in history]
            }
        
        # Get emotional journey
        emotional_journey = [
            {
                "scene_id": state.scene_id,
                "emotion": state.emotion,
                "cause": state.cause,
                "intensity": state.intensity
            }
            for state in profile.emotional_states
        ]
        
        return {
            "id": profile.id,
            "name": profile.name,
            "background": profile.background,
            "current_arc": arc_summary,
            "scene_presence": scene_presence,
            "relationships": relationship_summary,
            "emotional_journey": emotional_journey,
            "psychological_profile": {
                "fears": profile.fears,
                "desires": profile.desires,
                "values": profile.values,
                "strengths": profile.strengths,
                "flaws": profile.flaws
            },
            "key_experiences": [exp.dict() for exp in profile.key_experiences]
        }
    
    def get_all_character_ids(self) -> List[str]:
        """Get IDs of all characters in memory."""
        return list(self.memory.character_profiles.keys())
    
    def get_scene_character_summary(self, scene_id: str) -> Dict[str, Any]:
        """Get a summary of characters in a specific scene."""
        if scene_id not in self.scene_analyses:
            return {"error": f"No analysis found for scene {scene_id}"}
        
        analysis = self.scene_analyses[scene_id]
        
        return {
            "scene_id": scene_id,
            "primary_characters": analysis.primary_characters,
            "secondary_characters": analysis.secondary_characters,
            "character_details": {
                name: {
                    "importance": ref.importance,
                    "dialogue_lines": ref.dialogue_lines,
                    "emotions": ref.emotions,
                    "actions": ref.actions[:3]  # Limit to top 3 actions
                }
                for name, ref in analysis.character_references.items()
            },
            "relationship_developments": analysis.relationships_developed,
            "character_arcs_advanced": analysis.character_arcs_advanced
        }