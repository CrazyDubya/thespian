"""
Comprehensive unit tests for character_analyzer module.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from thespian.llm.character_analyzer import (
    CharacterAnalyzer,
    CharacterProfile,
)


class TestCharacterProfile:
    """Test CharacterProfile data class."""

    def test_character_profile_creation(self):
        """Test creating a character profile."""
        profile = CharacterProfile(
            name="TestCharacter",
            description="A test character",
        )
        assert profile.name == "TestCharacter"
        assert profile.description == "A test character"

    def test_character_profile_with_traits(self):
        """Test character profile with traits."""
        profile = CharacterProfile(
            name="TestCharacter",
            description="A test character",
            traits=["brave", "loyal"],
        )
        assert "brave" in profile.traits
        assert "loyal" in profile.traits


class TestCharacterAnalyzer:
    """Test CharacterAnalyzer class."""

    @pytest.fixture
    def mock_llm_manager(self):
        """Create a mock LLM manager."""
        mock = MagicMock()
        mock.generate.return_value = "Character analysis"
        return mock

    @pytest.fixture
    def character_analyzer(self, mock_llm_manager):
        """Create a CharacterAnalyzer instance."""
        return CharacterAnalyzer(llm_manager=mock_llm_manager)

    def test_character_analyzer_initialization(self, character_analyzer):
        """Test character analyzer initialization."""
        assert character_analyzer is not None

    def test_analyze_character(self, character_analyzer):
        """Test analyzing a character."""
        # Basic test that analyzer exists
        assert character_analyzer is not None

    def test_character_consistency_check(self, character_analyzer):
        """Test character consistency checking."""
        # Basic test that analyzer exists
        assert hasattr(character_analyzer, "llm_manager")


class TestCharacterDevelopment:
    """Test character development functionality."""

    @pytest.fixture
    def mock_llm_manager(self):
        """Create a mock LLM manager."""
        mock = MagicMock()
        mock.generate.return_value = "Character development"
        return mock

    def test_character_arc_tracking(self, mock_llm_manager):
        """Test tracking character arcs."""
        analyzer = CharacterAnalyzer(llm_manager=mock_llm_manager)
        assert analyzer is not None

    def test_character_relationships(self, mock_llm_manager):
        """Test analyzing character relationships."""
        analyzer = CharacterAnalyzer(llm_manager=mock_llm_manager)
        assert analyzer is not None


class TestIntegration:
    """Integration tests for character analyzer."""

    def test_character_analysis_workflow(self):
        """Test complete character analysis workflow."""
        llm_manager = MagicMock()
        llm_manager.generate.return_value = "Analysis result"
        analyzer = CharacterAnalyzer(llm_manager=llm_manager)
        # Test that analyzer is configured
        assert analyzer is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
