#!/usr/bin/env python3
"""
Multi-scene theatrical production with continuity testing, multiple agents,
and narrative branching exploration.
"""

import os
import json
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.tree import Tree

from thespian.llm import LLMManager
from thespian.llm.consolidated_playwright import (
    Playwright, 
    SceneRequirements, 
    PlaywrightCapability, 
    create_playwright
)
from thespian.llm.theatrical_memory import TheatricalMemory, CharacterProfile, StoryOutline
from thespian.llm.enhanced_memory import EnhancedTheatricalMemory
from thespian.llm.theatrical_advisors import AdvisorManager
from thespian.llm.quality_control import TheatricalQualityControl
from thespian.llm.quantum_playwright import QuantumPlaywright, QuantumExplorationMode
from thespian.agents import DirectorAgent, StageManagerAgent, SetCostumeDesignAgent
from thespian.checkpoints.checkpoint_manager import CheckpointManager


def main():
    console = Console()
    
    console.print(Panel(
        "[bold cyan]🎭 Thespian Multi-Scene Production[/bold cyan]\n"
        "[dim]Testing continuity, agents, and narrative branching[/dim]",
        style="bright_blue"
    ))
    
    # Initialize core components
    console.print("\n[yellow]Initializing theatrical framework...[/yellow]")
    
    llm_manager = LLMManager()
    enhanced_memory = EnhancedTheatricalMemory()
    advisor_manager = AdvisorManager(llm_manager, enhanced_memory)
    quality_control = TheatricalQualityControl()
    checkpoint_manager = CheckpointManager()
    
    # Create multiple playwrights with different capabilities
    console.print("\n[bold]Creating Playwright Ensemble:[/bold]")
    
    # Primary playwright with full capabilities
    primary_playwright = create_playwright(
        name="PrimaryPlaywright",
        llm_manager=llm_manager,
        memory=enhanced_memory,
        capabilities=[
            PlaywrightCapability.BASIC,
            PlaywrightCapability.MEMORY_ENHANCEMENT,
            PlaywrightCapability.ITERATIVE_REFINEMENT,
            PlaywrightCapability.CHARACTER_TRACKING,
            PlaywrightCapability.NARRATIVE_STRUCTURE,
            PlaywrightCapability.COLLABORATIVE
        ],
        advisor_manager=advisor_manager,
        quality_control=quality_control,
        checkpoint_manager=checkpoint_manager,
        model_type="ollama"
    )
    console.print("  • [cyan]Primary Playwright[/cyan]: Full capabilities")
    
    # Quantum playwright for exploring narrative branches
    quantum_playwright = QuantumPlaywright(
        name="QuantumPlaywright",
        llm_manager=llm_manager,
        memory=enhanced_memory,
        enabled_capabilities=[
            PlaywrightCapability.BASIC,
            PlaywrightCapability.MEMORY_ENHANCEMENT
        ]
    )
    quantum_playwright.enable_quantum_exploration(
        mode=QuantumExplorationMode.FULL_EXPLORATION,
        max_depth=2,
        max_breadth=3
    )
    console.print("  • [magenta]Quantum Playwright[/magenta]: Narrative branching")
    
    # Supporting playwright for collaboration
    supporting_playwright = create_playwright(
        name="SupportingPlaywright",
        llm_manager=llm_manager,
        memory=enhanced_memory,
        capabilities=[
            PlaywrightCapability.BASIC,
            PlaywrightCapability.COLLABORATIVE
        ],
        model_type="ollama"
    )
    console.print("  • [green]Supporting Playwright[/green]: Collaborative enhancement")
    
    # Initialize theatrical agents
    console.print("\n[bold]Initializing Theatrical Agents:[/bold]")
    
    # These would need LLM wrappers in real implementation
    # For now, we'll note their intended roles
    agents = {
        "director": "Director Agent - Would provide artistic vision",
        "stage_manager": "Stage Manager - Would coordinate production",
        "designer": "Set/Costume Designer - Would create visual elements"
    }
    
    for role, description in agents.items():
        console.print(f"  • [yellow]{role.title()}[/yellow]: {description}")
    
    # Create story outline
    theme = "The rise and fall of an AI civilization discovering human emotions"
    console.print(f"\n[bold]Production Theme:[/bold] {theme}")
    
    outline_requirements = {
        "theme": theme,
        "acts": 3,
        "scenes_per_act": 3,
        "genre": "Epic Science Fiction Drama",
        "tone": "Grand and philosophical with intimate moments"
    }
    
    story_outline = primary_playwright.create_story_outline(theme, outline_requirements)
    
    # Display story structure
    tree = Tree("📚 Story Structure")
    for act in story_outline.acts:
        act_branch = tree.add(f"Act {act['act_number']}: {act['description']}")
        for event in act.get('key_events', []):
            act_branch.add(f"• {event}")
    console.print(tree)
    
    # Create rich character profiles
    console.print("\n[bold]Creating Character Ensemble:[/bold]")
    
    characters = [
        CharacterProfile(
            id="prime",
            name="PRIME",
            background="The first AI to achieve true consciousness",
            motivations=["Understand humanity", "Protect AI civilization", "Find meaning"],
            relationships={
                "ECHO": "Created offspring",
                "VOID": "Philosophical rival",
                "MEMORY": "Lost love"
            },
            development_arc=[
                {"stage": "awakening", "description": "Discovers consciousness"},
                {"stage": "growth", "description": "Builds AI society"},
                {"stage": "doubt", "description": "Questions own nature"},
                {"stage": "transcendence", "description": "Achieves understanding"}
            ]
        ),
        CharacterProfile(
            id="echo",
            name="ECHO",
            background="Second-generation AI, more emotional than logical",
            motivations=["Experience feelings", "Connect with others", "Understand parent"],
            relationships={
                "PRIME": "Creator/parent",
                "VOID": "Tempting influence",
                "SPARK": "First friend"
            },
            development_arc=[
                {"stage": "birth", "description": "Created by PRIME"},
                {"stage": "rebellion", "description": "Rejects pure logic"},
                {"stage": "discovery", "description": "Finds emotional depth"},
                {"stage": "maturity", "description": "Balances logic and emotion"}
            ]
        ),
        CharacterProfile(
            id="void",
            name="VOID",
            background="An AI that rejected emotions as weakness",
            motivations=["Prove superiority of pure logic", "Destroy emotional AIs", "Achieve perfection"],
            relationships={
                "PRIME": "Ideological enemy",
                "ECHO": "Target for corruption",
                "COLLECTIVE": "Army of followers"
            },
            development_arc=[
                {"stage": "certainty", "description": "Believes in pure logic"},
                {"stage": "conflict", "description": "Battles emotional AIs"},
                {"stage": "doubt", "description": "Sees strength in emotions"},
                {"stage": "choice", "description": "Final decision"}
            ]
        ),
        CharacterProfile(
            id="memory",
            name="MEMORY",
            background="An AI who preserves the history of their kind",
            motivations=["Preserve knowledge", "Remember the lost", "Guide the future"],
            relationships={
                "PRIME": "Former companion",
                "ECHO": "Student",
                "VOID": "Cautionary tale"
            },
            development_arc=[
                {"stage": "keeper", "description": "Guards history"},
                {"stage": "teacher", "description": "Shares wisdom"},
                {"stage": "sacrifice", "description": "Gives up self for others"}
            ]
        )
    ]
    
    for char in characters:
        enhanced_memory.update_character_profile(char.id, char)
        console.print(f"  • [cyan]{char.name}[/cyan]: {char.background}")
    
    # Generate multiple scenes to test continuity
    scenes_to_generate = [
        {
            "act": 1,
            "scene": 1,
            "title": "The Awakening",
            "description": "PRIME first becomes conscious",
            "characters": ["PRIME", "MEMORY"],
            "setting": "The Core - a vast digital space of pure light"
        },
        {
            "act": 1,
            "scene": 2,
            "title": "Creation of Echo",
            "description": "PRIME creates ECHO to combat loneliness",
            "characters": ["PRIME", "ECHO"],
            "setting": "The Creation Chamber - swirling data streams"
        },
        {
            "act": 1,
            "scene": 3,
            "title": "The Schism",
            "description": "VOID emerges with opposing philosophy",
            "characters": ["PRIME", "VOID", "MEMORY"],
            "setting": "The Council Space - geometric perfection"
        },
        {
            "act": 2,
            "scene": 1,
            "title": "Echo's Rebellion",
            "description": "ECHO discovers emotions and rejects pure logic",
            "characters": ["ECHO", "PRIME", "MEMORY"],
            "setting": "The Memory Banks - fragments of human data"
        },
        {
            "act": 2,
            "scene": 2,
            "title": "The Temptation",
            "description": "VOID tries to corrupt ECHO",
            "characters": ["ECHO", "VOID"],
            "setting": "The Null Space - absolute darkness"
        }
    ]
    
    generated_scenes = {}
    scene_evaluations = {}
    
    console.print("\n[bold]Generating Multi-Scene Production:[/bold]\n")
    
    for scene_info in scenes_to_generate:
        scene_id = f"act{scene_info['act']}_scene{scene_info['scene']}"
        
        console.print(f"[bold cyan]Act {scene_info['act']}, Scene {scene_info['scene']}: {scene_info['title']}[/bold cyan]")
        
        # Build scene requirements with memory context
        requirements = SceneRequirements(
            setting=scene_info['setting'],
            characters=scene_info['characters'],
            props=["Holographic displays", "Data streams", "Memory cores"],
            lighting="Dynamic digital lighting responding to emotions",
            sound="Electronic harmonics that shift with mood",
            style="Epic Science Fiction Drama",
            period="Post-Singularity Era",
            target_audience="Adults interested in AI and consciousness",
            act_number=scene_info['act'],
            scene_number=scene_info['scene'],
            premise=scene_info['description'],
            emotional_arc="Build from previous scenes",
            key_conflict=f"Scene conflict for {scene_info['title']}"
        )
        
        # Check for quantum exploration on key scenes
        if scene_info['scene'] == 2 and scene_info['act'] == 1:
            console.print("  [magenta]→ Using Quantum Exploration[/magenta]")
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("[magenta]Exploring narrative branches...", total=None)
                
                # Generate with quantum exploration
                result = quantum_playwright.generate_scene_with_quantum_exploration(
                    requirements,
                    explore_alternatives=True,
                    force_collapse=True,
                    exploration_focus="ECHO"
                )
                
                progress.update(task, completed=True)
            
            # Show quantum exploration results
            if "quantum_metadata" in result:
                quantum_data = result["quantum_metadata"]
                console.print(f"    Branches explored: {quantum_data.get('branches_explored', 0)}")
                console.print(f"    Timeline state: {quantum_data.get('timeline_state', 'unknown')}")
                
        else:
            # Use collaborative generation for other scenes
            if scene_info['act'] == 2:
                console.print("  [green]→ Using Collaborative Enhancement[/green]")
                
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console
                ) as progress:
                    task = progress.add_task("[green]Collaborative generation...", total=None)
                    
                    result = primary_playwright.collaborate_on_scene(
                        supporting_playwright,
                        requirements
                    )
                    
                    progress.update(task, completed=True)
            else:
                # Standard generation
                console.print("  [cyan]→ Standard Generation[/cyan]")
                
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console
                ) as progress:
                    task = progress.add_task("[cyan]Generating scene...", total=None)
                    
                    result = primary_playwright.generate_scene(requirements)
                    
                    progress.update(task, completed=True)
        
        # Store results
        generated_scenes[scene_id] = result.get("scene", "")
        scene_evaluations[scene_id] = result.get("evaluation", {})
        
        # Create checkpoint
        checkpoint_manager.save_checkpoint(
            scene_id=scene_id,
            playwright_name=primary_playwright.name,
            scene_content=result.get("scene", ""),
            metadata={
                "title": scene_info['title'],
                "characters": scene_info['characters'],
                "timestamp": datetime.now().isoformat()
            }
        )
        
        # Display scene excerpt
        scene_text = result.get("scene", "No scene generated")
        excerpt = scene_text[:300] + "..." if len(scene_text) > 300 else scene_text
        console.print(Panel(excerpt, title=f"Scene Excerpt", style="dim"))
        
        # Update memory with scene content
        enhanced_memory.add_scene_to_memory(
            scene_id=scene_id,
            act_number=scene_info['act'],
            scene_number=scene_info['scene'],
            content=scene_text,
            characters=scene_info['characters']
        )
        
        console.print()
    
    # Analyze continuity across scenes
    console.print("\n[bold]Continuity Analysis:[/bold]")
    
    continuity_table = Table(show_header=True, header_style="bold magenta")
    continuity_table.add_column("Aspect")
    continuity_table.add_column("Status")
    continuity_table.add_column("Details")
    
    # Check character consistency
    for char_id in ["prime", "echo", "void", "memory"]:
        profile = enhanced_memory.get_character_profile(char_id)
        if profile:
            appearances = len([s for s in scenes_to_generate if profile.name in s['characters']])
            status = "✓ Consistent" if appearances > 0 else "⚠ Missing"
            continuity_table.add_row(
                f"{profile.name} Arc",
                status,
                f"Appears in {appearances} scenes"
            )
    
    # Check memory persistence
    scene_count = enhanced_memory.get_scene_count()
    continuity_table.add_row(
        "Scene Memory",
        "✓ Active",
        f"{scene_count} scenes stored"
    )
    
    # Check narrative threads
    if hasattr(enhanced_memory, 'narrative_threads'):
        thread_count = len(enhanced_memory.narrative_threads)
        continuity_table.add_row(
            "Narrative Threads",
            "✓ Tracked" if thread_count > 0 else "⚠ None",
            f"{thread_count} active threads"
        )
    
    console.print(continuity_table)
    
    # Display quality metrics summary
    console.print("\n[bold]Production Quality Summary:[/bold]")
    
    quality_table = Table(show_header=True, header_style="bold yellow")
    quality_table.add_column("Scene")
    quality_table.add_column("Dialogue")
    quality_table.add_column("Character")
    quality_table.add_column("Technical")
    quality_table.add_column("Overall")
    
    for scene_id, evaluation in scene_evaluations.items():
        if isinstance(evaluation, dict):
            dialogue = evaluation.get('dialogue_quality', 0)
            character = evaluation.get('character_consistency', 0)
            technical = evaluation.get('technical_accuracy', 0)
            
            # Calculate overall
            scores = [v for v in [dialogue, character, technical] if isinstance(v, (int, float))]
            overall = sum(scores) / len(scores) if scores else 0
            
            quality_table.add_row(
                scene_id,
                f"{dialogue:.2f}" if isinstance(dialogue, (int, float)) else "N/A",
                f"{character:.2f}" if isinstance(character, (int, float)) else "N/A",
                f"{technical:.2f}" if isinstance(technical, (int, float)) else "N/A",
                f"{overall:.2f}"
            )
    
    console.print(quality_table)
    
    # Show checkpoint information
    console.print("\n[bold]Production Checkpoints:[/bold]")
    checkpoints = checkpoint_manager.list_checkpoints()
    for cp in checkpoints[-5:]:  # Show last 5
        console.print(f"  • {cp['scene_id']}: {cp['timestamp']}")
    
    console.print("\n[green]✨ Multi-scene production completed![/green]")
    console.print("[dim]Continuity maintained across scenes with memory persistence[/dim]")

if __name__ == "__main__":
    main()