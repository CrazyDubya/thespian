"""
Compare the baseline and enhanced playwright implementations.
"""

import os
import sys
import logging
from pathlib import Path
import time
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.markdown import Markdown
from rich.text import Text

# Add the project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from thespian.llm import LLMManager
from thespian.llm.playwright import EnhancedPlaywright as BasePlaywright, SceneRequirements
from thespian.llm.enhanced_playwright import EnhancedPlaywright
from thespian.llm.theatrical_memory import TheatricalMemory, CharacterProfile, StoryOutline
from thespian.llm.theatrical_advisors import AdvisorManager
from thespian.llm.quality_control import TheatricalQualityControl

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def progress_callback(progress_data):
    """Callback to update progress during generation."""
    logger.info(f"Progress: {progress_data}")

def main():
    console = Console()
    
    console.print(Panel.fit(
        "This script compares the baseline playwright with the enhanced version that includes iterative refinement.",
        title="Playwright Comparison"
    ))
    
    # Initialize shared components
    console.print("[bold]Initializing components...[/bold]")
    llm_manager = LLMManager()
    memory = TheatricalMemory()
    advisor_manager = AdvisorManager(llm_manager, memory)
    quality_control = TheatricalQualityControl()
    
    # Create story outline
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
    
    # Create scene requirements (same for both versions)
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
        scene_number=1
    )
    
    # Create both playwright versions
    console.print("[bold]Creating baseline and enhanced playwrights...[/bold]")
    baseline_playwright = BasePlaywright(
        name="Baseline Playwright",
        llm_manager=llm_manager,
        memory=memory,
        advisor_manager=advisor_manager,
        quality_control=quality_control,
        model_type="ollama"
    )
    baseline_playwright.story_outline = story_outline
    
    enhanced_playwright = EnhancedPlaywright(
        name="Enhanced Playwright",
        llm_manager=llm_manager,
        memory=memory,
        advisor_manager=advisor_manager,
        quality_control=quality_control,
        model_type="ollama",
        refinement_max_iterations=3,
        target_scene_length=4000
    )
    enhanced_playwright.story_outline = story_outline
    
    # Generate scenes with both versions
    results = {}
    
    # Setup progress tracking
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}[/bold blue]"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        # Generate with baseline playwright
        console.print("\n[bold]Generating scene with baseline playwright...[/bold]")
        baseline_task = progress.add_task("[cyan]Generating baseline scene...", total=100)
        
        start_time = time.time()
        baseline_result = baseline_playwright.generate_scene(
            requirements=requirements
        )
        baseline_time = time.time() - start_time
        
        progress.update(baseline_task, completed=100)
        results["baseline"] = baseline_result
        results["baseline"]["generation_time"] = baseline_time
        
        # Generate with enhanced playwright
        console.print("\n[bold]Generating scene with enhanced playwright...[/bold]")
        enhanced_task = progress.add_task("[cyan]Generating enhanced scene...", total=100)
        
        def ui_progress_callback(data):
            """Update the UI progress bar."""
            progress_callback(data)
            
            # Update progress description
            message = data.get("message", "Processing...")
            description = f"[cyan]{message}[/cyan]"
            progress.update(enhanced_task, description=description)
            
            # Update progress percentage
            if "current_step" in data and "total_steps" in data:
                percentage = (data["current_step"] / data["total_steps"]) * 100
                progress.update(enhanced_task, completed=percentage)
            elif "phase" in data:
                # Rough phase-based progress if steps not available
                phases = ["initial_generation", "expansion", "refinement"]
                if data["phase"] in phases:
                    phase_idx = phases.index(data["phase"])
                    percentage = ((phase_idx + 1) / len(phases)) * 100
                    progress.update(enhanced_task, completed=percentage)
        
        start_time = time.time()
        enhanced_result = enhanced_playwright.generate_scene(
            requirements=requirements,
            progress_callback=ui_progress_callback
        )
        enhanced_time = time.time() - start_time
        
        progress.update(enhanced_task, completed=100)
        results["enhanced"] = enhanced_result
        results["enhanced"]["generation_time"] = enhanced_time
    
    # Display comparison results
    console.print("\n[bold]Comparison Results:[/bold]")
    
    # Compare metrics
    metrics_table = Table(show_header=True, header_style="bold magenta", title="Metrics Comparison")
    metrics_table.add_column("Metric")
    metrics_table.add_column("Baseline")
    metrics_table.add_column("Enhanced")
    metrics_table.add_column("Difference")
    
    # Scene length
    baseline_length = len(results["baseline"]["scene"])
    enhanced_length = len(results["enhanced"]["scene"])
    length_diff = enhanced_length - baseline_length
    length_diff_pct = (length_diff / baseline_length) * 100 if baseline_length > 0 else 0
    
    metrics_table.add_row(
        "Scene Length (chars)",
        str(baseline_length),
        str(enhanced_length),
        f"{length_diff:+d} ({length_diff_pct:+.1f}%)"
    )
    
    # Generation time
    baseline_time = results["baseline"]["generation_time"]
    enhanced_time = results["enhanced"]["generation_time"]
    time_diff = enhanced_time - baseline_time
    time_diff_pct = (time_diff / baseline_time) * 100 if baseline_time > 0 else 0
    
    metrics_table.add_row(
        "Generation Time (s)",
        f"{baseline_time:.2f}",
        f"{enhanced_time:.2f}",
        f"{time_diff:+.2f} ({time_diff_pct:+.1f}%)"
    )
    
    # Quality metrics
    baseline_scores = {k: v for k, v in results["baseline"]["evaluation"].items() if isinstance(v, (int, float))}
    enhanced_scores = {k: v for k, v in results["enhanced"]["evaluation"].items() if isinstance(v, (int, float))}
    
    # Overall quality
    baseline_quality = sum(baseline_scores.values()) / len(baseline_scores) if baseline_scores else 0
    enhanced_quality = sum(enhanced_scores.values()) / len(enhanced_scores) if enhanced_scores else 0
    quality_diff = enhanced_quality - baseline_quality
    quality_diff_pct = (quality_diff / baseline_quality) * 100 if baseline_quality > 0 else 0
    
    metrics_table.add_row(
        "Overall Quality",
        f"{baseline_quality:.2f}",
        f"{enhanced_quality:.2f}",
        f"{quality_diff:+.2f} ({quality_diff_pct:+.1f}%)"
    )
    
    # Iterations
    baseline_iterations = 1  # Baseline only does one pass
    enhanced_iterations = results["enhanced"].get("iterations", 1)
    
    metrics_table.add_row(
        "Iterations",
        str(baseline_iterations),
        str(enhanced_iterations),
        f"{enhanced_iterations - baseline_iterations:+d}"
    )
    
    console.print(metrics_table)
    
    # Quality breakdown
    quality_table = Table(show_header=True, header_style="bold magenta", title="Quality Metrics Breakdown")
    quality_table.add_column("Aspect")
    quality_table.add_column("Baseline")
    quality_table.add_column("Enhanced")
    quality_table.add_column("Improvement")
    
    # Get all unique keys
    all_aspects = set(baseline_scores.keys()) | set(enhanced_scores.keys())
    
    for aspect in sorted(all_aspects):
        baseline_score = baseline_scores.get(aspect, 0)
        enhanced_score = enhanced_scores.get(aspect, 0)
        diff = enhanced_score - baseline_score
        diff_pct = (diff / baseline_score) * 100 if baseline_score > 0 else 0
        
        # Format the aspect name for display
        display_aspect = aspect.replace("_", " ").title()
        
        quality_table.add_row(
            display_aspect,
            f"{baseline_score:.2f}",
            f"{enhanced_score:.2f}",
            f"{diff:+.2f} ({diff_pct:+.1f}%)"
        )
    
    console.print(quality_table)
    
    # Save both scenes to files
    baseline_file = Path("./baseline_scene_output.txt")
    with open(baseline_file, "w") as f:
        f.write(results["baseline"]["scene"])
    
    enhanced_file = Path("./enhanced_scene_output.txt")
    with open(enhanced_file, "w") as f:
        f.write(results["enhanced"]["scene"])
    
    console.print(f"\nBaseline scene saved to: [bold]{baseline_file}[/bold]")
    console.print(f"Enhanced scene saved to: [bold]{enhanced_file}[/bold]")
    
    # Display scene previews
    console.print("\n[bold]Scene Previews:[/bold]")
    
    console.print(Panel.fit(
        results["baseline"]["scene"][:500] + "...",
        title="Baseline Scene (First 500 chars)",
        width=80
    ))
    
    console.print(Panel.fit(
        results["enhanced"]["scene"][:500] + "...",
        title="Enhanced Scene (First 500 chars)",
        width=80
    ))
    
    console.print("\n[bold]Conclusion:[/bold]")
    if enhanced_quality > baseline_quality:
        console.print("✅ The enhanced playwright produced higher quality content.")
    else:
        console.print("❌ The baseline playwright produced higher quality content.")
        
    if enhanced_length > baseline_length:
        console.print("✅ The enhanced playwright produced more detailed content.")
    else:
        console.print("❌ The baseline playwright produced more detailed content.")
        
    console.print(f"⏱️ The enhanced version took {time_diff:.2f}s longer ({time_diff_pct:.1f}% increase in generation time).")

if __name__ == "__main__":
    main()