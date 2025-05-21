"""
Test script for the dialogue system.
"""

import os
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress
from rich.table import Table
from thespian.llm import LLMManager
from thespian.llm.theatrical_memory import TheatricalMemory
from thespian.llm.theatrical_advisors import AdvisorManager
from thespian.llm.quality_control import TheatricalQualityControl
from thespian.llm.playwright import EnhancedPlaywright, SceneRequirements
from thespian.llm.dialogue_system import DialogueSystem


def main():
    console = Console()

    # Initialize components
    llm_manager = LLMManager()
    memory = TheatricalMemory()
    advisor_manager = AdvisorManager(llm_manager, memory)
    quality_control = TheatricalQualityControl()

    # Create playwright
    playwright = EnhancedPlaywright(
        name="Test Playwright",
        llm_manager=llm_manager,
        memory=memory,
        advisor_manager=advisor_manager,
        quality_control=quality_control,
    )

    # Define scene requirements
    requirements = SceneRequirements(
        setting="A Victorian-era drawing room",
        characters=["Lady Eleanor", "Professor Blackwood", "The Butler"],
        props=["antique clock", "tea set", "mysterious letter"],
        lighting="dim gas lamps",
        sound="distant thunder",
        style="Gothic Mystery",
        period="Victorian",
        target_audience="Adult",
    )

    # Display production information
    console.print(
        Panel.fit(
            f"[bold]The Enchanted Garden[/bold]\n"
            f"Style: {requirements.style}\n"
            f"Period: {requirements.period}\n"
            f"Target Audience: {requirements.target_audience}",
            title="Production Information",
        )
    )

    # Generate scene with progress tracking
    with Progress() as progress:
        task = progress.add_task("[cyan]Generating scene...", total=playwright.max_iterations + 1)

        result = playwright.generate_scene(
            requirements,
            progress_callback=lambda current, total: progress.update(task, completed=current),
        )

    # Display scene
    console.print("\n[bold]Generated Scene:[/bold]")
    console.print(Panel(result["scene"], title="Scene Content"))

    # Display evaluation
    console.print("\n[bold]Scene Evaluation:[/bold]")
    evaluation_table = Table(show_header=True, header_style="bold magenta")
    evaluation_table.add_column("Aspect")
    evaluation_table.add_column("Score")
    evaluation_table.add_column("Feedback")

    for aspect, data in result["evaluation"].items():
        evaluation_table.add_row(
            aspect.replace("_", " ").title(), f"{data['score']:.2f}", data["feedback"]
        )

    console.print(evaluation_table)

    # Display dialogue history
    console.print("\n[bold]Advisor Dialogue History:[/bold]")
    for advisor_type, history in result["dialogue_history"].items():
        if history:
            console.print(f"\n[bold]{advisor_type.title()} Advisor:[/bold]")
            for entry in history:
                console.print(
                    Panel(
                        f"[bold]Question:[/bold] {entry['question']}\n"
                        f"[bold]Feedback:[/bold] {entry['feedback']['feedback']}\n"
                        f"[bold]Suggestions:[/bold]\n"
                        + "\n".join(f"- {s}" for s in entry["feedback"]["suggestions"]),
                        title=f"Dialogue Entry ({entry['timestamp']})",
                    )
                )

    # Display timing metrics
    console.print("\n[bold]Timing Metrics:[/bold]")
    timing_table = Table(show_header=True, header_style="bold magenta")
    timing_table.add_column("Stage")
    timing_table.add_column("Time (seconds)")

    for stage, time_taken in result["timing_metrics"].items():
        timing_table.add_row(stage.replace("_", " ").title(), f"{time_taken:.2f}")

    console.print(timing_table)


if __name__ == "__main__":
    main()
