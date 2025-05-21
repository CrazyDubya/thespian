"""
Script Editor component for collaborative script development.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.live import Live
from rich.table import Table

from ..agents import PlaywrightAgent, DirectorAgent


class ScriptVersion(BaseModel):
    """Represents a version of the script with metadata."""

    content: str = Field(..., description="The script content")
    version: int = Field(..., description="Version number")
    timestamp: datetime = Field(default_factory=datetime.now)
    author: str = Field(..., description="Author of the version")
    comments: List[str] = Field(default_factory=list)


class ScriptEditor(BaseModel):
    """
    Collaborative script editor with version control and real-time collaboration.
    """

    current_script: Optional[ScriptVersion] = None
    versions: List[ScriptVersion] = Field(default_factory=list)
    playwright: Optional[PlaywrightAgent] = None
    director: Optional[DirectorAgent] = None
    console: Console = Field(default_factory=Console)

    def __init__(self, **data):
        super().__init__(**data)
        self.playwright = PlaywrightAgent()
        self.director = DirectorAgent()

    def create_new_script(self, theme: str) -> None:
        """Create a new script from a theme."""
        concept = self.playwright.generate_concept(theme)
        script = self.playwright.write_script(concept)

        self.current_script = ScriptVersion(
            content=script["script"], version=1, author="Playwright Agent"
        )
        self.versions.append(self.current_script)

    def edit_script(self, new_content: str, author: str) -> None:
        """Edit the current script and create a new version."""
        if not self.current_script:
            raise ValueError("No script exists to edit")

        new_version = ScriptVersion(
            content=new_content, version=len(self.versions) + 1, author=author
        )
        self.versions.append(new_version)
        self.current_script = new_version

    def get_director_feedback(self) -> Dict[str, Any]:
        """Get feedback from the director agent."""
        if not self.current_script:
            raise ValueError("No script exists to review")

        feedback = self.director.review_script({"script": self.current_script.content})
        return feedback

    def apply_director_feedback(self) -> None:
        """Apply director's feedback to the script."""
        if not self.current_script:
            raise ValueError("No script exists to revise")

        feedback = self.get_director_feedback()
        revised_script = self.playwright.revise_script(
            {"script": self.current_script.content}, feedback
        )

        self.edit_script(revised_script["script"], "Playwright Agent (Director Feedback)")

    def display_script(self) -> None:
        """Display the current script with rich formatting."""
        if not self.current_script:
            self.console.print("[red]No script exists[/red]")
            return

        self.console.print(
            Panel.fit(
                Markdown(self.current_script.content),
                title=f"Script v{self.current_script.version}",
                subtitle=f"By {self.current_script.author} at {self.current_script.timestamp}",
            )
        )

    def display_version_history(self) -> None:
        """Display the version history of the script."""
        table = Table(title="Script Version History")
        table.add_column("Version", style="cyan")
        table.add_column("Author", style="green")
        table.add_column("Timestamp", style="yellow")
        table.add_column("Comments", style="blue")

        for version in self.versions:
            table.add_row(
                str(version.version),
                version.author,
                version.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "\n".join(version.comments) if version.comments else "",
            )

        self.console.print(table)

    def add_comment(self, comment: str) -> None:
        """Add a comment to the current script version."""
        if not self.current_script:
            raise ValueError("No script exists to comment on")

        self.current_script.comments.append(comment)

    def compare_versions(self, version1: int, version2: int) -> None:
        """Compare two versions of the script."""
        v1 = next((v for v in self.versions if v.version == version1), None)
        v2 = next((v for v in self.versions if v.version == version2), None)

        if not v1 or not v2:
            self.console.print("[red]One or both versions not found[/red]")
            return

        # Simple line-by-line comparison
        lines1 = v1.content.split("\n")
        lines2 = v2.content.split("\n")

        table = Table(title=f"Comparing Versions {version1} and {version2}")
        table.add_column("Line", style="cyan")
        table.add_column(f"Version {version1}", style="green")
        table.add_column(f"Version {version2}", style="yellow")

        for i, (line1, line2) in enumerate(zip(lines1, lines2)):
            if line1 != line2:
                table.add_row(str(i + 1), line1, line2)

        self.console.print(table)
