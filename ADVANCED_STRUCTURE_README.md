# Advanced Story Structure System

This enhancement adds sophisticated narrative structure capabilities to the Thespian framework, enabling the creation of more complex and varied narrative patterns beyond the standard three-act format.

## Overview

The Advanced Story Structure System builds on the existing memory enhancements to create more cohesive and sophisticated narratives with varied structural patterns like non-linear, parallel, or nested story structures. It provides tools for defining and managing complex narrative configurations, ensuring that generated scenes align with the chosen structure while maintaining narrative continuity.

## Key Components

### 1. AdvancedStoryPlanner

The central class for planning and structuring complex narratives with features including:

- Support for multiple narrative structures (linear, non-linear, parallel, nested, etc.)
- Various act structure patterns (3-act, 5-act, hero's journey, etc.)
- Story beat tracking and management
- Plot thread and subplot coordination
- Plot reversal and twist management
- Structural element mapping (scene sequence, time jumps, etc.)

```python
story_planner = AdvancedStoryPlanner(
    structure_type=NarrativeStructureType.NON_LINEAR,
    act_structure=ActStructureType.THREE_ACT,
    num_acts=3,
    narrative_complexity=NarrativeComplexityLevel.COMPLEX
)
```

### 2. DynamicScenePlanner

A scene planner that adapts to the evolving needs of the story, creating scene requirements based on:

- Current position in the narrative
- Story beats that need to be fulfilled
- Active plot threads and subplots
- Pending plot reversals or twists
- Character and narrative continuity from past scenes

```python
scene_planner = DynamicScenePlanner(
    story_planner=story_planner,
    memory=memory,
    total_acts=3,
    scenes_per_act={1: 3, 2: 4, 3: 3}
)
```

### 3. StructureEnhancedPlaywright

A specialized playwright that integrates the advanced story structure system with scene generation:

- Incorporates structural requirements into scene generation
- Maintains narrative consistency across complex structures
- Tracks story beat fulfillment
- Updates memory and continuity based on generated scenes

```python
playwright = StructureEnhancedPlaywright(
    memory=memory,
    story_planner=story_planner,
    scene_planner=scene_planner,
    llm_invoke_func=llm.invoke
)
```

## Supported Narrative Structures

The system supports various narrative structures including:

- **Linear**: Traditional sequential storytelling
- **Non-Linear**: Scenes presented out of chronological order
- **Parallel**: Multiple storylines running concurrently
- **Nested**: Stories within stories
- **Circular**: Ending connects back to beginning
- **Fragmented**: Disconnected scenes that form a coherent whole
- **Episodic**: Semi-independent episodes with loose connections
- **Frame**: Story framed within another story

## Supported Act Structures

Various act structures are supported:

- **3-Act Structure**: Classic setup, confrontation, resolution
- **5-Act Structure**: Exposition, rising action, climax, falling action, denouement
- **Hero's Journey**: Campbell's monomyth pattern
- **Freytag's Pyramid**: Exposition, rising action, climax, falling action, denouement
- **Kishōtenketsu**: 4-part Japanese structure (introduction, development, twist, conclusion)
- **7-Point Structure**: Hook, plot turn 1, pinch 1, midpoint, pinch 2, plot turn 2, resolution
- **Sequence Method**: 8 sequences of approximately equal length

## Usage Example

```python
# Initialize components
memory = EnhancedTheatricalMemory()
story_planner = AdvancedStoryPlanner(
    structure_type=NarrativeStructureType.PARALLEL,
    act_structure=ActStructureType.THREE_ACT,
    num_acts=3,
    narrative_complexity=NarrativeComplexityLevel.COMPLEX
)

# Add narrative elements
main_thread = PlotThread(
    name="Main Quest",
    description="Hero's journey to save the kingdom",
    importance=1.0,
    character_focus=["protagonist"]
)
story_planner.add_plot_thread(main_thread)

subplot = SubplotDefinition(
    name="Political Intrigue",
    description="Power struggles in the court",
    characters=["advisor", "queen"],
    arc_type="rise-fall",
    integration_points=[0.2, 0.5, 0.8],
    resolution_target=0.9
)
story_planner.add_subplot(subplot)

# Create scene planner
scene_planner = DynamicScenePlanner(
    story_planner=story_planner,
    memory=memory
)

# Create enhanced playwright
playwright = StructureEnhancedPlaywright(
    memory=memory,
    story_planner=story_planner,
    scene_planner=scene_planner,
    llm_invoke_func=llm.invoke
)

# Generate a scene
scene = playwright.generate_structured_scene(
    act_number=1,
    scene_number=2,
    additional_requirements={
        "setting": "Royal court",
        "tone": "Tense and suspenseful"
    }
)
```

## Integration with Memory System

The advanced structure system integrates with the enhanced memory system to:

1. Track character development across complex narrative patterns
2. Maintain consistent character psychology even with non-linear scene presentation
3. Ensure foreshadowing and payoffs connect appropriately
4. Preserve thematic continuity across parallel storylines
5. Update memory with narrative structure-specific information

## Benefits

- **More Sophisticated Narratives**: Create complex narrative structures that go beyond simple linear storytelling
- **Better Narrative Cohesion**: Ensure that complex narratives remain coherent and satisfying
- **Structural Flexibility**: Choose from multiple narrative and act structures to match your creative vision
- **Improved Character Development**: Character arcs unfold naturally even in complex narrative patterns
- **Enhanced Theme Development**: Themes can be explored across different narrative threads

## Demo

See `examples/advanced_story_structure_demo.py` for a complete working example of the advanced story structure system in action.