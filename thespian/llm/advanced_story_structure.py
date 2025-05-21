"""
Advanced story structure management for complex narrative structures.

This module provides classes and functions for managing more sophisticated story structures
beyond the conventional three-act format, enabling more nuanced and varied storytelling patterns.
"""

from typing import Dict, Any, List, Optional, Union, Set, Tuple
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
import logging
import json
import os
from enum import Enum

from thespian.llm.theatrical_memory import TheatricalMemory, StoryOutline
from thespian.llm.enhanced_memory import EnhancedTheatricalMemory, NarrativeContinuityTracker
from thespian.llm.production_structure import ProductionStructure, ActRequirements

logger = logging.getLogger(__name__)


class NarrativeStructureType(str, Enum):
    """Types of narrative structures available for story planning."""
    
    LINEAR = "linear"
    NON_LINEAR = "non_linear"
    PARALLEL = "parallel"
    NESTED = "nested"
    CIRCULAR = "circular"
    FRAGMENTED = "fragmented"
    EPISODIC = "episodic"
    FRAME = "frame"


class ActStructureType(str, Enum):
    """Types of act structures for different storytelling formats."""
    
    THREE_ACT = "3-act"
    FIVE_ACT = "5-act"
    HERO_JOURNEY = "hero-journey"
    FREYTAG = "freytag-pyramid"
    KISHŌTENKETSU = "kishotenketsu"
    SEVEN_POINT = "seven-point"
    SEQUENCE = "sequence-method"


class NarrativeComplexityLevel(str, Enum):
    """Complexity levels for narrative structures."""
    
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    VERY_COMPLEX = "very_complex"


class StoryBeat(BaseModel):
    """A specific story beat within a narrative structure."""
    
    name: str = Field(..., description="Name of the story beat")
    description: str = Field(..., description="Description of what happens in this beat")
    purpose: str = Field(..., description="Narrative purpose of this beat")
    target_position: float = Field(..., description="Target position in the story (0.0-1.0)")
    emotional_tone: str = Field(..., description="Intended emotional tone")
    required_elements: List[str] = Field(default_factory=list, description="Required story elements")
    optional_elements: List[str] = Field(default_factory=list, description="Optional story elements")
    scene_ids: List[str] = Field(default_factory=list, description="Scenes that fulfill this beat")
    complete: bool = Field(default=False, description="Whether this beat has been completed")


class PlotThread(BaseModel):
    """A thread of plot running through the story."""
    
    name: str = Field(..., description="Name of the plot thread")
    description: str = Field(..., description="Description of this plot thread")
    importance: float = Field(0.5, ge=0.0, le=1.0, description="Importance of this thread (0.0-1.0)")
    character_focus: List[str] = Field(default_factory=list, description="Characters central to this thread")
    arc_points: List[Dict[str, Any]] = Field(default_factory=list, description="Key points in this thread's arc")
    status: str = Field(default="active", description="Status of this thread (active, resolved, etc.)")
    connections: List[str] = Field(default_factory=list, description="Connections to other plot threads")


class PlotReversal(BaseModel):
    """A major reversal or twist in the plot."""
    
    description: str = Field(..., description="Description of the reversal")
    target_position: float = Field(..., description="Target position in the story (0.0-1.0)")
    affected_threads: List[str] = Field(default_factory=list, description="Plot threads affected by this reversal")
    foreshadowing: List[str] = Field(default_factory=list, description="Elements that foreshadow this reversal")
    impact: str = Field(..., description="Impact on the story")
    scene_id: Optional[str] = Field(None, description="Scene where this reversal occurs")
    complete: bool = Field(default=False, description="Whether this reversal has been executed")


class SubplotDefinition(BaseModel):
    """Definition of a subplot within the larger narrative."""
    
    name: str = Field(..., description="Name of the subplot")
    description: str = Field(..., description="Description of this subplot")
    characters: List[str] = Field(default_factory=list, description="Characters involved in this subplot")
    arc_type: str = Field(..., description="Type of narrative arc (rise-fall, etc.)")
    integration_points: List[float] = Field(default_factory=list, description="Points where subplot integrates with main plot (0.0-1.0)")
    resolution_target: float = Field(..., description="Target position for resolution (0.0-1.0)")
    status: str = Field(default="active", description="Status of this subplot")
    scenes: List[str] = Field(default_factory=list, description="Scenes that advance this subplot")


class AdvancedStoryPlanner(BaseModel):
    """Advanced story planner with complex narrative structures."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    structure_type: NarrativeStructureType = Field(..., description="Type of narrative structure")
    act_structure: ActStructureType = Field(..., description="Act structure pattern")
    num_acts: int = Field(ge=1, le=7, description="Number of acts in the story")
    narrative_complexity: NarrativeComplexityLevel = Field(..., description="Narrative complexity level")
    
    # Plot structure elements
    main_plot: Dict[str, Any] = Field(default_factory=dict)
    subplots: List[SubplotDefinition] = Field(default_factory=list)
    plot_threads: List[PlotThread] = Field(default_factory=list)
    plot_reversals: List[PlotReversal] = Field(default_factory=list)
    
    # Story beats specific to the chosen act structure
    story_beats: List[StoryBeat] = Field(default_factory=list)
    
    # Structural elements
    scene_sequence: List[Dict[str, Any]] = Field(default_factory=list)
    time_jumps: List[Dict[str, Any]] = Field(default_factory=list)
    narrative_devices: List[str] = Field(default_factory=list)
    
    # Tracking
    generated_scenes: Dict[str, Any] = Field(default_factory=dict)
    structural_notes: List[str] = Field(default_factory=list)
    
    def __init__(self, **data):
        """Initialize the advanced story planner with appropriate structure."""
        super().__init__(**data)
        if not self.story_beats:
            self._initialize_story_beats()
        if not self.main_plot:
            self._initialize_main_plot()
    
    def _initialize_story_beats(self) -> None:
        """Initialize story beats based on the selected act structure."""
        beats = []
        
        if self.act_structure == ActStructureType.THREE_ACT:
            beats = [
                StoryBeat(
                    name="Introduction",
                    description="Establish the ordinary world and introduce main characters",
                    purpose="Set the stage and introduce the protagonist",
                    target_position=0.05,
                    emotional_tone="Neutral or positive"
                ),
                StoryBeat(
                    name="Inciting Incident",
                    description="Event that sets the story in motion",
                    purpose="Disrupt the status quo and present a challenge",
                    target_position=0.12,
                    emotional_tone="Surprise or disturbance"
                ),
                StoryBeat(
                    name="First Plot Point",
                    description="Protagonist accepts the challenge or is forced into it",
                    purpose="Transition to Act 2 and commit to the journey",
                    target_position=0.25,
                    emotional_tone="Determination or fear"
                ),
                StoryBeat(
                    name="Rising Action",
                    description="Protagonist faces obstacles and complications",
                    purpose="Build tension and develop character",
                    target_position=0.45,
                    emotional_tone="Struggle and growth"
                ),
                StoryBeat(
                    name="Midpoint",
                    description="Major revelation or reversal that changes the context",
                    purpose="Raise stakes and deepen the story",
                    target_position=0.5,
                    emotional_tone="Revelation or surprise"
                ),
                StoryBeat(
                    name="Complications",
                    description="New obstacles emerge, often more difficult",
                    purpose="Increase tension and test the protagonist",
                    target_position=0.65,
                    emotional_tone="Mounting pressure"
                ),
                StoryBeat(
                    name="Second Plot Point",
                    description="Final piece of information or challenge before climax",
                    purpose="Set up the final confrontation",
                    target_position=0.75,
                    emotional_tone="Determination or desperation"
                ),
                StoryBeat(
                    name="Climax",
                    description="Protagonist faces the main conflict directly",
                    purpose="Resolve the central conflict",
                    target_position=0.88,
                    emotional_tone="High tension and catharsis"
                ),
                StoryBeat(
                    name="Resolution",
                    description="Show the aftermath and tie up loose ends",
                    purpose="Provide closure and show change",
                    target_position=0.95,
                    emotional_tone="Satisfaction or reflection"
                )
            ]
        elif self.act_structure == ActStructureType.HERO_JOURNEY:
            beats = [
                StoryBeat(
                    name="Ordinary World",
                    description="Establish hero's normal life before the adventure",
                    purpose="Show what's at stake and establish contrast",
                    target_position=0.05,
                    emotional_tone="Comfortable but incomplete"
                ),
                StoryBeat(
                    name="Call to Adventure",
                    description="Hero is presented with a challenge or opportunity",
                    purpose="Present the central conflict or goal",
                    target_position=0.1,
                    emotional_tone="Curiosity or uncertainty"
                ),
                StoryBeat(
                    name="Refusal of the Call",
                    description="Hero initially resists the challenge",
                    purpose="Show reluctance and raise stakes",
                    target_position=0.15,
                    emotional_tone="Fear or doubt"
                ),
                StoryBeat(
                    name="Meeting the Mentor",
                    description="Hero gains guidance or assistance",
                    purpose="Provide tools or wisdom for the journey",
                    target_position=0.2,
                    emotional_tone="Hope or enlightenment"
                ),
                StoryBeat(
                    name="Crossing the Threshold",
                    description="Hero commits to the adventure",
                    purpose="Transition to the special world",
                    target_position=0.25,
                    emotional_tone="Commitment or trepidation"
                ),
                StoryBeat(
                    name="Tests, Allies, and Enemies",
                    description="Hero faces challenges and meets supporting characters",
                    purpose="Develop character and world",
                    target_position=0.35,
                    emotional_tone="Growth and adaptation"
                ),
                StoryBeat(
                    name="Approach to the Innermost Cave",
                    description="Hero prepares for major challenge",
                    purpose="Build tension before major confrontation",
                    target_position=0.45,
                    emotional_tone="Anticipation or fear"
                ),
                StoryBeat(
                    name="Ordeal",
                    description="Hero faces a major crisis or challenge",
                    purpose="Test the hero's resolve and abilities",
                    target_position=0.5,
                    emotional_tone="Struggle and revelation"
                ),
                StoryBeat(
                    name="Reward",
                    description="Hero gains something from the ordeal",
                    purpose="Provide a moment of achievement",
                    target_position=0.6,
                    emotional_tone="Triumph or relief"
                ),
                StoryBeat(
                    name="The Road Back",
                    description="Hero begins the return journey",
                    purpose="Create urgency to resolve remaining conflicts",
                    target_position=0.7,
                    emotional_tone="Determination or anxiety"
                ),
                StoryBeat(
                    name="Resurrection",
                    description="Hero faces final and most dangerous challenge",
                    purpose="Provide ultimate test and transformation",
                    target_position=0.85,
                    emotional_tone="Sacrifice and transformation"
                ),
                StoryBeat(
                    name="Return with the Elixir",
                    description="Hero returns with something to benefit the ordinary world",
                    purpose="Show growth and provide closure",
                    target_position=0.95,
                    emotional_tone="Fulfillment and wisdom"
                )
            ]
        elif self.act_structure == ActStructureType.FIVE_ACT:
            beats = [
                # Act 1: Exposition
                StoryBeat(
                    name="Exposition",
                    description="Introduce the setting, characters, and initial situation",
                    purpose="Establish the world and characters",
                    target_position=0.1,
                    emotional_tone="Neutral or establishing"
                ),
                # Act 2: Rising Action
                StoryBeat(
                    name="Inciting Incident",
                    description="Event that sets the story in motion",
                    purpose="Begin the central conflict",
                    target_position=0.2,
                    emotional_tone="Disruption or call to action"
                ),
                StoryBeat(
                    name="Rising Complications",
                    description="Protagonist faces increasing challenges",
                    purpose="Build tension and develop character",
                    target_position=0.35,
                    emotional_tone="Struggle and determination"
                ),
                # Act 3: Climax
                StoryBeat(
                    name="Climax",
                    description="Turning point of the story, highest tension",
                    purpose="Present the major confrontation or decision",
                    target_position=0.5,
                    emotional_tone="Peak tension and revelation"
                ),
                # Act 4: Falling Action
                StoryBeat(
                    name="Falling Action",
                    description="Consequences of the climax unfold",
                    purpose="Show results of climactic choices",
                    target_position=0.7,
                    emotional_tone="Impact and processing"
                ),
                StoryBeat(
                    name="Final Suspense",
                    description="Last moment of uncertainty before resolution",
                    purpose="Create final tension",
                    target_position=0.8,
                    emotional_tone="Anticipation or anxiety"
                ),
                # Act 5: Denouement
                StoryBeat(
                    name="Resolution",
                    description="Final outcome is revealed",
                    purpose="Provide closure to central conflict",
                    target_position=0.9,
                    emotional_tone="Release of tension"
                ),
                StoryBeat(
                    name="Denouement",
                    description="Tying up loose ends and showing new normal",
                    purpose="Provide complete closure",
                    target_position=0.95,
                    emotional_tone="Satisfaction or reflection"
                )
            ]
        elif self.act_structure == ActStructureType.KISHŌTENKETSU:
            beats = [
                # Ki: Introduction
                StoryBeat(
                    name="Ki (Introduction)",
                    description="Establish the foundation of the story",
                    purpose="Introduce characters, setting, and situation",
                    target_position=0.2,
                    emotional_tone="Establishment and familiarity"
                ),
                # Shō: Development
                StoryBeat(
                    name="Shō (Development)",
                    description="Develop the characters and situation",
                    purpose="Deepen understanding and build complexity",
                    target_position=0.4,
                    emotional_tone="Growth and exploration"
                ),
                # Ten: Twist
                StoryBeat(
                    name="Ten (Twist)",
                    description="Introduce an unexpected element or perspective",
                    purpose="Challenge expectations and create cognitive shift",
                    target_position=0.7,
                    emotional_tone="Surprise or revelation"
                ),
                # Ketsu: Conclusion
                StoryBeat(
                    name="Ketsu (Conclusion)",
                    description="Bring elements together for meaningful resolution",
                    purpose="Provide resolution that reveals new meaning",
                    target_position=0.9,
                    emotional_tone="Harmony or realization"
                )
            ]
        elif self.act_structure == ActStructureType.SEVEN_POINT:
            beats = [
                StoryBeat(
                    name="Hook",
                    description="Capture interest and establish normal world",
                    purpose="Engage audience and set baseline",
                    target_position=0.05,
                    emotional_tone="Curiosity or comfort"
                ),
                StoryBeat(
                    name="Plot Turn 1",
                    description="Event that propels protagonist into the story",
                    purpose="Commit character to the journey",
                    target_position=0.14,
                    emotional_tone="Disruption or challenge"
                ),
                StoryBeat(
                    name="Pinch Point 1",
                    description="First major pressure point, often showing antagonistic force",
                    purpose="Reveal opposition and raise stakes",
                    target_position=0.25,
                    emotional_tone="Threat or pressure"
                ),
                StoryBeat(
                    name="Midpoint",
                    description="Major shift from reaction to action",
                    purpose="Transform character's approach",
                    target_position=0.5,
                    emotional_tone="Determination or revelation"
                ),
                StoryBeat(
                    name="Pinch Point 2",
                    description="Second major pressure point, usually worse than first",
                    purpose="Create maximum pressure",
                    target_position=0.62,
                    emotional_tone="Crisis or desperation"
                ),
                StoryBeat(
                    name="Plot Turn 2",
                    description="Final discovery or decision that enables resolution",
                    purpose="Equip protagonist for final confrontation",
                    target_position=0.75,
                    emotional_tone="Realization or preparation"
                ),
                StoryBeat(
                    name="Resolution",
                    description="Final confrontation and conclusion",
                    purpose="Resolve central conflict and show transformation",
                    target_position=0.9,
                    emotional_tone="Climax and closure"
                )
            ]
        
        # Add custom story beats for other structures
        if self.structure_type == NarrativeStructureType.NON_LINEAR:
            # Add special beats for non-linear narratives
            beats.extend([
                StoryBeat(
                    name="Timeline Anchor",
                    description="Key event that grounds the non-linear structure",
                    purpose="Provide reference point for audience",
                    target_position=0.3,
                    emotional_tone="Orientation"
                ),
                StoryBeat(
                    name="Convergence Point",
                    description="Point where narrative threads begin to connect",
                    purpose="Build toward cohesive meaning",
                    target_position=0.7,
                    emotional_tone="Realization or connection"
                )
            ])
        elif self.structure_type == NarrativeStructureType.PARALLEL:
            # Add special beats for parallel narratives
            beats.extend([
                StoryBeat(
                    name="Parallel Introduction",
                    description="Establish secondary narrative thread",
                    purpose="Create contrast or complementary story",
                    target_position=0.15,
                    emotional_tone="Contrast or harmony"
                ),
                StoryBeat(
                    name="Thread Intersection",
                    description="Point where parallel narratives interact",
                    purpose="Create meaningful connection",
                    target_position=0.55,
                    emotional_tone="Significance or revelation"
                )
            ])
        elif self.structure_type == NarrativeStructureType.CIRCULAR:
            # Add special beats for circular narratives
            beats.extend([
                StoryBeat(
                    name="Foreshadowing Echo",
                    description="Early element that will be repeated at the end",
                    purpose="Plant seeds for circular resolution",
                    target_position=0.15,
                    emotional_tone="Subtle significance"
                ),
                StoryBeat(
                    name="Circular Return",
                    description="Return to beginning with new context",
                    purpose="Complete the circle with transformation",
                    target_position=0.95,
                    emotional_tone="Recognition or transformation"
                )
            ])
        
        self.story_beats = beats
    
    def _initialize_main_plot(self) -> None:
        """Initialize the main plot structure."""
        self.main_plot = {
            "premise": "Central premise of the story",
            "central_conflict": "Main conflict driving the narrative",
            "protagonist_goal": "What the protagonist aims to achieve",
            "stakes": "What's at risk if the protagonist fails",
            "theme": "Core thematic elements explored",
            "resolution_type": "How the conflict resolves"
        }
    
    def add_subplot(self, subplot: SubplotDefinition) -> None:
        """Add a subplot to the story structure."""
        self.subplots.append(subplot)
    
    def add_plot_thread(self, thread: PlotThread) -> None:
        """Add a plot thread to the story structure."""
        self.plot_threads.append(thread)
    
    def add_plot_reversal(self, reversal: PlotReversal) -> None:
        """Add a plot reversal to the story structure."""
        self.plot_reversals.append(reversal)
    
    def update_story_beat(self, beat_name: str, scene_id: str, complete: bool = True) -> bool:
        """Update a story beat with a scene that fulfills it."""
        for beat in self.story_beats:
            if beat.name == beat_name:
                beat.scene_ids.append(scene_id)
                beat.complete = complete
                return True
        return False
    
    def get_story_beat_by_position(self, position: float, tolerance: float = 0.05) -> Optional[StoryBeat]:
        """Get the story beat closest to a given narrative position."""
        closest_beat = None
        closest_distance = float('inf')
        
        for beat in self.story_beats:
            distance = abs(beat.target_position - position)
            if distance < closest_distance and distance <= tolerance:
                closest_beat = beat
                closest_distance = distance
        
        return closest_beat
    
    def get_next_incomplete_beat(self) -> Optional[StoryBeat]:
        """Get the next incomplete story beat in sequence."""
        for beat in sorted(self.story_beats, key=lambda x: x.target_position):
            if not beat.complete:
                return beat
        return None
    
    def calculate_narrative_position(self, act: int, scene: int, total_acts: int, scenes_per_act: int) -> float:
        """Calculate approximate position in narrative (0.0-1.0) based on act and scene numbers."""
        act_fraction = (act - 1) / total_acts
        scene_fraction = (scene - 1) / scenes_per_act / total_acts
        return act_fraction + scene_fraction
    
    def get_active_subplots(self, position: float, tolerance: float = 0.1) -> List[SubplotDefinition]:
        """Get subplots that should be active at the current narrative position."""
        active_subplots = []
        
        for subplot in self.subplots:
            # Check if subplot is active
            if subplot.status != "resolved":
                # Check if this is an integration point for the subplot
                for point in subplot.integration_points:
                    if abs(point - position) <= tolerance:
                        active_subplots.append(subplot)
                        break
        
        return active_subplots
    
    def get_pending_reversals(self, position: float, tolerance: float = 0.05) -> List[PlotReversal]:
        """Get plot reversals that should occur near the current narrative position."""
        pending_reversals = []
        
        for reversal in self.plot_reversals:
            if not reversal.complete and abs(reversal.target_position - position) <= tolerance:
                pending_reversals.append(reversal)
        
        return pending_reversals
    
    def get_necessary_story_elements(self, position: float) -> Dict[str, Any]:
        """Get necessary story elements for the current narrative position."""
        # Get current story beat
        closest_beat = self.get_story_beat_by_position(position)
        active_subplots = self.get_active_subplots(position)
        pending_reversals = self.get_pending_reversals(position)
        
        elements = {
            "current_beat": closest_beat.dict() if closest_beat else None,
            "active_subplots": [subplot.dict() for subplot in active_subplots],
            "pending_reversals": [reversal.dict() for reversal in pending_reversals],
            "position": position,
            "narrative_devices": [device for device in self.narrative_devices 
                               if device.get("start_position", 0) <= position <= device.get("end_position", 1.0)]
        }
        
        # Add specific requirements based on narrative structure type
        if self.structure_type == NarrativeStructureType.NON_LINEAR:
            elements["timeline_requirements"] = self._get_non_linear_requirements(position)
        elif self.structure_type == NarrativeStructureType.PARALLEL:
            elements["thread_requirements"] = self._get_parallel_requirements(position)
        
        return elements
    
    def _get_non_linear_requirements(self, position: float) -> Dict[str, Any]:
        """Get requirements specific to non-linear narrative at this position."""
        return {
            "timeline_connections": [jump for jump in self.time_jumps 
                                  if jump.get("target_position") == position],
            "chronological_position": self._calculate_chronological_position(position)
        }
    
    def _get_parallel_requirements(self, position: float) -> Dict[str, Any]:
        """Get requirements specific to parallel narrative at this position."""
        active_threads = [thread for thread in self.plot_threads 
                       if thread.status == "active"]
        
        return {
            "active_threads": [thread.name for thread in active_threads],
            "thread_focus": self._determine_thread_focus(position, active_threads)
        }
    
    def _calculate_chronological_position(self, narrative_position: float) -> float:
        """Calculate chronological position for non-linear narratives."""
        # This would implement story-specific logic for mapping narrative position to chronological position
        # For simple implementation, return a placeholder
        for jump in self.time_jumps:
            if jump.get("narrative_position") == narrative_position:
                return jump.get("chronological_position", narrative_position)
        return narrative_position
    
    def _determine_thread_focus(self, position: float, active_threads: List[PlotThread]) -> str:
        """Determine which parallel thread should be in focus at this position."""
        if not active_threads:
            return ""
            
        # Simple alternating pattern for now
        thread_index = int((position * 10) % len(active_threads))
        return active_threads[thread_index].name


class DynamicScenePlanner(BaseModel):
    """
    Dynamic scene planner for complex narrative structures that adapts to the story's evolving needs.
    Creates scene requirements based on the advanced story structure and narrative continuity.
    """
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    story_planner: AdvancedStoryPlanner
    memory: EnhancedTheatricalMemory
    continuity_tracker: NarrativeContinuityTracker
    
    current_act: int = 1
    current_scene: int = 1
    total_acts: int = Field(3, ge=1, le=7)
    scenes_per_act: Dict[int, int] = Field(default_factory=dict)
    scene_sequence: List[Dict[str, Any]] = Field(default_factory=list)
    
    def __init__(self, story_planner: AdvancedStoryPlanner, memory: EnhancedTheatricalMemory, **data):
        """Initialize the dynamic scene planner with story structure and memory."""
        super().__init__(
            story_planner=story_planner,
            memory=memory,
            continuity_tracker=memory.continuity_tracker,
            **data
        )
        
        # Initialize scenes per act structure
        if not self.scenes_per_act:
            self._initialize_scene_distribution()
    
    def _initialize_scene_distribution(self) -> None:
        """Initialize the distribution of scenes across acts."""
        # Default to 3-5 scenes per act
        total_scenes = 0
        base_scenes_per_act = 4
        
        # Adjust based on complexity
        complexity_adjustments = {
            NarrativeComplexityLevel.SIMPLE: -1,
            NarrativeComplexityLevel.MODERATE: 0,
            NarrativeComplexityLevel.COMPLEX: 1,
            NarrativeComplexityLevel.VERY_COMPLEX: 2
        }
        
        complexity_adj = complexity_adjustments.get(self.story_planner.narrative_complexity, 0)
        
        # Special distribution for specific structures
        if self.story_planner.structure_type == NarrativeStructureType.EPISODIC:
            # Episodic tends to have more evenly distributed scenes
            for act in range(1, self.total_acts + 1):
                self.scenes_per_act[act] = base_scenes_per_act + complexity_adj
                total_scenes += self.scenes_per_act[act]
        elif self.story_planner.act_structure == ActStructureType.THREE_ACT:
            # Classic distribution with more scenes in the middle act
            self.scenes_per_act = {
                1: base_scenes_per_act - 1 + complexity_adj,
                2: base_scenes_per_act + 1 + complexity_adj,
                3: base_scenes_per_act - 1 + complexity_adj
            }
            # Adjust for acts beyond 3 if needed
            for act in range(4, self.total_acts + 1):
                self.scenes_per_act[act] = 3 + complexity_adj
        else:
            # Generic balanced distribution
            for act in range(1, self.total_acts + 1):
                self.scenes_per_act[act] = base_scenes_per_act + complexity_adj
        
        # Ensure scene counts match story beats when appropriate
        if self.story_planner.act_structure == ActStructureType.KISHŌTENKETSU and self.total_acts == 4:
            # Kishōtenketsu usually has 4 parts with 1-2 scenes each
            self.scenes_per_act = {1: 2, 2: 2, 3: 2, 4: 2}
            if self.story_planner.narrative_complexity in [NarrativeComplexityLevel.COMPLEX, 
                                                        NarrativeComplexityLevel.VERY_COMPLEX]:
                # Add more scenes for complex narratives
                self.scenes_per_act = {1: 3, 2: 3, 3: 2, 4: 2}
    
    def create_scene_requirements(self, act_number: int, scene_number: int) -> Dict[str, Any]:
        """Create detailed requirements for a specific scene based on narrative structure."""
        # Calculate position in the narrative
        position = self.story_planner.calculate_narrative_position(
            act_number, 
            scene_number, 
            self.total_acts, 
            self.scenes_per_act.get(act_number, 4)
        )
        
        # Get story elements needed at this position
        story_elements = self.story_planner.get_necessary_story_elements(position)
        
        # Get narrative context from memory
        character_states = {}
        for char_id, profile in self.memory.character_profiles.items():
            arc_summary = profile.get_arc_summary() if hasattr(profile, "get_arc_summary") else {"status": "unknown"}
            emotional_state = profile.get_current_emotional_state() if hasattr(profile, "get_current_emotional_state") else None
            
            character_states[char_id] = {
                "name": profile.name,
                "arc_status": arc_summary.get("status", "unknown"),
                "current_stage": arc_summary.get("current_stage", ""),
                "current_emotion": emotional_state.emotion if emotional_state else "",
                "relationships": getattr(profile, "relationships", {})
            }
        
        # Get relevant plot points
        unresolved_plots = []
        pending_foreshadowing = []
        
        if hasattr(self.continuity_tracker, "get_unresolved_plot_points"):
            unresolved_plots = self.continuity_tracker.get_unresolved_plot_points()
        
        if hasattr(self.continuity_tracker, "get_pending_foreshadowing"):
            pending_foreshadowing = self.continuity_tracker.get_pending_foreshadowing()
        
        # Get thematic status
        themes = {}
        if hasattr(self.continuity_tracker, "thematic_developments"):
            for theme, developments in self.continuity_tracker.thematic_developments.items():
                if developments:
                    themes[theme] = developments[-1].development
        
        # Build requirements
        requirements = {
            "act_number": act_number,
            "scene_number": scene_number,
            "narrative_position": position,
            "story_elements": story_elements,
            "character_states": character_states,
            "unresolved_plots": [point.dict() if hasattr(point, "dict") else point for point in unresolved_plots],
            "pending_foreshadowing": [element.dict() if hasattr(element, "dict") else element for element in pending_foreshadowing],
            "thematic_status": themes,
            "structure_type": self.story_planner.structure_type,
            "act_structure": self.story_planner.act_structure
        }
        
        # Add structure-specific requirements
        if self.story_planner.structure_type == NarrativeStructureType.NON_LINEAR:
            requirements["timeline_position"] = self._calculate_chronological_position(position)
        elif self.story_planner.structure_type == NarrativeStructureType.PARALLEL:
            requirements["active_threads"] = self._get_active_threads(position)
        
        return requirements
    
    def _calculate_chronological_position(self, narrative_position: float) -> float:
        """Calculate chronological position for non-linear narratives."""
        return self.story_planner._calculate_chronological_position(narrative_position)
    
    def _get_active_threads(self, position: float) -> List[str]:
        """Get active plot threads at the current position."""
        threads = self.story_planner.get_active_subplots(position)
        return [subplot.name for subplot in threads]
    
    def handle_scene_completion(self, scene_id: str, scene_content: str, act_number: int, scene_number: int) -> None:
        """Process a completed scene and update story tracking."""
        # Calculate position in the narrative
        position = self.story_planner.calculate_narrative_position(
            act_number, 
            scene_number, 
            self.total_acts, 
            self.scenes_per_act.get(act_number, 4)
        )
        
        # Update story beat tracking
        closest_beat = self.story_planner.get_story_beat_by_position(position)
        if closest_beat:
            self.story_planner.update_story_beat(closest_beat.name, scene_id)
        
        # Check for plot reversals
        pending_reversals = self.story_planner.get_pending_reversals(position)
        for reversal in pending_reversals:
            reversal.scene_id = scene_id
            reversal.complete = True
        
        # Update active subplots
        active_subplots = self.story_planner.get_active_subplots(position)
        for subplot in active_subplots:
            if scene_id not in subplot.scenes:
                subplot.scenes.append(scene_id)
        
        # Add to scene sequence
        self.scene_sequence.append({
            "scene_id": scene_id,
            "act_number": act_number,
            "scene_number": scene_number,
            "position": position,
            "beat": closest_beat.name if closest_beat else None
        })
    
    def get_narrative_requirements_for_llm(self, act_number: int, scene_number: int) -> str:
        """
        Generate narrative requirements formatted for an LLM prompt.
        
        Args:
            act_number: Current act number
            scene_number: Current scene number
            
        Returns:
            Formatted string with narrative requirements
        """
        requirements = self.create_scene_requirements(act_number, scene_number)
        story_elements = requirements.get("story_elements", {})
        current_beat = story_elements.get("current_beat", {})
        
        # Format the requirements as a string for an LLM prompt
        prompt_text = f"""
NARRATIVE STRUCTURE REQUIREMENTS:
Act: {act_number}, Scene: {scene_number}
Structure Type: {requirements['structure_type']}
Act Structure: {requirements['act_structure']}
Narrative Position: {requirements['narrative_position']:.2f} (0.0-1.0 scale)

CURRENT STORY BEAT:
Name: {current_beat.get('name', 'None')}
Description: {current_beat.get('description', 'None')}
Purpose: {current_beat.get('purpose', 'None')}
Emotional Tone: {current_beat.get('emotional_tone', 'None')}

ACTIVE ELEMENTS:
"""
        
        # Add active subplots
        active_subplots = story_elements.get("active_subplots", [])
        if active_subplots:
            prompt_text += "Active Subplots:\n"
            for subplot in active_subplots:
                prompt_text += f"- {subplot.get('name', 'Unknown')}: {subplot.get('description', '')}\n"
        
        # Add pending plot reversals
        pending_reversals = story_elements.get("pending_reversals", [])
        if pending_reversals:
            prompt_text += "\nPending Plot Reversals:\n"
            for reversal in pending_reversals:
                prompt_text += f"- {reversal.get('description', '')}\n"
        
        # Add unresolved plot points
        unresolved_plots = requirements.get("unresolved_plots", [])
        if unresolved_plots:
            prompt_text += "\nUnresolved Plot Points:\n"
            for plot in unresolved_plots[:3]:  # Limit to 3 for brevity
                desc = plot.get("description", "") if isinstance(plot, dict) else str(plot)
                prompt_text += f"- {desc}\n"
        
        # Add pending foreshadowing
        pending_foreshadowing = requirements.get("pending_foreshadowing", [])
        if pending_foreshadowing:
            prompt_text += "\nPending Foreshadowing Elements:\n"
            for element in pending_foreshadowing[:3]:  # Limit to 3 for brevity
                foreshadowing = element.get("foreshadowing", "") if isinstance(element, dict) else str(element)
                prompt_text += f"- {foreshadowing}\n"
        
        # Add thematic status
        themes = requirements.get("thematic_status", {})
        if themes:
            prompt_text += "\nThematic Elements:\n"
            for theme, status in list(themes.items())[:3]:  # Limit to 3 for brevity
                prompt_text += f"- {theme}: {status}\n"
        
        # Add structure-specific guidance
        if requirements['structure_type'] == NarrativeStructureType.NON_LINEAR:
            prompt_text += f"\nTimeline Position: {requirements.get('timeline_position', 0.5):.2f} (chronological timeline)\n"
        elif requirements['structure_type'] == NarrativeStructureType.PARALLEL:
            prompt_text += "\nActive Narrative Threads:\n"
            for thread in requirements.get("active_threads", []):
                prompt_text += f"- {thread}\n"
        
        return prompt_text


class StructureEnhancedPlaywright:
    """
    Enhanced playwright that incorporates advanced narrative structure awareness.
    Uses both the enhanced memory system and the advanced story structure system
    to generate more sophisticated and structured theatrical scenes.
    """
    
    def __init__(
        self, 
        memory: EnhancedTheatricalMemory,
        story_planner: AdvancedStoryPlanner,
        scene_planner: DynamicScenePlanner,
        llm_invoke_func: callable
    ):
        """
        Initialize the structure-enhanced playwright.
        
        Args:
            memory: Enhanced theatrical memory for character and narrative tracking
            story_planner: Advanced story planner for complex narrative structures
            scene_planner: Dynamic scene planner for adaptive scene requirements
            llm_invoke_func: Function to invoke the LLM for text generation
        """
        self.memory = memory
        self.story_planner = story_planner
        self.scene_planner = scene_planner
        self.llm_invoke_func = llm_invoke_func
        
    def generate_structured_scene(
        self, 
        act_number: int, 
        scene_number: int, 
        additional_requirements: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Generate a scene incorporating advanced narrative structure.
        
        Args:
            act_number: Current act number
            scene_number: Current scene number
            additional_requirements: Additional scene requirements
            
        Returns:
            Dict containing the generated scene content and metadata
        """
        # Get narrative requirements
        narrative_requirements = self.scene_planner.get_narrative_requirements_for_llm(act_number, scene_number)
        
        # Get character context
        character_context = self._build_character_context()
        
        # Combine requirements
        requirements = additional_requirements or {}
        
        # Create the generation prompt
        prompt = f"""Generate a theatrical scene that fulfills these structural requirements.

{narrative_requirements}

CHARACTER CONTEXT:
{character_context}

ADDITIONAL REQUIREMENTS:
"""
        
        for key, value in requirements.items():
            if isinstance(value, (list, tuple)):
                prompt += f"{key}:\n"
                for item in value:
                    prompt += f"- {item}\n"
            else:
                prompt += f"{key}: {value}\n"
        
        prompt += """
INSTRUCTIONS:
1. Create a scene that fulfills the current story beat requirements
2. Maintain character consistency based on their current state
3. Advance relevant plot threads and subplots
4. Honor the specified narrative structure type
5. Include stage directions in parentheses
6. Use standard dialogue format with character names followed by colons

FORMAT YOUR SCENE AS:
[Scene heading and description]

[Character dialogue and stage directions]

[Scene conclusion and transition]
"""

        # Generate the scene content
        response = self.llm_invoke_func(prompt)
        scene_content = str(response.content if hasattr(response, "content") else response)
        
        # Create scene identifier
        scene_id = f"act{act_number}_scene{scene_number}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Update tracking
        self.scene_planner.handle_scene_completion(scene_id, scene_content, act_number, scene_number)
        
        # Analyze scene for memory updates
        self._analyze_scene_for_memory(scene_id, scene_content)
        
        # Return the scene data
        return {
            "scene_id": scene_id,
            "act": act_number,
            "scene": scene_number,
            "content": scene_content,
            "narrative_position": self.story_planner.calculate_narrative_position(
                act_number, 
                scene_number, 
                self.scene_planner.total_acts, 
                self.scene_planner.scenes_per_act.get(act_number, 4)
            ),
            "current_beat": self._get_current_beat_name(act_number, scene_number)
        }
    
    def _build_character_context(self) -> str:
        """Build character context string from memory for LLM consumption."""
        context = ""
        
        for char_id, profile in self.memory.character_profiles.items():
            arc_summary = profile.get_arc_summary() if hasattr(profile, "get_arc_summary") else {"status": "unknown"}
            emotional_state = profile.get_current_emotional_state() if hasattr(profile, "get_current_emotional_state") else None
            
            context += f"{profile.name}:\n"
            context += f"- Current Arc Stage: {arc_summary.get('current_stage', 'Unknown')}\n"
            context += f"- Current Emotional State: {emotional_state.emotion if emotional_state else 'Unknown'}\n"
            
            # Add relationship information
            if hasattr(profile, "relationships") and profile.relationships:
                context += "- Key Relationships:\n"
                for other, status in list(profile.relationships.items())[:3]:  # Limit to 3 for brevity
                    context += f"  * {other}: {status}\n"
            
            # Add psychological attributes
            if hasattr(profile, "fears") and profile.fears:
                context += f"- Fears: {', '.join(profile.fears[:2])}\n"
            if hasattr(profile, "desires") and profile.desires:
                context += f"- Desires: {', '.join(profile.desires[:2])}\n"
            
            context += "\n"
        
        return context
    
    def _get_current_beat_name(self, act_number: int, scene_number: int) -> str:
        """Get the name of the current story beat based on narrative position."""
        position = self.story_planner.calculate_narrative_position(
            act_number, 
            scene_number, 
            self.scene_planner.total_acts, 
            self.scene_planner.scenes_per_act.get(act_number, 4)
        )
        
        beat = self.story_planner.get_story_beat_by_position(position)
        return beat.name if beat else "Unspecified Beat"
    
    def _analyze_scene_for_memory(self, scene_id: str, scene_content: str) -> None:
        """Analyze scene content and update memory system."""
        if not hasattr(self.memory, "update_narrative_from_scene"):
            return
            
        # Update narrative continuity
        self.memory.update_narrative_from_scene(scene_id, scene_content, self.llm_invoke_func)
        
        # Update character profiles
        for char_id in self.memory.character_profiles:
            if hasattr(self.memory, "update_character_from_scene"):
                self.memory.update_character_from_scene(char_id, scene_id, scene_content, self.llm_invoke_func)