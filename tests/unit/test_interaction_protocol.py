"""
Unit tests for agent interaction protocol.
"""

import pytest
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
    DialogueFeedback
)


class TestAgentMessage:
    """Test AgentMessage functionality."""
    
    def test_create_message(self):
        """Test creating an agent message."""
        msg = AgentMessage(
            sender="Director",
            recipient="Actor",
            message_type=MessageType.FEEDBACK,
            priority=Priority.HIGH,
            content={"feedback": "Needs more emotion"}
        )
        
        assert msg.sender == "Director"
        assert msg.recipient == "Actor"
        assert msg.message_type == MessageType.FEEDBACK
        assert msg.priority == Priority.HIGH
        assert msg.id is not None
        assert msg.timestamp is not None
    
    def test_message_serialization(self):
        """Test message to/from dict conversion."""
        original = AgentMessage(
            sender="StageManager",
            recipient="all",
            message_type=MessageType.DIRECTIVE,
            content={"directive": "Check props"}
        )
        
        # Convert to dict and back
        msg_dict = original.to_dict()
        restored = AgentMessage.from_dict(msg_dict)
        
        assert restored.sender == original.sender
        assert restored.recipient == original.recipient
        assert restored.content == original.content


class TestConversationThread:
    """Test ConversationThread functionality."""
    
    def test_create_thread(self):
        """Test creating a conversation thread."""
        thread = ConversationThread(
            topic="Scene 1 Revision",
            participants=["Director", "Actor1", "Actor2"]
        )
        
        assert thread.topic == "Scene 1 Revision"
        assert len(thread.participants) == 3
        assert thread.status == "active"
        assert len(thread.messages) == 0
    
    def test_add_messages(self):
        """Test adding messages to thread."""
        thread = ConversationThread(topic="Test")
        
        msg1 = AgentMessage(sender="Director", recipient="all", content={"note": "Test"})
        msg2 = AgentMessage(sender="Actor", recipient="Director", content={"response": "OK"})
        
        thread.add_message(msg1)
        thread.add_message(msg2)
        
        assert len(thread.messages) == 2
        assert "Director" in thread.participants
        assert "Actor" in thread.participants
    
    def test_get_messages_by_type(self):
        """Test filtering messages by type."""
        thread = ConversationThread(topic="Test")
        
        feedback = AgentMessage(sender="A", message_type=MessageType.FEEDBACK)
        question = AgentMessage(sender="B", message_type=MessageType.QUESTION)
        response = AgentMessage(sender="C", message_type=MessageType.RESPONSE)
        
        thread.add_message(feedback)
        thread.add_message(question)
        thread.add_message(response)
        
        feedback_msgs = thread.get_messages_by_type(MessageType.FEEDBACK)
        assert len(feedback_msgs) == 1
        assert feedback_msgs[0].sender == "A"
    
    def test_unresolved_conflicts(self):
        """Test tracking unresolved conflicts."""
        thread = ConversationThread(topic="Test")
        
        # Add a conflict
        conflict = AgentMessage(
            id="conflict1",
            sender="Actor",
            message_type=MessageType.CONFLICT,
            content={"issue": "Disagree with direction"}
        )
        thread.add_message(conflict)
        
        # Should have one unresolved conflict
        assert len(thread.get_unresolved_conflicts()) == 1
        
        # Add consensus resolving the conflict
        consensus = AgentMessage(
            sender="Director",
            message_type=MessageType.CONSENSUS,
            in_reply_to="conflict1",
            content={"resolution": "Agreed on compromise"}
        )
        thread.add_message(consensus)
        
        # Should have no unresolved conflicts
        assert len(thread.get_unresolved_conflicts()) == 0


class TestInteractionCoordinator:
    """Test InteractionCoordinator functionality."""
    
    def test_register_agents(self):
        """Test registering agents with coordinator."""
        coordinator = InteractionCoordinator()
        
        class MockAgent:
            def send_message(self, msg): pass
            def receive_message(self, msg): return None
            def join_conversation(self, thread): pass
            def propose_revision(self, content, reasoning): pass
            def evaluate_proposal(self, proposal): pass
        
        agent1 = MockAgent()
        agent2 = MockAgent()
        
        coordinator.register_agent("Agent1", agent1)
        coordinator.register_agent("Agent2", agent2)
        
        assert len(coordinator.agents) == 2
        assert "Agent1" in coordinator.agents
        assert "Agent2" in coordinator.agents
    
    def test_create_thread(self):
        """Test creating conversation threads."""
        coordinator = InteractionCoordinator()
        
        thread = coordinator.create_thread(
            topic="Scene Planning",
            initial_participants=["Director", "Writer"]
        )
        
        assert thread.topic == "Scene Planning"
        assert thread.id in coordinator.threads
        assert len(thread.participants) == 2
    
    def test_conflict_resolution_director(self):
        """Test director override conflict resolution."""
        coordinator = InteractionCoordinator()
        thread = coordinator.create_thread("Test", [])
        
        # Add conflicting messages
        actor_conflict = AgentMessage(
            sender="Actor",
            message_type=MessageType.CONFLICT,
            content={"position": "Keep original"}
        )
        director_conflict = AgentMessage(
            sender="Director",
            message_type=MessageType.CONFLICT,
            content={"position": "Change everything"}
        )
        
        thread.add_message(actor_conflict)
        thread.add_message(director_conflict)
        
        # Resolve conflicts
        resolution = coordinator.resolve_conflicts(thread.id)
        
        assert resolution["status"] == "resolved"
        assert resolution["method"] == "director_override"
        assert resolution["resolution"]["position"] == "Change everything"


class TestFeedbackSchema:
    """Test feedback schema functionality."""
    
    def test_feedback_item(self):
        """Test creating feedback items."""
        item = FeedbackItem(
            type=FeedbackType.DIALOGUE,
            severity=Severity.MAJOR,
            description="Dialogue feels unnatural",
            location="Line 45",
            suggestion="Make it more conversational"
        )
        
        assert item.type == FeedbackType.DIALOGUE
        assert item.severity == Severity.MAJOR
        assert item.location == "Line 45"
    
    def test_dialogue_feedback(self):
        """Test dialogue-specific feedback."""
        feedback = DialogueFeedback(
            character_name="Hamlet",
            line_reference="To be or not to be",
            issue="Too cliché",
            improved_version="To exist or fade away",
            reasoning="Modernize while keeping meaning"
        )
        
        assert feedback.character_name == "Hamlet"
        assert feedback.maintains_voice is True
        assert feedback.improved_version is not None
    
    def test_comprehensive_feedback(self):
        """Test comprehensive feedback package."""
        feedback = ComprehensiveFeedback(
            agent_name="Director",
            agent_role="Director",
            scene_id="act1_scene1",
            overall_impression="Good start but needs work",
            quality_score=0.7
        )
        
        # Add some feedback items
        blocker = FeedbackItem(
            type=FeedbackType.STRUCTURE,
            severity=Severity.BLOCKER,
            description="Scene ends abruptly"
        )
        critical = FeedbackItem(
            type=FeedbackType.CHARACTER,
            severity=Severity.CRITICAL,
            description="Character motivation unclear"
        )
        
        feedback.priority_items.extend([blocker, critical])
        
        # Test methods
        blockers = feedback.get_blockers()
        assert len(blockers) == 1
        assert blockers[0].description == "Scene ends abruptly"
        
        # Test revision instructions
        instructions = feedback.to_revision_instructions()
        assert "MUST FIX BEFORE PROCEEDING" in instructions
        assert "Scene ends abruptly" in instructions
    
    def test_feedback_aggregator(self):
        """Test aggregating feedback from multiple agents."""
        aggregator = FeedbackAggregator(scene_id="test_scene")
        
        # Add feedback from multiple agents
        director_feedback = ComprehensiveFeedback(
            agent_name="Director",
            agent_role="Director",
            scene_id="test_scene",
            overall_impression="Needs more tension",
            quality_score=0.6
        )
        
        actor_feedback = ComprehensiveFeedback(
            agent_name="LeadActor",
            agent_role="Actor",
            scene_id="test_scene",
            overall_impression="Dialogue needs work",
            quality_score=0.7
        )
        
        aggregator.add_feedback(director_feedback)
        aggregator.add_feedback(actor_feedback)
        
        # Test consensus score
        consensus = aggregator.get_consensus_score()
        assert abs(consensus - 0.65) < 0.0001  # Average of 0.6 and 0.7
        
        # Test unified revision plan
        plan = aggregator.create_unified_revision_plan()
        assert "OVERALL QUALITY SCORE: 0.65" in plan
        assert "FEEDBACK FROM 2 AGENTS" in plan


class TestFeedbackIntegrator:
    """Test feedback integration functionality."""
    
    def test_categorize_feedback(self):
        """Test categorizing feedback messages."""
        integrator = FeedbackIntegrator()
        
        messages = [
            AgentMessage(
                sender="Director",
                message_type=MessageType.FEEDBACK,
                content={"issue": "Dialogue needs more emotion"}
            ),
            AgentMessage(
                sender="StageManager",
                message_type=MessageType.FEEDBACK,
                content={"issue": "Lighting cue missing"}
            ),
            AgentMessage(
                sender="Actor",
                message_type=MessageType.FEEDBACK,
                content={"issue": "Character motivation unclear"}
            )
        ]
        
        categorized = integrator.categorize_feedback(messages)
        
        assert len(categorized["dialogue"]) == 1
        assert len(categorized["technical"]) == 1
        assert len(categorized["character"]) == 1
    
    def test_create_revision_plan(self):
        """Test creating revision plan from feedback."""
        integrator = FeedbackIntegrator()
        
        # Create categorized feedback
        dialogue_msg = AgentMessage(
            sender="Director",
            message_type=MessageType.FEEDBACK,
            priority=Priority.HIGH,
            content={"issue": "Fix dialogue", "line": 10}
        )
        
        tech_msg = AgentMessage(
            sender="StageManager",
            message_type=MessageType.FEEDBACK,
            priority=Priority.CRITICAL,
            content={"issue": "Add sound cue", "location": "entrance"}
        )
        
        categorized = {
            "dialogue": [dialogue_msg],
            "technical": [tech_msg],
            "character": [],
            "pacing": [],
            "atmosphere": [],
            "structure": []
        }
        
        plan = integrator.create_revision_plan(categorized)
        
        assert len(plan) == 2
        assert plan[0]["priority"] == Priority.CRITICAL.value  # Critical comes first
        assert plan[0]["category"] == "technical"
        assert plan[1]["priority"] == Priority.HIGH.value
        assert plan[1]["category"] == "dialogue"