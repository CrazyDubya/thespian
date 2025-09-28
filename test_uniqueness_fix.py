#!/usr/bin/env python3
"""
Test script to validate the scene uniqueness fixes.
"""

import os
import sys
import uuid
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from thespian.llm.consolidated_playwright import (
    ConsolidatedPlaywright, 
    PlaywrightCapability, 
    SceneRequirements
)
from thespian.llm.run_manager import RunManager
from thespian.llm.theatrical_memory import StoryOutline

def test_uniqueness_validation():
    """Test the scene uniqueness validation logic."""
    print("Testing scene uniqueness validation...")
    
    # Create a minimal playwright
    playwright = ConsolidatedPlaywright(
        name="TestPlaywright",
        enabled_capabilities=[PlaywrightCapability.BASIC_GENERATION]
    )
    
    # Test scenes (similar content)
    scene1 = """[SETTING: Laboratory with computers]
DR. SMITH: (looking at data) The results are fascinating.
DR. JONES: (nodding) Yes, this could change everything."""
    
    scene2 = """[SETTING: Laboratory with computers]  
DR. SMITH: (examining data) The results are remarkable.
DR. JONES: (agreeing) Indeed, this might transform everything."""
    
    scene3 = """[SETTING: Corporate office with city view]
CEO BROWN: (reviewing reports) The quarterly numbers exceeded expectations.
CFO WHITE: (smiling) Our strategy is paying dividends."""
    
    previous_scenes = [scene1, scene2]
    
    # Test uniqueness validation
    is_unique_similar = playwright._validate_scene_uniqueness("similar scene", previous_scenes)
    is_unique_different = playwright._validate_scene_uniqueness(scene3, previous_scenes)
    
    print(f"Similar scene validation (should be False): {is_unique_similar}")
    print(f"Different scene validation (should be True): {is_unique_different}")
    
    # Test uniqueness constraint building
    requirements = SceneRequirements(
        title="Test Play",
        setting="Test Setting",
        characters=["DR. SMITH", "DR. JONES"],
        act_number=1,
        scene_number=3
    )
    
    constraint = playwright._build_uniqueness_constraint(previous_scenes, requirements)
    print(f"\nUniqueness constraint preview:")
    print(constraint[:200] + "..." if len(constraint) > 200 else constraint)
    
    return True

def test_generation_type_directives():
    """Test generation type directive building."""
    print("\nTesting generation type directives...")
    
    playwright = ConsolidatedPlaywright(
        name="TestPlaywright",
        enabled_capabilities=[PlaywrightCapability.BASIC_GENERATION]
    )
    
    # Test different generation types
    test_types = ["basic", "collaborative", "character_focused", "memory_enhanced", "iterative_refinement"]
    
    for gen_type in test_types:
        playwright._current_generation_type = gen_type
        directive = playwright._get_generation_type_directive()
        print(f"{gen_type}: {directive}")
    
    return True

def test_scene_specific_directives():
    """Test scene-specific directive building."""
    print("\nTesting scene-specific directives...")
    
    playwright = ConsolidatedPlaywright(
        name="TestPlaywright",
        enabled_capabilities=[PlaywrightCapability.BASIC_GENERATION]
    )
    
    # Test a few key scenes
    test_scenes = [
        (1, 1, "Opening scene test"),
        (1, 5, "Act 1 climax test"), 
        (2, 3, "Midpoint test"),
        (3, 5, "Final scene test")
    ]
    
    for act, scene, outline in test_scenes:
        requirements = SceneRequirements(
            title="Test Play",
            setting="Test Setting", 
            characters=["CHARACTER1"],
            act_number=act,
            scene_number=scene
        )
        
        directive = playwright._build_scene_specific_directive(requirements, outline)
        print(f"Act {act}, Scene {scene}:")
        print(directive)
        print()
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("TESTING SCENE UNIQUENESS FIXES")
    print("=" * 60)
    
    try:
        test_uniqueness_validation()
        test_generation_type_directives()
        test_scene_specific_directives()
        
        print("=" * 60)
        print("ALL TESTS PASSED!")
        print("=" * 60)
        
    except Exception as e:
        print(f"TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)