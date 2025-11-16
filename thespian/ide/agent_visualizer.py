"""
Agent Visualizer Backend API

Provides visualization data for agent interactions and decision-making processes.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import uuid


class InteractionType(str, Enum):
    """Types of agent interactions."""
    COLLABORATION = "collaboration"
    FEEDBACK = "feedback"
    CRITIQUE = "critique"
    SUGGESTION = "suggestion"
    APPROVAL = "approval"
    REVISION = "revision"


@dataclass
class AgentInteraction:
    """Represents an interaction between agents."""
    interaction_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_agent: str = ""
    target_agent: str = ""
    interaction_type: InteractionType = InteractionType.COLLABORATION
    content: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    scene_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class AgentVisualizer:
    """
    Backend API for visualizing agent interactions and workflows.

    Features:
    - Agent interaction graph
    - Decision tree visualization
    - Collaboration flow tracking
    - Agent contribution metrics
    """

    def __init__(self):
        """Initialize the agent visualizer."""
        self.interactions: List[AgentInteraction] = []
        self.agent_registry: Dict[str, Dict[str, Any]] = {}

    def register_agent(
        self,
        agent_id: str,
        agent_type: str,
        capabilities: Optional[List[str]] = None
    ) -> None:
        """Register an agent in the visualizer."""
        self.agent_registry[agent_id] = {
            "agent_id": agent_id,
            "agent_type": agent_type,
            "capabilities": capabilities or [],
            "registered_at": datetime.now().isoformat()
        }

    def record_interaction(
        self,
        source_agent: str,
        target_agent: str,
        interaction_type: InteractionType,
        content: str = "",
        scene_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AgentInteraction:
        """Record an interaction between agents."""
        interaction = AgentInteraction(
            source_agent=source_agent,
            target_agent=target_agent,
            interaction_type=interaction_type,
            content=content,
            scene_id=scene_id,
            metadata=metadata or {},
            timestamp=datetime.now()
        )

        self.interactions.append(interaction)
        return interaction

    def get_interaction_graph(
        self,
        scene_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get interaction graph data for visualization.

        Returns a graph structure with nodes (agents) and edges (interactions).
        """
        filtered_interactions = self.interactions
        if scene_id:
            filtered_interactions = [
                i for i in self.interactions if i.scene_id == scene_id
            ]

        # Build nodes
        agents = set()
        for interaction in filtered_interactions:
            agents.add(interaction.source_agent)
            agents.add(interaction.target_agent)

        nodes = [
            {
                "id": agent_id,
                "label": agent_id,
                "type": self.agent_registry.get(agent_id, {}).get("agent_type", "unknown")
            }
            for agent_id in agents
        ]

        # Build edges
        edges = [
            {
                "id": i.interaction_id,
                "source": i.source_agent,
                "target": i.target_agent,
                "type": i.interaction_type.value,
                "timestamp": i.timestamp.isoformat()
            }
            for i in filtered_interactions
        ]

        return {
            "nodes": nodes,
            "edges": edges,
            "total_interactions": len(filtered_interactions)
        }

    def get_agent_contributions(
        self,
        scene_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get contribution statistics for each agent."""
        filtered_interactions = self.interactions
        if scene_id:
            filtered_interactions = [
                i for i in self.interactions if i.scene_id == scene_id
            ]

        agent_stats: Dict[str, Dict[str, int]] = {}

        for interaction in filtered_interactions:
            source = interaction.source_agent
            if source not in agent_stats:
                agent_stats[source] = {
                    "total_interactions": 0,
                    "feedback_given": 0,
                    "suggestions_made": 0,
                }

            agent_stats[source]["total_interactions"] += 1

            if interaction.interaction_type == InteractionType.FEEDBACK:
                agent_stats[source]["feedback_given"] += 1
            elif interaction.interaction_type == InteractionType.SUGGESTION:
                agent_stats[source]["suggestions_made"] += 1

        return [
            {
                "agent_id": agent_id,
                **stats
            }
            for agent_id, stats in agent_stats.items()
        ]
