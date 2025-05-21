"""
Memory management for theatrical content and context.
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime
from pathlib import Path
from pydantic import ConfigDict
import logging
from dataclasses import dataclass, field
import uuid

logger = logging.getLogger(__name__)


@dataclass
class CharacterProfile:
    id: str
    name: str
    description: str = ""
    background: str = ""
    relationships: Dict[str, str] = field(default_factory=dict)
    goals: List[str] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)
    motivations: List[str] = field(default_factory=list)
    development_arc: List[Dict[str, str]] = field(default_factory=list)


@dataclass
class SceneData:
    id: str
    act_number: int
    scene_number: int
    content: str
    evaluation: Dict[str, Any]
    timing_metrics: Dict[str, float]
    iterations: int
    iteration_metrics: Dict[str, Any]
    timestamp: str


class StoryOutline:
    def __init__(self, title: str, acts: List[Dict[str, Any]] = None):
        self.title = title
        self.acts = acts or []
        self.planning_status = "planning"
        self.planning_discussions = []
        self.version = "1.0"
        self.last_modified = datetime.now()
    
    @classmethod
    def from_text(cls, text: str) -> 'StoryOutline':
        """Create a story outline from LLM-generated text.
        
        The text should contain:
        1. A title
        2. Three acts with descriptions and key events
        3. Character descriptions and relationships
        4. Major plot points and conflicts
        5. Thematic elements and motifs
        6. Technical requirements and staging notes
        """
        # Extract title
        title = None
        acts = []
        
        # Split text into sections
        sections = text.split('\n\n')
        
        # Find title (usually first line or after "Title:")
        for section in sections:
            if section.strip().startswith('Title:'):
                title = section.replace('Title:', '').strip()
                break
            elif not title and len(section.strip()) > 0:
                title = section.strip()
                break
        
        if not title:
            raise ValueError("Could not find title in text")
            
        # Parse acts
        current_act = None
        current_events = []
        
        for section in sections:
            section = section.strip()
            
            # Look for act headers
            if section.lower().startswith(('act 1', 'act i', 'first act')):
                if current_act:
                    acts.append({
                        "act_number": len(acts) + 1,
                        "description": current_act,
                        "key_events": current_events[:5],  # Ensure exactly 5 events
                        "status": "draft"
                    })
                current_act = section
                current_events = []
            elif section.lower().startswith(('act 2', 'act ii', 'second act')):
                if current_act:
                    acts.append({
                        "act_number": len(acts) + 1,
                        "description": current_act,
                        "key_events": current_events[:5],
                        "status": "draft"
                    })
                current_act = section
                current_events = []
            elif section.lower().startswith(('act 3', 'act iii', 'third act')):
                if current_act:
                    acts.append({
                        "act_number": len(acts) + 1,
                        "description": current_act,
                        "key_events": current_events[:5],
                        "status": "draft"
                    })
                current_act = section
                current_events = []
            # Look for key events (usually numbered or bulleted)
            elif section.strip().startswith(('-', '*', '•', '1.', '2.', '3.', '4.', '5.')):
                event = section.lstrip('-*•12345. ').strip()
                if event:
                    current_events.append(event)
            # If we have a current act and this isn't a new act, it's part of the description
            elif current_act and not section.lower().startswith(('act', 'scene', 'character', 'plot', 'theme')):
                current_act += '\n' + section
        
        # Add the last act if we have one
        if current_act:
            acts.append({
                "act_number": len(acts) + 1,
                "description": current_act,
                "key_events": current_events[:5],
                "status": "draft"
            })
        
        # Ensure we have exactly 3 acts
        if len(acts) < 3:
            # Pad with placeholder acts if needed
            while len(acts) < 3:
                acts.append({
                    "act_number": len(acts) + 1,
                    "description": f"Act {len(acts) + 1} - To be developed",
                    "key_events": ["Event 1", "Event 2", "Event 3", "Event 4", "Event 5"],
                    "status": "draft"
                })
        
        return cls(title=title, acts=acts)
    
    def add_planning_discussion(self, participant: str, suggestion: str, reasoning: str) -> None:
        """Add a planning discussion entry."""
        if not all([participant, suggestion, reasoning]):
            raise ValueError("All discussion fields must be non-empty")
            
        self.planning_discussions.append({
            "participant": participant,
            "suggestion": suggestion,
            "reasoning": reasoning,
            "timestamp": datetime.now().isoformat(),
            "discussion_id": str(uuid.uuid4())
        })
        self.last_modified = datetime.now()
    
    def commit_act(self, act_number: int, description: str, key_events: List[str]) -> None:
        """Commit an act to the outline after planning discussions."""
        if not description or not key_events:
            raise ValueError("Description and key events are required")
            
        if len(key_events) != 5:
            raise ValueError("Exactly 5 key events are required")
            
        # Validate act number
        if act_number < 1 or act_number > 5:
            raise ValueError("Act number must be between 1 and 5")
            
        # Remove any existing act with this number
        self.acts = [act for act in self.acts if act.get("act_number") != act_number]
        
        # Add the committed act
        self.acts.append({
            "act_number": act_number,
            "description": description,
            "key_events": key_events,
            "commitment_timestamp": datetime.now().isoformat(),
            "status": "committed",
            "act_id": str(uuid.uuid4()),
            "version": self.version
        })
        
        # Sort acts by number
        self.acts.sort(key=lambda x: x.get("act_number", 0))
        self.last_modified = datetime.now()
    
    def get_act_outline(self, act_number: int) -> Optional[Dict[str, Any]]:
        """Get the outline for a specific act."""
        if not 1 <= act_number <= 5:
            raise ValueError("Act number must be between 1 and 5")
            
        for act in self.acts:
            if act.get("act_number") == act_number:
                return act
        return None
    
    def update_act_status(self, act_number: int, status: str) -> None:
        """Update the status of an act (committed, in_progress, completed)."""
        if status not in ["committed", "in_progress", "completed"]:
            raise ValueError("Invalid status")
            
        act = self.get_act_outline(act_number)
        if not act:
            raise ValueError(f"No act found with number {act_number}")
            
        act["status"] = status
        act["last_status_update"] = datetime.now().isoformat()
        self.last_modified = datetime.now()
    
    def get_planning_summary(self) -> str:
        """Get a summary of planning discussions."""
        if not self.planning_discussions:
            return "No planning discussions yet."
            
        summary = []
        for discussion in self.planning_discussions:
            summary.append(
                f"{discussion['participant']} suggested: {discussion['suggestion']}\n"
                f"Reasoning: {discussion['reasoning']}\n"
                f"Time: {discussion['timestamp']}\n"
            )
        return "\n".join(summary)
    
    def validate_act_sequence(self) -> bool:
        """Validate the sequence of acts."""
        if not self.acts:
            return False
            
        # Check for gaps in act numbers
        act_numbers = sorted(act.get("act_number", 0) for act in self.acts)
        expected_numbers = list(range(1, len(act_numbers) + 1))
        if act_numbers != expected_numbers:
            return False
            
        # Check for duplicate act numbers
        if len(act_numbers) != len(set(act_numbers)):
            return False
            
        return True
    
    def get_act_dependencies(self, act_number: int) -> List[int]:
        """Get the dependencies for a specific act."""
        if not 1 <= act_number <= 5:
            raise ValueError("Act number must be between 1 and 5")
            
        # Simple dependency: each act depends on the previous one
        return [act_number - 1] if act_number > 1 else []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the outline to a dictionary."""
        return {
            "title": self.title,
            "acts": self.acts,
            "planning_status": self.planning_status,
            "planning_discussions": self.planning_discussions,
            "version": self.version,
            "last_modified": self.last_modified.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StoryOutline':
        """Create an outline from a dictionary."""
        data = data.copy()
        data["last_modified"] = datetime.fromisoformat(data["last_modified"])
        return cls(**data)


class TheatricalMemory(BaseModel):
    """Memory store for theatrical content and context."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    character_profiles: Dict[str, CharacterProfile] = Field(default_factory=dict)
    scenes: List[SceneData] = Field(default_factory=list)
    thematic_elements: Dict[str, List[str]] = Field(default_factory=dict)
    technical_notes: Dict[str, List[str]] = Field(default_factory=dict)
    _db_path: Optional[Path] = None
    version: str = Field(default="1.0")
    last_modified: datetime = Field(default_factory=datetime.now)
    story_outline: Optional[StoryOutline] = None

    def __init__(self, **data) -> None:
        """Initialize TheatricalMemory, optionally handling a db_path."""
        db_path_val = data.pop("db_path", None)
        super().__init__(**data)
        if db_path_val:
            self._db_path = Path(db_path_val)
            if self._db_path.parent:
                self._db_path.parent.mkdir(parents=True, exist_ok=True)

    def update_character_profile(self, char_id: str, profile: CharacterProfile) -> None:
        """Update a character's profile in the memory system."""
        if not char_id or not profile:
            raise ValueError("Character ID and profile are required")
        self.character_profiles[char_id] = profile
        self.last_modified = datetime.now()
        logger.info(f"Updated character profile for {char_id}")

    def get_character_profile(self, char_id: str) -> Optional[CharacterProfile]:
        """Get a character's profile from the memory system."""
        return self.character_profiles.get(char_id)

    def add_scene(self, scene: SceneData) -> None:
        """Add a scene to the memory system."""
        if not scene:
            raise ValueError("Scene data is required")
        self.scenes.append(scene)
        self.last_modified = datetime.now()
        logger.info(f"Added scene {scene.id}")

    def get_scene(self, scene_id: str) -> Optional[SceneData]:
        """Get a scene from the memory system."""
        for scene in self.scenes:
            if scene.id == scene_id:
                return scene
        return None

    def update_story_outline(self, outline: StoryOutline) -> None:
        """Update the story outline."""
        self.story_outline = outline
        self.last_modified = datetime.now()
        logger.info(f"Updated story outline: {outline.title}")

    def get_story_outline(self) -> Optional[StoryOutline]:
        """Get the current story outline."""
        return self.story_outline

    def store_thematic_element(self, theme: str, elements: List[str]) -> None:
        """Store thematic elements."""
        self.thematic_elements[theme] = elements

    def get_thematic_elements(self, theme: str) -> List[str]:
        """Get thematic elements for a theme."""
        return self.thematic_elements.get(theme, [])

    def store_technical_note(self, category: str, notes: List[str]) -> None:
        """Store technical notes."""
        self.technical_notes[category] = notes

    def get_technical_notes(self, category: str) -> List[str]:
        """Get technical notes for a category."""
        return self.technical_notes.get(category, [])

    def get_scene_context(self, scene_id: str) -> Dict[str, Any]:
        """Get context for a specific scene."""
        scene = self.get_scene(scene_id)
        if not scene:
            return {}

        # Get character profiles
        character_profiles = {}
        for char_id in scene.requirements.get("characters", []):
            profile = self.get_character_profile(char_id)
            if profile:
                character_profiles[char_id] = profile

        # Get thematic elements
        themes = []
        for theme, elements in self.thematic_elements.items():
            if any(element.lower() in scene.content.lower() for element in elements):
                themes.append(theme)

        return {
            "scene": scene,
            "character_profiles": character_profiles,
            "themes": themes,
            "technical_notes": {
                category: notes
                for category, notes in self.technical_notes.items()
                if any(note.lower() in scene.content.lower() for note in notes)
            },
        }
