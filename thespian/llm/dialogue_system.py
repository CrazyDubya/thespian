"""
Dialogue system for advisor-playwright interactions.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, ConfigDict
from thespian.llm.theatrical_advisors import TheatricalAdvisor, AdvisorFeedback
from thespian.llm.theatrical_memory import TheatricalMemory
import time


class DialogueMemory(BaseModel):
    """Memory for dialogue interactions between playwrights and advisors."""

    scene_id: str
    advisor_type: str
    feedback_history: List[Dict[str, Any]] = Field(default_factory=list)
    questions_asked: List[str] = Field(default_factory=list)
    last_interaction: float = Field(default_factory=time.time)


class DialogueSystem(BaseModel):
    """Manages dialogue interactions between playwrights and advisors."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    memory: TheatricalMemory
    dialogue_memories: Dict[str, DialogueMemory] = Field(default_factory=dict)

    def get_specialized_questions(self, advisor_type: str, feedback: AdvisorFeedback) -> List[str]:
        """Generate specialized questions based on advisor type and feedback."""
        questions = []

        if advisor_type == "character":
            if feedback.score < 0.7:
                questions.extend(
                    [
                        "Could you elaborate on how to strengthen the character's emotional arc?",
                        "What specific aspects of character consistency need improvement?",
                        "How can I better develop the relationships between characters?",
                    ]
                )
            if feedback.priority <= 2:
                questions.extend(
                    [
                        "Which character's development needs the most attention?",
                        "How can I make the character's voice more distinctive?",
                    ]
                )

        elif advisor_type == "dramatic":
            if feedback.score < 0.7:
                questions.extend(
                    [
                        "How can I improve the scene's dramatic tension?",
                        "What specific elements would strengthen the climax?",
                        "How can I better structure the emotional beats?",
                    ]
                )
            if feedback.priority <= 2:
                questions.extend(
                    [
                        "Which part of the dramatic structure needs the most work?",
                        "How can I make the scene's impact more powerful?",
                    ]
                )

        elif advisor_type == "technical":
            if feedback.score < 0.7:
                questions.extend(
                    [
                        "How can I better integrate the technical elements?",
                        "What specific stage directions would improve the scene?",
                        "How can I make the lighting and sound more effective?",
                    ]
                )
            if feedback.priority <= 2:
                questions.extend(
                    [
                        "Which technical elements need the most attention?",
                        "How can I make the scene more technically feasible?",
                    ]
                )

        elif advisor_type == "thematic":
            if feedback.score < 0.7:
                questions.extend(
                    [
                        "How can I strengthen the thematic elements?",
                        "What specific symbols or motifs would enhance the scene?",
                        "How can I better integrate the period and style?",
                    ]
                )
            if feedback.priority <= 2:
                questions.extend(
                    [
                        "Which thematic aspects need the most development?",
                        "How can I make the scene more resonant with the target audience?",
                    ]
                )

        return questions

    def engage_with_advisor(
        self,
        scene_id: str,
        advisor_type: str,
        advisor: TheatricalAdvisor,
        feedback: AdvisorFeedback,
        scene: str,
        context: Dict[str, Any],
    ) -> AdvisorFeedback:
        """Engage in multi-turn dialogue with an advisor."""
        # Initialize or get dialogue memory
        memory_key = f"{scene_id}_{advisor_type}"
        if memory_key not in self.dialogue_memories:
            self.dialogue_memories[memory_key] = DialogueMemory(
                scene_id=scene_id, advisor_type=advisor_type
            )
        dialogue_memory = self.dialogue_memories[memory_key]

        # Generate specialized questions
        questions = self.get_specialized_questions(advisor_type, feedback)

        # Filter out previously asked questions
        new_questions = [q for q in questions if q not in dialogue_memory.questions_asked]

        if not new_questions:
            return feedback

        # Ask questions and get follow-up feedback
        enhanced_feedback = feedback
        for question in new_questions[:2]:  # Limit to 2 questions per turn
            dialogue_memory.questions_asked.append(question)

            # Get follow-up feedback
            follow_up = self._get_follow_up_feedback(advisor, scene, context, feedback, question)

            # Update feedback with follow-up information
            enhanced_feedback = self._merge_feedback(enhanced_feedback, follow_up)

            # Store in dialogue history
            dialogue_memory.feedback_history.append(
                {"question": question, "feedback": follow_up.model_dump() if hasattr(follow_up, 'model_dump') else follow_up.dict(), "timestamp": time.time()}
            )

        dialogue_memory.last_interaction = time.time()
        return enhanced_feedback

    def _get_follow_up_feedback(
        self,
        advisor: TheatricalAdvisor,
        scene: str,
        context: Dict[str, Any],
        original_feedback: AdvisorFeedback,
        question: str,
    ) -> AdvisorFeedback:
        """Get follow-up feedback from an advisor."""
        llm = advisor.get_llm()

        prompt = f"""As a theatrical advisor, provide detailed follow-up feedback on this scene:

Scene:
{scene}

Original Feedback:
{original_feedback.feedback}

Specific Question:
{question}

Consider the original feedback and provide detailed guidance addressing the specific question.
Focus on practical, actionable suggestions that would improve the scene.

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

        # Try LLM with self-correction
        max_retries = 2
        for attempt in range(max_retries + 1):
            if attempt > 0:
                # Add corrective feedback for retry
                correction_prompt = f"""CORRECTION NEEDED: Your previous response didn't follow the required format.

Previous response that failed:
{response.content[:1000]}...

Please provide feedback in EXACTLY this format:
SCORE: [number between 0.0 and 1.0]
FEEDBACK: [your feedback text]
SUGGESTIONS:
- [suggestion 1]
- [suggestion 2]
EXAMPLES:
- [example 1]
- [example 2]
PRIORITY: [number between 1 and 5]

{prompt}"""
                response = llm.invoke(correction_prompt)
            else:
                response = llm.invoke(prompt)

            # Parse response into structured feedback
            lines = response.content.split("\n")
            score = original_feedback.score  # Default to original score
            feedback = "Follow-up feedback provided"  # Default feedback
            suggestions = []
            examples = []
            priority = original_feedback.priority  # Default to original priority
            
            # Try to parse the response
            parsing_success = False
            current_section = None
            for line in lines:
                line = line.strip()
                if not line:
                    continue

                if line.startswith("SCORE:"):
                    try:
                        score = float(line.split(":")[1].strip())
                        parsing_success = True
                    except (ValueError, IndexError):
                        pass
                elif line.startswith("FEEDBACK:"):
                    feedback = line.split(":")[1].strip()
                    parsing_success = True
                elif line.startswith("SUGGESTIONS:"):
                    current_section = "suggestions"
                elif line.startswith("EXAMPLES:"):
                    current_section = "examples"
                elif line.startswith("PRIORITY:"):
                    try:
                        priority = int(line.split(":")[1].strip())
                        parsing_success = True
                    except (ValueError, IndexError):
                        pass
                elif line.startswith("- "):
                    if current_section == "suggestions":
                        suggestions.append(line[2:])
                    elif current_section == "examples":
                        examples.append(line[2:])
            
            if parsing_success:
                break
            else:
                logger.warning(f"Dialogue feedback parsing attempt {attempt + 1} failed")
                if attempt == max_retries:
                    logger.warning("Failed to parse dialogue feedback - using defaults")


        return AdvisorFeedback(
            score=score,
            feedback=feedback,
            suggestions=suggestions,
            specific_examples=examples,
            priority=priority,
        )

    def _merge_feedback(
        self, original: AdvisorFeedback, follow_up: AdvisorFeedback
    ) -> AdvisorFeedback:
        """Merge original and follow-up feedback."""
        return AdvisorFeedback(
            score=max(original.score, follow_up.score),  # Take the better score
            feedback=f"{original.feedback}\n\nFollow-up: {follow_up.feedback}",
            suggestions=original.suggestions + follow_up.suggestions,
            specific_examples=original.specific_examples + follow_up.specific_examples,
            priority=min(original.priority, follow_up.priority),  # Take the higher priority
        )

    def get_dialogue_history(self, scene_id: str, advisor_type: str) -> List[Dict[str, Any]]:
        """Get dialogue history for a scene and advisor."""
        memory_key = f"{scene_id}_{advisor_type}"
        if memory_key in self.dialogue_memories:
            return self.dialogue_memories[memory_key].feedback_history
        return []
