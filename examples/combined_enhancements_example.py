"""
Combined Enhancements Example for Thespian Framework

This example demonstrates how to use all enhanced systems together:
1. Iterative Refinement System
2. Memory and Continuity System
3. Advanced Story Structure System

The combined approach creates a sophisticated theatrical production
with complex structure, detailed character development, and high-quality scenes.
"""

import os
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from thespian.llm import LLMManager
from thespian.llm.enhanced_memory import EnhancedTheatricalMemory
from thespian.llm.iterative_refinement import refine_scene_iteratively
from thespian.llm.advanced_story_structure import (
    AdvancedStoryPlanner, 
    DynamicScenePlanner, 
    StructureEnhancedPlaywright,
    NarrativeStructureType,
    ActStructureType, 
    NarrativeComplexityLevel,
    PlotThread,
    SubplotDefinition,
    PlotReversal
)

# Import enhanced prompts
from thespian.config.enhanced_prompts import (
    ENHANCED_SCENE_GENERATION_PROMPT, 
    ITERATIVE_SCENE_REFINEMENT_PROMPT,
    CHARACTER_DEPTH_PROMPT
)


class CombinedEnhancementPlaywright:
    """
    Combines all enhancement systems for the most sophisticated scene generation.
    """
    
    def __init__(self, memory, story_planner, scene_planner, llm_manager):
        """Initialize the combined enhancement playwright."""
        self.memory = memory
        self.story_planner = story_planner
        self.scene_planner = scene_planner
        self.llm_manager = llm_manager
        self.base_llm = llm_manager.get_llm("ollama")
        
        # Create structure enhanced playwright
        self.structure_playwright = StructureEnhancedPlaywright(
            memory=memory,
            story_planner=story_planner,
            scene_planner=scene_planner,
            llm_invoke_func=self.base_llm.invoke
        )
    
    def generate_refined_structured_scene(
        self, 
        act_number: int, 
        scene_number: int, 
        additional_requirements=None, 
        refinement_iterations=2
    ):
        """
        Generate a scene using all enhancement systems.
        
        1. First, generate a scene with advanced structure awareness
        2. Then, refine the scene iteratively for quality and detail
        3. Finally, update memory and narrative continuity
        
        Args:
            act_number: Current act number
            scene_number: Current scene number
            additional_requirements: Additional scene requirements
            refinement_iterations: Number of refinement iterations
            
        Returns:
            Dict containing the generated and refined scene
        """
        print(f"Generating initial scene for Act {act_number}, Scene {scene_number}...")
        
        # Generate initial scene with structure awareness
        initial_scene = self.structure_playwright.generate_structured_scene(
            act_number=act_number,
            scene_number=scene_number,
            additional_requirements=additional_requirements
        )
        
        # Prepare refinement context
        narrative_position = self.story_planner.calculate_narrative_position(
            act_number, 
            scene_number, 
            self.scene_planner.total_acts, 
            self.scene_planner.scenes_per_act.get(act_number, 4)
        )
        
        current_beat = self.story_planner.get_story_beat_by_position(narrative_position)
        
        refinement_context = {
            "act_number": act_number,
            "scene_number": scene_number,
            "narrative_position": narrative_position,
            "current_beat": current_beat.name if current_beat else "Unknown",
            "current_beat_purpose": current_beat.purpose if current_beat else "",
            "current_beat_emotion": current_beat.emotional_tone if current_beat else "",
            "structure_type": self.story_planner.structure_type.value,
            "act_structure": self.story_planner.act_structure.value
        }
        
        # Get character context for refinement
        characters = {}
        for char_id, profile in self.memory.character_profiles.items():
            # Only include main characters in refinement context
            if hasattr(profile, "get_arc_summary"):
                arc_summary = profile.get_arc_summary()
                emotional_state = profile.get_current_emotional_state()
                
                characters[profile.name] = {
                    "arc_stage": arc_summary.get("current_stage", "unknown"),
                    "emotion": emotional_state.emotion if emotional_state else "neutral",
                    "relationships": getattr(profile, "relationships", {})
                }
        
        refinement_context["characters"] = characters
        
        print(f"Refining scene with {refinement_iterations} iterations...")
        
        # Refine the scene iteratively
        refined_content = refine_scene_iteratively(
            scene_content=initial_scene["content"],
            context=refinement_context,
            llm_invoke_func=self.base_llm.invoke,
            iterations=refinement_iterations,
            focus_areas=["character_depth", "sensory_detail", "emotional_impact", "dialogue_quality"]
        )
        
        # Create the final scene with refined content
        refined_scene = dict(initial_scene)
        refined_scene["content"] = refined_content
        refined_scene["refined"] = True
        refined_scene["refinement_iterations"] = refinement_iterations
        
        # Update memory with the refined scene
        scene_id = initial_scene["scene_id"]
        
        # Update narrative tracking
        if hasattr(self.memory, "update_narrative_from_scene"):
            self.memory.update_narrative_from_scene(scene_id, refined_content, self.base_llm.invoke)
        
        # Update character profiles
        for char_id in self.memory.character_profiles:
            if hasattr(self.memory, "update_character_from_scene"):
                self.memory.update_character_from_scene(
                    char_id, scene_id, refined_content, self.base_llm.invoke
                )
        
        return refined_scene


def main():
    """Run the combined enhancements example."""
    print("Initializing Combined Enhancements Demo...")
    
    # Initialize LLM manager
    llm_manager = LLMManager()
    
    # Initialize enhanced memory system
    memory = EnhancedTheatricalMemory()
    
    # Initialize character profiles
    memory.update_character_profile("protagonist", {
        "id": "protagonist",
        "name": "Amara",
        "background": "Former royal advisor who uncovered ancient magic in forbidden texts",
        "relationships": {"mentor": "former teacher", "antagonist": "childhood friend turned rival"},
        "goals": ["Master the ancient magic", "Restore balance to the kingdom"],
        "conflicts": ["Temptation to use power for personal gain", "Doubt in her abilities"],
        "motivations": ["Protect the innocent", "Prove her worth"],
        "fears": ["Losing control of the magic", "Becoming like those who abused power"],
        "desires": ["Recognition", "Understanding the world's mysteries"],
        "strengths": ["Intelligence", "Determination"],
        "flaws": ["Pride", "Recklessness"]
    })
    
    memory.update_character_profile("mentor", {
        "id": "mentor",
        "name": "Elias",
        "background": "Ancient mage who has seen the rise and fall of kingdoms",
        "relationships": {"protagonist": "promising student", "antagonist": "former rival"},
        "goals": ["Guide the next generation", "Ensure magic is used responsibly"],
        "conflicts": ["Declining health", "Regrets from the past"],
        "motivations": ["Legacy", "Wisdom"],
        "fears": ["Dying before completing his mission", "The return of dark magic"],
        "desires": ["Peace", "Seeing his student succeed"],
        "strengths": ["Wisdom", "Magical knowledge"],
        "flaws": ["Secretive", "Stubborn"]
    })
    
    memory.update_character_profile("antagonist", {
        "id": "antagonist",
        "name": "Kairo",
        "background": "Brilliant scholar who believes magic belongs to the strongest",
        "relationships": {"protagonist": "rival with shared history", "mentor": "former teacher"},
        "goals": ["Claim ancient magic for himself", "Reshape kingdom in his image"],
        "conflicts": ["Humanity vs. ambition", "Genuine affection for protagonist"],
        "motivations": ["Power", "Recognition", "Wounded pride"],
        "fears": ["Being forgotten", "Being proven wrong"],
        "desires": ["Control", "Validation", "The protagonist's respect"],
        "strengths": ["Charisma", "Magical talent"],
        "flaws": ["Arrogance", "Insecurity"]
    })
    
    # Create advanced story planner - using nested structure with hero's journey
    story_planner = AdvancedStoryPlanner(
        structure_type=NarrativeStructureType.NESTED,
        act_structure=ActStructureType.HERO_JOURNEY,
        num_acts=3,
        narrative_complexity=NarrativeComplexityLevel.COMPLEX
    )
    
    # Add main plot thread
    main_thread = PlotThread(
        name="Ancient Magic Awakening",
        description="The rediscovery and mastery of ancient, forgotten magic",
        importance=1.0,
        character_focus=["protagonist", "mentor", "antagonist"],
        arc_points=[
            {"position": 0.1, "description": "Discovery of ancient magical texts"},
            {"position": 0.3, "description": "First attempts to use the magic"},
            {"position": 0.5, "description": "Magic begins to transform the protagonist"},
            {"position": 0.7, "description": "Magic threatens to corrupt or overwhelm"},
            {"position": 0.9, "description": "Final mastery or rejection of the power"}
        ]
    )
    story_planner.add_plot_thread(main_thread)
    
    # Add subplots
    mentor_subplot = SubplotDefinition(
        name="Mentor's Last Lessons",
        description="The mentor's final chance to share wisdom before time runs out",
        characters=["mentor", "protagonist"],
        arc_type="passing-the-torch",
        integration_points=[0.2, 0.4, 0.65, 0.85],
        resolution_target=0.85
    )
    story_planner.add_subplot(mentor_subplot)
    
    relationship_subplot = SubplotDefinition(
        name="Friendship to Rivalry",
        description="The complicated relationship between protagonist and antagonist",
        characters=["protagonist", "antagonist"],
        arc_type="tragic-separation",
        integration_points=[0.15, 0.35, 0.55, 0.75, 0.95],
        resolution_target=0.95
    )
    story_planner.add_subplot(relationship_subplot)
    
    # Add plot reversal
    reversal = PlotReversal(
        description="The mentor is revealed to have created the dark magic threatening the kingdom",
        target_position=0.65,
        affected_threads=["Ancient Magic Awakening", "Mentor's Last Lessons"],
        impact="Forces protagonist to confront mentor and reconsider everything",
        foreshadowing=["Mentor's reluctance to discuss certain texts", "Strange reactions to specific magic"]
    )
    story_planner.add_plot_reversal(reversal)
    
    # Create scene planner
    scene_planner = DynamicScenePlanner(
        story_planner=story_planner,
        memory=memory,
        total_acts=3,
        scenes_per_act={1: 3, 2: 4, 3: 3}
    )
    
    # Create combined enhancement playwright
    playwright = CombinedEnhancementPlaywright(
        memory=memory,
        story_planner=story_planner,
        scene_planner=scene_planner,
        llm_manager=llm_manager
    )
    
    # Generate the play with all enhancements active
    print("\nGenerating play with combined enhancements system...\n")
    
    # Generate scenes with varied refinement levels
    all_scenes = []
    
    # Act 1 - Normal refinement (2 iterations)
    print("=== Act 1 ===")
    for scene_num in range(1, 4):
        print(f"Generating Act 1, Scene {scene_num}...")
        scene = playwright.generate_refined_structured_scene(
            act_number=1,
            scene_number=scene_num,
            additional_requirements={
                "setting": "Ancient library and magical academy",
                "tone": "Mystery and wonder mixed with growing tension",
                "focus": "Establishing characters and the discovery of ancient magic"
            },
            refinement_iterations=2
        )
        all_scenes.append(scene)
        print(f"Generated refined scene with beat: {scene['current_beat']}")
    
    # Act 2 - Increased refinement for rising action (3 iterations)
    print("\n=== Act 2 ===")
    for scene_num in range(1, 5):
        print(f"Generating Act 2, Scene {scene_num}...")
        scene = playwright.generate_refined_structured_scene(
            act_number=2,
            scene_number=scene_num,
            additional_requirements={
                "setting": "Magical locations with increasing enchantment and danger",
                "tone": "Intensifying conflict and increasing magical elements",
                "focus": "Character development and magical transformation"
            },
            refinement_iterations=3  # More refinement for important middle act
        )
        all_scenes.append(scene)
        print(f"Generated refined scene with beat: {scene['current_beat']}")
    
    # Act 3 - Highest refinement for climax (4 iterations)
    print("\n=== Act 3 ===")
    for scene_num in range(1, 4):
        print(f"Generating Act 3, Scene {scene_num}...")
        
        # Extra refinement for the climactic scene
        iterations = 4 if scene_num == 2 else 3
        
        scene = playwright.generate_refined_structured_scene(
            act_number=3,
            scene_number=scene_num,
            additional_requirements={
                "setting": "Ancient magical nexus where power converges",
                "tone": "Epic confrontation with magical and emotional intensity",
                "focus": "Resolution of character arcs and magical conflict"
            },
            refinement_iterations=iterations
        )
        all_scenes.append(scene)
        print(f"Generated refined scene with beat: {scene['current_beat']}")
    
    # Output the full play
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    
    output_path = output_dir / "combined_enhancements_play.txt"
    
    with open(output_path, "w") as f:
        f.write("# The Ancient Awakening: A Nested Structure Play\n\n")
        f.write("## Play Details\n")
        f.write(f"- Structure Type: {story_planner.structure_type.value}\n")
        f.write(f"- Act Structure: {story_planner.act_structure.value}\n")
        f.write(f"- Narrative Complexity: {story_planner.narrative_complexity.value}\n")
        f.write(f"- Enhancement Systems: Iterative Refinement, Memory System, Advanced Structure\n\n")
        
        # Write Act 1
        f.write("## Act 1\n\n")
        for scene in [s for s in all_scenes if s['act'] == 1]:
            f.write(f"### Scene {scene['scene']} - {scene['current_beat']}\n")
            f.write(f"*Refinement Iterations: {scene['refinement_iterations']}*\n\n")
            f.write(scene["content"])
            f.write("\n\n---\n\n")
        
        # Write Act 2
        f.write("## Act 2\n\n")
        for scene in [s for s in all_scenes if s['act'] == 2]:
            f.write(f"### Scene {scene['scene']} - {scene['current_beat']}\n")
            f.write(f"*Refinement Iterations: {scene['refinement_iterations']}*\n\n")
            f.write(scene["content"])
            f.write("\n\n---\n\n")
        
        # Write Act 3
        f.write("## Act 3\n\n")
        for scene in [s for s in all_scenes if s['act'] == 3]:
            f.write(f"### Scene {scene['scene']} - {scene['current_beat']}\n")
            f.write(f"*Refinement Iterations: {scene['refinement_iterations']}*\n\n")
            f.write(scene["content"])
            f.write("\n\n---\n\n")
        
        # Write character development summary
        f.write("## Character Development Summary\n\n")
        for char_id, profile in memory.character_profiles.items():
            f.write(f"### {profile.name}\n\n")
            
            if hasattr(profile, "development_arc") and profile.development_arc:
                f.write("#### Character Arc\n")
                for point in profile.development_arc:
                    f.write(f"- {point.stage}: {point.description}\n")
                f.write("\n")
            
            if hasattr(profile, "emotional_states") and profile.emotional_states:
                f.write("#### Emotional Journey\n")
                for state in profile.emotional_states[-5:]:  # Show last 5 emotional states
                    f.write(f"- {state.emotion} ({state.intensity:.1f}): {state.cause}\n")
                f.write("\n")
            
            if hasattr(profile, "relationship_developments") and profile.relationship_developments:
                f.write("#### Key Relationship Changes\n")
                for other, changes in profile.relationship_developments.items():
                    if changes:
                        latest = changes[-1]
                        f.write(f"- With {other}: {latest.status} - {latest.change}\n")
                f.write("\n")
    
    print(f"\nPlay written to {output_path}")
    print("\nEnhancement Results:")
    print(f"- Total scenes generated: {len(all_scenes)}")
    print(f"- Total refinement iterations: {sum(s['refinement_iterations'] for s in all_scenes)}")
    print(f"- Character development points tracked: {sum(len(profile.development_arc) for profile in memory.character_profiles.values() if hasattr(profile, 'development_arc'))}")
    print(f"- Story beats fulfilled: {sum(1 for beat in story_planner.story_beats if beat.complete)}/{len(story_planner.story_beats)}")


if __name__ == "__main__":
    main()