"""
Performance class for executing theatrical performances.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class Performance(BaseModel):
    """
    Represents a theatrical performance of a production.
    """

    production: Any = Field(..., description="The production being performed")
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: str = Field(default="not_started", description="Current status of the performance")
    current_scene: Optional[str] = None
    scene_history: List[Dict[str, Any]] = Field(default_factory=list)

    def start(self) -> None:
        """Start the performance."""
        self.start_time = datetime.now()
        self.status = "in_progress"

    def end(self) -> None:
        """End the performance."""
        self.end_time = datetime.now()
        self.status = "completed"

    def advance_scene(self, scene: Dict[str, Any]) -> None:
        """Advance to the next scene in the performance."""
        self.current_scene = scene.get("name")
        self.scene_history.append(scene)

    def get_duration(self) -> Optional[float]:
        """Get the duration of the performance in seconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None

    def get_current_scene(self) -> Optional[str]:
        """Get the current scene being performed."""
        return self.current_scene

    def get_scene_history(self) -> List[Dict[str, Any]]:
        """Get the history of performed scenes."""
        return self.scene_history
