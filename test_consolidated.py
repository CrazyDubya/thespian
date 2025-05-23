#!/usr/bin/env python3

"""
Simple test script to verify that the consolidated playwright module works correctly.
"""

import sys
from pathlib import Path

# Add the project root to sys.path
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from thespian.llm import LLMManager
from thespian.llm.consolidated_playwright import Playwright, SceneRequirements, PlaywrightCapability, create_playwright
from thespian.llm.theatrical_memory import TheatricalMemory
from thespian.llm.theatrical_advisors import AdvisorManager
from thespian.llm.quality_control import TheatricalQualityControl

def main():
    """Test that we can create a playwright instance."""
    print("Testing consolidated playwright module...")
    
    # Initialize components
    llm_manager = LLMManager()
    memory = TheatricalMemory()
    advisor_manager = AdvisorManager(llm_manager, memory)
    quality_control = TheatricalQualityControl()
    
    # Create playwright using factory function
    playwright = create_playwright(
        name="Test Playwright",
        llm_manager=llm_manager,
        memory=memory,
        capabilities=[
            PlaywrightCapability.BASIC,
            PlaywrightCapability.ITERATIVE_REFINEMENT
        ],
        advisor_manager=advisor_manager,
        quality_control=quality_control,
    )
    
    # Verify playwright capabilities
    print(f"Playwright name: {playwright.name}")
    print(f"Enabled capabilities: {playwright.enabled_capabilities}")
    
    # Verify that we can create scene requirements
    requirements = SceneRequirements(
        setting="A futuristic cityscape",
        characters=["Protagonist", "Antagonist"],
        props=["Holographic display", "Neural interface"],
        lighting="Neon-lit ambiance",
        sound="Ambient electronic tones",
        style="Cyberpunk",
        period="Future",
        target_audience="Young adults"
    )
    
    print(f"Created scene requirements for {requirements.style} scene")
    print("Test completed successfully!")

if __name__ == "__main__":
    main()