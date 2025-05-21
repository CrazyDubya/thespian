# Advanced Story Structure User Guide

This guide explains how to use the advanced story structure system in the Thespian framework to create complex, engaging theatrical productions with sophisticated narrative structures.

## Table of Contents

1. [Introduction](#introduction)
2. [Core Components](#core-components)
3. [Usage Scenarios](#usage-scenarios)
4. [Getting Started](#getting-started)
5. [API Reference](#api-reference)
6. [Advanced Features](#advanced-features)
7. [Integration with Memory System](#integration-with-memory-system)
8. [Examples](#examples)
9. [Troubleshooting](#troubleshooting)

## Introduction

The Advanced Story Structure System enhances the Thespian framework with sophisticated narrative structure capabilities that go beyond the conventional three-act format. It enables:

- Complex narrative structures like non-linear or parallel storytelling
- Various act structure patterns from the 3-act structure to the Hero's Journey
- Detailed story beat tracking and management
- Plot thread and subplot coordination
- Strategic plot reversals and twists

## Core Components

The system consists of three main components:

1. **AdvancedStoryPlanner**: The central class that defines and manages complex narrative structures.
2. **DynamicScenePlanner**: Creates scene requirements based on narrative position and structure.
3. **StructureEnhancedPlaywright**: Integrates the structure system with scene generation.

## Usage Scenarios

The advanced story structure system can be used in several ways:

### 1. Standalone Structure Planning

Use the `AdvancedStoryPlanner` to design a narrative structure without immediately generating content:

```python
from thespian.llm.advanced_story_structure import (
    AdvancedStoryPlanner, 
    NarrativeStructureType,
    ActStructureType
)

# Create a non-linear story with hero's journey structure
planner = AdvancedStoryPlanner(
    structure_type=NarrativeStructureType.NON_LINEAR,
    act_structure=ActStructureType.HERO_JOURNEY,
    num_acts=3,
    narrative_complexity="complex"
)

# Add plot threads, subplots, and reversals
# ...

# Analyze the structure
beats = planner.story_beats
next_beat = planner.get_next_incomplete_beat()
```

### 2. Structure-Aware Scene Generation

Use the `StructureEnhancedPlaywright` to generate scenes that incorporate structural elements:

```python
from thespian.llm.advanced_story_structure import StructureEnhancedPlaywright

# Initialize components
# ...

playwright = StructureEnhancedPlaywright(
    memory=memory,
    story_planner=story_planner,
    scene_planner=scene_planner,
    llm_invoke_func=llm.invoke
)

# Generate a structured scene
scene = playwright.generate_structured_scene(
    act_number=1,
    scene_number=2,
    additional_requirements={"setting": "castle", "tone": "mysterious"}
)
```

### 3. Combined with Memory and Refinement Systems

Use all enhanced systems together for maximum impact:

```python
from thespian.llm.advanced_story_structure import AdvancedStoryPlanner
from thespian.llm.enhanced_memory import EnhancedTheatricalMemory
from thespian.llm.iterative_refinement import refine_scene_iteratively

# Initialize systems
# ...

# Generate a scene with structure awareness
scene = playwright.generate_structured_scene(act_number=1, scene_number=2)

# Refine the scene with iterative enhancement
refined_scene = refine_scene_iteratively(
    scene_content=scene["content"],
    context={"narrative_position": 0.2, "current_beat": "Call to Adventure"},
    llm_invoke_func=llm.invoke,
    iterations=3
)

# Update memory with the refined scene
memory.update_narrative_from_scene(scene["scene_id"], refined_scene, llm.invoke)
```

## Getting Started

To start using the advanced story structure system:

1. **Import the necessary components**:

```python
from thespian.llm.advanced_story_structure import (
    AdvancedStoryPlanner, 
    DynamicScenePlanner, 
    StructureEnhancedPlaywright,
    NarrativeStructureType,
    ActStructureType, 
    NarrativeComplexityLevel,
    PlotThread,
    SubplotDefinition,
    PlotReversal
)
```

2. **Choose a narrative structure and act structure**:

```python
story_planner = AdvancedStoryPlanner(
    structure_type=NarrativeStructureType.NESTED,  # Choose from available types
    act_structure=ActStructureType.THREE_ACT,      # Choose from available patterns
    num_acts=3,
    narrative_complexity=NarrativeComplexityLevel.COMPLEX
)
```

3. **Define plot threads and subplots**:

```python
main_thread = PlotThread(
    name="Main Quest",
    description="Hero's journey to save the kingdom",
    importance=1.0,
    character_focus=["protagonist", "antagonist"],
    arc_points=[
        {"position": 0.1, "description": "Quest begins"},
        {"position": 0.5, "description": "Major challenge"},
        {"position": 0.9, "description": "Final confrontation"}
    ]
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
```

4. **Add plot reversals**:

```python
reversal = PlotReversal(
    description="The mentor is revealed to be the true antagonist",
    target_position=0.7,
    affected_threads=["Main Quest"],
    impact="Forces protagonist to continue alone",
    foreshadowing=["Mentor's strange behavior", "Inconsistent advice"]
)
story_planner.add_plot_reversal(reversal)
```

5. **Create scene planner and enhanced playwright**:

```python
scene_planner = DynamicScenePlanner(
    story_planner=story_planner,
    memory=memory,
    total_acts=3,
    scenes_per_act={1: 3, 2: 4, 3: 3}
)

playwright = StructureEnhancedPlaywright(
    memory=memory,
    story_planner=story_planner,
    scene_planner=scene_planner,
    llm_invoke_func=llm.invoke
)
```

6. **Generate scenes with structure awareness**:

```python
for act in range(1, 4):
    for scene in range(1, scenes_per_act[act] + 1):
        scene_data = playwright.generate_structured_scene(
            act_number=act,
            scene_number=scene,
            additional_requirements={
                "setting": f"Act {act} setting",
                "tone": "appropriate tone for this position"
            }
        )
        
        # Process the generated scene
        print(f"Generated scene with beat: {scene_data['current_beat']}")
```

## API Reference

### AdvancedStoryPlanner

#### Constructor Parameters

- `structure_type` (NarrativeStructureType): Type of narrative structure (linear, non-linear, parallel, etc.)
- `act_structure` (ActStructureType): Type of act structure (3-act, 5-act, hero's journey, etc.)
- `num_acts` (int): Number of acts in the story (1-7)
- `narrative_complexity` (NarrativeComplexityLevel): Complexity level of the narrative

#### Key Methods

- `add_plot_thread(thread)`: Add a plot thread to the story
- `add_subplot(subplot)`: Add a subplot to the story
- `add_plot_reversal(reversal)`: Add a plot reversal/twist
- `get_story_beat_by_position(position, tolerance=0.05)`: Get story beat at a specific position
- `get_next_incomplete_beat()`: Get the next story beat that hasn't been completed
- `update_story_beat(beat_name, scene_id, complete=True)`: Mark a story beat as completed
- `calculate_narrative_position(act, scene, total_acts, scenes_per_act)`: Calculate position in the narrative
- `get_necessary_story_elements(position)`: Get story elements needed at a specific position

### DynamicScenePlanner

#### Constructor Parameters

- `story_planner` (AdvancedStoryPlanner): The story planner to use
- `memory` (EnhancedTheatricalMemory): Memory system for tracking narrative elements
- `total_acts` (int): Total number of acts
- `scenes_per_act` (Dict[int, int]): Number of scenes per act

#### Key Methods

- `create_scene_requirements(act_number, scene_number)`: Create requirements for a scene
- `handle_scene_completion(scene_id, scene_content, act_number, scene_number)`: Process a completed scene
- `get_narrative_requirements_for_llm(act_number, scene_number)`: Generate formatted requirements for an LLM prompt

### StructureEnhancedPlaywright

#### Constructor Parameters

- `memory` (EnhancedTheatricalMemory): Memory system for character and narrative tracking
- `story_planner` (AdvancedStoryPlanner): Story planner for structure management
- `scene_planner` (DynamicScenePlanner): Scene planner for requirements
- `llm_invoke_func` (callable): Function to invoke the LLM for text generation

#### Key Methods

- `generate_structured_scene(act_number, scene_number, additional_requirements=None)`: Generate a scene with structure awareness

## Advanced Features

### Narrative Structure Types

The system supports multiple narrative structure types:

- **Linear**: Traditional sequential storytelling
- **Non-Linear**: Scenes presented out of chronological order
- **Parallel**: Multiple storylines running concurrently
- **Nested**: Stories within stories
- **Circular**: Ending connects back to beginning
- **Fragmented**: Disconnected scenes that form a coherent whole
- **Episodic**: Semi-independent episodes with loose connections
- **Frame**: Story framed within another story

### Act Structure Patterns

Various act structures are supported:

- **3-Act Structure**: Classic setup, confrontation, resolution
- **5-Act Structure**: Exposition, rising action, climax, falling action, denouement
- **Hero's Journey**: Campbell's monomyth pattern with 12 stages
- **Freytag's Pyramid**: Exposition, rising action, climax, falling action, denouement
- **Kishōtenketsu**: 4-part Japanese structure (introduction, development, twist, conclusion)
- **7-Point Structure**: Hook, plot turn 1, pinch 1, midpoint, pinch 2, plot turn 2, resolution
- **Sequence Method**: 8 sequences of approximately equal length

## Integration with Memory System

The advanced structure system integrates seamlessly with the enhanced memory system:

1. The `DynamicScenePlanner` uses memory information to create context-aware scene requirements
2. The `StructureEnhancedPlaywright` updates memory with structural elements from generated scenes
3. Characters can develop along their arcs according to the plot structure

Example integration:

```python
# After generating a scene
scene = playwright.generate_structured_scene(act_number=2, scene_number=3)

# Update narrative and character memory
memory.update_narrative_from_scene(scene["scene_id"], scene["content"], llm.invoke)

# Update character memory
for char_id in memory.character_profiles:
    memory.update_character_from_scene(char_id, scene["scene_id"], scene["content"], llm.invoke)
```

## Examples

### Example 1: Creating a Non-Linear Mystery Story

See `examples/advanced_story_structure_demo.py` for a complete demonstration of:
- Creating a non-linear narrative structure
- Defining plot threads and subplots
- Adding plot reversals
- Generating scenes with structure awareness

### Example 2: Combined Enhancement System

See `examples/combined_enhancements_example.py` for a demonstration of using:
- Advanced story structure
- Enhanced memory system
- Iterative refinement

## Troubleshooting

### Common Issues

1. **Story beats not properly aligning with scenes**:
   - Check the `scenes_per_act` configuration to ensure proper narrative position calculation
   - Adjust the tolerance parameter when retrieving story beats

2. **Plot reversals not triggering**:
   - Verify the target position is calculated correctly
   - Use `get_necessary_story_elements` to confirm the reversal is pending

3. **Subplots not integrating properly**:
   - Check the integration_points values
   - Ensure the subplot is properly linked to relevant characters

### Getting Help

For additional help, check:
- The examples directory for reference implementations
- The advanced structure README (`ADVANCED_STRUCTURE_README.md`)
- The main enhancement documentation (`ENHANCEMENTS_MASTER_README.md`)