"""
Structured feedback schemas for agent communication.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class FeedbackType(str, Enum):
    """Types of feedback agents can provide."""
    DIALOGUE = "dialogue"
    CHARACTER = "character"
    PACING = "pacing"
    TECHNICAL = "technical"
    ATMOSPHERE = "atmosphere"
    STRUCTURE = "structure"
    CONTINUITY = "continuity"
    PERFORMANCE = "performance"


class Severity(str, Enum):
    """Severity levels for feedback items."""
    BLOCKER = "blocker"       # Must fix before proceeding
    CRITICAL = "critical"     # Serious issue affecting quality
    MAJOR = "major"           # Significant improvement needed
    MINOR = "minor"           # Would be nice to fix
    SUGGESTION = "suggestion" # Optional enhancement


class FeedbackItem(BaseModel):
    """Individual feedback item."""
    type: FeedbackType
    severity: Severity
    description: str
    location: Optional[str] = Field(None, description="Line number or scene location")
    suggestion: Optional[str] = Field(None, description="Specific suggestion for improvement")
    examples: List[str] = Field(default_factory=list, description="Example implementations")
    
    class Config:
        use_enum_values = True


class DialogueFeedback(BaseModel):
    """Specific feedback for dialogue."""
    character_name: str
    line_reference: str
    issue: str
    improved_version: Optional[str] = None
    reasoning: str
    maintains_voice: bool = True
    subtext_notes: Optional[str] = None


class CharacterFeedback(BaseModel):
    """Feedback on character consistency and development."""
    character_name: str
    consistency_score: float = Field(ge=0.0, le=1.0)
    arc_progression: str
    inconsistencies: List[str] = Field(default_factory=list)
    growth_opportunities: List[str] = Field(default_factory=list)
    relationship_dynamics: Dict[str, str] = Field(default_factory=dict)


class PacingFeedback(BaseModel):
    """Feedback on scene pacing and rhythm."""
    overall_pace: str = Field(description="slow, moderate, fast, varied")
    problem_areas: List[Dict[str, str]] = Field(default_factory=list)
    suggested_beats: List[str] = Field(default_factory=list)
    tension_curve: List[float] = Field(default_factory=list, description="Tension levels throughout scene")
    recommended_adjustments: str


class TechnicalFeedback(BaseModel):
    """Technical production feedback."""
    element_type: str = Field(description="lighting, sound, props, costumes, set")
    cues: List[Dict[str, Any]] = Field(default_factory=list)
    requirements: List[str] = Field(default_factory=list)
    safety_concerns: List[str] = Field(default_factory=list)
    budget_impact: Optional[str] = None
    feasibility: str = Field(default="feasible", description="feasible, challenging, requires_adaptation")


class AtmosphereFeedback(BaseModel):
    """Feedback on mood and atmosphere."""
    current_mood: str
    intended_mood: str
    alignment_score: float = Field(ge=0.0, le=1.0)
    enhancement_suggestions: List[str] = Field(default_factory=list)
    sensory_elements: Dict[str, List[str]] = Field(
        default_factory=lambda: {
            "visual": [],
            "auditory": [],
            "tactile": [],
            "olfactory": []
        }
    )


class StructuralFeedback(BaseModel):
    """Feedback on scene structure."""
    structure_type: str = Field(description="Type of structure issue")
    current_structure: str
    recommended_structure: str
    impact_on_flow: str
    specific_changes: List[Dict[str, str]] = Field(default_factory=list)


class ComprehensiveFeedback(BaseModel):
    """Complete feedback package from an agent."""
    agent_name: str
    agent_role: str
    scene_id: str
    overall_impression: str
    quality_score: float = Field(ge=0.0, le=1.0)
    
    dialogue_feedback: List[DialogueFeedback] = Field(default_factory=list)
    character_feedback: List[CharacterFeedback] = Field(default_factory=list)
    pacing_feedback: Optional[PacingFeedback] = None
    technical_feedback: List[TechnicalFeedback] = Field(default_factory=list)
    atmosphere_feedback: Optional[AtmosphereFeedback] = None
    structural_feedback: Optional[StructuralFeedback] = None
    
    priority_items: List[FeedbackItem] = Field(default_factory=list)
    
    def get_blockers(self) -> List[FeedbackItem]:
        """Get all blocking issues."""
        return [item for item in self.priority_items if item.severity == Severity.BLOCKER]
    
    def get_by_type(self, feedback_type: FeedbackType) -> List[FeedbackItem]:
        """Get all feedback items of a specific type."""
        return [item for item in self.priority_items if item.type == feedback_type]
    
    def to_revision_instructions(self) -> str:
        """Convert feedback to revision instructions."""
        instructions = []
        
        # Handle blockers first
        blockers = self.get_blockers()
        if blockers:
            instructions.append("MUST FIX BEFORE PROCEEDING:")
            for blocker in blockers:
                instructions.append(f"- {blocker.description}")
                if blocker.suggestion:
                    instructions.append(f"  Suggestion: {blocker.suggestion}")
        
        # Then critical items
        critical = [item for item in self.priority_items if item.severity == Severity.CRITICAL]
        if critical:
            instructions.append("\nCRITICAL IMPROVEMENTS:")
            for item in critical:
                instructions.append(f"- {item.description}")
        
        # Specific feedback sections
        if self.dialogue_feedback:
            instructions.append("\nDIALOGUE REVISIONS:")
            for df in self.dialogue_feedback:
                instructions.append(f"- {df.character_name}: {df.issue}")
                if df.improved_version:
                    instructions.append(f"  Suggested: {df.improved_version}")
        
        if self.pacing_feedback:
            instructions.append(f"\nPACING: {self.pacing_feedback.recommended_adjustments}")
        
        return "\n".join(instructions)


class FeedbackAggregator(BaseModel):
    """Aggregates feedback from multiple agents."""
    scene_id: str
    feedback_packages: List[ComprehensiveFeedback] = Field(default_factory=list)
    
    def add_feedback(self, feedback: ComprehensiveFeedback) -> None:
        """Add a feedback package from an agent."""
        self.feedback_packages.append(feedback)
    
    def get_consensus_score(self) -> float:
        """Calculate average quality score across all agents."""
        if not self.feedback_packages:
            return 0.0
        scores = [fb.quality_score for fb in self.feedback_packages]
        return sum(scores) / len(scores)
    
    def get_all_blockers(self) -> List[tuple[str, FeedbackItem]]:
        """Get all blocking issues from all agents."""
        blockers = []
        for feedback in self.feedback_packages:
            for blocker in feedback.get_blockers():
                blockers.append((feedback.agent_name, blocker))
        return blockers
    
    def get_conflicting_feedback(self) -> List[Dict[str, Any]]:
        """Identify conflicting feedback between agents."""
        conflicts = []
        
        # Check for conflicting dialogue suggestions
        dialogue_suggestions = {}
        for fb in self.feedback_packages:
            for df in fb.dialogue_feedback:
                key = (df.character_name, df.line_reference)
                if key not in dialogue_suggestions:
                    dialogue_suggestions[key] = []
                dialogue_suggestions[key].append({
                    "agent": fb.agent_name,
                    "suggestion": df.improved_version,
                    "reasoning": df.reasoning
                })
        
        # Find conflicts (multiple different suggestions for same line)
        for key, suggestions in dialogue_suggestions.items():
            if len(suggestions) > 1:
                unique_suggestions = set(s["suggestion"] for s in suggestions if s["suggestion"])
                if len(unique_suggestions) > 1:
                    conflicts.append({
                        "type": "dialogue",
                        "location": f"{key[0]}: {key[1]}",
                        "conflicting_suggestions": suggestions
                    })
        
        return conflicts
    
    def create_unified_revision_plan(self) -> str:
        """Create a unified revision plan from all feedback."""
        plan_sections = []
        
        # Consensus score
        consensus = self.get_consensus_score()
        plan_sections.append(f"OVERALL QUALITY SCORE: {consensus:.2f}/1.0")
        plan_sections.append(f"FEEDBACK FROM {len(self.feedback_packages)} AGENTS\n")
        
        # All blockers first
        all_blockers = self.get_all_blockers()
        if all_blockers:
            plan_sections.append("BLOCKING ISSUES (MUST FIX):")
            for agent, blocker in all_blockers:
                plan_sections.append(f"- [{agent}] {blocker.description}")
        
        # Conflicts that need resolution
        conflicts = self.get_conflicting_feedback()
        if conflicts:
            plan_sections.append("\nCONFLICTING FEEDBACK (NEEDS RESOLUTION):")
            for conflict in conflicts:
                plan_sections.append(f"- {conflict['type']}: {conflict['location']}")
                for sug in conflict['conflicting_suggestions']:
                    plan_sections.append(f"  • {sug['agent']}: {sug['suggestion']}")
        
        # Aggregate by category
        category_feedback = {cat: [] for cat in FeedbackType}
        for fb in self.feedback_packages:
            for item in fb.priority_items:
                category_feedback[item.type].append((fb.agent_name, item))
        
        # Add category sections
        for category, items in category_feedback.items():
            if items:
                plan_sections.append(f"\n{category.upper()} FEEDBACK:")
                # Sort by severity
                sorted_items = sorted(items, key=lambda x: list(Severity).index(x[1].severity))
                for agent, item in sorted_items[:5]:  # Top 5 per category
                    plan_sections.append(f"- [{agent}] {item.description}")
        
        return "\n".join(plan_sections)