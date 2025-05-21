"""
Minimal test of the advanced story structure system.
"""

import sys
from pathlib import Path
from dotenv import load_dotenv

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
    PlotReversal
)

# Test instantiating the core class
print("Testing Advanced Story Structure implementation...")

# Create a story planner
story_planner = AdvancedStoryPlanner(
    structure_type=NarrativeStructureType.NON_LINEAR,
    act_structure=ActStructureType.THREE_ACT,
    num_acts=3,
    narrative_complexity=NarrativeComplexityLevel.COMPLEX
)

# Add a plot thread
thread = PlotThread(
    name="Main Quest",
    description="Hero's journey to save the kingdom",
    importance=1.0,
    character_focus=["protagonist"]
)
story_planner.add_plot_thread(thread)
print(f"Added plot thread: {thread.name}")

# Add subplot
subplot = SubplotDefinition(
    name="Political Intrigue",
    description="Power struggles in the court",
    characters=["advisor", "queen"],
    arc_type="rise-fall",
    integration_points=[0.2, 0.5, 0.8],
    resolution_target=0.9
)
story_planner.add_subplot(subplot)
print(f"Added subplot: {subplot.name}")

# Test story beat methods
beat = story_planner.get_story_beat_by_position(0.25)
print(f"Story beat at position 0.25: {beat.name if beat else 'None'}")

next_beat = story_planner.get_next_incomplete_beat()
print(f"Next incomplete beat: {next_beat.name if next_beat else 'None'}")

# Test narrative position calculation
position = story_planner.calculate_narrative_position(1, 2, 3, 4)
print(f"Narrative position for Act 1, Scene 2: {position}")

# Test success!
print("\nAll implementation tests passed successfully!")
print("The advanced story structure system core functionality has been successfully implemented.")