"""
Script to generate Act 1 of a play with proper StoryOutline initialization.
"""

import os
from dotenv import load_dotenv
from thespian.llm import LLMManager
from thespian.llm.playwright import EnhancedPlaywright, SceneRequirements
from thespian.llm.theatrical_memory import TheatricalMemory, CharacterProfile, StoryOutline
from thespian.llm.theatrical_advisors import AdvisorManager
from thespian.llm.quality_control import TheatricalQualityControl
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    # Load environment variables
    load_dotenv()

    # Initialize components
    llm_manager = LLMManager()
    memory = TheatricalMemory()
    advisor_manager = AdvisorManager(llm_manager, memory)
    quality_control = TheatricalQualityControl()

    # Create playwright
    playwright = EnhancedPlaywright(
        name="Cyberpunk Playwright",
        llm_manager=llm_manager,
        memory=memory,
        advisor_manager=advisor_manager,
        quality_control=quality_control,
        model_type="ollama"
    )

    # Initialize story outline with Act 1
    story_outline = StoryOutline(
        title="Cyberpunk Romeo and Juliet",
        acts=[{
            "act_number": 1,
            "description": "The initial meeting and conflict setup",
            "key_events": [
                "Romeo and Juliet meet at a high-tech nightclub",
                "Their families' corporate rivalry is revealed",
                "They plan to meet again despite the danger",
                "Mercutio warns Romeo about the risks",
                "The lovers decide to defy their families"
            ],
            "status": "draft"
        }]
    )

    # Set story outline for playwright
    playwright.story_outline = story_outline

    # Define base play requirements
    base_requirements = {
        "setting": "Neo-Tokyo 2089",
        "characters": ["Romeo", "Juliet", "Mercutio", "Tybalt", "Nurse"],
        "props": ["Holographic displays", "Neural interfaces", "Smart weapons"],
        "lighting": "Neon and holographic",
        "sound": "Electronic ambient",
        "style": "Cyberpunk",
        "period": "2089",
        "target_audience": "Young adults"
    }

    try:
        # Plan Act 1
        logger.info("Planning Act 1...")
        act_plan = playwright.plan_act(1)
        logger.info("Act 1 planning completed successfully")
        logger.info(f"Act plan: {act_plan}")

    except Exception as e:
        logger.error(f"Error planning Act 1: {str(e)}")
        raise

if __name__ == "__main__":
    main() 