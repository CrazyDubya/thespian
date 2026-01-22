#!/usr/bin/env python3

"""
Simple demonstration of the consolidated playwright module.
"""

import sys
from pathlib import Path
import os
import json
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import uuid

# Add the project root to path
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import consolidated playwright
from thespian.llm.consolidated_playwright import (
    Playwright, 
    SceneRequirements, 
    PlaywrightCapability,
    CheckpointData
)

# Create a mock scene to demonstrate functionality
MOCK_SCENE = """ACT 1, SCENE 1: THE LABORATORY

[The scene opens in a high-tech laboratory with glowing holographic displays and softly humming equipment. DR. SARAH CHEN works intently at a terminal while DR. JAMES TANAKA reviews data on a floating screen. The AI ASSISTANT's voice comes from speakers throughout the room.]

DR. SARAH CHEN: (focused, typing rapidly) The quantum signature is unlike anything we've ever seen before. The entanglement patterns suggest a temporal component.

DR. JAMES TANAKA: (skeptical, adjusting glasses) That's theoretically impossible, Sarah. Quantum entanglement across time violates causality principles.

AI ASSISTANT: (neutral, analytical) Analysis complete, Doctor Chen. The data shows a 99.7% probability of temporal quantum correlation. This matches your hypothesis.

DR. SARAH CHEN: (excitedly) You see, James? The AI confirms it! We're looking at particles that appear to be entangled not just across space but across time itself.

DR. JAMES TANAKA: (moving to another display, concerned) If this gets into corporate hands before we understand the implications... there are serious ethical considerations.

[The lights briefly flicker. A low rumble is heard.]

AI ASSISTANT: (alert) Warning. Unexpected power fluctuation detected in the quantum containment field.

DR. SARAH CHEN: (alarmed) That shouldn't be possible with our safeguards! AI, run diagnostics immediately.

DR. JAMES TANAKA: (moving quickly to a control panel) I'm stabilizing the field. But look at these readings—the temporal signature is amplifying itself.

[The holographic displays flash with complex data patterns. The rumbling increases.]

DR. SARAH CHEN: (realizing) My god, James. It's not just that the particles are entangled across time. I think they're actually creating a feedback loop with their future states.

DR. JAMES TANAKA: (with dawning understanding) A temporal recursive entanglement? That would mean...

AI ASSISTANT: (urgent) Critical anomaly detected. Recommend immediate containment protocols.

[A bright flash of blue light erupts from the main quantum chamber, briefly engulfing the room, then subsiding.]

DR. SARAH CHEN: (shaken, looking at new data streaming in) The data... it's changing. I think we just witnessed the first documented case of quantum-temporal interaction.

DR. JAMES TANAKA: (solemn) We need to secure this lab immediately. And carefully consider what we do with this discovery.

AI ASSISTANT: (thoughtful) I am detecting patterns in the quantum flux that suggest deliberate organization. This may not be merely a natural phenomenon.

[The scientists exchange worried glances as the lights continue to flicker slightly.]

DR. SARAH CHEN: (quietly) What have we discovered?

[Blackout]

END OF SCENE"""

# Mock evaluation data
MOCK_EVALUATION = {
    "quality_score": 0.85,
    "quality_scores": {
        "dialogue_quality": 0.88,
        "narrative_coherence": 0.82,
        "character_consistency": 0.90,
        "stage_directions": 0.85,
        "thematic_relevance": 0.80
    },
    "feedback": "The scene effectively establishes the scientific premise and character dynamics.",
    "suggestions": [
        "Consider adding more technical details to enhance authenticity",
        "The emotional arc could be stronger between the scientists",
        "Add more visual descriptions of the quantum effects"
    ]
}

# Mock class instances to simulate LLM functionality
class MockPlaywright(Playwright):
    """Mock implementation of Playwright for demonstration."""

    def generate_scene(self, requirements, **kwargs):
        """Mock implementation that returns the hard-coded scene."""
        # Simulate progress callback if provided
        progress_callback = kwargs.get("progress_callback")
        if progress_callback:
            progress_callback({"phase": "initial_generation", "current_step": 1, "total_steps": 3, "message": "Generating initial scene draft"})
            progress_callback({"phase": "refinement", "current_step": 2, "total_steps": 3, "message": "Refining scene content"})
            progress_callback({"phase": "evaluation", "current_step": 3, "total_steps": 3, "message": "Evaluating final scene"})
        
        # Return a mock result
        return {
            "scene": MOCK_SCENE,
            "evaluation": MOCK_EVALUATION,
            "timing_metrics": {
                "initial_generation": 1.2,
                "refinement_iterations": 2,
                "expansion_ratio": 1.2,
                "total_time": 4.5
            },
            "iterations": 2,
            "iteration_metrics": [
                {"iteration_number": 1, "quality_scores": {"overall": 0.78}, "significant_changes": True, "advisor_dialogues": 2, "enhancement_time": 1.5},
                {"iteration_number": 2, "quality_scores": {"overall": 0.85}, "significant_changes": True, "advisor_dialogues": 1, "enhancement_time": 1.8}
            ],
            "scene_id": str(uuid.uuid4())
        }

def main():
    """Run simple demonstration."""
    console = Console()
    
    console.print(Panel.fit(
        "[bold]Thespian Framework: Consolidated Playwright Demo[/bold]",
        border_style="green"
    ))
    
    # Show available capabilities
    console.print("\n[bold]Available Playwright Capabilities:[/bold]")
    for capability in PlaywrightCapability:
        console.print(f"- {capability.name}: {capability.value}")
    
    # Create scene requirements
    console.print("\n[bold]Creating scene requirements...[/bold]")
    requirements = SceneRequirements(
        setting="A high-tech laboratory in Neo-Tokyo",
        characters=["DR. SARAH CHEN", "DR. JAMES TANAKA", "AI ASSISTANT"],
        props=["Holographic displays", "Quantum computer", "Neural interface terminals"],
        lighting="Bright, clinical lighting with blue accents",
        sound="Ambient electronic hum with occasional beeps",
        style="Science fiction",
        period="Near future",
        target_audience="Adult",
        act_number=1,
        scene_number=1
    )
    
    # Display scene requirements
    requirements_table = Table(title="Scene Requirements")
    requirements_table.add_column("Parameter", style="cyan")
    requirements_table.add_column("Value", style="green")
    
    # Use model_dump instead of dict for compatibility with Pydantic v2
    req_data = requirements.model_dump() if hasattr(requirements, "model_dump") else requirements.dict()
    for field, value in req_data.items():
        if isinstance(value, list):
            value_str = ", ".join(value)
        else:
            value_str = str(value) if value is not None else "None"
        requirements_table.add_row(field, value_str)
    
    console.print(requirements_table)
    
    # Create mock playwright with desired capabilities
    console.print("\n[bold]Creating mock playwright with capabilities...[/bold]")
    # We use the MockPlaywright to avoid actual LLM calls
    playwright = MockPlaywright(
        name="Demo Playwright",
        llm_manager=None,  # Mock, not used
        memory=None,  # Mock, not used
        advisor_manager=None,  # Mock, not used
        quality_control=None,  # Mock, not used
        model_type="mock",
        enabled_capabilities=[
            PlaywrightCapability.BASIC,
            PlaywrightCapability.ITERATIVE_REFINEMENT,
            PlaywrightCapability.COLLABORATIVE
        ]
    )
    
    # Display enabled capabilities
    console.print("Created playwright with capabilities:")
    for capability in playwright.enabled_capabilities:
        console.print(f"- {capability}")
    
    # Generate scene with progress tracking
    console.print("\n[bold]Simulating scene generation...[/bold]")
    progress_steps = []
    
    def progress_callback(data):
        progress_steps.append(data)
        console.print(f"  - {data.get('message', 'Progress update')}")
    
    # Generate scene
    result = playwright.generate_scene(
        requirements=requirements,
        progress_callback=progress_callback
    )
    
    # Display generated scene
    console.print("\n[bold]Generated Scene (sample):[/bold]")
    # Just show first few lines to avoid cluttering the console
    scene_lines = result["scene"].split("\n")
    sample_scene = "\n".join(scene_lines[:10] + ["...", "(scene truncated for display)"])
    console.print(Panel(sample_scene, title="Scene Sample"))
    
    # Display evaluation
    console.print("\n[bold]Scene Evaluation:[/bold]")
    evaluation_table = Table(show_header=True, header_style="bold magenta")
    evaluation_table.add_column("Aspect")
    evaluation_table.add_column("Score")
    
    scores = result["evaluation"]["quality_scores"]
    for aspect, score in scores.items():
        evaluation_table.add_row(aspect.replace("_", " ").title(), f"{score:.2f}")
    
    # Add overall score
    evaluation_table.add_row("Overall Quality", f"{result['evaluation']['quality_score']:.2f}")
    console.print(evaluation_table)
    
    # Display suggestions
    console.print("\n[bold]Improvement Suggestions:[/bold]")
    for suggestion in result["evaluation"]["suggestions"]:
        console.print(f"- {suggestion}")
    
    # Display timing metrics
    console.print("\n[bold]Timing Metrics:[/bold]")
    timing_table = Table(show_header=True, header_style="bold magenta")
    timing_table.add_column("Stage")
    timing_table.add_column("Time (seconds)")
    
    for stage, time_taken in result["timing_metrics"].items():
        if isinstance(time_taken, (int, float)):
            timing_table.add_row(stage.replace("_", " ").title(), f"{time_taken:.2f}")
    
    console.print(timing_table)
    
    # Save the full scene to a file
    output_file = Path("demo_scene.txt")
    with open(output_file, "w") as f:
        f.write(result["scene"])
    
    console.print(f"\nFull scene saved to: [bold]{output_file}[/bold]")
    console.print("\n[bold green]Demo completed successfully![/bold green]")
    console.print("[bold]✅ The consolidated_playwright module imports are working correctly[/bold]")

if __name__ == "__main__":
    main()