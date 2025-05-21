from textual.widget import Widget  # Base class
from textual.widgets import Static, Label, Markdown, ProgressBar, Button, ListView, ListItem
from textual.containers import VerticalScroll, Horizontal, Vertical, Container
from textual.reactive import reactive
from textual.message import Message
from typing import Optional, Dict, Any, TYPE_CHECKING, List, Callable, Union, TypeVar, cast
from dataclasses import dataclass, field
from datetime import datetime

if TYPE_CHECKING:
    from .state import Scene  # Forward reference for type hinting

T = TypeVar('T')

class SceneSelected(Message):
    """Message sent when a scene is selected in the library."""

    def __init__(self, scene_id: Optional[str]) -> None:
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


class SceneLibrary(Widget):
    """Widget to display and manage the list of scenes."""

    DEFAULT_CSS = """
    SceneLibrary {
        layout: vertical;
        height: 100%;
        border: heavy $primary;
    }
    #scene_list_view {
        height: 1fr;
        border: round $primary;
    }
    """

    selected_scene_id: reactive[Optional[str]] = reactive(None)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._list_view: Optional[ListView] = None
        self._title_label: Optional[Label] = None

    def compose(self) -> None:
        """Compose the widget's children."""
        self._title_label = Label("Scene Library")
        self._list_view = ListView(id="scene_list_view")
        yield self._title_label
        yield self._list_view

    def watch_selected_scene_id(self, old_value: Optional[str], new_value: Optional[str]) -> None:
        """Called when selected_scene_id changes to update the list view selection."""
        if not self._list_view:
            return

        # Find the item with matching scene_id and select it
        for item in self._list_view.children:
            if hasattr(item, "scene_id") and item.scene_id == new_value:
                self._list_view.index = self._list_view.children.index(item)
                break
        else:
            self._list_view.index = None

    def load_scenes(self, scenes_data: dict) -> None:
        """Clears and repopulates the scene list."""
        if not self._list_view:
            return

        self._list_view.clear()
        processed_item_ids_this_run = set()

        for scene_id, scene_obj in scenes_data.items():
            scene_name = scene_obj.name
            item_widget_id = f"scene_item_{scene_id}"

            if item_widget_id in processed_item_ids_this_run:
                continue

            processed_item_ids_this_run.add(item_widget_id)
            item = ListItem(Label(scene_name if scene_name else "Unnamed Scene"), id=item_widget_id)
            item.scene_id = scene_id  # Store scene_id on the item for later retrieval

            try:
                self._list_view.append(item)
            except Exception as e:
                self.app.log.error(f"Error appending ListItem with id '{item_widget_id}': {e}")
                raise

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle scene selection."""
        if not event.item:
            return
        scene_id = getattr(event.item, "scene_id", None)
        if scene_id:
            self.selected_scene_id = scene_id
            self.post_message(SceneSelected(scene_id))


class SceneWorkspace(Widget):
    """Widget to display the current scene, its content, and generation progress."""

    DEFAULT_CSS = """
    SceneWorkspace {
        layout: vertical;
        overflow-y: auto;        
        border: heavy $primary;
    }
    #scene_title_display {
        width: 100%;
        padding: 0 1;
        margin-bottom: 1;
        border: round $primary;
        min-height: 3;
    }
    #scene_content_display {
        height: 1fr;
        width: 100%;
        margin-bottom: 1;
        border: round $accent;
        padding: 1;
    }
    #quality_score_label {
        margin-top: 1;
        padding: 0 1;
        background: $primary-lighten-2;
        color: $text;
        width: 100%;
        text-align: center;
    }
    #generation_progress_bar {
        margin-top: 1;
        width: 100%;
        height: 1;
        background: $primary-background;
        color: $success;
    }
    .button-bar {
        layout: horizontal;
        align-horizontal: center;
        width: 100%;
        margin-top: 1;
    }
    .button-bar Button {
        margin: 0 1;
    }
    """

    current_scene_id: reactive[Optional[str]] = reactive(None)
    scene_title: reactive[str] = reactive("")
    scene_content: reactive[str] = reactive("")
    quality_score: reactive[float] = reactive(0.0)
    is_generating: reactive[bool] = reactive(False)
    generation_progress: reactive[float] = reactive(0.0)
    generation_in_progress: reactive[bool] = reactive(False)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._title_display: Optional[Static] = None
        self._content_display: Optional[Markdown] = None
        self._progress_bar: Optional[ProgressBar] = None
        self._quality_label: Optional[Label] = None
        self._edit_button: Optional[Button] = None
        self._generate_button: Optional[Button] = None
        self._save_button: Optional[Button] = None
        self._current_content_text_area: Optional[Static] = None

    def compose(self) -> None:
        """Compose the widget's children."""
        yield Label("Scene Workspace", classes="workspace-title")
        self._title_display = Static(self.scene_title, id="scene_title_display")
        yield self._title_display
        self._content_display = Markdown(self.scene_content, id="scene_content_display")
        yield self._content_display
        self._progress_bar = ProgressBar(total=100, id="generation_progress_bar")
        yield self._progress_bar
        self._quality_label = Label(f"Quality Score: {self.quality_score:.2f}", id="quality_score_label")
        yield self._quality_label
        with Horizontal(classes="button-bar"):
            self._edit_button = Button("Edit Scene", id="edit_scene_button", variant="primary", disabled=True)
            yield self._edit_button
            self._generate_button = Button("Generate/Regenerate", id="generate_scene_button", variant="success")
            yield self._generate_button
            self._save_button = Button("Save Scene", id="save_scene_button", variant="default")
            yield self._save_button

    def watch_scene_content(self, old_value: str, new_value: str) -> None:
        """Called when scene_content changes to update the markdown display."""
        if self._content_display:
            self._content_display.update(new_value if new_value else "*No content yet.*")

    def watch_scene_title(self, old_value: str, new_value: str) -> None:
        """Called when scene_title changes to update the title display."""
        if self._title_display:
            self._title_display.update(f"Scene Name: {new_value}" if new_value else "No scene selected.")

    def watch_quality_score(self, old_value: float, new_value: float) -> None:
        """Called when quality_score changes to update the label."""
        if self._quality_label:
            self._quality_label.update(f"Quality Score: {new_value:.2f}")

    def watch_is_generating(self, old_value: bool, new_value: bool) -> None:
        """Called when is_generating changes to show/hide progress bar and update button state."""
        if not self._progress_bar or not self._generate_button:
            return

        if new_value:
            self._progress_bar.remove_class("-hidden")
            self._generate_button.label = "Stop Generation"
            self._generate_button.variant = "error"
        else:
            self._progress_bar.add_class("-hidden")
            self._generate_button.label = "Generate/Regenerate"
            self._generate_button.variant = "success"
            self.generation_progress = 0

    def watch_generation_progress(self, old_value: float, new_value: float) -> None:
        """Called when generation_progress changes to update the progress bar."""
        if self._progress_bar:
            self._progress_bar.progress = new_value

    def watch_generation_in_progress(self, old_value: bool, new_value: bool) -> None:
        """Called when generation_in_progress changes to update the UI state."""
        self.is_generating = new_value

    def update_workspace(self, scene: Optional["Scene"]) -> None:
        """Update the workspace with a new scene."""
        if scene:
            self.current_scene_id = scene.id
            self.scene_title = scene.name
            self.scene_content = scene.content
            self.quality_score = scene.quality_score
        else:
            self.current_scene_id = None
            self.scene_title = ""
            self.scene_content = ""
            self.quality_score = 0.0

    def update_status(self, message: str) -> None:
        """Update the status message."""
        if self.app:
            self.app.notify(message)

    def update_progress(self, progress: float) -> None:
        """Update the generation progress."""
        self.generation_progress = progress

    def set_generating_state(self, is_generating: bool) -> None:
        """Set the generating state."""
        self.generation_in_progress = is_generating

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events within the SceneWorkspace."""
        if not event.button:
            return

        if event.button.id == "generate_scene_button":
            if self.is_generating:
                self.post_message(StopGeneration())
            elif self.current_scene_id:
                self.post_message(GenerateSceneContent(self.current_scene_id))
            else:
                self.app.notify("No scene selected to generate content for.", severity="warning")
        elif event.button.id == "save_scene_button":
            self.app.action_save_scene_action()
        elif event.button.id == "edit_scene_button":
            self.app.notify("Scene editing is not yet implemented.", severity="warning")


class AdvisorPanel(Widget):
    """Widget to display feedback from various advisors."""

    DEFAULT_CSS = """
    AdvisorPanel {
        layout: vertical;
        height: 100%;
        border: heavy $primary;
    }
    #advisor_panel_title {
        width: 100%;
        padding: 0 1;
        margin-bottom: 1;
        border: round $primary;
        background: $primary-lighten-2;
    }
    #advisor_feedback_scroll {
        height: 1fr;
        border: round $accent;
    }
    #advisor_feedback_markdown {
        padding: 1;
    }
    .advisor-section {
        margin: 1 0;
        padding: 1;
        border: round $primary;
    }
    .advisor-title {
        color: $accent;
        text-style: bold;
    }
    .advisor-critique {
        margin: 1 0;
        padding: 0 1;
        border-left: heavy $primary;
    }
    .advisor-suggestions {
        margin: 1 0;
        padding: 0 1;
        border-left: heavy $success;
    }
    """

    feedback_content = reactive("No feedback yet.")
    has_feedback = reactive(False)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._title_label: Optional[Label] = None
        self._feedback_markdown: Optional[Markdown] = None

    def compose(self) -> None:
        """Compose the widget's children."""
        self._title_label = Label("Advisor Feedback", id="advisor_panel_title")
        yield self._title_label
        with VerticalScroll(id="advisor_feedback_scroll"):
            self._feedback_markdown = Markdown(self.feedback_content, id="advisor_feedback_markdown")
            yield self._feedback_markdown

    def watch_feedback_content(self, old_value: str, new_value: str) -> None:
        """Called when feedback_content changes to update the markdown display."""
        if self._feedback_markdown:
            self._feedback_markdown.update(new_value)
            self.has_feedback = new_value != "No feedback yet." and new_value != "No feedback available."

    def watch_has_feedback(self, old_value: bool, new_value: bool) -> None:
        """Called when has_feedback changes to update the panel appearance."""
        if self._title_label:
            if new_value:
                self._title_label.styles.background = "transparent"
            else:
                self._title_label.styles.background = "$primary-lighten-2"

    def update_feedback(self, feedback_data: Optional[Dict[str, Any]]) -> None:
        """Updates the advisor panel with new feedback data."""
        if not feedback_data:
            self.feedback_content = "No feedback available."
            return

        formatted_feedback = []
        for advisor, messages in feedback_data.items():
            advisor_name = advisor.replace('_', ' ').title()
            section = [f"### {advisor_name}"]

            if isinstance(messages, dict):
                critique = messages.get("critique", "")
                suggestions = messages.get("suggestions", [])
                
                if critique:
                    section.append("\n**Critique:**")
                    section.append(f"> {critique}")
                
                if suggestions:
                    section.append("\n**Suggestions:**")
                    for suggestion in suggestions:
                        section.append(f"- {suggestion}")
            elif isinstance(messages, str):
                section.append(f"\n{messages}")
            else:
                section.append(f"\n{str(messages)}")

            formatted_feedback.append("\n".join(section))

        if formatted_feedback:
            self.feedback_content = "\n\n---\n\n".join(formatted_feedback)
        else:
            self.feedback_content = "No specific feedback provided."


class StatusBar(Widget):
    """A simple status bar widget."""

    DEFAULT_CSS = """
    StatusBar {
        width: 100%;
        height: 1;
        background: $primary-background;
        color: $text;
        padding: 0 1;
    }
    #status_bar_label {
        width: 100%;
        text-align: center;
    }
    .status-section {
        margin: 0 1;
    }
    .status-section.generating {
        color: $warning;
    }
    .status-section.current {
        color: $accent;
    }
    .status-section.count {
        color: $success;
    }
    """

    status_text = reactive("Ready.")
    is_generating = reactive(False)
    current_screen = reactive("")
    scene_count = reactive(0)
    current_scene_name = reactive("None")

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._status_label: Optional[Label] = None

    def compose(self) -> None:
        """Compose the widget's children."""
        self._status_label = Label(self.status_text, id="status_bar_label")
        yield self._status_label

    def watch_status_text(self, old_value: str, new_value: str) -> None:
        """Called when status_text changes to update the label."""
        if self._status_label:
            self._status_label.update(new_value)

    def watch_is_generating(self, old_value: bool, new_value: bool) -> None:
        """Called when is_generating changes to update the status."""
        self._update_status()

    def watch_current_screen(self, old_value: str, new_value: str) -> None:
        """Called when current_screen changes to update the status."""
        self._update_status()

    def watch_scene_count(self, old_value: int, new_value: int) -> None:
        """Called when scene_count changes to update the status."""
        self._update_status()

    def watch_current_scene_name(self, old_value: str, new_value: str) -> None:
        """Called when current_scene_name changes to update the status."""
        self._update_status()

    def _update_status(self) -> None:
        """Update the status text based on all reactive attributes."""
        sections = [
            f"[Screen: {self.current_screen}]",
            f"[Generating: {'Yes' if self.is_generating else 'No'}]",
            f"[Scenes: {self.scene_count}]",
            f"[Current: {self.current_scene_name}]"
        ]
        self.status_text = " | ".join(sections)

    def update_status(self, current_app_state: "AppState") -> None:
        """Updates the status bar text based on the overall application state."""
        self.current_screen = current_app_state.current_screen
        self.is_generating = current_app_state.is_generating
        self.scene_count = len(current_app_state.scenes)
        self.current_scene_name = (
            current_app_state.current_scene.name or "Unnamed"
            if current_app_state.current_scene
            else "None"
        )

    def update_message(self, message: str) -> None:
        """Update the status message directly."""
        self.status_text = message 