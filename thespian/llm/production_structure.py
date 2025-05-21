"""
Production structure management for theatrical performances.
"""

from typing import Dict, Any, List, Optional, Callable
from pydantic import BaseModel, Field, ConfigDict
from thespian.llm import LLMManager
from thespian.llm.theatrical_memory import TheatricalMemory
from thespian.llm.theatrical_advisors import TheatricalAdvisor, AdvisorFeedback, NarrativeContinuityAdvisor
import time


class ActRequirements(BaseModel):
    """
    Requirements for a theatrical act.

    Attributes:
        act_number (int): The act's sequence number in the production.
        min_scenes (int): Minimum number of scenes in the act.
        max_scenes (int): Maximum number of scenes in the act.
        target_duration (int): Target duration of the act in minutes.
        theme (str): Thematic focus of the act.
        dramatic_arc (str): The dramatic arc covered by the act.
        required_elements (Dict[str, List[str]]): Required characters, props, lighting, sound, etc.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    act_number: int
    min_scenes: int = 2
    max_scenes: int = 5
    target_duration: int  # in minutes
    theme: str
    dramatic_arc: str
    required_elements: Dict[str, List[str]] = Field(default_factory=dict)  # characters, props, lighting, sound
    
    def __init__(self, **data):
        super().__init__(**data)


class ProductionStructure(BaseModel):
    """
    Overall structure for a theatrical production.

    Attributes:
        title (str): Title of the production.
        num_acts (int): Number of acts in the production (1-5).
        total_target_duration (int): Total duration in minutes.
        style (str): The production's style (e.g., tragedy, comedy).
        target_audience (str): Intended audience.
        acts (List[ActRequirements]): List of act requirements.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    title: str
    num_acts: int = Field(ge=1, le=5)
    total_target_duration: int  # in minutes
    style: str
    target_audience: str
    acts: List[ActRequirements] = Field(default_factory=list)
    
    def __init__(self, **data):
        super().__init__(**data)
        if not self.acts:
            self.initialize_default_acts()

    def initialize_default_acts(self) -> None:
        """
        Initialize acts with default dramatic arcs and durations.

        This method populates the 'acts' list based on the total duration and number of acts,
        assigning each act a theme and dramatic arc for narrative pacing.
        """
        act_durations = {
            1: int(self.total_target_duration * 0.3),  # 30% of total
            2: int(self.total_target_duration * 0.4),  # 40% of total
            3: int(self.total_target_duration * 0.3),  # 30% of total
            4: int(self.total_target_duration * 0.25),  # 25% of total
            5: int(self.total_target_duration * 0.15),  # 15% of total
        }

        dramatic_arcs = {
            1: "Exposition and Rising Action",
            2: "Rising Action and Complications",
            3: "Climax and Resolution",
            4: "Extended Resolution and Denouement",
            5: "Final Resolution and Epilogue"
        }

        self.acts = [
            ActRequirements(
                act_number=i + 1,
                target_duration=act_durations.get(i + 1, self.total_target_duration // self.num_acts),
                theme=f"Act {i + 1} Theme",
                dramatic_arc=dramatic_arcs.get(i + 1, "Dramatic Development")
            )
            for i in range(self.num_acts)
        ]


class TimingAdvisor(TheatricalAdvisor):
    """
    Advisor specialized in timing and pacing analysis.

    Methods:
        analyze(content, context): Analyze a scene's pacing and timing, returning structured feedback.

    Notes:
        Uses LLM to estimate scene duration and provide expert suggestions for improvement.
    """
    
    def __init__(self, llm_manager: LLMManager, memory: TheatricalMemory):
        super().__init__(
            name="Timing Advisor",
            expertise="Timing and pacing analysis",
            llm_manager=llm_manager,
            memory=memory
        )
    
    def analyze(self, content: str, context: Dict[str, Any]) -> AdvisorFeedback:
        """
        Analyze the timing and pacing of a scene.

        Args:
            content (str): The text of the scene to analyze.
            context (Dict[str, Any]): Additional context, such as target duration.

        Returns:
            AdvisorFeedback: Structured feedback including score, suggestions, and priority.
        """
        llm = self.get_llm()
        
        # Estimate scene duration based on content length and complexity
        estimated_duration = self._estimate_duration(content)
        target_duration = context.get("target_duration", 0)
        
        prompt = f"""As a timing and pacing expert, analyze this theatrical scene:

Scene:
{content}

Target Duration: {target_duration} minutes
Estimated Duration: {estimated_duration:.1f} minutes

Consider:
1. Pacing and rhythm
2. Scene transitions
3. Emotional beats
4. Audience engagement
5. Timing balance

Provide a detailed analysis with:
1. A score from 0.0 to 1.0
2. Specific feedback on timing and pacing
3. Concrete suggestions for improvement
4. Specific examples from the scene that demonstrate strengths or areas for improvement
5. A priority level (1-5, where 1 is highest priority)

Format your response as:
SCORE: [0.0-1.0]
FEEDBACK: [detailed feedback]
SUGGESTIONS:
- [suggestion 1]
- [suggestion 2]
EXAMPLES:
- [example 1]
- [example 2]
PRIORITY: [1-5]"""

        response = llm.invoke(prompt)
        
        # Parse response into structured feedback
        lines = response.content.split('\n')
        score = 0.7  # Default score
        feedback = "Timing and pacing need adjustment"  # Default feedback
        suggestions = []
        examples = []
        priority = 2  # Default priority
        
        current_section = None
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('SCORE:'):
                try:
                    score = float(line.split(':')[1].strip())
                except (ValueError, IndexError):
                    pass
            elif line.startswith('FEEDBACK:'):
                feedback = line.split(':')[1].strip()
            elif line.startswith('SUGGESTIONS:'):
                current_section = 'suggestions'
            elif line.startswith('EXAMPLES:'):
                current_section = 'examples'
            elif line.startswith('PRIORITY:'):
                try:
                    priority = int(line.split(':')[1].strip())
                except (ValueError, IndexError):
                    pass
            elif line.startswith('- '):
                if current_section == 'suggestions':
                    suggestions.append(line[2:])
                elif current_section == 'examples':
                    examples.append(line[2:])
        
        return AdvisorFeedback(
            score=score,
            feedback=feedback,
            suggestions=suggestions,
            specific_examples=examples,
            priority=priority
        )
    
    def _estimate_duration(self, content: str) -> float:
        """Estimate scene duration based on content length and complexity."""
        # Simple heuristic: 1 minute per 150 words, adjusted for complexity
        words = len(content.split())
        base_duration = words / 150.0
        
        # Adjust for complexity factors
        complexity_factors = {
            "dialogue": len([line for line in content.split('\n') if ':' in line]) / words,
            "stage_directions": len([line for line in content.split('\n') if line.strip().startswith('(')]) / words,
            "emotional_beats": len([word for word in content.lower().split() if word in ['suddenly', 'dramatically', 'emotionally']]) / words
        }
        
        complexity_multiplier = 1.0 + sum(complexity_factors.values())
        return base_duration * complexity_multiplier


class ActManager(BaseModel):
    """
    Manages the generation and coordination of acts.
    
    Responsibilities:
        - Generates scenes for each act using the LLMManager
        - Uses TimingAdvisor to analyze and enhance scene pacing
        - Tracks timing metrics for generation, analysis, and enhancement phases
        - Ensures narrative continuity across acts
    """
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    llm_manager: LLMManager
    memory: TheatricalMemory
    timing_advisor: Optional[TimingAdvisor] = None
    narrative_advisor: Optional[NarrativeContinuityAdvisor] = None
    current_act: int = 0
    current_scene: int = 0
    act_scenes: Dict[int, List[Dict[str, Any]]] = Field(default_factory=dict)
    timing_metrics: Dict[str, float] = Field(default_factory=lambda: {
        "scene_generation": 0.0,
        "timing_analysis": 0.0,
        "scene_enhancement": 0.0,
        "act_transition": 0.0,
        "continuity_check": 0.0
    })
    character_arcs: Dict[str, List[str]] = Field(default_factory=dict)
    plot_points: List[str] = Field(default_factory=list)
    previous_scenes: List[str] = Field(default_factory=list)
    
    def __init__(self, llm_manager: LLMManager, memory: TheatricalMemory):
        """
        Initialize ActManager.
        
        Args:
            llm_manager (LLMManager): The model manager for LLM selection and invocation
            memory (TheatricalMemory): The shared memory object for the production
        """
        timing_advisor = TimingAdvisor(
            name="Timing Advisor",
            expertise="Timing and pacing analysis",
            llm_manager=llm_manager,
            memory=memory
        )
        narrative_advisor = NarrativeContinuityAdvisor(
            name="Narrative Continuity Advisor",
            expertise="Maintaining narrative continuity and scene uniqueness",
            llm_manager=llm_manager,
            memory=memory
        )
        super().__init__(
            llm_manager=llm_manager,
            memory=memory,
            timing_advisor=timing_advisor,
            narrative_advisor=narrative_advisor
        )
    
    def generate_act(self, act_number: int, requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate a complete act with narrative continuity.
        
        Args:
            act_number (int): The act number to generate
            requirements (Dict[str, Any]): Requirements for the act
            
        Returns:
            List[Dict[str, Any]]: List of generated scenes
        """
        self.current_act = act_number
        scenes = []
        
        # Generate scenes for the act
        for scene_number in range(1, 6):
            self.current_scene = scene_number
            logger.info(f"Generating Act {act_number}, Scene {scene_number}")
            
            # Update scene requirements with narrative context
            scene_requirements = {
                **requirements,
                "narrative_context": {
                    "previous_scenes": self.previous_scenes,
                    "character_arcs": self.character_arcs,
                    "plot_points": self.plot_points,
                    "act_number": act_number,
                    "scene_number": scene_number
                }
            }
            
            # Generate scene
            start_time = time.time()
            scene = self._generate_scene(scene_requirements)
            self.timing_metrics["scene_generation"] += time.time() - start_time
            
            # Check narrative continuity
            start_time = time.time()
            is_unique = self.narrative_advisor.validate_scene_uniqueness(
                scene["content"],
                self.previous_scenes
            )
            if not is_unique:
                logger.warning(f"Scene {scene_number} is not unique enough, regenerating...")
                scene = self._generate_scene(scene_requirements)
            
            # Track character arcs
            self.character_arcs = self.narrative_advisor.track_character_arcs(
                scene["content"],
                self.character_arcs
            )
            
            # Verify plot progression
            advances_plot, new_points = self.narrative_advisor.verify_plot_progression(
                scene["content"],
                self.plot_points
            )
            if not advances_plot:
                logger.warning(f"Scene {scene_number} does not advance the plot, regenerating...")
                scene = self._generate_scene(scene_requirements)
            self.plot_points.extend(new_points)
            
            self.timing_metrics["continuity_check"] += time.time() - start_time
            
            # Analyze timing
            start_time = time.time()
            timing_feedback = self.timing_advisor.analyze(scene["content"], scene_requirements)
            self.timing_metrics["timing_analysis"] += time.time() - start_time
            
            # Enhance scene based on timing feedback
            start_time = time.time()
            enhanced_scene = self._enhance_scene(scene, timing_feedback)
            self.timing_metrics["scene_enhancement"] += time.time() - start_time
            
            # Update narrative tracking
            self.previous_scenes.append(enhanced_scene["content"])
            scenes.append(enhanced_scene)
        
        # Handle act transition
        start_time = time.time()
        self._handle_act_transition(act_number, scenes)
        self.timing_metrics["act_transition"] += time.time() - start_time
        
        self.act_scenes[act_number] = scenes
        return scenes
    
    def _handle_act_transition(self, act_number: int, scenes: List[Dict[str, Any]]) -> None:
        """
        Handle the transition between acts.
        
        Args:
            act_number (int): The current act number
            scenes (List[Dict[str, Any]]): The scenes in the current act
        """
        if act_number < 3:  # Only handle transitions between acts 1-2 and 2-3
            llm = self.llm_manager.get_llm("ollama")
            
            prompt = f"""Analyze the transition from Act {act_number} to Act {act_number + 1}:

Act {act_number} Scenes:
{chr(10).join(f'Scene {i+1}:{chr(10)}{scene["content"]}' for i, scene in enumerate(scenes))}

Character Arcs:
{chr(10).join(f'{char}:{chr(10)}{chr(10).join(f"- {point}" for point in points)}' for char, points in self.character_arcs.items())}

Plot Points:
{chr(10).join(f'- {point}' for point in self.plot_points)}

Provide guidance for Act {act_number + 1}:
1. How should Act {act_number + 1} build upon Act {act_number}?
2. What character developments should be continued?
3. What plot threads should be resolved or introduced?
4. How should the themes be developed?
5. What emotional progression should occur?

Format response as:
TRANSITION_ANALYSIS:
[detailed analysis]

ACT_{act_number + 1}_GUIDANCE:
[guidance for next act]"""

            response = llm.invoke(prompt)
            
            # Store transition analysis in memory
            self.memory.store_transition_analysis(act_number, response.content)
    
    def get_timing_metrics(self) -> Dict[str, float]:
        """
        Get timing metrics for the act generation process.
        
        Returns:
            Dict[str, float]: Timing metrics for generation, analysis, and enhancement
        """
        return self.timing_metrics
    
    def get_narrative_state(self) -> Dict[str, Any]:
        """
        Get the current state of narrative elements.
        
        Returns:
            Dict[str, Any]: Current character arcs, plot points, and scene history
        """
        return {
            "character_arcs": self.character_arcs,
            "plot_points": self.plot_points,
            "previous_scenes": self.previous_scenes
        }

    def _generate_scene(self, act_requirements: ActRequirements, scene_num: int) -> Dict[str, Any]:
        """
        Generate a single scene for an act.

        Args:
            act_requirements (ActRequirements): Requirements for the act.
            scene_num (int): The scene number within the act.

        Returns:
            Dict[str, Any]: The generated scene content and metadata.
        """
        # NOTE: The model used here is currently hardcoded to 'ollama'.
        # For agent-specific model selection, use llm_manager.get_model_info(agent_id).
        llm = self.llm_manager.get_llm("ollama")

        prompt = f"""Generate a theatrical scene for Act {act_requirements.act_number}, Scene {scene_num}:

Act Theme: {act_requirements.theme}
Dramatic Arc: {act_requirements.dramatic_arc}
Target Duration: {act_requirements.target_duration / act_requirements.min_scenes:.1f} minutes
Required Elements:
Characters: {', '.join(act_requirements.required_elements.get('characters', []))}
Props: {', '.join(act_requirements.required_elements.get('props', []))}
Lighting: {', '.join(act_requirements.required_elements.get('lighting', []))}
Sound: {', '.join(act_requirements.required_elements.get('sound', []))}

Create a scene that advances the act's dramatic arc and maintains appropriate pacing."""

        response = llm.invoke(prompt)
        return {
            "act": act_requirements.act_number,
            "scene": scene_num,
            "content": response.content,
            "requirements": act_requirements.dict()
        }

    def _enhance_scene(self, scene: Dict[str, Any], feedback: AdvisorFeedback) -> Dict[str, Any]:
        """
        Enhance a scene based on timing feedback.

        Args:
            scene (Dict[str, Any]): The original scene data.
            feedback (AdvisorFeedback): Timing and pacing feedback.

        Returns:
            Dict[str, Any]: The enhanced scene.
        """
        llm = self.llm_manager.get_llm("ollama")

        prompt = f"""Enhance this theatrical scene based on timing feedback:

Original Scene:
{scene['content']}

Feedback:
{feedback.feedback}

Suggestions:
{chr(10).join(f'- {suggestion}' for suggestion in feedback.suggestions)}

Maintain the scene's core elements while adjusting its pacing and timing."""

        response = llm.invoke(prompt)
        scene["content"] = response.content
        return scene