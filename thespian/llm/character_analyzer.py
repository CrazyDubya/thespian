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
        
        # Filter out technical cues that are not character names
        technical_cues = {
            "SOUND", "MUSIC", "LIGHTS", "LIGHTING", "SET", "SCENE", "ACT", 
            "CURTAIN", "STAGE", "BACKDROP", "PROPS", "COSTUME", "MAKEUP",
            "EFFECTS", "SFX", "BGM", "FADE", "CUT", "ENTER", "EXIT",
            "BLACKOUT", "SPOTLIGHT", "VOICEOVER", "NARRATOR", "END",
            "OPENING", "CLOSING", "INTERMISSION", "PAUSE", "CONTINUE"
        }
        
        character_names = []
        for name in all_matches:
            clean_name = name.strip()
            if len(clean_name) > 1 and clean_name.upper() not in technical_cues:
                character_names.append(clean_name)
        
        # Deduplicate while preserving order
        character_names = list(dict.fromkeys(character_names))
        
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
                    "current_arc": getattr(profile, 'development_arc', [])[-1].description if getattr(profile, 'development_arc', []) and isinstance(getattr(profile, 'development_arc', []), list) else "Not started",
                    "current_emotion": profile.get_current_emotional_state().emotion if profile.get_current_emotional_state() else "Unknown"
                }
            else:
                existing_profiles[char_name] = {"background": "Unknown", "current_arc": "Not started", "current_emotion": "Unknown"}
        
        # Create prompt for LLM analysis
        prompt = f"""You are a theatrical character analyst. Analyze the characters in this scene and return ONLY valid JSON.

SCENE CONTENT:
{scene_content}

DETECTED CHARACTERS: {', '.join(character_names)}

EXISTING CHARACTER PROFILES:
{json.dumps(existing_profiles, indent=2)}

CRITICAL INSTRUCTIONS:
1. Return ONLY valid JSON - no explanatory text
2. Use EXACT character names from the detected characters list
3. For character_arcs_advanced, each character entry MUST be an object with the specified fields
4. All arrays must contain strings, not objects
5. All numeric values must be numbers, not strings

JSON STRUCTURE REQUIREMENTS:
- character_references: object where each key is a character name
- primary_characters: array of character name strings
- secondary_characters: array of character name strings  
- relationships_developed: array of objects with "characters" and "development" fields
- character_arcs_advanced: object where each character name maps to an object with required fields

RESPOND WITH THIS EXACT JSON FORMAT:
{{
  "character_references": {{
    "{character_names[0] if character_names else 'CHARACTER_NAME'}": {{
      "mention_count": 1,
      "dialogue_lines": 1,
      "actions": ["speaks", "moves"],
      "emotions": ["determined", "curious"],
      "relations": {{}},
      "importance": 0.8
    }}
  }},
  "primary_characters": {json.dumps(character_names[:2] if len(character_names) >= 2 else character_names)},
  "secondary_characters": {json.dumps(character_names[2:] if len(character_names) > 2 else [])},
  "relationships_developed": [
    {{"characters": {json.dumps(character_names[:2] if len(character_names) >= 2 else character_names)}, "development": "characters interact meaningfully"}}
  ],
  "character_arcs_advanced": {{
    "{character_names[0] if character_names else 'CHARACTER_NAME'}": {{
      "arc_development": "character shows growth through scene interactions",
      "emotional_journey": "displays range of emotions appropriate to situation",
      "growth_areas": ["character development", "relationship building"],
      "conflicts_faced": ["internal struggle", "external challenge"]
    }}
  }}
}}

CRITICAL: Return ONLY this JSON structure with your analysis. NO other text."""
        
        # Try LLM analysis with self-correction on failure
        max_retries = 3  # Increase retries
        last_error = ""
        for attempt in range(max_retries + 1):
            if attempt > 0:
                # Add corrective feedback for retry
                correction_prompt = f"""CORRECTION NEEDED: Your previous response failed JSON validation.

Previous response that failed:
{response_text[:1000]}...

Error: {last_error}

Please provide ONLY valid JSON with NO additional text. The response must be a single JSON object with exactly these keys:
- "character_references": object with character names as keys
- "primary_characters": array of strings
- "secondary_characters": array of strings  
- "relationships_developed": array of objects
- "character_arcs_advanced": object with character names as keys, each value must be an OBJECT not a string

Example of correct character_arcs_advanced format:
"character_arcs_advanced": {{
  "LYRA": {{
    "arc_development": "description text",
    "emotional_journey": "emotional changes", 
    "growth_areas": ["area1", "area2"],
    "conflicts_faced": ["conflict1", "conflict2"]
  }}
}}

{prompt}"""
                response = llm_invoke_func(correction_prompt)
            else:
                response = llm_invoke_func(prompt)
                
            response_text = str(response.content if hasattr(response, "content") else response)
            
            # Extract JSON data
            try:
                # Try to extract JSON from the response if it's wrapped in text
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                if json_start != -1 and json_end > json_start:
                    json_text = response_text[json_start:json_end]
                    data = json.loads(json_text)
                else:
                    # If no JSON braces found, try the whole response
                    data = json.loads(response_text)
                break  # Success, exit retry loop
                
            except (json.JSONDecodeError, ValueError) as e:
                last_error = str(e)
                logger.warning(f"JSON parsing attempt {attempt + 1} failed: {last_error}")
                logger.warning(f"Response text was: {response_text[:500]}...")
                if attempt == max_retries:
                    # Final attempt failed, use fallback
                    logger.error(f"All JSON parsing attempts failed for character analysis")
                    logger.error(f"Final failed response: {response_text}")
                    raise
                continue
            
            # Convert to CharacterReference objects with better validation
            character_refs = {}
            for char_name, char_data in data.get("character_references", {}).items():
                # Ensure char_data is a dictionary
                if not isinstance(char_data, dict):
                    logger.warning(f"Character data for {char_name} is not a dict, creating default")
                    char_data = {}
                
                # Validate and sanitize actions field
                actions = char_data.get("actions", [])
                if not isinstance(actions, list):
                    if actions is None:
                        actions = []
                    elif isinstance(actions, str):
                        actions = [actions]  # Convert single string to list
                    else:
                        actions = []
                
                # Validate and sanitize emotions field
                emotions = char_data.get("emotions", [])
                if not isinstance(emotions, list):
                    if emotions is None:
                        emotions = []
                    elif isinstance(emotions, str):
                        emotions = [emotions]  # Convert single string to list
                    else:
                        emotions = []
                
                # Validate relations field
                relations = char_data.get("relations", {})
                if not isinstance(relations, dict):
                    relations = {}
                
                character_refs[char_name] = CharacterReference(
                    name=char_name,
                    mention_count=char_data.get("mention_count", 0),
                    dialogue_lines=char_data.get("dialogue_lines", 0),
                    actions=actions,
                    emotions=emotions,
                    relations=relations,
                    importance=char_data.get("importance", 0.0)
                )
            
            # Validate and sanitize character_arcs_advanced
            character_arcs_raw = data.get("character_arcs_advanced", {})
            character_arcs_advanced = {}
            
            if isinstance(character_arcs_raw, dict):
                for char_name, arc_data in character_arcs_raw.items():
                    if isinstance(arc_data, dict):
                        character_arcs_advanced[char_name] = arc_data
                    elif isinstance(arc_data, str):
                        # Convert string description to dictionary
                        character_arcs_advanced[char_name] = {
                            "arc_development": arc_data,
                            "emotional_journey": "Not specified",
                            "growth_areas": ["Character development"],
                            "conflicts_faced": ["Internal development"]
                        }
                    else:
                        logger.warning(f"Invalid arc data for {char_name}: {type(arc_data)}")
                        character_arcs_advanced[char_name] = {
                            "arc_development": "Character appears in scene",
                            "emotional_journey": "Not specified",
                            "growth_areas": [],
                            "conflicts_faced": []
                        }
            
            # Validate relationships_developed
            relationships_developed = data.get("relationships_developed", [])
            if not isinstance(relationships_developed, list):
                relationships_developed = []
            
            # Create scene analysis with validation error handling
            try:
                analysis = SceneCharacterAnalysis(
                    scene_id=scene_id,
                    character_references=character_refs,
                    primary_characters=data.get("primary_characters", []),
                    secondary_characters=data.get("secondary_characters", []),
                    relationships_developed=relationships_developed,
                    character_arcs_advanced=character_arcs_advanced
                )
                return analysis
                
            except Exception as validation_error:
                last_error = f"Validation error: {str(validation_error)}"
                logger.warning(f"Character analysis validation attempt {attempt + 1} failed: {last_error}")
                logger.warning(f"Data that failed validation: {json.dumps(data, indent=2) if 'data' in locals() else 'No data'}")
                logger.warning(f"character_arcs_advanced structure: {json.dumps(character_arcs_advanced, indent=2) if 'character_arcs_advanced' in locals() else 'Not created yet'}")
                if attempt == max_retries:
                    # Final attempt failed, use fallback
                    logger.error(f"All validation attempts failed for character analysis")
                    logger.error(f"Final validation error: {validation_error}")
                    raise
                continue
            
        # Final fallback - try with a minimal template that should always work
        logger.warning("All sophisticated attempts failed, trying minimal template")
        try:
            minimal_template = {
                "character_references": {
                    name: {
                        "mention_count": 1,
                        "dialogue_lines": 1,
                        "actions": ["appears"],
                        "emotions": ["neutral"],
                        "relations": {},
                        "importance": 0.5
                    } for name in character_names
                },
                "primary_characters": character_names[:2] if len(character_names) >= 2 else character_names,
                "secondary_characters": character_names[2:] if len(character_names) > 2 else [],
                "relationships_developed": [],
                "character_arcs_advanced": {
                    name: {
                        "arc_development": f"{name} appears in this scene",
                        "emotional_journey": "character participates in scene",
                        "growth_areas": ["scene participation"],
                        "conflicts_faced": ["none specific"]
                    } for name in character_names
                }
            }
            
            # Convert to CharacterReference objects
            character_refs = {}
            for char_name, char_data in minimal_template["character_references"].items():
                character_refs[char_name] = CharacterReference(
                    name=char_name,
                    mention_count=char_data["mention_count"],
                    dialogue_lines=char_data["dialogue_lines"],
                    actions=char_data["actions"],
                    emotions=char_data["emotions"],
                    relations=char_data["relations"],
                    importance=char_data["importance"]
                )
            
            return SceneCharacterAnalysis(
                scene_id=scene_id,
                character_references=character_refs,
                primary_characters=minimal_template["primary_characters"],
                secondary_characters=minimal_template["secondary_characters"],
                relationships_developed=minimal_template["relationships_developed"],
                character_arcs_advanced=minimal_template["character_arcs_advanced"]
            )
            
        except Exception as fallback_error:
            logger.error(f"Even minimal fallback failed: {fallback_error}")
            # Ultimate fallback - just basic character references
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