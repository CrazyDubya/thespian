"""
Proximics Mapping Agent

Analyzes and enhances staging based on proxemics - the use of physical distance
to convey emotional dynamics, power relationships, and dramatic tension.
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import math


class ProxemicZone(str, Enum):
    """Proxemic zones based on Edward T. Hall's theory."""
    INTIMATE = "intimate"  # 0-1.5 feet - close relationships, physical contact
    PERSONAL = "personal"  # 1.5-4 feet - friends, casual interactions
    SOCIAL = "social"  # 4-12 feet - professional, formal interactions
    PUBLIC = "public"  # 12+ feet - public speaking, performances


class MovementType(str, Enum):
    """Types of character movement."""
    APPROACH = "approach"
    RETREAT = "retreat"
    CIRCLE = "circle"
    PARALLEL = "parallel"
    CROSS = "cross"
    STATIC = "static"


@dataclass
class StagePosition:
    """Represents a position on stage."""
    x: float  # Left (-1) to Right (1)
    y: float  # Upstage (-1) to Downstage (1)
    z: float = 0.0  # Elevation (for platforms, stairs)
    area: str = "center"  # Stage area name


@dataclass
class CharacterPosition:
    """Represents a character's position and orientation on stage."""
    character_id: str
    position: StagePosition
    facing_direction: float = 0.0  # Angle in degrees (0 = facing audience)
    body_orientation: str = "open"  # open, closed, profile
    timestamp: float = 0.0  # Time in scene
    emotional_state: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProxemicRelationship:
    """Analyzes the proxemic relationship between two characters."""
    character_a: str
    character_b: str
    distance: float
    zone: ProxemicZone
    power_dynamic: str  # "equal", "a_dominant", "b_dominant"
    emotional_valence: str  # "positive", "negative", "neutral", "complex"
    tension_level: float = 0.5  # 0-1
    suggested_staging: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ProximicsMappingAgent:
    """
    Agent for analyzing and enhancing staging through proxemics.

    Capabilities:
    - Map character positions and distances
    - Analyze power dynamics through spatial relationships
    - Suggest staging that reinforces dramatic tension
    - Track character movement patterns
    - Ensure spatial consistency across scenes
    """

    def __init__(self):
        """Initialize the proximics mapping agent."""
        self.character_positions: Dict[str, CharacterPosition] = {}
        self.position_history: List[Dict[str, CharacterPosition]] = []
        self.stage_dimensions = {"width": 40, "depth": 30}  # feet

    def calculate_distance(
        self,
        pos_a: StagePosition,
        pos_b: StagePosition
    ) -> float:
        """Calculate the distance between two stage positions."""
        # Convert normalized coordinates to actual stage dimensions
        x_dist = (pos_a.x - pos_b.x) * self.stage_dimensions["width"]
        y_dist = (pos_a.y - pos_b.y) * self.stage_dimensions["depth"]
        z_dist = (pos_a.z - pos_b.z)

        return math.sqrt(x_dist**2 + y_dist**2 + z_dist**2)

    def classify_zone(self, distance: float) -> ProxemicZone:
        """Classify the distance into a proxemic zone."""
        if distance <= 1.5:
            return ProxemicZone.INTIMATE
        elif distance <= 4.0:
            return ProxemicZone.PERSONAL
        elif distance <= 12.0:
            return ProxemicZone.SOCIAL
        else:
            return ProxemicZone.PUBLIC

    def analyze_relationship(
        self,
        char_a: CharacterPosition,
        char_b: CharacterPosition,
        relationship_context: Optional[Dict[str, Any]] = None
    ) -> ProxemicRelationship:
        """
        Analyze the proxemic relationship between two characters.

        Args:
            char_a: Position data for first character
            char_b: Position data for second character
            relationship_context: Optional context about their relationship

        Returns:
            ProxemicRelationship analysis
        """
        distance = self.calculate_distance(char_a.position, char_b.position)
        zone = self.classify_zone(distance)

        # Analyze power dynamic based on positioning
        power_dynamic = self._analyze_power_dynamic(char_a, char_b)

        # Analyze emotional valence
        emotional_valence = self._analyze_emotional_valence(
            zone, power_dynamic, relationship_context
        )

        # Calculate tension level
        tension_level = self._calculate_tension(
            char_a, char_b, zone, relationship_context
        )

        # Generate staging suggestions
        suggestions = self._generate_staging_suggestions(
            char_a, char_b, zone, power_dynamic, tension_level
        )

        return ProxemicRelationship(
            character_a=char_a.character_id,
            character_b=char_b.character_id,
            distance=distance,
            zone=zone,
            power_dynamic=power_dynamic,
            emotional_valence=emotional_valence,
            tension_level=tension_level,
            suggested_staging=suggestions
        )

    def _analyze_power_dynamic(
        self,
        char_a: CharacterPosition,
        char_b: CharacterPosition
    ) -> str:
        """Analyze power dynamics based on positioning."""
        # Upstage position often conveys more power
        if char_a.position.y < char_b.position.y - 0.2:
            return "a_dominant"
        elif char_b.position.y < char_a.position.y - 0.2:
            return "b_dominant"

        # Elevation conveys power
        if char_a.position.z > char_b.position.z + 1.0:
            return "a_dominant"
        elif char_b.position.z > char_a.position.z + 1.0:
            return "b_dominant"

        # Body orientation can indicate power
        if char_a.body_orientation == "open" and char_b.body_orientation == "closed":
            return "a_dominant"
        elif char_b.body_orientation == "open" and char_a.body_orientation == "closed":
            return "b_dominant"

        return "equal"

    def _analyze_emotional_valence(
        self,
        zone: ProxemicZone,
        power_dynamic: str,
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Analyze emotional valence of the proxemic relationship."""
        if not context:
            return "neutral"

        relationship_type = context.get("relationship_type", "neutral")

        # Intimate zone
        if zone == ProxemicZone.INTIMATE:
            if relationship_type in ["romantic", "familial", "close_friends"]:
                return "positive"
            else:
                return "negative"  # Invasion of space

        # Personal zone
        if zone == ProxemicZone.PERSONAL:
            if relationship_type in ["friends", "colleagues"]:
                return "positive"
            elif power_dynamic != "equal":
                return "complex"  # Power play at close range

        # Public zone
        if zone == ProxemicZone.PUBLIC:
            if relationship_type in ["romantic", "familial"]:
                return "negative"  # Unwanted distance
            elif context.get("conflict_level", 0) > 0.5:
                return "negative"  # Avoidance

        return "neutral"

    def _calculate_tension(
        self,
        char_a: CharacterPosition,
        char_b: CharacterPosition,
        zone: ProxemicZone,
        context: Optional[Dict[str, Any]]
    ) -> float:
        """Calculate dramatic tension based on proxemics."""
        tension = 0.0

        # Base tension from zone appropriateness
        if context:
            relationship_type = context.get("relationship_type", "neutral")

            # Inappropriate proximity increases tension
            if zone == ProxemicZone.INTIMATE and relationship_type in ["enemies", "strangers"]:
                tension += 0.4
            elif zone == ProxemicZone.PUBLIC and relationship_type in ["romantic", "familial"]:
                tension += 0.3

        # Tension from power dynamics
        if char_a.emotional_state == "aggressive" or char_b.emotional_state == "aggressive":
            tension += 0.3

        # Tension from conflicting orientations
        if char_a.body_orientation == "closed" and char_b.body_orientation == "closed":
            tension += 0.2

        # Context-based tension
        if context and context.get("conflict_level"):
            tension += context["conflict_level"] * 0.4

        return min(tension, 1.0)

    def _generate_staging_suggestions(
        self,
        char_a: CharacterPosition,
        char_b: CharacterPosition,
        zone: ProxemicZone,
        power_dynamic: str,
        tension_level: float
    ) -> List[str]:
        """Generate staging suggestions based on proxemic analysis."""
        suggestions = []

        # Distance-based suggestions
        if zone == ProxemicZone.INTIMATE and tension_level > 0.6:
            suggestions.append(
                f"{char_a.character_id} should maintain eye contact while {char_b.character_id} looks away - showing discomfort"
            )

        if zone == ProxemicZone.PUBLIC and tension_level > 0.6:
            suggestions.append(
                f"Consider having one character attempt to close the distance, increasing tension"
            )

        # Power dynamic suggestions
        if power_dynamic == "a_dominant":
            suggestions.append(
                f"{char_a.character_id} could move to a higher position or further upstage to emphasize dominance"
            )
        elif power_dynamic == "b_dominant":
            suggestions.append(
                f"{char_b.character_id} could step forward (downstage) to claim power in the scene"
            )

        # Tension-building movements
        if tension_level > 0.7:
            suggestions.append(
                "Consider slow, deliberate movements to build suspense"
            )
            suggestions.append(
                "Use pauses when characters cross each other's personal space"
            )

        return suggestions

    def track_movement(
        self,
        character_id: str,
        new_position: StagePosition,
        timestamp: float,
        movement_type: MovementType
    ) -> Dict[str, Any]:
        """
        Track character movement and analyze its dramatic significance.

        Args:
            character_id: ID of the character moving
            new_position: The character's new position
            timestamp: Time in the scene
            movement_type: Type of movement

        Returns:
            Analysis of the movement's dramatic significance
        """
        old_position = self.character_positions.get(character_id)

        # Update position
        self.character_positions[character_id] = CharacterPosition(
            character_id=character_id,
            position=new_position,
            timestamp=timestamp
        )

        # Analyze movement significance
        analysis = {
            "character": character_id,
            "movement_type": movement_type.value,
            "timestamp": timestamp,
        }

        if old_position:
            distance_moved = self.calculate_distance(old_position.position, new_position)
            analysis["distance_moved"] = distance_moved

            # Analyze direction of movement
            if new_position.y < old_position.position.y:
                analysis["direction"] = "upstage"
                analysis["dramatic_effect"] = "Withdrawing from audience/scene"
            elif new_position.y > old_position.position.y:
                analysis["direction"] = "downstage"
                analysis["dramatic_effect"] = "Engaging with audience/scene"

            # Analyze lateral movement
            if abs(new_position.x - old_position.position.x) > 0.3:
                analysis["lateral_movement"] = "significant"
                analysis["staging_note"] = "Major position change - draws attention"

        return analysis

    def generate_blocking_plan(
        self,
        scene_beats: List[Dict[str, Any]],
        characters: List[str],
        scene_dynamics: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate a complete blocking plan for a scene.

        Args:
            scene_beats: List of dramatic beats in the scene
            characters: List of characters in the scene
            scene_dynamics: Information about scene dynamics and relationships

        Returns:
            Detailed blocking plan with positions and movements
        """
        blocking_plan = []

        for i, beat in enumerate(scene_beats):
            beat_blocking = {
                "beat_number": i + 1,
                "beat_description": beat.get("description", ""),
                "character_positions": {},
                "movements": [],
                "proxemic_analysis": {},
            }

            # Assign positions based on beat dynamics
            emotional_intensity = beat.get("emotional_intensity", 0.5)
            conflict_level = beat.get("conflict_level", 0.5)

            for char in characters:
                # Calculate ideal position for this character in this beat
                position = self._calculate_ideal_position(
                    char, beat, scene_dynamics, emotional_intensity, conflict_level
                )

                beat_blocking["character_positions"][char] = {
                    "x": position.x,
                    "y": position.y,
                    "z": position.z,
                    "area": position.area,
                }

            # Analyze proxemic relationships in this beat
            char_list = list(characters)
            for j in range(len(char_list)):
                for k in range(j + 1, len(char_list)):
                    char_a_pos = CharacterPosition(
                        character_id=char_list[j],
                        position=StagePosition(
                            **beat_blocking["character_positions"][char_list[j]]
                        )
                    )
                    char_b_pos = CharacterPosition(
                        character_id=char_list[k],
                        position=StagePosition(
                            **beat_blocking["character_positions"][char_list[k]]
                        )
                    )

                    relationship = self.analyze_relationship(
                        char_a_pos,
                        char_b_pos,
                        scene_dynamics.get("relationships", {}).get(
                            f"{char_list[j]}_{char_list[k]}", {}
                        )
                    )

                    beat_blocking["proxemic_analysis"][
                        f"{char_list[j]}_{char_list[k]}"
                    ] = {
                        "distance": relationship.distance,
                        "zone": relationship.zone.value,
                        "tension": relationship.tension_level,
                        "suggestions": relationship.suggested_staging,
                    }

            blocking_plan.append(beat_blocking)

        return blocking_plan

    def _calculate_ideal_position(
        self,
        character: str,
        beat: Dict[str, Any],
        scene_dynamics: Dict[str, Any],
        emotional_intensity: float,
        conflict_level: float
    ) -> StagePosition:
        """Calculate ideal position for a character in a specific beat."""
        # Default center position
        x, y, z = 0.0, 0.0, 0.0

        # Adjust based on character role in beat
        if character == beat.get("focus_character"):
            # Focus character should be downstage center
            x = 0.0
            y = 0.5
        elif character in beat.get("supporting_characters", []):
            # Supporting characters more upstage
            y = -0.3

        # Adjust based on conflict level
        if conflict_level > 0.7:
            # High conflict - spread characters apart
            char_index = beat.get("characters", []).index(character)
            x = -0.5 + (char_index * 0.5)

        # Determine stage area
        area = "center"
        if x < -0.3:
            area = "stage_left"
        elif x > 0.3:
            area = "stage_right"

        if y < -0.3:
            area += "_upstage"
        elif y > 0.3:
            area += "_downstage"

        return StagePosition(x=x, y=y, z=z, area=area)

    def validate_blocking_continuity(
        self,
        scenes: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Validate that blocking remains consistent across scenes.

        Args:
            scenes: List of scenes with blocking information

        Returns:
            Validation report with continuity analysis
        """
        issues = []

        for i in range(len(scenes) - 1):
            current_scene = scenes[i]
            next_scene = scenes[i + 1]

            # Check if scene transitions make spatial sense
            if current_scene.get("location") == next_scene.get("location"):
                # Same location - positions should be somewhat consistent
                for character in current_scene.get("characters", []):
                    if character in next_scene.get("characters", []):
                        # Check for dramatic position changes
                        curr_pos = current_scene.get("final_positions", {}).get(character)
                        next_pos = next_scene.get("initial_positions", {}).get(character)

                        if curr_pos and next_pos:
                            if abs(curr_pos["x"] - next_pos["x"]) > 0.5:
                                issues.append({
                                    "scene_transition": f"{i} to {i+1}",
                                    "character": character,
                                    "issue": "Large position jump without justification",
                                    "suggestion": "Add stage direction explaining movement",
                                })

        return {
            "scenes_analyzed": len(scenes),
            "issues_found": len(issues),
            "issues": issues,
            "continuity_score": 1.0 - (len(issues) / max(len(scenes) - 1, 1)),
        }
