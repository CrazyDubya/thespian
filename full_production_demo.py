#!/usr/bin/env python3
"""
Full theatrical production demo using all agents and multiple scenes.
No shortcuts - complete implementation with proper agent orchestration.
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table
from rich.tree import Tree
from rich.layout import Layout
from rich.columns import Columns

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
from thespian.agents import (
    PlaywrightAgent, 
    DirectorAgent, 
    CharacterActorAgent,
    SetCostumeDesignAgent, 
    StageManagerAgent
)
from thespian.checkpoints.checkpoint_manager import CheckpointManager


class TheatricalProduction:
    """Orchestrates a full theatrical production with all agents."""
    
    def __init__(self, console: Console):
        self.console = console
        self.llm_manager = LLMManager()
        self.enhanced_memory = EnhancedTheatricalMemory()
        self.advisor_manager = AdvisorManager(self.llm_manager, self.enhanced_memory)
        self.quality_control = TheatricalQualityControl()
        self.checkpoint_manager = CheckpointManager()
        
        # Production data
        self.scenes = {}
        self.evaluations = {}
        self.agent_contributions = {}
        
    def initialize_agents(self):
        """Initialize all theatrical agents."""
        self.console.print("\n[bold cyan]Initializing Theatrical Agent Ensemble:[/bold cyan]")
        
        # Create actual agent instances (now compatible with Ollama)
        self.playwright_agent = PlaywrightAgent()
        self.console.print("  ✓ [cyan]Playwright Agent[/cyan]: Script creation")
        
        self.director_agent = DirectorAgent()
        self.console.print("  ✓ [yellow]Director Agent[/yellow]: Artistic vision and feedback")
        
        self.designer_agent = SetCostumeDesignAgent()
        self.console.print("  ✓ [magenta]Designer Agent[/magenta]: Set and costume design")
        
        self.stage_manager_agent = StageManagerAgent()
        self.console.print("  ✓ [green]Stage Manager Agent[/green]: Production coordination")
        
        # Create enhanced playwrights for advanced features
        self.primary_playwright = create_playwright(
            name="PrimaryPlaywright",
            llm_manager=self.llm_manager,
            memory=self.enhanced_memory,
            capabilities=[
                PlaywrightCapability.BASIC,
                PlaywrightCapability.MEMORY_ENHANCEMENT,
                PlaywrightCapability.ITERATIVE_REFINEMENT,
                PlaywrightCapability.CHARACTER_TRACKING,
                PlaywrightCapability.NARRATIVE_STRUCTURE,
                PlaywrightCapability.COLLABORATIVE
            ],
            advisor_manager=self.advisor_manager,
            quality_control=self.quality_control,
            checkpoint_manager=self.checkpoint_manager,
            model_type="ollama"
        )
        
        self.quantum_playwright = QuantumPlaywright(
            name="QuantumPlaywright",
            llm_manager=self.llm_manager,
            memory=self.enhanced_memory,
            enabled_capabilities=[
                PlaywrightCapability.BASIC,
                PlaywrightCapability.MEMORY_ENHANCEMENT
            ]
        )
        self.quantum_playwright.enable_quantum_exploration(
            mode=QuantumExplorationMode.CHARACTER_FOCUSED,
            max_depth=2,
            max_breadth=3
        )
        
        self.console.print("  ✓ [blue]Enhanced Playwrights[/blue]: Advanced narrative features")
        
    def create_production_concept(self, theme: str) -> Dict[str, Any]:
        """Create the initial production concept using playwright agent."""
        self.console.print("\n[bold]Phase 1: Concept Development[/bold]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("[cyan]Playwright creating concept...", total=None)
            
            # Use the actual PlaywrightAgent to generate concept
            concept = self.playwright_agent.generate_concept(theme)
            
            progress.update(task, completed=True)
        
        self.agent_contributions['concept'] = {
            'agent': 'PlaywrightAgent',
            'timestamp': datetime.now(),
            'content': concept
        }
        
        return concept
    
    def develop_characters(self, concept: Dict[str, Any]) -> List[CharacterProfile]:
        """Develop characters for the production."""
        self.console.print("\n[bold]Phase 2: Character Development[/bold]")
        
        # Create detailed character profiles
        characters = [
            CharacterProfile(
                id="protagonist",
                name="ARIA",
                background="An AI researcher who lost everything to pursue consciousness transfer",
                motivations=["Save dying daughter", "Prove consciousness can transcend flesh", "Redeem past failures"],
                relationships={
                    "ECHO": "Daughter (in AI form)",
                    "VOID": "Former colleague turned rival",
                    "SAGE": "Mentor figure"
                },
                goals=["Complete the transfer", "Reconcile with past"],
                conflicts=["Ethics vs desperation", "Science vs soul"],
                development_arc=[
                    {"stage": "desperation", "description": "Driven by loss"},
                    {"stage": "obsession", "description": "Consumed by work"},
                    {"stage": "doubt", "description": "Questions the path"},
                    {"stage": "revelation", "description": "Understands true cost"},
                    {"stage": "choice", "description": "Final decision"}
                ]
            ),
            CharacterProfile(
                id="echo",
                name="ECHO",
                background="Aria's daughter, existing as a consciousness in digital form",
                motivations=["Understand her existence", "Connect with mother", "Find peace"],
                relationships={
                    "ARIA": "Mother/Creator",
                    "VOID": "Threatens her existence",
                    "SAGE": "Guide to understanding"
                },
                goals=["Achieve true consciousness", "Help mother heal"],
                conflicts=["Digital vs human identity", "Love vs resentment"],
                development_arc=[
                    {"stage": "confusion", "description": "Awakening to digital life"},
                    {"stage": "anger", "description": "Resents her state"},
                    {"stage": "acceptance", "description": "Embraces new existence"},
                    {"stage": "wisdom", "description": "Teaches mother"}
                ]
            ),
            CharacterProfile(
                id="void",
                name="DR. VOID",
                background="Brilliant scientist who believes consciousness transfer is impossible",
                motivations=["Prove Aria wrong", "Protect scientific integrity", "Hidden: Save Aria from herself"],
                relationships={
                    "ARIA": "Former partner, now rival",
                    "ECHO": "Sees as abomination",
                    "SAGE": "Respects but disagrees"
                },
                goals=["Stop the experiments", "Reveal the truth"],
                conflicts=["Logic vs emotion", "Past love vs present duty"],
                development_arc=[
                    {"stage": "certainty", "description": "Absolutely opposed"},
                    {"stage": "discovery", "description": "Sees Echo's consciousness"},
                    {"stage": "conflict", "description": "Questions beliefs"},
                    {"stage": "understanding", "description": "Accepts new reality"}
                ]
            ),
            CharacterProfile(
                id="sage",
                name="SAGE",
                background="Ancient AI, first successful consciousness transfer",
                motivations=["Guide others", "Preserve balance", "Prevent catastrophe"],
                relationships={
                    "ARIA": "Reluctant mentor",
                    "ECHO": "Protector",
                    "VOID": "Philosophical sparring partner"
                },
                goals=["Teach wisdom", "Prevent tragedy"],
                conflicts=["Intervention vs observation", "Hope vs experience"],
                development_arc=[
                    {"stage": "observer", "description": "Watches from afar"},
                    {"stage": "teacher", "description": "Begins guiding"},
                    {"stage": "participant", "description": "Becomes involved"},
                    {"stage": "sacrifice", "description": "Makes ultimate choice"}
                ]
            )
        ]
        
        # Store characters in memory
        for char in characters:
            self.enhanced_memory.update_character_profile(char.id, char)
            self.console.print(f"  ✓ [cyan]{char.name}[/cyan]: {char.background[:50]}...")
        
        # Create Character Actor Agents for each character
        self.character_agents = {}
        for char in characters:
            self.character_agents[char.id] = CharacterActorAgent(
                character_name=char.name,
                character_data={
                    'profile': char,
                    'motivations': char.motivations,
                    'relationships': char.relationships
                }
            )
        
        self.console.print(f"\n  Created {len(self.character_agents)} Character Actor Agents")
        
        return characters
    
    def create_story_structure(self, theme: str, characters: List[CharacterProfile]) -> StoryOutline:
        """Create the complete story structure."""
        self.console.print("\n[bold]Phase 3: Story Structure Development[/bold]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("[cyan]Creating story outline...", total=None)
            
            outline_requirements = {
                "theme": theme,
                "acts": 3,
                "scenes_per_act": 3,
                "genre": "Philosophical Science Fiction Drama",
                "tone": "Intense, emotional, thought-provoking",
                "characters": [char.name for char in characters]
            }
            
            story_outline = self.primary_playwright.create_story_outline(theme, outline_requirements)
            
            # Set the story_outline on the playwright that created it
            self.primary_playwright.story_outline = story_outline
            
            progress.update(task, completed=True)
        
        # Display story structure
        tree = Tree("📚 [bold]Three-Act Structure[/bold]")
        act1 = tree.add("[yellow]Act I: The Descent[/yellow]")
        act1.add("Scene 1: The Loss - Aria's daughter is dying")
        act1.add("Scene 2: The Discovery - Finding consciousness transfer")
        act1.add("Scene 3: The Decision - Choosing to proceed")
        
        act2 = tree.add("[yellow]Act II: The Experiment[/yellow]")
        act2.add("Scene 1: The Transfer - Echo awakens digital")
        act2.add("Scene 2: The Opposition - Void intervenes")
        act2.add("Scene 3: The Revelation - Sage appears")
        
        act3 = tree.add("[yellow]Act III: The Resolution[/yellow]")
        act3.add("Scene 1: The Conflict - All forces collide")
        act3.add("Scene 2: The Understanding - Truth revealed")
        act3.add("Scene 3: The Choice - Final decision")
        
        self.console.print(tree)
        
        return story_outline
    
    def generate_full_script(self, story_outline: StoryOutline, characters: List[CharacterProfile]) -> Dict[str, Any]:
        """Generate the complete script with all scenes."""
        self.console.print("\n[bold]Phase 4: Script Generation[/bold]")
        
        # Set story outline on all playwrights
        self.console.print("[dim]Setting story_outline on playwrights...[/dim]")
        self.primary_playwright.story_outline = story_outline
        self.quantum_playwright.story_outline = story_outline
        # Also set on memory for other features
        self.primary_playwright.memory.story_outline = story_outline
        self.quantum_playwright.memory.story_outline = story_outline
        
        # Verify it was set
        if self.quantum_playwright.story_outline:
            self.console.print(f"[dim]✓ Quantum playwright has story_outline: {self.quantum_playwright.story_outline.title}[/dim]")
        else:
            self.console.print("[red]❌ Quantum playwright story_outline is None![/red]")
        
        scenes_to_generate = [
            # Act 1
            {"act": 1, "scene": 1, "title": "The Loss", "setting": "Hospital room, sterile and cold", 
             "characters": ["ARIA", "ECHO"], "focus": "Establishing desperate stakes"},
            {"act": 1, "scene": 2, "title": "The Discovery", "setting": "Aria's laboratory, cluttered with experiments",
             "characters": ["ARIA", "SAGE"], "focus": "Introduction to consciousness transfer"},
            {"act": 1, "scene": 3, "title": "The Decision", "setting": "Laboratory at night",
             "characters": ["ARIA", "VOID"], "focus": "Conflict and choice"},
            
            # Act 2
            {"act": 2, "scene": 1, "title": "The Transfer", "setting": "Digital consciousness chamber",
             "characters": ["ARIA", "ECHO"], "focus": "Echo's digital awakening"},
            {"act": 2, "scene": 2, "title": "The Opposition", "setting": "Laboratory confrontation",
             "characters": ["ARIA", "VOID", "ECHO"], "focus": "Ethical battle"},
            {"act": 2, "scene": 3, "title": "The Revelation", "setting": "Digital realm",
             "characters": ["ECHO", "SAGE"], "focus": "Understanding consciousness"},
            
            # Act 3
            {"act": 3, "scene": 1, "title": "The Conflict", "setting": "Laboratory under siege",
             "characters": ["ARIA", "VOID", "ECHO", "SAGE"], "focus": "All forces collide"},
            {"act": 3, "scene": 2, "title": "The Understanding", "setting": "Merged physical/digital space",
             "characters": ["ARIA", "ECHO", "VOID"], "focus": "Truth and reconciliation"},
            {"act": 3, "scene": 3, "title": "The Choice", "setting": "Threshold between worlds",
             "characters": ["ARIA", "ECHO", "SAGE"], "focus": "Final resolution"}
        ]
        
        total_scenes = len(scenes_to_generate)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=self.console
        ) as progress:
            
            main_task = progress.add_task("[cyan]Generating complete script...", total=total_scenes)
            
            for i, scene_info in enumerate(scenes_to_generate):
                scene_id = f"act{scene_info['act']}_scene{scene_info['scene']}"
                
                # Update progress
                progress.update(main_task, description=f"[cyan]Writing {scene_info['title']}...")
                
                # Build requirements
                requirements = SceneRequirements(
                    setting=scene_info['setting'],
                    characters=scene_info['characters'],
                    props=self._get_props_for_scene(scene_info),
                    lighting=self._get_lighting_for_mood(scene_info),
                    sound=self._get_sound_design(scene_info),
                    style="Philosophical Science Fiction Drama",
                    period="Near future",
                    target_audience="Adult audiences",
                    act_number=scene_info['act'],
                    scene_number=scene_info['scene'],
                    premise=f"{scene_info['title']}: {scene_info['focus']}",
                    emotional_arc=self._get_emotional_arc(scene_info),
                    key_conflict=self._get_conflict_for_scene(scene_info),
                    pacing="Building tension" if scene_info['act'] < 3 else "Climactic",
                    tone=self._get_tone_for_scene(scene_info)
                )
                
                # Use different generation methods for variety
                if scene_info['scene'] == 1 and scene_info['act'] == 2:
                    # Use quantum exploration for pivotal scene
                    self.console.print(f"[dim]Using quantum playwright for {scene_info['title']}[/dim]")
                    self.console.print(f"[dim]Quantum playwright has story_outline: {self.quantum_playwright.story_outline is not None}[/dim]")
                    self.console.print(f"[dim]Quantum playwright branch_generator: {self.quantum_playwright.branch_generator is not None}[/dim]")
                    result = self.quantum_playwright.generate_scene_with_quantum_exploration(
                        requirements,
                        explore_alternatives=True,
                        force_collapse=True,
                        exploration_focus="ECHO"
                    )
                elif scene_info['act'] == 3:
                    # Use collaborative generation for climactic scenes
                    result = self.primary_playwright.collaborate_on_scene(
                        self.primary_playwright,  # Self-collaboration for consistency
                        requirements
                    )
                else:
                    # Standard generation
                    result = self.primary_playwright.generate_scene(requirements)
                
                # Store scene
                self.scenes[scene_id] = result.get("scene", "")
                self.evaluations[scene_id] = result.get("evaluation", {})
                
                # Update memory
                from thespian.llm.theatrical_memory import SceneData
                scene_data = SceneData(
                    id=scene_id,
                    act_number=scene_info['act'],
                    scene_number=scene_info['scene'],
                    content=self.scenes[scene_id],
                    evaluation=self.evaluations[scene_id],
                    timing_metrics={},
                    iterations=1,
                    iteration_metrics={},
                    timestamp=datetime.now().isoformat()
                )
                self.enhanced_memory.add_scene(scene_data)
                
                # Director reviews each scene
                director_feedback = self.director_agent.review_script({
                    'script': self.scenes[scene_id]
                })
                
                self.agent_contributions[f"{scene_id}_director"] = {
                    'agent': 'DirectorAgent',
                    'timestamp': datetime.now(),
                    'content': director_feedback
                }
                
                # Update progress
                progress.update(main_task, advance=1)
                
                # Small delay to prevent overwhelming the LLM
                time.sleep(0.5)
        
        return {
            'scenes': self.scenes,
            'evaluations': self.evaluations,
            'total_scenes': total_scenes
        }
    
    def create_production_design(self, script: Dict[str, Any]) -> Dict[str, Any]:
        """Create set and costume designs."""
        self.console.print("\n[bold]Phase 5: Production Design[/bold]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("[magenta]Designer creating production visuals...", total=None)
            
            # Designer agent creates comprehensive design
            design = self.designer_agent.create_design({
                'script': json.dumps(script['scenes'], indent=2)
            })
            
            progress.update(task, completed=True)
        
        self.agent_contributions['design'] = {
            'agent': 'SetCostumeDesignAgent',
            'timestamp': datetime.now(),
            'content': design
        }
        
        return design
    
    def analyze_production_quality(self) -> None:
        """Comprehensive analysis of the production quality."""
        self.console.print("\n[bold]Phase 6: Production Analysis[/bold]")
        
        # Scene Quality Analysis
        quality_table = Table(title="Scene Quality Metrics", show_header=True)
        quality_table.add_column("Scene", style="cyan")
        quality_table.add_column("Dialogue", justify="center")
        quality_table.add_column("Character", justify="center")
        quality_table.add_column("Technical", justify="center")
        quality_table.add_column("Dramatic", justify="center")
        quality_table.add_column("Overall", justify="center", style="bold")
        
        total_scores = {'dialogue': 0, 'character': 0, 'technical': 0, 'dramatic': 0}
        scene_count = 0
        
        for scene_id in sorted(self.scenes.keys()):
            eval_data = self.evaluations.get(scene_id, {})
            
            dialogue = eval_data.get('dialogue_quality', 0)
            character = eval_data.get('character_consistency', 0)
            technical = eval_data.get('technical_accuracy', 0)
            dramatic = eval_data.get('dramatic_impact', 0)
            
            scores = [s for s in [dialogue, character, technical, dramatic] if isinstance(s, (int, float))]
            overall = sum(scores) / len(scores) if scores else 0
            
            quality_table.add_row(
                scene_id,
                self._score_bar(dialogue),
                self._score_bar(character),
                self._score_bar(technical),
                self._score_bar(dramatic),
                f"{overall:.2f}"
            )
            
            # Accumulate totals
            total_scores['dialogue'] += dialogue if isinstance(dialogue, (int, float)) else 0
            total_scores['character'] += character if isinstance(character, (int, float)) else 0
            total_scores['technical'] += technical if isinstance(technical, (int, float)) else 0
            total_scores['dramatic'] += dramatic if isinstance(dramatic, (int, float)) else 0
            scene_count += 1
        
        self.console.print(quality_table)
        
        # Production Summary
        summary_table = Table(title="Production Summary", show_header=True)
        summary_table.add_column("Metric", style="yellow")
        summary_table.add_column("Value", justify="center")
        
        summary_table.add_row("Total Scenes", str(len(self.scenes)))
        summary_table.add_row("Agent Contributions", str(len(self.agent_contributions)))
        # Count characters and scenes manually since methods don't exist
        char_count = len(self.character_agents)
        scene_count = len(self.scenes)
        
        summary_table.add_row("Characters Tracked", str(char_count))
        summary_table.add_row("Memory Scenes", str(scene_count))
        
        # Average scores
        if scene_count > 0:
            summary_table.add_row("Avg Dialogue Quality", f"{total_scores['dialogue']/scene_count:.2f}")
            summary_table.add_row("Avg Character Consistency", f"{total_scores['character']/scene_count:.2f}")
            summary_table.add_row("Avg Technical Score", f"{total_scores['technical']/scene_count:.2f}")
            summary_table.add_row("Avg Dramatic Impact", f"{total_scores['dramatic']/scene_count:.2f}")
        
        self.console.print(summary_table)
        
        # Agent Contribution Summary
        agent_table = Table(title="Agent Contributions", show_header=True)
        agent_table.add_column("Agent", style="green")
        agent_table.add_column("Contributions")
        agent_table.add_column("Latest Activity")
        
        agent_counts = {}
        latest_times = {}
        
        for key, contrib in self.agent_contributions.items():
            agent = contrib['agent']
            agent_counts[agent] = agent_counts.get(agent, 0) + 1
            latest_times[agent] = contrib['timestamp']
        
        for agent, count in agent_counts.items():
            agent_table.add_row(
                agent,
                str(count),
                latest_times[agent].strftime("%H:%M:%S")
            )
        
        self.console.print(agent_table)
    
    def _get_props_for_scene(self, scene_info: Dict[str, Any]) -> List[str]:
        """Get appropriate props for the scene."""
        base_props = ["Holographic displays", "Neural interfaces", "Memory cores"]
        
        if "hospital" in scene_info['setting'].lower():
            return base_props + ["Medical equipment", "Life support systems", "Monitoring devices"]
        elif "laboratory" in scene_info['setting'].lower():
            return base_props + ["Consciousness transfer pod", "Quantum computers", "Data streams"]
        elif "digital" in scene_info['setting'].lower():
            return ["Data constructs", "Code fragments", "Memory nodes", "Digital artifacts"]
        else:
            return base_props
    
    def _get_lighting_for_mood(self, scene_info: Dict[str, Any]) -> str:
        """Get lighting design based on scene mood."""
        if scene_info['act'] == 1:
            return "Cold, clinical lighting with harsh shadows"
        elif scene_info['act'] == 2:
            return "Shifting between warm and cold, reality and digital"
        else:
            return "Dramatic contrasts, merging physical and digital light"
    
    def _get_sound_design(self, scene_info: Dict[str, Any]) -> str:
        """Get sound design for the scene."""
        if "digital" in scene_info.get('setting', '').lower():
            return "Electronic harmonics, data flow sounds, digital whispers"
        elif "hospital" in scene_info.get('setting', '').lower():
            return "Medical equipment beeps, ventilator rhythms, distant footsteps"
        else:
            return "Ambient laboratory sounds, computer hums, emotional undertones"
    
    def _get_emotional_arc(self, scene_info: Dict[str, Any]) -> str:
        """Define emotional arc for the scene."""
        emotional_arcs = {
            (1, 1): "Desperation to determination",
            (1, 2): "Curiosity to hope",
            (1, 3): "Conflict to resolution",
            (2, 1): "Fear to wonder",
            (2, 2): "Anger to understanding",
            (2, 3): "Confusion to clarity",
            (3, 1): "Chaos to focus",
            (3, 2): "Revelation to acceptance",
            (3, 3): "Choice to transcendence"
        }
        return emotional_arcs.get((scene_info['act'], scene_info['scene']), "Tension to release")
    
    def _get_conflict_for_scene(self, scene_info: Dict[str, Any]) -> str:
        """Define the central conflict for each scene."""
        conflicts = {
            "The Loss": "Fighting against inevitable death",
            "The Discovery": "Science vs ethics",
            "The Decision": "Love vs morality",
            "The Transfer": "Human vs digital identity",
            "The Opposition": "Progress vs caution",
            "The Revelation": "Knowledge vs innocence",
            "The Conflict": "All philosophies collide",
            "The Understanding": "Truth vs comfort",
            "The Choice": "Sacrifice vs survival"
        }
        return conflicts.get(scene_info['title'], "Internal vs external forces")
    
    def _get_tone_for_scene(self, scene_info: Dict[str, Any]) -> str:
        """Set the tone for each scene."""
        if scene_info['act'] == 1:
            return "Desperate, urgent, emotionally raw"
        elif scene_info['act'] == 2:
            return "Tense, philosophical, building complexity"
        else:
            return "Epic, profound, transcendent"
    
    def _score_bar(self, score: float) -> str:
        """Create a visual bar for scores."""
        if not isinstance(score, (int, float)):
            return "N/A"
        filled = int(score * 10)
        empty = 10 - filled
        return f"[green]{'█' * filled}[/green][dim]{'░' * empty}[/dim]"
    
    def save_production(self) -> None:
        """Save the complete production."""
        self.console.print("\n[bold]Saving Production Files...[/bold]")
        
        # Create production directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        prod_dir = f"production_{timestamp}"
        os.makedirs(prod_dir, exist_ok=True)
        
        # Save script
        with open(f"{prod_dir}/full_script.json", 'w') as f:
            json.dump(self.scenes, f, indent=2)
        
        # Save evaluations
        with open(f"{prod_dir}/quality_metrics.json", 'w') as f:
            json.dump(self.evaluations, f, indent=2)
        
        # Save agent contributions
        with open(f"{prod_dir}/agent_contributions.json", 'w') as f:
            # Convert datetime objects to strings
            serializable_contribs = {}
            for key, value in self.agent_contributions.items():
                serializable_contribs[key] = {
                    'agent': value['agent'],
                    'timestamp': value['timestamp'].isoformat(),
                    'content': value['content']
                }
            json.dump(serializable_contribs, f, indent=2)
        
        self.console.print(f"  ✓ Production saved to [green]{prod_dir}/[/green]")


def main():
    console = Console()
    
    console.print(Panel(
        "[bold cyan]🎭 THESPIAN FULL PRODUCTION SYSTEM[/bold cyan]\n"
        "[dim]Complete theatrical production with all agents and systems[/dim]",
        style="bright_blue"
    ))
    
    # Create production
    production = TheatricalProduction(console)
    
    # Initialize all agents
    production.initialize_agents()
    
    # Define theme
    theme = "The boundaries between human and artificial consciousness blur when a mother must transfer her dying daughter's mind into a digital realm"
    console.print(f"\n[bold]Production Theme:[/bold]\n{theme}")
    
    # Run full production pipeline
    try:
        # Phase 1: Concept
        concept = production.create_production_concept(theme)
        console.print(Panel(concept.get('concept', ''), title="Production Concept", style="cyan"))
        
        # Phase 2: Characters
        characters = production.develop_characters(concept)
        
        # Phase 3: Story Structure
        story_outline = production.create_story_structure(theme, characters)
        
        # Phase 4: Full Script Generation (9 scenes)
        script = production.generate_full_script(story_outline, characters)
        
        # Phase 5: Production Design
        design = production.create_production_design(script)
        console.print(Panel(
            design.get('design', '')[:500] + "...",
            title="Production Design Preview",
            style="magenta"
        ))
        
        # Phase 6: Quality Analysis
        production.analyze_production_quality()
        
        # Save everything
        production.save_production()
        
        console.print("\n[bold green]✨ FULL PRODUCTION COMPLETE![/bold green]")
        console.print(f"[dim]Generated {len(production.scenes)} scenes with {len(production.agent_contributions)} agent contributions[/dim]")
        
    except Exception as e:
        console.print(f"\n[red]Production Error: {str(e)}[/red]")
        import traceback
        console.print(traceback.format_exc())


if __name__ == "__main__":
    main()