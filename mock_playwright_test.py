#!/usr/bin/env python3

"""
Test the consolidated playwright module with mock components for demonstration.
"""

import sys
import os
from pathlib import Path
import json
from datetime import datetime
import uuid
from pydantic import BaseModel
from typing import Dict, Any, List, Optional, Union, Callable

# Add the project root to path
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import the consolidated playwright module
from thespian.llm.consolidated_playwright import (
    Playwright, 
    SceneRequirements, 
    PlaywrightCapability,
    CheckpointData
)

# Mock classes to avoid requiring external LLM API
class MockLLMResponse:
    """Mock response from an LLM."""
    def __init__(self, content):
        self.content = content

class MockLLM:
    """Mock LLM provider."""
    def invoke(self, prompt):
        """Generate a mock response based on the prompt."""
        scene_content = """ACT 1, SCENE 1: THE LABORATORY

[The scene opens in a high-tech laboratory with glowing holographic displays and softly humming equipment. DR. SARAH CHEN works intently at a terminal while DR. JAMES TANAKA reviews data on a floating screen. The AI ASSISTANT's voice comes from speakers throughout the room.]

DR. SARAH CHEN: (focused, typing rapidly) The quantum signature is unlike anything we've ever seen before. The entanglement patterns suggest a temporal component.

DR. JAMES TANAKA: (skeptical, adjusting glasses) That's theoretically impossible, Sarah. Quantum entanglement across time violates causality principles.

AI ASSISTANT: (neutral, analytical) Analysis complete, Doctor Chen. The data shows a 99.7% probability of temporal quantum correlation. This matches your hypothesis.

DR. SARAH CHEN: (excitedly) You see, James? The AI confirms it! We're looking at particles that appear to be entangled not just across space but across time itself.

DR. JAMES TANAKA: (moving to another display, concerned) If this gets into corporate hands before we understand the implications... there are serious ethical considerations.

[The lights briefly flicker. A low rumble is heard.]

AI ASSISTANT: (alert) Warning. Unexpected power fluctuation detected in the quantum containment field.

DR. SARAH CHEN: (alarmed) That shouldn't be possible with our safeguards! AI, run diagnostics immediately.

DR. JAMES TANAKA: (moving quickly to a control panel) I'm stabilizing the field. But look at these readings—the temporal signature is amplifying itself.

[The holographic displays flash with complex data patterns. The rumbling increases.]

DR. SARAH CHEN: (realizing) My god, James. It's not just that the particles are entangled across time. I think they're actually creating a feedback loop with their future states.

DR. JAMES TANAKA: (with dawning understanding) A temporal recursive entanglement? That would mean...

AI ASSISTANT: (urgent) Critical anomaly detected. Recommend immediate containment protocols.

[A bright flash of blue light erupts from the main quantum chamber, briefly engulfing the room, then subsiding.]

DR. SARAH CHEN: (shaken, looking at new data streaming in) The data... it's changing. I think we just witnessed the first documented case of quantum-temporal interaction.

DR. JAMES TANAKA: (solemn) We need to secure this lab immediately. And carefully consider what we do with this discovery.

AI ASSISTANT: (thoughtful) I am detecting patterns in the quantum flux that suggest deliberate organization. This may not be merely a natural phenomenon.

[The scientists exchange worried glances as the lights continue to flicker slightly.]

DR. SARAH CHEN: (quietly) What have we discovered?

[Blackout]

END OF SCENE"""
        return MockLLMResponse(scene_content)

class MockLLMManager:
    """Mock LLM Manager."""
    def get_llm(self, model_type):
        """Return a mock LLM instance."""
        return MockLLM()

class MockMemory:
    """Mock theatrical memory."""
    def __init__(self):
        self.character_profiles = {}
        self.story_outline = None
        
    def update_character_profile(self, char_id, profile):
        """Update a character profile."""
        self.character_profiles[char_id] = profile

class MockQualityControl:
    """Mock quality control system."""
    def evaluate_scene(self, scene, requirements):
        """Evaluate a scene with mock metrics."""
        return {
            "quality_score": 0.85,
            "quality_scores": {
                "dialogue_quality": 0.88,
                "narrative_coherence": 0.82,
                "character_consistency": 0.90,
                "stage_directions": 0.85,
                "thematic_relevance": 0.80
            },
            "feedback": "The scene effectively establishes the scientific premise and character dynamics.",
            "suggestions": [
                "Consider adding more technical details to enhance authenticity",
                "The emotional arc could be stronger between the scientists",
                "Add more visual descriptions of the quantum effects"
            ]
        }

class MockAdvisorManager:
    """Mock advisor manager."""
    def __init__(self, llm_manager, memory):
        self.llm_manager = llm_manager
        self.memory = memory
        self.advisors = {
            "narrative_advisor": None,
            "character_advisor": None,
            "dialogue_advisor": None
        }

class MockSceneProcessor:
    """Mock scene processor."""
    def __init__(self):
        self.min_length = 2000
        self.max_length = 8000
        
    def process_scene_content(self, content):
        """Process scene content."""
        return {
            "scene": content,
            "narrative_analysis": "The scene establishes the central scientific discovery and character dynamics.",
            "raw_content": content
        }

class MockCheckpointManager:
    """Mock checkpoint manager."""
    def cleanup_checkpoint(self, scene_id):
        """Mock cleanup."""
        pass

def main():
    """Run the test with mock components."""
    print("\n" + "="*80)
    print("TESTING CONSOLIDATED PLAYWRIGHT WITH MOCK COMPONENTS")
    print("="*80)
    
    # Initialize mock components
    print("\n[1] Initializing mock components...")
    llm_manager = MockLLMManager()
    memory = MockMemory()
    quality_control = MockQualityControl()
    advisor_manager = MockAdvisorManager(llm_manager, memory)
    scene_processor = MockSceneProcessor()
    checkpoint_manager = MockCheckpointManager()
    
    # Create a playwright instance with different capability combinations
    print("\n[2] Creating playwright instance with modular capabilities...")
    playwright = Playwright(
        name="Mock Playwright",
        llm_manager=llm_manager,
        memory=memory,
        quality_control=quality_control,
        advisor_manager=advisor_manager,
        scene_processor=scene_processor,
        checkpoint_manager=checkpoint_manager,
        model_type="mock_model",
        enabled_capabilities=[
            PlaywrightCapability.BASIC,
            PlaywrightCapability.ITERATIVE_REFINEMENT,
            PlaywrightCapability.CHARACTER_TRACKING
        ]
    )
    
    # Set up a story outline
    print("\n[3] Setting up story outline...")
    from thespian.llm.theatrical_memory import StoryOutline
    story_outline = StoryOutline(
        title="The Quantum Paradox",
        acts=[{
            "act_number": 1,
            "description": "The discovery of quantum entanglement across time",
            "key_events": [
                "Scientists discover temporal quantum entanglement",
                "AI Assistant confirms the extraordinary findings",
                "Unexpected quantum anomaly occurs",
                "Ethical implications are discussed",
                "Decision to secure the discovery"
            ],
            "status": "committed"
        }]
    )
    playwright.story_outline = story_outline
    
    # Create scene requirements
    print("\n[4] Creating scene requirements...")
    requirements = SceneRequirements(
        setting="A high-tech laboratory in Neo-Tokyo",
        characters=["DR. SARAH CHEN", "DR. JAMES TANAKA", "AI ASSISTANT"],
        props=["Holographic displays", "Quantum computers", "Neural interfaces"],
        lighting="Bright, clinical lighting with blue accents",
        sound="Ambient electronic hum with occasional beeps",
        style="Science fiction",
        period="Near future",
        target_audience="Adult",
        act_number=1,
        scene_number=1
    )
    
    # Track progress
    progress_steps = []
    def mock_progress_callback(data):
        progress_steps.append(data)
        print(f"  - {data.get('message', 'Progress update')}")
    
    # Generate a scene
    print("\n[5] Generating scene...")
    try:
        # Monkey patch playwright methods to use our mocks
        old_generate_initial_scene = playwright._generate_initial_scene
        def mock_generate_initial_scene(*args, **kwargs):
            result = old_generate_initial_scene(*args, **kwargs)
            # Mock some timing metrics
            result["timing_metrics"]["total_time"] = 2.5
            return result
        
        playwright._generate_initial_scene = mock_generate_initial_scene
        
        # Generate the scene
        result = playwright.generate_scene(
            requirements=requirements,
            progress_callback=mock_progress_callback
        )
        
        # Show scene content (truncated for display)
        print("\n[6] Generated scene content (first 300 chars):")
        print("-"*80)
        print(result["scene"][:300] + "...")
        print("-"*80)
        
        # Show evaluation
        print("\n[7] Scene evaluation:")
        evaluation = result["evaluation"]
        for metric, score in evaluation.get("quality_scores", {}).items():
            print(f"  - {metric.replace('_', ' ').title()}: {score:.2f}")
        print(f"  Overall quality score: {evaluation.get('quality_score', 0):.2f}")
        
        # Show suggestions
        print("\n[8] Improvement suggestions:")
        for suggestion in evaluation.get("suggestions", []):
            print(f"  - {suggestion}")
        
        # Display timing metrics
        print("\n[9] Timing metrics:")
        for metric, value in result.get("timing_metrics", {}).items():
            print(f"  - {metric.replace('_', ' ').title()}: {value}")
        
        # Show progress tracker
        print("\n[10] Progress steps tracked:")
        for i, step in enumerate(progress_steps, 1):
            print(f"  Step {i}: {step.get('phase', 'unknown')} - {step.get('message', 'No message')}")
        
    except Exception as e:
        print(f"Error during scene generation: {e}")
    
    print("\n" + "="*80)
    print("TEST COMPLETED SUCCESSFULLY")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()