from textual.widget import Widget  # Base class
from textual.widgets import Static, Label, Markdown, ProgressBar, Button, ListView, ListItem
from textual.containers import VerticalScroll, Horizontal, Vertical, Container
from textual.reactive import reactive
from textual.message import Message
from textual.app import ComposeResult
from typing import Optional, Dict, Any, TYPE_CHECKING, List, Callable, Union, TypeVar, cast
from dataclasses import dataclass, field
from datetime import datetime
import logging
from thespian.tui.state import Scene

if TYPE_CHECKING:
    from .state import Scene  # Forward reference for type hinting

T = TypeVar('T')

class SceneSelected(Message):
    """Message sent when a scene is selected in the library."""

    def __init__(self, scene_id: str) -> None:
        super().__init__()
        self.scene_id = scene_id


class GenerateSceneContent(Message):
    """Message to request generating content for a scene."""

    def __init__(self, scene_id: str) -> None:
        super().__init__()
        self.scene_id = scene_id


class StopGeneration(Message):
    """Message to signal stopping the current generation process."""
    pass


class SceneLibrary(Static):
    """Widget to display and manage the list of scenes."""

    selected_scene_id: reactive[Optional[str]] = reactive(None)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scenes = {}

    def compose(self):
        yield Label("Scene Library", id="scene_library_title")
        yield ListView(id="scene_library_list_view")

    def load_scenes(self, scenes: dict[str, Scene]) -> None:
        self.scenes = scenes
        list_view = self.query_one("#scene_library_list_view")
        list_view.clear()
        seen_ids = set()
        for scene in scenes.values():
            print(f"[DEBUG] Attempting to add scene with id: {scene.id} and name: {scene.name}")
            if scene.id in seen_ids:
                print(f"[WARNING] Duplicate scene id detected: {scene.id}. Skipping this scene.")
                continue
            seen_ids.add(scene.id)
            item = ListItem(Label(scene.name), id=f"scene_library_item_{scene.id}")
            item.scene_id = scene.id  # Store the scene_id directly
            list_view.append(item)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle scene selection from the list view."""
        self._handle_selection(event.item)

    def _handle_selection(self, item: ListItem) -> None:
        """Handle selection of a scene item."""
        if not item:
            return
        scene_id = getattr(item, 'scene_id', None)
        if scene_id and scene_id in self.scenes:
            self.selected_scene_id = scene_id
            scene = self.scenes[scene_id]
            workspace = self.app.query_one(SceneWorkspace)
            workspace.update_workspace(scene)
            self.refresh()

    def on_mount(self) -> None:
        """Called when the widget is mounted."""
        list_view = self.query_one(ListView)
        list_view.index = None  # Clear any initial selection


class SceneWorkspace(Container):
    """Widget to display the current scene, its content, and generation progress."""

    DEFAULT_CSS = """
    SceneWorkspace {
        height: 100%;
        min-height: 30;
        background: $surface;
        border: solid $primary;
        padding: 1;
        overflow-y: auto;
        layout: vertical;
    }
    
    SceneWorkspace .button-bar {
        height: 7;
        min-height: 7;
        background: $surface;
        border-top: solid $primary;
        padding: 1;
        width: 100%;
        layout: horizontal;
        align: center middle;
        dock: bottom;
    }
    
    SceneWorkspace #scene_workspace_generate_button {
        width: auto;
        min-width: 20;
        height: 5;
        min-height: 5;
    }
    #scene_workspace_title_display {
        width: 100%;
        padding: 0 1;
        margin-bottom: 1;
        border: round $primary;
        min-height: 3;
    }
    #scene_workspace_content_display {
        height: 1fr;
        width: 100%;
        margin-bottom: 1;
        border: round $accent;
        overflow-y: auto;
        min-height: 10;
    }
    #scene_workspace_quality_score {
        margin-top: 1;
        padding: 0 1;
        background: $primary-lighten-2;
        color: $text;
        width: 100%;
        text-align: center;
    }
    #scene_workspace_progress_bar {
        margin-top: 1;
        width: 100%;
        height: 1;
        background: $primary-background;
        color: $success;
    }
    .button-bar Button {
        margin: 0 1;
        min-width: 10;
        height: 3;
        min-height: 3;
    }
    """

    current_scene_id: reactive[Optional[str]] = reactive(None)
    scene_title: reactive[str] = reactive("")
    scene_content: reactive[str] = reactive("")
    quality_score: reactive[float] = reactive(0.0)
    is_generating: reactive[bool] = reactive(False)
    generation_progress: reactive[float] = reactive(0.0)
    generation_in_progress: reactive[bool] = reactive(False)

    def set_generating_state(self, is_generating: bool) -> None:
        """Set the generating state of the workspace."""
        self.is_generating = is_generating
        self.generation_in_progress = is_generating
        if is_generating:
            self.generation_progress = 0.0
        else:
            self.generation_progress = 100.0

    def update_progress(self, progress: float) -> None:
        """Update the generation progress."""
        self.generation_progress = progress
        progress_bar = self.query_one("#scene_workspace_progress_bar", ProgressBar)
        progress_bar.progress = progress

    def on_mount(self) -> None:
        self.app.log.info("--- SceneWorkspace: Mounted --- ")
        initial_scene = (
            self.app.state.current_scene
            if hasattr(self.app, "state") and self.app.state.current_scene
            else None
        )
        self.update_workspace(initial_scene)
        self.watch_quality_score(0.0, self.quality_score)
        self.watch_is_generating(False, self.is_generating)

    def compose(self) -> None:
        """Compose the widget's children."""
        yield Label("Scene Workspace", classes="workspace-title", id="scene_workspace_title")
        yield Static(self.scene_title, id="scene_workspace_title_display")
        yield Markdown(self.scene_content, id="scene_workspace_content_display")
        yield ProgressBar(total=100, id="scene_workspace_progress_bar")
        yield Label(f"Quality Score: {self.quality_score:.2f}", id="scene_workspace_quality_score")
        with Horizontal(classes="button-bar"):
            yield Button("Edit Scene", id="scene_workspace_edit_button", variant="primary", disabled=True)
            yield Button("Generate/Regenerate", id="scene_workspace_generate_button", variant="success")
            yield Button("Save Scene", id="scene_workspace_save_button", variant="default")

    def watch_quality_score(self, old_value: float, new_value: float) -> None:
        """Called when quality_score changes to update the label."""
        try:
            quality_label = self.query_one("#scene_workspace_quality_score", Label)
            quality_label.update(f"Quality Score: {new_value:.2f}")
            self.app.log.info(
                f"--- SceneWorkspace: watch_quality_score triggered. Old: {old_value}, New: {new_value}. Label updated. ---"
            )
        except Exception as e:
            self.app.log.error(f"--- SceneWorkspace: ERROR in watch_quality_score: {e} ---")

    def watch_is_generating(self, old_value: bool, new_value: bool) -> None:
        """Called when is_generating changes to show/hide progress bar and update button state."""
        progress_bar = self.query_one("#scene_workspace_progress_bar", ProgressBar)
        generate_button = self.query_one("#scene_workspace_generate_button", Button)
        if new_value:
            progress_bar.remove_class("-hidden")
            generate_button.label = "Stop Generation"
            generate_button.variant = "error"
        else:
            progress_bar.add_class("-hidden")
            generate_button.label = "Generate/Regenerate"
            generate_button.variant = "success"
            self.generation_progress = 0  # Reset progress when stopping
        self.app.log.info(f"--- SceneWorkspace: watch_is_generating. Generating: {new_value} ---")

    def watch_generation_progress(self, old_value: float, new_value: float) -> None:
        """Called when generation_progress changes to update the progress bar."""
        progress_bar = self.query_one("#scene_workspace_progress_bar", ProgressBar)
        progress_bar.progress = new_value
        self.app.log.info(
            f"--- SceneWorkspace: watch_generation_progress. Progress: {new_value} ---"
        )

    def update_workspace(self, scene: Optional["Scene"]) -> None:
        """Update the workspace with a scene."""
        if scene:
            self.current_scene_id = scene.id
            self.scene_title = scene.name
            self.scene_content = scene.content
            self.query_one("#scene_workspace_title_display", Static).update(f"Scene Name: {scene.name}")
            self.query_one("#scene_workspace_content_display", Markdown).update(
                scene.content if scene.content else "*No content yet.*"
            )
            self.quality_score = scene.quality_score
            self.app.log.info(
                f"--- SceneWorkspace: Updated with scene '{scene.id}', Name: '{scene.name}', QS: {scene.quality_score} ---"
            )
        else:
            self.current_scene_id = None
            self.scene_title = ""
            self.scene_content = ""
            self.query_one("#scene_workspace_title_display", Static).update("No scene selected.")
            self.query_one("#scene_workspace_content_display", Markdown).update(
                "*Select a scene from the library or create a new one.*"
            )
            self.quality_score = 0.0
            self.app.log.info("--- SceneWorkspace: Cleared (no scene selected). ---")
        self.refresh()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events within the SceneWorkspace."""
        self.app.log.info(
            f"--- SceneWorkspace.on_button_pressed: Button ID '{event.button.id}' pressed. ---"
        )
        if event.button.id == "scene_workspace_generate_button":
            if self.is_generating:  # If already generating, this button means 'Stop'
                self.app.log.info(
                    "--- SceneWorkspace: 'Stop Generation' button pressed. Posting StopGeneration message. ---"
                )
                self.post_message(StopGeneration())
            elif self.current_scene_id:
                self.app.log.info(
                    f"--- SceneWorkspace: 'Generate/Regenerate' button pressed for scene {self.current_scene_id}. Posting GenerateSceneContent message. ---"
                )
                self.post_message(GenerateSceneContent(self.current_scene_id))
            else:
                self.app.notify("No scene selected to generate content for.", severity="warning")
                self.app.log.warning(
                    "--- SceneWorkspace: 'Generate/Regenerate' pressed but no current_scene_id. ---"
                )
        elif event.button.id == "scene_workspace_save_button":
            self.app.log.info(
                "--- SceneWorkspace: 'Save Scene' button pressed. Action handled by app binding. ---"
            )
        elif event.button.id == "scene_workspace_edit_button":
            self.app.log.info(
                "--- SceneWorkspace: 'Edit Scene' button pressed. Functionality not implemented. ---"
            )
            self.app.notify("Scene editing is not yet implemented.", severity="warning")


class AdvisorPanel(Widget):
    """Panel for displaying advisor feedback."""
    
    def __init__(self, feedback_content: str = "", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.feedback_content = feedback_content
    
    def compose(self) -> ComposeResult:
        """Create child widgets for the advisor panel."""
        yield Label("Advisor Feedback", id="advisor_panel_title")
        with VerticalScroll(id="advisor_panel_feedback_scroll"):
            yield Markdown(self.feedback_content, id="advisor_panel_feedback_markdown")
    
    def on_mount(self) -> None:
        """Initialize the advisor panel."""
        self.app.log.info("AdvisorPanel: Mounted")
        markdown_widget = self.query_one("#advisor_panel_feedback_markdown", Markdown)
        markdown_widget.update(self.feedback_content)
    
    def update_feedback(self, feedback: str) -> None:
        """Update the feedback content."""
        self.feedback_content = feedback
        markdown_widget = self.query_one("#advisor_panel_feedback_markdown", Markdown)
        markdown_widget.update(feedback)


class StatusBar(Static):
    """A simple status bar widget."""

    status_text = reactive("Ready.")
    is_generating: reactive[bool] = reactive(False)

    def compose(self):
        # This Label's content will automatically update when self.status_text changes.
        yield Label(self.status_text, id="status_bar_label")

    def update_message(self, message: str) -> None:
        """Update the status bar with a direct message."""
        self.status_text = message
        self.app.log.info(f"StatusBar: Updated message - {message}")

    def update_status(self, current_app_state: "AppState") -> None:
        """Update the status bar with the current application state."""
        status_parts = []
        
        # Add screen information
        status_parts.append(f"Screen: {current_app_state.current_screen}")
        
        # Add generation status
        self.is_generating = current_app_state.is_generating
        status_parts.append(f"Generating: {'Yes' if self.is_generating else 'No'}")
        
        # Add scene information
        scene_count = len(current_app_state.scenes)
        status_parts.append(f"Scenes: {scene_count}")
        
        if current_app_state.current_scene:
            status_parts.append(f"Current: {current_app_state.current_scene.name}")
        
        self.status_text = " | ".join(status_parts)
        self.app.log.info(f"StatusBar: Updated status - {self.status_text}")

    def on_mount(self) -> None:
        """Initialize the status bar."""
        self.app.log.info("StatusBar: Mounted")
        self.update_message("Ready.") 