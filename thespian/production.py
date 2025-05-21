"""
Production class for managing theatrical productions.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class Production(BaseModel):
    """
    Represents a theatrical production with all its components.
    """

    theme: str = Field(..., description="The theme or concept of the production")
    created_at: datetime = Field(default_factory=datetime.now)
    script: Optional[Dict[str, Any]] = None
    design: Optional[Dict[str, Any]] = None
    characters: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    status: str = Field(default="draft", description="Current status of the production")

    def update_script(self, script: Dict[str, Any]) -> None:
        """Update the production's script."""
        self.script = script
        self.status = "script_updated"

    def update_design(self, design: Dict[str, Any]) -> None:
        """Update the production's design elements."""
        self.design = design
        self.status = "design_updated"

    def add_character(self, name: str, data: Dict[str, Any]) -> None:
        """Add a character to the production."""
        self.characters[name] = data
        self.status = "characters_updated"

    def get_status(self) -> str:
        """Get the current status of the production."""
        return self.status

    def is_ready_for_performance(self) -> bool:
        """Check if the production is ready for performance."""
        return all(
            [
                self.script is not None,
                self.design is not None,
                len(self.characters) > 0,
                self.status in ["script_updated", "design_updated", "characters_updated"],
            ]
        )

    def to_markdown(self) -> str:
        """Convert the production to markdown format."""
        lines = []
        
        # Title and Theme
        lines.append(f"# {self.script['title'] if self.script else self.theme}")
        lines.append(f"\nTheme: {self.theme}")
        lines.append(f"Status: {self.status}\n")
        
        # Script
        if self.script:
            lines.append("## Script\n")
            for act_num, scenes in sorted(self.script['acts'].items()):
                lines.append(f"### Act {act_num}\n")
                for scene in sorted(scenes, key=lambda x: x['scene_number']):
                    lines.append(f"#### Scene {scene['scene_number']}\n")
                    lines.append(scene['scene'])
                    lines.append("")
        
        # Design
        if self.design:
            lines.append("## Design\n")
            if 'set_design' in self.design:
                lines.append("### Set Design\n")
                lines.append(self.design['set_design'])
                lines.append("")
            if 'costume_design' in self.design:
                lines.append("### Costume Design\n")
                lines.append(self.design['costume_design'])
                lines.append("")
        
        # Characters
        if self.characters:
            lines.append("## Characters\n")
            for name, data in self.characters.items():
                lines.append(f"### {name}\n")
                for key, value in data.items():
                    lines.append(f"**{key.title()}**: {value}\n")
                lines.append("")
        
        return "\n".join(lines)
