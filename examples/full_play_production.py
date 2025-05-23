"""
Example of generating a full 3-act play with 5 scenes each.
"""

import os
from thespian.llm import LLMManager
from thespian.llm.consolidated_playwright import Playwright, SceneRequirements, PlaywrightCapability, create_playwright
from thespian.llm.theatrical_memory import TheatricalMemory, CharacterProfile, StoryOutline
from thespian.llm.manager import LLMResponseEncoder
import logging
import json
from datetime import datetime
from pathlib import Path
from thespian.llm.quality_control import TheatricalQualityControl
import time
from thespian.llm.run_manager import RunManager
from extract_scenes import consolidate_scenes
import uuid
from thespian.llm.theatrical_advisors import AdvisorManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_character_profile(name: str, description: str, background: str) -> CharacterProfile:
    """Create a character profile."""
    return CharacterProfile(
        id=name.lower(),  # Use lowercase name as ID
        name=name,
        description=description,
        background=background,
        relationships={},
        goals=[],
        conflicts=[],
        motivations=[],  # Add empty motivations list
        development_arc=[]  # Change to list type
    )

def generate_act(
    playwright: Playwright,
    act_number: int,
    requirements: SceneRequirements,
    run_manager: RunManager,
    run_id: str,
    previous_scenes: list = None
) -> list:
    """Generate a complete act with 5 scenes."""
    try:
        scenes = []
        previous_scene = None
        previous_feedback = None
        
        # Update run status
        run_manager.update_run_status(run_id, "in_progress", {
            "current_act": act_number,
            "current_scene": None
        })
        
        # Check if act is already completed
        current_act = playwright.story_outline.get_act_outline(act_number)
        if current_act and current_act["status"] == "completed":
            logger.info(f"Act {act_number} is already completed")
            return scenes
        
        # First, plan the act collaboratively
        logger.info(f"Planning Act {act_number}")
        try:
            act_plan = playwright.plan_act(act_number)
            run_manager.save_act_plan(run_id, act_number, act_plan)
        except ValueError as e:
            logger.error(f"Error planning act {act_number}: {str(e)}")
            run_manager.save_error(run_id, e, {
                "act_number": act_number,
                "stage": "planning"
            })
            raise
        
        # Update act status to in_progress
        playwright.story_outline.update_act_status(act_number, "in_progress")
        
        # Generate each scene following the committed plan
        for scene_number in range(1, 6):
            logger.info(f"Generating Act {act_number}, Scene {scene_number}")
            
            # Update run status
            run_manager.update_run_status(run_id, "in_progress", {
                "current_act": act_number,
                "current_scene": scene_number
            })
            
            try:
                # Update scene requirements based on act and scene number
                scene_requirements = SceneRequirements(
                    setting=requirements.setting,
                    characters=requirements.characters,
                    props=requirements.props,
                    lighting=requirements.lighting,
                    sound=requirements.sound,
                    style=requirements.style,
                    period=requirements.period,
                    target_audience=requirements.target_audience,
                    act_number=act_number,
                    scene_number=scene_number
                )
                
                # Generate scene with retry logic
                max_retries = 3
                retry_count = 0
                while retry_count < max_retries:
                    try:
                        result = playwright.generate_scene(
                            requirements=scene_requirements,
                            previous_scene=previous_scene,
                            previous_feedback=previous_feedback,
                            progress_callback=lambda current, total: logger.info(f"Progress: {current}/{total}")
                        )
                        break
                    except Exception as e:
                        retry_count += 1
                        if retry_count == max_retries:
                            logger.error(f"Failed to generate scene after {max_retries} attempts: {str(e)}")
                            run_manager.save_error(run_id, e, {
                                "act_number": act_number,
                                "scene_number": scene_number,
                                "retry_count": retry_count,
                                "stage": "generation"
                            })
                            raise
                        logger.warning(f"Retry {retry_count}/{max_retries} for scene generation")
                        time.sleep(1)  # Add delay between retries
                
                scenes.append(result)
                previous_scene = result["scene"]
                previous_feedback = result["evaluation"]
                
                # Save scene using run manager
                run_manager.save_scene(run_id, act_number, scene_number, {
                    "scene": result["scene"],
                    "evaluation": result["evaluation"],
                    "timing_metrics": result["timing_metrics"],
                    "iterations": result["iterations"],
                    "iteration_metrics": result["iteration_metrics"],
                    "scene_number": scene_number,
                    "act_number": act_number,
                    "timestamp": datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"Error generating scene {scene_number} for act {act_number}: {str(e)}")
                run_manager.save_error(run_id, e, {
                    "act_number": act_number,
                    "scene_number": scene_number,
                    "stage": "generation"
                })
                raise
        
        # Update act status to completed
        playwright.story_outline.update_act_status(act_number, "completed")
        
        # Validate act sequence
        if not playwright.story_outline.validate_act_sequence():
            logger.warning(f"Act {act_number} sequence validation failed")
            run_manager.save_error(run_id, ValueError("Act sequence validation failed"), {
                "act_number": act_number,
                "stage": "validation"
            })
        
        # Save act summary
        run_manager.save_artifact(run_id, "act_summary", {
            "act_number": act_number,
            "plan": act_plan["committed_outline"],
            "scenes": [{
                "scene_number": i + 1,
                "evaluation": scene["evaluation"],
                "timing_metrics": scene["timing_metrics"]
            } for i, scene in enumerate(scenes)],
            "character_development": act_plan.get("character_development", ""),
            "thematic_elements": act_plan.get("thematic_elements", ""),
            "timestamp": datetime.now().isoformat(),
            "status": "completed"
        }, subpath=f"acts/act{act_number}")
        
        # Update run status
        run_manager.update_run_status(run_id, "act_completed", {
            "completed_act": act_number,
            "current_act": None,
            "current_scene": None
        })
        
        return scenes
        
    except Exception as e:
        logger.error(f"Error generating act {act_number}: {str(e)}")
        run_manager.save_error(run_id, e, {
            "act_number": act_number,
            "stage": "act_generation"
        })
        raise

def main():
    # Initialize LLM manager
    llm_manager = LLMManager()
    
    # Initialize memory system
    memory = TheatricalMemory()
    
    # Initialize advisor manager
    advisor_manager = AdvisorManager(llm_manager, memory)
    
    # Initialize quality control
    quality_control = TheatricalQualityControl()
    
    # Create playwright using factory function
    playwright = create_playwright(
        name="Cyberpunk Playwright",
        llm_manager=llm_manager,
        memory=memory,
        capabilities=[
            PlaywrightCapability.BASIC,
            PlaywrightCapability.ITERATIVE_REFINEMENT,
            PlaywrightCapability.COLLABORATIVE
        ],
        advisor_manager=advisor_manager,
        quality_control=quality_control,
        model_type="ollama"
    )
    
    # Initialize run manager
    run_manager = RunManager()
    
    try:
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
        
        # Create a new run
        run_id = str(uuid.uuid4())
        run_manager.start_run(run_id)
        run_manager.save_artifact(run_id, "metadata", {
            "title": "Cyberpunk Romeo and Juliet",
            "requirements": base_requirements,
            "start_time": datetime.now().isoformat()
        })
        
        # Initialize story outline
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
            }, {
                "act_number": 2,
                "description": "The deepening conflict and secret meetings",
                "key_events": [
                    "Romeo and Juliet meet in secret using VR technology",
                    "Tybalt challenges Romeo to a cyber-duel",
                    "Mercutio is injured in the duel",
                    "Romeo seeks revenge",
                    "The lovers plan their escape"
                ],
                "status": "draft"
            }, {
                "act_number": 3,
                "description": "The tragic conclusion",
                "key_events": [
                    "The escape plan goes wrong",
                    "Communication breakdown leads to tragedy",
                    "Romeo and Juliet's final moments",
                    "The families' reconciliation",
                    "The legacy of their love"
                ],
                "status": "draft"
            }]
        )
        
        # Set story outline for playwright
        playwright.story_outline = story_outline
        
        # Generate acts sequentially, stopping on first failure
        all_scenes = []
        for act_number in range(1, 4):
            logger.info(f"Generating Act {act_number}")
            
            # Create act-specific requirements
            act_requirements = SceneRequirements(
                **base_requirements,
                act_number=act_number,
                scene_number=1  # Initial scene number, will be updated in generate_act
            )
            
            try:
                act_scenes = generate_act(playwright, act_number, act_requirements, run_manager, run_id)
                all_scenes.extend(act_scenes)
                
                # Verify act was actually completed
                current_act = playwright.story_outline.get_act_outline(act_number)
                if not current_act or current_act["status"] != "completed":
                    raise ValueError(f"Act {act_number} was not properly completed")
                
            except Exception as e:
                logger.error(f"Failed to generate Act {act_number}: {str(e)}")
                run_manager.save_error(run_id, e, {
                    "act_number": act_number,
                    "stage": "act_generation",
                    "completed_acts": list(range(1, act_number))
                })
                
                # Update run status to failed and stop
                run_manager.update_run_status(run_id, "failed", {
                    "end_time": datetime.now().isoformat(),
                    "error": str(e),
                    "failed_act": act_number,
                    "completed_acts": list(range(1, act_number))
                })
                
                # Save partial play summary
                if all_scenes:
                    run_manager.save_artifact(run_id, "partial_play_summary", {
                        "title": "Cyberpunk Romeo and Juliet",
                        "acts": [{
                            "act_number": i + 1,
                            "scenes": [{
                                "scene_number": j + 1,
                                "evaluation": scene["evaluation"],
                                "timing_metrics": scene["timing_metrics"]
                            } for j, scene in enumerate(all_scenes[i*5:(i+1)*5])]
                        } for i in range(len(all_scenes) // 5)],
                        "timestamp": datetime.now().isoformat(),
                        "status": "incomplete",
                        "failed_at_act": act_number,
                        "error": str(e)
                    })
                return
        
        # Only save complete play summary if all acts were successful
        run_manager.save_artifact(run_id, "play_summary", {
            "title": "Cyberpunk Romeo and Juliet",
            "acts": [{
                "act_number": i + 1,
                "scenes": [{
                    "scene_number": j + 1,
                    "evaluation": scene["evaluation"],
                    "timing_metrics": scene["timing_metrics"]
                } for j, scene in enumerate(all_scenes[i*5:(i+1)*5])]
            } for i in range(3)],
            "timestamp": datetime.now().isoformat(),
            "status": "completed"
        })
        
        # Update final run status only if everything succeeded
        run_manager.update_run_status(run_id, "completed", {
            "end_time": datetime.now().isoformat(),
            "total_scenes": len(all_scenes),
            "completed_acts": list(range(1, 4))
        })
        
        # End the run
        run_manager.end_run("completed")
        
        # Consolidate all scenes into a single file
        logger.info("Consolidating scenes into a single file...")
        try:
            consolidate_scenes(run_id)
            logger.info("Scene consolidation completed successfully")
        except Exception as e:
            logger.error(f"Error consolidating scenes: {str(e)}")
            # Don't raise the error since this is a post-processing step
            # and shouldn't affect the main play generation process
        
    except Exception as e:
        logger.error(f"Fatal error in play generation: {str(e)}")
        if 'run_id' in locals():
            run_manager.save_error(run_id, e, {
                "stage": "play_generation",
                "fatal": True
            })
            run_manager.update_run_status(run_id, "failed", {
                "end_time": datetime.now().isoformat(),
                "error": str(e)
            })
        raise

if __name__ == "__main__":
    main() 