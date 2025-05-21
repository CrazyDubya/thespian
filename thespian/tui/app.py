# /Users/pup/thespian/thespian/tui/app.py

# Previous imports should be here, ensure these are present:
from pathlib import Path
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any, List, Callable, Union, TypeVar, cast
from dataclasses import dataclass, field

from textual.app import App, ComposeResult
from textual.containers import (
    Container,
    Horizontal,
    Vertical,
)  # VerticalScroll if SceneLibrary uses it directly
from textual.widgets import (
    Header,
    Footer,
    Static,
    Button,
    ProgressBar,
    Label,
    RichLog,
    LoadingIndicator,
    Markdown,
    Tabs,
    Tab,
    ContentSwitcher,
    ListView,
    ListItem,
)
from textual.binding import Binding
from textual.worker import Worker, get_current_worker, WorkerCancelled
from textual.message import Message
from textual.screen import Screen
from textual.reactive import reactive

from rich.text import Text  # If used

# Imports from your project
from thespian.llm import LLMManager  # Assuming this and other llm components are needed
from thespian.llm.playwright import EnhancedPlaywright, SceneRequirements  # CRITICAL IMPORT
from thespian.llm.theatrical_memory import TheatricalMemory
from thespian.llm.quality_control import TheatricalQualityControl
from thespian.llm.theatrical_advisors import AdvisorManager

from .state import AppState, Scene, TUIState
from .dialogs import NewSceneDialog, ConfirmDeleteDialog, HelpScreen  # Removed EditSceneDialog

# Ensure these widgets and messages are correctly imported
from .widgets import (
    SceneLibrary,
    SceneWorkspace,
    AdvisorPanel,
    StatusBar,
    SceneSelected,
    # NewSceneDialog is imported from .dialogs
    GenerateSceneContent,
    StopGeneration,  # Correctly import top-level messages
    Widget,
)

T = TypeVar('T')

@dataclass
class TUIApp:
    """TUI application."""
    
    # State
    state: TUIState = field(default_factory=TUIState)
    
    # Widgets
    widgets: Dict[str, Widget] = field(default_factory=dict)
    
    # Callbacks
    on_exit: Optional[Callable[[], None]] = None
    
    def __post_init__(self) -> None:
        """Initialize the application."""
        self.state.on_state_change = self._handle_state_change
        
    def add_widget(self, widget: Widget) -> None:
        """Add a widget to the application."""
        self.widgets[widget.id] = widget
        
    def remove_widget(self, widget_id: str) -> None:
        """Remove a widget from the application."""
        if widget_id in self.widgets:
            del self.widgets[widget_id]
            
    def get_widget(self, widget_id: str) -> Optional[Widget]:
        """Get a widget by ID."""
        return self.widgets.get(widget_id)
        
    def render(self) -> str:
        """Render the application."""
        lines = []
        
        # Render visible widgets
        for widget in self.widgets.values():
            if widget.visible:
                rendered = widget.render()
                if rendered:
                    lines.append(rendered)
                    
        return "\n".join(lines)
        
    def handle_input(self, key: str) -> bool:
        """Handle input for the application."""
        # Handle global keys
        if key == "q":
            if self.on_exit:
                self.on_exit()
            return True
            
        # Handle widget input
        for widget in self.widgets.values():
            if widget.visible and widget.enabled:
                if widget.handle_input(key):
                    return True
                    
        return False
        
    def _handle_state_change(self) -> None:
        """Handle state changes."""
        # Update widget states based on application state
        for widget in self.widgets.values():
            if isinstance(widget, ListView):
                widget.selected_index = self.state.selected_index
                widget.scroll_position = self.state.scroll_position
                widget.visible_items = 5  # Fixed for now
                
    def get_state(self) -> Dict[str, Any]:
        """Get the application state."""
        return {
            "state": self.state.get_state(),
            "widgets": {
                widget_id: widget.get_state()
                for widget_id, widget in self.widgets.items()
            }
        }
        
    def set_state(self, state: Dict[str, Any]) -> None:
        """Set the application state."""
        if "state" in state:
            self.state.set_state(state["state"])
            
        if "widgets" in state:
            for widget_id, widget_state in state["widgets"].items():
                if widget_id in self.widgets:
                    self.widgets[widget_id].set_state(widget_state)
                    
    def run(self) -> None:
        """Run the application."""
        import curses
        
        def main(stdscr: Any) -> None:
            # Initialize curses
            curses.curs_set(0)  # Hide cursor
            stdscr.clear()
            stdscr.refresh()
            
            # Main loop
            while True:
                # Clear screen
                stdscr.clear()
                
                # Render application
                rendered = self.render()
                stdscr.addstr(0, 0, rendered)
                
                # Refresh screen
                stdscr.refresh()
                
                # Handle input
                key = stdscr.getkey()
                if not self.handle_input(key):
                    break
                    
        # Run curses application
        curses.wrapper(main)

class ThespianTUI(App[None]):  # Specify typevar for App if not returning a value on exit
    """Thespian Theater Manager TUI application."""

    BINDINGS = [
        Binding("n", "new_scene", "New Scene"),
        Binding("g", "generate", "Generate"),
        Binding("s", "save_scene_action", "Save"),
        Binding("d", "delete_scene_action", "Delete"),
        Binding("q", "quit", "Quit"),
        Binding("h", "help_screen", "Help"),
    ]
    # CSS_PATH = "app.tcss" # Uncomment if you have a TCSS file

    def __init__(self, playwright_instance: Optional[EnhancedPlaywright] = None) -> None:
        super().__init__()
        self.state: AppState = AppState()
        self.generation_worker: Optional[Worker[None]] = None

        if playwright_instance:
            self.playwright: EnhancedPlaywright = playwright_instance
        else:
            # Default initialization for standalone app run
            llm_manager: LLMManager = LLMManager()
            memory: TheatricalMemory = TheatricalMemory(db_path=Path.home() / ".thespian" / "memory.db")
            quality_control: TheatricalQualityControl = TheatricalQualityControl()
            checkpoint_dir: Path = Path.home() / ".thespian" / "checkpoints"
            checkpoint_dir.mkdir(parents=True, exist_ok=True)

            self.playwright = EnhancedPlaywright(
                name="TUI Default Playwright",
                llm_manager=llm_manager,
                memory=memory,
                quality_control=quality_control,
                llm_model_type="ollama",  # Example default
                checkpoint_dir=str(checkpoint_dir),
            )
        self.state.playwright_instance = self.playwright

    def compose(self) -> ComposeResult:
        yield Header()
        yield StatusBar(id="status_bar")
        with Container(id="main_layout_container"):
            yield SceneLibrary(id="scene_library")
            yield SceneWorkspace(id="scene_workspace")
            yield AdvisorPanel(id="advisor_panel")
        yield Footer()

    def on_mount(self) -> None:
        """Called when the app is first mounted."""
        self.app.log("--- App mounting process started. ---")
        try:
            self.app.log("--- Attempting to load all scenes... ---")
            self.state.load_all_scenes()  # Explicitly load scenes here
            self.app.log(
                f"--- Scenes loaded. Count: {len(self.state.scenes)}. Attempting to populate library. ---"
            )

            self.query_one("#scene_library", SceneLibrary).load_scenes(self.state.scenes)  # Populate library
            self.app.log("--- SceneLibrary populated. ---")

            # Select the first scene if available, or a sensible default
            if self.state.scenes:
                # Attempt to select the most recently updated scene first
                try:
                    sorted_scenes = sorted(
                        self.state.scenes.values(), key=lambda s: s.updated_at, reverse=True
                    )
                    if sorted_scenes:
                        first_scene_id = sorted_scenes[0].id
                        self.state.set_current_scene(first_scene_id)
                        self.app.log(
                            f"--- App mounted. Initially selected scene: {first_scene_id} (most recent) ---"
                        )
                    else:
                        self.app.log("--- App mounted. No scenes found after sorting. ---")
                except Exception as e:
                    self.app.log.error(
                        f"Error selecting most recent scene: {e}. Falling back to first available.",
                        exc_info=True,
                    )
                    # Fallback to just picking the first one if sorting/selection fails
                    first_scene_id = next(iter(self.state.scenes))
                    self.state.set_current_scene(first_scene_id)
                    self.app.log(
                        f"--- App mounted. Initially selected scene: {first_scene_id} (fallback) ---"
                    )
            else:
                self.app.log("--- App mounted. No scenes found to select. ---")

            self.app.log("--- Updating UI after mount. ---")
            self.update_ui()  # Initial UI update
            self.app.log("--- UI updated. ---")

        except Exception as e:
            self.app.log.error(f"CRITICAL ERROR during app mount: {e}", exc_info=True)
            self.notify(f"Mounting Error: {e}. Check logs.", severity="error", timeout=15)

        try:
            # Start periodic cleanup of old checkpoints if playwright_instance exists
            if (
                hasattr(self, "playwright_instance")
                and self.playwright_instance
                and hasattr(self.playwright_instance, "CHECKPOINT_TTL_SECONDS")
                and hasattr(self.playwright_instance, "_cleanup_old_checkpoints")
            ):
                self.set_interval(
                    self.playwright_instance.CHECKPOINT_TTL_SECONDS,
                    self.playwright_instance._cleanup_old_checkpoints,
                )
                self.app.log("--- Periodic playwright checkpoint cleanup scheduled. ---")
            else:
                self.app.log.warning(
                    "--- Playwright instance or its checkpoint methods not fully available for cleanup scheduling. ---"
                )
        except Exception as e:
            self.app.log.error(f"Error scheduling checkpoint cleanup: {e}", exc_info=True)
            self.notify(f"Checkpoint Cleanup Error: {e}", severity="warning", timeout=10)

        self.app.log("--- App mounting process completed. ---")

    def update_ui(self) -> None:
        """Updates all relevant parts of the UI based on the current state."""
        self.query_one("#scene_library", SceneLibrary).load_scenes(self.state.scenes)
        self.query_one("#scene_workspace", SceneWorkspace).update_workspace(
            self.state.current_scene_id
        )
        feedback = getattr(
            self.state.current_scene, "advisor_feedback", {}
        )
        self.query_one("#advisor_panel", AdvisorPanel).update_feedback(feedback)
        self.query_one("#status_bar", StatusBar).update_status(self.state)

        # Highlight current scene in SceneLibrary's ListView
        scene_lib = self.query_one("#scene_library", SceneLibrary)
        try:
            list_view = scene_lib.query_one("#scene_library_list_view", ListView)
            current_idx = -1
            if self.state.current_scene_id:
                for i, item_widget in enumerate(list_view.children):
                    if (
                        hasattr(item_widget, "scene_id")
                        and item_widget.scene_id == self.state.current_scene_id
                    ):
                        current_idx = i
                        break
            list_view.index = current_idx if current_idx != -1 else None
        except Exception as e:
            self.app.log.error(f"Error updating SceneLibrary highlight: {e}")

    async def action_new_scene(self) -> None:
        """Show the new scene dialog."""
        await self.push_screen(NewSceneDialog())

    def on_new_scene_dialog_new_scene(self, message: NewSceneDialog.NewScene) -> None:
        """Handle the creation of a new scene from the dialog."""
        self.app.log.info(
            f"--- on_new_scene_dialog_new_scene: Received message. Data: {message.data} ---"
        )
        try:
            self.app.log.info(
                "--- on_new_scene_dialog_new_scene: Attempting to add scene to state... ---"
            )
            new_scene = self.state.add_scene(message.data)  # message.data is dialog_requirements
            self.app.log.info(
                f"--- on_new_scene_dialog_new_scene: Scene added/retrieved: ID {new_scene.id}, Name: {new_scene.name} ---"
            )

            self.app.log.info("--- on_new_scene_dialog_new_scene: Updating status bar... ---")
            self.query_one("#status_bar", StatusBar).update_message(f"Scene '{new_scene.name}' created.")
            self.app.log.info("--- on_new_scene_dialog_new_scene: Status bar updated. ---")

            self.app.log.info(
                "--- on_new_scene_dialog_new_scene: Setting current scene in state... ---"
            )
            self.state.set_current_scene(new_scene.id)
            self.app.log.info(
                f"--- on_new_scene_dialog_new_scene: Current scene set to {new_scene.id}. ---"
            )

            self.app.log.info("--- on_new_scene_dialog_new_scene: Calling update_ui()... ---")
            self.update_ui()  # This will reload scenes in library and update workspace
            self.app.log.info("--- on_new_scene_dialog_new_scene: update_ui() called. ---")

            # Focus the new scene in the list view
            self.app.log.info(
                "--- on_new_scene_dialog_new_scene: Attempting to focus new scene in list... ---"
            )
            list_view = self.query_one("#scene_library", SceneLibrary).query_one("#scene_library_list_view", ListView)
            for index, item in enumerate(list_view.children):
                if hasattr(item, "scene_id") and item.scene_id == new_scene.id:
                    list_view.index = index
                    self.app.log.info(
                        f"--- on_new_scene_dialog_new_scene: Found scene at index {index}, setting ListView index. ---"
                    )
                    break
            if list_view.index is not None:  # Only focus if found
                self.app.log.info("--- on_new_scene_dialog_new_scene: Focusing ListView. ---")
                list_view.focus()
            self.app.log.info(
                "--- on_new_scene_dialog_new_scene: Scene creation process complete. ---"
            )
        except Exception as e:
            self.app.log.error(
                f"--- on_new_scene_dialog_new_scene: EXCEPTION during scene creation: {e} ---",
                exc_info=True,
            )
            self.notify(f"Error creating scene: {e}", severity="error")
            self.app.log.error(f"Error creating scene (re-log post-notify): {e}", exc_info=True)

    # -------------------------------------------------------------------------
    # Message Handlers
    # -------------------------------------------------------------------------
    async def on_scene_selected(self, message: SceneSelected) -> None:
        """Handle scene selection from the library."""
        self.app.log(f"--- SceneSelected message received: scene_id={message.scene_id} ---")
        self.action_select_scene(message.scene_id)

    async def on_stop_generation(self, message: StopGeneration) -> None:
        """Handle request to stop scene generation."""
        self.app.log("--- Stop Generation message received in App ---")
        if self.playwright_instance and self.state.is_generating:
            # TODO: Implement self.playwright_instance.stop_generation()
            self.state.is_generating = False
            self.state.error_message = "Generation stopped by user."
            # If SceneWorkspace has a set_generating_state method, call it:
            # scene_workspace = self.query_one(SceneWorkspace)
            # scene_workspace.set_generating_state(False)
            self.query_one("#status_bar", StatusBar).update_status(self.state)
            self.notify(
                "Scene generation stopped (TODO: implement interruption).", severity="warning"
            )
        else:
            self.notify("Nothing to stop.", severity="warning")

    async def on_generate_scene_content(self, message: GenerateSceneContent) -> None:
        """Handle request to generate scene content from workspace."""
        self.app.log(
            f"--- GenerateSceneContent message received for scene_id: {message.scene_id} ---"
        )
        if not message.scene_id:
            self.notify("No scene ID provided for generation.", severity="error")
            return
        # Offload the actual generation to an async worker or ensure _initiate_generation is async friendly
        # For now, assuming _initiate_generation can be called directly if it's quick or properly awaited/threaded itself.
        self._initiate_generation(
            message.scene_id
        )  # This method might need to become async or run in a worker

    # -------------------------------------------------------------------------
    # Internal Helper Methods
    # -------------------------------------------------------------------------
    def _initiate_generation(self, scene_id: Optional[str]) -> None:
        """Validates and starts the scene generation worker."""
        self.app.log(
            f"--- _initiate_generation called with scene_id: {scene_id} (type: {type(scene_id)}) ---"
        )

        if not scene_id:
            self.app_notify(
                "Error: Cannot initiate generation without a scene ID.", severity="error"
            )
            self.app_log("--- _initiate_generation ERROR: scene_id is None or empty. Aborting. ---")
            return

        if self.state.is_generating:
            self.app_notify("Generation already in progress.", severity="warning")
            self.app_log(
                "--- _initiate_generation WARNING: Generation already in progress. Aborting. ---"
            )
            return

        scene_workspace = self.query_one("#scene_workspace", SceneWorkspace)
        scene_workspace.update_status("Initiating generation...")
        scene_workspace.is_generating = True  # Set generating flag

        # Log before calling run_worker
        self.app.log(
            f"--- _initiate_generation: About to run worker for _run_generation with scene_id: {scene_id} ---"
        )
        try:
            # Ensure the scene_id is explicitly passed as an argument to the worker function
            self.generation_worker = self.run_worker(
                self._run_generation, scene_id, name=f"gen-{scene_id[:8]}"
            )
            self.app.log(f"--- _initiate_generation: Worker started: {self.generation_worker} ---")
        except Exception as e:
            self.app_log(
                f"--- _initiate_generation ERROR: Failed to start worker: {e} ---", level="error"
            )
            scene_workspace.is_generating = False  # Reset flag on error
            self.app_notify(f"Failed to start generation worker: {e}", severity="error")

    async def _run_generation(self, scene_id: str) -> None:
        """Handles the asynchronous scene generation process.
        This method is run in a worker thread.
        """
        scene_workspace = self.query_one("#scene_workspace", SceneWorkspace)  # This is fine, getting a reference
        scene_workspace.generation_in_progress = True
        scene_workspace.update_status("Starting generation...")
        self.app_log(f"--- _run_generation: Starting for scene_id: {scene_id} ---")

        scene = self.state.get_scene(scene_id)
        if not scene:
            self.app_log.error(f"--- _run_generation: Scene {scene_id} not found. Aborting. ---")
            scene_workspace.update_status(f"Error: Scene {scene_id} not found.")
            scene_workspace.generation_in_progress = False
            return

        self.app_log(
            f"--- _run_generation: Scene '{scene.name}' found. Preparing requirements. ---"
        )
        scene.status = (
            "generating"  # Update status in Scene object itself (data model change, not direct UI)
        )
        self.update_ui()  # Reflect status change in UI

        # Prepare requirements for SceneRequirements Pydantic model
        requirements_data = {
            # Direct attributes from Scene model
            "setting": scene.setting,
            "characters": scene.characters,
            "props": scene.props,
            "lighting": scene.lighting,
            "sound": scene.sound,
            "style": scene.style,
            "period": scene.period,
            "target_audience": scene.target_audience,
            "act_number": scene.act_number,
            "scene_number": scene.scene_number,
            "premise": scene.premise,  # Added to Scene and SceneRequirements
        }

        # Add relevant fields from scene.additional_requirements
        additional_reqs = scene.additional_requirements or {}
        self.app_log(f"--- _run_generation: Scene.additional_requirements: {additional_reqs} ---")

        requirements_data["pacing"] = additional_reqs.get("pacing")
        requirements_data["tone"] = additional_reqs.get("tone")
        requirements_data["emotional_arc"] = additional_reqs.get("emotional_arc")
        requirements_data["key_conflict"] = additional_reqs.get("core_conflict_goal")  # Mapping
        requirements_data["resolution"] = additional_reqs.get("resolution")
        requirements_data["generation_directives"] = additional_reqs.get("generation_directives")
        requirements_data["model_type"] = additional_reqs.get(
            "llm_model_type", additional_reqs.get("model_type")
        )

        requirements_data = {k: v for k, v in requirements_data.items() if v is not None}

        self.app_log(
            f"--- _run_generation: Final requirements_data for SceneRequirements: {requirements_data} ---"
        )

        try:
            requirements_obj = SceneRequirements(**requirements_data)
            self.app_log(
                f"--- _run_generation: SceneRequirements object created: {requirements_obj.model_dump_json(indent=2)} ---"
            )
        except ValidationError as ve:
            self.app_log.error(
                f"--- _run_generation: Validation_Error creating SceneRequirements for scene '{scene.name}': {ve} ---",
                exc_info=True,
            )
            error_details = ve.errors()
            error_messages = [
                f"{err['loc'][0] if err['loc'] else 'General'}: {err['msg']}"
                for err in error_details
            ]
            scene_workspace.update_status(
                f"Validation Error: {'; '.join(error_messages)}. Check logs."
            )
            scene_workspace.generation_in_progress = False
            scene.status = "error"
            self.update_ui()
            return
        except Exception as e:
            self.app_log.error(
                f"--- _run_generation: Unexpected error creating SceneRequirements for scene '{scene.name}': {e} ---",
                exc_info=True,
            )
            scene.content = f"Error during generation: {str(e)}"
            scene.generation_log.append(f"[{datetime.now().isoformat()}] Generation error: {e}")
            scene.status = "error"
            scene_workspace.update_status(f"Error: {e}. Check logs.")
            scene_workspace.generation_in_progress = False
            return

        try:
            if not self.playwright_instance:
                self.app_log.warning(
                    "--- _run_generation: Playwright instance not initialized. Attempting init. ---"
                )
                # _initialize_playwright is async, so we need to run it in the main event loop from the worker
                # However, direct await from a sync worker is problematic. This init should ideally happen before starting worker.
                # For now, if it's not there, we might have to fail or reconsider init strategy.
                # Let's assume _initialize_playwright was called in on_mount or similar main-thread context.
                if not self.playwright_instance:
                    self.app_log.error(
                        "--- _run_generation: Playwright instance STILL not available. Critical init failure. Aborting. ---"
                    )
                    scene_workspace.update_status("Playwright Error. Check logs.")
                    scene_workspace.generation_in_progress = False
                    return

            self.app_log(
                f"--- _run_generation: Calling playwright.generate_scene_content for '{scene.name}' ---"
            )
            scene_workspace.update_status(f"Generating '{scene.name}'...")

            # Define the actual callback function that will be invoked by playwright
            def progress_callback_adapter(progress_data: Dict[str, Any]):
                self._handle_generation_progress(scene_id, progress_data)

            # playwright_instance.generate_scene_content is assumed to be a blocking call here if run in a worker.
            # If it's async, _run_generation shouldn't be run in a worker with thread=True but managed by asyncio.
            # For now, proceeding with assumption it's blocking or internally manages its async operations appropriately for this call.
            generated_content_data = await self.playwright_instance.generate_scene_content(
                requirements=requirements_obj,
                story_outline=self.state.story_outline,
                previous_scenes=self.state.get_previous_scenes_summary(
                    scene.act_number, scene.scene_number
                ),
                progress_callback=progress_callback_adapter,
            )

            self.app_log(
                f"--- _run_generation: Generation completed for '{scene.name}'. Content data received. ---"
            )

            if generated_content_data:
                scene.content = generated_content_data.get("text", "")
                scene.quality_score = generated_content_data.get("quality_score")
                scene.critique = generated_content_data.get("critique")
                scene.generation_log.append(
                    f"[{datetime.now().isoformat()}] Generation successful. Score: {scene.quality_score}"
                )
                scene.status = "completed"
                self.app_log(
                    f"--- _run_generation: Scene '{scene.name}' updated. Score: {scene.quality_score} ---"
                )
            else:
                scene.content = "Error: No content generated or generation failed."
                scene.generation_log.append(
                    f"[{datetime.now().isoformat()}] Generation failed or returned no data."
                )
                scene.status = "error"
                self.app_log.error(
                    f"--- _run_generation: No content data received for '{scene.name}'. ---"
                )

        except Exception as e:
            self.app_log.error(
                f"--- _run_generation: Error during generation for scene '{scene.name}': {e} ---",
                exc_info=True,
            )
            scene.content = f"Error during generation: {str(e)}"
            scene.generation_log.append(f"[{datetime.now().isoformat()}] Generation error: {e}")
            scene.status = "error"
            scene_workspace.update_status(f"Error: {e}. Check logs.")
        finally:
            scene.update_timestamp()
            self.state.save_scene(scene.id)  # state method, not direct UI
            scene_workspace.generation_in_progress = False
            self.update_ui()
            self.app_log(
                f"--- _run_generation: Process finished for scene '{scene.name}'. Status: {scene.status} ---"
            )

    def _handle_generation_progress(self, scene_id: str, progress_data: Dict[str, Any]):
        """Handles progress updates from the generation process.
        This method is called via call_from_thread from the worker.
        """
        # progress_data might contain fields like 'current_step', 'total_steps', 'message', 'phase'
        self.app_log(
            f"--- _handle_generation_progress: Scene ID {scene_id}, Data: {progress_data} ---"
        )
        scene_workspace = self.query_one("#scene_workspace", SceneWorkspace)

        message = progress_data.get("message", "")
        current_step = progress_data.get("current_step")
        total_steps = progress_data.get("total_steps")
        phase = progress_data.get("phase")  # e.g., 'drafting', 'critiquing'

        status_update = f"Generating '{self.state.get_scene(scene_id).name if self.state.get_scene(scene_id) else scene_id}'"
        if phase:
            status_update += f" - Phase: {phase}"
        if message:
            status_update += f" - {message}"

        if current_step is not None and total_steps is not None and total_steps > 0:
            progress_percent = int((current_step / total_steps) * 100)
            status_update += f" ({progress_percent}%)"
            scene_workspace.update_progress(progress_percent)
        else:
            scene_workspace.update_progress(None)  # Indeterminate or no percentage

        scene_workspace.update_status(status_update)
        # Potentially update a progress bar or other more specific UI elements here.

    # --- Action methods for key bindings ---
    async def action_generate(self) -> None:
        """Bound to 'g'. Generate content for the current scene."""
        if self.state.current_scene:
            self._initiate_generation(self.state.current_scene.id)
        else:
            self.notify("No scene selected to generate.", severity="error")

    async def action_save_scene_action(self) -> None:
        """Saves the currently selected scene's content from the workspace."""
        self.app.log.info("--- action_save_scene_action: Triggered. ---")
        if self.state.current_scene_id:
            current_scene = self.state.get_scene(self.state.current_scene_id)
            if current_scene:
                workspace = self.query_one("#scene_workspace", SceneWorkspace)
                # Assuming workspace.current_content_text_area holds the latest text
                current_scene.content = workspace.current_content_text_area.text
                current_scene.update_timestamp()
                self.state.save_scene(current_scene)
                msg = f"Scene '{current_scene.name}' saved."
                self.query_one("#status_bar", StatusBar).update_message(msg)
                self.notify(msg)
                self.app.log.info(f"--- action_save_scene_action: {msg} ---")
            else:
                self.notify("No current scene object found to save.", severity="warning")
                self.app.log.warning(
                    "--- action_save_scene_action: Current scene object not found. ---"
                )
        else:
            self.notify("No scene selected to save.", severity="warning")
            self.app.log.warning("--- action_save_scene_action: No current_scene_id. ---")

    async def action_delete_scene_action(self) -> None:
        """Handles the deletion of the selected scene after confirmation."""
        self.app.log.info("--- action_delete_scene_action: Triggered. ---")
        if self.state.current_scene_id:
            scene_del = self.state.get_scene(self.state.current_scene_id)
            if scene_del:
                self.app.log.info(
                    f"--- action_delete_scene_action: Pushing ConfirmDeleteDialog for scene {scene_del.id} ({scene_del.name}). ---"
                )
                await self.push_screen(ConfirmDeleteDialog(scene_del.name, scene_del.id))
            else:
                self.notify("Scene to delete not found.", severity="error")
                self.app.log.error(
                    f"--- action_delete_scene_action: Scene {self.state.current_scene_id} not found in state for deletion. ---"
                )
        else:
            self.notify("No scene selected to delete.", severity="warning")
            self.app.log.warning("--- action_delete_scene_action: No current_scene_id. ---")

    def on_confirm_delete_dialog_confirmed_delete(
        self, message: ConfirmDeleteDialog.ConfirmedDelete
    ) -> None:
        """Handle the actual deletion after dialog confirmation."""
        self.app.log.info(
            f"--- on_confirm_delete_dialog_confirmed_delete: Received confirmation to delete scene ID: {message.scene_id} ---"
        )
        scene_being_deleted = self.state.get_scene(
            message.scene_id
        )  # Get scene object before deleting its state
        scene_name = scene_being_deleted.name if scene_being_deleted else "Unknown Scene"

        self.state.delete_scene(message.scene_id)
        self.query_one("#scene_library", SceneLibrary).remove_scene_from_list(message.scene_id)

        msg = f"Scene '{scene_name}' deleted."
        self.query_one("#status_bar", StatusBar).update_message(msg)
        self.notify(msg)
        self.app.log.info(f"--- on_confirm_delete_dialog_confirmed_delete: {msg} ---")
        self.update_ui()

    async def action_help_screen(self) -> None:
        """Show the help screen."""
        self.app.log("--- Show Help action triggered ---")
        self.push_screen(HelpScreen())

    async def on_stop_generation(self, message: StopGeneration) -> None:
        """Handle request to stop scene generation."""
        self.app.log("--- Stop Generation message received in App ---")
        if self.playwright_instance and self.state.is_generating:
            self.playwright_instance.stop_generation()  # Assuming playwright has such a method
            self.state.is_generating = False
            self.state.error_message = "Generation stopped by user."
            self.query_one("#scene_workspace", SceneWorkspace).set_generating_state(False)
            self.query_one("#status_bar", StatusBar).update_status(self.state)
            self.notify("Scene generation stopped.")
        else:
            self.notify("Nothing to stop.", severity="warning")

    async def on_generate_scene_content(self, message: GenerateSceneContent) -> None:
        """Handle request to generate scene content from workspace."""
        self.app.log(
            f"--- GenerateSceneContent message received for scene_id: {message.scene_id} ---"
        )
        if not message.scene_id:
            self.notify("No scene ID provided for generation.", severity="error")
            return
        self._initiate_generation(message.scene_id)


# --- Entry point for running the TUI directly ---
if __name__ == "__main__":
    # This setup is for running app.py directly (e.g., python -m thespian.tui.app)
    # It provides default instances for dependencies.
    # Adjust paths and configurations as necessary for your environment.

    # Ensure project root is in Python path if running as script
    # (not strictly necessary if running as module 'python -m ...')
    # import sys
    # project_root = Path(__file__).resolve().parents[2] # Adjust if structure differs
    # if str(project_root) not in sys.path:
    #    sys.path.insert(0, str(project_root))

    from thespian.llm.manager import LLMManager
    from thespian.llm.theatrical_memory import TheatricalMemory
    from thespian.llm.quality_control import TheatricalQualityControl
    from thespian.llm.playwright import EnhancedPlaywright

    # Create a default home directory for Thespian app data if it doesn't exist
    thespian_home = Path.home() / ".thespian"
    thespian_home.mkdir(parents=True, exist_ok=True)

    default_llm_manager = LLMManager()
    default_memory = TheatricalMemory(db_path=thespian_home / "thespian_standalone_memory.db")
    default_quality_control = TheatricalQualityControl()
    default_checkpoint_dir = thespian_home / "checkpoints_standalone"
    default_checkpoint_dir.mkdir(parents=True, exist_ok=True)

    default_playwright = EnhancedPlaywright(
        name="Standalone TUI Playwright",
        llm_manager=default_llm_manager,
        memory=default_memory,
        quality_control=default_quality_control,
        llm_model_type="ollama",
        checkpoint_dir=str(default_checkpoint_dir),
    )

    app = ThespianTUI(playwright_instance=default_playwright)
    app.run()
