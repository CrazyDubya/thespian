"""
Performance Dashboard for orchestrating and monitoring theatrical performances.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.layout import Layout
from rich.text import Text

from ..agents import CharacterActorAgent, StageManagerAgent
from ..performance import Performance


class PerformanceMetrics(BaseModel):
    """Metrics for tracking performance quality."""

    scene_timing: Dict[str, float] = Field(default_factory=dict)
    actor_engagement: Dict[str, float] = Field(default_factory=dict)
    audience_reaction: Dict[str, float] = Field(default_factory=dict)
    technical_issues: List[str] = Field(default_factory=list)


class PerformanceDashboard(BaseModel):
    """
    Dashboard for orchestrating and monitoring theatrical performances.
    """

    performance: Optional[Performance] = None
    stage_manager: Optional[StageManagerAgent] = None
    metrics: PerformanceMetrics = Field(default_factory=PerformanceMetrics)
    console: Console = Field(default_factory=Console)

    def __init__(self, **data):
        super().__init__(**data)
        self.stage_manager = StageManagerAgent()

    def start_performance(self, production: Any) -> None:
        """Start a new performance."""
        self.performance = Performance(production=production)
        self.performance.start()
        self.console.print("[green]Performance started[/green]")

    def end_performance(self) -> None:
        """End the current performance."""
        if not self.performance:
            raise ValueError("No performance is currently running")

        self.performance.end()
        self.console.print("[green]Performance ended[/green]")

    def advance_scene(self, scene: Dict[str, Any]) -> None:
        """Advance to the next scene in the performance."""
        if not self.performance:
            raise ValueError("No performance is currently running")

        self.performance.advance_scene(scene)
        self._update_metrics(scene)

    def _update_metrics(self, scene: Dict[str, Any]) -> None:
        """Update performance metrics for the current scene."""
        scene_name = scene.get("name", "Unknown Scene")

        # Update scene timing
        if self.performance.start_time:
            duration = (datetime.now() - self.performance.start_time).total_seconds()
            self.metrics.scene_timing[scene_name] = duration

        # Simulate actor engagement (in a real implementation, this would be based on actual metrics)
        for actor_name in scene.get("actors", []):
            self.metrics.actor_engagement[actor_name] = 0.8  # Example value

        # Simulate audience reaction (in a real implementation, this would be based on actual metrics)
        self.metrics.audience_reaction[scene_name] = 0.9  # Example value

    def display_dashboard(self) -> None:
        """Display the performance dashboard with live updates."""
        if not self.performance:
            self.console.print("[red]No performance is currently running[/red]")
            return

        layout = Layout()
        layout.split_column(Layout(name="header"), Layout(name="main"), Layout(name="footer"))

        # Header
        header = Panel(
            Text(f"Performance Dashboard - {self.performance.status}", justify="center"),
            style="bold blue",
        )
        layout["header"].update(header)

        # Main content
        main_content = []

        # Current scene
        if self.performance.current_scene:
            main_content.append(
                Panel(
                    f"Current Scene: {self.performance.current_scene}", title="Scene", style="green"
                )
            )

        # Performance metrics
        metrics_table = Table(title="Performance Metrics")
        metrics_table.add_column("Metric", style="cyan")
        metrics_table.add_column("Value", style="green")

        for scene, timing in self.metrics.scene_timing.items():
            metrics_table.add_row(f"Scene Timing ({scene})", f"{timing:.2f}s")

        for actor, engagement in self.metrics.actor_engagement.items():
            metrics_table.add_row(f"Actor Engagement ({actor})", f"{engagement:.2%}")

        for scene, reaction in self.metrics.audience_reaction.items():
            metrics_table.add_row(f"Audience Reaction ({scene})", f"{reaction:.2%}")

        main_content.append(metrics_table)

        # Technical issues
        if self.metrics.technical_issues:
            issues_panel = Panel(
                "\n".join(self.metrics.technical_issues), title="Technical Issues", style="red"
            )
            main_content.append(issues_panel)

        layout["main"].update(Panel("\n".join(str(x) for x in main_content)))

        # Footer
        footer = Panel(
            (
                f"Duration: {self.performance.get_duration():.2f}s"
                if self.performance.get_duration()
                else "Duration: N/A"
            ),
            style="bold yellow",
        )
        layout["footer"].update(footer)

        self.console.print(layout)

    def add_technical_issue(self, issue: str) -> None:
        """Add a technical issue to the dashboard."""
        self.metrics.technical_issues.append(f"{datetime.now().strftime('%H:%M:%S')} - {issue}")

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get a summary of the performance."""
        if not self.performance:
            raise ValueError("No performance is currently running")

        return {
            "duration": self.performance.get_duration(),
            "scenes_performed": len(self.performance.scene_history),
            "average_scene_timing": (
                sum(self.metrics.scene_timing.values()) / len(self.metrics.scene_timing)
                if self.metrics.scene_timing
                else 0
            ),
            "average_actor_engagement": (
                sum(self.metrics.actor_engagement.values()) / len(self.metrics.actor_engagement)
                if self.metrics.actor_engagement
                else 0
            ),
            "average_audience_reaction": (
                sum(self.metrics.audience_reaction.values()) / len(self.metrics.audience_reaction)
                if self.metrics.audience_reaction
                else 0
            ),
            "technical_issues": len(self.metrics.technical_issues),
        }
