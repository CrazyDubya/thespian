#!/usr/bin/env python3
"""
Variable Quantum Narrative Demo - Configurable Multi-Character Exploration

This demo creates a TRULY variable quantum exploration system:
- 4 characters with rich psychological profiles
- Variable exploration intensity: 1-3 branches per dimension
- Configurable depth and breadth parameters
- True iterative multi-level exploration
- Expert agent integration at each level
- Parallel exploration tracks
"""

import os
import sys
from pathlib import Path
import time
import random
from typing import Dict, Any, List, Optional

# Add paths
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent / "thespian"))

# Import quantum framework components
from llm.quantum_narrative import (
    QuantumNarrativeTree, 
    NarrativeQuantumState,
    QuantumBranchGenerator,
    CollapseTrigger
)
from llm.quantum_playwright import QuantumPlaywright
from pydantic import Field

class VariableQuantumExplorer:
    """Variable quantum exploration with configurable parameters."""
    
    def __init__(self, exploration_intensity: int = 2):
        """
        Initialize with configurable exploration intensity.
        
        Args:
            exploration_intensity: 1-3, controls how many branches per dimension
                1 = Light exploration (1 branch per dimension)
                2 = Moderate exploration (2 branches per dimension) 
                3 = Heavy exploration (3 branches per dimension)
        """
        self.exploration_intensity = max(1, min(3, exploration_intensity))
        self.total_llm_calls = 0
        self.total_branches = 0
        self.exploration_levels = []
        
    def run_variable_quantum_exploration(self):
        """Run variable quantum exploration with 4 characters."""
        
        print(f"🌀 VARIABLE QUANTUM EXPLORATION")
        print(f"Exploration Intensity: {self.exploration_intensity}/3")
        print(f"Expected branches per level: {self.calculate_expected_branches()}")
        print("="*60)
        
        # Check API keys
        api_keys = {
            'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
            'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY'),
            'XAI_API_KEY': os.getenv('XAI_API_KEY')
        }
        
        available = {k: v for k, v in api_keys.items() if v}
        if not available:
            print("❌ NO API KEYS FOUND")
            sys.exit(1)
        
        print(f"🔑 Using APIs: {list(available.keys())}")
        
        # Import components
        try:
            from thespian.llm.manager import LLMManager
            from thespian.llm.enhanced_memory import EnhancedTheatricalMemory, EnhancedCharacterProfile
            from thespian.llm.quantum_playwright import QuantumPlaywright, QuantumExplorationMode
            from thespian.llm.consolidated_playwright import PlaywrightCapability, SceneRequirements
            from thespian.llm.theatrical_memory import StoryOutline
        except Exception as e:
            print(f"❌ Import failed: {e}")
            sys.exit(1)
        
        print("✓ All components imported")
        
        # Initialize systems
        llm_manager = LLMManager()
        memory = EnhancedTheatricalMemory()
        
        # Create 4 rich characters
        characters = self.create_four_character_universe(memory, EnhancedCharacterProfile)
        print(f"✓ Created 4 characters: {list(characters.keys())}")
        
        # Create complex story
        story_outline = self.create_multi_character_story(StoryOutline)
        
        # Initialize quantum playwright with custom tracking
        quantum_playwright = VariableQuantumPlaywright(
            name="variable_quantum",
            llm_manager=llm_manager,
            memory=memory,
            story_outline=story_outline,
            exploration_intensity=self.exploration_intensity,
            enabled_capabilities=[
                PlaywrightCapability.BASIC,
                PlaywrightCapability.MEMORY_ENHANCEMENT,
                PlaywrightCapability.CHARACTER_TRACKING,
                PlaywrightCapability.NARRATIVE_STRUCTURE
            ]
        )
        
        # Enable variable quantum exploration
        quantum_playwright.enable_quantum_exploration(
            mode=QuantumExplorationMode.FULL_EXPLORATION,
            max_depth=4,  # 4 levels for thorough exploration
            max_breadth=20  # Allow many branches per level
        )
        
        print(f"✓ Variable quantum playwright initialized")
        
        # Create demanding 4-character scene
        scene_requirements = SceneRequirements(
            setting="Community center meeting room after heated town hall about pipeline, 10 PM",
            characters=["MAYA", "DAVID", "ELENA", "DR_PATEL"],
            props=["protest signs", "legal documents", "environmental reports", "microphone", "folding chairs"],
            lighting="Harsh fluorescent lighting, dramatic shadows",
            style="Multi-character ensemble drama with overlapping dialogue",
            period="Present day",
            act_number=2,
            scene_number=5,
            premise="Four key figures with opposing views must negotiate after public confrontation over pipeline project",
            key_conflict="Environmental protection vs economic development vs legal obligations vs community safety",
            emotional_arc="Heated argument through strategic negotiation to fragile compromise",
            sound="Distant traffic noise, air conditioning hum, occasional chair scraping",
            target_audience="Adult audiences interested in environmental and social justice themes"
        )
        
        print(f"\n🎭 4-CHARACTER SCENE SETUP:")
        print(f"Characters: {', '.join(scene_requirements.characters)}")
        print(f"Central Conflict: {scene_requirements.key_conflict}")
        
        # Run variable exploration
        start_time = time.time()
        
        def variable_progress_callback(data):
            phase = data.get('phase', 'unknown')
            message = data.get('message', '')
            level = data.get('level', 0)
            character = data.get('character', '')
            
            if character:
                print(f"  [L{level}] {character}: {message}")
            else:
                print(f"  [{phase.upper()}] {message}")
        
        print(f"\n🚀 STARTING VARIABLE QUANTUM EXPLORATION")
        
        result = quantum_playwright.generate_variable_quantum_scene(
            requirements=scene_requirements,
            progress_callback=variable_progress_callback
        )
        
        exploration_time = time.time() - start_time
        
        # Report results
        print(f"\n✨ VARIABLE EXPLORATION COMPLETE!")
        print(f"Total time: {exploration_time:.1f} seconds")
        print(f"Total LLM calls: {quantum_playwright.llm_call_count}")
        print(f"Total branches: {quantum_playwright.total_branches_generated}")
        print(f"Exploration levels: {quantum_playwright.levels_explored}")
        
        # Show level-by-level breakdown
        if hasattr(quantum_playwright, 'level_breakdown'):
            print(f"\n📊 LEVEL-BY-LEVEL BREAKDOWN:")
            for level, data in quantum_playwright.level_breakdown.items():
                print(f"Level {level}: {data['branches']} branches, {data['llm_calls']} LLM calls")
        
        # Final scene
        if result and 'final_scene' in result:
            print(f"\n🎭 FINAL SCENE PREVIEW:")
            content = result['final_scene'].get('content', '')
            print(content[:400] + "..." if len(content) > 400 else content)
        
        return result
    
    def calculate_expected_branches(self):
        """Calculate expected branches per level based on intensity."""
        # 4 characters × intensity branches each = character branches
        character_branches = 4 * self.exploration_intensity
        
        # 3 thematic dimensions × intensity branches each = thematic branches  
        thematic_branches = 3 * self.exploration_intensity
        
        # 4 structural focuses × intensity branches each = structural branches
        structural_branches = 4 * self.exploration_intensity
        
        total_per_level = character_branches + thematic_branches + structural_branches
        return total_per_level
    
    def create_four_character_universe(self, memory, EnhancedCharacterProfile):
        """Create 4 rich characters for the scene."""
        
        # MAYA - Environmental Activist
        maya = EnhancedCharacterProfile(
            id="maya",
            name="MAYA",
            description="Passionate environmental activist, community organizer",
            background="25-year-old environmental justice advocate who lost her mother to pollution-related illness",
            motivations=["Prevent environmental health tragedies", "Honor mother's memory", "Build sustainable community"],
            goals=["Stop pipeline project", "Unite diverse opposition", "Create lasting policy change"],
            conflicts=["Individual action vs collective organizing", "Idealism vs pragmatic compromise"],
            relationships={
                "DAVID": "Childhood friend now representing opposing interests",
                "ELENA": "Close ally in immigrant rights movement", 
                "DR_PATEL": "Academic mentor and research partner"
            }
        )
        maya.fears = ["Failing community", "Becoming like absent father", "Losing moral clarity"]
        maya.desires = ["Environmental justice", "Community healing", "Personal redemption"]
        maya.values = ["Environmental protection", "Social justice", "Intergenerational responsibility"]
        
        # DAVID - Corporate Lawyer
        david = EnhancedCharacterProfile(
            id="david",
            name="DAVID",
            description="Corporate environmental lawyer torn between duty and conscience",
            background="26-year-old Mexican-American lawyer representing pipeline company while questioning his role",
            motivations=["Financial security for family", "Professional advancement", "Ethical practice"],
            goals=["Complete legal representation", "Maintain friendship with Maya", "Find moral middle ground"],
            conflicts=["Professional duty vs personal values", "Economic need vs environmental concern"],
            relationships={
                "MAYA": "Childhood friend whose activism challenges his choices",
                "ELENA": "Reminds him of his community roots",
                "DR_PATEL": "Respected academic whose research complicates his case"
            }
        )
        david.fears = ["Poverty like his childhood", "Losing Maya's respect", "Moral compromise"]
        david.desires = ["Financial stability", "Ethical clarity", "Community acceptance"]
        david.values = ["Family loyalty", "Professional competence", "Cultural identity"]
        
        # ELENA - Immigrant Rights Organizer  
        elena = EnhancedCharacterProfile(
            id="elena",
            name="ELENA",
            description="Undocumented immigrant rights organizer building coalitions",
            background="30-year-old Salvadoran organizer connecting environmental and immigrant justice",
            motivations=["Protect vulnerable communities", "Build political power", "Secure family safety"],
            goals=["Prevent displacement from pipeline", "Expand coalition influence", "Achieve immigration reform"],
            conflicts=["Personal safety vs public activism", "Ideological purity vs political pragmatism"],
            relationships={
                "MAYA": "Trusted ally in intersectional organizing",
                "DAVID": "Suspicious of but willing to work with",
                "DR_PATEL": "Academic ally who provides research legitimacy"
            }
        )
        elena.fears = ["Deportation", "Community fragmentation", "Betrayal by allies"]
        elena.desires = ["Legal status", "Community power", "Intergenerational justice"]
        elena.values = ["Solidarity", "Collective liberation", "Cultural preservation"]
        
        # DR_PATEL - Environmental Health Researcher
        dr_patel = EnhancedCharacterProfile(
            id="dr_patel",
            name="DR_PATEL",
            description="Environmental health researcher documenting pollution impacts",
            background="45-year-old public health professor whose research reveals pipeline health risks",
            motivations=["Scientific integrity", "Public health protection", "Academic responsibility"],
            goals=["Complete rigorous research", "Inform policy decisions", "Protect scientific independence"],
            conflicts=["Academic objectivity vs advocacy", "Research timeline vs political urgency"],
            relationships={
                "MAYA": "Mentee and activist she guides",
                "DAVID": "Professional acquaintance whose legal strategy she must counter",
                "ELENA": "Community partner whose lived experience enriches her research"
            }
        )
        dr_patel.fears = ["Research being misused", "Academic retaliation", "Community disappointment"]
        dr_patel.desires = ["Scientific truth", "Policy influence", "Community wellbeing"]
        dr_patel.values = ["Scientific rigor", "Public service", "Environmental stewardship"]
        
        # Add all characters to memory
        characters = {"maya": maya, "david": david, "elena": elena, "dr_patel": dr_patel}
        for char_id, char_profile in characters.items():
            memory.update_character_profile(char_id, char_profile)
        
        return characters
    
    def create_multi_character_story(self, StoryOutline):
        """Create story outline for 4-character narrative."""
        acts_data = [
            {
                "act_number": 2,
                "description": "The negotiation - Four perspectives clash and seek resolution",
                "key_events": [
                    "Public town hall reveals deep divisions",
                    "Private negotiations between key figures", 
                    "Research evidence complicates simple positions",
                    "Coalition building across unexpected alliances",
                    "Fragile compromise emerges from conflict"
                ],
                "status": "in_progress"
            }
        ]
        
        story_outline = StoryOutline(title="The Four-Way Negotiation", acts=acts_data)
        story_outline.themes = [
            "Environmental justice meets economic development",
            "Professional duty vs personal conscience", 
            "Individual action vs collective organizing",
            "Academic research vs political activism"
        ]
        story_outline.characters = ["MAYA", "DAVID", "ELENA", "DR_PATEL"]
        
        return story_outline


class VariableQuantumPlaywright(QuantumPlaywright):
    """Extended quantum playwright with variable exploration."""
    
    exploration_intensity: int = Field(default=2, ge=1, le=3)
    total_branches_generated: int = Field(default=0)
    levels_explored: int = Field(default=0)
    level_breakdown: Dict[str, Any] = Field(default_factory=dict)
        
    def generate_variable_quantum_scene(self, requirements, progress_callback=None):
        """Generate scene with variable quantum exploration."""
        
        if progress_callback:
            progress_callback({"phase": "initialization", "message": "Starting variable quantum exploration"})
        
        # Initialize quantum tree
        self.quantum_tree.clear_all_branches()
        initial_state = self._create_initial_quantum_state(requirements)
        self.quantum_tree.add_root_branch(initial_state)
        
        # Run iterative exploration for each level
        for level in range(self.max_exploration_depth):
            self.levels_explored = level + 1
            
            if progress_callback:
                progress_callback({"phase": "exploration", "level": level, "message": f"Exploring level {level+1}"})
            
            level_stats = self._explore_level(level, requirements, progress_callback)
            self.level_breakdown[level] = level_stats
            
            # Stop if no new branches generated
            if level_stats['branches'] == 0:
                break
        
        # Select best path and collapse
        if progress_callback:
            progress_callback({"phase": "collapse", "message": "Selecting optimal narrative path"})
        
        final_result = self._collapse_to_best_path()
        
        return {
            "final_scene": final_result,
            "exploration_stats": {
                "total_llm_calls": self.llm_call_count,
                "total_branches": self.total_branches_generated,
                "levels_explored": self.levels_explored,
                "level_breakdown": self.level_breakdown
            }
        }
    
    def _explore_level(self, level, requirements, progress_callback):
        """Explore all branches at a specific level."""
        level_llm_calls = self.llm_call_count
        level_branches = 0
        
        # Get current branches at this level
        current_branches = [b for b in self.quantum_tree.active_branches.values() 
                          if b.depth_level == level]
        
        if not current_branches:
            return {"branches": 0, "llm_calls": 0}
        
        # For each current branch, generate variable number of new branches
        for branch in current_branches:
            # Character-focused exploration (variable per character)
            for character in requirements.characters:
                branch_count = self._generate_variable_character_branches(
                    branch, character, requirements, level, progress_callback
                )
                level_branches += branch_count
            
            # Thematic exploration (variable per theme)
            theme_count = self._generate_variable_thematic_branches(
                branch, requirements, level, progress_callback
            )
            level_branches += theme_count
            
            # Structural exploration (variable per structure)
            struct_count = self._generate_variable_structural_branches(
                branch, requirements, level, progress_callback
            )
            level_branches += struct_count
        
        level_llm_calls = self.llm_call_count - level_llm_calls
        self.total_branches_generated += level_branches
        
        return {"branches": level_branches, "llm_calls": level_llm_calls}
    
    def _generate_variable_character_branches(self, parent_branch, character, requirements, level, progress_callback):
        """Generate variable number of character psychology branches."""
        psychology_types = ["fear_driven", "desire_driven", "values_driven", "attachment_driven"]
        
        # Select random subset based on exploration intensity
        selected_types = random.sample(psychology_types, min(self.exploration_intensity, len(psychology_types)))
        
        branches_created = 0
        for psych_type in selected_types:
            if progress_callback:
                progress_callback({
                    "phase": "character_generation", 
                    "level": level,
                    "character": character,
                    "message": f"Generating {psych_type} branch"
                })
            
            # Create character-specific prompt
            prompt = self._create_character_psychology_prompt(character, psych_type, parent_branch, requirements)
            
            try:
                response = self.tracked_llm_invoke(prompt)
                new_branch = self._create_branch_from_response(
                    response, parent_branch, f"{character} {psych_type} response", "character_decision"
                )
                
                if self.quantum_tree.add_branch(parent_branch.branch_id, new_branch):
                    branches_created += 1
                    
            except Exception as e:
                if progress_callback:
                    progress_callback({"phase": "error", "message": f"Error generating {character} {psych_type}: {e}"})
        
        return branches_created
    
    def _generate_variable_thematic_branches(self, parent_branch, requirements, level, progress_callback):
        """Generate variable number of thematic exploration branches."""
        thematic_approaches = ["emphasis", "synthesis", "paradox"]
        
        # Select random subset based on exploration intensity
        selected_approaches = random.sample(thematic_approaches, min(self.exploration_intensity, len(thematic_approaches)))
        
        branches_created = 0
        for approach in selected_approaches:
            if progress_callback:
                progress_callback({
                    "phase": "thematic_generation",
                    "level": level, 
                    "message": f"Generating {approach} thematic branch"
                })
            
            prompt = self._create_thematic_prompt(approach, parent_branch, requirements)
            
            try:
                response = self.tracked_llm_invoke(prompt)
                new_branch = self._create_branch_from_response(
                    response, parent_branch, f"Thematic {approach} exploration", "thematic_exploration"
                )
                
                if self.quantum_tree.add_branch(parent_branch.branch_id, new_branch):
                    branches_created += 1
                    
            except Exception as e:
                if progress_callback:
                    progress_callback({"phase": "error", "message": f"Error generating thematic {approach}: {e}"})
        
        return branches_created
    
    def _generate_variable_structural_branches(self, parent_branch, requirements, level, progress_callback):
        """Generate variable number of structural branches."""
        structural_focuses = ["tension_escalation", "emotional_revelation", "relationship_shift", "plot_advancement"]
        
        # Select random subset based on exploration intensity  
        selected_focuses = random.sample(structural_focuses, min(self.exploration_intensity, len(structural_focuses)))
        
        branches_created = 0
        for focus in selected_focuses:
            if progress_callback:
                progress_callback({
                    "phase": "structural_generation",
                    "level": level,
                    "message": f"Generating {focus} structural branch"
                })
            
            prompt = self._create_structural_prompt(focus, parent_branch, requirements)
            
            try:
                response = self.tracked_llm_invoke(prompt)
                new_branch = self._create_branch_from_response(
                    response, parent_branch, f"Structural {focus}", "dramatic_structure"
                )
                
                if self.quantum_tree.add_branch(parent_branch.branch_id, new_branch):
                    branches_created += 1
                    
            except Exception as e:
                if progress_callback:
                    progress_callback({"phase": "error", "message": f"Error generating structural {focus}: {e}"})
        
        return branches_created
    
    def _create_character_psychology_prompt(self, character, psych_type, parent_branch, requirements):
        """Create character psychology prompt."""
        return f"""Continue this scene focusing on {character}'s {psych_type} psychological response:

Current scene: {parent_branch.narrative_content[:200]}...

Setting: {requirements.setting}
Characters: {', '.join(requirements.characters)}
Conflict: {requirements.key_conflict}

Generate 300-400 words where {character} responds primarily from their {psych_type.replace('_', ' ')} psychological state. Show how this inner drive shapes their dialogue, actions, and reactions to other characters.

Use theatrical format with character names in CAPS and stage directions in parentheses."""
    
    def _create_thematic_prompt(self, approach, parent_branch, requirements):
        """Create thematic exploration prompt."""
        return f"""Continue this scene using a {approach} thematic approach:

Current scene: {parent_branch.narrative_content[:200]}...

Take a {approach} approach to the central themes. Generate 300-400 words that explore the thematic tension through this lens, showing how different characters embody different aspects of the theme.

Use theatrical format with character names in CAPS and stage directions in parentheses."""
    
    def _create_structural_prompt(self, focus, parent_branch, requirements):
        """Create structural prompt."""
        return f"""Continue this scene with structural focus on {focus.replace('_', ' ')}:

Current scene: {parent_branch.narrative_content[:200]}...

Generate 300-400 words that emphasize {focus.replace('_', ' ')} as the primary structural element. Show how this affects pacing, character interactions, and dramatic momentum.

Use theatrical format with character names in CAPS and stage directions in parentheses."""
    
    def _create_branch_from_response(self, response, parent_branch, divergence_point, divergence_type):
        """Create quantum branch from LLM response."""
        from thespian.llm.quantum_narrative import NarrativeQuantumState, DivergenceType
        
        content = str(response.content if hasattr(response, "content") else response)
        
        return NarrativeQuantumState(
            narrative_content=content,
            divergence_point=divergence_point,
            divergence_type=getattr(DivergenceType, divergence_type.upper(), DivergenceType.CHARACTER_DECISION),
            parent_branch=parent_branch.branch_id,
            depth_level=parent_branch.depth_level + 1
        )
    
    def _collapse_to_best_path(self):
        """Collapse quantum state to best narrative path."""
        if not self.quantum_tree.active_branches:
            return {"content": "No branches available", "quality": 0.0}
        
        # Find branch with highest quality
        best_branch = max(
            self.quantum_tree.active_branches.values(),
            key=lambda b: b.calculate_overall_quality()
        )
        
        return {
            "content": best_branch.narrative_content,
            "quality": best_branch.calculate_overall_quality(),
            "branch_id": best_branch.branch_id,
            "depth": best_branch.depth_level
        }


def main():
    """Main execution with configurable intensity."""
    
    print("🌀 VARIABLE QUANTUM NARRATIVE EXPLORER")
    print("Choose exploration intensity:")
    print("1 = Light (1 branch per dimension)")
    print("2 = Moderate (2 branches per dimension)") 
    print("3 = Heavy (3 branches per dimension)")
    
    try:
        intensity = int(input("Enter intensity (1-3): ") or "2")
    except:
        intensity = 2
    
    explorer = VariableQuantumExplorer(exploration_intensity=intensity)
    result = explorer.run_variable_quantum_exploration()
    
    print(f"\n🎉 VARIABLE QUANTUM EXPLORATION COMPLETE!")

if __name__ == "__main__":
    main()