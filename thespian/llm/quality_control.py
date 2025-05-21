"""
Quality control system for theatrical content.
"""

from typing import Dict, Any, List, Optional, Union, Tuple
from pydantic import BaseModel, Field, confloat, ConfigDict
import logging
import re

logger = logging.getLogger(__name__)

class QualityMetrics(BaseModel):
    """Quality metrics for scene evaluation."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    character_development: float = Field(default=0.0, ge=0.0, le=1.0)
    dialogue_quality: float = Field(default=0.0, ge=0.0, le=1.0)
    plot_coherence: float = Field(default=0.0, ge=0.0, le=1.0)
    dramatic_tension: float = Field(default=0.0, ge=0.0, le=1.0)
    thematic_depth: float = Field(default=0.0, ge=0.0, le=1.0)
    technical_execution: float = Field(default=0.0, ge=0.0, le=1.0)
    overall_quality: float = Field(default=0.0, ge=0.0, le=1.0)


class TheatricalQualityControl(BaseModel):
    """Quality control system for theatrical content."""

    evaluations: List[Dict[str, Any]] = Field(default_factory=list)

    def evaluate_scene(self, scene: str, requirements: Any) -> Dict[str, float]:
        """Evaluate a scene across multiple dimensions."""
        evaluation = {
            "character_consistency": self._evaluate_characters(scene, requirements)["score"],
            "thematic_coherence": self._evaluate_themes(scene, requirements)["score"],
            "technical_accuracy": self._evaluate_technical(scene, requirements)["score"],
            "dramatic_impact": self._evaluate_dramatic_structure(scene)["score"],
            "dialogue_quality": self._evaluate_dialogue(scene)["score"],
            "stage_direction_quality": self._evaluate_stage_directions(scene)["score"],
        }

        self.evaluations.append(
            {"scene": scene, "requirements": requirements, "metrics": evaluation}
        )

        return evaluation

    def _evaluate_characters(self, scene: str, requirements: Any) -> Dict[str, Any]:
        """Evaluate character consistency and development."""
        # Get character names from memory
        characters = []
        for char_id in requirements.characters if hasattr(requirements, "characters") else []:
            profile = (
                self.memory.get_character_profile(char_id) if hasattr(self, "memory") else None
            )
            if profile:
                characters.append(profile.name)

        scene_content = scene.content if hasattr(scene, "content") else str(scene)
        mentioned_chars = sum(1 for char in characters if char.lower() in scene_content.lower())
        score = mentioned_chars / len(characters) if characters else 0.0

        return {
            "score": score,
            "feedback": (
                "All characters are present and well-utilized"
                if score > 0.8
                else "Some characters are underutilized or missing"
            ),
            "suggestions": (
                ["Ensure all characters have meaningful interactions"] if score < 0.8 else []
            ),
        }

    def _evaluate_themes(self, scene: str, requirements: Any) -> Dict[str, Any]:
        """Evaluate thematic coherence."""
        # Simple heuristic: check if style and period are reflected
        style = requirements.style if hasattr(requirements, "style") else ""
        period = requirements.period if hasattr(requirements, "period") else ""
        scene_content = scene.content if hasattr(scene, "content") else str(scene)

        style_present = style.lower() in scene_content.lower()
        period_present = period.lower() in scene_content.lower()
        score = sum([style_present, period_present]) / 2

        return {
            "score": score,
            "feedback": (
                "Strong thematic elements present"
                if score > 0.8
                else "Thematic elements could be strengthened"
            ),
            "suggestions": (
                [
                    "Incorporate more period-specific details",
                    "Emphasize the chosen style more clearly",
                ]
                if score < 0.8
                else []
            ),
        }

    def _evaluate_technical(self, scene: str, requirements: Any) -> Dict[str, Any]:
        """Evaluate technical accuracy."""
        # Check for technical elements
        props = requirements.props if hasattr(requirements, "props") else []
        lighting = requirements.lighting if hasattr(requirements, "lighting") else ""
        sound = requirements.sound if hasattr(requirements, "sound") else ""
        scene_content = scene.content if hasattr(scene, "content") else str(scene)

        props_used = sum(1 for prop in props if prop.lower() in scene_content.lower())
        props_score = props_used / len(props) if props else 0.0
        lighting_score = 1.0 if lighting.lower() in scene_content.lower() else 0.0
        sound_score = 1.0 if sound.lower() in scene_content.lower() else 0.0

        score = (props_score + lighting_score + sound_score) / 3

        return {
            "score": score,
            "feedback": (
                "Technical elements well integrated"
                if score > 0.8
                else "Technical elements need better integration"
            ),
            "suggestions": (
                [
                    "Ensure all props are meaningfully used",
                    "Add more specific lighting and sound cues",
                ]
                if score < 0.8
                else []
            ),
        }

    def _evaluate_dramatic_structure(self, scene: str) -> Dict[str, Any]:
        """Evaluate dramatic structure and impact."""
        # Simple heuristic: check for key dramatic elements
        dramatic_elements = ["tension", "conflict", "resolution", "climax"]
        scene_content = scene.content if hasattr(scene, "content") else str(scene)
        elements_present = sum(1 for elem in dramatic_elements if elem in scene_content.lower())
        score = elements_present / len(dramatic_elements)

        return {
            "score": score,
            "feedback": (
                "Strong dramatic structure"
                if score > 0.8
                else "Dramatic structure needs strengthening"
            ),
            "suggestions": (
                ["Add more dramatic tension", "Build to a clearer climax"] if score < 0.8 else []
            ),
        }

    def _evaluate_dialogue(self, scene: str) -> Dict[str, Any]:
        """Evaluate dialogue quality."""
        # Simple heuristic: check for dialogue markers and variety
        dialogue_markers = ["said", ":", '"', "'"]
        scene_content = scene.content if hasattr(scene, "content") else str(scene)
        has_dialogue = any(marker in scene_content for marker in dialogue_markers)
        lines = [
            line.strip()
            for line in scene_content.split("\n")
            if any(marker in line for marker in dialogue_markers)
        ]
        variety_score = len(set(lines)) / len(lines) if lines else 0.0

        score = (has_dialogue + variety_score) / 2 if has_dialogue else 0.0

        return {
            "score": score,
            "feedback": (
                "Natural and varied dialogue"
                if score > 0.8
                else "Dialogue needs more variety and naturalism"
            ),
            "suggestions": (
                ["Add more character-specific speech patterns", "Vary dialogue length and rhythm"]
                if score < 0.8
                else []
            ),
        }

    def _evaluate_stage_directions(self, scene: str) -> Dict[str, Any]:
        """Evaluate stage direction quality."""
        # Simple heuristic: check for parenthetical directions
        scene_content = scene.content if hasattr(scene, "content") else str(scene)
        lines = scene_content.split("\n")
        directions = [
            line for line in lines if line.strip().startswith("(") and line.strip().endswith(")")
        ]
        has_directions = bool(directions)
        variety_score = len(set(directions)) / len(directions) if directions else 0.0

        score = (has_directions + variety_score) / 2 if has_directions else 0.0

        return {
            "score": score,
            "feedback": (
                "Clear and varied stage directions"
                if score > 0.8
                else "Stage directions need more detail and variety"
            ),
            "suggestions": (
                ["Add more specific movement directions", "Include emotional cues in directions"]
                if score < 0.8
                else []
            ),
        }

    def get_average_metrics(self) -> Dict[str, float]:
        """Get average metrics across all evaluations."""
        if not self.evaluations:
            return {}

        total_metrics = {}
        for evaluation in self.evaluations:
            for metric, data in evaluation["metrics"].items():
                if metric not in total_metrics:
                    total_metrics[metric] = 0.0
                total_metrics[metric] += data["score"]

        return {metric: score / len(self.evaluations) for metric, score in total_metrics.items()}

    def check_scene_quality(self, scene: str) -> Tuple[bool, str]:
        """Check if a scene meets quality standards."""
        checks = [
            self._check_dialogue(scene),
            self._check_stage_directions(scene),
            self._check_character_movements(scene),
            self._check_technical_notes(scene),
            self._check_emotional_depth(scene),
            self._check_formatting(scene),
            self._check_scene_length(scene),
            self._check_character_consistency(scene),
            self._check_plot_continuity(scene),
            self._check_act_balance(scene)
        ]
        
        if all(checks):
            return True, "Scene meets all quality standards."
        
        feedback = self._generate_feedback(checks)
        return False, feedback

    def _check_scene_length(self, scene: str) -> bool:
        """Check if scene has appropriate length."""
        lines = scene.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        return len(non_empty_lines) >= 20  # Minimum 20 lines for a proper scene

    def _check_character_consistency(self, scene: str) -> bool:
        """Check for character consistency within the scene."""
        # Extract character names and their descriptions
        character_pattern = r'\(([A-Z\s]+):'
        characters = re.findall(character_pattern, scene)
        
        # Check for consistent character descriptions
        for char in set(characters):
            char_lines = [line for line in scene.split('\n') if char in line]
            if len(char_lines) < 2:  # Character should appear at least twice
                return False
        return True

    def _check_plot_continuity(self, scene: str) -> bool:
        """Check for plot continuity within the scene."""
        # Check for proper scene transitions
        if not scene.startswith('SCENE') and not scene.startswith('REVISED SCENE'):
            return False
            
        # Check for proper scene endings
        if not scene.endswith('END OF SCENE') and not scene.endswith('[End Scene]'):
            return False
            
        return True

    def _check_act_balance(self, scene: str) -> bool:
        """Check if the act is properly balanced."""
        # Count scenes in each act
        act_pattern = r'### Act (\d+)'
        scene_pattern = r'#### Scene (\d+)'
        
        acts = re.findall(act_pattern, scene)
        scenes = re.findall(scene_pattern, scene)
        
        # Each act should have 5 scenes
        if len(scenes) != 5:
            return False
            
        return True

    def _check_dialogue(self, scene: str) -> bool:
        """Check if scene has proper dialogue."""
        dialogue_pattern = r'[A-Z\s]+: \(.*\)'
        return bool(re.search(dialogue_pattern, scene))

    def _check_stage_directions(self, scene: str) -> bool:
        """Check if scene has proper stage directions."""
        direction_pattern = r'\([^)]+\)'
        return bool(re.search(direction_pattern, scene))

    def _check_character_movements(self, scene: str) -> bool:
        """Check if scene has character movements."""
        movement_pattern = r'\([A-Z\s]+ [a-z]+'
        return bool(re.search(movement_pattern, scene))

    def _check_technical_notes(self, scene: str) -> bool:
        """Check if scene has technical notes."""
        return 'TECHNICAL NOTES:' in scene or 'Notes:' in scene

    def _check_emotional_depth(self, scene: str) -> bool:
        """Check if scene has emotional depth."""
        emotion_pattern = r'\(.*emotion.*\)|\(.*feeling.*\)'
        return bool(re.search(emotion_pattern, scene))

    def _check_formatting(self, scene: str) -> bool:
        """Check if scene has proper formatting."""
        return bool(re.search(r'SCENE \d+:|REVISED SCENE:', scene))

    def _generate_feedback(self, checks: List[bool]) -> str:
        """Generate feedback based on failed checks."""
        feedback = []
        if not checks[0]:
            feedback.append("Scene lacks proper dialogue.")
        if not checks[1]:
            feedback.append("Scene lacks stage directions.")
        if not checks[2]:
            feedback.append("Scene lacks character movements.")
        if not checks[3]:
            feedback.append("Scene lacks technical notes.")
        if not checks[4]:
            feedback.append("Scene lacks emotional depth.")
        if not checks[5]:
            feedback.append("Scene lacks proper formatting.")
        if not checks[6]:
            feedback.append("Scene is too short - needs more content.")
        if not checks[7]:
            feedback.append("Scene has character consistency issues.")
        if not checks[8]:
            feedback.append("Scene has plot continuity issues.")
        if not checks[9]:
            feedback.append("Scene doesn't maintain proper act balance.")
        
        return "\n".join(feedback)
