"""
Collaborative playwright system that orchestrates enhanced agents working together.
"""

from typing import Dict, Any, List, Optional, Tuple
import json
from datetime import datetime
from pydantic import Field

from thespian.llm.playwright import EnhancedPlaywright
from thespian.agents_enhanced import (
    EnhancedDirectorAgent,
    EnhancedCharacterActorAgent,
    EnhancedSetCostumeDesignAgent,
    EnhancedStageManagerAgent
)
from thespian.llm.enhanced_memory import EnhancedTheatricalMemory


class CollaborativePlaywright(EnhancedPlaywright):
    """Enhanced playwright that coordinates agent collaboration for richer scene generation."""
    
    # Additional fields for collaborative features
    enable_pre_production: bool = True
    enable_workshops: bool = True
    iteration_limit: int = 3
    director: Optional[EnhancedDirectorAgent] = None
    designer: Optional[EnhancedSetCostumeDesignAgent] = None
    stage_manager: Optional[EnhancedStageManagerAgent] = None
    actors: Dict[str, EnhancedCharacterActorAgent] = Field(default_factory=dict)
    
    def __init__(
        self,
        memory: Optional[EnhancedTheatricalMemory] = None,
        enable_pre_production: bool = True,
        enable_workshops: bool = True,
        iteration_limit: int = 3,
        **kwargs
    ):
        """Initialize collaborative playwright with enhanced features.
        
        Args:
            memory: Enhanced theatrical memory system
            enable_pre_production: Whether to conduct pre-production meetings
            enable_workshops: Whether to workshop scenes with agents
            iteration_limit: Maximum iterations for scene refinement
        """
        # Import required components
        from thespian.llm.manager import LLMManager
        from thespian.llm.theatrical_advisors import AdvisorManager
        from thespian.llm.quality_control import TheatricalQualityControl
        from thespian.llm.theatrical_memory import TheatricalMemory
        
        # Set up required fields if not provided
        if 'name' not in kwargs:
            kwargs['name'] = 'CollaborativePlaywright'
        if 'llm_manager' not in kwargs:
            kwargs['llm_manager'] = LLMManager()
        if 'memory' not in kwargs:
            kwargs['memory'] = memory or EnhancedTheatricalMemory()
        if 'advisor_manager' not in kwargs:
            # AdvisorManager needs llm_manager and memory
            llm_mgr = kwargs.get('llm_manager', LLMManager())
            mem = kwargs.get('memory', memory or EnhancedTheatricalMemory())
            kwargs['advisor_manager'] = AdvisorManager(llm_manager=llm_mgr, memory=mem)
        if 'quality_control' not in kwargs:
            kwargs['quality_control'] = TheatricalQualityControl()
        
        super().__init__(**kwargs)
        
        # Override with enhanced memory if provided
        if memory:
            self.memory = memory
        
        self.enable_pre_production = enable_pre_production
        self.enable_workshops = enable_workshops
        self.iteration_limit = iteration_limit
        
        # Initialize enhanced agents
        self.director = EnhancedDirectorAgent()
        self.designer = EnhancedSetCostumeDesignAgent()
        self.stage_manager = EnhancedStageManagerAgent()
        self.actors: Dict[str, EnhancedCharacterActorAgent] = {}
    
    def _initialize_actors(self, characters: List[Dict[str, Any]]) -> None:
        """Initialize character actors for the production."""
        self.actors = {}
        for char in characters:
            if isinstance(char, dict) and 'name' in char:
                self.actors[char['name']] = EnhancedCharacterActorAgent(
                    character_name=char['name'],
                    character_data=char
                )
    
    def conduct_pre_production_meeting(
        self, 
        premise: str, 
        characters: List[Dict[str, Any]],
        themes: List[str]
    ) -> Dict[str, Any]:
        """Conduct a pre-production meeting with all agents.
        
        Returns production guidelines and creative vision.
        """
        print("\n🎭 Conducting Pre-Production Meeting...")
        
        meeting_prompt = f"""
        As the playwright, I'm gathering the creative team for our production.
        
        PREMISE: {premise}
        THEMES: {', '.join(themes)}
        CHARACTERS: {json.dumps(characters, indent=2)}
        
        Please provide your creative vision and requirements for this production.
        """
        
        # Get director's overall vision
        director_vision = self.director.provide_scene_notes(
            meeting_prompt,
            {
                "type": "pre_production",
                "themes": themes,
                "scope": "full_production"
            }
        )
        
        # Get designer's production concepts
        design_concept = self.designer.suggest_scene_elements(
            f"Full production based on: {premise}",
            "varied - from intimate to grand"
        )
        
        # Get stage manager's technical requirements
        technical_reqs = {
            "estimated_runtime": "2 hours with intermission",
            "scene_changes": "Plan for 8-10 distinct scenes",
            "special_requirements": ["Depends on director and designer vision"]
        }
        
        pre_production_notes = {
            "director_vision": director_vision,
            "design_concept": design_concept,
            "technical_requirements": technical_reqs,
            "collaborative_goals": [
                "Maintain thematic consistency throughout",
                "Develop rich character arcs",
                "Create dynamic staging and atmosphere",
                "Ensure smooth technical execution"
            ],
            "timestamp": datetime.now().isoformat()
        }
        
        # Store in memory
        self.memory.add_to_production_bible("pre_production_meeting", pre_production_notes)
        
        return pre_production_notes
    
    def workshop_scene(
        self,
        scene_content: str,
        scene_number: int,
        scene_metadata: Dict[str, Any]
    ) -> Tuple[str, Dict[str, Any]]:
        """Workshop a scene with all agents providing feedback.
        
        Returns refined scene and workshop notes.
        """
        print(f"\n🎬 Workshopping Scene {scene_number}...")
        
        # Get actors for this scene
        scene_characters = scene_metadata.get('characters', [])
        scene_actors = [
            self.actors.get(char) for char in scene_characters 
            if char in self.actors
        ]
        
        workshop_notes = {
            "scene_number": scene_number,
            "iterations": []
        }
        
        current_scene = scene_content
        
        for iteration in range(min(self.iteration_limit, 3)):
            print(f"  Iteration {iteration + 1}...")
            
            # Director workshops with actors
            director_feedback = {}
            if scene_actors:
                director_feedback = self.director.workshop_scene(
                    current_scene,
                    scene_actors
                )
            
            # Actors suggest improvements
            actor_suggestions = {}
            for char_name, actor in self.actors.items():
                if char_name in scene_characters:
                    suggestions = actor.suggest_dialogue_improvements(
                        current_scene,
                        actor.character_data
                    )
                    if suggestions:
                        actor_suggestions[char_name] = suggestions
            
            # Designer provides atmosphere notes
            atmosphere_notes = self.designer.create_atmosphere_notes(
                {
                    "location": scene_metadata.get('location', 'unspecified'),
                    "time": scene_metadata.get('time_of_day', 'day'),
                    "mood": scene_metadata.get('emotional_tone', 'neutral')
                },
                scene_metadata.get('emotional_arc', 'steady')
            )
            
            # Stage manager checks continuity
            previous_scenes = self.memory.get_all_scenes()[:scene_number - 1]
            continuity_check = {}
            if previous_scenes:
                continuity_check = self.stage_manager.check_continuity(
                    [current_scene],
                    [s['content'] for s in previous_scenes],
                    self.memory.production_bible
                )
            
            iteration_data = {
                "director_feedback": director_feedback,
                "actor_suggestions": actor_suggestions,
                "atmosphere_notes": atmosphere_notes,
                "continuity_check": continuity_check
            }
            workshop_notes["iterations"].append(iteration_data)
            
            # Synthesize feedback and refine scene
            if any([director_feedback, actor_suggestions, atmosphere_notes, continuity_check]):
                current_scene = self._refine_scene_with_feedback(
                    current_scene,
                    iteration_data,
                    scene_metadata
                )
            else:
                break  # No more feedback, scene is ready
        
        workshop_notes["final_version"] = current_scene
        workshop_notes["total_iterations"] = len(workshop_notes["iterations"])
        
        return current_scene, workshop_notes
    
    def _refine_scene_with_feedback(
        self,
        scene: str,
        feedback: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> str:
        """Refine scene based on agent feedback."""
        refinement_prompt = f"""
        Refine the following scene based on the collaborative feedback:
        
        CURRENT SCENE:
        {scene}
        
        DIRECTOR FEEDBACK:
        {json.dumps(feedback.get('director_feedback', {}), indent=2)}
        
        ACTOR SUGGESTIONS:
        {json.dumps(feedback.get('actor_suggestions', {}), indent=2)}
        
        ATMOSPHERE NOTES:
        {json.dumps(feedback.get('atmosphere_notes', {}), indent=2)}
        
        CONTINUITY ISSUES:
        {json.dumps(feedback.get('continuity_check', {}), indent=2)}
        
        Please revise the scene incorporating this feedback while maintaining the original intent.
        Make the dialogue more natural, add suggested atmosphere elements, and fix any continuity issues.
        Ensure the scene is rich, detailed, and at least 5000 characters long.
        """
        
        try:
            response = self.llm.generate(refinement_prompt)
            refined_scene = response.strip()
            
            # Ensure we got a substantial refinement
            if len(refined_scene) > len(scene) * 0.8:  # At least 80% of original length
                return refined_scene
            else:
                # Fallback: make targeted improvements
                return self._apply_targeted_improvements(scene, feedback)
                
        except Exception as e:
            print(f"  Error refining scene: {e}")
            return scene
    
    def _apply_targeted_improvements(
        self,
        scene: str,
        feedback: Dict[str, Any]
    ) -> str:
        """Apply specific improvements from feedback when full refinement fails."""
        improved_scene = scene
        
        # Apply actor dialogue suggestions
        actor_suggestions = feedback.get('actor_suggestions', {})
        for char_name, suggestions in actor_suggestions.items():
            if isinstance(suggestions, list):
                for suggestion in suggestions[:2]:  # Apply first 2 suggestions
                    if isinstance(suggestion, dict) and 'original' in suggestion and 'improved' in suggestion:
                        improved_scene = improved_scene.replace(
                            suggestion['original'],
                            suggestion['improved']
                        )
        
        # Add atmosphere elements as stage directions
        atmosphere = feedback.get('atmosphere_notes', {})
        if atmosphere and isinstance(atmosphere, dict):
            lighting = atmosphere.get('lighting_design', {})
            sound = atmosphere.get('sound_design', {})
            
            atmosphere_addition = "\n\n[ATMOSPHERE: "
            if lighting:
                atmosphere_addition += f"Lighting - {lighting.get('overall', 'standard')}. "
            if sound:
                atmosphere_addition += f"Sound - {sound.get('ambient', 'quiet')}."
            atmosphere_addition += "]\n\n"
            
            # Add at the beginning of the scene
            improved_scene = atmosphere_addition + improved_scene
        
        return improved_scene
    
    def generate_scene(
        self,
        act_number: int,
        scene_number: int,
        scene_guide: Dict[str, Any],
        previous_scenes: List[Dict[str, Any]] = None,
        word_count: int = 1500
    ) -> Dict[str, Any]:
        """Generate a scene with full agent collaboration.
        
        Overrides base method to add collaborative features.
        """
        # First, generate base scene using parent method
        base_scene = super().generate_scene(
            act_number=act_number,
            scene_number=scene_number,
            scene_guide=scene_guide,
            previous_scenes=previous_scenes,
            word_count=word_count
        )
        
        # Initialize actors if not already done
        if not self.actors and hasattr(self, 'story_outline'):
            characters = self.story_outline.get('characters', [])
            self._initialize_actors(characters)
        
        # Workshop the scene if enabled
        if self.enable_workshops and base_scene.get('content'):
            workshopped_content, workshop_notes = self.workshop_scene(
                base_scene['content'],
                scene_number,
                {
                    'location': scene_guide.get('location', 'unspecified'),
                    'time_of_day': scene_guide.get('time', 'day'),
                    'emotional_tone': scene_guide.get('emotional_tone', 'neutral'),
                    'emotional_arc': scene_guide.get('conflict', 'steady'),
                    'characters': scene_guide.get('characters', [])
                }
            )
            
            # Update scene with workshopped content
            base_scene['content'] = workshopped_content
            base_scene['workshop_notes'] = workshop_notes
            base_scene['workshop_iterations'] = workshop_notes.get('total_iterations', 0)
        
        # Add to memory with enhanced metadata
        if self.memory:
            self.memory.add_scene(
                scene_id=f"act_{act_number}_scene_{scene_number}",
                content=base_scene['content'],
                metadata={
                    **base_scene.get('metadata', {}),
                    'workshop_notes': base_scene.get('workshop_notes', {}),
                    'collaborative_generation': True
                }
            )
        
        return base_scene
    
    def generate_production(
        self,
        premise: str,
        themes: List[str] = None,
        num_acts: int = 2,
        scenes_per_act: int = 4,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate a full production with collaborative enhancement.
        
        Overrides base method to add pre-production and collaboration.
        """
        print("🎭 Starting Collaborative Production Generation...")
        
        # Generate initial story outline
        self.story_outline = self.create_story_outline(premise, themes)
        
        # Initialize actors
        self._initialize_actors(self.story_outline.get('characters', []))
        
        # Conduct pre-production meeting if enabled
        if self.enable_pre_production:
            pre_production = self.conduct_pre_production_meeting(
                premise,
                self.story_outline.get('characters', []),
                themes or []
            )
            self.memory.add_to_production_bible("pre_production", pre_production)
        
        # Generate production with base method (which now uses our enhanced generate_scene)
        production = super().generate_production(
            premise=premise,
            themes=themes,
            num_acts=num_acts,
            scenes_per_act=scenes_per_act,
            **kwargs
        )
        
        # Add collaborative metadata
        production['collaborative_features'] = {
            'pre_production_meeting': self.enable_pre_production,
            'scene_workshops': self.enable_workshops,
            'total_workshop_iterations': sum(
                scene.get('workshop_iterations', 0)
                for act in production.get('acts', [])
                for scene in act.get('scenes', [])
            ),
            'agents_involved': {
                'director': True,
                'designer': True,
                'stage_manager': True,
                'actors': list(self.actors.keys())
            }
        }
        
        return production