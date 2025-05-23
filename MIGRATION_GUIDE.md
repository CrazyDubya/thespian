# Migration Guide: Consolidated Playwright Module

This document explains how to migrate from the older playwright modules (playwright.py, enhanced_playwright.py, memory_enhanced_playwright.py) to the new consolidated module.

## Overview

The Thespian framework has consolidated its playwright implementations into a single module with modular capabilities. This provides several advantages:

- **Simplified API**: A single `Playwright` class with capabilities that can be enabled/disabled
- **Consistent behavior**: All capabilities work together seamlessly
- **Easier maintenance**: Code is organized in a more modular way
- **Future extensibility**: New capabilities can be added without creating new classes

## Key Changes

### 1. Class Naming

- Old: `EnhancedPlaywright`, `MemoryEnhancedPlaywright`
- New: `Playwright` with `PlaywrightCapability` enum

### 2. Imports

Replace:
```python
from thespian.llm.playwright import EnhancedPlaywright, SceneRequirements
# or
from thespian.llm.enhanced_playwright import EnhancedPlaywright
# or
from thespian.llm.memory_enhanced_playwright import MemoryEnhancedPlaywright
```

With:
```python
from thespian.llm.consolidated_playwright import Playwright, SceneRequirements, PlaywrightCapability, create_playwright
```

### 3. Capability Selection

The new system uses capability flags to enable/disable features:

```python
# Create with specific capabilities
playwright = Playwright(
    name="My Playwright",
    llm_manager=llm_manager,
    memory=memory,
    quality_control=quality_control,
    enabled_capabilities=[
        PlaywrightCapability.BASIC,            # Basic functionality (required)
        PlaywrightCapability.ITERATIVE_REFINEMENT,  # Enhanced playwright features
        PlaywrightCapability.MEMORY_ENHANCEMENT,    # Memory enhancement features
        PlaywrightCapability.CHARACTER_TRACKING,    # Character tracking features
        # Other available capabilities:
        # PlaywrightCapability.NARRATIVE_STRUCTURE
        # PlaywrightCapability.COLLABORATIVE
    ]
)
```

### 4. Factory Function

For convenience, a factory function is provided:

```python
playwright = create_playwright(
    name="My Playwright",
    llm_manager=llm_manager,
    memory=memory,
    capabilities=[PlaywrightCapability.BASIC, PlaywrightCapability.ITERATIVE_REFINEMENT],
    # Additional parameters...
)
```

### 5. Parameter Changes

- `enhanced_memory` parameter is no longer needed - the system automatically converts `memory` to an enhanced version when required
- `model_type` replaces `llm_model_type` for consistency
- `checkpoint_manager` is now directly accepted instead of `checkpoint_dir`

## Examples

### Basic Playwright

```python
playwright = create_playwright(
    name="Basic Playwright",
    llm_manager=llm_manager,
    memory=memory,
    capabilities=[PlaywrightCapability.BASIC]
)
```

### Enhanced (Iterative) Playwright

```python
playwright = create_playwright(
    name="Enhanced Playwright",
    llm_manager=llm_manager,
    memory=memory,
    capabilities=[
        PlaywrightCapability.BASIC,
        PlaywrightCapability.ITERATIVE_REFINEMENT
    ],
    refinement_max_iterations=3,
    target_scene_length=4000
)
```

### Memory-Enhanced Playwright

```python
playwright = create_playwright(
    name="Memory-Enhanced Playwright",
    llm_manager=llm_manager,
    memory=memory,  # Can be EnhancedTheatricalMemory or standard TheatricalMemory
    capabilities=[
        PlaywrightCapability.BASIC,
        PlaywrightCapability.MEMORY_ENHANCEMENT,
        PlaywrightCapability.CHARACTER_TRACKING
    ],
    memory_integration_level=2  # 1=basic, 2=standard, 3=deep
)
```

### Fully-Featured Playwright

```python
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
    ]
)
```

## Additional Notes

- The `SceneRequirements` class remains unchanged
- Method signatures remain largely the same for compatibility
- Special methods from specific implementations are now available based on enabled capabilities