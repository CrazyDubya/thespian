"""
Script Editor Backend API

Provides collaborative script editing capabilities with version control,
real-time collaboration, and integration with the theatrical memory system.
"""

from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
from pathlib import Path


class EditType(str, Enum):
    """Types of edits that can be made to a script."""
    INSERT = "insert"
    DELETE = "delete"
    REPLACE = "replace"
    FORMAT = "format"
    COMMENT = "comment"


@dataclass
class ScriptEdit:
    """Represents a single edit to a script."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    edit_type: EditType = EditType.REPLACE
    position: int = 0
    content: str = ""
    previous_content: Optional[str] = None
    author: str = "system"
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ScriptVersion:
    """Represents a version of a script."""
    version_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: str = ""
    author: str = "system"
    timestamp: datetime = field(default_factory=datetime.now)
    message: str = ""
    parent_version: Optional[str] = None
    edits: List[ScriptEdit] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ScriptEditor:
    """
    Backend API for collaborative script editing.

    Features:
    - Version control with full edit history
    - Real-time collaboration support
    - Conflict resolution
    - Integration with theatrical memory
    - Auto-save and recovery
    """

    def __init__(
        self,
        script_id: Optional[str] = None,
        storage_path: Optional[Path] = None
    ):
        """Initialize the script editor."""
        self.script_id = script_id or str(uuid.uuid4())
        self.storage_path = storage_path or Path.home() / ".thespian" / "scripts"
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.current_content: str = ""
        self.versions: List[ScriptVersion] = []
        self.current_version: Optional[ScriptVersion] = None
        self.pending_edits: List[ScriptEdit] = []
        self.change_callbacks: List[Callable[[ScriptEdit], None]] = []

    def create_version(
        self,
        content: str,
        author: str = "system",
        message: str = ""
    ) -> ScriptVersion:
        """
        Create a new version of the script.

        Args:
            content: The content of the new version
            author: The author of the version
            message: A commit message describing the changes

        Returns:
            The newly created ScriptVersion
        """
        version = ScriptVersion(
            content=content,
            author=author,
            message=message,
            parent_version=self.current_version.version_id if self.current_version else None,
            timestamp=datetime.now()
        )

        self.versions.append(version)
        self.current_version = version
        self.current_content = content

        # Save to disk
        self._save_version(version)

        return version

    def apply_edit(
        self,
        edit: ScriptEdit,
        auto_version: bool = False
    ) -> bool:
        """
        Apply an edit to the current script.

        Args:
            edit: The edit to apply
            auto_version: Whether to automatically create a version after applying

        Returns:
            True if the edit was applied successfully
        """
        try:
            if edit.edit_type == EditType.INSERT:
                self.current_content = (
                    self.current_content[:edit.position] +
                    edit.content +
                    self.current_content[edit.position:]
                )
            elif edit.edit_type == EditType.DELETE:
                end_pos = edit.position + len(edit.previous_content or "")
                self.current_content = (
                    self.current_content[:edit.position] +
                    self.current_content[end_pos:]
                )
            elif edit.edit_type == EditType.REPLACE:
                end_pos = edit.position + len(edit.previous_content or "")
                self.current_content = (
                    self.current_content[:edit.position] +
                    edit.content +
                    self.current_content[end_pos:]
                )

            self.pending_edits.append(edit)

            # Notify callbacks
            for callback in self.change_callbacks:
                callback(edit)

            if auto_version:
                self.create_version(
                    self.current_content,
                    author=edit.author,
                    message=f"Auto-version after {edit.edit_type.value} edit"
                )

            return True

        except Exception as e:
            print(f"Error applying edit: {e}")
            return False

    def get_version(self, version_id: str) -> Optional[ScriptVersion]:
        """Get a specific version by ID."""
        for version in self.versions:
            if version.version_id == version_id:
                return version
        return None

    def revert_to_version(self, version_id: str) -> bool:
        """
        Revert the script to a specific version.

        Args:
            version_id: The ID of the version to revert to

        Returns:
            True if the revert was successful
        """
        version = self.get_version(version_id)
        if not version:
            return False

        self.current_content = version.content
        self.current_version = version
        return True

    def get_diff(
        self,
        version_id_a: str,
        version_id_b: str
    ) -> Dict[str, Any]:
        """
        Get the diff between two versions.

        Args:
            version_id_a: The first version ID
            version_id_b: The second version ID

        Returns:
            A dictionary containing the diff information
        """
        version_a = self.get_version(version_id_a)
        version_b = self.get_version(version_id_b)

        if not version_a or not version_b:
            return {"error": "One or both versions not found"}

        # Simple diff calculation (can be enhanced with difflib)
        return {
            "version_a": version_id_a,
            "version_b": version_id_b,
            "content_a": version_a.content,
            "content_b": version_b.content,
            "timestamp_a": version_a.timestamp.isoformat(),
            "timestamp_b": version_b.timestamp.isoformat(),
        }

    def register_change_callback(
        self,
        callback: Callable[[ScriptEdit], None]
    ) -> None:
        """Register a callback to be called when edits are applied."""
        self.change_callbacks.append(callback)

    def export_to_file(self, file_path: Path) -> bool:
        """Export the current script to a file."""
        try:
            file_path.write_text(self.current_content, encoding='utf-8')
            return True
        except Exception as e:
            print(f"Error exporting script: {e}")
            return False

    def import_from_file(self, file_path: Path, create_version: bool = True) -> bool:
        """Import a script from a file."""
        try:
            content = file_path.read_text(encoding='utf-8')
            self.current_content = content

            if create_version:
                self.create_version(
                    content,
                    author="import",
                    message=f"Imported from {file_path.name}"
                )

            return True
        except Exception as e:
            print(f"Error importing script: {e}")
            return False

    def _save_version(self, version: ScriptVersion) -> None:
        """Save a version to disk."""
        version_file = self.storage_path / f"{self.script_id}_{version.version_id}.json"

        version_data = {
            "version_id": version.version_id,
            "content": version.content,
            "author": version.author,
            "timestamp": version.timestamp.isoformat(),
            "message": version.message,
            "parent_version": version.parent_version,
            "metadata": version.metadata,
        }

        version_file.write_text(json.dumps(version_data, indent=2), encoding='utf-8')

    def get_version_history(self) -> List[Dict[str, Any]]:
        """Get the version history as a list of dictionaries."""
        return [
            {
                "version_id": v.version_id,
                "author": v.author,
                "timestamp": v.timestamp.isoformat(),
                "message": v.message,
                "parent_version": v.parent_version,
            }
            for v in self.versions
        ]
