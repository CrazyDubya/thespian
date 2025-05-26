"""
Demonstration of agent interaction protocol in action.
"""

import sys
sys.path.append('.')

from thespian.protocols import (
    AgentMessage,
    MessageType,
    Priority,
    ConversationThread,
    InteractionCoordinator,
    FeedbackIntegrator,
    ComprehensiveFeedback,
    FeedbackAggregator,
    FeedbackType,
    Severity,
    FeedbackItem,
    DialogueFeedback,
    CharacterFeedback,
    PacingFeedback
)


class DemoAgent:
    """Demo agent that can participate in conversations."""
    
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.received_messages = []
    
    def send_message(self, message: AgentMessage) -> None:
        """Send a message (in real implementation, would use coordinator)."""
        print(f"{self.name} sends: {message.content}")
    
    def receive_message(self, message: AgentMessage) -> AgentMessage:
        """Receive and respond to a message."""
        self.received_messages.append(message)
        print(f"{self.name} receives from {message.sender}: {message.content}")
        
        # Generate response based on role
        if self.role == "Director" and message.message_type == MessageType.SUGGESTION:
            return AgentMessage(
                sender=self.name,
                recipient=message.sender,
                message_type=MessageType.APPROVAL,
                content={"response": "Good suggestion, let's implement it"},
                in_reply_to=message.id
            )
        elif self.role == "Actor" and message.message_type == MessageType.FEEDBACK:
            return AgentMessage(
                sender=self.name,
                recipient=message.sender,
                message_type=MessageType.RESPONSE,
                content={"response": "I'll work on that"},
                in_reply_to=message.id
            )
        return None
    
    def join_conversation(self, thread: ConversationThread) -> None:
        """Join a conversation thread."""
        print(f"{self.name} joins conversation: {thread.topic}")
    
    def propose_revision(self, content: str, reasoning: str) -> AgentMessage:
        """Propose a revision."""
        return AgentMessage(
            sender=self.name,
            recipient="all",
            message_type=MessageType.SUGGESTION,
            priority=Priority.MEDIUM,
            content={"revision": content, "reasoning": reasoning}
        )
    
    def evaluate_proposal(self, proposal: AgentMessage) -> AgentMessage:
        """Evaluate a proposal from another agent."""
        return AgentMessage(
            sender=self.name,
            recipient=proposal.sender,
            message_type=MessageType.RESPONSE,
            content={"evaluation": "Looks good", "approved": True}
        )


def demonstrate_basic_interaction():
    """Demonstrate basic agent interaction."""
    print("=== Basic Agent Interaction Demo ===\n")
    
    # Create coordinator and agents
    coordinator = InteractionCoordinator()
    
    director = DemoAgent("Director", "Director")
    actor1 = DemoAgent("LeadActor", "Actor")
    actor2 = DemoAgent("SupportingActor", "Actor")
    stage_manager = DemoAgent("StageManager", "StageManager")
    
    # Register agents
    coordinator.register_agent("Director", director)
    coordinator.register_agent("LeadActor", actor1)
    coordinator.register_agent("SupportingActor", actor2)
    coordinator.register_agent("StageManager", stage_manager)
    
    # Create a conversation thread
    thread = coordinator.create_thread(
        topic="Scene 2 Workshop",
        initial_participants=["Director", "LeadActor", "SupportingActor", "StageManager"]
    )
    
    print(f"\nThread created: {thread.topic}")
    print(f"Participants: {', '.join(thread.participants)}\n")
    
    # Director sends initial feedback
    director_msg = AgentMessage(
        sender="Director",
        recipient="all",
        message_type=MessageType.FEEDBACK,
        priority=Priority.HIGH,
        content={
            "feedback": "The opening needs more energy",
            "specific_notes": "Consider a more dynamic entrance"
        },
        context={"thread_id": thread.id}
    )
    
    print("1. Director sends feedback:")
    responses = coordinator.route_message(director_msg)
    print(f"   Received {len(responses)} responses\n")
    
    # Actor proposes a revision
    actor_proposal = actor1.propose_revision(
        "What if I enter running, out of breath?",
        "Creates immediate tension and energy"
    )
    actor_proposal.context = {"thread_id": thread.id}
    
    print("2. Lead Actor proposes revision:")
    responses = coordinator.route_message(actor_proposal)
    print(f"   Received {len(responses)} responses\n")
    
    # Stage manager raises a concern
    concern = AgentMessage(
        sender="StageManager",
        recipient="all",
        message_type=MessageType.FEEDBACK,
        priority=Priority.CRITICAL,
        content={
            "concern": "Running entrance requires clear path",
            "technical_note": "Need to reposition furniture"
        },
        context={"thread_id": thread.id}
    )
    
    print("3. Stage Manager raises concern:")
    coordinator.route_message(concern)
    
    # Get thread summary
    summary = coordinator.get_thread_summary(thread.id)
    print(f"\nThread Summary:")
    print(f"- Messages: {summary['message_count']}")
    print(f"- Message types: {summary['messages_by_type']}")
    print(f"- Status: {summary['status']}")


def demonstrate_feedback_aggregation():
    """Demonstrate feedback aggregation from multiple agents."""
    print("\n\n=== Feedback Aggregation Demo ===\n")
    
    scene_id = "act1_scene3"
    aggregator = FeedbackAggregator(scene_id=scene_id)
    
    # Director's comprehensive feedback
    director_feedback = ComprehensiveFeedback(
        agent_name="Director",
        agent_role="Director",
        scene_id=scene_id,
        overall_impression="Strong emotional core but pacing issues",
        quality_score=0.75
    )
    
    # Add specific feedback items
    director_feedback.dialogue_feedback.append(
        DialogueFeedback(
            character_name="Protagonist",
            line_reference="I can't go on like this",
            issue="Too melodramatic",
            improved_version="This isn't working anymore",
            reasoning="More understated delivery fits character better"
        )
    )
    
    director_feedback.pacing_feedback = PacingFeedback(
        overall_pace="slow",
        problem_areas=[
            {"location": "middle section", "issue": "drags without conflict"},
            {"location": "ending", "issue": "rushes resolution"}
        ],
        suggested_beats=["Add interruption at midpoint", "Extend final moment"],
        tension_curve=[0.3, 0.4, 0.3, 0.5, 0.9, 0.6],
        recommended_adjustments="Increase tempo in middle, slow down ending"
    )
    
    director_feedback.priority_items.extend([
        FeedbackItem(
            type=FeedbackType.PACING,
            severity=Severity.MAJOR,
            description="Middle section loses momentum",
            suggestion="Add conflict or revelation"
        ),
        FeedbackItem(
            type=FeedbackType.STRUCTURE,
            severity=Severity.CRITICAL,
            description="Ending feels rushed",
            suggestion="Add beat for emotional resolution"
        )
    ])
    
    # Actor's feedback
    actor_feedback = ComprehensiveFeedback(
        agent_name="LeadActor",
        agent_role="Actor",
        scene_id=scene_id,
        overall_impression="Character journey unclear in places",
        quality_score=0.70
    )
    
    actor_feedback.character_feedback.append(
        CharacterFeedback(
            character_name="Protagonist",
            consistency_score=0.8,
            arc_progression="Good start but unclear middle",
            inconsistencies=["Sudden shift in attitude unexplained"],
            growth_opportunities=["Show internal struggle more clearly"],
            relationship_dynamics={"Antagonist": "Needs more complexity"}
        )
    )
    
    actor_feedback.priority_items.append(
        FeedbackItem(
            type=FeedbackType.CHARACTER,
            severity=Severity.MAJOR,
            description="Character motivation needs clarification",
            location="Turning point",
            suggestion="Add internal monologue or physical action showing decision"
        )
    )
    
    # Stage Manager's feedback
    stage_mgr_feedback = ComprehensiveFeedback(
        agent_name="StageManager",
        agent_role="StageManager",
        scene_id=scene_id,
        overall_impression="Technical elements need coordination",
        quality_score=0.65
    )
    
    stage_mgr_feedback.priority_items.extend([
        FeedbackItem(
            type=FeedbackType.TECHNICAL,
            severity=Severity.BLOCKER,
            description="Quick change impossible with current staging",
            location="Scene transition",
            suggestion="Add 30 seconds of dialogue or rearrange blocking"
        ),
        FeedbackItem(
            type=FeedbackType.CONTINUITY,
            severity=Severity.CRITICAL,
            description="Prop mentioned but never established",
            location="Page 5",
            suggestion="Add prop to earlier scene or cut reference"
        )
    ])
    
    # Aggregate all feedback
    aggregator.add_feedback(director_feedback)
    aggregator.add_feedback(actor_feedback)
    aggregator.add_feedback(stage_mgr_feedback)
    
    # Get consensus and create plan
    consensus_score = aggregator.get_consensus_score()
    print(f"Consensus Quality Score: {consensus_score:.2f}/1.0")
    
    # Check for blockers
    blockers = aggregator.get_all_blockers()
    if blockers:
        print(f"\nBLOCKING ISSUES ({len(blockers)}):")
        for agent, blocker in blockers:
            print(f"- [{agent}] {blocker.description}")
    
    # Create unified revision plan
    print("\n=== UNIFIED REVISION PLAN ===")
    print(aggregator.create_unified_revision_plan())


def demonstrate_conflict_resolution():
    """Demonstrate conflict resolution between agents."""
    print("\n\n=== Conflict Resolution Demo ===\n")
    
    coordinator = InteractionCoordinator()
    
    # Register demo agents
    coordinator.register_agent("Director", DemoAgent("Director", "Director"))
    coordinator.register_agent("Actor", DemoAgent("Actor", "Actor"))
    coordinator.register_agent("Designer", DemoAgent("Designer", "Designer"))
    
    # Create thread for conflict
    thread = coordinator.create_thread(
        topic="Costume Design Conflict",
        initial_participants=["Director", "Actor", "Designer"]
    )
    
    # Actor wants modern costume
    actor_position = AgentMessage(
        sender="Actor",
        recipient="all",
        message_type=MessageType.CONFLICT,
        content={
            "position": "modern casual wear",
            "reasoning": "Makes character relatable"
        },
        context={"thread_id": thread.id}
    )
    
    # Designer wants period costume
    designer_position = AgentMessage(
        sender="Designer",
        recipient="all",
        message_type=MessageType.CONFLICT,
        content={
            "position": "period accurate costume",
            "reasoning": "Maintains historical authenticity"
        },
        context={"thread_id": thread.id}
    )
    
    # Director's decisive input
    director_position = AgentMessage(
        sender="Director",
        recipient="all",
        message_type=MessageType.CONFLICT,
        content={
            "position": "modernized period - contemporary cut with period details",
            "reasoning": "Balances accessibility with production concept"
        },
        context={"thread_id": thread.id}
    )
    
    # Add conflicts
    coordinator.route_message(actor_position)
    coordinator.route_message(designer_position)
    coordinator.route_message(director_position)
    
    print("Positions submitted:")
    print("- Actor: modern casual wear")
    print("- Designer: period accurate costume")
    print("- Director: modernized period hybrid")
    
    # Resolve conflict
    resolution = coordinator.resolve_conflicts(thread.id)
    
    print(f"\nResolution: {resolution['status']}")
    print(f"Method: {resolution['method']}")
    print(f"Final decision: {resolution['resolution']['position']}")


def demonstrate_feedback_integration():
    """Demonstrate integrating feedback into revision plan."""
    print("\n\n=== Feedback Integration Demo ===\n")
    
    integrator = FeedbackIntegrator()
    
    # Create various feedback messages
    messages = [
        AgentMessage(
            sender="Director",
            message_type=MessageType.FEEDBACK,
            priority=Priority.CRITICAL,
            content={
                "issue": "Opening dialogue too exposition-heavy",
                "suggestion": "Start with action, weave in backstory"
            }
        ),
        AgentMessage(
            sender="Actor",
            message_type=MessageType.FEEDBACK,
            priority=Priority.HIGH,
            content={
                "issue": "Character transition feels abrupt",
                "line": 45,
                "suggestion": "Add moment of realization"
            }
        ),
        AgentMessage(
            sender="StageManager",
            message_type=MessageType.FEEDBACK,
            priority=Priority.CRITICAL,
            content={
                "issue": "Lighting transition impossible as written",
                "location": "page 10",
                "suggestion": "Add 10 seconds of stage business"
            }
        ),
        AgentMessage(
            sender="Designer",
            message_type=MessageType.FEEDBACK,
            priority=Priority.MEDIUM,
            content={
                "issue": "Atmosphere needs more visual elements",
                "suggestion": "Add fog effect and dim lighting"
            }
        )
    ]
    
    # Categorize feedback
    categorized = integrator.categorize_feedback(messages)
    
    print("Feedback Categories:")
    for category, msgs in categorized.items():
        if msgs:
            print(f"- {category}: {len(msgs)} items")
    
    # Create revision plan
    revision_plan = integrator.create_revision_plan(categorized)
    
    print("\nPrioritized Revision Plan:")
    for i, item in enumerate(revision_plan, 1):
        print(f"{i}. [{item['category'].upper()}] Priority {item['priority']}")
        print(f"   From: {item['agent']}")
        print(f"   Feedback: {item['feedback']}")
        print()


if __name__ == "__main__":
    # Run all demonstrations
    demonstrate_basic_interaction()
    demonstrate_feedback_aggregation()
    demonstrate_conflict_resolution()
    demonstrate_feedback_integration()
    
    print("\n=== Interaction Protocol Demo Complete ===")
    print("\nKey Features Demonstrated:")
    print("- Structured message passing between agents")
    print("- Conversation threading and context tracking")
    print("- Comprehensive feedback schemas")
    print("- Feedback aggregation from multiple agents")
    print("- Conflict resolution with director override")
    print("- Prioritized revision planning")