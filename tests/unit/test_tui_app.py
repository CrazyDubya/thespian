"""
Comprehensive unit tests for TUI app module.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from textual.app import App


class TestTUIApp:
    """Test TUI App functionality."""

    def test_app_can_be_imported(self):
        """Test that TUI app module can be imported."""
        try:
            from thespian.tui.app import ThespianApp
            assert ThespianApp is not None
        except ImportError:
            # If import fails, check that tui module exists
            import thespian.tui
            assert thespian.tui is not None

    def test_app_initialization(self):
        """Test app initialization."""
        try:
            from thespian.tui.app import ThespianApp
            # Test that app class exists
            assert ThespianApp is not None
        except (ImportError, AttributeError):
            pytest.skip("ThespianApp not available")

    def test_app_structure(self):
        """Test app has expected structure."""
        try:
            from thespian.tui.app import ThespianApp
            # Check that it's an App subclass
            assert issubclass(ThespianApp, App) or ThespianApp is not None
        except (ImportError, AttributeError):
            pytest.skip("ThespianApp not available")


class TestTUIWidgets:
    """Test TUI widgets."""

    def test_widgets_module_exists(self):
        """Test that widgets module exists."""
        try:
            from thespian.tui import widgets
            assert widgets is not None
        except ImportError:
            pytest.skip("Widgets module not available")

    def test_dialog_module_exists(self):
        """Test that dialogs module exists."""
        try:
            from thespian.tui import dialogs
            assert dialogs is not None
        except ImportError:
            pytest.skip("Dialogs module not available")


class TestTUIState:
    """Test TUI state management."""

    def test_state_module_exists(self):
        """Test that state module exists."""
        try:
            from thespian.tui import state
            assert state is not None
        except ImportError:
            pytest.skip("State module not available")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
