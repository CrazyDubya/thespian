"""
Act processor for scene generation.
"""

from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field
import logging
import json
from datetime import datetime
import time

logger = logging.getLogger(__name__)

class ActRequirements(BaseModel):
    """Requirements for act generation."""
    
    act_number: int
    scene_count: int
    characters: List[str] = Field(default_factory=list)
    setting: str = ""
    theme: str = ""
    style: str = ""
    period: str = ""
    target_audience: str = ""

class ActProcessor:
    """Act processor for scene generation."""
    
    def __init__(self, max_advisor_retries: int = 3, max_synthesis_retries: int = 3) -> None:
        """Initialize act processor."""
        self.max_advisor_retries = max_advisor_retries
        self.max_synthesis_retries = max_synthesis_retries
    
    def process_advisor_suggestion(self, suggestion: str) -> Dict[str, Any]:
        """Process and validate an advisor's suggestion."""
        sections = {
            "DESCRIPTION": "",
            "KEY EVENTS": [],
            "CHARACTER DEVELOPMENT": "",
            "THEMATIC ELEMENTS": ""
        }
        
        current_section = None
        current_content = []
        
        for line in suggestion.split("\n"):
            line = line.strip()
            if not line:
                continue
                
            # Check for section headers
            found_section = False
            for header in sections.keys():
                if header in line.upper():
                    if current_section:
                        if current_section == "KEY EVENTS":
                            sections[current_section] = current_content
                        else:
                            sections[current_section] = "\n".join(current_content).strip()
                    current_section = header
                    current_content = []
                    found_section = True
                    break
            
            if not found_section and current_section:
                current_content.append(line)
        
        # Add the last section
        if current_section and current_content:
            if current_section == "KEY EVENTS":
                sections[current_section] = current_content
            else:
                sections[current_section] = "\n".join(current_content).strip()
        
        # Validate required sections
        missing_sections = [section for section, content in sections.items() 
                          if not content]
        if missing_sections:
            raise ValueError(f"Missing required sections: {', '.join(missing_sections)}")
        
        # Extract and validate key events
        key_events = []
        for line in sections["KEY EVENTS"]:
            line = line.strip()
            if line and line[0].isdigit() and ". " in line:
                try:
                    num = int(line.split(".", 1)[0])
                    if 1 <= num <= 5:
                        event = line.split(". ", 1)[1].strip()
                        if not event.endswith("."):
                            event += "."
                        key_events.append(event)
                except ValueError:
                    continue
        
        if len(key_events) != 5:
            # Log the issue but allow processing to continue with a warning
            logger.warning(f"Expected 5 key events, found {len(key_events)}. Continuing with available events.")
            # If we have some events, use them; if none, create basic events
            if len(key_events) == 0:
                logger.warning("No key events found, creating basic events")
                key_events = [
                    "Opening scene establishes setting and characters.",
                    "Initial conflict or challenge is introduced.",
                    "Characters face obstacles and complications.",
                    "Tension builds toward climactic moment.",
                    "Resolution or cliffhanger concludes the act."
                ][:5]  # Ensure exactly 5 events
            # If we have partial events, pad to 5
            while len(key_events) < 5:
                key_events.append("Additional scene develops the story further.")
        
        # Validate event content
        for i, event in enumerate(key_events):
            if len(event) < 20:
                raise ValueError(f"Key event {i+1} is too short")
            if not any(char in event for char in [".", "!", "?"]):
                raise ValueError(f"Key event {i+1} is not a complete sentence")
        
        # Validate description length
        if len(sections["DESCRIPTION"]) < 50:
            raise ValueError("Description is too short")
        
        # Validate character development
        if len(sections["CHARACTER DEVELOPMENT"]) < 30:
            raise ValueError("Character development section is too short")
        
        # Validate thematic elements
        if len(sections["THEMATIC ELEMENTS"]) < 30:
            raise ValueError("Thematic elements section is too short")
        
        return {
            "description": sections["DESCRIPTION"],
            "key_events": key_events,
            "character_development": sections["CHARACTER DEVELOPMENT"],
            "thematic_elements": sections["THEMATIC ELEMENTS"]
        }
    
    def process_synthesis(self, outline_str: str) -> Dict[str, Any]:
        """Process and validate the synthesized act outline."""
        return self.process_advisor_suggestion(outline_str)
    
    def get_previous_acts_summary(self, acts: List[Dict[str, Any]]) -> str:
        """Get summary of previous acts."""
        if not acts:
            return "No previous acts"
        summary_parts = []
        for act in acts:
            summary_parts.append(f"Act {act['act_number']}: {act['description']}")
        return "\n".join(summary_parts)
    
    def get_previous_scenes_summary(self, scenes: List[str], max_scenes: int = 5) -> str:
        """Get summary of previous scenes."""
        if not scenes:
            return 'No previous scenes'
        # Return the last max_scenes as a string
        return "\n".join(scenes[-max_scenes:])
    
    def validate_act_sequence(self, acts: List[Dict[str, Any]]) -> bool:
        """Validate act sequence."""
        if not acts:
            return True
            
        # Check for gaps in act numbers
        act_numbers = [act["act_number"] for act in acts]
        act_numbers.sort()
        
        for i in range(len(act_numbers) - 1):
            if act_numbers[i + 1] - act_numbers[i] > 1:
                return False
                
        # Check for duplicate act numbers
        if len(act_numbers) != len(set(act_numbers)):
            return False
            
        return True
    
    def get_state(self) -> Dict[str, Any]:
        """Get the act processor state."""
        return {
            "max_advisor_retries": self.max_advisor_retries,
            "max_synthesis_retries": self.max_synthesis_retries
        }
    
    def set_state(self, state: Dict[str, Any]) -> None:
        """Set the act processor state."""
        self.max_advisor_retries = state.get("max_advisor_retries", self.max_advisor_retries)
        self.max_synthesis_retries = state.get("max_synthesis_retries", self.max_synthesis_retries) 