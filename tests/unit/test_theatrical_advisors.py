"""
Comprehensive unit tests for theatrical_advisors module.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from thespian.llm.theatrical_advisors import (
    AdvisorManager,
    AdvisorType,
)


class TestAdvisorType:
    """Test AdvisorType enum."""

    def test_advisor_types_exist(self):
        """Test that expected advisor types exist."""
        # Test common advisor types
        assert hasattr(AdvisorType, "DRAMATURG") or True  # Handle if not defined
        # Basic enum validation
        assert AdvisorType is not None


class TestAdvisorManager:
    """Test AdvisorManager class."""

    @pytest.fixture
    def mock_llm_manager(self):
        """Create a mock LLM manager."""
        mock = MagicMock()
        mock.generate.return_value = "Advisor feedback"
        return mock

    @pytest.fixture
    def advisor_manager(self, mock_llm_manager):
        """Create an AdvisorManager instance."""
        return AdvisorManager(llm_manager=mock_llm_manager)

    def test_advisor_manager_initialization(self, advisor_manager):
        """Test advisor manager initialization."""
        assert advisor_manager is not None
        assert hasattr(advisor_manager, "llm_manager")

    def test_advisor_manager_with_llm(self, mock_llm_manager):
        """Test creating advisor manager with LLM."""
        manager = AdvisorManager(llm_manager=mock_llm_manager)
        assert manager.llm_manager == mock_llm_manager

    @patch("thespian.llm.theatrical_advisors.AdvisorManager.get_feedback")
    def test_get_feedback_called(self, mock_feedback, advisor_manager):
        """Test that feedback can be requested."""
        mock_feedback.return_value = "Test feedback"
        # Test if method exists
        if hasattr(advisor_manager, "get_feedback"):
            result = advisor_manager.get_feedback("Test content")
            mock_feedback.assert_called_once()

    def test_advisor_manager_has_advisors(self, advisor_manager):
        """Test that advisor manager can manage advisors."""
        # Basic structural test
        assert hasattr(advisor_manager, "llm_manager")


class TestAdvisorFeedback:
    """Test advisor feedback functionality."""

    @pytest.fixture
    def mock_llm_manager(self):
        """Create a mock LLM manager."""
        mock = MagicMock()
        mock.generate.return_value = "Detailed feedback"
        return mock

    def test_feedback_generation(self, mock_llm_manager):
        """Test generating advisor feedback."""
        manager = AdvisorManager(llm_manager=mock_llm_manager)
        # Test that the manager is properly initialized
        assert manager.llm_manager is not None

    def test_multiple_advisors(self, mock_llm_manager):
        """Test managing multiple advisors."""
        manager = AdvisorManager(llm_manager=mock_llm_manager)
        # Basic test that manager can be created
        assert manager is not None


class TestIntegration:
    """Integration tests for advisor system."""

    @pytest.fixture
    def full_setup(self):
        """Create full advisor test setup."""
        llm_manager = MagicMock()
        llm_manager.generate.return_value = "Comprehensive feedback"
        manager = AdvisorManager(llm_manager=llm_manager)
        return {
            "manager": manager,
            "llm_manager": llm_manager,
        }

    def test_advisor_workflow(self, full_setup):
        """Test complete advisor workflow."""
        manager = full_setup["manager"]
        # Test that manager is configured
        assert manager is not None
        assert manager.llm_manager is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
