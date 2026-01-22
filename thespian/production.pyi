"""
Type stubs for thespian.production module.

This stub file provides type information for IDEs and type checkers.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime

class Production(BaseModel):
    """
    Represents a theatrical production with all its components.
    """
    theme: str
    created_at: datetime
    script: Optional[Dict[str, Any]]
    design: Optional[Dict[str, Any]]
    characters: Dict[str, Dict[str, Any]]
    status: str
    
    def update_script(self, script: Dict[str, Any]) -> None: ...
    def update_design(self, design: Dict[str, Any]) -> None: ...
    def add_character(self, name: str, details: Dict[str, Any]) -> None: ...
    def get_status(self) -> str: ...
