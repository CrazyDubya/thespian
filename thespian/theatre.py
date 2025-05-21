"""
Core Theatre class that orchestrates the entire production process.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

from .agents import (
    PlaywrightAgent,
    DirectorAgent,
    CharacterActorAgent,
    SetCostumeDesignAgent,
    StageManagerAgent,
)
from .production import Production


class Theatre(BaseModel):
    """
    Main Theatre class that orchestrates the entire production process.
    """

    theme: str = Field(..., description="The theme or concept for the theatrical production")
    config: Dict[str, Any] = Field(
        default_factory=dict, description="Configuration for the theatre"
    )

    # Agent instances
    playwright: Optional[PlaywrightAgent] = None
    director: Optional[DirectorAgent] = None
    character_actors: Dict[str, CharacterActorAgent] = Field(default_factory=dict)
    designer: Optional[SetCostumeDesignAgent] = None
    stage_manager: Optional[StageManagerAgent] = None

    def __init__(self, **data):
        super().__init__(**data)
        self._initialize_agents()

    def _initialize_agents(self) -> None:
        """Initialize all required agents for the production."""
        self.playwright = PlaywrightAgent()
        self.director = DirectorAgent()
        self.designer = SetCostumeDesignAgent()
        self.stage_manager = StageManagerAgent()

    def create_production(self) -> Production:
        """
        Create a new theatrical production based on the theme.

        Returns:
            Production: A new production instance
        """
        # Initialize production with theme
        production = Production(theme=self.theme)

        # Generate initial concept and script
        concept = self.playwright.generate_concept(self.theme)
        script = self.playwright.write_script(concept)

        # Director reviews and provides feedback
        feedback = self.director.review_script(script)
        revised_script = self.playwright.revise_script(script, feedback)

        # Designer creates visual elements
        design = self.designer.create_design(revised_script)

        # Initialize character actors
        characters = self.playwright.get_characters(revised_script)
        for char_name, char_data in characters.items():
            self.character_actors[char_name] = CharacterActorAgent(
                character_name=char_name, character_data=char_data
            )

        # Stage manager prepares for production
        self.stage_manager.prepare_production(
            script=revised_script, design=design, characters=self.character_actors
        )

        # Update production with all components
        production.update_script(revised_script)
        production.update_design(design)
        for char_name, char_data in characters.items():
            production.add_character(char_name, char_data)

        return production

    def perform(self, production: Production) -> None:
        """
        Execute the theatrical performance.

        Args:
            production: The production to perform
        """
        self.stage_manager.conduct_performance(production)
