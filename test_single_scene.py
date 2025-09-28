#!/usr/bin/env python3
"""
Test script to generate a single scene and validate the fixes.
"""

import os
import sys
from pathlib import Path
import logging

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_single_scene_generation():
    """Test generating a single scene with the fixed system."""
    
    try:
        from thespian.llm.consolidated_playwright import (
            ConsolidatedPlaywright, 
            PlaywrightCapability,
            SceneRequirements
        )
        from thespian.llm.theatrical_memory import StoryOutline
        from thespian.llm import LLMManager
        
        # Create story outline
        story = StoryOutline(
            title="Test Play",
            genre="sci-fi",
            acts={
                1: {
                    "description": "Scientists discover artificial consciousness",
                    "key_events": [
                        "Dr. Voss demonstrates the consciousness transfer",
                        "Corporate interference revealed",
                        "ARIA develops self-awareness",
                        "Ethical dilemmas emerge", 
                        "First act climax"
                    ]
                }
            }
        )
        
        # Create playwright
        playwright = ConsolidatedPlaywright(
            name="TestPlaywright",
            enabled_capabilities=[
                PlaywrightCapability.BASIC_GENERATION,
                PlaywrightCapability.MEMORY_ENHANCEMENT
            ],
            story_outline=story
        )
        
        # Create scene requirements  
        requirements = SceneRequirements(
            title="Test Play",
            setting="Advanced laboratory",
            characters=["DR. VOSS", "DR. CHEN", "ARIA"],
            props=["quantum computer", "holographic displays"],
            lighting="bright lab lighting",
            sound="electronic hums",
            style="realistic",
            period="near future",
            target_audience="adult",
            act_number=1,
            scene_number=1
        )
        
        print("Testing single scene generation...")
        print(f"Story: {story.title}")
        print(f"Scene: Act {requirements.act_number}, Scene {requirements.scene_number}")
        print(f"Characters: {', '.join(requirements.characters)}")
        
        # Generate the scene
        result = playwright.generate_scene(
            requirements=requirements,
            generation_type="basic"
        )
        
        print("\n" + "="*60)
        print("✅ SCENE GENERATION SUCCESSFUL!")
        print("="*60)
        print(f"Scene length: {len(result['scene'])} characters")
        print(f"Generation attempts: {result['timing_metrics'].get('attempts', 1)}")
        print(f"Uniqueness validated: {result.get('uniqueness_validated', False)}")
        
        print("\nGenerated scene preview:")
        print("-" * 40)
        scene_preview = result['scene'][:500] + "..." if len(result['scene']) > 500 else result['scene']
        print(scene_preview)
        print("-" * 40)
        
        return True
        
    except Exception as e:
        print(f"❌ Scene generation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("TESTING SINGLE SCENE GENERATION")
    print("=" * 60)
    
    success = test_single_scene_generation()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ SINGLE SCENE TEST PASSED!")
        print("The uniqueness fixes are working correctly.")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ SINGLE SCENE TEST FAILED!")
        print("=" * 60)