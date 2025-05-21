"""
Advanced Story Structure Capabilities Demo

This script demonstrates the capabilities of the advanced story structure system
without requiring the full LLM integration. It creates a complete story structure
and shows how it progresses through different narrative stages.
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from pprint import pprint

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from thespian.llm.advanced_story_structure import (
    AdvancedStoryPlanner, 
    NarrativeStructureType,
    ActStructureType, 
    NarrativeComplexityLevel,
    PlotThread,
    SubplotDefinition,
    PlotReversal,
    StoryBeat
)

def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80 + "\n")

def print_section(title):
    """Print a formatted section header."""
    print("\n" + "-" * 60)
    print(f" {title} ".center(60, "-"))
    print("-" * 60)

def print_story_beat(beat):
    """Print a formatted story beat."""
    if not beat:
        print("  No beat found")
        return
    
    print(f"  Name: {beat.name}")
    print(f"  Description: {beat.description}")
    print(f"  Purpose: {beat.purpose}")
    print(f"  Target Position: {beat.target_position:.2f}")
    print(f"  Emotional Tone: {beat.emotional_tone}")
    print(f"  Complete: {beat.complete}")

def simulate_scene_generation(act, scene, story_planner, description):
    """Simulate generating a scene and updating story beats."""
    position = story_planner.calculate_narrative_position(
        act, scene, story_planner.num_acts, 4
    )
    
    # Find the closest beat
    beat = story_planner.get_story_beat_by_position(position)
    
    # Update the beat as completed
    if beat:
        scene_id = f"act{act}_scene{scene}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        story_planner.update_story_beat(beat.name, scene_id, complete=True)
    
    print(f"  Act {act}, Scene {scene} - Position: {position:.2f}")
    print(f"  Description: {description}")
    print(f"  Beat: {beat.name if beat else 'None'}")
    print(f"  Completed: {'Yes' if beat and beat.complete else 'No'}")
    print()

# Main demonstration
if __name__ == "__main__":
    print_header("ADVANCED STORY STRUCTURE SYSTEM DEMO")
    
    print("This demo showcases the capabilities of the advanced story structure system")
    print("by creating and manipulating a complex narrative structure.")
    
    # Create story planner with hero's journey structure
    print_section("Creating Story Structure")
    
    story_planner = AdvancedStoryPlanner(
        structure_type=NarrativeStructureType.NESTED,
        act_structure=ActStructureType.HERO_JOURNEY,
        num_acts=3,
        narrative_complexity=NarrativeComplexityLevel.COMPLEX
    )
    
    print(f"Created story structure with:")
    print(f"  Structure Type: {story_planner.structure_type}")
    print(f"  Act Structure: {story_planner.act_structure}")
    print(f"  Acts: {story_planner.num_acts}")
    print(f"  Complexity: {story_planner.narrative_complexity}")
    print(f"  Story Beats: {len(story_planner.story_beats)}")
    
    # Add main plot thread
    print_section("Adding Plot Threads")
    
    main_plot = PlotThread(
        name="The Chosen One's Quest",
        description="A reluctant hero discovers their destiny to save the world from darkness",
        importance=1.0,
        character_focus=["hero", "mentor"],
        arc_points=[
            {"position": 0.1, "description": "Hero discovers unusual abilities"},
            {"position": 0.3, "description": "Hero meets the mentor and learns of their destiny"},
            {"position": 0.5, "description": "Hero faces first major challenge and doubts their path"},
            {"position": 0.7, "description": "Hero makes a sacrifice and embraces their destiny"},
            {"position": 0.9, "description": "Hero confronts the ultimate darkness"}
        ]
    )
    story_planner.add_plot_thread(main_plot)
    print(f"Added main plot thread: {main_plot.name}")
    print(f"  Description: {main_plot.description}")
    print(f"  Arc Points: {len(main_plot.arc_points)}")
    
    # Add subplots
    mentor_subplot = SubplotDefinition(
        name="Mentor's Redemption",
        description="The mentor seeks to make amends for past failures through the hero",
        characters=["mentor", "hero"],
        arc_type="redemption",
        integration_points=[0.2, 0.45, 0.8],
        resolution_target=0.85
    )
    story_planner.add_subplot(mentor_subplot)
    print(f"Added subplot: {mentor_subplot.name}")
    
    romance_subplot = SubplotDefinition(
        name="Forbidden Romance",
        description="The hero falls for someone from the opposing side",
        characters=["hero", "love_interest"],
        arc_type="tragic-romance",
        integration_points=[0.25, 0.5, 0.75],
        resolution_target=0.9
    )
    story_planner.add_subplot(romance_subplot)
    print(f"Added subplot: {romance_subplot.name}")
    
    # Add plot reversal
    print_section("Adding Plot Reversals")
    
    reversal = PlotReversal(
        description="The mentor is revealed to be working for the darkness",
        target_position=0.65,
        affected_threads=["The Chosen One's Quest", "Mentor's Redemption"],
        impact="Forces the hero to continue alone and question everything they've learned",
        foreshadowing=["Mentor's mysterious absences", "Contradictions in mentor's teachings"]
    )
    story_planner.add_plot_reversal(reversal)
    print(f"Added plot reversal: {reversal.description}")
    print(f"  Target position: {reversal.target_position}")
    print(f"  Affected threads: {', '.join(reversal.affected_threads)}")
    
    # Show story beats
    print_section("Story Beats")
    
    for i, beat in enumerate(sorted(story_planner.story_beats, key=lambda x: x.target_position)):
        print(f"{i+1}. {beat.name} (position: {beat.target_position:.2f})")
    
    # Examine specific story beats
    print_section("Examining Key Story Beats")
    
    beginning_beat = story_planner.get_story_beat_by_position(0.1)
    print("Beginning of story:")
    print_story_beat(beginning_beat)
    
    middle_beat = story_planner.get_story_beat_by_position(0.5)
    print("\nMiddle of story:")
    print_story_beat(middle_beat)
    
    end_beat = story_planner.get_story_beat_by_position(0.9)
    print("\nEnd of story:")
    print_story_beat(end_beat)
    
    # Simulate story progression
    print_section("Simulating Story Progression")
    
    print("Act 1 - Beginning of the Hero's Journey")
    simulate_scene_generation(1, 1, story_planner, "Ordinary World: The hero's normal life before adventure")
    simulate_scene_generation(1, 2, story_planner, "Call to Adventure: Supernatural event disrupts hero's life")
    simulate_scene_generation(1, 3, story_planner, "Refusal of the Call: Hero initially rejects destiny")
    simulate_scene_generation(1, 4, story_planner, "Meeting the Mentor: Mysterious figure offers guidance")
    
    print("Act 2 - Transformation and Challenges")
    simulate_scene_generation(2, 1, story_planner, "Crossing the Threshold: Hero leaves familiar world")
    simulate_scene_generation(2, 2, story_planner, "Tests, Allies, Enemies: First challenges and new friends")
    simulate_scene_generation(2, 3, story_planner, "Approach to the Inmost Cave: Preparing for major challenge")
    simulate_scene_generation(2, 4, story_planner, "The Ordeal: Facing death and transformation")
    
    print("Act 3 - Return and Resolution")
    simulate_scene_generation(3, 1, story_planner, "The Road Back: Consequences pursue the hero")
    simulate_scene_generation(3, 2, story_planner, "Resurrection: Final and most dangerous confrontation")
    simulate_scene_generation(3, 3, story_planner, "Return with the Elixir: Hero brings wisdom back home")
    
    # Show narrative structure at key points
    print_section("Story Structure Analysis")
    
    act1_position = story_planner.calculate_narrative_position(1, 2, story_planner.num_acts, 4)
    print(f"Act 1, Scene 2 (Position: {act1_position:.2f}):")
    elements = story_planner.get_necessary_story_elements(act1_position)
    active_subplots = elements.get("active_subplots", [])
    current_beat = elements.get("current_beat")
    current_beat_name = current_beat.get("name", "None") if current_beat else "None"
    print(f"  Current Beat: {current_beat_name}")
    print(f"  Active Subplots: {', '.join([s.get('name', '') for s in active_subplots])}")
    print(f"  Pending Reversals: {len(elements.get('pending_reversals', []))}")
    
    midpoint_position = story_planner.calculate_narrative_position(2, 2, story_planner.num_acts, 4)
    print(f"\nMidpoint (Position: {midpoint_position:.2f}):")
    elements = story_planner.get_necessary_story_elements(midpoint_position)
    active_subplots = elements.get("active_subplots", [])
    current_beat = elements.get("current_beat")
    current_beat_name = current_beat.get("name", "None") if current_beat else "None"
    print(f"  Current Beat: {current_beat_name}")
    print(f"  Active Subplots: {', '.join([s.get('name', '') for s in active_subplots])}")
    print(f"  Pending Reversals: {len(elements.get('pending_reversals', []))}")
    
    climax_position = story_planner.calculate_narrative_position(3, 2, story_planner.num_acts, 4)
    print(f"\nClimax (Position: {climax_position:.2f}):")
    elements = story_planner.get_necessary_story_elements(climax_position)
    active_subplots = elements.get("active_subplots", [])
    current_beat = elements.get("current_beat")
    current_beat_name = current_beat.get("name", "None") if current_beat else "None"
    print(f"  Current Beat: {current_beat_name}")
    print(f"  Active Subplots: {', '.join([s.get('name', '') for s in active_subplots])}")
    print(f"  Pending Reversals: {len(elements.get('pending_reversals', []))}")
    
    # Status summary
    print_section("Story Completion Status")
    
    completed_beats = sum(1 for beat in story_planner.story_beats if beat.complete)
    total_beats = len(story_planner.story_beats)
    print(f"Story Beats: {completed_beats}/{total_beats} completed ({completed_beats/total_beats*100:.1f}%)")
    
    next_beat = story_planner.get_next_incomplete_beat()
    if next_beat:
        print(f"Next beat to complete: {next_beat.name} (position: {next_beat.target_position:.2f})")
    else:
        print("All story beats completed!")
    
    # Report on plot reversals
    reversals_executed = sum(1 for r in story_planner.plot_reversals if r.complete)
    print(f"Plot Reversals: {reversals_executed}/{len(story_planner.plot_reversals)} executed")
    
    print_header("DEMO COMPLETED")
    print("The advanced story structure system has successfully demonstrated its capabilities!")
    print("It can manage complex narrative structures with multiple plot threads, subplots,")
    print("and dynamic story beats that adapt to the narrative progression.")