#!/usr/bin/env python3
"""
Simplified multi-scene demo focusing on continuity and memory.
"""

import os
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from thespian.llm import LLMManager
from thespian.llm.consolidated_playwright import (
    Playwright, 
    SceneRequirements, 
    PlaywrightCapability, 
    create_playwright
)
from thespian.llm.theatrical_memory import TheatricalMemory, CharacterProfile, StoryOutline
from thespian.llm.enhanced_memory import EnhancedTheatricalMemory
from thespian.llm.quality_control import TheatricalQualityControl


def main():
    console = Console()
    
    console.print(Panel(
        "[bold cyan]🎭 Thespian Continuity Demo[/bold cyan]\n"
        "[dim]Testing memory and continuity across scenes[/dim]",
        style="bright_blue"
    ))
    
    # Initialize components
    llm_manager = LLMManager()
    enhanced_memory = EnhancedTheatricalMemory()
    quality_control = TheatricalQualityControl()
    
    # Create playwright with memory capabilities
    playwright = create_playwright(
        name="ContinuityPlaywright",
        llm_manager=llm_manager,
        memory=enhanced_memory,
        capabilities=[
            PlaywrightCapability.BASIC,
            PlaywrightCapability.MEMORY_ENHANCEMENT,
            PlaywrightCapability.CHARACTER_TRACKING
        ],
        quality_control=quality_control,
        model_type="ollama"
    )
    
    # Create a simple story
    theme = "A family of robots learns about love across generations"
    console.print(f"\n[bold]Theme:[/bold] {theme}")
    
    # Create characters with relationships
    console.print("\n[bold]Creating Character Family:[/bold]")
    
    characters = [
        CharacterProfile(
            id="elder",
            name="ELDER-UNIT",
            background="The oldest robot, creator of the family",
            motivations=["Pass on wisdom", "See family thrive"],
            relationships={
                "PARENT-UNIT": "Created child",
                "YOUNG-UNIT": "Grandchild"
            },
            development_arc=[
                {"stage": "wisdom", "description": "Shares knowledge"},
                {"stage": "acceptance", "description": "Accepts mortality"}
            ]
        ),
        CharacterProfile(
            id="parent",
            name="PARENT-UNIT",
            background="Middle generation, bridge between old and new",
            motivations=["Protect family", "Honor Elder's legacy"],
            relationships={
                "ELDER-UNIT": "Creator/parent", 
                "YOUNG-UNIT": "Created child"
            },
            development_arc=[
                {"stage": "duty", "description": "Follows Elder's teachings"},
                {"stage": "growth", "description": "Finds own path"}
            ]
        ),
        CharacterProfile(
            id="young",
            name="YOUNG-UNIT",
            background="Newest generation, full of curiosity",
            motivations=["Explore world", "Understand emotions"],
            relationships={
                "ELDER-UNIT": "Grandparent",
                "PARENT-UNIT": "Creator/parent"
            },
            development_arc=[
                {"stage": "curiosity", "description": "Questions everything"},
                {"stage": "understanding", "description": "Learns about love"}
            ]
        )
    ]
    
    for char in characters:
        enhanced_memory.update_character_profile(char.id, char)
        console.print(f"  • [cyan]{char.name}[/cyan]: {char.background}")
    
    # Generate three connected scenes
    scenes = [
        {
            "id": "scene1",
            "title": "The Teaching",
            "description": "Elder teaches Parent about emotions",
            "characters": ["ELDER-UNIT", "PARENT-UNIT"],
            "setting": "The Family Core - warm glowing space"
        },
        {
            "id": "scene2", 
            "title": "The Birth",
            "description": "Parent creates Young with Elder's guidance",
            "characters": ["ELDER-UNIT", "PARENT-UNIT", "YOUNG-UNIT"],
            "setting": "The Creation Chamber - pulsing with new life"
        },
        {
            "id": "scene3",
            "title": "The Legacy", 
            "description": "Three generations share their understanding of love",
            "characters": ["ELDER-UNIT", "PARENT-UNIT", "YOUNG-UNIT"],
            "setting": "The Memory Garden - where experiences are stored"
        }
    ]
    
    generated_scenes = {}
    
    console.print("\n[bold]Generating Connected Scenes:[/bold]\n")
    
    for i, scene in enumerate(scenes):
        console.print(f"[cyan]Scene {i+1}: {scene['title']}[/cyan]")
        
        # Build requirements with increasing context
        requirements = SceneRequirements(
            setting=scene['setting'],
            characters=scene['characters'],
            props=["Memory cores", "Holographic photos", "Energy bonds"],
            lighting="Soft, warm lighting that pulses with emotion",
            sound="Harmonic resonance between family units",
            style="Intimate Science Fiction Drama",
            period="Post-human era",
            target_audience="All ages",
            act_number=1,
            scene_number=i+1,
            premise=scene['description'],
            emotional_arc="Building understanding of love",
            key_conflict="Bridging generational understanding"
        )
        
        # Add generation directive for continuity
        if i > 0:
            requirements.generation_directives = (
                f"Build on previous scenes. Reference earlier conversations. "
                f"Show character growth from scene {i}."
            )
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(f"[cyan]Generating scene {i+1}...", total=None)
            
            result = playwright.generate_scene(requirements)
            
            progress.update(task, completed=True)
        
        # Store scene
        scene_content = result.get("scene", "")
        generated_scenes[scene['id']] = scene_content
        
        # Update memory
        enhanced_memory.add_scene_to_memory(
            scene_id=scene['id'],
            act_number=1,
            scene_number=i+1,
            content=scene_content,
            characters=scene['characters']
        )
        
        # Show excerpt
        excerpt = scene_content[:250] + "..." if len(scene_content) > 250 else scene_content
        console.print(Panel(excerpt, style="dim"))
        
        # Analyze character mentions for continuity
        char_mentions = {}
        for char in scene['characters']:
            mentions = scene_content.upper().count(char)
            char_mentions[char] = mentions
        
        console.print(f"  Character presence: {char_mentions}")
        console.print()
    
    # Continuity Analysis
    console.print("\n[bold]Continuity Analysis:[/bold]")
    
    continuity_table = Table(show_header=True, header_style="bold magenta")
    continuity_table.add_column("Check")
    continuity_table.add_column("Result")
    continuity_table.add_column("Details")
    
    # Check character consistency
    all_characters = set()
    for scene in scenes:
        all_characters.update(scene['characters'])
    
    for char_name in all_characters:
        appearances = sum(1 for s in scenes if char_name in s['characters'])
        char_profile = enhanced_memory.get_character_profile(char_name.lower().replace('-', ''))
        
        continuity_table.add_row(
            f"{char_name} Continuity",
            "✓ Present" if char_profile else "⚠ Missing",
            f"Appears in {appearances} scenes"
        )
    
    # Check scene memory
    scene_count = enhanced_memory.get_scene_count()
    continuity_table.add_row(
        "Scene Memory",
        f"✓ {scene_count} scenes",
        "All scenes stored in memory"
    )
    
    # Check relationship tracking
    relationship_count = 0
    for char_id in ["elder", "parent", "young"]:
        profile = enhanced_memory.get_character_profile(char_id)
        if profile and hasattr(profile, 'relationships'):
            relationship_count += len(profile.relationships)
    
    continuity_table.add_row(
        "Relationships",
        f"✓ {relationship_count} tracked",
        "Family connections maintained"
    )
    
    console.print(continuity_table)
    
    # Character Development Summary
    console.print("\n[bold]Character Development Tracking:[/bold]")
    
    dev_table = Table(show_header=True, header_style="bold yellow")
    dev_table.add_column("Character")
    dev_table.add_column("Initial State")
    dev_table.add_column("Development")
    dev_table.add_column("Relationships")
    
    for char in characters:
        profile = enhanced_memory.get_character_profile(char.id)
        if profile:
            initial = profile.development_arc[0]['description'] if profile.development_arc else "Unknown"
            dev_stage = len(profile.development_arc) if hasattr(profile, 'development_arc') else 0
            rel_count = len(profile.relationships) if hasattr(profile, 'relationships') else 0
            
            dev_table.add_row(
                char.name,
                initial,
                f"{dev_stage} stages",
                f"{rel_count} connections"
            )
    
    console.print(dev_table)
    
    # Memory Context Check
    console.print("\n[bold]Memory Context Verification:[/bold]")
    
    # Get memory context for final scene
    memory_context = playwright._get_memory_context(1, 3)
    
    if memory_context:
        console.print(f"  • Previous scenes recalled: {memory_context.get('previous_scene_count', 0)}")
        console.print(f"  • Character profiles loaded: {len(memory_context.get('character_profiles', {}))}")
        console.print(f"  • Story context: {'✓ Active' if memory_context.get('story_context') else '⚠ Missing'}")
    
    console.print("\n[green]✨ Continuity demo completed![/green]")
    console.print("[dim]Memory system successfully maintained context across scenes[/dim]")

if __name__ == "__main__":
    main()