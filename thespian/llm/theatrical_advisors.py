"""
Theatrical advisors for helping with production quality.

This module contains theatrical advisors that help with various aspects of theatrical productions,
such as timing, dialogue, characterization, and narrative continuity.
"""

from typing import Dict, Any, List, Optional, Union, Type
from pydantic import BaseModel, Field, ConfigDict
from thespian.llm import LLMManager
from thespian.llm.theatrical_memory import TheatricalMemory
import logging
import json
import time
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvisorType(str, Enum):
    """Types of theatrical advisors."""
    NARRATIVE = "narrative"
    DIALOGUE = "dialogue"
    CHARACTER = "character"
    SCENIC = "scenic"
    PACING = "pacing"
    THEMATIC = "thematic"


class AdvisorFeedback(BaseModel):
    """
    Feedback from a theatrical advisor.
    
    Attributes:
        score (float): Numeric score from 0.0 to 1.0.
        feedback (str): Textual feedback.
        suggestions (List[str]): List of specific suggestions.
        specific_examples (List[str]): Examples from the content.
        priority (int): Priority level (1-5, with 1 being highest).
    """
    
    score: float = Field(ge=0.0, le=1.0)
    feedback: str
    suggestions: List[str] = Field(default_factory=list)
    specific_examples: List[str] = Field(default_factory=list)
    priority: int = Field(ge=1, le=5)


class TheatricalAdvisor(BaseModel):
    """
    Base class for theatrical advisors.
    
    Attributes:
        name (str): Name of the advisor.
        expertise (str): Area of expertise.
        llm_manager (LLMManager): Manager for LLM interactions.
        memory (TheatricalMemory): Production memory.
    """
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    name: str
    expertise: str
    llm_manager: LLMManager
    memory: TheatricalMemory
    
    def analyze(self, content: str, context: Dict[str, Any]) -> AdvisorFeedback:
        """
        Analyze content and provide feedback.
        
        Args:
            content (str): The content to analyze.
            context (Dict[str, Any]): Additional context for analysis.
            
        Returns:
            AdvisorFeedback: Structured feedback.
        """
        raise NotImplementedError("Subclasses must implement analyze method")
    
    def get_llm(self, model_name: str = "ollama"):
        """Get the LLM for this advisor."""
        return self.llm_manager.get_llm(model_name)


class NarrativeAdvisor(TheatricalAdvisor):
    """
    Advisor specialized in narrative structure and plot coherence.
    """
    
    def __init__(self, name: str, llm_manager: LLMManager, memory: TheatricalMemory):
        """Initialize the narrative advisor."""
        super().__init__(
            name=name,
            expertise=AdvisorType.NARRATIVE,
            llm_manager=llm_manager,
            memory=memory
        )
    
    def analyze(self, content: str, context: Dict[str, Any]) -> AdvisorFeedback:
        """
        Analyze narrative aspects of a scene.
        
        Args:
            content (str): The text of the scene to analyze.
            context (Dict[str, Any]): Additional context for analysis.
            
        Returns:
            AdvisorFeedback: Structured feedback including score, suggestions, and priority.
        """
        llm = self.get_llm()
        
        # Get act and scene information from context
        act_number = context.get("act_number", 1)
        scene_number = context.get("scene_number", 1)
        
        # Get story outline if available
        story_outline_summary = "Story outline unavailable"
        if hasattr(self.memory, "story_outline") and self.memory.story_outline:
            story_outline = self.memory.story_outline
            story_outline_summary = f"Title: {story_outline.title}\n"
            
            # Add act information
            if act_number <= len(story_outline.acts):
                act = story_outline.acts[act_number - 1]
                story_outline_summary += f"Act {act_number}: {act.get('description', 'No description')}\n"
                
                # Add key events for the act
                if "key_events" in act and act["key_events"]:
                    if scene_number <= len(act["key_events"]):
                        story_outline_summary += f"Scene {scene_number} outline: {act['key_events'][scene_number - 1]}\n"
        
        # Get previous scenes summary
        previous_scenes_summary = context.get("previous_scenes_summary", "No previous scenes available.")
        
        prompt = f"""Analyze the narrative structure in this theatrical scene:

Scene:
{content}

Story Context:
{story_outline_summary}

Previous Scenes:
{previous_scenes_summary}

Consider:
1. Plot progression and pacing
2. Narrative coherence with the larger story
3. Scene purpose and contribution to the plot
4. Character motivations and consistency
5. Conflict development
6. Scene resolution

Provide a detailed analysis with:
1. A score from 0.0 to 1.0 rating the narrative quality
2. Specific feedback on narrative structure
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
        return self._parse_advisor_response(response.content)
    
    def _parse_advisor_response(self, response_text: str) -> AdvisorFeedback:
        """Parse the advisor response into structured feedback."""
        lines = response_text.split('\n')
        score = 0.7  # Default score
        feedback = "Narrative structure needs improvement"  # Default feedback
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


class DialogueAdvisor(TheatricalAdvisor):
    """
    Advisor specialized in dialogue quality and character voice.
    """
    
    def __init__(self, name: str, llm_manager: LLMManager, memory: TheatricalMemory):
        """Initialize the dialogue advisor."""
        super().__init__(
            name=name,
            expertise=AdvisorType.DIALOGUE,
            llm_manager=llm_manager,
            memory=memory
        )
    
    def analyze(self, content: str, context: Dict[str, Any]) -> AdvisorFeedback:
        """
        Analyze dialogue aspects of a scene.
        
        Args:
            content (str): The text of the scene to analyze.
            context (Dict[str, Any]): Additional context for analysis.
            
        Returns:
            AdvisorFeedback: Structured feedback including score, suggestions, and priority.
        """
        llm = self.get_llm()
        
        # Get character information
        characters = []
        if hasattr(self.memory, "character_profiles"):
            for char_id, profile in self.memory.character_profiles.items():
                characters.append({
                    "name": profile.name,
                    "background": getattr(profile, "background", ""),
                    "voice": getattr(profile, "voice", ""),
                    "personality": getattr(profile, "personality", "")
                })
        
        characters_info = json.dumps(characters, indent=2) if characters else "No character information available."
        
        prompt = f"""Analyze the dialogue in this theatrical scene:

Scene:
{content}

Character Information:
{characters_info}

Analyze the dialogue for:
1. Character voice consistency
2. Dialogue authenticity and naturalism
3. Subtext and depth
4. Pacing and rhythm
5. Purpose and advancement of plot through dialogue
6. Character relationships expressed through dialogue

Provide a detailed analysis with:
1. A score from 0.0 to 1.0 rating the dialogue quality
2. Specific feedback on dialogue strengths and weaknesses
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
        return self._parse_advisor_response(response.content)
    
    def _parse_advisor_response(self, response_text: str) -> AdvisorFeedback:
        """Parse the advisor response into structured feedback."""
        lines = response_text.split('\n')
        score = 0.7  # Default score
        feedback = "Dialogue needs improvement"  # Default feedback
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


class CharacterAdvisor(TheatricalAdvisor):
    """
    Advisor specialized in character development and consistency.
    """
    
    def __init__(self, name: str, llm_manager: LLMManager, memory: TheatricalMemory):
        """Initialize the character advisor."""
        super().__init__(
            name=name,
            expertise=AdvisorType.CHARACTER,
            llm_manager=llm_manager,
            memory=memory
        )
    
    def analyze(self, content: str, context: Dict[str, Any]) -> AdvisorFeedback:
        """
        Analyze character aspects of a scene.
        
        Args:
            content (str): The text of the scene to analyze.
            context (Dict[str, Any]): Additional context for analysis.
            
        Returns:
            AdvisorFeedback: Structured feedback including score, suggestions, and priority.
        """
        llm = self.get_llm()
        
        # Get character arcs if available
        character_arcs = {}
        if hasattr(self.memory, "character_profiles"):
            for char_id, profile in self.memory.character_profiles.items():
                if hasattr(profile, "development_arc"):
                    character_arcs[profile.name] = [
                        {"stage": arc.stage, "description": arc.description}
                        for arc in profile.development_arc
                    ]
        
        characters_info = json.dumps(character_arcs, indent=2) if character_arcs else "No character arc information available."
        
        prompt = f"""Analyze the character development in this theatrical scene:

Scene:
{content}

Character Arcs:
{characters_info}

Analyze the characters for:
1. Character consistency with established traits
2. Growth and development within arcs
3. Motivations and goals
4. Relationships and interactions
5. Emotional authenticity
6. Actions aligned with character traits

Provide a detailed analysis with:
1. A score from 0.0 to 1.0 rating the character development quality
2. Specific feedback on character strengths and weaknesses
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
        return self._parse_advisor_response(response.content)
    
    def _parse_advisor_response(self, response_text: str) -> AdvisorFeedback:
        """Parse the advisor response into structured feedback."""
        lines = response_text.split('\n')
        score = 0.7  # Default score
        feedback = "Character development needs improvement"  # Default feedback
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


class ScenicAdvisor(TheatricalAdvisor):
    """
    Advisor specialized in scenic elements, staging, and technical aspects.
    """
    
    def __init__(self, name: str, llm_manager: LLMManager, memory: TheatricalMemory):
        """Initialize the scenic advisor."""
        super().__init__(
            name=name,
            expertise=AdvisorType.SCENIC,
            llm_manager=llm_manager,
            memory=memory
        )
    
    def analyze(self, content: str, context: Dict[str, Any]) -> AdvisorFeedback:
        """
        Analyze scenic aspects of a scene.
        
        Args:
            content (str): The text of the scene to analyze.
            context (Dict[str, Any]): Additional context for analysis.
            
        Returns:
            AdvisorFeedback: Structured feedback including score, suggestions, and priority.
        """
        llm = self.get_llm()
        
        # Get technical requirements
        technical_reqs = context.get("technical_requirements", {})
        technical_info = json.dumps(technical_reqs, indent=2) if technical_reqs else "No technical requirements specified."
        
        prompt = f"""Analyze the scenic elements in this theatrical scene:

Scene:
{content}

Technical Requirements:
{technical_info}

Analyze the scene for:
1. Staging clarity and effectiveness
2. Use of space and movement
3. Integration of technical elements (lighting, sound, props)
4. Visual storytelling
5. Atmosphere and mood creation
6. Practical feasibility of staging

Provide a detailed analysis with:
1. A score from 0.0 to 1.0 rating the scenic quality
2. Specific feedback on scenic strengths and weaknesses
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
        return self._parse_advisor_response(response.content)
    
    def _parse_advisor_response(self, response_text: str) -> AdvisorFeedback:
        """Parse the advisor response into structured feedback."""
        lines = response_text.split('\n')
        score = 0.7  # Default score
        feedback = "Scenic elements need improvement"  # Default feedback
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


class PacingAdvisor(TheatricalAdvisor):
    """
    Advisor specialized in scene pacing and timing.
    """
    
    def __init__(self, name: str, llm_manager: LLMManager, memory: TheatricalMemory):
        """Initialize the pacing advisor."""
        super().__init__(
            name=name,
            expertise=AdvisorType.PACING,
            llm_manager=llm_manager,
            memory=memory
        )
    
    def analyze(self, content: str, context: Dict[str, Any]) -> AdvisorFeedback:
        """
        Analyze pacing aspects of a scene.
        
        Args:
            content (str): The text of the scene to analyze.
            context (Dict[str, Any]): Additional context for analysis.
            
        Returns:
            AdvisorFeedback: Structured feedback including score, suggestions, and priority.
        """
        llm = self.get_llm()
        
        # Get act and scene information
        act_number = context.get("act_number", 1)
        scene_number = context.get("scene_number", 1)
        
        # Determine expected pacing based on act and scene position
        expected_pacing = "moderate"
        if act_number == 1:
            if scene_number == 1:
                expected_pacing = "slower, establishing"
            elif scene_number == 5:
                expected_pacing = "building to act transition"
        elif act_number == 2:
            if scene_number == 3:
                expected_pacing = "midpoint climax"
            elif scene_number == 5:
                expected_pacing = "heightened tension"
        elif act_number == 3:
            if scene_number < 3:
                expected_pacing = "building tension"
            elif scene_number == 5:
                expected_pacing = "climactic resolution"
        
        prompt = f"""Analyze the pacing in this theatrical scene:

Scene:
{content}

Act: {act_number}, Scene: {scene_number}
Expected Pacing: {expected_pacing}

Analyze the scene for:
1. Overall rhythm and flow
2. Tension building and release
3. Scene length and density
4. Dialogue pacing
5. Action and movement pacing
6. Appropriate pacing for scene position in the larger structure

Provide a detailed analysis with:
1. A score from 0.0 to 1.0 rating the pacing quality
2. Specific feedback on pacing strengths and weaknesses
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
        return self._parse_advisor_response(response.content)
    
    def _parse_advisor_response(self, response_text: str) -> AdvisorFeedback:
        """Parse the advisor response into structured feedback."""
        lines = response_text.split('\n')
        score = 0.7  # Default score
        feedback = "Pacing needs adjustment"  # Default feedback
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


class ThematicAdvisor(TheatricalAdvisor):
    """
    Advisor specialized in thematic development and symbolism.
    """
    
    def __init__(self, name: str, llm_manager: LLMManager, memory: TheatricalMemory):
        """Initialize the thematic advisor."""
        super().__init__(
            name=name,
            expertise=AdvisorType.THEMATIC,
            llm_manager=llm_manager,
            memory=memory
        )
    
    def analyze(self, content: str, context: Dict[str, Any]) -> AdvisorFeedback:
        """
        Analyze thematic aspects of a scene.
        
        Args:
            content (str): The text of the scene to analyze.
            context (Dict[str, Any]): Additional context for analysis.
            
        Returns:
            AdvisorFeedback: Structured feedback including score, suggestions, and priority.
        """
        llm = self.get_llm()
        
        # Get themes if available
        themes = []
        if hasattr(self.memory, "story_outline") and self.memory.story_outline:
            if hasattr(self.memory.story_outline, "themes"):
                themes = self.memory.story_outline.themes
        
        themes_info = json.dumps(themes, indent=2) if themes else "No theme information available."
        
        prompt = f"""Analyze the thematic elements in this theatrical scene:

Scene:
{content}

Established Themes:
{themes_info}

Analyze the scene for:
1. Theme development and exploration
2. Symbolism and motifs
3. Thematic consistency
4. Subtext and layered meaning
5. Integration of themes with character and plot
6. Thematic evolution across the narrative

Provide a detailed analysis with:
1. A score from 0.0 to 1.0 rating the thematic quality
2. Specific feedback on thematic strengths and weaknesses
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
        return self._parse_advisor_response(response.content)
    
    def _parse_advisor_response(self, response_text: str) -> AdvisorFeedback:
        """Parse the advisor response into structured feedback."""
        lines = response_text.split('\n')
        score = 0.7  # Default score
        feedback = "Thematic development needs enhancement"  # Default feedback
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


class NarrativeContinuityAdvisor(TheatricalAdvisor):
    """
    Advisor specialized in maintaining narrative continuity and scene uniqueness.
    
    Methods:
        analyze(content, context): Analyze narrative continuity, returning structured feedback.
        validate_scene_uniqueness(content, previous_scenes): Check if a scene is sufficiently unique.
        track_character_arcs(content, current_arcs): Update character arc tracking.
        verify_plot_progression(content, plot_points): Check if the scene advances the plot.
    """
    
    def __init__(self, name: str, expertise: str, llm_manager: LLMManager, memory: TheatricalMemory):
        """Initialize the narrative continuity advisor."""
        super().__init__(
            name=name,
            expertise=expertise,
            llm_manager=llm_manager,
            memory=memory
        )
    
    def analyze(self, content: str, context: Dict[str, Any]) -> AdvisorFeedback:
        """
        Analyze narrative continuity aspects of a scene.
        
        Args:
            content (str): The text of the scene to analyze.
            context (Dict[str, Any]): Additional context for analysis.
            
        Returns:
            AdvisorFeedback: Structured feedback including score, suggestions, and priority.
        """
        llm = self.get_llm()
        
        prompt = f"""Analyze the narrative continuity in this theatrical scene:

Scene:
{content}

Previous Scenes Context:
{context.get('previous_scenes_summary', 'No previous scenes available.')}

Consider:
1. Character consistency
2. Plot continuity
3. Narrative arc development
4. Logical progression from previous scenes
5. Thematic consistency

Provide a detailed analysis with:
1. A score from 0.0 to 1.0
2. Specific feedback on narrative continuity
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
        feedback = "Narrative continuity needs improvement"  # Default feedback
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
    
    def validate_scene_uniqueness(self, content: str, previous_scenes: List[str]) -> bool:
        """
        Check if a scene is sufficiently unique compared to previous scenes.
        
        Args:
            content (str): The content of the scene to check.
            previous_scenes (List[str]): Previous scene contents.
            
        Returns:
            bool: True if the scene is unique enough, False otherwise.
        """
        if not previous_scenes:
            return True
            
        llm = self.get_llm()
        
        # Create a summary of previous scenes for context
        previous_scenes_summary = ""
        for i, scene in enumerate(previous_scenes[-3:]):  # Only use the last 3 scenes for efficiency
            previous_scenes_summary += f"Scene {i+1}: {scene[:200]}...\n"
        
        prompt = f"""Analyze if this new scene is sufficiently unique compared to previous scenes:

New Scene:
{content}

Previous Scenes:
{previous_scenes_summary}

Evaluate the uniqueness of the new scene compared to previous scenes. Consider:
1. Plot development (is it advancing the story or repeating?)
2. Character dynamics (are interactions fresh or repetitive?)
3. Setting and atmosphere (is it a new environment or recycled?)
4. Dialogue patterns (is the dialogue distinct or reusing patterns?)
5. Emotional tone (does it bring new emotional elements?)

Provide your assessment as a single score from 0.0 (completely redundant) to 1.0 (entirely unique), followed by brief reasoning.
FORMAT: UNIQUENESS_SCORE: [0.0-1.0]
REASONING: [brief explanation]"""

        response = llm.invoke(prompt)
        
        # Parse response to get uniqueness score
        uniqueness_score = 0.7  # Default, somewhat unique
        
        for line in response.content.split('\n'):
            if line.startswith('UNIQUENESS_SCORE:'):
                try:
                    uniqueness_score = float(line.split(':')[1].strip())
                except (ValueError, IndexError):
                    pass
        
        # Consider a scene unique enough if score is above 0.6
        return uniqueness_score > 0.6
    
    def track_character_arcs(self, content: str, current_arcs: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """
        Update character arc tracking based on scene content.
        
        Args:
            content (str): The content of the scene.
            current_arcs (Dict[str, List[str]]): Current character arcs.
            
        Returns:
            Dict[str, List[str]]: Updated character arcs.
        """
        llm = self.get_llm()
        
        # Create context from current arcs
        arcs_context = ""
        for char, points in current_arcs.items():
            arcs_context += f"{char}:\n"
            for point in points:
                arcs_context += f"- {point}\n"
            arcs_context += "\n"
        
        prompt = f"""Analyze character development in this scene:

Scene:
{content}

Current Character Arcs:
{arcs_context if arcs_context else "No character arcs tracked yet."}

Extract key character development points from this scene. For each character that appears in the scene:
1. Identify any significant changes in the character's emotions, beliefs, or relationships
2. Note key decisions or actions that impact their arc
3. Recognize any revelations or realizations the character experiences

Format your response as:
CHARACTER_NAME_1:
- [development point 1]
- [development point 2]

CHARACTER_NAME_2:
- [development point 1]
- [development point 2]"""

        response = llm.invoke(prompt)
        
        # Parse response to update character arcs
        updated_arcs = dict(current_arcs)  # Start with existing arcs
        
        current_character = None
        for line in response.content.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            if ':' in line and not line.startswith('-'):
                current_character = line.split(':')[0].strip()
                if current_character not in updated_arcs:
                    updated_arcs[current_character] = []
            elif line.startswith('-') and current_character:
                point = line[2:].strip()
                if point and point not in updated_arcs[current_character]:
                    updated_arcs[current_character].append(point)
        
        return updated_arcs
    
    def verify_plot_progression(self, content: str, plot_points: List[str]) -> tuple[bool, List[str]]:
        """
        Check if the scene advances the plot and extract new plot points.
        
        Args:
            content (str): The content of the scene.
            plot_points (List[str]): Current plot points.
            
        Returns:
            tuple[bool, List[str]]: (advances_plot, new_plot_points)
        """
        llm = self.get_llm()
        
        # Create context from current plot points
        plot_context = ""
        for point in plot_points[-5:]:  # Only use the last 5 points for efficiency
            plot_context += f"- {point}\n"
        
        prompt = f"""Analyze plot progression in this scene:

Scene:
{content}

Current Plot Points:
{plot_context if plot_context else "No plot points tracked yet."}

1. Does this scene advance the plot in a meaningful way? Consider:
   - New information revealed
   - Character decisions with consequences
   - Changes to the status quo
   - Progress toward or away from goals
   - New obstacles or complications

2. Extract 1-3 key new plot points from this scene.

Format your response as:
ADVANCES_PLOT: [YES/NO]
REASONING: [brief explanation]
NEW_PLOT_POINTS:
- [new plot point 1]
- [new plot point 2]
- [new plot point 3]"""

        response = llm.invoke(prompt)
        
        # Parse response to check plot progression
        advances_plot = True  # Default, assume it advances plot
        new_points = []
        
        collecting_points = False
        for line in response.content.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('ADVANCES_PLOT:'):
                answer = line.split(':')[1].strip().upper()
                advances_plot = answer == "YES"
            elif line == "NEW_PLOT_POINTS:" or line.startswith("NEW_PLOT_POINTS:"):
                collecting_points = True
            elif collecting_points and line.startswith('-'):
                point = line[2:].strip()
                if point and point not in plot_points:
                    new_points.append(point)
        
        return advances_plot, new_points


class AdvisorManager(BaseModel):
    """
    Manager for theatrical advisors.
    
    This class manages a collection of theatrical advisors and provides methods
    for getting advisors by name or expertise, as well as running analysis
    with multiple advisors.
    
    Attributes:
        llm_manager (LLMManager): Manager for LLM interactions.
        memory (TheatricalMemory): Production memory.
        advisors (Dict[str, TheatricalAdvisor]): Dictionary of advisors by name.
    """
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    llm_manager: LLMManager
    memory: TheatricalMemory
    advisors: Dict[str, TheatricalAdvisor] = Field(default_factory=dict)
    
    def __init__(self, llm_manager: LLMManager, memory: TheatricalMemory, **data):
        """Initialize the advisor manager."""
        super().__init__(
            llm_manager=llm_manager,
            memory=memory,
            **data
        )
        self._register_default_advisors()
    
    def _register_default_advisors(self) -> None:
        """Register default advisors."""
        # Register the default set of advisors
        self.register_advisor(
            NarrativeAdvisor(
                name="narrative_advisor",
                llm_manager=self.llm_manager,
                memory=self.memory
            )
        )
        
        self.register_advisor(
            DialogueAdvisor(
                name="dialogue_advisor",
                llm_manager=self.llm_manager,
                memory=self.memory
            )
        )
        
        self.register_advisor(
            CharacterAdvisor(
                name="character_advisor",
                llm_manager=self.llm_manager,
                memory=self.memory
            )
        )
        
        self.register_advisor(
            ScenicAdvisor(
                name="scenic_advisor",
                llm_manager=self.llm_manager,
                memory=self.memory
            )
        )
        
        self.register_advisor(
            PacingAdvisor(
                name="pacing_advisor",
                llm_manager=self.llm_manager,
                memory=self.memory
            )
        )
        
        self.register_advisor(
            ThematicAdvisor(
                name="thematic_advisor",
                llm_manager=self.llm_manager,
                memory=self.memory
            )
        )
        
        self.register_advisor(
            NarrativeContinuityAdvisor(
                name="continuity_advisor",
                expertise="narrative_continuity",
                llm_manager=self.llm_manager,
                memory=self.memory
            )
        )
    
    def register_advisor(self, advisor: TheatricalAdvisor) -> None:
        """Register an advisor with the manager."""
        self.advisors[advisor.name] = advisor
    
    def get_advisor(self, name: str) -> Optional[TheatricalAdvisor]:
        """Get an advisor by name."""
        return self.advisors.get(name)
    
    def get_advisors_by_expertise(self, expertise: str) -> List[TheatricalAdvisor]:
        """Get advisors by expertise."""
        return [advisor for advisor in self.advisors.values() 
                if expertise.lower() in advisor.expertise.lower()]
    
    def run_analysis(self, content: str, context: Dict[str, Any], 
                    advisor_names: Optional[List[str]] = None) -> Dict[str, AdvisorFeedback]:
        """
        Run analysis with multiple advisors.
        
        Args:
            content (str): The content to analyze.
            context (Dict[str, Any]): Additional context for analysis.
            advisor_names (Optional[List[str]]): Names of advisors to use. If None, use all.
            
        Returns:
            Dict[str, AdvisorFeedback]: Dictionary of advisor names to feedback.
        """
        results = {}
        
        # Determine which advisors to use
        if advisor_names:
            advisors = [self.get_advisor(name) for name in advisor_names if self.get_advisor(name)]
        else:
            advisors = list(self.advisors.values())
        
        # Run analysis with each advisor
        for advisor in advisors:
            try:
                feedback = advisor.analyze(content, context)
                results[advisor.name] = feedback
            except Exception as e:
                logger.error(f"Error running analysis with {advisor.name}: {str(e)}")
                # Create a fallback feedback object for the failed advisor
                results[advisor.name] = AdvisorFeedback(
                    score=0.5,
                    feedback=f"Analysis failed: {str(e)}",
                    suggestions=["Try again with more context"],
                    specific_examples=[],
                    priority=3
                )
        
        return results
    
    def get_consolidated_feedback(self, content: str, context: Dict[str, Any],
                                advisor_names: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Get consolidated feedback from multiple advisors.
        
        Args:
            content (str): The content to analyze.
            context (Dict[str, Any]): Additional context for analysis.
            advisor_names (Optional[List[str]]): Names of advisors to use. If None, use all.
            
        Returns:
            Dict[str, Any]: Consolidated feedback with suggestions, examples, and an overall score.
        """
        # Run analysis with advisors
        results = self.run_analysis(content, context, advisor_names)
        
        # Consolidate feedback
        all_suggestions = []
        all_examples = []
        avg_score = 0.0
        
        for advisor_name, feedback in results.items():
            # Add advisor-specific prefix to suggestions and examples
            for suggestion in feedback.suggestions:
                all_suggestions.append(f"{advisor_name}: {suggestion}")
            
            for example in feedback.specific_examples:
                all_examples.append(f"{advisor_name}: {example}")
            
            # Add to average score
            avg_score += feedback.score
        
        # Calculate average score
        if results:
            avg_score /= len(results)
        
        # Sort suggestions by priority (if available in context)
        priority_areas = context.get("priority_areas", [])
        if priority_areas:
            # This is a simple approach - in a real implementation, you might
            # use a more sophisticated method to prioritize suggestions
            prioritized_suggestions = []
            for area in priority_areas:
                area_suggestions = [s for s in all_suggestions 
                                if area.lower() in s.lower()]
                prioritized_suggestions.extend(area_suggestions)
            
            # Add any remaining suggestions
            remaining = [s for s in all_suggestions 
                       if not any(area.lower() in s.lower() for area in priority_areas)]
            prioritized_suggestions.extend(remaining)
            
            all_suggestions = prioritized_suggestions
        
        return {
            "score": avg_score,
            "suggestions": all_suggestions,
            "examples": all_examples,
            "advisor_count": len(results),
            "detailed_feedback": results
        }

# Create an advisor factory to easily get advisors of specific types
def get_advisor(advisor_type: AdvisorType, llm_manager: LLMManager, memory: TheatricalMemory, name: Optional[str] = None) -> TheatricalAdvisor:
    """
    Create an advisor of the specified type.
    
    Args:
        advisor_type: The type of advisor to create
        llm_manager: Manager for LLM interactions
        memory: Production memory
        name: Optional name for the advisor
        
    Returns:
        TheatricalAdvisor: An instance of the requested advisor type
    """
    advisor_map: Dict[AdvisorType, Type[TheatricalAdvisor]] = {
        AdvisorType.NARRATIVE: NarrativeAdvisor,
        AdvisorType.DIALOGUE: DialogueAdvisor,
        AdvisorType.CHARACTER: CharacterAdvisor,
        AdvisorType.SCENIC: ScenicAdvisor,
        AdvisorType.PACING: PacingAdvisor,
        AdvisorType.THEMATIC: ThematicAdvisor,
    }
    
    advisor_class = advisor_map.get(advisor_type)
    if not advisor_class:
        raise ValueError(f"Unsupported advisor type: {advisor_type}")
    
    if name is None:
        name = f"{advisor_type}_advisor"
        
    return advisor_class(name=name, llm_manager=llm_manager, memory=memory)