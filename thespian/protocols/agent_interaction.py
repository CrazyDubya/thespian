"""
Agent Interaction Protocol for structured communication between theatrical agents.
"""

from typing import Dict, Any, List, Optional, Protocol, Tuple
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import uuid
import json


class MessageType(Enum):
    """Types of messages agents can exchange."""
    FEEDBACK = "feedback"
    SUGGESTION = "suggestion"
    QUESTION = "question"
    RESPONSE = "response"
    DIRECTIVE = "directive"
    APPROVAL = "approval"
    REVISION_REQUEST = "revision_request"
    CONFLICT = "conflict"
    CONSENSUS = "consensus"


class Priority(Enum):
    """Priority levels for agent messages."""
    CRITICAL = 1  # Must be addressed
    HIGH = 2      # Should be addressed
    MEDIUM = 3    # Consider addressing
    LOW = 4       # Optional to address
    INFO = 5      # Informational only


@dataclass
class AgentMessage:
    """Structured message between agents."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sender: str = ""
    recipient: str = ""  # Can be "all" for broadcast
    message_type: MessageType = MessageType.FEEDBACK
    priority: Priority = Priority.MEDIUM
    content: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    in_reply_to: Optional[str] = None
    requires_response: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            "id": self.id,
            "sender": self.sender,
            "recipient": self.recipient,
            "message_type": self.message_type.value,
            "priority": self.priority.value,
            "content": self.content,
            "context": self.context,
            "timestamp": self.timestamp,
            "in_reply_to": self.in_reply_to,
            "requires_response": self.requires_response
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentMessage':
        """Create message from dictionary."""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            sender=data.get("sender", ""),
            recipient=data.get("recipient", ""),
            message_type=MessageType(data.get("message_type", "feedback")),
            priority=Priority(data.get("priority", 3)),
            content=data.get("content", {}),
            context=data.get("context", {}),
            timestamp=data.get("timestamp", datetime.now().isoformat()),
            in_reply_to=data.get("in_reply_to"),
            requires_response=data.get("requires_response", False)
        )


@dataclass
class ConversationThread:
    """Thread of related messages in a conversation."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    topic: str = ""
    participants: List[str] = field(default_factory=list)
    messages: List[AgentMessage] = field(default_factory=list)
    status: str = "active"  # active, resolved, deferred
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    resolved_at: Optional[str] = None
    resolution: Optional[Dict[str, Any]] = None
    
    def add_message(self, message: AgentMessage) -> None:
        """Add a message to the thread."""
        self.messages.append(message)
        if message.sender not in self.participants:
            self.participants.append(message.sender)
    
    def get_messages_by_type(self, message_type: MessageType) -> List[AgentMessage]:
        """Get all messages of a specific type."""
        return [msg for msg in self.messages if msg.message_type == message_type]
    
    def get_unresolved_conflicts(self) -> List[AgentMessage]:
        """Get all unresolved conflict messages."""
        conflicts = self.get_messages_by_type(MessageType.CONFLICT)
        resolved_ids = {msg.in_reply_to for msg in self.messages 
                       if msg.message_type == MessageType.CONSENSUS}
        return [c for c in conflicts if c.id not in resolved_ids]


class AgentInteractionProtocol(Protocol):
    """Protocol defining agent interaction capabilities."""
    
    def send_message(self, message: AgentMessage) -> None:
        """Send a message to another agent or broadcast."""
        ...
    
    def receive_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Receive and process a message, optionally returning a response."""
        ...
    
    def join_conversation(self, thread: ConversationThread) -> None:
        """Join an ongoing conversation thread."""
        ...
    
    def propose_revision(self, content: str, reasoning: str) -> AgentMessage:
        """Propose a revision with reasoning."""
        ...
    
    def evaluate_proposal(self, proposal: AgentMessage) -> AgentMessage:
        """Evaluate another agent's proposal."""
        ...


class InteractionCoordinator:
    """Coordinates interactions between multiple agents."""
    
    def __init__(self):
        self.agents: Dict[str, AgentInteractionProtocol] = {}
        self.threads: Dict[str, ConversationThread] = {}
        self.message_queue: List[AgentMessage] = []
        self.message_history: List[AgentMessage] = []
    
    def register_agent(self, name: str, agent: AgentInteractionProtocol) -> None:
        """Register an agent with the coordinator."""
        self.agents[name] = agent
    
    def create_thread(self, topic: str, initial_participants: List[str]) -> ConversationThread:
        """Create a new conversation thread."""
        thread = ConversationThread(
            topic=topic,
            participants=initial_participants
        )
        self.threads[thread.id] = thread
        
        # Notify participants
        for participant in initial_participants:
            if participant in self.agents:
                self.agents[participant].join_conversation(thread)
        
        return thread
    
    def route_message(self, message: AgentMessage) -> List[AgentMessage]:
        """Route a message and collect responses."""
        responses = []
        self.message_history.append(message)
        
        # Add to relevant thread
        if message.context.get("thread_id"):
            thread_id = message.context["thread_id"]
            if thread_id in self.threads:
                self.threads[thread_id].add_message(message)
        
        # Route to recipient(s)
        if message.recipient == "all":
            # Broadcast to all agents except sender
            for agent_name, agent in self.agents.items():
                if agent_name != message.sender:
                    response = agent.receive_message(message)
                    if response:
                        responses.append(response)
        elif message.recipient in self.agents:
            # Direct message
            response = self.agents[message.recipient].receive_message(message)
            if response:
                responses.append(response)
        
        return responses
    
    def resolve_conflicts(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """Attempt to resolve conflicts in a thread."""
        if thread_id not in self.threads:
            return None
        
        thread = self.threads[thread_id]
        conflicts = thread.get_unresolved_conflicts()
        
        if not conflicts:
            return {"status": "no_conflicts"}
        
        # Implement conflict resolution strategies
        resolution_strategies = {
            "director_override": self._director_resolution,
            "majority_vote": self._majority_vote_resolution,
            "compromise": self._compromise_resolution
        }
        
        # Try director override first (if director involved)
        if any("Director" in c.sender for c in conflicts):
            return resolution_strategies["director_override"](conflicts, thread)
        
        # Otherwise use majority vote
        return resolution_strategies["majority_vote"](conflicts, thread)
    
    def _director_resolution(self, conflicts: List[AgentMessage], thread: ConversationThread) -> Dict[str, Any]:
        """Director has final say in conflicts."""
        director_messages = [c for c in conflicts if "Director" in c.sender]
        if director_messages:
            # Take the most recent director decision
            resolution = director_messages[-1].content
            consensus_msg = AgentMessage(
                sender="System",
                recipient="all",
                message_type=MessageType.CONSENSUS,
                content={"resolution": resolution, "method": "director_override"},
                in_reply_to=director_messages[-1].id
            )
            thread.add_message(consensus_msg)
            return {"status": "resolved", "method": "director_override", "resolution": resolution}
        return None
    
    def _majority_vote_resolution(self, conflicts: List[AgentMessage], thread: ConversationThread) -> Dict[str, Any]:
        """Resolve by majority vote among participating agents."""
        # Count votes for different positions
        votes = {}
        for msg in conflicts:
            position = json.dumps(msg.content.get("position", ""), sort_keys=True)
            votes[position] = votes.get(position, 0) + 1
        
        # Find majority position
        if votes:
            majority_position = max(votes.items(), key=lambda x: x[1])
            if majority_position[1] > len(conflicts) / 2:
                resolution = json.loads(majority_position[0])
                consensus_msg = AgentMessage(
                    sender="System",
                    recipient="all",
                    message_type=MessageType.CONSENSUS,
                    content={"resolution": resolution, "method": "majority_vote", "votes": votes}
                )
                thread.add_message(consensus_msg)
                return {"status": "resolved", "method": "majority_vote", "resolution": resolution}
        
        return {"status": "no_majority"}
    
    def _compromise_resolution(self, conflicts: List[AgentMessage], thread: ConversationThread) -> Dict[str, Any]:
        """Find a compromise between conflicting positions."""
        # This would need domain-specific logic to merge positions
        # For now, return that compromise is needed
        return {"status": "requires_compromise", "conflicts": len(conflicts)}
    
    def get_thread_summary(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """Get a summary of a conversation thread."""
        if thread_id not in self.threads:
            return None
        
        thread = self.threads[thread_id]
        return {
            "id": thread.id,
            "topic": thread.topic,
            "participants": thread.participants,
            "message_count": len(thread.messages),
            "status": thread.status,
            "messages_by_type": {
                msg_type.value: len(thread.get_messages_by_type(msg_type))
                for msg_type in MessageType
            },
            "unresolved_conflicts": len(thread.get_unresolved_conflicts()),
            "created_at": thread.created_at,
            "resolved_at": thread.resolved_at,
            "resolution": thread.resolution
        }
    
    def prioritize_feedback(self, thread_id: str) -> List[AgentMessage]:
        """Get prioritized feedback from a thread."""
        if thread_id not in self.threads:
            return []
        
        thread = self.threads[thread_id]
        feedback_messages = thread.get_messages_by_type(MessageType.FEEDBACK)
        
        # Sort by priority (lower number = higher priority)
        return sorted(feedback_messages, key=lambda m: m.priority.value)


class FeedbackIntegrator:
    """Integrates feedback from multiple agents into actionable revisions."""
    
    def __init__(self):
        self.feedback_categories = {
            "dialogue": [],
            "character": [],
            "pacing": [],
            "technical": [],
            "atmosphere": [],
            "structure": []
        }
    
    def categorize_feedback(self, messages: List[AgentMessage]) -> Dict[str, List[AgentMessage]]:
        """Categorize feedback messages by type."""
        categorized = {cat: [] for cat in self.feedback_categories}
        
        for msg in messages:
            if msg.message_type != MessageType.FEEDBACK:
                continue
            
            # Determine category based on content
            content = msg.content
            if any(key in str(content).lower() for key in ["dialogue", "line", "speech"]):
                categorized["dialogue"].append(msg)
            elif any(key in str(content).lower() for key in ["character", "motivation", "arc"]):
                categorized["character"].append(msg)
            elif any(key in str(content).lower() for key in ["pacing", "rhythm", "tempo"]):
                categorized["pacing"].append(msg)
            elif any(key in str(content).lower() for key in ["lighting", "sound", "props"]):
                categorized["technical"].append(msg)
            elif any(key in str(content).lower() for key in ["mood", "atmosphere", "tone"]):
                categorized["atmosphere"].append(msg)
            else:
                categorized["structure"].append(msg)
        
        return categorized
    
    def create_revision_plan(self, categorized_feedback: Dict[str, List[AgentMessage]]) -> List[Dict[str, Any]]:
        """Create a prioritized revision plan from categorized feedback."""
        revision_plan = []
        
        for category, messages in categorized_feedback.items():
            if not messages:
                continue
            
            # Group by priority
            priority_groups = {}
            for msg in messages:
                priority = msg.priority.value
                if priority not in priority_groups:
                    priority_groups[priority] = []
                priority_groups[priority].append(msg)
            
            # Create revision items
            for priority in sorted(priority_groups.keys()):
                for msg in priority_groups[priority]:
                    revision_plan.append({
                        "category": category,
                        "priority": priority,
                        "agent": msg.sender,
                        "feedback": msg.content,
                        "context": msg.context,
                        "message_id": msg.id
                    })
        
        return revision_plan