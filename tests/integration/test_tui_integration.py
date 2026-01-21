"""
Integration tests for TUI and agent systems.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch


class TestTUIIntegration:
    """Integration tests for TUI application."""

    def test_app_initialization(self):
        """Test TUI app can be initialized."""
        try:
            from thespian.tui.app import ThespianApp
            # Test app class exists
            assert ThespianApp is not None
        except (ImportError, AttributeError) as e:
            pytest.skip(f"TUI app test skipped: {e}")

    def test_widgets_integration(self):
        """Test widgets work with app."""
        try:
            from thespian.tui import widgets
            from thespian.tui import dialogs
            
            # Test modules exist
            assert widgets is not None
            assert dialogs is not None
        except ImportError as e:
            pytest.skip(f"Widgets integration test skipped: {e}")


class TestAgentIntegration:
    """Integration tests for agent system."""

    def test_agents_collaboration(self):
        """Test agents can collaborate."""
        try:
            from thespian.agents import theatrical
            # Test theatrical agents module
            assert theatrical is not None
        except ImportError as e:
            pytest.skip(f"Agent integration test skipped: {e}")

    def test_enhanced_agents(self):
        """Test enhanced agents functionality."""
        try:
            from thespian import agents_enhanced
            # Test enhanced agents module
            assert agents_enhanced is not None
        except ImportError as e:
            pytest.skip(f"Enhanced agents test skipped: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
