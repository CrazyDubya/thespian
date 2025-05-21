"""
Advanced Story Structure Demo for Thespian Framework

This example demonstrates how to use the advanced story structure system to create
theatrical productions with more complex narrative patterns.
"""

import os
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from thespian.llm import LLMManager
from thespian.llm.enhanced_memory import EnhancedTheatricalMemory
from thespian.llm.memory_enhanced_playwright import MemoryEnhancedPlaywright
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


def main():
    """Run the advanced story structure demo."""
    print("Initializing Advanced Story Structure Demo...")
    
    # Initialize LLM manager
    llm_manager = LLMManager()
    llm = llm_manager.get_llm("ollama")
    
    # Initialize enhanced memory system
    memory = EnhancedTheatricalMemory()
    
    # Initialize character profiles
    memory.update_character_profile("protagonist", {
        "id": "protagonist",
        "name": "Eleanor",
        "background": "Brilliant physicist who discovered time manipulation",
        "relationships": {"antagonist": "former colleague"},
        "goals": ["Fix timeline anomalies", "Return to proper timeline"],
        "conflicts": ["Ethical concerns about changing the past"],
        "motivations": ["Scientific discovery", "Protecting loved ones"],
        "fears": ["Creating worse futures", "Being trapped in the wrong time"],
        "desires": ["Understanding the laws of time", "Returning home"]
    })
    
    memory.update_character_profile("antagonist", {
        "id": "antagonist",
        "name": "Marcus",
        "background": "Ambitious researcher who believes in controlling time",
        "relationships": {"protagonist": "rival"},
        "goals": ["Gain control of time manipulation technology", "Reshape history"],
        "conflicts": ["Blind ambition vs. potential consequences"],
        "motivations": ["Power", "Desire to fix personal tragedy"],
        "fears": ["Losing control", "Being proven wrong"],
        "desires": ["Validation", "Changing a personal loss"]
    })
    
    memory.update_character_profile("supporter", {
        "id": "supporter",
        "name": "Talia",
        "background": "Quantum engineer and Eleanor's close friend",
        "relationships": {"protagonist": "trusted friend", "antagonist": "suspicious"},
        "goals": ["Help Eleanor", "Understand time anomalies"],
        "conflicts": ["Loyalty vs. scientific ethics"],
        "motivations": ["Friendship", "Scientific curiosity"],
        "fears": ["Losing Eleanor", "Catastrophic time collapse"],
        "desires": ["Resolution", "Safety for all involved"]
    })
    
    # Create advanced story planner with a non-linear structure
    story_planner = AdvancedStoryPlanner(
        structure_type=NarrativeStructureType.NON_LINEAR,
        act_structure=ActStructureType.THREE_ACT,
        num_acts=3,
        narrative_complexity=NarrativeComplexityLevel.COMPLEX
    )
    
    # Add plot threads
    main_thread = PlotThread(
        name="Timeline Restoration",
        description="Eleanor's quest to fix the fractured timeline",
        importance=1.0,
        character_focus=["protagonist", "antagonist"],
        arc_points=[
            {"position": 0.1, "description": "Discovery of timeline fractures"},
            {"position": 0.5, "description": "Understanding the scope of the damage"},
            {"position": 0.85, "description": "Final attempt to restore proper flow of time"}
        ]
    )
    story_planner.add_plot_thread(main_thread)
    
    subplot = SubplotDefinition(
        name="Ethics of Time",
        description="Exploration of the moral implications of changing time",
        characters=["protagonist", "supporter"],
        arc_type="intellectual-debate",
        integration_points=[0.2, 0.6, 0.75],
        resolution_target=0.8
    )
    story_planner.add_subplot(subplot)
    
    # Add plot reversal
    reversal = PlotReversal(
        description="The protagonist discovers she created the time fractures",
        target_position=0.6,
        affected_threads=["Timeline Restoration"],
        impact="Forces protagonist to reconsider her entire approach",
        foreshadowing=["Strange calculations that don't add up", "Déjà vu experiences"]
    )
    story_planner.add_plot_reversal(reversal)
    
    # Create scene planner
    scene_planner = DynamicScenePlanner(
        story_planner=story_planner,
        memory=memory,
        total_acts=3,
        scenes_per_act={1: 3, 2: 4, 3: 3}
    )
    
    # Create enhanced playwright with structure awareness
    playwright = StructureEnhancedPlaywright(
        memory=memory,
        story_planner=story_planner,
        scene_planner=scene_planner,
        llm_invoke_func=llm.invoke
    )
    
    # Generate scenes
    print("\nGenerating scenes with advanced story structure...\n")
    
    # Generate Act 1
    print("=== Act 1 ===")
    act1_scenes = []
    for scene_num in range(1, 4):
        print(f"Generating Act 1, Scene {scene_num}...")
        scene = playwright.generate_structured_scene(
            act_number=1,
            scene_number=scene_num,
            additional_requirements={
                "setting": "Advanced physics laboratory and time anomaly locations",
                "tone": "Scientific mystery with growing tension",
                "focus": "Establishing characters and the central time anomaly problem"
            }
        )
        act1_scenes.append(scene)
        print(f"Generated scene with beat: {scene['current_beat']}")
    
    # Generate Act 2
    print("\n=== Act 2 ===")
    act2_scenes = []
    for scene_num in range(1, 5):
        print(f"Generating Act 2, Scene {scene_num}...")
        scene = playwright.generate_structured_scene(
            act_number=2,
            scene_number=scene_num,
            additional_requirements={
                "setting": "Multiple time periods affected by anomalies",
                "tone": "Increasing complexity and ethical dilemmas",
                "focus": "Deepening conflict between characters and approaches"
            }
        )
        act2_scenes.append(scene)
        print(f"Generated scene with beat: {scene['current_beat']}")
    
    # Generate Act 3
    print("\n=== Act 3 ===")
    act3_scenes = []
    for scene_num in range(1, 4):
        print(f"Generating Act 3, Scene {scene_num}...")
        scene = playwright.generate_structured_scene(
            act_number=3,
            scene_number=scene_num,
            additional_requirements={
                "setting": "Time nexus point where all timelines converge",
                "tone": "Climactic confrontation and revelation",
                "focus": "Resolution of conflicts and restoration of order"
            }
        )
        act3_scenes.append(scene)
        print(f"Generated scene with beat: {scene['current_beat']}")
    
    # Output the full play
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    
    output_path = output_dir / "advanced_structure_play.txt"
    
    with open(output_path, "w") as f:
        f.write("# Temporal Convergence: A Non-Linear Play\n\n")
        
        f.write("## Act 1\n\n")
        for i, scene in enumerate(act1_scenes, 1):
            f.write(f"### Scene {i} - {scene['current_beat']}\n\n")
            f.write(scene["content"])
            f.write("\n\n---\n\n")
        
        f.write("## Act 2\n\n")
        for i, scene in enumerate(act2_scenes, 1):
            f.write(f"### Scene {i} - {scene['current_beat']}\n\n")
            f.write(scene["content"])
            f.write("\n\n---\n\n")
        
        f.write("## Act 3\n\n")
        for i, scene in enumerate(act3_scenes, 1):
            f.write(f"### Scene {i} - {scene['current_beat']}\n\n")
            f.write(scene["content"])
            f.write("\n\n---\n\n")
    
    print(f"\nPlay written to {output_path}")
    print("\nStructural Analysis:")
    print(f"- Total scenes generated: {len(act1_scenes) + len(act2_scenes) + len(act3_scenes)}")
    print(f"- Story beats covered: {sum(1 for beat in story_planner.story_beats if beat.complete)}/{len(story_planner.story_beats)}")
    print(f"- Structure type: {story_planner.structure_type}")
    print(f"- Act structure: {story_planner.act_structure}")
    print(f"- Narrative complexity: {story_planner.narrative_complexity}")


if __name__ == "__main__":
    main()