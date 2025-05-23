"""
QuantumNarrative framework for multi-branch creative exploration.

This module implements a quantum-inspired approach to narrative generation,
allowing multiple story possibilities to exist in superposition until
character choices or dramatic necessities force collapse into a single path.
"""

from typing import Dict, Any, List, Optional, Union, Callable, Set, Tuple
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum
import logging
import json
import uuid
import time
import math
from datetime import datetime
from collections import defaultdict
import hashlib

from thespian.llm.enhanced_memory import EnhancedTheatricalMemory, EnhancedCharacterProfile
from thespian.llm.theatrical_memory import StoryOutline

logger = logging.getLogger(__name__)

class DivergenceType(str, Enum):
    """Types of narrative divergence points."""
    CHARACTER_DECISION = "character_decision"
    THEMATIC_EXPLORATION = "thematic_exploration"
    DRAMATIC_STRUCTURE = "dramatic_structure"
    RELATIONSHIP_DYNAMIC = "relationship_dynamic"
    EXTERNAL_FORCE = "external_force"
    EMOTIONAL_STATE = "emotional_state"
    MORAL_DILEMMA = "moral_dilemma"
    GENRE_SHIFT = "genre_shift"

class CollapseTriggerType(str, Enum):
    """Types of triggers that cause branch collapse."""
    CHARACTER_COMMITMENT = "character_commitment"
    DRAMATIC_NECESSITY = "dramatic_necessity"
    RESOURCE_CONSTRAINT = "resource_constraint"
    EXTERNAL_DEADLINE = "external_deadline"
    THEMATIC_RESOLUTION = "thematic_resolution"
    AUDIENCE_FEEDBACK = "audience_feedback"
    HUMAN_DECISION = "human_decision"

class NarrativeQuantumState(BaseModel):
    """Represents a single narrative possibility in quantum superposition."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    # Core identity
    branch_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    timestamp: datetime = Field(default_factory=datetime.now)
    
    # Hierarchical structure
    parent_branch: Optional[str] = None
    child_branches: List[str] = Field(default_factory=list)
    depth_level: int = Field(default=0)
    
    # Narrative content
    narrative_content: str = Field(default="")
    scene_outline: str = Field(default="")
    dialogue_fragments: List[str] = Field(default_factory=list)
    stage_directions: List[str] = Field(default_factory=list)
    
    # State tracking
    character_states: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    world_state: Dict[str, Any] = Field(default_factory=dict)
    relationship_matrix: Dict[str, Dict[str, float]] = Field(default_factory=dict)
    
    # Divergence information
    divergence_point: str = Field(default="")
    divergence_type: DivergenceType = DivergenceType.CHARACTER_DECISION
    divergence_description: str = Field(default="")
    
    # Quality metrics
    probability_weight: float = Field(default=0.5, ge=0.0, le=1.0)
    emotional_resonance: float = Field(default=0.5, ge=0.0, le=1.0)
    thematic_alignment: float = Field(default=0.5, ge=0.0, le=1.0)
    dramatic_tension: float = Field(default=0.5, ge=0.0, le=1.0)
    character_consistency: float = Field(default=0.5, ge=0.0, le=1.0)
    narrative_coherence: float = Field(default=0.5, ge=0.0, le=1.0)
    
    # Exploration metadata
    exploration_notes: List[str] = Field(default_factory=list)
    creative_risk_level: float = Field(default=0.5, ge=0.0, le=1.0)
    innovation_score: float = Field(default=0.5, ge=0.0, le=1.0)
    
    def add_exploration_note(self, note: str) -> None:
        """Add a note about this branch's exploration."""
        self.exploration_notes.append(f"{datetime.now().isoformat()}: {note}")
    
    def calculate_overall_quality(self) -> float:
        """Calculate weighted overall quality score."""
        weights = {
            'emotional_resonance': 0.25,
            'thematic_alignment': 0.20,
            'dramatic_tension': 0.20,
            'character_consistency': 0.20,
            'narrative_coherence': 0.15
        }
        
        quality_score = (
            self.emotional_resonance * weights['emotional_resonance'] +
            self.thematic_alignment * weights['thematic_alignment'] +
            self.dramatic_tension * weights['dramatic_tension'] +
            self.character_consistency * weights['character_consistency'] +
            self.narrative_coherence * weights['narrative_coherence']
        )
        
        return quality_score
    
    def get_content_hash(self) -> str:
        """Generate hash of narrative content for deduplication."""
        content_str = f"{self.narrative_content}{self.scene_outline}{''.join(self.dialogue_fragments)}"
        return hashlib.md5(content_str.encode()).hexdigest()[:12]

class CollapseTrigger(BaseModel):
    """Defines conditions that trigger branch collapse."""
    
    trigger_type: CollapseTriggerType
    urgency: float = Field(ge=0.0, le=1.0)  # How immediately this forces collapse
    scope: str = Field(default="scene")  # "scene", "act", "story", "immediate"
    condition: str = Field(default="")  # Specific condition description
    threshold: float = Field(default=0.7, ge=0.0, le=1.0)  # Quality threshold for collapse
    reason: str = Field(default="")  # Human-readable explanation
    
    def should_trigger(self, context: Dict[str, Any]) -> bool:
        """Determine if this trigger should activate given current context."""
        if self.trigger_type == CollapseTriggerType.CHARACTER_COMMITMENT:
            return context.get("character_makes_irreversible_choice", False)
        elif self.trigger_type == CollapseTriggerType.DRAMATIC_NECESSITY:
            return context.get("act_ending_approaches", False) or context.get("climax_approaching", False)
        elif self.trigger_type == CollapseTriggerType.RESOURCE_CONSTRAINT:
            return context.get("branch_count", 0) > context.get("max_branches", 5)
        elif self.trigger_type == CollapseTriggerType.THEMATIC_RESOLUTION:
            return context.get("theme_needs_resolution", False)
        else:
            return False

class BranchGenerationStrategy(BaseModel):
    """Strategy for generating new narrative branches."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    strategy_name: str
    priority: int = Field(ge=1, le=10)  # Higher number = higher priority
    max_branches_per_call: int = Field(default=3, ge=1, le=10)
    
    # Character psychology parameters
    explore_attachment_styles: bool = Field(default=True)
    explore_trauma_responses: bool = Field(default=True)
    explore_value_conflicts: bool = Field(default=True)
    
    # Thematic parameters
    explore_philosophical_contrasts: bool = Field(default=True)
    explore_moral_complexity: bool = Field(default=True)
    
    # Structural parameters
    explore_genre_variations: bool = Field(default=False)
    explore_pacing_alternatives: bool = Field(default=True)
    
    def should_apply(self, context: Dict[str, Any], current_state: NarrativeQuantumState) -> bool:
        """Determine if this strategy should be applied in current context."""
        # Character-focused strategies
        if "character_decision" in self.strategy_name:
            return context.get("has_character_choice_point", False)
        
        # Thematic strategies
        if "thematic" in self.strategy_name:
            return context.get("thematic_tension_present", False)
        
        # Structural strategies
        if "structural" in self.strategy_name:
            return context.get("at_structural_turning_point", False)
        
        # Default: apply if not too many branches already
        return len(current_state.child_branches) < self.max_branches_per_call

class QuantumNarrativeTree(BaseModel):
    """Manages the tree of all possible narrative branches."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    # Tree structure
    root_state: NarrativeQuantumState
    active_branches: Dict[str, NarrativeQuantumState] = Field(default_factory=dict)
    collapsed_path: List[str] = Field(default_factory=list)
    pruned_branches: Dict[str, NarrativeQuantumState] = Field(default_factory=dict)
    
    # Configuration
    max_active_branches: int = Field(default=50)  # Allow many simultaneous branches
    max_exploration_depth: int = Field(default=25)  # Allow ultra-deep exploration
    min_quality_threshold: float = Field(default=0.3)
    
    # Generation strategies
    generation_strategies: List[BranchGenerationStrategy] = Field(default_factory=list)
    
    # Collapse configuration
    collapse_triggers: List[CollapseTrigger] = Field(default_factory=list)
    auto_collapse_enabled: bool = Field(default=True)
    
    # Metadata
    exploration_history: List[Dict[str, Any]] = Field(default_factory=list)
    performance_metrics: Dict[str, float] = Field(default_factory=dict)
    
    def __init__(self, **data):
        super().__init__(**data)
        
        # Initialize with root state in active branches
        if self.root_state:
            self.active_branches[self.root_state.branch_id] = self.root_state
        
        # Set up default generation strategies
        if not self.generation_strategies:
            self._initialize_default_strategies()
        
        # Set up default collapse triggers
        if not self.collapse_triggers:
            self._initialize_default_triggers()
    
    def _initialize_default_strategies(self) -> None:
        """Initialize default branch generation strategies."""
        strategies = [
            BranchGenerationStrategy(
                strategy_name="character_psychology_exploration",
                priority=9,
                max_branches_per_call=4,
                explore_attachment_styles=True,
                explore_trauma_responses=True,
                explore_value_conflicts=True
            ),
            BranchGenerationStrategy(
                strategy_name="thematic_divergence_exploration", 
                priority=8,
                max_branches_per_call=3,
                explore_philosophical_contrasts=True,
                explore_moral_complexity=True
            ),
            BranchGenerationStrategy(
                strategy_name="dramatic_structure_alternatives",
                priority=7,
                max_branches_per_call=3,
                explore_pacing_alternatives=True,
                explore_genre_variations=False
            ),
            BranchGenerationStrategy(
                strategy_name="relationship_dynamic_variations",
                priority=6,
                max_branches_per_call=2,
                explore_attachment_styles=True
            )
        ]
        
        self.generation_strategies.extend(strategies)
    
    def _initialize_default_triggers(self) -> None:
        """Initialize default collapse triggers."""
        triggers = [
            CollapseTrigger(
                trigger_type=CollapseTriggerType.CHARACTER_COMMITMENT,
                urgency=0.9,
                scope="scene",
                condition="irreversible_character_decision",
                threshold=0.7,
                reason="Character has made a commitment that eliminates other possibilities"
            ),
            CollapseTrigger(
                trigger_type=CollapseTriggerType.DRAMATIC_NECESSITY,
                urgency=0.8,
                scope="act",
                condition="structural_checkpoint_reached",
                threshold=0.6,
                reason="Story structure requires resolution of current tension"
            ),
            CollapseTrigger(
                trigger_type=CollapseTriggerType.RESOURCE_CONSTRAINT,
                urgency=0.7,
                scope="immediate",
                condition="too_many_active_branches",
                threshold=0.5,
                reason="Computational limits require branch reduction"
            )
        ]
        
        self.collapse_triggers.extend(triggers)
    
    def add_branch(self, 
                   parent_branch_id: str, 
                   new_branch: NarrativeQuantumState) -> bool:
        """Add a new branch to the tree."""
        if parent_branch_id not in self.active_branches:
            logger.warning(f"Parent branch {parent_branch_id} not found in active branches")
            return False
        
        # Set parent-child relationships
        new_branch.parent_branch = parent_branch_id
        new_branch.depth_level = self.active_branches[parent_branch_id].depth_level + 1
        
        # Check depth limits
        if new_branch.depth_level > self.max_exploration_depth:
            logger.info(f"Branch {new_branch.branch_id} exceeds depth limit, not adding")
            return False
        
        # Check quality threshold
        if new_branch.calculate_overall_quality() < self.min_quality_threshold:
            logger.info(f"Branch {new_branch.branch_id} below quality threshold, not adding")
            return False
        
        # Add to parent's children
        self.active_branches[parent_branch_id].child_branches.append(new_branch.branch_id)
        
        # Add to active branches
        self.active_branches[new_branch.branch_id] = new_branch
        
        # Check if we need to prune due to resource constraints
        if len(self.active_branches) > self.max_active_branches:
            self._prune_low_quality_branches()
        
        logger.info(f"Added branch {new_branch.branch_id} as child of {parent_branch_id}")
        return True
    
    def _prune_low_quality_branches(self) -> None:
        """Prune branches with lowest quality scores."""
        if len(self.active_branches) <= self.max_active_branches:
            return
        
        # Sort branches by quality (excluding root and collapsed path)
        pruneable_branches = []
        for branch_id, branch in self.active_branches.items():
            if (branch_id != self.root_state.branch_id and 
                branch_id not in self.collapsed_path):
                pruneable_branches.append((branch_id, branch.calculate_overall_quality()))
        
        # Sort by quality (lowest first)
        pruneable_branches.sort(key=lambda x: x[1])
        
        # Prune lowest quality branches
        branches_to_prune = len(self.active_branches) - self.max_active_branches
        for i in range(min(branches_to_prune, len(pruneable_branches))):
            branch_id = pruneable_branches[i][0]
            self._prune_branch(branch_id)
    
    def _prune_branch(self, branch_id: str) -> None:
        """Prune a specific branch and its descendants."""
        if branch_id not in self.active_branches:
            return
        
        branch = self.active_branches[branch_id]
        
        # Recursively prune child branches
        for child_id in branch.child_branches:
            self._prune_branch(child_id)
        
        # Move to pruned branches for potential future reference
        self.pruned_branches[branch_id] = branch
        
        # Remove from active branches
        del self.active_branches[branch_id]
        
        # Remove from parent's children list
        if branch.parent_branch and branch.parent_branch in self.active_branches:
            parent = self.active_branches[branch.parent_branch]
            if branch_id in parent.child_branches:
                parent.child_branches.remove(branch_id)
        
        logger.info(f"Pruned branch {branch_id}")
    
    def evaluate_collapse_triggers(self, context: Dict[str, Any]) -> Optional[CollapseTrigger]:
        """Evaluate if any collapse triggers should activate."""
        # Add branch count to context
        context["branch_count"] = len(self.active_branches)
        context["max_branches"] = self.max_active_branches
        
        # Check each trigger
        for trigger in self.collapse_triggers:
            if trigger.should_trigger(context):
                logger.info(f"Collapse trigger activated: {trigger.trigger_type} - {trigger.reason}")
                return trigger
        
        return None
    
    def collapse_to_path(self, trigger: Optional[CollapseTrigger] = None) -> NarrativeQuantumState:
        """Collapse quantum superposition into single narrative path."""
        if not self.active_branches:
            logger.warning("No active branches to collapse")
            return self.root_state
        
        # Calculate selection probabilities
        branch_probabilities = self._calculate_branch_probabilities(trigger)
        
        # Select branch based on weighted probability
        selected_branch_id = self._weighted_random_selection(branch_probabilities)
        selected_branch = self.active_branches[selected_branch_id]
        
        # Record collapse in history
        collapse_record = {
            "timestamp": datetime.now().isoformat(),
            "trigger": trigger.dict() if trigger else None,
            "selected_branch": selected_branch_id,
            "alternatives_pruned": list(self.active_branches.keys()),
            "selection_probability": branch_probabilities.get(selected_branch_id, 0.0)
        }
        self.exploration_history.append(collapse_record)
        
        # Add to collapsed path
        self.collapsed_path.append(selected_branch_id)
        
        # Prune incompatible branches
        self._prune_incompatible_branches(selected_branch)
        
        logger.info(f"Collapsed to branch {selected_branch_id} with probability {branch_probabilities.get(selected_branch_id, 0.0):.3f}")
        
        return selected_branch
    
    def _calculate_branch_probabilities(self, trigger: Optional[CollapseTrigger]) -> Dict[str, float]:
        """Calculate selection probabilities for all active branches."""
        probabilities = {}
        
        for branch_id, branch in self.active_branches.items():
            # Base probability from branch quality
            base_prob = branch.calculate_overall_quality()
            
            # Apply trigger-specific weighting
            if trigger:
                if trigger.trigger_type == CollapseTriggerType.CHARACTER_COMMITMENT:
                    # Favor branches with strong character consistency
                    base_prob *= (1.0 + branch.character_consistency)
                elif trigger.trigger_type == CollapseTriggerType.DRAMATIC_NECESSITY:
                    # Favor branches with high dramatic tension
                    base_prob *= (1.0 + branch.dramatic_tension)
                elif trigger.trigger_type == CollapseTriggerType.THEMATIC_RESOLUTION:
                    # Favor branches with strong thematic alignment
                    base_prob *= (1.0 + branch.thematic_alignment)
            
            # Apply innovation bonus (slight preference for creative risk)
            innovation_bonus = 1.0 + (branch.innovation_score * 0.1)
            base_prob *= innovation_bonus
            
            probabilities[branch_id] = max(0.01, base_prob)  # Minimum probability
        
        # Normalize probabilities
        total_prob = sum(probabilities.values())
        if total_prob > 0:
            probabilities = {k: v / total_prob for k, v in probabilities.items()}
        
        return probabilities
    
    def _weighted_random_selection(self, probabilities: Dict[str, float]) -> str:
        """Select branch ID based on weighted probabilities."""
        import random
        
        # Create cumulative probability distribution
        items = list(probabilities.items())
        cumulative_probs = []
        cumulative_sum = 0.0
        
        for branch_id, prob in items:
            cumulative_sum += prob
            cumulative_probs.append((branch_id, cumulative_sum))
        
        # Generate random number and find corresponding branch
        rand_val = random.random() * cumulative_sum
        
        for branch_id, cumulative_prob in cumulative_probs:
            if rand_val <= cumulative_prob:
                return branch_id
        
        # Fallback: return first branch
        return items[0][0] if items else self.root_state.branch_id
    
    def _prune_incompatible_branches(self, selected_branch: NarrativeQuantumState) -> None:
        """Prune branches incompatible with selected branch."""
        branches_to_prune = []
        
        for branch_id, branch in self.active_branches.items():
            if branch_id == selected_branch.branch_id:
                continue
            
            # Prune branches that are siblings of the selected branch
            # (they represent alternative choices that are now impossible)
            if (branch.parent_branch == selected_branch.parent_branch and
                branch.parent_branch is not None):
                branches_to_prune.append(branch_id)
        
        for branch_id in branches_to_prune:
            self._prune_branch(branch_id)
    
    def get_exploration_summary(self) -> Dict[str, Any]:
        """Get summary of current exploration state."""
        return {
            "total_active_branches": len(self.active_branches),
            "total_pruned_branches": len(self.pruned_branches),
            "max_depth_explored": max((b.depth_level for b in self.active_branches.values()), default=0),
            "collapsed_decisions": len(self.collapsed_path),
            "average_branch_quality": sum(b.calculate_overall_quality() for b in self.active_branches.values()) / len(self.active_branches) if self.active_branches else 0.0,
            "exploration_history_length": len(self.exploration_history),
            "root_branch_id": self.root_state.branch_id
        }
    
    def export_tree_visualization(self) -> Dict[str, Any]:
        """Export tree structure for visualization."""
        def export_branch(branch: NarrativeQuantumState) -> Dict[str, Any]:
            return {
                "id": branch.branch_id,
                "content_preview": branch.narrative_content[:100] + "..." if len(branch.narrative_content) > 100 else branch.narrative_content,
                "divergence_type": branch.divergence_type,
                "divergence_point": branch.divergence_point,
                "quality_score": branch.calculate_overall_quality(),
                "probability_weight": branch.probability_weight,
                "depth": branch.depth_level,
                "children": [export_branch(self.active_branches[child_id]) 
                           for child_id in branch.child_branches 
                           if child_id in self.active_branches],
                "is_collapsed": branch.branch_id in self.collapsed_path,
                "timestamp": branch.timestamp.isoformat()
            }
        
        return {
            "tree": export_branch(self.root_state),
            "metadata": self.get_exploration_summary()
        }


class QuantumBranchGenerator:
    """Generates narrative branches based on different strategies."""
    
    def __init__(self, memory: EnhancedTheatricalMemory):
        self.memory = memory
        self.logger = logging.getLogger(__name__ + ".BranchGenerator")
    
    def generate_character_psychology_branches(self,
                                             character_name: str,
                                             decision_context: str,
                                             current_state: NarrativeQuantumState,
                                             llm_invoke_func: Callable) -> List[NarrativeQuantumState]:
        """Generate branches based on character psychology."""
        branches = []
        
        # Get character profile
        char_id = character_name.lower().replace(" ", "_")
        profile = self.memory.get_character_profile(char_id)
        
        if not profile:
            self.logger.warning(f"No profile found for character {character_name}")
            return branches
        
        # Generate psychology-based response branches
        psychology_prompts = self._create_psychology_prompts(character_name, decision_context, profile)
        
        for prompt_type, prompt in psychology_prompts.items():
            try:
                response = llm_invoke_func(prompt)
                response_text = str(response.content if hasattr(response, "content") else response)
                
                # Create new branch
                new_branch = NarrativeQuantumState(
                    narrative_content=response_text,
                    divergence_point=f"{character_name} {prompt_type} response to {decision_context}",
                    divergence_type=DivergenceType.CHARACTER_DECISION,
                    divergence_description=f"Character responds based on {prompt_type}",
                    parent_branch=current_state.branch_id,
                    depth_level=current_state.depth_level + 1
                )
                
                # Set character state
                new_branch.character_states[char_id] = {
                    "psychological_state": prompt_type,
                    "decision_rationale": f"Acting from {prompt_type}",
                    "emotional_state": self._infer_emotional_state(prompt_type),
                    "character_growth": f"Expressing {prompt_type} aspect of personality"
                }
                
                # Calculate quality metrics
                new_branch.character_consistency = self._evaluate_character_consistency(new_branch, profile)
                new_branch.emotional_resonance = self._evaluate_emotional_resonance(new_branch, prompt_type)
                new_branch.probability_weight = self._calculate_psychology_probability(prompt_type, profile)
                
                new_branch.add_exploration_note(f"Generated from {prompt_type} psychological response")
                
                branches.append(new_branch)
                
            except Exception as e:
                self.logger.error(f"Error generating {prompt_type} branch: {str(e)}")
        
        return branches
    
    def _create_psychology_prompts(self, 
                                  character_name: str, 
                                  decision_context: str, 
                                  profile: EnhancedCharacterProfile) -> Dict[str, str]:
        """Create prompts for different psychological response types."""
        
        base_context = f"""Character: {character_name}
Background: {profile.background}
Current situation: {decision_context}

Character's core traits:
- Fears: {', '.join(profile.fears[:3]) if profile.fears else 'Unknown'}
- Desires: {', '.join(profile.desires[:3]) if profile.desires else 'Unknown'}
- Values: {', '.join(profile.values[:3]) if profile.values else 'Unknown'}
- Flaws: {', '.join(profile.flaws[:3]) if profile.flaws else 'Unknown'}"""

        prompts = {
            "fear_driven": f"""{base_context}

Generate a scene where {character_name} responds primarily from their deepest fears. Show how their past traumas and anxieties drive their decision-making in this moment. The response should feel authentic to someone acting from a place of fear and self-protection.

Focus on:
- Physical manifestations of fear (trembling, shallow breathing, etc.)
- Defensive dialogue patterns
- Attempts to control or avoid the situation
- How fear distorts their perception of others' intentions

Generate 200-400 words of scene content with dialogue and stage directions.""",

            "desire_driven": f"""{base_context}

Generate a scene where {character_name} responds primarily from their deepest desires and longings. Show how their core wants and needs drive their decision-making, even if it means taking risks or being vulnerable.

Focus on:
- Passionate, authentic expression of wants
- Willingness to be vulnerable to get what they need
- How desire gives them courage or makes them reckless
- The beauty and danger of acting from pure desire

Generate 200-400 words of scene content with dialogue and stage directions.""",

            "values_driven": f"""{base_context}

Generate a scene where {character_name} responds primarily from their core values and moral principles. Show how their ethical framework guides their decision, even when it's difficult or costly.

Focus on:
- Clear moral reasoning in dialogue
- Standing up for principles despite consequences
- How values provide strength and clarity
- The integrity and sacrifice that comes with moral choices

Generate 200-400 words of scene content with dialogue and stage directions.""",

            "attachment_driven": f"""{base_context}

Generate a scene where {character_name} responds based on their attachment style and relationship patterns. Show how their way of connecting (or avoiding connection) with others drives their decision.

Focus on:
- Relationship-focused dialogue and concerns
- How they seek or avoid intimacy
- Patterns of dependence, independence, or ambivalence
- How their past relationships influence current choices

Generate 200-400 words of scene content with dialogue and stage directions."""
        }
        
        return prompts
    
    def _infer_emotional_state(self, psychology_type: str) -> str:
        """Infer likely emotional state from psychology type."""
        emotion_mapping = {
            "fear_driven": "anxious and defensive",
            "desire_driven": "passionate and vulnerable", 
            "values_driven": "determined and principled",
            "attachment_driven": "seeking connection or avoiding intimacy"
        }
        return emotion_mapping.get(psychology_type, "complex emotional state")
    
    def _evaluate_character_consistency(self, branch: NarrativeQuantumState, profile: EnhancedCharacterProfile) -> float:
        """Evaluate how consistent the branch is with character profile."""
        # Simple heuristic based on content analysis
        content = branch.narrative_content.lower()
        
        consistency_score = 0.5  # Base score
        
        # Check if character traits are reflected in content
        trait_keywords = []
        trait_keywords.extend(profile.fears)
        trait_keywords.extend(profile.desires)
        trait_keywords.extend(profile.values)
        
        trait_matches = sum(1 for trait in trait_keywords if trait.lower() in content)
        if trait_keywords:
            consistency_score += (trait_matches / len(trait_keywords)) * 0.3
        
        # Check for character name usage
        if profile.name.lower() in content:
            consistency_score += 0.1
        
        # Check content length (substantial content scores higher)
        if len(content) > 500:
            consistency_score += 0.1
        
        return min(1.0, consistency_score)
    
    def _evaluate_emotional_resonance(self, branch: NarrativeQuantumState, psychology_type: str) -> float:
        """Evaluate emotional resonance of the branch."""
        content = branch.narrative_content.lower()
        
        # Emotional keywords by psychology type
        emotion_keywords = {
            "fear_driven": ["afraid", "scared", "anxious", "worried", "trembling", "panic", "nervous"],
            "desire_driven": ["want", "need", "passion", "love", "longing", "dream", "hope"],
            "values_driven": ["right", "wrong", "principle", "believe", "stand", "moral", "ethics"],
            "attachment_driven": ["together", "alone", "relationship", "connect", "love", "trust", "bond"]
        }
        
        keywords = emotion_keywords.get(psychology_type, [])
        emotion_matches = sum(1 for keyword in keywords if keyword in content)
        
        base_score = 0.5
        if keywords:
            emotion_score = min(1.0, base_score + (emotion_matches / len(keywords)) * 0.5)
        else:
            emotion_score = base_score
        
        return emotion_score
    
    def _calculate_psychology_probability(self, psychology_type: str, profile: EnhancedCharacterProfile) -> float:
        """Calculate probability weight based on character psychology."""
        # Get current emotional state
        current_emotion = profile.get_current_emotional_state()
        
        # Base probabilities by psychology type
        base_probs = {
            "fear_driven": 0.3,  # Often default in crisis
            "desire_driven": 0.25,  # When feeling safe to express wants
            "values_driven": 0.25,  # When moral clarity is needed
            "attachment_driven": 0.2  # When relationships are at stake
        }
        
        prob = base_probs.get(psychology_type, 0.25)
        
        # Adjust based on current emotional state
        if current_emotion:
            if "fear" in current_emotion.emotion.lower() and psychology_type == "fear_driven":
                prob += 0.2
            elif "joy" in current_emotion.emotion.lower() and psychology_type == "desire_driven":
                prob += 0.2
            elif "anger" in current_emotion.emotion.lower() and psychology_type == "values_driven":
                prob += 0.2
        
        return min(1.0, prob)

    def generate_thematic_exploration_branches(self,
                                             thematic_tension: str,
                                             current_state: NarrativeQuantumState,
                                             llm_invoke_func: Callable) -> List[NarrativeQuantumState]:
        """Generate branches exploring different thematic directions."""
        branches = []
        
        # Create thematic exploration prompts
        thematic_prompts = self._create_thematic_prompts(thematic_tension, current_state)
        
        for theme_type, prompt in thematic_prompts.items():
            try:
                response = llm_invoke_func(prompt)
                response_text = str(response.content if hasattr(response, "content") else response)
                
                # Create new branch
                new_branch = NarrativeQuantumState(
                    narrative_content=response_text,
                    divergence_point=f"Thematic exploration: {theme_type}",
                    divergence_type=DivergenceType.THEMATIC_EXPLORATION,
                    divergence_description=f"Scene explores {theme_type} thematic direction",
                    parent_branch=current_state.branch_id,
                    depth_level=current_state.depth_level + 1
                )
                
                # Set thematic focus in world state
                new_branch.world_state.update({
                    "dominant_theme": theme_type,
                    "thematic_tension": thematic_tension,
                    "philosophical_stance": self._extract_philosophical_stance(theme_type),
                    "thematic_development": f"Exploring {theme_type} implications"
                })
                
                # Calculate quality metrics
                new_branch.thematic_alignment = self._evaluate_thematic_alignment(new_branch, theme_type)
                new_branch.innovation_score = self._evaluate_thematic_innovation(new_branch, theme_type)
                new_branch.probability_weight = self._calculate_thematic_probability(theme_type)
                
                new_branch.add_exploration_note(f"Thematic exploration of {theme_type}")
                
                branches.append(new_branch)
                
            except Exception as e:
                self.logger.error(f"Error generating thematic branch {theme_type}: {str(e)}")
        
        return branches
    
    def _create_thematic_prompts(self, thematic_tension: str, current_state: NarrativeQuantumState) -> Dict[str, str]:
        """Create prompts for different thematic explorations."""
        
        base_context = f"""Current narrative context:
{current_state.narrative_content[:500]}...

Central thematic tension: {thematic_tension}
Current world state: {json.dumps(current_state.world_state, indent=2)}"""

        # Extract opposing concepts from thematic tension
        if "vs" in thematic_tension or "versus" in thematic_tension:
            concepts = thematic_tension.replace(" versus ", " vs ").split(" vs ")
            if len(concepts) >= 2:
                concept_a = concepts[0].strip()
                concept_b = concepts[1].strip()
            else:
                concept_a = "individual autonomy"
                concept_b = "collective responsibility"
        else:
            concept_a = "traditional approach"
            concept_b = "innovative approach"
        
        prompts = {
            f"{concept_a}_emphasis": f"""{base_context}

Generate a scene that explores and emphasizes {concept_a}. Show how this perspective offers wisdom, strength, or solutions. Let the characters embody this viewpoint authentically, showing both its beauty and its costs.

The scene should:
- Demonstrate the value and truth of {concept_a}
- Show characters making choices based on this principle
- Explore the emotional and practical consequences
- Reveal deeper layers of this philosophical stance

Generate 300-500 words with rich dialogue and meaningful character interactions.""",

            f"{concept_b}_emphasis": f"""{base_context}

Generate a scene that explores and emphasizes {concept_b}. Show how this perspective offers wisdom, strength, or solutions. Let the characters embody this viewpoint authentically, showing both its beauty and its costs.

The scene should:
- Demonstrate the value and truth of {concept_b}
- Show characters making choices based on this principle
- Explore the emotional and practical consequences
- Reveal deeper layers of this philosophical stance

Generate 300-500 words with rich dialogue and meaningful character interactions.""",

            "synthesis_exploration": f"""{base_context}

Generate a scene that explores a potential synthesis or transcendence of the tension between {concept_a} and {concept_b}. Show how these seemingly opposing forces might complement each other or how the characters might find a third way.

The scene should:
- Acknowledge the truth in both perspectives
- Show characters struggling to integrate both viewpoints
- Explore creative solutions that honor both sides
- Demonstrate the complexity of real human experience

Generate 300-500 words with nuanced dialogue and character development.""",

            "paradox_exploration": f"""{base_context}

Generate a scene that leans into the paradox and irony of the tension between {concept_a} and {concept_b}. Show how pursuing one extreme might actually lead to its opposite, or how the characters discover unexpected connections.

The scene should:
- Reveal ironies and paradoxes in the thematic tension
- Show unintended consequences of extreme positions
- Demonstrate the complexity and ambiguity of human truth
- Use dramatic irony to illuminate deeper meanings

Generate 300-500 words with sophisticated subtext and layered meaning."""
        }
        
        return prompts
    
    def _extract_philosophical_stance(self, theme_type: str) -> str:
        """Extract philosophical stance from theme type."""
        if "emphasis" in theme_type:
            return f"Prioritizing {theme_type.replace('_emphasis', '').replace('_', ' ')}"
        elif "synthesis" in theme_type:
            return "Seeking integration and balance"
        elif "paradox" in theme_type:
            return "Embracing complexity and contradiction"
        else:
            return "Philosophical exploration"
    
    def _evaluate_thematic_alignment(self, branch: NarrativeQuantumState, theme_type: str) -> float:
        """Evaluate how well the branch explores its intended theme."""
        content = branch.narrative_content.lower()
        
        # Theme-specific keywords
        thematic_keywords = {
            "freedom": ["choice", "liberty", "independence", "autonomy", "self-determination"],
            "security": ["safety", "protection", "stability", "certainty", "order"],
            "individual": ["personal", "self", "unique", "private", "individual"],
            "collective": ["together", "community", "group", "shared", "collective"],
            "tradition": ["heritage", "custom", "established", "proven", "traditional"],
            "innovation": ["new", "creative", "change", "progress", "innovation"]
        }
        
        # Extract keywords from theme type
        theme_words = theme_type.replace("_emphasis", "").replace("_exploration", "").split("_")
        relevant_keywords = []
        for word in theme_words:
            relevant_keywords.extend(thematic_keywords.get(word, [word]))
        
        # Count thematic matches
        thematic_matches = sum(1 for keyword in relevant_keywords if keyword in content)
        
        base_score = 0.5
        if relevant_keywords:
            theme_score = min(1.0, base_score + (thematic_matches / len(relevant_keywords)) * 0.5)
        else:
            theme_score = base_score
        
        return theme_score
    
    def _evaluate_thematic_innovation(self, branch: NarrativeQuantumState, theme_type: str) -> float:
        """Evaluate the innovative approach to thematic exploration."""
        content = branch.narrative_content.lower()
        
        innovation_indicators = [
            "paradox", "irony", "unexpected", "surprise", "twist",
            "complex", "nuanced", "layered", "subtle", "contradiction"
        ]
        
        innovation_matches = sum(1 for indicator in innovation_indicators if indicator in content)
        
        base_score = 0.5
        innovation_score = min(1.0, base_score + (innovation_matches / len(innovation_indicators)) * 0.5)
        
        # Bonus for synthesis and paradox explorations
        if "synthesis" in theme_type or "paradox" in theme_type:
            innovation_score += 0.1
        
        return min(1.0, innovation_score)
    
    def _calculate_thematic_probability(self, theme_type: str) -> float:
        """Calculate probability weight for thematic branch."""
        # Base probabilities favor exploration over simple emphasis
        if "synthesis" in theme_type:
            return 0.35  # Highest probability for synthetic thinking
        elif "paradox" in theme_type:
            return 0.3   # High probability for complex exploration
        elif "emphasis" in theme_type:
            return 0.2   # Lower probability for simple emphasis
        else:
            return 0.15  # Lowest for other types