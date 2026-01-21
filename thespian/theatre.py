"""
Core Theatre class that orchestrates the entire theatrical production process.

The Theatre module serves as the main entry point for creating theatrical productions.
It coordinates between various agents (playwright, director, actors, designers, etc.)
to generate complete theatrical works.

Example Usage:
    >>> from thespian.theatre import Theatre
    >>> theatre = Theatre(theme="A tale of redemption")
    >>> production = theatre.create_production()
    >>> print(production.script)

The Theatre class manages:
    - Agent initialization and coordination
    - Production workflow orchestration
    - Resource management and configuration
    - Communication between different creative agents
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
    
    The Theatre class is the central coordinator for creating theatrical productions.
    It manages all the creative agents and ensures they work together harmoniously
    to produce cohesive, high-quality theatrical works.
    
    Attributes:
        theme (str): The central theme or concept for the theatrical production.
            This guides all creative decisions throughout the production process.
        config (Dict[str, Any]): Configuration dictionary for customizing the
            theatre's behavior, agent parameters, and production settings.
        playwright (PlaywrightAgent): The agent responsible for writing the script.
        director (DirectorAgent): The agent that provides directorial vision.
        character_actors (Dict[str, CharacterActorAgent]): Mapping of character
            names to their respective actor agents.
        designer (SetCostumeDesignAgent): The agent for set and costume design.
        stage_manager (StageManagerAgent): The agent managing production logistics.
    
    Example:
        >>> theatre = Theatre(
        ...     theme="Love and betrayal in Renaissance Venice",
        ...     config={"style": "dramatic", "acts": 3}
        ... )
        >>> production = theatre.create_production()
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
