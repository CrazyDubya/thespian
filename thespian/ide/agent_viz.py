"""Agent visualization module for the IDE."""
from typing import Dict, List, Optional, Any, TypedDict
from dataclasses import dataclass
from datetime import datetime

@dataclass
class AgentState:
    """Represents the current state of an agent."""
    name: str
    status: str
    current_task: Optional[str]
    last_updated: datetime
    metrics: Dict[str, Any]

class InteractionData(TypedDict):
    """Type definition for interaction data."""
    source: str
    target: str
    type: str
    data: Dict[str, Any]
    timestamp: datetime

class AgentVisualizer:
    """Visualizes agent states and interactions."""
    
    def __init__(self) -> None:
        """Initialize the visualizer."""
        self.agents: Dict[str, AgentState] = {}
        self.interactions: List[InteractionData] = []
    
    def update_agent_state(self, agent_id: str, state: AgentState) -> None:
        """Update the state of an agent.
        
        Args:
            agent_id: The unique identifier of the agent
            state: The new state of the agent
        """
        self.agents[agent_id] = state
    
    def record_interaction(self, source_id: str, target_id: str, interaction_type: str, data: Dict[str, Any]) -> None:
        """Record an interaction between agents.
        
        Args:
            source_id: The ID of the source agent
            target_id: The ID of the target agent
            interaction_type: The type of interaction
            data: Additional data about the interaction
        """
        self.interactions.append({
            "source": source_id,
            "target": target_id,
            "type": interaction_type,
            "data": data,
            "timestamp": datetime.now()
        })
    
    def get_agent_state(self, agent_id: str) -> Optional[AgentState]:
        """Get the current state of an agent.
        
        Args:
            agent_id: The ID of the agent
            
        Returns:
            The current state of the agent, or None if not found
        """
        return self.agents.get(agent_id)
    
    def get_interactions(self, agent_id: Optional[str] = None) -> List[InteractionData]:
        """Get interactions involving an agent.
        
        Args:
            agent_id: Optional ID of an agent to filter interactions
            
        Returns:
            List of interactions involving the specified agent, or all interactions if no agent specified
        """
        if agent_id is None:
            return self.interactions
        return [
            interaction for interaction in self.interactions
            if interaction["source"] == agent_id or interaction["target"] == agent_id
        ] 