"""
Type stubs for thespian.theatre module.

This stub file provides type information for IDEs and type checkers.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel
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
    theme: str
    config: Dict[str, Any]
    playwright: Optional[PlaywrightAgent]
    director: Optional[DirectorAgent]
    character_actors: Dict[str, CharacterActorAgent]
    designer: Optional[SetCostumeDesignAgent]
    stage_manager: Optional[StageManagerAgent]
    
    def __init__(self, **data: Any) -> None: ...
    def _initialize_agents(self) -> None: ...
    def create_production(self) -> Production: ...
    def generate_script(self, acts: int = ..., scenes_per_act: int = ...) -> Dict[str, Any]: ...
