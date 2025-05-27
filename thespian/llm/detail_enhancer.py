"""
Scene Detail Enhancement System for expanding and enriching theatrical scenes.
"""

from typing import Dict, Any, List, Optional, Tuple
import re
from dataclasses import dataclass, field
import json


@dataclass
class DetailLayer:
    """Represents a layer of detail that can be added to a scene."""
    layer_type: str  # subtext, atmosphere, technical, character_detail, etc.
    content: str
    location: Optional[str] = None  # Where in the scene to add this
    priority: int = 5  # 1-10, higher = more important


@dataclass
class EnhancementStrategy:
    """Strategy for enhancing a particular aspect of a scene."""
    name: str
    target_element: str  # dialogue, stage_directions, character_actions, etc.
    enhancement_prompts: List[str] = field(default_factory=list)
    min_addition_length: int = 100
    max_additions_per_scene: int = 5


class SceneDetailEnhancer:
    """Enhances scenes with rich detail to meet length and quality requirements."""
    
    def __init__(self, target_length: int = 5000, enable_all_layers: bool = True):
        """Initialize the detail enhancer.
        
        Args:
            target_length: Target character count for scenes
            enable_all_layers: Whether to use all enhancement layers
        """
        self.target_length = target_length
        self.enable_all_layers = enable_all_layers
        self.enhancement_strategies = self._initialize_strategies()
        self.detail_layers = []
    
    def _initialize_strategies(self) -> Dict[str, EnhancementStrategy]:
        """Initialize enhancement strategies."""
        return {
            "subtext": EnhancementStrategy(
                name="Subtext Enhancement",
                target_element="dialogue",
                enhancement_prompts=[
                    "Add unspoken tensions and hidden meanings",
                    "Include physical reactions that contradict words",
                    "Layer in character's true feelings through action",
                    "Add pauses, hesitations, and meaningful silences"
                ],
                min_addition_length=150
            ),
            "atmosphere": EnhancementStrategy(
                name="Atmospheric Detail",
                target_element="stage_directions",
                enhancement_prompts=[
                    "Describe lighting changes and shadow play",
                    "Add ambient sounds and their emotional effect",
                    "Include sensory details (smells, temperature, textures)",
                    "Describe the space's emotional resonance"
                ],
                min_addition_length=200
            ),
            "character_business": EnhancementStrategy(
                name="Character Business",
                target_element="character_actions",
                enhancement_prompts=[
                    "Add specific physical activities while speaking",
                    "Include nervous habits and unconscious gestures",
                    "Describe how characters occupy space",
                    "Add interactions with props and environment"
                ],
                min_addition_length=100
            ),
            "technical_elements": EnhancementStrategy(
                name="Technical Elements",
                target_element="technical_cues",
                enhancement_prompts=[
                    "Specify exact lighting states and transitions",
                    "Add detailed sound cues with timing",
                    "Include projection or special effects",
                    "Describe costume details revealed in action"
                ],
                min_addition_length=100
            ),
            "internal_life": EnhancementStrategy(
                name="Internal Life",
                target_element="character_thoughts",
                enhancement_prompts=[
                    "Add parenthetical emotional states",
                    "Include internal conflicts during dialogue",
                    "Describe micro-expressions and tells",
                    "Add subconscious reactions"
                ],
                min_addition_length=80
            ),
            "relationship_dynamics": EnhancementStrategy(
                name="Relationship Dynamics",
                target_element="interactions",
                enhancement_prompts=[
                    "Show power dynamics through positioning",
                    "Add physical distance/closeness changes",
                    "Include mirroring or contrasting movements",
                    "Describe territorial behavior"
                ],
                min_addition_length=120
            ),
            "environmental_storytelling": EnhancementStrategy(
                name="Environmental Storytelling",
                target_element="setting_details",
                enhancement_prompts=[
                    "Describe wear patterns telling history",
                    "Add details revealing character through space",
                    "Include time of day effects on the environment",
                    "Show how the space has been lived in"
                ],
                min_addition_length=150
            )
        }
    
    def analyze_scene(self, scene_content: str) -> Dict[str, Any]:
        """Analyze a scene to determine what enhancements are needed.
        
        Returns:
            Analysis including current length, structure, and enhancement opportunities
        """
        analysis = {
            "current_length": len(scene_content),
            "length_deficit": max(0, self.target_length - len(scene_content)),
            "structure": self._analyze_structure(scene_content),
            "enhancement_opportunities": [],
            "dialogue_to_direction_ratio": self._calculate_dialogue_ratio(scene_content)
        }
        
        # Identify where we can add detail
        if analysis["dialogue_to_direction_ratio"] > 0.8:
            analysis["enhancement_opportunities"].append("needs_more_stage_directions")
        if analysis["dialogue_to_direction_ratio"] < 0.4:
            analysis["enhancement_opportunities"].append("needs_more_dialogue")
        
        # Check for missing elements
        if "[" not in scene_content and "(" not in scene_content:
            analysis["enhancement_opportunities"].append("needs_technical_annotations")
        
        if not re.search(r'\b(slowly|quickly|carefully|nervously|hesitantly)\b', scene_content, re.I):
            analysis["enhancement_opportunities"].append("needs_movement_qualities")
        
        if not re.search(r'(pause|beat|silence|moment)', scene_content, re.I):
            analysis["enhancement_opportunities"].append("needs_pacing_elements")
        
        return analysis
    
    def _analyze_structure(self, scene_content: str) -> Dict[str, int]:
        """Analyze the structural elements of a scene."""
        lines = scene_content.split('\n')
        structure = {
            "total_lines": len(lines),
            "dialogue_lines": 0,
            "stage_direction_lines": 0,
            "character_names": set(),
            "technical_cues": 0
        }
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Character dialogue (NAME: dialogue)
            if ':' in line and line.split(':')[0].strip().isupper():
                structure["dialogue_lines"] += 1
                structure["character_names"].add(line.split(':')[0].strip())
            # Stage directions (in brackets or parentheses)
            elif line.startswith('[') or line.startswith('('):
                structure["stage_direction_lines"] += 1
            # Technical cues
            elif any(cue in line.upper() for cue in ['LIGHTS:', 'SOUND:', 'MUSIC:', 'SFX:']):
                structure["technical_cues"] += 1
        
        structure["character_count"] = len(structure["character_names"])
        structure["character_names"] = list(structure["character_names"])
        
        return structure
    
    def _calculate_dialogue_ratio(self, scene_content: str) -> float:
        """Calculate the ratio of dialogue to stage directions."""
        dialogue_chars = 0
        direction_chars = 0
        
        lines = scene_content.split('\n')
        for line in lines:
            line = line.strip()
            if ':' in line and line.split(':')[0].strip().isupper():
                # This is dialogue
                dialogue_chars += len(line.split(':', 1)[1])
            elif line.startswith('[') or line.startswith('('):
                # This is a stage direction
                direction_chars += len(line)
        
        total = dialogue_chars + direction_chars
        if total == 0:
            return 0.5
        
        return dialogue_chars / total
    
    def enhance_scene(self, scene_content: str, analysis: Optional[Dict[str, Any]] = None) -> str:
        """Enhance a scene with additional detail.
        
        Args:
            scene_content: Original scene content
            analysis: Pre-computed analysis (optional)
            
        Returns:
            Enhanced scene content
        """
        if analysis is None:
            analysis = self.analyze_scene(scene_content)
        
        enhanced_content = scene_content
        
        # Apply enhancement strategies based on needs
        length_added = 0
        target_addition = analysis["length_deficit"]
        
        if target_addition <= 0:
            return enhanced_content  # Already long enough
        
        # Prioritize strategies based on opportunities
        strategies_to_apply = []
        
        if "needs_more_stage_directions" in analysis["enhancement_opportunities"]:
            strategies_to_apply.extend(["atmosphere", "character_business", "environmental_storytelling"])
        
        if "needs_movement_qualities" in analysis["enhancement_opportunities"]:
            strategies_to_apply.append("character_business")
        
        if "needs_pacing_elements" in analysis["enhancement_opportunities"]:
            strategies_to_apply.append("internal_life")
        
        # Always include some core strategies
        strategies_to_apply.extend(["subtext", "relationship_dynamics"])
        
        # Remove duplicates while preserving order
        strategies_to_apply = list(dict.fromkeys(strategies_to_apply))
        
        # Apply strategies
        for strategy_name in strategies_to_apply:
            if length_added >= target_addition:
                break
            
            if strategy_name in self.enhancement_strategies:
                strategy = self.enhancement_strategies[strategy_name]
                enhanced_content = self._apply_strategy(enhanced_content, strategy, analysis)
                
                new_length = len(enhanced_content)
                length_added = new_length - len(scene_content)
        
        # If still too short, add more comprehensive enhancements
        if len(enhanced_content) < self.target_length:
            enhanced_content = self._add_comprehensive_details(enhanced_content, analysis)
        
        return enhanced_content
    
    def _apply_strategy(self, content: str, strategy: EnhancementStrategy, analysis: Dict[str, Any]) -> str:
        """Apply a specific enhancement strategy to the content."""
        lines = content.split('\n')
        enhanced_lines = []
        additions_made = 0
        
        i = 0
        while i < len(lines):
            line = lines[i]
            enhanced_lines.append(line)
            
            # Decide if we should add enhancement after this line
            if additions_made < strategy.max_additions_per_scene:
                if self._should_enhance_here(line, strategy, analysis):
                    enhancement = self._generate_enhancement(line, strategy, analysis)
                    if enhancement:
                        enhanced_lines.append(enhancement)
                        additions_made += 1
            
            i += 1
        
        return '\n'.join(enhanced_lines)
    
    def _should_enhance_here(self, line: str, strategy: EnhancementStrategy, analysis: Dict[str, Any]) -> bool:
        """Determine if enhancement should be added after this line."""
        line = line.strip()
        
        # Strategy-specific logic
        if strategy.target_element == "dialogue" and ':' in line:
            # Enhance after dialogue lines
            return line.split(':')[0].strip().isupper()
        
        elif strategy.target_element == "stage_directions":
            # Enhance between dialogue sections
            return ':' in line and not line.startswith('[')
        
        elif strategy.target_element == "character_actions":
            # Enhance when characters are mentioned
            for char in analysis["structure"].get("character_names", []):
                if char in line:
                    return True
        
        elif strategy.target_element == "technical_cues":
            # Enhance at scene transitions
            return any(marker in line.upper() for marker in ['ENTER', 'EXIT', 'LIGHTS', 'SCENE'])
        
        return False
    
    def _generate_enhancement(self, context_line: str, strategy: EnhancementStrategy, analysis: Dict[str, Any]) -> str:
        """Generate enhancement content based on context and strategy."""
        # This is where we would call an LLM in the real implementation
        # For now, return template-based enhancements
        
        templates = {
            "subtext": [
                "[{character} glances away, fingers tightening on the edge of the table]",
                "[A pause. The unspoken words hang heavy in the air between them]",
                "[{character}'s smile doesn't quite reach their eyes]",
                "[The silence stretches, loaded with everything they cannot say]"
            ],
            "atmosphere": [
                "[The afternoon light slants through dusty windows, casting long shadows across the floor]",
                "[Somewhere in the distance, a clock ticks relentlessly, marking each tense second]",
                "[The air feels thick, oppressive, as if the room itself holds its breath]",
                "[Outside, the wind picks up, rattling the windows like restless spirits]"
            ],
            "character_business": [
                "[{character} picks up a book, pages through it without seeing, sets it down again]",
                "[Moving to the window, {character} traces patterns in the condensation]",
                "[{character} straightens items on the desk, creating order in the chaos]",
                "[Hands find pockets, then hair, then pockets again—a restless dance of anxiety]"
            ],
            "technical_elements": [
                "[LIGHTS: Subtle shift to cooler tones, suggesting emotional distance]",
                "[SOUND: Faint traffic noise fades, leaving only the sound of breathing]",
                "[The afternoon sun gradually dims through the scene, marking time's passage]",
                "[MUSIC: Underscoring swells almost imperceptibly, supporting the emotional build]"
            ],
            "internal_life": [
                "[{character} (fighting to maintain composure)]",
                "[{character} (the words catching in their throat)]",
                "[{character} (searching for the right words, finding none)]",
                "[{character} (a flash of something—regret?—crosses their face)]"
            ],
            "relationship_dynamics": [
                "[They stand at opposite ends of the room now, the distance between them palpable]",
                "[{character} takes a step forward; the other instinctively moves back]",
                "[For a moment, they move in unconscious synchrony, old habits die hard]",
                "[The space between them feels charged, electric with unspoken history]"
            ],
            "environmental_storytelling": [
                "[The worn patch on the armchair speaks of countless evenings spent waiting]",
                "[Family photos on the mantle watch the scene unfold, silent witnesses]",
                "[A half-finished puzzle on the side table—abandoned, like so much else]",
                "[The room bears the scars of their life together: marks on the floor, faded wallpaper]"
            ]
        }
        
        # Get appropriate templates
        enhancement_templates = templates.get(strategy.name.lower().replace(" ", "_"), [])
        if not enhancement_templates:
            return ""
        
        # Select and customize a template
        import random
        template = random.choice(enhancement_templates)
        
        # Extract character name from context if available
        character = "They"
        if ':' in context_line:
            character = context_line.split(':')[0].strip()
        
        enhancement = template.replace("{character}", character)
        
        return enhancement
    
    def _add_comprehensive_details(self, content: str, analysis: Dict[str, Any]) -> str:
        """Add comprehensive details throughout the scene."""
        lines = content.split('\n')
        enhanced_lines = []
        
        # Add opening atmosphere if not present
        if not any(line.strip().startswith('[') for line in lines[:5]):
            enhanced_lines.append("[The scene opens on a space heavy with anticipation. Every object, every shadow seems to wait.]")
            enhanced_lines.append("")
        
        # Process each section
        for i, line in enumerate(lines):
            enhanced_lines.append(line)
            
            # Add details at natural breaks
            if i > 0 and i % 10 == 0 and line.strip() == "":
                # Add a substantial stage direction
                detail = self._generate_comprehensive_detail(lines[max(0, i-5):i], analysis)
                if detail:
                    enhanced_lines.append(detail)
        
        # Add closing moment if needed
        if len(enhanced_lines) < len(lines) * 1.5:
            enhanced_lines.append("")
            enhanced_lines.append("[The lights fade slowly, leaving the characters in silhouette—frozen in this moment that will echo long after the darkness claims them.]")
        
        return '\n'.join(enhanced_lines)
    
    def _generate_comprehensive_detail(self, context_lines: List[str], analysis: Dict[str, Any]) -> str:
        """Generate a comprehensive detail paragraph based on context."""
        # Analyze recent dialogue for mood
        recent_dialogue = ' '.join([line for line in context_lines if ':' in line])
        
        # Generate appropriate atmospheric detail
        detail_options = [
            "[The weight of what has been said—and what hasn't—settles over the room like dust. "
            "Every surface seems to absorb the tension, the very walls becoming witnesses to this "
            "moment of reckoning. Time slows, stretches, each heartbeat a small eternity.]",
            
            "[In the growing silence, small sounds become significant: the creak of a floorboard, "
            "the distant hum of traffic, the whisper of fabric as someone shifts their weight. "
            "The ordinary world continues outside, oblivious to the seismic shifts occurring within "
            "these four walls.]",
            
            "[The space between the characters has become a living thing—expanding and contracting "
            "with each word, each gesture. They navigate around furniture like sailors around rocks, "
            "every movement calculated, every position strategic. The room has become a battlefield "
            "of emotions, and they are both generals and soldiers.]",
            
            "[Light plays across their faces, revealing and concealing in turn. In this moment, "
            "they are simultaneously the people they were, are, and might become—all versions "
            "existing in the same space, the same breath. The past and future collapse into this "
            "single, crystalline now.]"
        ]
        
        import random
        return random.choice(detail_options)
    
    def inject_subtext_layers(self, content: str) -> str:
        """Inject layers of subtext throughout the scene."""
        lines = content.split('\n')
        enhanced_lines = []
        
        for i, line in enumerate(lines):
            enhanced_lines.append(line)
            
            # Add subtext after certain dialogue patterns
            if ':' in line and any(word in line.lower() for word in ['fine', 'okay', 'nothing', 'sure']):
                # These words often hide true feelings
                char = line.split(':')[0].strip()
                subtext_options = [
                    f"[{char}'s voice betrays what their words deny]",
                    f"[The word hangs between truth and fiction]",
                    f"[{char} looks anywhere but at the person they're addressing]",
                    f"[A micro-expression flickers across {char}'s face—gone before it can be read]"
                ]
                import random
                enhanced_lines.append(random.choice(subtext_options))
        
        return '\n'.join(enhanced_lines)
    
    def expand_technical_elements(self, content: str) -> str:
        """Expand technical elements with specific cues and timing."""
        lines = content.split('\n')
        enhanced_lines = []
        
        scene_time = "afternoon"  # Would be determined by scene analysis
        
        for i, line in enumerate(lines):
            # Add technical cues at key moments
            if i == 0:
                enhanced_lines.append(f"[LIGHTS: Fade up on {scene_time} wash, warm but with cool undertones suggesting unease]")
            
            enhanced_lines.append(line)
            
            # Add sound cues for entrances/exits
            if any(word in line.upper() for word in ['ENTERS', 'EXITS', 'ENTER', 'EXIT']):
                enhanced_lines.append("[SOUND: Footsteps, the particular rhythm revealing emotional state]")
            
            # Add lighting changes for emotional shifts
            if any(word in line.lower() for word in ['realizes', 'understands', 'discovers']):
                enhanced_lines.append("[LIGHTS: Subtle shift, as if the world has tilted on its axis]")
        
        return '\n'.join(enhanced_lines)
    
    def create_detail_plan(self, scene_content: str) -> List[DetailLayer]:
        """Create a plan for what details to add to a scene."""
        analysis = self.analyze_scene(scene_content)
        detail_plan = []
        
        # Calculate how much we need to add
        length_needed = analysis["length_deficit"]
        if length_needed <= 0:
            return detail_plan
        
        # Plan detail layers based on what's missing
        if analysis["dialogue_to_direction_ratio"] > 0.7:
            # Too much dialogue, need more action/atmosphere
            detail_plan.append(DetailLayer(
                layer_type="atmosphere",
                content="Rich atmospheric descriptions between dialogue sections",
                priority=9
            ))
            detail_plan.append(DetailLayer(
                layer_type="character_business", 
                content="Specific physical actions during dialogue",
                priority=8
            ))
        
        if "needs_pacing_elements" in analysis["enhancement_opportunities"]:
            detail_plan.append(DetailLayer(
                layer_type="pacing",
                content="Pauses, beats, and rhythm markers",
                priority=7
            ))
        
        # Always add some subtext
        detail_plan.append(DetailLayer(
            layer_type="subtext",
            content="Unspoken tensions and contradictions",
            priority=6
        ))
        
        # Technical elements if missing
        if analysis["structure"]["technical_cues"] < 3:
            detail_plan.append(DetailLayer(
                layer_type="technical",
                content="Lighting, sound, and other technical cues",
                priority=5
            ))
        
        return sorted(detail_plan, key=lambda x: x.priority, reverse=True)