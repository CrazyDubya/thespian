"""
Test script for production structure with acts and timing analysis.
"""

import os
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.table import Table
from rich.panel import Panel

from thespian.llm import LLMManager
from thespian.llm.theatrical_memory import TheatricalMemory
from thespian.llm.production_structure import ProductionStructure, ActManager
from thespian.llm.agent_personas import get_persona


def main():
    console = Console()

    # Initialize components
    llm_manager = LLMManager()
    memory = TheatricalMemory()

    # Create production structure
    production = ProductionStructure(
        title="The Enchanted Garden",
        num_acts=3,
        total_target_duration=120,  # 2 hours
        style="Magical Realism",
        target_audience="Family",
    )
    production.initialize_default_acts()

    # Initialize act manager and get persona
    act_manager = ActManager(llm_manager, memory)
    act_persona = get_persona("ActManager")

    # Display production info with act manager's persona
    console.print(
        Panel.fit(
            f"[bold blue]Production:[/] {production.title}\n"
            f"[bold blue]Style:[/] {production.style}\n"
            f"[bold blue]Target Audience:[/] {production.target_audience}\n"
            f"[bold blue]Total Duration:[/] {production.total_target_duration} minutes\n\n"
            f"[bold magenta]Overseen by:[/] {act_persona.name}, {act_persona.title}\n"
            f'[italic]"{act_persona.catchphrase}"[/]',
            title="Production Structure",
        )
    )

    # Generate acts
    for act in production.acts:
        console.print(f"\n[bold green]Generating Act {act.act_number}[/]")
        console.print(f"Theme: {act.theme}")
        console.print(f"Dramatic Arc: {act.dramatic_arc}")
        console.print(f"Target Duration: {act.target_duration} minutes")

        # Get timing advisor persona
        timing_persona = get_persona("TimingAdvisor")
        console.print(f"\n[dim italic]{timing_persona.name} adjusts her antique stopwatch...[/]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            task = progress.add_task(f"Generating Act {act.act_number}...", total=act.min_scenes)

            def update_progress(current: int, total: int):
                progress.update(task, completed=current)

            scenes = act_manager.generate_act(act, update_progress)

            # Display timing metrics with persona flavor
            metrics = act_manager.get_timing_metrics()
            console.print(
                f"\n[italic]{timing_persona.name} consults her temporal instruments...[/]"
            )
            table = Table(title=f"Act {act.act_number} Timing Analysis by {timing_persona.name}")
            table.add_column("Stage", style="cyan")
            table.add_column("Time (seconds)", justify="right", style="green")

            for stage, time_taken in metrics.items():
                table.add_row(stage.replace("_", " ").title(), f"{time_taken:.2f}")

            console.print(table)
            console.print(f'[dim italic]"{timing_persona.catchphrase}"[/]')

            # Display scene summaries with dramatic flair
            dramatic_persona = get_persona("DramaticStructureAdvisor")
            console.print(f"\n[italic]{dramatic_persona.name} reviews the dramatic structure...[/]")
            for scene in scenes:
                console.print(
                    Panel(
                        f"[bold]Scene {scene['scene']}[/]\n\n" f"{scene['content'][:200]}...",
                        title=f"Act {act.act_number}, Scene {scene['scene']}",
                    )
                )
            console.print(f'[dim italic]"{dramatic_persona.catchphrase}"[/]')


if __name__ == "__main__":
    main()
