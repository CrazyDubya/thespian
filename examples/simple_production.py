"""
Simple example of using the Thespian framework to create a theatrical production
with enhanced playwright collaboration and advisor integration.
"""

import os
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress
from rich.table import Table

from thespian.llm import LLMManager
from thespian.llm.playwright import EnhancedPlaywright, SceneRequirements
from thespian.llm.theatrical_memory import TheatricalMemory, CharacterProfile, StoryOutline
from thespian.llm.theatrical_advisors import AdvisorManager
from thespian.llm.quality_control import TheatricalQualityControl
from thespian.llm.dialogue_system import DialogueSystem


def main():
    console = Console()

    # Initialize components
    llm_manager = LLMManager()
    memory = TheatricalMemory()
    advisor_manager = AdvisorManager(llm_manager, memory)
    quality_control = TheatricalQualityControl()

    # Create enhanced playwrights
    ollama_playwright = EnhancedPlaywright(
        name="Ollama",
        llm_manager=llm_manager,
        memory=memory,
        advisor_manager=advisor_manager,
        quality_control=quality_control,
        model_type="ollama",
    )

    grok_playwright = EnhancedPlaywright(
        name="Grok",
        llm_manager=llm_manager,
        memory=memory,
        advisor_manager=advisor_manager,
        quality_control=quality_control,
        model_type="grok",
    )

    # Initialize character profiles
    character_profiles = {
        "romeo": CharacterProfile(
            id="romeo",
            name="Romeo",
            background="A young hacker in Neo-Tokyo",
            motivations=["Find true love", "Escape corporate control", "Prove his worth"],
            relationships={"Juliet": "Love interest", "Mercutio": "Best friend"},
            development_arc=[
                {
                    "stage": "initial",
                    "description": "Rebellious hacker seeking meaning in a corporate world",
                }
            ],
        ),
        "juliet": CharacterProfile(
            id="juliet",
            name="Juliet",
            background="Heir to a corporate empire",
            motivations=["Find freedom", "Experience real life", "Defy family expectations"],
            relationships={"Romeo": "Love interest", "Nurse": "Confidant"},
            development_arc=[
                {"stage": "initial", "description": "Trapped in a gilded cage, seeking escape"}
            ],
        ),
    }

    # Store character profiles
    for char_id, profile in character_profiles.items():
        ollama_playwright.update_character_profile(char_id, profile)
        grok_playwright.update_character_profile(char_id, profile)

    # Initialize story outline
    story_outline = StoryOutline(
        title="The Quantum Paradox",
        acts=[{
            "act_number": 1,
            "description": "The discovery of quantum entanglement in the lab",
            "key_events": [
                "Dr. Chen and Dr. Tanaka make breakthrough discovery",
                "AI Assistant helps analyze the data",
                "Initial experiment shows unexpected results"
            ],
            "status": "draft"
        }]
    )
    
    # Set story outline for both playwrights
    ollama_playwright.story_outline = story_outline
    grok_playwright.story_outline = story_outline

    # Create scene requirements
    requirements = SceneRequirements(
        setting="A high-tech laboratory in Neo-Tokyo",
        characters=["Dr. Sarah Chen", "Dr. James Tanaka", "AI Assistant"],
        props=["Holographic displays", "Neural interface terminals", "Quantum computers"],
        lighting="Bright, clinical lighting with blue accents",
        sound="Ambient electronic hum with occasional beeps",
        style="Science fiction",
        period="2089",
        target_audience="Young adults",
        act_number=1,
        scene_number=1
    )

    # Display production information
    console.print(
        Panel.fit(
            "[bold]Cyberpunk Romeo and Juliet[/bold]\n"
            f"Style: {requirements.style}\n"
            f"Period: {requirements.period}\n"
            f"Target Audience: {requirements.target_audience}",
            title="Production Information",
        )
    )

    # Generate scene with progress tracking
    with Progress() as progress:
        task = progress.add_task("[cyan]Generating scene...", total=3)

        def progress_callback(current: int, total: int):
            status = (
                "Ollama generating opening"
                if current == 1
                else "Getting opening feedback" if current == 2 else "Grok enhancing scene"
            )
            progress.update(task, completed=current, description=f"[cyan]{status}")

        # Collaborate on scene generation
        result = ollama_playwright.collaborate_on_scene(
            grok_playwright, requirements, progress_callback=progress_callback
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
