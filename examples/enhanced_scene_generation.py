"""
Example of enhanced scene generation with iterative refinement.
"""

import os
import sys
import logging
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.table import Table
from rich.markdown import Markdown

# Add the project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from thespian.llm import LLMManager
from thespian.llm.enhanced_playwright import EnhancedPlaywright, SceneRequirements
from thespian.llm.theatrical_memory import TheatricalMemory, CharacterProfile, StoryOutline
from thespian.llm.theatrical_advisors import AdvisorManager
from thespian.llm.quality_control import TheatricalQualityControl

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def progress_callback(progress_data):
    """Callback to update progress during generation."""
    logger.info(f"Progress: {progress_data}")
    # In a real application, this would update a progress bar or other UI element

def main():
    console = Console()
    
    # Initialize components
    console.print("[bold]Initializing components...[/bold]")
    llm_manager = LLMManager()
    memory = TheatricalMemory()
    advisor_manager = AdvisorManager(llm_manager, memory)
    quality_control = TheatricalQualityControl()
    
    # Create enhanced playwright
    console.print("[bold]Creating enhanced playwright...[/bold]")
    playwright = EnhancedPlaywright(
        name="Enhanced Playwright",
        llm_manager=llm_manager,
        memory=memory,
        advisor_manager=advisor_manager,
        quality_control=quality_control,
        model_type="ollama",  # Using local Ollama model
        refinement_max_iterations=3,  # Limit to 3 iterations for demo
        target_scene_length=4000  # Target a medium-length scene
    )
    
    # Initialize story outline
    console.print("[bold]Initializing story outline...[/bold]")
    story_outline = StoryOutline(
        title="The Quantum Paradox",
        acts=[{
            "act_number": 1,
            "description": "The discovery of quantum entanglement in the lab",
            "key_events": [
                "Dr. Chen and Dr. Tanaka make breakthrough discovery",
                "AI Assistant helps analyze the data",
                "Initial experiment shows unexpected results",
                "Corporate executives learn of the discovery",
                "Team decides to keep developing in secret"
            ],
            "status": "draft"
        }]
    )
    
    # Set story outline for playwright
    playwright.story_outline = story_outline
    
    # Create scene requirements
    requirements = SceneRequirements(
        setting="A high-tech laboratory in Neo-Tokyo",
        characters=["DR. SARAH CHEN", "DR. JAMES TANAKA", "AI ASSISTANT", "LAB TECHNICIAN"],
        props=["Holographic displays", "Quantum computer", "Neural interface terminals", "Coffee mugs"],
        lighting="Bright, clinical lighting with blue accents",
        sound="Ambient electronic hum with occasional beeps",
        style="Science fiction",
        period="2089",
        target_audience="Young adults",
        act_number=1,
        scene_number=1,
        premise="Dr. Chen and Dr. Tanaka discover quantum entanglement across time, leading to ethical dilemmas and corporate interest",
        pacing="Medium",
        tone="Suspenseful, thoughtful",
        emotional_arc="From excitement to concern to determination",
        key_conflict="The conflict between scientific discovery and potential misuse"
    )
    
    # Display production information
    console.print(
        Panel.fit(
            "[bold]The Quantum Paradox[/bold]\n"
            f"Setting: {requirements.setting}\n"
            f"Style: {requirements.style}\n"
            f"Period: {requirements.period}\n"
            f"Characters: {', '.join(requirements.characters)}\n"
            f"Premise: {requirements.premise}",
            title="Production Information",
        )
    )
    
    # Generate scene with progress tracking
    console.print("\n[bold]Generating enhanced scene with iterative refinement...[/bold]")
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}[/bold blue]"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]Generating scene...", total=100)
        
        def ui_progress_callback(data):
            """Update the UI progress bar."""
            progress_callback(data)  # Also log the progress
            
            # Update progress description
            message = data.get("message", "Processing...")
            phase = data.get("phase", "")
            description = f"[cyan]{message}[/cyan]"
            progress.update(task, description=description)
            
            # Update progress percentage
            if "current_step" in data and "total_steps" in data:
                percentage = (data["current_step"] / data["total_steps"]) * 100
                progress.update(task, completed=percentage)
        
        # Generate the scene with enhanced process
        result = playwright.generate_scene(
            requirements=requirements,
            progress_callback=ui_progress_callback
        )
    
    # Display results
    console.print("\n[bold]Generation Complete![/bold]")
    
    # Display metrics
    console.print("\n[bold]Generation Metrics:[/bold]")
    metrics_table = Table(show_header=True, header_style="bold magenta")
    metrics_table.add_column("Metric")
    metrics_table.add_column("Value")
    
    metrics_table.add_row("Initial Generation Time", f"{result['timing_metrics'].get('initial_generation', 0):.2f}s")
    metrics_table.add_row("Expansion Ratio", f"{result['timing_metrics'].get('expansion', 1.0):.2f}x")
    metrics_table.add_row("Refinement Iterations", str(result.get('iterations', 0)))
    metrics_table.add_row("Quality Improvement", f"{result.get('quality_improvement', 0):.2f}")
    metrics_table.add_row("Total Scene Length", str(len(result['scene'])))
    
    console.print(metrics_table)
    
    # Display quality evaluation
    console.print("\n[bold]Quality Evaluation:[/bold]")
    evaluation_table = Table(show_header=True, header_style="bold magenta")
    evaluation_table.add_column("Aspect")
    evaluation_table.add_column("Score")
    
    for aspect, score in result['evaluation'].items():
        if isinstance(score, (int, float)):
            evaluation_table.add_row(aspect.replace("_", " ").title(), f"{score:.2f}")
    
    console.print(evaluation_table)
    
    # Display the scene
    console.print("\n[bold]Generated Scene:[/bold]")
    scene_panel = Panel(
        result['scene'][:1000] + "...\n[See full scene in file]",  # Truncated for display
        title="Scene Content (Preview)",
        expand=False
    )
    console.print(scene_panel)
    
    # Save the scene to a file
    output_file = Path("./enhanced_scene_output.txt")
    with open(output_file, "w") as f:
        f.write(result['scene'])
    
    console.print(f"\nFull scene saved to: [bold]{output_file}[/bold]")
    
    # If refinement occurred, show iteration data
    if result.get('iterations', 0) > 1 and result.get('iteration_metrics'):
        console.print("\n[bold]Refinement Iterations:[/bold]")
        iterations_table = Table(show_header=True, header_style="bold magenta")
        iterations_table.add_column("Iteration")
        iterations_table.add_column("Quality")
        iterations_table.add_column("Improvement")
        iterations_table.add_column("Focus Areas")
        
        for i, metrics in enumerate(result['iteration_metrics']):
            iteration_num = metrics.get("iteration_number", i+1)
            quality = sum(metrics.get("quality_scores", {}).values()) / len(metrics.get("quality_scores", {})) if metrics.get("quality_scores") else 0
            improvement = metrics.get("overall_improvement", 0)
            focus_areas = ", ".join(metrics.get("focus_areas", []))
            
            iterations_table.add_row(
                str(iteration_num),
                f"{quality:.2f}",
                f"{improvement:.2f}",
                focus_areas
            )
        
        console.print(iterations_table)

if __name__ == "__main__":
    main()