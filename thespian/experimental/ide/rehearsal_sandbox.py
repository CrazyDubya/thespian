"""
Rehearsal Sandbox for testing and refining theatrical performances.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.table import Table
from rich.progress import Progress

from ..agents import CharacterActorAgent, DirectorAgent


class RehearsalScene(BaseModel):
    """Represents a scene being rehearsed."""

    name: str = Field(..., description="Name of the scene")
    script_content: str = Field(..., description="Script content for the scene")
    actors: Dict[str, CharacterActorAgent] = Field(..., description="Actors in the scene")
    director: DirectorAgent = Field(..., description="Director for the scene")
    takes: List[Dict[str, Any]] = Field(default_factory=list)
    current_take: Optional[Dict[str, Any]] = None


class RehearsalSandbox(BaseModel):
    """
    Virtual environment for rehearsing scenes and refining performances.
    """

    scenes: Dict[str, RehearsalScene] = Field(default_factory=dict)
    current_scene: Optional[RehearsalScene] = None
    console: Console = Field(default_factory=Console)

    def add_scene(
        self,
        name: str,
        script_content: str,
        actors: Dict[str, CharacterActorAgent],
        director: DirectorAgent,
    ) -> None:
        """Add a new scene to the rehearsal sandbox."""
        scene = RehearsalScene(
            name=name, script_content=script_content, actors=actors, director=director
        )
        self.scenes[name] = scene

    def start_rehearsal(self, scene_name: str) -> None:
        """Start rehearsing a specific scene."""
        if scene_name not in self.scenes:
            raise ValueError(f"Scene '{scene_name}' not found")

        self.current_scene = self.scenes[scene_name]
        self.console.print(f"[green]Starting rehearsal of scene: {scene_name}[/green]")

    def run_take(self) -> Dict[str, Any]:
        """Run a take of the current scene."""
        if not self.current_scene:
            raise ValueError("No scene is currently being rehearsed")

        take = {"timestamp": datetime.now(), "performances": {}, "director_notes": None}

        # Each actor performs their lines
        for actor_name, actor in self.current_scene.actors.items():
            performance = actor.interpret_line(
                self.current_scene.script_content, {"scene": self.current_scene.name}
            )
            take["performances"][actor_name] = performance

        # Director provides feedback
        director_feedback = self.current_scene.director.review_script(
            {"script": self.current_scene.script_content, "performances": take["performances"]}
        )
        take["director_notes"] = director_feedback

        self.current_scene.takes.append(take)
        self.current_scene.current_take = take

        return take

    def display_current_take(self) -> None:
        """Display the current take with rich formatting."""
        if not self.current_scene or not self.current_scene.current_take:
            self.console.print("[red]No take to display[/red]")
            return

        take = self.current_scene.current_take

        # Display performances
        for actor_name, performance in take["performances"].items():
            self.console.print(
                Panel.fit(
                    performance["delivery"], title=f"{actor_name}'s Performance", style="blue"
                )
            )

        # Display director's notes
        if take["director_notes"]:
            self.console.print(
                Panel.fit(
                    take["director_notes"]["feedback"], title="Director's Notes", style="yellow"
                )
            )

    def display_take_history(self) -> None:
        """Display the history of takes for the current scene."""
        if not self.current_scene:
            self.console.print("[red]No scene is currently being rehearsed[/red]")
            return

        table = Table(title=f"Take History for Scene: {self.current_scene.name}")
        table.add_column("Take", style="cyan")
        table.add_column("Timestamp", style="green")
        table.add_column("Actors", style="blue")
        table.add_column("Director Notes", style="yellow")

        for i, take in enumerate(self.current_scene.takes):
            actors = ", ".join(take["performances"].keys())
            director_notes = take["director_notes"]["feedback"] if take["director_notes"] else ""

            table.add_row(
                str(i + 1),
                take["timestamp"].strftime("%H:%M:%S"),
                actors,
                director_notes[:50] + "..." if len(director_notes) > 50 else director_notes,
            )

        self.console.print(table)

    def get_best_take(self) -> Optional[Dict[str, Any]]:
        """Get the best take based on director's feedback."""
        if not self.current_scene or not self.current_scene.takes:
            return None

        # Simple implementation: return the most recent take
        # In a real implementation, this would analyze director's feedback
        return self.current_scene.takes[-1]

    def apply_director_feedback(self, take_index: int) -> None:
        """Apply director's feedback to a specific take."""
        if not self.current_scene or not self.current_scene.takes:
            raise ValueError("No takes available")

        if take_index >= len(self.current_scene.takes):
            raise ValueError(f"Take {take_index} not found")

        take = self.current_scene.takes[take_index]
        if not take["director_notes"]:
            raise ValueError("No director notes available for this take")

        # Apply feedback to each actor
        for actor_name, actor in self.current_scene.actors.items():
            if actor_name in take["performances"]:
                # In a real implementation, this would use the feedback to improve the performance
                pass
