from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import (
    Button,
    Label,
    Input,
    Select,
    TextArea,
    RadioSet,
    RadioButton,
    Static,
    Markdown,
)
from textual.validation import Number, Length
from textual.message import Message
from textual.binding import Binding


class NewSceneDialog(Screen):
    """Dialog for creating a new scene."""

    CSS = """
    NewSceneDialog {
        align: center middle;
        /* Additional styling if needed */
    }
    #dialog_container {
        width: auto;
        max-width: 90%;
        height: auto;
        max-height: 90%;
        background: $panel;
        padding: 2;
        border: thick $primary;
        overflow: auto; /* Make dialog scrollable if content exceeds size */
    }
    #dialog_title {
        width: 100%;
        text-align: center;
        padding-bottom: 1;
    }
    #inputs_container {
        width: auto;
        height: auto;
        overflow-y: auto; /* Make input area scrollable */
    }
    #inputs_container Horizontal {
        height: auto;
        margin-bottom: 1;
        align: left middle; /* Align label and input on the same line */
    }
    #inputs_container Label {
        width: 30%; /* Adjust label width */
        margin-right: 1;
    }
    #inputs_container Input, #inputs_container TextArea, #inputs_container Select {
        width: 68%; /* Adjust input width */
        height: auto;
    }
    #inputs_container TextArea {
        min-height: 3; /* Ensure TextArea has a minimum height */
    }
    #buttons_container {
        padding-top: 1;
        align-horizontal: right;
        width: 100%;
        height: auto;
    }
    #buttons_container Button {
        margin-left: 2;
    }
    """

    def compose(self) -> ComposeResult:
        with Container(id="dialog_container"):
            yield Label("Create New Scene", id="dialog_title")
            with Vertical(id="inputs_container"):
                with Horizontal():
                    yield Label("Scene Name:", classes="dialog_label")
                    yield Input(
                        value="Untitled Scene",
                        id="scene_name",
                        validators=[Length(minimum=1, maximum=100)],
                    )
                with Horizontal():
                    yield Label("Act Number:", classes="dialog_label")
                    yield Input(value="1", id="act_number", validators=[Number(minimum=1)])
                with Horizontal():
                    yield Label("Scene Number:", classes="dialog_label")
                    yield Input(value="1", id="scene_number", validators=[Number(minimum=1)])
                with Horizontal():
                    yield Label("Scene Premise:", classes="dialog_label")
                    yield TextArea(text="A brief, intriguing premise.", id="scene_premise")
                with Horizontal():
                    yield Label("Number of Characters (1-5):", classes="dialog_label")
                    yield Input(
                        value="2", id="num_characters", validators=[Number(minimum=1, maximum=5)]
                    )

                yield Label("Characters (one per line):")
                yield TextArea(text="Alice\nBob", id="characters")

                yield Label("Props (one per line):")
                yield TextArea(text="A mysterious letter\nA flickering candle", id="props")

                yield Label("Setting Description:")
                yield Input(
                    value="A cozy, dimly lit study with bookshelves lining the walls.",
                    id="scene_setting",
                )

                yield Label("Lighting Description:")
                yield Input(
                    value="Soft, warm light from a desk lamp, shadows in the corners.",
                    id="scene_lighting",
                )

                yield Label("Sound Description:")
                yield Input(
                    value="The gentle crackling of a fireplace, distant city hum.", id="scene_sound"
                )

                yield Label("Overall Style:")
                yield Input(value="Mystery", id="scene_style")

                yield Label("Time Period (General):")
                yield Input(value="Present Day", id="scene_period")  # Was scene_period

                yield Label("Target Audience:")
                yield Input(value="Adults", id="target_audience")

                yield Label("Target Audience (Original):", classes="dialog_label")
                yield Input(value="Adults", id="target_audience_original")

                yield Label("Setting Location:", classes="dialog_label")
                yield Input(value="An old manor", id="setting_location")

                yield Label(
                    "Time Period (Specific):", classes="dialog_label"
                )  # Was time_period (again)
                yield Input(value="Victorian Era", id="time_period")

                yield Label("Core Conflict / Goal:")
                yield Input(
                    value="Uncover a hidden secret before midnight", id="core_conflict_goal"
                )

                yield Label("Key Plot Points (one per line):")
                yield TextArea(
                    text="The protagonist discovers a cryptic message.\nThe protagonist follows a series of clues.",
                    id="key_plot_points",
                )

                yield Label("Desired Tone / Mood:")
                yield Select(
                    [
                        (t, t)
                        for t in [
                            "Suspenseful",
                            "Comedic",
                            "Dramatic",
                            "Romantic",
                            "Mysterious",
                            "Action-packed",
                        ]
                    ],
                    prompt="Select Tone",
                    id="desired_tone_mood",
                )

                yield Label("Pacing:")
                yield Select(
                    [(p, p) for p in ["Slow-burn", "Medium", "Fast-paced"]],
                    prompt="Select Pacing",
                    id="pacing",
                )

                yield Label("Generation Directives / Constraints (optional):")
                yield TextArea(
                    text="Avoid explicit content.\nInclude a twist ending.",
                    id="generation_directives",
                )

                yield Label("Quality Threshold (0.0-1.0):")
                yield Input(
                    value="0.75",
                    id="quality_threshold",
                    validators=[Number(minimum=0.0, maximum=1.0)],
                )

            with Horizontal(id="buttons_container"):
                yield Button("Create Scene", variant="primary", id="create_scene_button")
                yield Button("Cancel", id="cancel_button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "create_scene_button":
            scene_name_input = self.query_one("#scene_name", Input)
            act_number_input = self.query_one("#act_number", Input)
            scene_number_input = self.query_one("#scene_number", Input)
            scene_premise_input = self.query_one("#scene_premise", TextArea)
            num_characters_input = self.query_one("#num_characters", Input)
            characters_input = self.query_one("#characters", TextArea)
            props_input = self.query_one("#props", TextArea)
            setting_input = self.query_one("#scene_setting", Input)
            lighting_input = self.query_one("#scene_lighting", Input)
            sound_input = self.query_one("#scene_sound", Input)
            style_input = self.query_one("#scene_style", Input)
            period_input = self.query_one("#scene_period", Input)
            target_audience_input = self.query_one("#target_audience", Input)

            target_audience_original_input = self.query_one("#target_audience_original", Input)
            setting_location_input = self.query_one("#setting_location", Input)
            time_period_specific_input = self.query_one("#time_period", Input)
            core_conflict_goal_input = self.query_one("#core_conflict_goal", Input)
            key_plot_points_input = self.query_one("#key_plot_points", TextArea)
            desired_tone_mood_input = self.query_one("#desired_tone_mood", Select)
            pacing_input = self.query_one("#pacing", Select)
            generation_directives_input = self.query_one("#generation_directives", TextArea)
            quality_threshold_input = self.query_one("#quality_threshold", Input)

            all_valid = all(
                [
                    scene_name_input.is_valid,
                    act_number_input.is_valid,
                    scene_number_input.is_valid,
                    num_characters_input.is_valid,
                    setting_input.is_valid,
                    lighting_input.is_valid,
                    sound_input.is_valid,
                    style_input.is_valid,
                    period_input.is_valid,
                    target_audience_input.is_valid,
                    target_audience_original_input.is_valid,
                    setting_location_input.is_valid,
                    time_period_specific_input.is_valid,
                    core_conflict_goal_input.is_valid,
                    quality_threshold_input.is_valid,
                ]
            )

            if not all_valid:
                self.app.notify(
                    "Validation failed for one or more fields. Please check inputs.",
                    severity="error",
                    timeout=5,
                )
                return

            data = {
                "name": scene_name_input.value,
                "act_number": int(act_number_input.value) if act_number_input.value else 1,
                "scene_number": int(scene_number_input.value) if scene_number_input.value else 1,
                "premise": scene_premise_input.text,
                "num_characters": (
                    int(num_characters_input.value) if num_characters_input.value else 0
                ),
                "characters": characters_input.text.splitlines(),
                "props": props_input.text.splitlines(),
                "setting": setting_input.value,
                "lighting": lighting_input.value,
                "sound": sound_input.value,
                "style": style_input.value,
                "period": period_input.value,
                "target_audience": target_audience_input.value,
                "target_audience_original": target_audience_original_input.value,
                "setting_location": setting_location_input.value,
                "time_period": time_period_specific_input.value,
                "core_conflict_goal": core_conflict_goal_input.value,
                "key_plot_points": [
                    p.strip() for p in key_plot_points_input.text.split("\n") if p.strip()
                ],
                "desired_tone_mood": desired_tone_mood_input.value,
                "pacing": pacing_input.value,
                "generation_directives": generation_directives_input.text,
                "quality_threshold": float(quality_threshold_input.value or 0.0),
            }
            self.post_message(self.NewScene(data))
            self.app.pop_screen()
        elif event.button.id == "cancel_button":
            self.app.pop_screen()

    class NewScene(Message):
        """Message sent when a new scene is created."""

        def __init__(self, data: dict) -> None:
            super().__init__()
            self.data = data


class ConfirmDeleteDialog(Screen):
    """A dialog to confirm scene deletion."""

    CSS = """
    ConfirmDeleteDialog {
        align: center middle;
        layout: vertical;
        width: auto;
        height: auto;
        padding: 2 4;
        background: $panel;
        border: thick $primary;
    }
    #confirm_delete_question {
        width: auto;
        padding-bottom: 1;
    }
    #confirm_delete_buttons {
        width: auto;
        padding-top: 1;
        align-horizontal: right;
    }
    Button {
        margin-left: 2;
        min-width: 8;
    }
    """

    class ConfirmedDelete(Message):
        """Message sent when deletion is confirmed."""

        def __init__(self, scene_id: str):
            super().__init__()
            self.scene_id = scene_id

    def __init__(self, scene_name: str, scene_id: str):
        super().__init__()
        self.scene_name = scene_name
        self.scene_id = scene_id

    def compose(self) -> ComposeResult:
        yield Label(
            f"Are you sure you want to delete scene: '{self.scene_name}'?",
            id="confirm_delete_question",
        )
        with Horizontal(id="confirm_delete_buttons"):
            yield Button("Delete", variant="error", id="delete_confirm_button")
            yield Button("Cancel", variant="default", id="delete_cancel_button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "delete_confirm_button":
            self.post_message(self.ConfirmedDelete(self.scene_id))
            self.app.pop_screen()
        elif event.button.id == "delete_cancel_button":
            self.app.pop_screen()


class HelpScreen(Screen):
    """A screen to display help information and keyboard shortcuts."""

    BINDINGS = [Binding("escape,q", "close_help", "Close Help")]

    HELP_TEXT = """
    ## Thespian TUI Help

    This application helps you manage and generate theatrical scenes using AI.

    ### Main Interface Panels:
    - **Scene Library (Left):** Lists all your saved scenes. Click to select a scene.
    - **Scene Workspace (Top-Right):** Displays the content of the selected scene, generation progress, and quality score. You can generate or regenerate content here.
    - **Advisor Panel (Bottom-Right):** Shows feedback from various AI advisors on the scene's quality, coherence, etc.

    ### Keyboard Shortcuts:
    - **Ctrl+N:** Create a New Scene
    - **Ctrl+G:** Generate content for the current scene (or regenerate if content exists)
    - **Ctrl+S:** Save the current scene's content and data
    - **Ctrl+D:** Delete the currently selected scene (will ask for confirmation)
    - **Ctrl+Q:** Quit the application
    - **Ctrl+H:** Show this Help screen
    - **Escape / Q (in Help/Dialogs):** Close the current help screen or dialog

    ### Scene Creation:
    When creating a new scene, you'll be prompted for various details:
    - **Scene Name:** A unique identifier for your scene.
    - **Premise:** A brief summary of what the scene is about.
    - **Number of Characters:** How many main characters are in the scene.
    - **Characters:** Names of the characters.
    - **Props:** Important objects in the scene.
    - **And other details** to guide the AI generation process.

    ### Scene Generation:
    - Select a scene from the library.
    - Click the "Generate/Regenerate" button in the Scene Workspace.
    - You can stop an ongoing generation using the "Stop Generation" button.

    ### Saving and Loading:
    - Scenes are automatically saved when created or when content is generated/updated (if auto-save is configured for playwright).
    - Manual save (Ctrl+S) ensures the latest state is persisted to disk (`scenes_data` directory).
    - Scenes are loaded from the `scenes_data` directory when the application starts.
    """

    def compose(self) -> ComposeResult:
        from textual.widgets import Header, Footer
        from textual.containers import VerticalScroll

        yield Header(show_clock=True, name="Help")
        with VerticalScroll(id="help_content_scroll"):
            yield Markdown(self.HELP_TEXT)
        yield Footer()

    def action_close_help(self) -> None:
        self.app.pop_screen()
