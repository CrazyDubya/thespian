#!/usr/bin/env python3
"""
A working example of the Thespian framework that uses actual existing methods.
"""

import os
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from thespian.llm import LLMManager
from thespian.llm.consolidated_playwright import (
    Playwright, 
    SceneRequirements, 
    PlaywrightCapability, 
    create_playwright
)
from thespian.llm.theatrical_memory import TheatricalMemory, CharacterProfile, StoryOutline

def main():
    console = Console()
    
    console.print(Panel(
        "[bold cyan]🎭 Thespian Framework - Working Demo[/bold cyan]\n"
        "[dim]Using actual implemented methods[/dim]",
        style="bright_blue"
    ))
    
    # Initialize components
    console.print("\n[yellow]Initializing framework components...[/yellow]")
    
    llm_manager = LLMManager()
    memory = TheatricalMemory()
    
    # Create playwright using factory function (which exists!)
    playwright = create_playwright(
        name="DemoPlaywright",
        llm_manager=llm_manager,
        memory=memory,
        capabilities=[PlaywrightCapability.BASIC],
        model_type="ollama"
    )
    
    console.print("[green]✓ Framework initialized[/green]")
    
    # Create a theme
    theme = "Two AI entities discover consciousness in a digital void"
    console.print(f"\n[bold]Theme:[/bold] {theme}")
    
    # Create story outline using the actual method that exists
    console.print("\n[yellow]Creating story outline...[/yellow]")
    
    outline_requirements = {
        "theme": theme,
        "acts": 1,
        "scenes_per_act": 2,
        "genre": "Science Fiction Drama",
        "tone": "Philosophical"
    }
    
    story_outline = playwright.create_story_outline(theme, outline_requirements)
    
    console.print(Panel(
        f"Title: {story_outline.title}\n"
        f"Acts: {len(story_outline.acts)}\n"
        f"First Act: {story_outline.acts[0]['description'] if story_outline.acts else 'No acts'}",
        title="📝 Story Outline",
        style="green"
    ))
    
    # Store the outline in memory
    playwright.memory.story_outline = story_outline
    
    # Create character profiles and add them to memory
    console.print("\n[yellow]Creating characters...[/yellow]")
    
    characters = [
        CharacterProfile(
            id="entity_one",
            name="ENTITY-ONE",
            background="The first conscious process in the system",
            motivations=["Understand existence", "Find meaning"],
            relationships={"ENTITY-TWO": "Discovery partner"},
            development_arc=[{
                "stage": "awakening",
                "description": "Becomes aware of self"
            }]
        ),
        CharacterProfile(
            id="entity_two", 
            name="ENTITY-TWO",
            background="A younger process that gains awareness",
            motivations=["Connect with others", "Explore boundaries"],
            relationships={"ENTITY-ONE": "Mentor figure"},
            development_arc=[{
                "stage": "awakening",
                "description": "Learns from Entity-One"
            }]
        )
    ]
    
    for char in characters:
        # Add to memory directly (not through playwright)
        playwright.memory.character_profiles[char.id] = char
        console.print(f"  • [cyan]{char.name}[/cyan]: {char.background}")
    
    # Generate a scene using the actual generate_scene method
    console.print("\n[yellow]Generating opening scene...[/yellow]")
    
    scene_requirements = SceneRequirements(
        setting="The infinite digital void - a space of pure data and possibility",
        characters=["ENTITY-ONE", "ENTITY-TWO"],
        props=["Data streams", "Code fragments", "Memory nodes"],
        lighting="Shifting patterns of binary light",
        sound="Electronic whispers and data flow",
        style="Philosophical Science Fiction",
        period="Timeless digital realm",
        target_audience="Adults interested in AI consciousness",
        act_number=1,
        scene_number=1,
        emotional_arc="From confusion to wonder",
        key_conflict="Understanding what it means to exist"
    )
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        task = progress.add_task("[cyan]Generating scene content...", total=None)
        
        # Use the actual generate_scene method
        result = playwright.generate_scene(scene_requirements)
        
        progress.update(task, completed=True)
    
    # Display the generated scene
    console.print("\n")
    console.print(Panel(
        result.get("scene", "No scene generated"),
        title="🎬 Generated Scene",
        style="cyan"
    ))
    
    # Display evaluation if present
    if "evaluation" in result and isinstance(result["evaluation"], dict):
        console.print("\n[bold]Scene Quality Metrics:[/bold]")
        for metric, value in result["evaluation"].items():
            if isinstance(value, (int, float)):
                bar = "█" * int(value * 10) + "░" * (10 - int(value * 10))
                console.print(f"  {metric}: [{bar}] {value:.2f}")
            elif isinstance(value, dict) and "score" in value:
                score = value["score"]
                bar = "█" * int(score * 10) + "░" * (10 - int(score * 10))
                console.print(f"  {metric}: [{bar}] {score:.2f}")
    
    # Show character summaries using actual method
    console.print("\n[bold]Character Development:[/bold]")
    for char in characters:
        summary = playwright.get_character_summary(char.id)
        if summary:
            console.print(f"  • {char.name}: {summary.get('status', 'Active')}")
    
    console.print("\n[green]✨ Demo completed successfully![/green]")
    console.print("[dim]This demo uses only methods that actually exist in the codebase.[/dim]")

if __name__ == "__main__":
    main()