"""
Subtext Layering Agent

Analyzes and enhances dialogue with multiple levels of meaning,
creating theatrical depth where characters say one thing but mean another.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import re


class SubtextType(str, Enum):
    """Types of subtext in dialogue."""
    EMOTIONAL = "emotional"  # Hiding true emotions
    INTENTIONAL = "intentional"  # Hidden agendas or goals
    SOCIAL = "social"  # Social dynamics and power plays
    PSYCHOLOGICAL = "psychological"  # Inner conflicts and desires
    DRAMATIC_IRONY = "dramatic_irony"  # Audience knows more than characters
    CONTEXTUAL = "contextual"  # Meaning derived from context/history


@dataclass
class SubtextLayer:
    """Represents a layer of subtext in dialogue."""
    surface_meaning: str  # What is actually said
    hidden_meaning: str  # What is really meant
    subtext_type: SubtextType
    intensity: float = 0.5  # How strong the subtext is (0-1)
    character_id: Optional[str] = None
    line_number: Optional[int] = None
    context_clues: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DialogueLine:
    """Represents a line of dialogue with its subtext."""
    character: str
    text: str
    line_number: int
    subtext_layers: List[SubtextLayer] = field(default_factory=list)
    stage_direction: Optional[str] = None
    emotional_state: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class SubtextLayeringAgent:
    """
    Agent for analyzing and enhancing dialogue with subtext.

    Capabilities:
    - Identify potential subtext in existing dialogue
    - Suggest subtextual layers for scenes
    - Analyze emotional vs. spoken content
    - Generate stage directions that reveal subtext
    - Ensure consistency of hidden meanings across scenes
    """

    def __init__(self, llm_manager=None):
        """Initialize the subtext layering agent."""
        self.llm_manager = llm_manager
        self.known_patterns = self._initialize_patterns()
        self.character_profiles: Dict[str, Dict[str, Any]] = {}

    def _initialize_patterns(self) -> Dict[str, List[str]]:
        """Initialize common subtext patterns."""
        return {
            "deflection": [
                r"I'm fine",
                r"It doesn't matter",
                r"Whatever you want",
                r"I don't care",
            ],
            "hidden_emotion": [
                r"I'm happy for you",
                r"That's great",
                r"Good for you",
                r"I understand",
            ],
            "power_play": [
                r"If you think that's best",
                r"I trust your judgment",
                r"You would know",
                r"I defer to you",
            ],
            "avoidance": [
                r"Can we talk about this later",
                r"I'd rather not discuss",
                r"Let's change the subject",
            ],
        }

    def analyze_dialogue(
        self,
        dialogue_lines: List[DialogueLine],
        scene_context: Optional[Dict[str, Any]] = None
    ) -> List[DialogueLine]:
        """
        Analyze dialogue and identify potential subtext.

        Args:
            dialogue_lines: List of dialogue lines to analyze
            scene_context: Optional context about the scene

        Returns:
            Dialogue lines enriched with subtext analysis
        """
        analyzed_lines = []

        for line in dialogue_lines:
            # Check for pattern-based subtext
            subtext_layers = self._detect_pattern_subtext(line.text)

            # Add contextual analysis if context provided
            if scene_context:
                contextual_layers = self._analyze_contextual_subtext(
                    line, scene_context
                )
                subtext_layers.extend(contextual_layers)

            # Update line with detected subtext
            line.subtext_layers = subtext_layers
            analyzed_lines.append(line)

        return analyzed_lines

    def _detect_pattern_subtext(self, text: str) -> List[SubtextLayer]:
        """Detect subtext based on known patterns."""
        subtext_layers = []

        for pattern_type, patterns in self.known_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    # Map pattern type to SubtextType
                    subtext_type = self._map_pattern_to_type(pattern_type)

                    layer = SubtextLayer(
                        surface_meaning=text,
                        hidden_meaning=self._infer_hidden_meaning(text, pattern_type),
                        subtext_type=subtext_type,
                        intensity=0.6,
                        context_clues=[f"Pattern match: {pattern_type}"]
                    )
                    subtext_layers.append(layer)

        return subtext_layers

    def _map_pattern_to_type(self, pattern_type: str) -> SubtextType:
        """Map pattern categories to SubtextType."""
        mapping = {
            "deflection": SubtextType.EMOTIONAL,
            "hidden_emotion": SubtextType.EMOTIONAL,
            "power_play": SubtextType.SOCIAL,
            "avoidance": SubtextType.PSYCHOLOGICAL,
        }
        return mapping.get(pattern_type, SubtextType.CONTEXTUAL)

    def _infer_hidden_meaning(self, text: str, pattern_type: str) -> str:
        """Infer the hidden meaning based on the pattern type."""
        inferences = {
            "deflection": "The character is hiding their true emotional state.",
            "hidden_emotion": "The character feels the opposite of what they're saying.",
            "power_play": "The character is asserting or testing social hierarchy.",
            "avoidance": "The character is uncomfortable with the topic.",
        }
        return inferences.get(pattern_type, "Hidden meaning present.")

    def _analyze_contextual_subtext(
        self,
        line: DialogueLine,
        context: Dict[str, Any]
    ) -> List[SubtextLayer]:
        """Analyze subtext based on scene context."""
        layers = []

        # Check for dramatic irony
        if context.get("audience_knowledge") and context.get("character_knowledge"):
            audience_knows = context["audience_knowledge"]
            char_knows = context["character_knowledge"].get(line.character, set())

            knowledge_gap = audience_knows - char_knows
            if knowledge_gap:
                layers.append(SubtextLayer(
                    surface_meaning=line.text,
                    hidden_meaning=f"Character unaware of: {', '.join(knowledge_gap)}",
                    subtext_type=SubtextType.DRAMATIC_IRONY,
                    intensity=0.8,
                    character_id=line.character,
                    context_clues=[f"Knowledge gap: {len(knowledge_gap)} items"]
                ))

        # Check for relationship dynamics
        if context.get("relationships") and line.character in context["relationships"]:
            rel_data = context["relationships"][line.character]
            for other_char, dynamic in rel_data.items():
                if dynamic.get("tension_level", 0) > 0.5:
                    layers.append(SubtextLayer(
                        surface_meaning=line.text,
                        hidden_meaning=f"Unresolved tension with {other_char}",
                        subtext_type=SubtextType.SOCIAL,
                        intensity=dynamic["tension_level"],
                        character_id=line.character,
                        context_clues=[f"Relationship tension: {dynamic.get('type', 'unknown')}"]
                    ))

        return layers

    def enhance_with_subtext(
        self,
        dialogue: str,
        character_goals: Optional[Dict[str, str]] = None,
        relationship_dynamics: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Enhance plain dialogue with subtext suggestions.

        Args:
            dialogue: The dialogue text to enhance
            character_goals: Optional dictionary of character goals
            relationship_dynamics: Optional relationship information

        Returns:
            Dictionary containing enhanced dialogue and subtext information
        """
        # Parse dialogue into lines
        lines = self._parse_dialogue(dialogue)

        # Build scene context
        context = {
            "character_goals": character_goals or {},
            "relationships": relationship_dynamics or {},
        }

        # Analyze for subtext
        analyzed_lines = self.analyze_dialogue(lines, context)

        # Generate enhancement suggestions
        suggestions = self._generate_enhancement_suggestions(analyzed_lines)

        return {
            "original_dialogue": dialogue,
            "analyzed_lines": [
                {
                    "character": line.character,
                    "text": line.text,
                    "subtext_count": len(line.subtext_layers),
                    "subtext_layers": [
                        {
                            "type": layer.subtext_type.value,
                            "hidden_meaning": layer.hidden_meaning,
                            "intensity": layer.intensity,
                        }
                        for layer in line.subtext_layers
                    ]
                }
                for line in analyzed_lines
            ],
            "enhancement_suggestions": suggestions,
        }

    def _parse_dialogue(self, dialogue: str) -> List[DialogueLine]:
        """Parse dialogue text into DialogueLine objects."""
        lines = []
        dialogue_pattern = r'^([A-Z][A-Z\s]+):\s*(.+)$'

        for i, line in enumerate(dialogue.split('\n'), 1):
            line = line.strip()
            if not line:
                continue

            match = re.match(dialogue_pattern, line)
            if match:
                character = match.group(1).strip()
                text = match.group(2).strip()

                lines.append(DialogueLine(
                    character=character,
                    text=text,
                    line_number=i
                ))

        return lines

    def _generate_enhancement_suggestions(
        self,
        analyzed_lines: List[DialogueLine]
    ) -> List[Dict[str, Any]]:
        """Generate suggestions for enhancing subtext."""
        suggestions = []

        for line in analyzed_lines:
            if not line.subtext_layers:
                # Suggest adding subtext to plain lines
                suggestions.append({
                    "line_number": line.line_number,
                    "character": line.character,
                    "suggestion_type": "add_subtext",
                    "recommendation": "Consider adding emotional subtext or hidden meaning to this line.",
                })
            else:
                # Suggest stage directions to reveal subtext
                for layer in line.subtext_layers:
                    if layer.intensity > 0.6:
                        suggestions.append({
                            "line_number": line.line_number,
                            "character": line.character,
                            "suggestion_type": "stage_direction",
                            "recommendation": f"Add stage direction to reveal {layer.subtext_type.value} subtext.",
                            "example": self._suggest_stage_direction(layer),
                        })

        return suggestions

    def _suggest_stage_direction(self, layer: SubtextLayer) -> str:
        """Suggest a stage direction based on subtext type."""
        suggestions = {
            SubtextType.EMOTIONAL: "(with forced smile, eyes betraying sadness)",
            SubtextType.INTENTIONAL: "(choosing words carefully, hiding true purpose)",
            SubtextType.SOCIAL: "(assertive posture, maintaining eye contact)",
            SubtextType.PSYCHOLOGICAL: "(fidgeting, avoiding the subject)",
            SubtextType.DRAMATIC_IRONY: "(unaware of the danger, speaking confidently)",
            SubtextType.CONTEXTUAL: "(weighted pause, remembering past events)",
        }
        return suggestions.get(layer.subtext_type, "(meaningful pause)")

    def generate_subtext_prompt(
        self,
        scene_summary: str,
        characters: List[str],
        desired_layers: List[SubtextType]
    ) -> str:
        """
        Generate a prompt for LLM to create dialogue with specific subtext.

        Args:
            scene_summary: Summary of the scene
            characters: List of characters involved
            desired_layers: Types of subtext to include

        Returns:
            A prompt string for LLM generation
        """
        layer_descriptions = {
            SubtextType.EMOTIONAL: "characters hiding or contradicting their true feelings",
            SubtextType.INTENTIONAL: "characters with hidden agendas or goals",
            SubtextType.SOCIAL: "power dynamics and social maneuvering",
            SubtextType.PSYCHOLOGICAL: "inner conflicts manifesting in dialogue",
            SubtextType.DRAMATIC_IRONY: "characters unaware of information known to the audience",
            SubtextType.CONTEXTUAL: "meanings derived from character history and relationships",
        }

        layers_text = "\n".join([
            f"- {layer_descriptions[layer]}"
            for layer in desired_layers
        ])

        return f"""
Generate dialogue for a theatrical scene with rich subtext and layered meanings.

Scene Summary: {scene_summary}

Characters: {', '.join(characters)}

Required Subtext Layers:
{layers_text}

Requirements:
1. Characters should say one thing while meaning another
2. Include subtle contradictions between words and emotions
3. Layer multiple levels of meaning in key exchanges
4. Use pauses, interruptions, and non-verbal cues
5. Create dramatic tension through what is NOT said
6. Ensure subtext is discoverable but not obvious

Format: Standard theatrical dialogue with character names, lines, and stage directions.
"""

    def validate_subtext_consistency(
        self,
        scenes: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Validate that subtext remains consistent across multiple scenes.

        Args:
            scenes: List of scenes with dialogue and subtext

        Returns:
            Validation report with consistency analysis
        """
        inconsistencies = []
        character_subtexts: Dict[str, List[SubtextLayer]] = {}

        # Collect all subtext layers by character
        for scene in scenes:
            if "dialogue_lines" in scene:
                for line in scene["dialogue_lines"]:
                    char = line.get("character")
                    if char:
                        if char not in character_subtexts:
                            character_subtexts[char] = []
                        character_subtexts[char].extend(
                            line.get("subtext_layers", [])
                        )

        # Check for contradictory subtexts
        for character, layers in character_subtexts.items():
            emotional_layers = [
                l for l in layers
                if l.subtext_type == SubtextType.EMOTIONAL
            ]

            if len(emotional_layers) > 1:
                # Check if emotional subtexts contradict
                meanings = [l.hidden_meaning for l in emotional_layers]
                if len(set(meanings)) > 1:
                    inconsistencies.append({
                        "character": character,
                        "issue": "Contradictory emotional subtext",
                        "details": f"Found {len(set(meanings))} different emotional states",
                    })

        return {
            "total_characters_analyzed": len(character_subtexts),
            "total_subtext_layers": sum(len(layers) for layers in character_subtexts.values()),
            "inconsistencies_found": len(inconsistencies),
            "inconsistencies": inconsistencies,
            "consistency_score": 1.0 - (len(inconsistencies) / max(len(character_subtexts), 1)),
        }
