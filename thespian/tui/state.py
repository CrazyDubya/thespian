from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Union, TypeVar, cast
from datetime import datetime
import uuid
import json
from pathlib import Path
from dataclasses import fields, asdict

SCENES_DIR = Path("scenes_data")

T = TypeVar('T')


@dataclass
class Scene:
    """Represents a scene in the system."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "Untitled Scene"  # Changed from title to name to match dialog
    act_number: int = 1
    scene_number: int = 1
    premise: str = ""

    # Core descriptive elements that are also high-level requirements
    setting: str = ""  # Overall setting description
    characters: List[str] = field(default_factory=list)
    num_characters: Optional[int] = None  # Can be derived from len(characters) or specified
    props: List[str] = field(default_factory=list)
    lighting: str = ""
    sound: str = ""
    style: str = ""  # e.g., Film Noir, Shakespearean
    period: str = ""  # e.g., Victorian England, Present Day. This will store the 'primary' period.
    target_audience: str = ""

    # Generated content and metadata
    content: str = ""
    generation_log: List[str] = field(default_factory=list)
    quality_score: Optional[float] = 0.0  # Ensured default
    critique: Optional[str] = None
    suggestions: List[str] = field(default_factory=list)
    advisor_feedback: Dict[str, Any] = field(default_factory=dict)

    # All other fields from the dialog that guide generation but aren't top-level attributes.
    # This will store fields like 'setting_location', 'time_period' (if different from main period),
    # 'target_audience_original', 'core_conflict_goal', 'key_plot_points', 'desired_tone_mood',
    # 'pacing', 'generation_directives', 'quality_threshold'.
    additional_requirements: Dict[str, Any] = field(default_factory=dict)

    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if self.num_characters is None and self.characters:
            self.num_characters = len(self.characters)
        elif self.num_characters is not None and not self.characters and self.num_characters > 0:
            self.characters = [f"Character {i+1}" for i in range(self.num_characters)]
        elif (
            self.num_characters is not None
            and self.characters
            and self.num_characters != len(self.characters)
        ):
            print(
                f"Warning: Scene '{self.name}' (ID: {self.id}) has num_characters={self.num_characters} but {len(self.characters)} names listed."
            )

    def to_dict(self) -> Dict[str, Any]:
        """Convert scene to a dictionary for JSON serialization."""
        data = {
            "id": self.id,
            "name": self.name,
            "act_number": self.act_number,
            "scene_number": self.scene_number,
            "premise": self.premise,
            "setting": self.setting,
            "characters": self.characters,
            "num_characters": self.num_characters,
            "props": self.props,
            "lighting": self.lighting,
            "sound": self.sound,
            "style": self.style,
            "period": self.period,
            "target_audience": self.target_audience,
            "content": self.content,
            "generation_log": self.generation_log,
            "quality_score": self.quality_score,
            "critique": self.critique,
            "suggestions": self.suggestions,
            "advisor_feedback": self.advisor_feedback,
            "additional_requirements": self.additional_requirements,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Scene":
        """Create a Scene object from a dictionary, handling datetime fields appropriately."""
        # Handle datetime fields: if they exist as strings, parse them.
        # Otherwise, let the dataclass __init__ handle defaults.
        for field_name in ["created_at", "updated_at"]:
            if field_name in data and isinstance(data[field_name], str):
                try:
                    data[field_name] = datetime.fromisoformat(data[field_name])
                except ValueError:
                    # If parsing fails (e.g., not a valid ISO string), remove it to allow default_factory
                    # or log an error if this field is expected to be a valid string from certain sources.
                    # For now, removing to allow default factory seems safest for new scene creation.
                    del data[field_name]
            elif field_name in data and not isinstance(data[field_name], datetime):
                # If it's present but not a string or datetime, it's an unexpected type.
                # Remove it to let default_factory take over to avoid constructor errors.
                del data[field_name]

        # Ensure fields expected by Scene dataclass but not necessarily in dialog data (like 'content', 'status')
        # are handled by dataclass defaults if not present in 'data'.
        # The **data spread will pass through all relevant fields from the dialog.
        # Fields like id, created_at, updated_at will use default_factory if not in data after above processing.

        # Collect all keys that are valid field names for the Scene dataclass
        valid_scene_fields = {f.name for f in fields(cls)}
        filtered_data = {k: v for k, v in data.items() if k in valid_scene_fields}

        # Any other keys in `data` (from dialog) that are not direct Scene fields
        # should go into `additional_requirements`.
        additional_reqs_data = {k: v for k, v in data.items() if k not in valid_scene_fields}
        if additional_reqs_data:
            filtered_data["additional_requirements"] = additional_reqs_data

        return cls(**filtered_data)


@dataclass
class AppState:
    """Global application state."""

    current_screen: str = "welcome"
    current_scene: Optional[Scene] = None
    scenes: Dict[str, Scene] = field(default_factory=dict)
    model_name: str = "ollama/mistral"
    is_generating: bool = False
    generation_progress: float = 0.0
    error_message: Optional[str] = None

    def __post_init__(self):
        SCENES_DIR.mkdir(parents=True, exist_ok=True)
        # Removed load_all_scenes() from here to be more explicit in TUI on_mount
        # self.load_all_scenes()
        print(
            ">>> AppState.__post_init__: SCENES_DIR ensured. Scene loading deferred to app.on_mount. <<<"
        )

    def add_scene(self, scene_data: Dict[str, Any]) -> Scene:
        """Add a new scene from data, store it, and return the Scene object."""
        print(f"--- AppState.add_scene: Received data: {scene_data} ---")
        try:
            new_scene = Scene.from_dict(scene_data)
            print(
                f"--- AppState.add_scene: Scene.from_dict successful. Scene ID: {new_scene.id}, Name: {new_scene.name} ---"
            )
        except Exception as e:
            print(f"--- AppState.add_scene: EXCEPTION in Scene.from_dict: {e} ---")
            import traceback

            traceback.print_exc()
            raise

        if new_scene.id in self.scenes:
            print(
                f"--- AppState.add_scene: Scene ID '{new_scene.id}' already exists. Overwriting. ---"
            )
        self.scenes[new_scene.id] = new_scene

        try:
            print(f"--- AppState.add_scene: Attempting to save scene {new_scene.id} ---")
            self.save_scene(new_scene)  # Persist the newly created scene
            print(f"--- AppState.add_scene: Scene {new_scene.id} saved successfully. ---")
        except Exception as e:
            print(f"--- AppState.add_scene: EXCEPTION in self.save_scene: {e} ---")
            import traceback

            traceback.print_exc()
            raise

        return new_scene

    def remove_scene(self, scene_id: str) -> None:
        """Remove a scene from the state."""
        print(f">>> AppState.remove_scene: Attempting to remove scene ID '{scene_id}' <<<")
        if scene_id in self.scenes:
            del self.scenes[scene_id]
            file_path = SCENES_DIR / f"{scene_id}.json"
            if file_path.exists():
                file_path.unlink()
                print(f">>> AppState.remove_scene: Deleted file {file_path} <<<")
            if self.current_scene and self.current_scene.id == scene_id:
                self.current_scene = None
                print(
                    f">>> AppState.remove_scene: Cleared current_scene as it was the one removed. <<<"
                )
            print(f">>> AppState.remove_scene: Scene ID '{scene_id}' removed successfully. <<<")
        else:
            print(f">>> AppState.remove_scene: Scene ID '{scene_id}' not found in self.scenes. <<<")

    def set_current_scene(self, scene_id: str) -> None:
        """Set the current scene."""
        print(f">>> AppState.set_current_scene: Setting current scene to ID '{scene_id}' <<<")
        if scene_id in self.scenes:
            self.current_scene = self.scenes[scene_id]
        else:
            print(
                f">>> AppState.set_current_scene: Scene ID '{scene_id}' not found. Current scene not changed. <<<"
            )

    def update_scene(self, scene_id: str, **updates) -> None:
        """Update a scene's attributes."""
        print(
            f">>> AppState.update_scene: Updating scene ID '{scene_id}' with updates: {updates} <<<"
        )
        if scene_id in self.scenes:
            scene = self.scenes[scene_id]
            for key, value in updates.items():
                setattr(scene, key, value)
            scene.updated_at = datetime.now()
            if self.current_scene and self.current_scene.id == scene_id:
                self.current_scene = scene  # Ensure current_scene reflects updates
            self.save_scene(scene)  # Persist updated scene
            print(f">>> AppState.update_scene: Scene ID '{scene_id}' updated and saved. <<<")
        else:
            print(f">>> AppState.update_scene: Scene ID '{scene_id}' not found for update. <<<")

    def save_scene(self, scene: Scene) -> None:
        """Save a single scene to a JSON file."""
        if not scene:
            print(">>> AppState.save_scene: Attempted to save a None scene. Skipping. <<<")
            return
        SCENES_DIR.mkdir(parents=True, exist_ok=True)
        file_path = SCENES_DIR / f"{scene.id}.json"
        scene.updated_at = datetime.now()  # Ensure updated_at is current
        print(f">>> AppState.save_scene: Saving scene ID '{scene.id}' to {file_path} <<<")
        try:
            with open(file_path, "w") as f:
                json.dump(scene.to_dict(), f, indent=4)
            print(f">>> AppState.save_scene: Scene ID '{scene.id}' saved successfully. <<<")
        except Exception as e:
            print(
                f">>> AppState.save_scene: ERROR saving scene ID '{scene.id}' to {file_path}: {e} <<<"
            )

    def load_all_scenes(self) -> None:
        """Load all scenes from the scenes_data directory."""
        print("\n>>> AppState.load_all_scenes: Starting scene load. <<<")
        if not SCENES_DIR.exists():
            print(">>> AppState.load_all_scenes: SCENES_DIR does not exist. Creating it. <<<")
            try:
                SCENES_DIR.mkdir(parents=True, exist_ok=True)  # Ensure it exists
                print(">>> AppState.load_all_scenes: SCENES_DIR created successfully. <<<")
            except Exception as e:
                print(
                    f">>> AppState.load_all_scenes: CRITICAL ERROR - Could not create SCENES_DIR at {SCENES_DIR}: {e} <<<"
                )
                # If directory creation fails, we cannot proceed with loading.
                # Consider how to notify the TUI or handle this critical failure.
                return
            return  # Nothing to load if it was just created

        # Clear existing scenes dictionary before loading to prevent duplicates from multiple calls
        if self.scenes:  # Check if there's anything to clear
            print(
                f">>> AppState.load_all_scenes: Clearing {len(self.scenes)} existing scenes from self.scenes dict. Current keys: {list(self.scenes.keys())} <<<"
            )
            self.scenes.clear()
        else:
            print(
                ">>> AppState.load_all_scenes: No existing scenes in self.scenes dict to clear. <<<"
            )

        loaded_count = 0
        corrupted_files = 0
        print(f">>> AppState.load_all_scenes: Globbing files in {SCENES_DIR} <<<")
        scene_files = list(SCENES_DIR.glob("*.json"))
        print(
            f">>> AppState.load_all_scenes: Found {len(scene_files)} potential scene files: {scene_files} <<<"
        )

        for file_path in scene_files:
            print(f">>> AppState.load_all_scenes: Processing file {file_path} <<<")
            try:
                with open(file_path, "r") as f:
                    try:
                        data = json.load(f)
                    except json.JSONDecodeError as jde:
                        print(
                            f">>> AppState.load_all_scenes: JSON DECODE ERROR for file {file_path}: {jde}. Skipping this file. <<<"
                        )
                        corrupted_files += 1
                        continue  # Skip to the next file

                scene_id_from_file = data.get("id")
                scene_title_from_file = data.get("name", "Untitled")  # Get title for logging
                if not scene_id_from_file:
                    print(
                        f">>> AppState.load_all_scenes: SKIPPING file {file_path} (name: '{scene_title_from_file}') due to missing 'id' in JSON content. <<<"
                    )
                    corrupted_files += 1
                    continue

                # Additional validation for required fields like created_at, updated_at before Scene.from_dict
                if "created_at" not in data or "updated_at" not in data:
                    print(
                        f">>> AppState.load_all_scenes: SKIPPING file {file_path} (ID: {scene_id_from_file}, name: '{scene_title_from_file}') due to missing 'created_at' or 'updated_at'. <<<"
                    )
                    corrupted_files += 1
                    continue

                scene = Scene.from_dict(data)
                if scene.id in self.scenes:
                    print(
                        f">>> AppState.load_all_scenes: WARNING - Scene ID '{scene.id}' (name: '{scene.name}') from file {file_path} ALREADY EXISTS. Overwriting with content from {file_path}. <<<"
                    )
                else:
                    print(
                        f">>> AppState.load_all_scenes: Adding new scene with ID '{scene.id}' (name: '{scene.name}') from file {file_path}. <<<"
                    )
                self.scenes[scene.id] = scene
                loaded_count += 1
            except FileNotFoundError:
                print(
                    f">>> AppState.load_all_scenes: FILE NOT FOUND ERROR for file {file_path}. This shouldn't happen if globbed correctly. Skipping. <<<"
                )
                corrupted_files += 1
            except (KeyError, TypeError, ValueError) as e:
                # Catch errors from Scene.from_dict or missing critical fields after initial checks
                print(
                    f">>> AppState.load_all_scenes: ERROR processing scene data from {file_path} (ID: {data.get('id', 'N/A')}, name: '{data.get('name', 'N/A')}'): {type(e).__name__} - {e}. Skipping this file. <<<"
                )
                corrupted_files += 1
            except Exception as e:
                # Catch-all for other unexpected errors during file processing
                print(
                    f">>> AppState.load_all_scenes: UNEXPECTED ERROR processing file {file_path} (ID: {data.get('id', 'N/A')}, name: '{data.get('name', 'N/A')}'): {type(e).__name__} - {e}. Skipping this file. <<<"
                )
                corrupted_files += 1
        print(
            f">>> AppState.load_all_scenes: Finished loading. Successfully loaded: {loaded_count}. Corrupted/Skipped files: {corrupted_files}. Total scenes in dict: {len(self.scenes)}. Keys: {list(self.scenes.keys())} <<<"
        )


@dataclass
class TUIState:
    """State management for the TUI."""
    
    # State tracking
    current_view: str = "main"
    current_act: int = 1
    current_scene: int = 1
    is_processing: bool = False
    error_message: Optional[str] = None
    
    # Navigation history
    view_history: List[str] = field(default_factory=list)
    act_history: List[int] = field(default_factory=list)
    scene_history: List[int] = field(default_factory=list)
    
    # UI state
    selected_index: int = 0
    scroll_position: int = 0
    max_scroll: int = 0
    
    # Callbacks
    on_state_change: Optional[Callable[[], None]] = None
    
    def set_view(self, view: str) -> None:
        """Set the current view and update history."""
        self.view_history.append(self.current_view)
        self.current_view = view
        self._notify_state_change()
        
    def set_act(self, act: int) -> None:
        """Set the current act and update history."""
        self.act_history.append(self.current_act)
        self.current_act = act
        self._notify_state_change()
        
    def set_scene(self, scene: int) -> None:
        """Set the current scene and update history."""
        self.scene_history.append(self.current_scene)
        self.current_scene = scene
        self._notify_state_change()
        
    def set_processing(self, is_processing: bool) -> None:
        """Set the processing state."""
        self.is_processing = is_processing
        self._notify_state_change()
        
    def set_error(self, error: Optional[str]) -> None:
        """Set the error message."""
        self.error_message = error
        self._notify_state_change()
        
    def set_selection(self, index: int) -> None:
        """Set the selected index."""
        self.selected_index = index
        self._notify_state_change()
        
    def set_scroll(self, position: int) -> None:
        """Set the scroll position."""
        self.scroll_position = max(0, min(position, self.max_scroll))
        self._notify_state_change()
        
    def set_max_scroll(self, max_scroll: int) -> None:
        """Set the maximum scroll position."""
        self.max_scroll = max_scroll
        self._notify_state_change()
        
    def go_back(self) -> None:
        """Go back to the previous view."""
        if self.view_history:
            self.current_view = self.view_history.pop()
            self._notify_state_change()
            
    def go_back_act(self) -> None:
        """Go back to the previous act."""
        if self.act_history:
            self.current_act = self.act_history.pop()
            self._notify_state_change()
            
    def go_back_scene(self) -> None:
        """Go back to the previous scene."""
        if self.scene_history:
            self.current_scene = self.scene_history.pop()
            self._notify_state_change()
            
    def clear_history(self) -> None:
        """Clear all history."""
        self.view_history.clear()
        self.act_history.clear()
        self.scene_history.clear()
        self._notify_state_change()
        
    def _notify_state_change(self) -> None:
        """Notify listeners of state change."""
        if self.on_state_change:
            self.on_state_change()
            
    def get_state(self) -> Dict[str, Any]:
        """Get the current state as a dictionary."""
        return {
            "current_view": self.current_view,
            "current_act": self.current_act,
            "current_scene": self.current_scene,
            "is_processing": self.is_processing,
            "error_message": self.error_message,
            "selected_index": self.selected_index,
            "scroll_position": self.scroll_position,
            "max_scroll": self.max_scroll
        }
        
    def set_state(self, state: Dict[str, Any]) -> None:
        """Set the state from a dictionary."""
        self.current_view = state.get("current_view", self.current_view)
        self.current_act = state.get("current_act", self.current_act)
        self.current_scene = state.get("current_scene", self.current_scene)
        self.is_processing = state.get("is_processing", self.is_processing)
        self.error_message = state.get("error_message", self.error_message)
        self.selected_index = state.get("selected_index", self.selected_index)
        self.scroll_position = state.get("scroll_position", self.scroll_position)
        self.max_scroll = state.get("max_scroll", self.max_scroll)
        self._notify_state_change()
