import pytest
from unittest.mock import MagicMock, patch
from thespian.llm.consolidated_playwright import Playwright, SceneRequirements, PlaywrightCapability, create_playwright
from thespian.llm import LLMManager
from thespian.llm.theatrical_memory import TheatricalMemory, StoryOutline
from thespian.llm.theatrical_advisors import AdvisorManager
from thespian.llm.quality_control import TheatricalQualityControl
from thespian.processors.scene_processor import SceneProcessor

@pytest.fixture
def basic_playwright():
    llm_manager = LLMManager()
    memory = TheatricalMemory()
    advisor_manager = AdvisorManager(llm_manager, memory)
    quality_control = TheatricalQualityControl()
    scene_processor = SceneProcessor()
    playwright = create_playwright(
        name="TestAgent",
        llm_manager=llm_manager,
        memory=memory,
        capabilities=[PlaywrightCapability.BASIC],
        advisor_manager=advisor_manager,
        quality_control=quality_control,
        scene_processor=scene_processor,
        model_type="ollama"
    )
    # Set a minimal story outline
    playwright.story_outline = StoryOutline(
        title="Test Play",
        acts=[{"act_number": 1, "description": "desc", "key_events": ["event1", "event2", "event3", "event4", "event5"], "status": "committed"}]
    )
    return playwright

def test_generate_scene_success(basic_playwright):
    requirements = SceneRequirements(
        setting="Test Setting",
        characters=["A"],
        props=[],
        lighting="Bright",
        sound="Quiet",
        style="Drama",
        period="2024",
        target_audience="Testers",
        act_number=1,
        scene_number=1
    )
    with patch.object(EnhancedPlaywright, "get_llm") as mock_get_llm, \
         patch.object(TheatricalQualityControl, "evaluate_scene") as mock_evaluate_scene:
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = MagicMock(content="FAKE SCENE CONTENT")
        mock_get_llm.return_value = mock_llm
        basic_playwright.scene_processor.process_scene_content = MagicMock(return_value={"scene": "FAKE SCENE CONTENT", "narrative_analysis": "analysis", "raw_content": "FAKE SCENE CONTENT"})
        mock_evaluate_scene.return_value = {
            "character_consistency": 1.0,
            "thematic_coherence": 1.0,
            "technical_accuracy": 1.0,
            "dramatic_impact": 1.0,
            "dialogue_quality": 1.0,
            "stage_direction_quality": 1.0
        }
        result = basic_playwright.generate_scene(requirements)
        assert result["scene"] == "FAKE SCENE CONTENT"
        assert result["narrative_analysis"] == "analysis"
        assert result["evaluation"]["character_consistency"] == 1.0
        assert result["evaluation"]["thematic_coherence"] == 1.0
        assert result["evaluation"]["technical_accuracy"] == 1.0
        assert result["evaluation"]["dramatic_impact"] == 1.0
        assert result["evaluation"]["dialogue_quality"] == 1.0
        assert result["evaluation"]["stage_direction_quality"] == 1.0
        assert "scene_id" in result 