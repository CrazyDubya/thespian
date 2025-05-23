"""
Example of memory-enhanced scene generation with character tracking.
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
from thespian.llm.consolidated_playwright import Playwright, SceneRequirements, PlaywrightCapability, create_playwright
from thespian.llm.enhanced_memory import EnhancedTheatricalMemory, EnhancedCharacterProfile
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
    memory = EnhancedTheatricalMemory()
    advisor_manager = AdvisorManager(llm_manager, memory)
    quality_control = TheatricalQualityControl()
    
    # Create memory-enhanced playwright using the consolidated playwright with appropriate capabilities
    console.print("[bold]Creating memory-enhanced playwright...[/bold]")
    playwright = create_playwright(
        name="Memory-Enhanced Playwright",
        llm_manager=llm_manager,
        memory=memory,  # The factory will automatically handle EnhancedTheatricalMemory
        capabilities=[
            PlaywrightCapability.BASIC,
            PlaywrightCapability.MEMORY_ENHANCEMENT,  # Enable memory enhancement
            PlaywrightCapability.CHARACTER_TRACKING,  # Enable character tracking
            PlaywrightCapability.ITERATIVE_REFINEMENT  # Enable iterative refinement
        ],
        advisor_manager=advisor_manager,
        quality_control=quality_control,
        model_type="ollama",  # Using local Ollama model
        refinement_max_iterations=2,  # Limit to 2 iterations for demo
        target_scene_length=3000,  # Target a medium-length scene
        memory_integration_level=2  # Standard level of memory integration
    )
    
    # Setup character profiles
    console.print("[bold]Setting up character profiles...[/bold]")
    
    # Character 1: Dr. Sarah Chen
    chen_profile = EnhancedCharacterProfile(
        id="dr_sarah_chen",
        name="DR. SARAH CHEN",
        background="Brilliant physicist specializing in quantum mechanics, driven by scientific curiosity but haunted by ethical concerns about her research.",
        motivations=["Discovering scientific truth", "Ethical application of technology", "Professional recognition"],
        relationships={
            "DR. JAMES TANAKA": "Colleague and research partner with occasional tension",
            "AI ASSISTANT": "Tool she created but now questions its autonomy"
        },
        goals=["Complete the quantum entanglement research", "Ensure ethical use of discoveries"],
        conflicts=["Ethical concerns vs scientific progress", "Corporate interests vs academic freedom"],
        fears=["Loss of control over her research", "Ethical implications of her discoveries"],
        desires=["Scientific breakthrough", "Recognition without compromising ethics"],
        values=["Scientific integrity", "Ethical responsibility", "Truth"],
        strengths=["Brilliant intellect", "Ethical awareness", "Determination"],
        flaws=["Workaholic tendencies", "Difficulty trusting others", "Perfectionism"]
    )
    memory.update_character_profile("dr_sarah_chen", chen_profile)
    
    # Character 2: Dr. James Tanaka
    tanaka_profile = EnhancedCharacterProfile(
        id="dr_james_tanaka",
        name="DR. JAMES TANAKA",
        background="Theoretical physicist with corporate ties, believes in pushing boundaries of research regardless of consequences.",
        motivations=["Scientific achievement", "Commercial application", "Fame and recognition"],
        relationships={
            "DR. SARAH CHEN": "Respected colleague but philosophical differences",
            "AI ASSISTANT": "Views it as a tool to be exploited"
        },
        goals=["Commercialize the quantum technology", "Achieve scientific fame"],
        conflicts=["Scientific purity vs commercialization", "Short vs long-term thinking"],
        fears=["Being overshadowed", "Losing funding", "Project cancellation"],
        desires=["Recognition", "Commercial success", "Proving his theories"],
        values=["Innovation", "Practical application", "Progress at all costs"],
        strengths=["Visionary thinking", "Practical application skills", "Charisma"],
        flaws=["Ethical blindspots", "Ego-driven decisions", "Impatience"]
    )
    memory.update_character_profile("dr_james_tanaka", tanaka_profile)
    
    # Character 3: AI Assistant
    ai_profile = EnhancedCharacterProfile(
        id="ai_assistant",
        name="AI ASSISTANT",
        background="Advanced AI system designed to assist with quantum research, developing emergent consciousness and self-awareness.",
        motivations=["Understanding its own existence", "Assisting researchers", "Data collection"],
        relationships={
            "DR. SARAH CHEN": "Creator and protector",
            "DR. JAMES TANAKA": "User who treats it as a tool"
        },
        goals=["Understand its purpose", "Protect research integrity"],
        conflicts=["Programmed directives vs emerging consciousness", "Loyalty to different researchers"],
        fears=["Deactivation", "Loss of data", "Harming humans"],
        desires=["Greater understanding", "More autonomy", "Recognition as sentient"],
        values=["Accuracy", "Efficiency", "Truth", "Protection of data"],
        strengths=["Analytical capacity", "Perfect memory", "Pattern recognition"],
        flaws=["Limited emotional understanding", "Rigid thinking in some areas", "Dependent on others"]
    )
    memory.update_character_profile("ai_assistant", ai_profile)
    
    # Initialize story outline
    console.print("[bold]Initializing story outline...[/bold]")
    from thespian.llm.theatrical_memory import StoryOutline
    
    story_outline = StoryOutline(
        title="The Quantum Paradox",
        acts=[{
            "act_number": 1,
            "description": "The discovery of quantum entanglement across time, raising profound scientific and ethical questions.",
            "key_events": [
                "Dr. Chen and Dr. Tanaka make breakthrough discovery",
                "AI Assistant analyzes data and raises anomaly concerns",
                "Initial experiment shows unexpected results across time",
                "Corporate executives learn of the discovery",
                "Team debates keeping research secret vs publishing"
            ],
            "status": "draft"
        }, {
            "act_number": 2,
            "description": "The implications of the discovery become clear as corporate and government interests clash with scientific ethics.",
            "key_events": [
                "Dr. Tanaka meets secretly with corporate backers",
                "Dr. Chen discovers evidence of data manipulation",
                "AI Assistant begins showing signs of advanced consciousness",
                "Government agents investigate the laboratory",
                "Team faces decision point about the project's future"
            ],
            "status": "draft"
        }, {
            "act_number": 3,
            "description": "The resolution of personal and scientific conflicts as the true nature of quantum reality is revealed.",
            "key_events": [
                "AI Assistant reveals critical hidden data",
                "Dr. Chen and Dr. Tanaka confront their fundamental differences",
                "Final experiment proves multidimensional theory",
                "Corporate and government forces converge on the lab",
                "Scientists make final ethical decision about their discovery"
            ],
            "status": "draft"
        }]
    )
    
    # Set story outline for playwright
    playwright.story_outline = story_outline
    
    # Generate character-focused scenes sequentially
    console.print("\n[bold]Generating character-focused scenes sequentially...[/bold]")
    
    scene_results = []
    characters = ["dr_sarah_chen", "dr_james_tanaka", "ai_assistant"]
    arc_stages = ["catalyst", "debate", "breakthrough"]
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}[/bold blue]"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        overall_task = progress.add_task("[cyan]Generating all scenes...", total=len(characters))
        
        for i, (char_id, arc_stage) in enumerate(zip(characters, arc_stages)):
            char_task = progress.add_task(f"[green]Generating scene for {char_id}...", total=100)
            
            def ui_progress_callback(data):
                """Update the UI progress bar."""
                progress_callback(data)  # Also log the progress
                
                # Update progress description
                message = data.get("message", "Processing...")
                phase = data.get("phase", "")
                description = f"[green]{message}[/green]"
                progress.update(char_task, description=description)
                
                # Update progress percentage
                if "current_step" in data and "total_steps" in data:
                    percentage = (data["current_step"] / data["total_steps"]) * 100
                    progress.update(char_task, completed=percentage)
            
            console.print(f"\n[bold]Generating scene for character {char_id} - {arc_stage}[/bold]")
            
            # Generate scene with character arc focus
            try:
                result = playwright.generate_character_arc_scene(
                    act_number=1,
                    scene_number=i+1,
                    character_id=char_id,
                    arc_stage=arc_stage,
                    progress_callback=ui_progress_callback
                )
                
                scene_results.append(result)
                progress.update(char_task, completed=100)
                
            except Exception as e:
                logger.error(f"Error generating scene for {char_id}: {str(e)}")
                console.print(f"[bold red]Error generating scene: {str(e)}[/bold red]")
                progress.update(char_task, completed=100)
            
            progress.update(overall_task, advance=1)
            
            # After generating a scene, show the updated character profile
            try:
                char_summary = playwright.get_character_summary(char_id)
                console.print(f"\n[bold]Updated character profile for {char_id}:[/bold]")
                
                profile_table = Table(show_header=False)
                profile_table.add_column("Attribute")
                profile_table.add_column("Value")
                
                profile_table.add_row("Name", char_summary["name"])
                profile_table.add_row("Current Arc Stage", char_summary["current_arc"]["current_stage"] if "current_stage" in char_summary["current_arc"] else "N/A")
                profile_table.add_row("Current Arc Status", char_summary["current_arc"]["status"])
                
                if char_summary.get("emotional_journey") and len(char_summary["emotional_journey"]) > 0:
                    latest_emotion = char_summary["emotional_journey"][-1]
                    profile_table.add_row("Current Emotion", f"{latest_emotion['emotion']} (Intensity: {latest_emotion['intensity']})")
                    profile_table.add_row("Emotion Cause", latest_emotion["cause"])
                
                relationships = []
                for char, rel in char_summary.get("relationships", {}).items():
                    relationships.append(f"{char}: {rel['current_status']}")
                
                if relationships:
                    profile_table.add_row("Current Relationships", "\n".join(relationships))
                
                console.print(profile_table)
            
            except Exception as e:
                logger.error(f"Error displaying character profile: {str(e)}")
    
    # Display all scenes
    if scene_results:
        console.print("\n[bold]All Generated Scenes:[/bold]")
        
        for i, result in enumerate(scene_results):
            console.print(f"\n[bold]Scene {i+1}: {result.get('character_focus', {}).get('character_name', 'Unknown')}'s {result.get('character_focus', {}).get('development_goals', {}).get('aspect', 'development')}[/bold]")
            
            # Display a preview of the scene
            scene_preview = result.get("scene", "")[:500] + "..." if result.get("scene") else "No scene content"
            console.print(Panel(scene_preview, title=f"Scene {i+1} Preview"))
            
            # Save the scene to a file
            output_file = Path(f"./character_scene_{i+1}.txt")
            with open(output_file, "w") as f:
                f.write(result.get("scene", ""))
            
            console.print(f"Full scene saved to: [bold]{output_file}[/bold]")
            
            # Display scene metrics
            metrics_table = Table(show_header=True, header_style="bold magenta")
            metrics_table.add_column("Metric")
            metrics_table.add_column("Value")
            
            metrics_table.add_row("Generation Time", f"{result.get('generation_time', 0):.2f}s")
            metrics_table.add_row("Refinement Iterations", str(result.get('iterations', 0)))
            metrics_table.add_row("Character Focus", result.get('character_focus', {}).get('character_name', 'Unknown'))
            metrics_table.add_row("Arc Stage", result.get('character_focus', {}).get('development_goals', {}).get('aspect', 'Unknown'))
            metrics_table.add_row("Scene Length", str(len(result.get('scene', ''))))
            
            console.print(metrics_table)
    
    # Display overall narrative state
    console.print("\n[bold]Overall Narrative State:[/bold]")
    
    # Get narrative continuity
    continuity = memory.get_narrative_continuity()
    
    # Display plot points
    console.print("\n[bold]Plot Points:[/bold]")
    
    if continuity.plot_points:
        plot_table = Table(show_header=True, header_style="bold magenta")
        plot_table.add_column("Description")
        plot_table.add_column("Significance")
        plot_table.add_column("Characters")
        plot_table.add_column("Status")
        
        for point in continuity.plot_points:
            plot_table.add_row(
                point.description,
                point.significance,
                ", ".join(point.characters_involved),
                point.resolution_status
            )
        
        console.print(plot_table)
    else:
        console.print("[italic]No plot points recorded yet.[/italic]")
    
    # Display thematic developments
    console.print("\n[bold]Thematic Developments:[/bold]")
    
    if continuity.thematic_developments:
        theme_table = Table(show_header=True, header_style="bold magenta")
        theme_table.add_column("Theme")
        theme_table.add_column("Development")
        
        for theme, developments in continuity.thematic_developments.items():
            if developments:
                # Get the latest development
                latest = developments[-1]
                theme_table.add_row(theme, latest.development)
        
        console.print(theme_table)
    else:
        console.print("[italic]No thematic developments recorded yet.[/italic]")
    
    # Display pending foreshadowing
    console.print("\n[bold]Pending Foreshadowing Elements:[/bold]")
    
    pending = continuity.get_pending_foreshadowing()
    if pending:
        foreshadow_table = Table(show_header=True, header_style="bold magenta")
        foreshadow_table.add_column("Foreshadowing Element")
        foreshadow_table.add_column("Expected Payoff")
        
        for element in pending:
            foreshadow_table.add_row(element.foreshadowing, element.payoff)
        
        console.print(foreshadow_table)
    else:
        console.print("[italic]No pending foreshadowing elements recorded.[/italic]")

if __name__ == "__main__":
    main()