"""
Unit tests for scene length and detail enhancement.
"""

import pytest
from thespian.llm.detail_enhancer import (
    SceneDetailEnhancer,
    DetailLayer,
    EnhancementStrategy
)
from thespian.config.enhanced_prompts import (
    get_enhanced_scene_prompt,
    get_expansion_prompt,
    get_character_dialogue_prompt
)


class TestSceneDetailEnhancer:
    """Test the scene detail enhancement system."""
    
    @pytest.fixture
    def enhancer(self):
        """Create a detail enhancer instance."""
        return SceneDetailEnhancer(target_length=5000)
    
    @pytest.fixture
    def short_scene(self):
        """A short scene that needs enhancement."""
        return """
SCENE 1

SARAH: I can't do this anymore.

JOHN: What do you mean?

SARAH: You know exactly what I mean.

[SARAH exits]

JOHN: Wait!
"""
    
    @pytest.fixture
    def medium_scene(self):
        """A medium-length scene."""
        return """
ACT 1, SCENE 2

[The living room. Evening. SARAH stands by the window, looking out. JOHN enters from the kitchen.]

JOHN: We need to talk about this.

SARAH: There's nothing to talk about.

JOHN: Sarah, please. Just give me five minutes.

[SARAH turns to face him, arms crossed.]

SARAH: Five minutes won't change anything, John. Five years didn't change anything.

JOHN: That's not fair.

SARAH: Fair? You want to talk about fair?

[She laughs, but there's no humor in it.]

SARAH: I gave up everything for this. For us. And what did I get in return?

JOHN: I know I haven't been—

SARAH: (interrupting) Don't. Just don't.

[Long pause. They stand facing each other across the room.]

JOHN: So that's it then?

SARAH: That's it.

[SARAH exits. JOHN stands alone in the growing darkness.]
"""
    
    def test_analyze_scene_structure(self, enhancer, short_scene):
        """Test scene structure analysis."""
        analysis = enhancer.analyze_scene(short_scene)
        
        assert "current_length" in analysis
        assert "length_deficit" in analysis
        assert "structure" in analysis
        assert "dialogue_to_direction_ratio" in analysis
        
        # Check structure details
        structure = analysis["structure"]
        assert structure["character_count"] == 2
        assert "SARAH" in structure["character_names"]
        assert "JOHN" in structure["character_names"]
        assert structure["dialogue_lines"] > 0
    
    def test_length_deficit_calculation(self, enhancer, short_scene, medium_scene):
        """Test that length deficit is calculated correctly."""
        short_analysis = enhancer.analyze_scene(short_scene)
        medium_analysis = enhancer.analyze_scene(medium_scene)
        
        assert short_analysis["length_deficit"] > medium_analysis["length_deficit"]
        assert short_analysis["current_length"] < enhancer.target_length
    
    def test_dialogue_ratio_calculation(self, enhancer, short_scene):
        """Test dialogue to direction ratio calculation."""
        analysis = enhancer.analyze_scene(short_scene)
        ratio = analysis["dialogue_to_direction_ratio"]
        
        assert 0 <= ratio <= 1
        # Short scene has mostly dialogue
        assert ratio > 0.7
    
    def test_enhancement_opportunities(self, enhancer, short_scene):
        """Test identification of enhancement opportunities."""
        analysis = enhancer.analyze_scene(short_scene)
        opportunities = analysis["enhancement_opportunities"]
        
        assert "needs_more_stage_directions" in opportunities
        assert len(opportunities) > 0
    
    def test_enhance_scene_adds_content(self, enhancer, short_scene):
        """Test that enhance_scene increases content length."""
        original_length = len(short_scene)
        enhanced = enhancer.enhance_scene(short_scene)
        
        assert len(enhanced) > original_length
        # Should add substantial content
        assert len(enhanced) >= original_length * 1.5
    
    def test_enhance_preserves_original_dialogue(self, enhancer, short_scene):
        """Test that enhancement preserves original dialogue."""
        enhanced = enhancer.enhance_scene(short_scene)
        
        # Check that original dialogue is preserved
        assert "I can't do this anymore" in enhanced
        assert "What do you mean?" in enhanced
        assert "You know exactly what I mean" in enhanced
    
    def test_enhancement_strategies(self, enhancer):
        """Test that enhancement strategies are properly initialized."""
        strategies = enhancer.enhancement_strategies
        
        assert "subtext" in strategies
        assert "atmosphere" in strategies
        assert "character_business" in strategies
        assert "technical_elements" in strategies
        
        # Check strategy properties
        subtext_strategy = strategies["subtext"]
        assert subtext_strategy.name == "Subtext Enhancement"
        assert subtext_strategy.target_element == "dialogue"
        assert len(subtext_strategy.enhancement_prompts) > 0
    
    def test_detail_plan_creation(self, enhancer, short_scene):
        """Test creation of detail enhancement plan."""
        plan = enhancer.create_detail_plan(short_scene)
        
        assert len(plan) > 0
        assert all(isinstance(layer, DetailLayer) for layer in plan)
        
        # Check that high-priority items come first
        priorities = [layer.priority for layer in plan]
        assert priorities == sorted(priorities, reverse=True)
    
    def test_inject_subtext_layers(self, enhancer, medium_scene):
        """Test subtext injection."""
        enhanced = enhancer.inject_subtext_layers(medium_scene)
        
        # Should add subtext after key dialogue
        assert enhanced.count('[') > medium_scene.count('[')
        # Should preserve original content
        assert "There's nothing to talk about" in enhanced
    
    def test_expand_technical_elements(self, enhancer, medium_scene):
        """Test technical element expansion."""
        enhanced = enhancer.expand_technical_elements(medium_scene)
        
        # Should add lighting cues
        assert "LIGHTS:" in enhanced
        # Should add sound cues for entrances/exits
        assert "SOUND:" in enhanced or "enters" in enhanced.lower()
    
    def test_comprehensive_detail_generation(self, enhancer, short_scene):
        """Test comprehensive detail addition."""
        enhanced = enhancer._add_comprehensive_details(short_scene, enhancer.analyze_scene(short_scene))
        
        # Should be substantially longer
        assert len(enhanced) > len(short_scene) * 2
        # Should have opening atmosphere
        assert enhanced.startswith("[") or "[" in enhanced[:100]


class TestEnhancedPrompts:
    """Test the enhanced prompt generation."""
    
    def test_enhanced_scene_prompt_formatting(self):
        """Test that enhanced scene prompt is properly formatted."""
        prompt = get_enhanced_scene_prompt(word_count=1500, scene_context="A tense confrontation")
        
        assert "{word_count}" not in prompt  # Should be replaced
        assert "{char_count}" not in prompt  # Should be replaced
        assert "{scene_context}" not in prompt  # Should be replaced
        
        assert "7500" in prompt  # 1500 * 5
        assert "A tense confrontation" in prompt
        assert "at least" in prompt.lower()
    
    def test_expansion_prompt_formatting(self):
        """Test scene expansion prompt formatting."""
        original = "Short scene content"
        prompt = get_expansion_prompt(original, target_length=5000)
        
        assert "Short scene content" in prompt
        assert "5000" in prompt
        assert str(len(original)) in prompt
    
    def test_character_dialogue_prompt(self):
        """Test character dialogue prompt generation."""
        prompt = get_character_dialogue_prompt(
            character_name="Hamlet",
            character_info="The melancholy prince",
            scene_context="Confronting his mother",
            line_count=10
        )
        
        assert "Hamlet" in prompt
        assert "melancholy prince" in prompt
        assert "Confronting his mother" in prompt
        assert "10" in prompt
    
    def test_prompt_length_requirements(self):
        """Test that prompts emphasize length requirements."""
        prompt = get_enhanced_scene_prompt(word_count=2000)
        
        # Should mention specific character count
        assert "10000" in prompt  # 2000 * 5
        # Should emphasize minimum length
        assert "MUST be at least" in prompt or "AT LEAST" in prompt


class TestSceneLengthRequirements:
    """Test that scenes meet length requirements."""
    
    def test_target_length_configuration(self):
        """Test different target length configurations."""
        enhancer_5k = SceneDetailEnhancer(target_length=5000)
        enhancer_7k = SceneDetailEnhancer(target_length=7000)
        
        assert enhancer_5k.target_length == 5000
        assert enhancer_7k.target_length == 7000
    
    def test_enhancement_to_target(self):
        """Test that enhancement aims for target length."""
        target = 3000
        enhancer = SceneDetailEnhancer(target_length=target)
        
        short_scene = "JOHN: Hello.\nSARAH: Hi.\nJOHN: Goodbye.\nSARAH: Bye."
        enhanced = enhancer.enhance_scene(short_scene)
        
        # Should be substantially enhanced
        assert len(enhanced) > len(short_scene) * 5
        # Should aim towards target (may not reach it without LLM)
        assert len(enhanced) > target * 0.5  # At least halfway there
    
    def test_already_long_scene(self):
        """Test handling of scenes that already meet length."""
        enhancer = SceneDetailEnhancer(target_length=100)
        
        long_scene = "A" * 200  # Already exceeds target
        enhanced = enhancer.enhance_scene(long_scene)
        
        # Should not reduce length
        assert len(enhanced) >= len(long_scene)
        # Should return original if already long enough
        assert enhanced == long_scene


class TestDetailLayerPriorities:
    """Test detail layer prioritization."""
    
    def test_detail_layer_creation(self):
        """Test creating detail layers."""
        layer = DetailLayer(
            layer_type="atmosphere",
            content="Rich atmospheric description",
            priority=8
        )
        
        assert layer.layer_type == "atmosphere"
        assert layer.priority == 8
        assert layer.location is None
    
    def test_detail_layer_sorting(self):
        """Test that detail layers sort by priority."""
        layers = [
            DetailLayer("subtext", "content1", priority=5),
            DetailLayer("atmosphere", "content2", priority=8),
            DetailLayer("technical", "content3", priority=3),
            DetailLayer("character", "content4", priority=9)
        ]
        
        sorted_layers = sorted(layers, key=lambda x: x.priority, reverse=True)
        
        assert sorted_layers[0].priority == 9
        assert sorted_layers[-1].priority == 3
        assert sorted_layers[0].layer_type == "character"