"""
Unit tests for enhanced agent methods.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from thespian.agents_enhanced import (
    EnhancedDirectorAgent,
    EnhancedCharacterActorAgent,
    EnhancedSetCostumeDesignAgent,
    EnhancedStageManagerAgent
)


class TestEnhancedDirectorAgent:
    """Test enhanced director agent methods."""
    
    @pytest.fixture
    def director(self):
        """Create a director agent with mocked LLM."""
        with patch('thespian.llm.manager.LLMManager') as mock_llm_manager:
            mock_llm = Mock()
            mock_llm_manager.return_value.llm = mock_llm
            agent = EnhancedDirectorAgent()
            agent.llm = mock_llm
            return agent
    
    def test_provide_scene_notes(self, director):
        """Test director provides comprehensive scene notes."""
        director.llm.generate.return_value = """
        {
            "pacing": "Build tension slowly through the first half, then accelerate",
            "tone": "Dark comedy with undertones of existential dread",
            "blocking_suggestions": [
                "Characters should maintain physical distance initially",
                "Gradual closing of space as conflict intensifies"
            ],
            "emotional_beats": [
                {"line": 10, "emotion": "suppressed anger"},
                {"line": 25, "emotion": "breaking point"},
                {"line": 40, "emotion": "bitter resignation"}
            ],
            "technical_notes": "Use lighting to create shadows that grow longer as scene progresses"
        }
        """
        
        scene = "A tense confrontation between two old friends"
        requirements = {"theme": "betrayal", "mood": "tense"}
        
        notes = director.provide_scene_notes(scene, requirements)
        
        # The method returns the parsed JSON, so check the actual structure
        assert isinstance(notes, dict)
        assert notes.get("pacing") == "Build tension slowly through the first half, then accelerate"
        assert notes.get("tone") == "Dark comedy with undertones of existential dread"
        assert isinstance(notes.get("blocking_suggestions"), list)
        assert len(notes.get("emotional_beats", [])) == 3
    
    def test_workshop_scene(self, director):
        """Test director workshops scene with actors."""
        director.llm.generate.return_value = """
        {
            "workshop_notes": "The scene needs more subtext in the dialogue",
            "character_dynamics": {
                "tension_points": ["The unspoken history", "Power imbalance"],
                "relationship_evolution": "From guarded politeness to open hostility"
            },
            "suggested_improvements": [
                "Add more pauses for dramatic effect",
                "Include physical business to show nervousness",
                "Layer in contradictory body language"
            ],
            "actor_feedback_integration": "Incorporated actor suggestions for more naturalistic dialogue"
        }
        """
        
        scene = "Two characters meeting after years apart"
        actors = [Mock(), Mock()]
        
        workshop_result = director.workshop_scene(scene, actors)
        
        assert isinstance(workshop_result, dict)
        assert workshop_result.get("workshop_notes") == "The scene needs more subtext in the dialogue"
        assert "character_dynamics" in workshop_result
        assert len(workshop_result.get("suggested_improvements", [])) == 3


class TestEnhancedCharacterActorAgent:
    """Test enhanced character actor agent methods."""
    
    @pytest.fixture
    def actor(self):
        """Create an actor agent with mocked LLM."""
        with patch('thespian.llm.manager.LLMManager') as mock_llm_manager:
            mock_llm = Mock()
            mock_llm_manager.return_value.llm = mock_llm
            agent = EnhancedCharacterActorAgent(
                character_name="Hamlet",
                character_data={"description": "The Prince of Denmark", "traits": ["melancholic", "intellectual"]}
            )
            agent.llm = mock_llm
            return agent
    
    def test_suggest_dialogue_improvements(self, actor):
        """Test actor suggests dialogue improvements."""
        actor.llm.generate.return_value = """
        [
            {
                "original": "I am sad about this.",
                "improved": "The weight of this sorrow threatens to unmake me.",
                "reasoning": "More poetic and character-appropriate language"
            },
            {
                "original": "Yes, I agree.",
                "improved": "Indeed... though agreement tastes of ash in my mouth.",
                "reasoning": "Adds complexity and internal conflict"
            }
        ]
        """
        
        scene = "Hamlet contemplates his situation"
        character_profile = {"traits": ["melancholic", "intellectual"]}
        
        suggestions = actor.suggest_dialogue_improvements(scene, character_profile)
        
        assert len(suggestions) == 2
        assert "improved" in suggestions[0]
        assert "reasoning" in suggestions[0]
    
    def test_validate_character_consistency(self, actor):
        """Test character consistency validation."""
        actor.llm.generate.return_value = """
        {
            "is_consistent": true,
            "consistency_score": 0.85,
            "inconsistencies": [
                {
                    "line": "I shall act swiftly!",
                    "issue": "Hamlet is typically indecisive",
                    "severity": "minor"
                }
            ],
            "character_growth": "Shows natural progression from paralysis to action",
            "suggestions": ["Add more internal hesitation before decisive moments"]
        }
        """
        
        scene = "Hamlet makes a decision"
        previous_scenes = ["Scene 1", "Scene 2"]
        
        validation = actor.validate_character_consistency(scene, previous_scenes)
        
        assert validation["is_consistent"] is True
        assert validation["consistency_score"] == 0.85
        assert len(validation["inconsistencies"]) == 1
    
    def test_develop_subtext(self, actor):
        """Test subtext development for dialogue."""
        actor.llm.generate.return_value = """
        {
            "surface_meaning": "Greeting an old friend",
            "subtext": "Testing whether they can still be trusted",
            "delivery_notes": "Slight pause before 'friend', emphasis on 'long'",
            "body_language": "Formal handshake instead of embrace, maintained eye contact",
            "internal_monologue": "Can I trust you after what happened?"
        }
        """
        
        dialogue_line = "Hello, old friend. It's been a long time."
        context = {"relationship": "former allies", "scene": "reunion"}
        
        subtext = actor.develop_subtext(dialogue_line, context)
        
        assert "subtext" in subtext
        assert "delivery_notes" in subtext
        assert "body_language" in subtext


class TestEnhancedSetCostumeDesignAgent:
    """Test enhanced set/costume design agent methods."""
    
    @pytest.fixture
    def designer(self):
        """Create a designer agent with mocked LLM."""
        with patch('thespian.llm.manager.LLMManager') as mock_llm_manager:
            mock_llm = Mock()
            mock_llm_manager.return_value.llm = mock_llm
            agent = EnhancedSetCostumeDesignAgent()
            agent.llm = mock_llm
            return agent
    
    def test_suggest_scene_elements(self, designer):
        """Test designer suggests scene elements."""
        designer.llm.generate.return_value = """
        {
            "set_pieces": [
                {
                    "item": "Weathered wooden desk",
                    "placement": "Stage right",
                    "significance": "Represents authority and age"
                },
                {
                    "item": "Cracked mirror",
                    "placement": "Upstage center",
                    "significance": "Fractured self-perception"
                }
            ],
            "costume_details": [
                {
                    "character": "Hamlet",
                    "elements": ["Disheveled black doublet", "Untied cravat"],
                    "symbolism": "Internal chaos manifested externally"
                }
            ],
            "color_palette": ["Deep blacks", "Muted grays", "Single splash of crimson"],
            "textures": ["Rough hewn wood", "Tarnished metal", "Heavy velvet"]
        }
        """
        
        scene = "Hamlet's private chamber"
        mood = "introspective melancholy"
        
        elements = designer.suggest_scene_elements(scene, mood)
        
        assert isinstance(elements, dict)
        assert len(elements.get("set_pieces", [])) == 2
        assert len(elements.get("costume_details", [])) == 1
        assert "color_palette" in elements
    
    def test_create_atmosphere_notes(self, designer):
        """Test atmosphere creation notes."""
        designer.llm.generate.return_value = """
        {
            "lighting_design": {
                "overall": "Chiaroscuro effect with deep shadows",
                "key_moments": [
                    {"cue": "Hamlet enters", "effect": "Single shaft of light from high window"},
                    {"cue": "Revelation", "effect": "Lightning flash through window"}
                ]
            },
            "sound_design": {
                "ambient": "Distant thunder, old house creaking",
                "effects": ["Clock chiming midnight", "Sudden silence before climax"]
            },
            "spatial_dynamics": "Vast empty space emphasizing isolation",
            "sensory_details": "Smell of old books and dust, cold draft from unseen source"
        }
        """
        
        scene_context = {"location": "castle", "time": "midnight", "mood": "ominous"}
        
        # Add the required emotional_arc parameter
        emotional_arc = "building tension"
        atmosphere = designer.create_atmosphere_notes(scene_context, emotional_arc)
        
        assert "lighting_design" in atmosphere
        assert "sound_design" in atmosphere
        assert len(atmosphere["lighting_design"]["key_moments"]) == 2


class TestEnhancedStageManagerAgent:
    """Test enhanced stage manager agent methods."""
    
    @pytest.fixture
    def stage_manager(self):
        """Create a stage manager agent with mocked LLM."""
        with patch('thespian.llm.manager.LLMManager') as mock_llm_manager:
            mock_llm = Mock()
            mock_llm_manager.return_value.llm = mock_llm
            agent = EnhancedStageManagerAgent()
            agent.llm = mock_llm
            return agent
    
    def test_check_continuity(self, stage_manager):
        """Test continuity checking."""
        stage_manager.llm.generate.return_value = """
        {
            "continuity_issues": [
                {
                    "type": "prop",
                    "issue": "Dagger appears in scene 3 but not established earlier",
                    "severity": "major",
                    "solution": "Add dagger to Hamlet's belt in scene 1"
                },
                {
                    "type": "costume",
                    "issue": "Ophelia's dress changes color between scenes",
                    "severity": "minor",
                    "solution": "Keep consistent white dress throughout act"
                }
            ],
            "timeline_consistency": true,
            "character_tracking": {
                "all_characters_accounted": true,
                "entrance_exit_issues": []
            }
        }
        """
        
        scenes = ["Scene 1", "Scene 2", "Scene 3"]
        
        # Add the required parameters
        previous_scenes = []  # Empty for first act
        production_bible = {"props": {}, "costumes": {}, "timeline": "linear"}
        continuity = stage_manager.check_continuity(scenes, previous_scenes, production_bible)
        
        assert len(continuity["continuity_issues"]) == 2
        assert continuity["timeline_consistency"] is True
        assert continuity["character_tracking"]["all_characters_accounted"] is True
    
    def test_track_technical_elements(self, stage_manager):
        """Test technical element tracking."""
        stage_manager.llm.generate.return_value = """
        {
            "lighting_cues": [
                {"cue_number": "LX1", "trigger": "Opening of scene", "effect": "Sunrise"},
                {"cue_number": "LX2", "trigger": "Hamlet's entrance", "effect": "Spotlight DSC"}
            ],
            "sound_cues": [
                {"cue_number": "SQ1", "trigger": "Pre-show", "effect": "Wind and rain"},
                {"cue_number": "SQ2", "trigger": "Ghost appears", "effect": "Ethereal music"}
            ],
            "prop_list": [
                {"item": "Letter", "scene": "2.1", "character": "Hamlet"},
                {"item": "Skull", "scene": "5.1", "character": "Gravedigger"}
            ],
            "scene_changes": [
                {"between": "1.1-1.2", "duration": "30 seconds", "elements": ["Remove throne", "Add garden bench"]}
            ],
            "technical_warnings": ["Fog machine needed for ghost scenes", "Quick change required for Polonius"]
        }
        """
        
        production_script = "Full Hamlet script"
        
        technical = stage_manager.track_technical_elements(production_script)
        
        assert isinstance(technical, dict)
        assert len(technical.get("lighting_cues", [])) == 2
        assert len(technical.get("sound_cues", [])) == 2
        assert len(technical.get("prop_list", [])) == 2
        assert "technical_warnings" in technical


def test_all_agents_have_enhanced_methods():
    """Verify all enhanced agents have required methods."""
    # Director
    assert hasattr(EnhancedDirectorAgent, 'provide_scene_notes')
    assert hasattr(EnhancedDirectorAgent, 'workshop_scene')
    
    # Actor
    assert hasattr(EnhancedCharacterActorAgent, 'suggest_dialogue_improvements')
    assert hasattr(EnhancedCharacterActorAgent, 'validate_character_consistency')
    assert hasattr(EnhancedCharacterActorAgent, 'develop_subtext')
    
    # Designer
    assert hasattr(EnhancedSetCostumeDesignAgent, 'suggest_scene_elements')
    assert hasattr(EnhancedSetCostumeDesignAgent, 'create_atmosphere_notes')
    
    # Stage Manager
    assert hasattr(EnhancedStageManagerAgent, 'check_continuity')
    assert hasattr(EnhancedStageManagerAgent, 'track_technical_elements')