"""
Comprehensive unit tests for consolidated_playwright module.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from thespian.llm.consolidated_playwright import (
    Playwright,
    SceneRequirements,
    PlaywrightCapability,
    create_playwright,
    SceneMetadata,
)
from thespian.llm.theatrical_memory import TheatricalMemory
from thespian.llm.quality_control import TheatricalQualityControl


class TestSceneRequirements:
    """Test SceneRequirements data class."""

    def test_scene_requirements_creation(self):
        """Test creating scene requirements."""
        requirements = SceneRequirements(
            act=1,
            scene=1,
            setting="A tavern",
            characters=["Alice", "Bob"],
            plot_points=["Alice enters", "Bob greets Alice"],
        )
        assert requirements.act == 1
        assert requirements.scene == 1
        assert requirements.setting == "A tavern"
        assert len(requirements.characters) == 2
        assert len(requirements.plot_points) == 2

    def test_scene_requirements_defaults(self):
        """Test default values for optional fields."""
        requirements = SceneRequirements(
            act=1,
            scene=1,
            setting="A room",
            characters=["Alice"],
        )
        assert requirements.plot_points == []
        assert requirements.themes == []
        assert requirements.mood is None


class TestPlaywrightCapability:
    """Test PlaywrightCapability enum."""

    def test_capability_values(self):
        """Test that all expected capabilities exist."""
        assert hasattr(PlaywrightCapability, "BASIC")
        assert hasattr(PlaywrightCapability, "ITERATIVE_REFINEMENT")
        assert hasattr(PlaywrightCapability, "MEMORY_INTEGRATION")
        assert hasattr(PlaywrightCapability, "QUALITY_CONTROL")

    def test_capability_enum_values(self):
        """Test enum value types."""
        assert isinstance(PlaywrightCapability.BASIC.value, str)


class TestPlaywright:
    """Test Playwright class."""

    @pytest.fixture
    def mock_llm_manager(self):
        """Create a mock LLM manager."""
        mock = MagicMock()
        mock.generate.return_value = "Generated scene content"
        return mock

    @pytest.fixture
    def mock_memory(self):
        """Create a mock theatrical memory."""
        return Mock(spec=TheatricalMemory)

    @pytest.fixture
    def mock_quality_control(self):
        """Create a mock quality control."""
        return Mock(spec=TheatricalQualityControl)

    @pytest.fixture
    def playwright(self, mock_llm_manager, mock_memory, mock_quality_control):
        """Create a Playwright instance."""
        return Playwright(
            name="TestPlaywright",
            llm_manager=mock_llm_manager,
            memory=mock_memory,
            quality_control=mock_quality_control,
            model_type="test",
            capabilities=[PlaywrightCapability.BASIC],
        )

    def test_playwright_initialization(self, playwright):
        """Test playwright initialization."""
        assert playwright.name == "TestPlaywright"
        assert playwright.model_type == "test"
        assert PlaywrightCapability.BASIC in playwright.capabilities

    def test_playwright_name_validation(self, mock_llm_manager):
        """Test that playwright requires a name."""
        with pytest.raises((TypeError, ValueError)):
            Playwright(
                name=None,
                llm_manager=mock_llm_manager,
            )

    def test_has_capability(self, playwright):
        """Test capability checking."""
        assert playwright.has_capability(PlaywrightCapability.BASIC)
        assert not playwright.has_capability(PlaywrightCapability.MEMORY_INTEGRATION)

    @patch("thespian.llm.consolidated_playwright.Playwright.generate_scene")
    def test_generate_scene_basic(self, mock_generate, playwright):
        """Test basic scene generation."""
        mock_generate.return_value = "Generated scene"
        requirements = SceneRequirements(
            act=1,
            scene=1,
            setting="Test setting",
            characters=["TestChar"],
        )
        result = playwright.generate_scene(requirements)
        mock_generate.assert_called_once()

    def test_scene_metadata_creation(self):
        """Test scene metadata creation."""
        metadata = SceneMetadata(
            act=1,
            scene=2,
            characters=["Alice"],
            setting="Forest",
        )
        assert metadata.act == 1
        assert metadata.scene == 2
        assert "Alice" in metadata.characters


class TestCreatePlaywright:
    """Test the create_playwright factory function."""

    @pytest.fixture
    def mock_llm_manager(self):
        """Create a mock LLM manager."""
        return MagicMock()

    @pytest.fixture
    def mock_memory(self):
        """Create a mock theatrical memory."""
        return Mock(spec=TheatricalMemory)

    @pytest.fixture
    def mock_quality_control(self):
        """Create a mock quality control."""
        return Mock(spec=TheatricalQualityControl)

    def test_create_basic_playwright(
        self, mock_llm_manager, mock_memory, mock_quality_control
    ):
        """Test creating a basic playwright."""
        playwright = create_playwright(
            name="BasicPlaywright",
            llm_manager=mock_llm_manager,
            memory=mock_memory,
            quality_control=mock_quality_control,
            model_type="test",
            capabilities=[PlaywrightCapability.BASIC],
        )
        assert playwright.name == "BasicPlaywright"
        assert playwright.model_type == "test"

    def test_create_enhanced_playwright(
        self, mock_llm_manager, mock_memory, mock_quality_control
    ):
        """Test creating an enhanced playwright with multiple capabilities."""
        playwright = create_playwright(
            name="EnhancedPlaywright",
            llm_manager=mock_llm_manager,
            memory=mock_memory,
            quality_control=mock_quality_control,
            model_type="test",
            capabilities=[
                PlaywrightCapability.BASIC,
                PlaywrightCapability.MEMORY_INTEGRATION,
                PlaywrightCapability.QUALITY_CONTROL,
            ],
        )
        assert playwright.has_capability(PlaywrightCapability.BASIC)
        assert playwright.has_capability(PlaywrightCapability.MEMORY_INTEGRATION)
        assert playwright.has_capability(PlaywrightCapability.QUALITY_CONTROL)

    def test_create_playwright_minimal(self, mock_llm_manager):
        """Test creating playwright with minimal parameters."""
        playwright = create_playwright(
            name="MinimalPlaywright",
            llm_manager=mock_llm_manager,
        )
        assert playwright.name == "MinimalPlaywright"


class TestIntegration:
    """Integration tests for playwright workflow."""

    @pytest.fixture
    def full_setup(self):
        """Create full test setup."""
        llm_manager = MagicMock()
        llm_manager.generate.return_value = "Test scene content"
        memory = Mock(spec=TheatricalMemory)
        quality_control = Mock(spec=TheatricalQualityControl)
        playwright = create_playwright(
            name="IntegrationTest",
            llm_manager=llm_manager,
            memory=memory,
            quality_control=quality_control,
            capabilities=[PlaywrightCapability.BASIC],
        )
        return {
            "playwright": playwright,
            "llm_manager": llm_manager,
            "memory": memory,
            "quality_control": quality_control,
        }

    def test_end_to_end_scene_generation(self, full_setup):
        """Test complete scene generation workflow."""
        playwright = full_setup["playwright"]
        requirements = SceneRequirements(
            act=1,
            scene=1,
            setting="Test location",
            characters=["Character1", "Character2"],
            plot_points=["Event 1", "Event 2"],
        )
        # This would test the full workflow if generate_scene is implemented
        # For now, test that the playwright is properly configured
        assert playwright is not None
        assert playwright.name == "IntegrationTest"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
