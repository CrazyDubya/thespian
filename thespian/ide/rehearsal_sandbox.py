"""
Rehearsal Sandbox Backend API

Provides an environment for testing and iterating on scenes,
allowing for rapid prototyping and experimentation.
"""

from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import uuid


class RehearsalState(str, Enum):
    """States of a rehearsal session."""
    SETUP = "setup"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class RehearsalIteration:
    """Represents a single iteration in the rehearsal process."""
    iteration_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    iteration_number: int = 1
    scene_content: str = ""
    feedback: List[str] = field(default_factory=list)
    quality_score: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.now)
    notes: str = ""
    changes_made: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RehearsalSession:
    """Represents a rehearsal session."""
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    scene_id: str = ""
    state: RehearsalState = RehearsalState.SETUP
    iterations: List[RehearsalIteration] = field(default_factory=list)
    current_iteration: Optional[RehearsalIteration] = None
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    goal: str = ""
    success_criteria: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class RehearsalSandbox:
    """
    Backend API for rehearsal and scene iteration.

    Features:
    - Rapid scene iteration with feedback loops
    - Quality tracking across iterations
    - A/B testing of different approaches
    - Integration with playwright for re-generation
    - Experiment management
    """

    def __init__(self):
        """Initialize the rehearsal sandbox."""
        self.sessions: Dict[str, RehearsalSession] = {}
        self.active_session: Optional[RehearsalSession] = None
        self.iteration_callbacks: List[Callable[[RehearsalIteration], None]] = []

    def create_session(
        self,
        scene_id: str,
        goal: str = "",
        success_criteria: Optional[Dict[str, Any]] = None
    ) -> RehearsalSession:
        """
        Create a new rehearsal session.

        Args:
            scene_id: The ID of the scene to rehearse
            goal: The goal of the rehearsal session
            success_criteria: Criteria for determining success

        Returns:
            The newly created RehearsalSession
        """
        session = RehearsalSession(
            scene_id=scene_id,
            goal=goal,
            success_criteria=success_criteria or {},
            started_at=datetime.now()
        )

        self.sessions[session.session_id] = session
        self.active_session = session

        return session

    def start_session(self, session_id: str) -> bool:
        """
        Start a rehearsal session.

        Args:
            session_id: The ID of the session to start

        Returns:
            True if the session was started successfully
        """
        session = self.sessions.get(session_id)
        if not session:
            return False

        if session.state != RehearsalState.SETUP:
            return False

        session.state = RehearsalState.RUNNING
        self.active_session = session

        return True

    def add_iteration(
        self,
        session_id: str,
        scene_content: str,
        feedback: Optional[List[str]] = None,
        quality_score: Optional[float] = None,
        notes: str = "",
        changes_made: Optional[List[str]] = None
    ) -> Optional[RehearsalIteration]:
        """
        Add a new iteration to the rehearsal session.

        Args:
            session_id: The ID of the session
            scene_content: The content of the scene in this iteration
            feedback: Feedback received on this iteration
            quality_score: Quality score for this iteration
            notes: Notes about this iteration
            changes_made: List of changes made in this iteration

        Returns:
            The newly created RehearsalIteration, or None if session not found
        """
        session = self.sessions.get(session_id)
        if not session:
            return None

        iteration = RehearsalIteration(
            iteration_number=len(session.iterations) + 1,
            scene_content=scene_content,
            feedback=feedback or [],
            quality_score=quality_score,
            notes=notes,
            changes_made=changes_made or [],
            timestamp=datetime.now()
        )

        session.iterations.append(iteration)
        session.current_iteration = iteration

        # Notify callbacks
        for callback in self.iteration_callbacks:
            callback(iteration)

        return iteration

    def pause_session(self, session_id: str) -> bool:
        """Pause a running session."""
        session = self.sessions.get(session_id)
        if not session or session.state != RehearsalState.RUNNING:
            return False

        session.state = RehearsalState.PAUSED
        return True

    def resume_session(self, session_id: str) -> bool:
        """Resume a paused session."""
        session = self.sessions.get(session_id)
        if not session or session.state != RehearsalState.PAUSED:
            return False

        session.state = RehearsalState.RUNNING
        self.active_session = session
        return True

    def complete_session(
        self,
        session_id: str,
        final_notes: str = ""
    ) -> bool:
        """
        Complete a rehearsal session.

        Args:
            session_id: The ID of the session to complete
            final_notes: Final notes about the session

        Returns:
            True if the session was completed successfully
        """
        session = self.sessions.get(session_id)
        if not session:
            return False

        session.state = RehearsalState.COMPLETED
        session.completed_at = datetime.now()
        session.metadata["final_notes"] = final_notes

        if self.active_session and self.active_session.session_id == session_id:
            self.active_session = None

        return True

    def cancel_session(self, session_id: str) -> bool:
        """Cancel a rehearsal session."""
        session = self.sessions.get(session_id)
        if not session:
            return False

        session.state = RehearsalState.CANCELLED
        session.completed_at = datetime.now()

        if self.active_session and self.active_session.session_id == session_id:
            self.active_session = None

        return True

    def get_session(self, session_id: str) -> Optional[RehearsalSession]:
        """Get a session by ID."""
        return self.sessions.get(session_id)

    def get_iteration_comparison(
        self,
        session_id: str,
        iteration_numbers: List[int]
    ) -> Dict[str, Any]:
        """
        Compare multiple iterations.

        Args:
            session_id: The ID of the session
            iteration_numbers: List of iteration numbers to compare

        Returns:
            Comparison data for the iterations
        """
        session = self.sessions.get(session_id)
        if not session:
            return {"error": "Session not found"}

        iterations = [
            it for it in session.iterations
            if it.iteration_number in iteration_numbers
        ]

        if not iterations:
            return {"error": "No matching iterations found"}

        return {
            "session_id": session_id,
            "iterations": [
                {
                    "iteration_number": it.iteration_number,
                    "quality_score": it.quality_score,
                    "feedback_count": len(it.feedback),
                    "changes_count": len(it.changes_made),
                    "timestamp": it.timestamp.isoformat(),
                    "content_length": len(it.scene_content),
                }
                for it in iterations
            ],
            "quality_trend": [it.quality_score for it in iterations if it.quality_score],
        }

    def get_best_iteration(
        self,
        session_id: str
    ) -> Optional[RehearsalIteration]:
        """
        Get the best iteration based on quality score.

        Args:
            session_id: The ID of the session

        Returns:
            The iteration with the highest quality score
        """
        session = self.sessions.get(session_id)
        if not session or not session.iterations:
            return None

        iterations_with_scores = [
            it for it in session.iterations
            if it.quality_score is not None
        ]

        if not iterations_with_scores:
            return None

        return max(iterations_with_scores, key=lambda it: it.quality_score or 0)

    def register_iteration_callback(
        self,
        callback: Callable[[RehearsalIteration], None]
    ) -> None:
        """Register a callback to be called when iterations are added."""
        self.iteration_callbacks.append(callback)

    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get a summary of a rehearsal session."""
        session = self.sessions.get(session_id)
        if not session:
            return {"error": "Session not found"}

        best_iteration = self.get_best_iteration(session_id)
        quality_scores = [
            it.quality_score for it in session.iterations
            if it.quality_score is not None
        ]

        return {
            "session_id": session_id,
            "scene_id": session.scene_id,
            "state": session.state.value,
            "goal": session.goal,
            "total_iterations": len(session.iterations),
            "started_at": session.started_at.isoformat(),
            "completed_at": session.completed_at.isoformat() if session.completed_at else None,
            "best_iteration": best_iteration.iteration_number if best_iteration else None,
            "best_quality_score": best_iteration.quality_score if best_iteration else None,
            "average_quality_score": sum(quality_scores) / len(quality_scores) if quality_scores else None,
            "quality_improvement": (
                quality_scores[-1] - quality_scores[0]
                if len(quality_scores) >= 2 else None
            ),
        }

    def get_all_sessions(
        self,
        scene_id: Optional[str] = None,
        state: Optional[RehearsalState] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all sessions, optionally filtered by scene_id and/or state.

        Args:
            scene_id: Optional scene ID to filter by
            state: Optional state to filter by

        Returns:
            List of session summaries
        """
        sessions = list(self.sessions.values())

        if scene_id:
            sessions = [s for s in sessions if s.scene_id == scene_id]

        if state:
            sessions = [s for s in sessions if s.state == state]

        return [self.get_session_summary(s.session_id) for s in sessions]
