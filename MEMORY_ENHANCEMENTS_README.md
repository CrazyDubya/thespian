# Thespian Memory Enhancement System

This document describes the memory enhancement system added to the Thespian framework to improve character development and narrative continuity across scenes and acts.

## Overview of Memory Enhancements

The memory enhancement system adds sophisticated character and narrative tracking that enables:

1. **Dynamic Character Evolution** - Characters evolve naturally across scenes with tracked emotional states, relationship changes, belief shifts, and arc progression
2. **Narrative Continuity** - Plot points, thematic developments, causal connections, and foreshadowing elements persist across scenes
3. **Memory-Enhanced Generation** - Scene generation incorporates character history, emotional states, and narrative elements
4. **Character-Focused Scenes** - Generate scenes specifically designed to develop characters through classic arc stages

## Core Components

### 1. Enhanced Character Profiles

The `EnhancedCharacterProfile` class extends the basic character profile with:

- **Development Arc** - Tracks a character's evolution through multiple stages
- **Emotional States** - Records emotional changes and their causes
- **Relationship Developments** - Maintains relationship history with other characters
- **Belief Changes** - Tracks shifts in a character's beliefs and values
- **Key Experiences** - Records significant events that impact the character
- **Psychological Attributes** - Tracks fears, desires, flaws, strengths, and values

```python
# Example of an enhanced character profile
chen_profile = EnhancedCharacterProfile(
    id="dr_sarah_chen",
    name="DR. SARAH CHEN",
    background="Brilliant physicist specializing in quantum mechanics...",
    motivations=["Discovering scientific truth", "Ethical application of technology"],
    relationships={"DR. JAMES TANAKA": "Colleague and research partner"},
    goals=["Complete the quantum research", "Ensure ethical use of discoveries"],
    conflicts=["Ethical concerns vs scientific progress"],
    fears=["Loss of control over her research"],
    desires=["Scientific breakthrough without compromising ethics"],
    values=["Scientific integrity", "Ethical responsibility"],
    strengths=["Brilliant intellect", "Ethical awareness"],
    flaws=["Workaholic tendencies", "Difficulty trusting others"]
)
```

### 2. Narrative Continuity Tracking

The `NarrativeContinuityTracker` class maintains:

- **Plot Points** - Significant narrative events with character involvement
- **Thematic Developments** - Evolution of themes across scenes
- **Causal Connections** - Cause-effect relationships between events
- **Foreshadowing Elements** - Planted elements and their intended payoffs
- **Scene Connections** - Relationships between different scenes

### 3. Character Analysis System

The `CharacterTracker` class provides:

- **Automatic scene analysis** - Extracts character activity, emotions, and relationships
- **Character presence tracking** - Records character involvement across scenes
- **Importance scoring** - Evaluates character importance in each scene
- **Relationship development tracking** - Monitors how relationships evolve

### 4. Memory-Enhanced Playwright

The `MemoryEnhancedPlaywright` extends `EnhancedPlaywright` with:

- **Memory context integration** - Incorporates character and narrative memory into scene generation
- **Character-focused generation** - Creates scenes designed to develop specific characters
- **Character arc scenes** - Generates scenes for specific character arc stages
- **Automatic memory updates** - Updates memory after each scene generation

## How to Use the Memory Enhancement System

### Basic Usage

```python
from thespian.llm import LLMManager
from thespian.llm.memory_enhanced_playwright import MemoryEnhancedPlaywright
from thespian.llm.enhanced_memory import EnhancedTheatricalMemory

# Initialize memory system
memory = EnhancedTheatricalMemory()

# Create memory-enhanced playwright
playwright = MemoryEnhancedPlaywright(
    name="Memory-Enhanced Playwright",
    llm_manager=llm_manager,
    memory=memory,  # Base memory system
    enhanced_memory=memory,  # Enhanced memory system
    quality_control=quality_control,
    track_characters=True,  # Enable character tracking
    track_narrative=True,  # Enable narrative tracking
    memory_integration_level=2  # Standard memory integration (1=basic, 2=standard, 3=deep)
)

# Initialize character profiles
chen_profile = EnhancedCharacterProfile(...)
memory.update_character_profile("dr_chen", chen_profile)

# Generate scene with memory context
result = playwright.generate_scene(requirements)

# Get character summary after scene generation
char_summary = playwright.get_character_summary("dr_chen")

# Generate character-focused scene
result = playwright.create_scene_with_character_focus(
    requirements,
    "dr_chen",
    {
        "aspect": "internal conflict",
        "moment_type": "revelation",
        "relationship_with": "DR. JAMES",
        "reveal_aspect": "motivation"
    }
)

# Generate character arc scene
result = playwright.generate_character_arc_scene(
    act_number=1,
    scene_number=1,
    character_id="dr_chen",
    arc_stage="call_to_adventure"  # From the hero's journey or other arc types
)
```

### Character Arc Stages

The system supports generating scenes focused on specific character arc stages:

**Hero's Journey Stages**:
- `ordinary_world` - Character's normal life before the adventure
- `call_to_adventure` - Character receives a challenge or call to change
- `refusal` - Character initially refuses or is reluctant
- `meeting_mentor` - Character encounters a mentor figure
- `crossing_threshold` - Character commits to the adventure/change
- `tests_allies_enemies` - Character faces challenges and meets allies/enemies
- `approach` - Character prepares for the major challenge
- `ordeal` - Character faces their greatest challenge
- `reward` - Character achieves their goal, but challenges remain
- `road_back` - Character deals with consequences
- `resurrection` - Character faces a final test
- `return` - Character returns transformed

**Alternative Arc Stages**:
- `catalyst` - Event that upsets the status quo
- `debate` - Character questions whether to pursue the goal
- `breakthrough` - Character commits to a new path
- `midpoint` - Character has a major revelation
- `fall` - Character experiences failure or setback
- `darknight` - Character reaches their lowest point
- `climax` - Character makes final push toward goal
- `resolution` - Character establishes a new equilibrium

## Example: Memory-Enhanced Generation

The `examples/memory_enhanced_generation.py` script demonstrates the memory enhancement system by:

1. Initializing character profiles with psychological attributes
2. Generating sequential character-focused scenes for multiple characters
3. Tracking character development across scenes
4. Maintaining narrative continuity elements
5. Displaying updated character states and narrative elements

Run the example:

```bash
python examples/memory_enhanced_generation.py
```

## Advanced Usage

### Memory Integration Levels

The memory system supports three levels of integration:

1. **Basic (Level 1)**: Minimal memory integration with basic character continuity
2. **Standard (Level 2)**: Incorporates character states, plot points, and themes
3. **Deep (Level 3)**: Full integration including emotional arcs, relationship dynamics, and thematic elements

```python
# Change memory integration level
playwright.memory_integration_level = 3  # Deep integration
```

### Character Development Analysis

Get detailed character development summaries:

```python
# Get character summary
char_summary = playwright.get_character_summary("character_id")

# Print current arc stage
print(f"Current Arc Stage: {char_summary['current_arc']['current_stage']}")

# Print emotional journey
for emotion in char_summary['emotional_journey']:
    print(f"Emotion: {emotion['emotion']} caused by {emotion['cause']}")

# Print relationship developments
for char, rel in char_summary['relationships'].items():
    print(f"Relationship with {char}: {rel['current_status']}")
    for change in rel['history']:
        print(f"  Changed to {change['status']} due to {change['change']}")
```

### Narrative Continuity Management

Access and manage narrative elements:

```python
# Get narrative continuity
continuity = memory.get_narrative_continuity()

# Get unresolved plot points
unresolved = continuity.get_unresolved_plot_points()

# Get pending foreshadowing elements
pending = continuity.get_pending_foreshadowing()

# Get character involvement in plot
character_plots = continuity.get_character_involvement("character_name")

# Get thematic development
theme_dev = continuity.get_theme_development("theme_name")

# Add a foreshadowing element
continuity.add_foreshadowing(
    "mysterious device on the desk",
    "will save everyone in the final scene",
    "scene_123"
)

# Update with its payoff later
continuity.update_foreshadowing_payoff(
    "mysterious device on the desk",
    "scene_456"
)
```

## Benefits of Memory Enhancements

1. **Consistency** - Characters maintain consistent traits, relationships, and arcs
2. **Natural Evolution** - Character development feels organic across scenes
3. **Narrative Coherence** - Plot threads and themes develop consistently
4. **Thematic Depth** - Themes can be woven throughout multiple scenes
5. **Narrative Planning** - Foreshadowing and setups pay off naturally

These memory enhancements transform Thespian from a scene-based generation system to a cohesive theatrical production framework capable of developing complex characters and narratives across complete plays.