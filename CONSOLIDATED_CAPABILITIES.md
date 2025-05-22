# Consolidated Playwright Module: Complete Feature Guide

This document provides a comprehensive overview of the consolidated playwright module and how it integrates all the capabilities that were previously spread across multiple implementations.

## Core Design Principles

The consolidated playwright module follows these key design principles:

1. **Composition over Inheritance**: Rather than using inheritance for different playwright types, the consolidated approach uses a capabilities-based composition model where features can be enabled or disabled.

2. **Factory Pattern**: The `create_playwright()` function provides a clean factory interface to create playwrights with specific capabilities.

3. **Memory-Enhanced by Default**: The enhanced memory system is integrated directly, with varying levels of integration (basic, standard, deep).

4. **Advisor-Driven Feedback**: Theatrical advisors provide specialized feedback for different aspects of the production.

5. **Modular Components**: All components (memory, advisors, quality control) are modular and can be customized independently.

## Capability Model

The consolidated playwright uses an enum-based capability model instead of inheritance hierarchies:

```python
class PlaywrightCapability(str, Enum):
    """Capabilities that can be enabled in the playwright."""
    BASIC = "basic"
    ITERATIVE_REFINEMENT = "iterative_refinement"
    MEMORY_ENHANCEMENT = "memory_enhancement"
    NARRATIVE_STRUCTURE = "narrative_structure"
    CHARACTER_TRACKING = "character_tracking"
    COLLABORATIVE = "collaborative"
```

Capabilities are enabled at initialization:

```python
playwright = create_playwright(
    name="Production Playwright",
    llm_manager=llm_manager,
    memory=memory,
    capabilities=[
        PlaywrightCapability.BASIC,
        PlaywrightCapability.ITERATIVE_REFINEMENT,
        PlaywrightCapability.MEMORY_ENHANCEMENT
    ],
    advisor_manager=advisor_manager,
    quality_control=quality_control
)
```

## Key Features

### 1. Scene Generation

The core scene generation functionality is enhanced with all capabilities while maintaining backward compatibility:

```python
# Basic scene generation
scene = playwright.generate_scene(
    requirements=SceneRequirements(...),
    previous_scene=None,
    previous_feedback=None,
    progress_callback=lambda data: print(f"Progress: {data}")
)
```

### 2. Iterative Refinement

When enabled, scenes go through multiple iterations of refinement with advisor feedback:

```python
# Generation with iterative refinement
playwright.refinement_max_iterations = 5  # Configure max iterations
playwright.refinement_quality_threshold = 0.85  # Configure quality threshold
playwright.refinement_improvement_threshold = 0.02  # Configure required improvement

scene = playwright.generate_scene(requirements=scene_requirements)
# Returns: Scene with refinement metrics and iterations tracked
```

### 3. Memory Enhancement

Memory enhancement integrates character development and narrative continuity:

```python
# Memory provides context for scenes
memory_context = playwright._get_memory_context(act_number=1, scene_number=3)
# Returns: Character states, unresolved plots, thematic status

# Requirements are automatically enhanced with memory context
enhanced_requirements = playwright._enhance_requirements_with_memory(requirements)
# Returns: Requirements with memory-enhanced generation directives
```

### 4. Character Tracking

Character tracking provides detailed analysis of character development:

```python
# Get character summary
character_summary = playwright.get_character_summary("protagonist")

# Get scene-specific character information
scene_character_info = playwright.get_scene_character_summary(scene_id)

# Create character-focused scene
scene = playwright.create_scene_with_character_focus(
    requirements=requirements,
    focus_character="protagonist",
    character_development={
        "aspect": "emotional",
        "moment_type": "revelation",
        "emotional_journey": "From certainty to doubt"
    }
)
```

### 5. Collaborative Mode

Multiple playwrights can collaborate on scene generation:

```python
# Collaborative scene generation
scene = main_playwright.collaborate_on_scene(
    other_playwright=dialogue_playwright,
    requirements=requirements
)
# Returns: Scene with collaboration data and contributions from both playwrights
```

### 6. Act Planning

The consolidated playwright includes comprehensive act planning with advisor input:

```python
# Plan an act with all advisors
act_plan = playwright.plan_act(act_number=1)
# Returns: Complete act plan with advisor discussions and committed outline
```

### 7. Theatrical Advisors

The advisor system provides specialized feedback:

```python
# Available advisor types:
# - Narrative: Plot structure and continuity
# - Dialogue: Speech patterns and conversation flow
# - Character: Character development and consistency
# - Scenic: Visual elements and staging
# - Pacing: Scene rhythm and tension
# - Thematic: Theme development and symbolism

# Get consolidated feedback
feedback = advisor_manager.get_consolidated_feedback(
    content=scene_content,
    context={"act_number": 1, "scene_number": 3}
)
```

## Using the Factory Function

The recommended way to create playwrights is through the factory function:

```python
# Create playwright with memory enhancement
playwright = create_playwright(
    name="Memory-Enhanced Playwright",
    llm_manager=llm_manager,
    memory=memory,
    capabilities=[
        PlaywrightCapability.BASIC,
        PlaywrightCapability.MEMORY_ENHANCEMENT
    ],
    model_type="ollama"
)

# Create playwright with all capabilities
playwright = create_playwright(
    name="Full-Featured Playwright",
    llm_manager=llm_manager,
    memory=memory,
    capabilities=[
        PlaywrightCapability.BASIC,
        PlaywrightCapability.ITERATIVE_REFINEMENT,
        PlaywrightCapability.MEMORY_ENHANCEMENT,
        PlaywrightCapability.CHARACTER_TRACKING,
        PlaywrightCapability.NARRATIVE_STRUCTURE,
        PlaywrightCapability.COLLABORATIVE
    ],
    advisor_manager=advisor_manager,
    quality_control=quality_control
)
```

## Complete Production Flow

A complete production flow using the consolidated playwright:

1. **Initialization**: Create playwright with desired capabilities
2. **Story Setup**: Create story outline and character profiles
3. **Act Planning**: Plan each act with advisor input
4. **Scene Generation**: Generate scenes for each act with specialized approaches
   - Basic scenes
   - Character-focused scenes
   - Memory-enhanced scenes
   - Collaborative scenes
   - Iteratively refined scenes
5. **Analysis**: Generate reports on character development, plot progression
6. **Output**: Consolidate scenes into a complete script

## Benefits Over Previous Implementations

The consolidated playwright provides several advantages:

1. **Reduced Code Duplication**: All functionality in a single module
2. **More Flexible Configuration**: Enable only the capabilities you need
3. **Easier Maintenance**: Single code path for core functionality
4. **Better Performance**: Shared optimizations benefit all usage patterns
5. **Simplified API**: Consistent interface regardless of capability configuration
6. **Enhanced Composition**: Mix and match capabilities without inheritance constraints

## Migration Guide

To migrate from previous playwright implementations to the consolidated version:

1. Replace imports from individual playwright modules to the consolidated module:
   ```python
   # Old
   from thespian.llm.playwright import Playwright
   from thespian.llm.enhanced_playwright import EnhancedPlaywright
   from thespian.llm.memory_enhanced_playwright import MemoryEnhancedPlaywright
   
   # New
   from thespian.llm.consolidated_playwright import Playwright, create_playwright, PlaywrightCapability
   ```

2. Replace direct instance creation with the factory function:
   ```python
   # Old
   playwright = EnhancedPlaywright(name="EnhancedPlaywright", llm_manager=llm_manager, memory=memory)
   
   # New
   playwright = create_playwright(
       name="EnhancedPlaywright",
       llm_manager=llm_manager,
       memory=memory,
       capabilities=[PlaywrightCapability.BASIC, PlaywrightCapability.ITERATIVE_REFINEMENT]
   )
   ```

3. Update method calls for consistency (all previous methods are supported)