#!/usr/bin/env python3
"""
Minimal working example of using the Thespian framework.
This uses only the methods and classes that actually exist in the codebase.
"""

import os
import sys
from pathlib import Path

# Add thespian to path
sys.path.insert(0, str(Path(__file__).parent))

from thespian.llm.manager import LLMManager
from thespian.llm.consolidated_playwright import (
    Playwright, 
    SceneRequirements, 
    PlaywrightCapability, 
    create_playwright
)
from thespian.llm.theatrical_memory import TheatricalMemory, CharacterProfile, StoryOutline
from thespian.llm.theatrical_advisors import AdvisorManager
from thespian.llm.quality_control import TheatricalQualityControl


def main():
    print("=== Thespian Minimal Working Example ===\n")
    
    # Step 1: Initialize core components
    print("1. Initializing core components...")
    llm_manager = LLMManager()
    memory = TheatricalMemory()
    
    # Step 2: Create a simple story outline
    print("2. Creating story outline...")
    story_outline = StoryOutline(
        title="A Simple Test Play",
        acts=[
            {
                "act_number": 1,
                "description": "The setup - introducing our characters",
                "key_events": [
                    "Character introductions",
                    "Setting the scene",
                    "Initial conflict",
                    "Rising tension",
                    "Cliffhanger"
                ],
                "status": "draft"
            }
        ]
    )
    
    # Step 3: Create character profiles
    print("3. Creating character profiles...")
    character_profile = CharacterProfile(
        id="protagonist",
        name="Alex",
        background="A curious scientist",
        motivations=["Discover truth", "Help others"],
        relationships={"Assistant": "Colleague"},
        development_arc=[
            {
                "stage": "initial",
                "description": "Eager but naive researcher"
            }
        ]
    )
    
    # Update memory with character
    memory.update_character_profile("protagonist", character_profile)
    
    # Step 4: Create playwright with basic capabilities
    print("4. Creating playwright...")
    playwright = Playwright(
        name="TestPlaywright",
        llm_manager=llm_manager,
        memory=memory,
        enabled_capabilities=[PlaywrightCapability.BASIC],
        model_type="ollama"
    )
    
    # Set the story outline
    playwright.story_outline = story_outline
    
    # Step 5: Create scene requirements
    print("5. Creating scene requirements...")
    requirements = SceneRequirements(
        setting="A modern research laboratory",
        characters=["ALEX", "ASSISTANT"],
        props=["Computer terminals", "Lab equipment"],
        lighting="Bright fluorescent lighting",
        sound="Humming of equipment",
        style="Contemporary drama",
        period="Present day",
        target_audience="General audience",
        act_number=1,
        scene_number=1
    )
    
    # Step 6: Generate a scene
    print("6. Generating scene...")
    print("(This may take a moment...)\n")
    
    try:
        result = playwright.generate_scene(requirements)
        
        print("=== Generated Scene ===")
        print(result["scene"])
        print("\n=== Scene Evaluation ===")
        for metric, score in result["evaluation"].items():
            print(f"{metric}: {score:.2f}")
            
    except Exception as e:
        print(f"Error generating scene: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure Ollama is running (ollama serve)")
        print("2. Make sure you have a model installed (ollama pull llama2)")
        print("3. Check the error message above for specific issues")


if __name__ == "__main__":
    main()