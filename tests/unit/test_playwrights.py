"""
Test script for enhanced playwright collaboration with advisor integration.
"""

import os
from thespian.llm import LLMManager
from thespian.llm.playwright import EnhancedPlaywright, SceneRequirements, StoryOutline
from thespian.llm.theatrical_memory import CharacterProfile, TheatricalMemory
from thespian.llm.theatrical_advisors import AdvisorManager
from thespian.llm.quality_control import TheatricalQualityControl
from thespian.llm.dialogue_system import DialogueSystem
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from typing import Dict, Any, List
import uuid
from pathlib import Path

console = Console()


def test_enhanced_playwright_collaboration():
    """Test collaboration between enhanced playwrights with advisor integration."""

    # Initialize LLM manager
    llm_manager = LLMManager()

    # Initialize shared components
    memory = TheatricalMemory()
    quality_control = TheatricalQualityControl()

    # Create enhanced playwrights
    ollama_playwright = EnhancedPlaywright(
        name="Ollama",
        llm_manager=llm_manager,
        memory=memory,
        quality_control=quality_control,
        model_type="ollama",
    )

    grok_playwright = EnhancedPlaywright(
        name="Grok",
        llm_manager=llm_manager,
        memory=memory,
        quality_control=quality_control,
        model_type="grok",
    )

    # Initialize story outline
    story_outline = StoryOutline(
        title="The Writer's Journey",
        acts=[
            {
                "act_number": 1,
                "description": "The beginning of John's journey as a writer",
                "key_events": [
                    "John meets Sarah at the coffee shop",
                    "They discuss his manuscript",
                    "Sarah offers to help edit",
                    "John struggles with self-doubt",
                    "They agree to work together"
                ],
                "status": "committed",
                "act_id": str(uuid.uuid4()),
                "version": "1.0"
            }
        ],
        planning_status="committed",
        version="1.0"
    )

    # Set story outline for both playwrights
    ollama_playwright.story_outline = story_outline
    grok_playwright.story_outline = story_outline

    # Initialize character profiles
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("[cyan]Initializing character profiles...", total=3)

        character_profiles = {
            "protagonist": CharacterProfile(
                id="protagonist",
                name="John",
                background="A struggling writer",
                motivations=["Finish his novel", "Find success", "Prove himself"],
                relationships={"Sarah": "Love interest", "Mike": "Best friend"},
                development_arc=[
                    {
                        "stage": "initial",
                        "description": "Struggling with self-doubt and writer's block",
                    }
                ],
            ),
            "antagonist": CharacterProfile(
                id="antagonist",
                name="Sarah",
                background="Successful editor",
                motivations=["Advance her career", "Maintain high standards", "Find balance"],
                relationships={"John": "Love interest", "Editor": "Mentor"},
                development_arc=[
                    {
                        "stage": "initial",
                        "description": "Balancing professional ambition with personal life",
                    }
                ],
            ),
        }

        # Store character profiles
        for char_id, profile in character_profiles.items():
            ollama_playwright.update_character_profile(char_id, profile)
            grok_playwright.update_character_profile(char_id, profile)
            progress.update(task, advance=1)

    console.print(
        Panel.fit(
            "[bold blue]Enhanced Playwright Collaboration Test[/bold blue]\n\n"
            f"Playwrights:\n"
            f"- {ollama_playwright.name} (using {ollama_playwright.model_type})\n"
            f"- {grok_playwright.name} (using {grok_playwright.model_type})",
            title="Thespian Playwrights",
            border_style="blue",
        )
    )

    # Test scene requirements
    scene_requirements = SceneRequirements(
        setting="A cozy coffee shop in downtown",
        characters=["protagonist", "antagonist"],
        props=["Laptop", "Coffee cups", "Notebook"],
        lighting="Warm, intimate lighting",
        sound="Soft jazz music, coffee machine sounds",
        style="Naturalistic",
        period="Modern day",
        target_audience="Young adults",
        act_number=1,
        scene_number=1
    )

    # Test individual scene generation with advisor feedback
    console.print("\n[bold yellow]Testing Individual Scene Generation with Advisors[/bold yellow]")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        # Ollama scene generation
        task1 = progress.add_task("[green]Generating Ollama scene...", total=100)

        def ollama_progress_callback(current: int, total: int):
            status = (
                "Generating initial scene"
                if current == 1
                else (
                    "Getting advisor feedback"
                    if current == 2
                    else "Enhancing scene" if current == 3 else "Final evaluation"
                )
            )
            progress.update(
                task1,
                completed=int((current / total) * 100),
                description=f"[green]Ollama: {status}",
            )

        ollama_result = ollama_playwright.generate_scene(
            scene_requirements, progress_callback=ollama_progress_callback
        )
        progress.update(task1, completed=100, description="[green]Ollama: Complete")

        # Grok scene generation
        task2 = progress.add_task("[blue]Generating Grok scene...", total=100)

        def grok_progress_callback(current: int, total: int):
            status = (
                "Generating initial scene"
                if current == 1
                else (
                    "Getting advisor feedback"
                    if current == 2
                    else "Enhancing scene" if current == 3 else "Final evaluation"
                )
            )
            progress.update(
                task2, completed=int((current / total) * 100), description=f"[blue]Grok: {status}"
            )

        grok_result = grok_playwright.generate_scene(
            scene_requirements, progress_callback=grok_progress_callback
        )
        progress.update(task2, completed=100, description="[blue]Grok: Complete")

    # Display individual scenes with advisor feedback
    console.print("\n[bold cyan]Ollama's Scene:[/bold cyan]")
    console.print(Panel(ollama_result["scene"], border_style="green"))
    console.print("\n[bold cyan]Advisor Feedback:[/bold cyan]")
    console.print(Markdown(str(ollama_result["evaluation"])))

    # Display iteration metrics
    console.print("\n[bold cyan]Ollama's Iteration Metrics:[/bold cyan]")
    for metric in ollama_result["iteration_metrics"]:
        console.print(
            Panel(
                f"Iteration {metric['iteration_number']}\n"
                f"Quality Scores: {metric['quality_scores']}\n"
                f"Significant Changes: {metric['significant_changes']}\n"
                f"Advisor Dialogues: {metric['advisor_dialogues']}\n"
                f"Enhancement Time: {metric['enhancement_time']:.2f}s",
                title=f"Iteration {metric['iteration_number']}",
                border_style="cyan",
            )
        )

    # Display timing metrics
    timing_table = Table(title="Ollama Scene Generation Timing")
    timing_table.add_column("Stage", style="cyan")
    timing_table.add_column("Time (s)", style="green")
    for stage, time_taken in ollama_result["timing_metrics"].items():
        timing_table.add_row(stage.replace("_", " ").title(), f"{time_taken:.2f}")
    console.print(timing_table)

    console.print("\n[bold cyan]Grok's Scene:[/bold cyan]")
    console.print(Panel(grok_result["scene"], border_style="blue"))
    console.print("\n[bold cyan]Advisor Feedback:[/bold cyan]")
    console.print(Markdown(str(grok_result["evaluation"])))

    # Display iteration metrics
    console.print("\n[bold cyan]Grok's Iteration Metrics:[/bold cyan]")
    for metric in grok_result["iteration_metrics"]:
        console.print(
            Panel(
                f"Iteration {metric['iteration_number']}\n"
                f"Quality Scores: {metric['quality_scores']}\n"
                f"Significant Changes: {metric['significant_changes']}\n"
                f"Advisor Dialogues: {metric['advisor_dialogues']}\n"
                f"Enhancement Time: {metric['enhancement_time']:.2f}s",
                title=f"Iteration {metric['iteration_number']}",
                border_style="cyan",
            )
        )

    # Display timing metrics
    timing_table = Table(title="Grok Scene Generation Timing")
    timing_table.add_column("Stage", style="cyan")
    timing_table.add_column("Time (s)", style="green")
    for stage, time_taken in grok_result["timing_metrics"].items():
        timing_table.add_row(stage.replace("_", " ").title(), f"{time_taken:.2f}")
    console.print(timing_table)

    # Test collaborative scene writing with advisor integration
    console.print("\n[bold yellow]Testing Collaborative Scene Writing with Advisors[/bold yellow]")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("[yellow]Generating collaborative scene...", total=100)

        def collaborative_progress_callback(current: int, total: int):
            status = (
                "Ollama generating opening"
                if current == 1
                else "Getting opening feedback" if current == 2 else "Grok enhancing scene"
            )
            progress.update(
                task, completed=int((current / total) * 100), description=f"[yellow]{status}"
            )

        # First playwright generates opening
        collaborative_result = ollama_playwright.collaborate_on_scene(
            grok_playwright, scene_requirements, progress_callback=collaborative_progress_callback
        )
        progress.update(task, completed=100, description="[yellow]Collaborative: Complete")

    # Display collaborative scene with advisor feedback
    console.print("\n[bold cyan]Collaborative Scene:[/bold cyan]")
    console.print(Panel(collaborative_result["scene"], border_style="yellow"))
    console.print("\n[bold cyan]Advisor Feedback:[/bold cyan]")
    console.print(Markdown(str(collaborative_result["evaluation"])))

    # Display quality metrics
    console.print("\n[bold yellow]Quality Metrics Summary[/bold yellow]")

    metrics_table = Table(show_header=True, header_style="bold magenta")
    metrics_table.add_column("Metric")
    metrics_table.add_column("Ollama")
    metrics_table.add_column("Grok")
    metrics_table.add_column("Collaborative")

    ollama_metrics = ollama_result["evaluation"]
    grok_metrics = grok_result["evaluation"]
    collaborative_metrics = collaborative_result["evaluation"]

    for metric in ollama_metrics.keys():
        metrics_table.add_row(
            metric,
            f"{ollama_metrics[metric]['score']:.2f}",
            f"{grok_metrics[metric]['score']:.2f}",
            f"{collaborative_metrics[metric]['score']:.2f}",
        )

    console.print(metrics_table)

    # Verify all results contain required fields
    for result in [ollama_result, grok_result, collaborative_result]:
        assert "scene" in result
        assert "evaluation" in result
        assert "timing_metrics" in result
        assert "dialogue_history" in result
        assert "iteration_metrics" in result
        assert isinstance(result["iteration_metrics"], list)

        # Verify iteration metrics structure
        for metric in result["iteration_metrics"]:
            assert "iteration_number" in metric
            assert "quality_scores" in metric
            assert "significant_changes" in metric
            assert "advisor_dialogues" in metric
            assert "enhancement_time" in metric

    console.print("\n[bold green]Test completed successfully![/bold green]")


def test_checkpoint_functionality():
    """Test the checkpoint functionality of EnhancedPlaywright."""
    console = Console()

    # Initialize components
    llm_manager = LLMManager()
    memory = TheatricalMemory()
    quality_control = TheatricalQualityControl()

    # Create playwright
    playwright = EnhancedPlaywright(
        name="Checkpoint Test",
        llm_manager=llm_manager,
        memory=memory,
        quality_control=quality_control,
        model_type="ollama",
    )

    # Define scene requirements
    requirements = SceneRequirements(
        setting="A Victorian-era drawing room",
        characters=["Lady Eleanor", "Professor Blackwood"],
        props=["antique clock", "tea set"],
        lighting="dim gas lamps",
        sound="distant thunder",
        style="Gothic Mystery",
        period="Victorian",
        target_audience="Adult",
    )

    # Generate a scene ID for testing
    scene_id = str(uuid.uuid4())
    console.print(
        f"\n[bold blue]Testing checkpoint functionality with scene ID: {scene_id}[/bold blue]"
    )

    # Start scene generation
    with Progress() as progress:
        task = progress.add_task("[cyan]Generating scene...", total=playwright.max_iterations + 1)

        # First attempt - will be interrupted
        try:
            result1 = playwright.generate_scene(
                requirements,
                scene_id=scene_id,
                progress_callback=lambda current, total: progress.update(task, completed=current),
            )
        except KeyboardInterrupt:
            console.print(
                "[yellow]Scene generation interrupted - simulating checkpoint save[/yellow]"
            )

        # Verify checkpoint was created
        checkpoint_path = Path(playwright.checkpoint_dir) / f"{scene_id}.pkl.gz"
        assert checkpoint_path.exists(), "Checkpoint file was not created"

        # Second attempt - should resume from checkpoint
        console.print("\n[bold green]Resuming from checkpoint...[/bold green]")
        result2 = playwright.generate_scene(
            requirements,
            scene_id=scene_id,
            progress_callback=lambda current, total: progress.update(task, completed=current),
        )

        # Verify results
        assert "scene" in result2, "Resumed scene generation did not produce a scene"
        assert "evaluation" in result2, "Resumed scene generation did not produce an evaluation"
        assert (
            "timing_metrics" in result2
        ), "Resumed scene generation did not produce timing metrics"

        # Display results
        console.print("\n[bold cyan]Resumed Scene:[/bold cyan]")
        console.print(Panel(result2["scene"], border_style="green"))

        # Display timing metrics
        timing_table = Table(title="Resumed Scene Generation Timing")
        timing_table.add_column("Stage", style="cyan")
        timing_table.add_column("Time (s)", style="green")
        for stage, time_taken in result2["timing_metrics"].items():
            timing_table.add_row(stage.replace("_", " ").title(), f"{time_taken:.2f}")
        console.print(timing_table)

    console.print("\n[bold green]Checkpoint test completed successfully![/bold green]")


if __name__ == "__main__":
    test_enhanced_playwright_collaboration()
    test_checkpoint_functionality()
