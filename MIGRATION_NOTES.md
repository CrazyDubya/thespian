# Migration to Consolidated Playwright Module

This document outlines the changes made to migrate from the older separate playwright modules to the new consolidated approach.

## Files Updated

1. **Main Example Files**
   - `/examples/simple_production.py`
   - `/examples/full_play_production.py`
   - `/examples/memory_enhanced_generation.py` (was already updated)

2. **Tests**
   - `/tests/unit/test_dialogue_system.py`
   - `/tests/unit/test_playwright_agent.py`
   - `/tests/unit/test_playwrights.py` (was already updated)

3. **Core Files**
   - Added deprecation notice to `StructureEnhancedPlaywright` in `/thespian/llm/advanced_story_structure.py`
   - `/thespian/cli.py` (was already updated)
   - `/thespian/tui/app.py` (was already updated)

## Migration Strategy

The migration followed these key principles:

1. **Import Changes**
   - Updated imports from:
     ```python
     from thespian.llm.playwright import EnhancedPlaywright, SceneRequirements
     ```
     to:
     ```python
     from thespian.llm.consolidated_playwright import Playwright, SceneRequirements, PlaywrightCapability, create_playwright
     ```

2. **Object Creation**
   - Changed from direct instantiation:
     ```python
     playwright = EnhancedPlaywright(
         name="Playwright Name",
         llm_manager=llm_manager,
         memory=memory,
         # other parameters...
     )
     ```
     to using the factory function with capability specification:
     ```python
     playwright = create_playwright(
         name="Playwright Name",
         llm_manager=llm_manager,
         memory=memory,
         capabilities=[
             PlaywrightCapability.BASIC,
             PlaywrightCapability.ITERATIVE_REFINEMENT,
             # other capabilities as needed...
         ],
         # other parameters...
     )
     ```

3. **Type Annotations**
   - Updated type annotations from `EnhancedPlaywright` to `Playwright`

## Backward Compatibility

The consolidated approach maintains backward compatibility by:

1. Preserving all functionality from previous implementations through the capability system
2. Maintaining the same parameter names and method signatures where possible
3. Accepting the same types of input and producing the same types of output

## Future Development

Going forward, new features should be added directly to the consolidated playwright module as new capabilities rather than creating separate playwright classes.