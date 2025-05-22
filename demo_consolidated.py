#!/usr/bin/env python3

"""
Demonstration of the consolidated playwright module structure and capabilities.
"""

import sys
from pathlib import Path

# Add the project root to path
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import just the types we need to show
from thespian.llm.consolidated_playwright import Playwright, SceneRequirements, PlaywrightCapability

def main():
    """Run a demonstration of the consolidated playwright."""
    print("\n" + "="*80)
    print("DEMONSTRATION OF THE CONSOLIDATED PLAYWRIGHT MODULE")
    print("="*80)
    
    # Show the available capabilities
    print("\n[1] Available Playwright Capabilities:")
    for capability in PlaywrightCapability:
        print(f"  - {capability.name}: {capability.value}")
    
    # Show the SceneRequirements class
    print("\n[2] SceneRequirements Class Fields:")
    fields = SceneRequirements.__annotations__
    for field_name, field_type in fields.items():
        print(f"  - {field_name}: {field_type}")
    
    # Demonstrate how to create scene requirements
    print("\n[3] Example SceneRequirements Creation:")
    requirements = SceneRequirements(
        setting="A high-tech laboratory in Neo-Tokyo",
        characters=["DR. SARAH CHEN", "DR. JAMES TANAKA", "AI ASSISTANT"],
        props=["Holographic displays", "Quantum computers", "Neural interfaces"],
        lighting="Bright, clinical lighting with blue accents",
        sound="Ambient electronic hum with occasional beeps",
        style="Science fiction",
        period="Near future",
        target_audience="Adult"
    )
    print(f"  Created requirements with:")
    print(f"  - Setting: {requirements.setting}")
    print(f"  - Characters: {requirements.characters}")
    print(f"  - Style: {requirements.style}")
    print(f"  - Period: {requirements.period}")
    
    # Show Playwright class fields
    print("\n[4] Playwright Class Fields:")
    fields = {}
    for name in dir(Playwright):
        if name.startswith('_'):
            continue
        attr = getattr(Playwright, name)
        if not callable(attr):
            fields[name] = attr
    
    for field_name in sorted(fields.keys()):
        print(f"  - {field_name}")
    
    # Show the key methods available in the Playwright class
    print("\n[5] Key Playwright Methods:")
    methods = [
        "generate_scene", 
        "collaborate_on_scene", 
        "plan_act", 
        "create_story_outline",
        "get_character_summary",
        "get_all_characters",
        "create_scene_with_character_focus"
    ]
    
    for method_name in methods:
        if hasattr(Playwright, method_name):
            method = getattr(Playwright, method_name)
            if callable(method):
                print(f"  - {method_name}")
    
    # Show example usage of the consolidated playwright
    print("\n[6] Example Usage Pattern:")
    print("""
    # Initialize components
    llm_manager = LLMManager()
    memory = TheatricalMemory()
    quality_control = TheatricalQualityControl()
    advisor_manager = AdvisorManager(llm_manager, memory)
    
    # Create playwright using factory function with desired capabilities
    playwright = create_playwright(
        name="Production Playwright",
        llm_manager=llm_manager,
        memory=memory,
        capabilities=[
            PlaywrightCapability.BASIC,
            PlaywrightCapability.ITERATIVE_REFINEMENT,
            PlaywrightCapability.MEMORY_ENHANCEMENT,
            PlaywrightCapability.CHARACTER_TRACKING
        ],
        advisor_manager=advisor_manager,
        quality_control=quality_control,
        model_type="ollama"
    )
    
    # Generate a scene with memory-enhanced capabilities
    result = playwright.generate_scene(
        requirements=scene_requirements,
        progress_callback=lambda data: print(f"Progress: {data}")
    )
    """)
    
    # Show benefits of the consolidated approach
    print("\n[7] Benefits of the Consolidated Approach:")
    benefits = [
        "Single consistent API for all playwright functionality",
        "Modular capabilities that can be enabled/disabled as needed",
        "No need to choose between different playwright classes",
        "Improved code maintainability with composition over inheritance",
        "Easier extension with new capabilities",
        "Reduced code duplication",
        "Consistent parameter naming and method signatures"
    ]
    
    for i, benefit in enumerate(benefits, 1):
        print(f"  {i}. {benefit}")
    
    print("\n" + "="*80)
    print("DEMONSTRATION COMPLETED")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()