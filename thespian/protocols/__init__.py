"""Protocol definitions for agent interactions."""

from .agent_interaction import (
    AgentMessage,
    MessageType,
    Priority,
    ConversationThread,
    AgentInteractionProtocol,
    InteractionCoordinator,
    FeedbackIntegrator
)

from .feedback_schema import (
    FeedbackType,
    Severity,
    FeedbackItem,
    DialogueFeedback,
    CharacterFeedback,
    PacingFeedback,
    TechnicalFeedback,
    AtmosphereFeedback,
    StructuralFeedback,
    ComprehensiveFeedback,
    FeedbackAggregator
)

__all__ = [
    # Agent interaction
    'AgentMessage',
    'MessageType',
    'Priority',
    'ConversationThread',
    'AgentInteractionProtocol',
    'InteractionCoordinator',
    'FeedbackIntegrator',
    
    # Feedback schemas
    'FeedbackType',
    'Severity',
    'FeedbackItem',
    'DialogueFeedback',
    'CharacterFeedback',
    'PacingFeedback',
    'TechnicalFeedback',
    'AtmosphereFeedback',
    'StructuralFeedback',
    'ComprehensiveFeedback',
    'FeedbackAggregator'
]