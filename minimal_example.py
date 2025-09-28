"""
Minimal example to test the consolidated playwright module.
"""

import sys
import os
from pathlib import Path

# Add the project root to path if not already there
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import only what we need for a minimal test
from thespian.llm.consolidated_playwright import Playwright, SceneRequirements, PlaywrightCapability

def main():
    """Run minimal example."""
    print("Testing imports for consolidated_playwright module")
    
    # Just verify we have the right imports
    print(f"Successfully imported Playwright class: {Playwright.__name__}")
    print(f"Successfully imported SceneRequirements class: {SceneRequirements.__name__}")
    print(f"Successfully imported PlaywrightCapability enum: {PlaywrightCapability.__name__}")
    
    # Print available capabilities
    print("\nAvailable capabilities:")
    for capability in PlaywrightCapability:
        print(f"- {capability.name}: {capability.value}")
    
    # Test creating SceneRequirements
    requirements = SceneRequirements(
        setting="A test setting",
        characters=["Character 1", "Character 2"],
        props=["Prop 1", "Prop 2"],
        lighting="Test lighting",
        sound="Test sound",
        style="Test style",
        period="Test period",
        target_audience="Test audience"
    )
    
    print(f"\nSuccessfully created SceneRequirements instance:")
    print(f"- Setting: {requirements.setting}")
    print(f"- Characters: {requirements.characters}")
    print(f"- Style: {requirements.style}")
    
    print("Example completed successfully!")

if __name__ == "__main__":
    main()