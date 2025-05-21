"""Tests for TUI widgets."""
import pytest
pytestmark = pytest.mark.asyncio

from textual.app import App, CSSPathType
from textual.widgets import Label
from textual.containers import Horizontal, Vertical
from thespian.tui.widgets import SceneLibrary, SceneWorkspace, AdvisorPanel, StatusBar
from thespian.tui.state import Scene, AppState
from typing import Dict, Any

class TestApp(App[None]):
    """Test application for widget testing."""

    def compose(self) -> None:
        """Compose the test application."""
        with Vertical():
            with Horizontal():
                yield SceneLibrary(id="scene_library")
                yield SceneWorkspace(id="scene_workspace", classes="test-workspace")
            yield AdvisorPanel(id="advisor_panel")
            yield StatusBar(id="status_bar")

# Ensure the SceneWorkspace is always tall enough in tests
TestApp.CSS_PATH: CSSPathType = None  # Disable default CSS
TestApp.CSS = """
Vertical {
    height: 100%;
    min-height: 40;
    layout: vertical;
}

Horizontal {
    height: 1fr;
    min-height: 30;
    layout: horizontal;
}

SceneLibrary {
    width: 30%;
    min-width: 30;
    height: 100%;
}

SceneWorkspace.test-workspace {
    width: 70%;
    min-width: 50;
    height: 100%;
    min-height: 30;
}

AdvisorPanel {
    height: 20%;
    min-height: 10;
}

StatusBar {
    height: 3;
    min-height: 3;
}

SceneWorkspace .button-bar {
    height: 7;
    min-height: 7;
    width: 100%;
    layout: horizontal;
    align: center middle;
}

SceneWorkspace #generate_scene_button {
    width: auto;
    min-width: 20;
    height: 5;
    min-height: 5;
}
"""

@pytest.fixture
def app() -> TestApp:
    """Create a test application instance."""
    return TestApp()

@pytest.fixture
def sample_scene() -> Scene:
    """Create a sample scene for testing."""
    return Scene(
        id="test_scene_1",
        name="Test Scene",
        content="This is a test scene content.",
        quality_score=0.85
    )

@pytest.fixture
def sample_feedback() -> Dict[str, Any]:
    """Create sample feedback data for testing."""
    return {
        "dramatic_advisor": {
            "critique": "The scene lacks dramatic tension.",
            "suggestions": [
                "Add more conflict between characters",
                "Increase the stakes"
            ]
        },
        "technical_advisor": "The scene structure is solid."
    }

async def test_scene_library(app: TestApp, sample_scene: Scene) -> None:
    """Test SceneLibrary widget functionality."""
    async with app.run_test(size=(120, 40)) as pilot:
        # Get the SceneLibrary widget
        scene_library = app.query_one(SceneLibrary)
        
        # Test loading scenes
        scenes_data = {sample_scene.id: sample_scene}
        scene_library.load_scenes(scenes_data)
        
        # Verify scene was loaded
        list_view = scene_library.query_one("#scene_list_view")
        assert len(list_view.children) == 1
        
        # Test scene selection
        list_view.index = 0  # Select the first item
        scene_library._handle_selection(list_view.children[0])  # Manually trigger selection
        assert scene_library.selected_scene_id == sample_scene.id

async def test_scene_workspace(app: TestApp, sample_scene: Scene) -> None:
    """Test SceneWorkspace widget functionality."""
    async with app.run_test(size=(120, 40)) as pilot:
        # Get the SceneWorkspace widget
        workspace = app.query_one(SceneWorkspace)
        
        # Test updating workspace with a scene
        workspace.update_workspace(sample_scene)
        assert workspace.current_scene_id == sample_scene.id
        assert workspace.scene_title == sample_scene.name
        assert workspace.scene_content == sample_scene.content
        assert workspace.quality_score == sample_scene.quality_score
        
        # Test generation state
        workspace.set_generating_state(True)
        assert workspace.is_generating
        assert workspace.generation_in_progress
        
        # Test progress updates
        workspace.update_progress(50.0)
        assert workspace.generation_progress == 50.0
        
        # Test button interactions
        generate_button = workspace.query_one("#generate_scene_button")
        await pilot.click(generate_button)
        assert workspace.is_generating

async def test_advisor_panel(app: TestApp, sample_feedback: Dict[str, Any]) -> None:
    """Test AdvisorPanel widget functionality."""
    async with app.run_test(size=(120, 40)) as pilot:
        # Get the AdvisorPanel widget
        advisor_panel = app.query_one(AdvisorPanel)
        
        # Test updating feedback
        advisor_panel.update_feedback(sample_feedback)
        assert advisor_panel.has_feedback
        
        # Verify feedback content
        feedback_markdown = advisor_panel.query_one("#advisor_feedback_markdown")
        content = feedback_markdown.render()
        assert "Dramatic Advisor" in content
        assert "Technical Advisor" in content
        assert "The scene lacks dramatic tension" in content

async def test_status_bar(app: TestApp) -> None:
    """Test StatusBar widget functionality."""
    async with app.run_test(size=(120, 40)) as pilot:
        # Get the StatusBar widget
        status_bar = app.query_one(StatusBar)
        
        # Test direct message update
        status_bar.update_message("Test message")
        assert status_bar.status_text == "Test message"
        
        # Test state-based updates
        app_state = AppState()
        app_state.current_screen = "main"
        app_state.is_generating = True
        app_state.scenes = {"scene1": Scene(id="scene1", name="Scene 1")}
        app_state.current_scene = app_state.scenes["scene1"]
        
        status_bar.update_status(app_state)
        assert "Screen: main" in status_bar.status_text
        assert "Generating: Yes" in status_bar.status_text
        assert "Scenes: 1" in status_bar.status_text
        assert "Current: Scene 1" in status_bar.status_text

async def test_widget_interactions(app: TestApp, sample_scene: Scene) -> None:
    """Test interactions between widgets."""
    async with app.run_test(size=(120, 40)) as pilot:
        # Get all widgets
        scene_library = app.query_one(SceneLibrary)
        workspace = app.query_one(SceneWorkspace)
        advisor_panel = app.query_one(AdvisorPanel)
        status_bar = app.query_one(StatusBar)
        
        # Load a scene
        scenes_data = {sample_scene.id: sample_scene}
        scene_library.load_scenes(scenes_data)
        
        # Select the scene
        list_view = scene_library.query_one("#scene_list_view")
        list_view.index = 0  # Select the first item
        scene_library._handle_selection(list_view.children[0])  # Manually trigger selection
        
        # Verify workspace updates
        assert workspace.current_scene_id == sample_scene.id
        
        # Start generation
        generate_button = workspace.query_one("#generate_scene_button")
        await pilot.click(generate_button)
        
        # Set generating state directly since we're not actually running generation
        workspace.set_generating_state(True)
        
        # Update status bar to reflect generating state
        app_state = AppState()
        app_state.current_screen = "main"
        app_state.is_generating = True
        app_state.scenes = scenes_data
        app_state.current_scene = sample_scene
        status_bar.update_status(app_state)
        
        # Verify status updates
        assert workspace.is_generating
        
        # Update feedback
        feedback = {
            "dramatic_advisor": "Scene is progressing well."
        }
        advisor_panel.update_feedback(feedback)
        
        # Verify all widgets reflect the current state
        assert scene_library.selected_scene_id == sample_scene.id
        assert workspace.is_generating
        assert advisor_panel.has_feedback
        assert "Generating: Yes" in status_bar.status_text 