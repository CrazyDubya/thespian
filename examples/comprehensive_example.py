"""
Comprehensive Example of the Consolidated Playwright Framework

This example demonstrates the full capabilities of the consolidated playwright
with all available features enabled, including:
- Memory enhancement
- Iterative refinement
- Collaborative mode with multiple playwright agents
- Character tracking
- Narrative structure awareness
- Advanced scene planning with theatrical advisors

The example produces a three-act play with 5 scenes per act, showing the
entire production pipeline from initial setup to final output.
"""

import os
import time
import json
import uuid
import logging
from datetime import datetime
from pathlib import Path

from thespian.llm import LLMManager
from thespian.llm.consolidated_playwright import (
    Playwright,
    SceneRequirements,
    PlaywrightCapability,
    create_playwright
)
from thespian.llm.theatrical_memory import (
    TheatricalMemory,
    CharacterProfile,
    StoryOutline
)
from thespian.llm.enhanced_memory import EnhancedTheatricalMemory
from thespian.llm.theatrical_advisors import AdvisorManager, AdvisorType, get_advisor
from thespian.llm.quality_control import TheatricalQualityControl
from thespian.llm.run_manager import RunManager
from thespian.processors.scene_processor import SceneProcessor
from thespian.processors.act_processor import ActProcessor

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProductionManager:
    """
    Manages the entire theatrical production process.
    
    This class demonstrates integration of all consolidated playwright capabilities,
    coordinating the generation of a complete three-act play while showcasing
    advanced features like memory enhancement, collaborative scene generation,
    and advisor-guided refinement.
    """
    
    def __init__(self):
        """Initialize the production manager with all required components."""
        # Core components
        self.llm_manager = LLMManager()
        
        # Enhanced memory with character tracking
        self.memory = EnhancedTheatricalMemory(db_path=None)
        
        # Advisor system with all advisor types
        self.advisor_manager = AdvisorManager(
            llm_manager=self.llm_manager,
            memory=self.memory
        )
        
        # Quality control for scene evaluation
        self.quality_control = TheatricalQualityControl()
        
        # Run manager for persistent storage and tracking
        self.run_manager = RunManager()
        
        # Main playwright with all capabilities enabled
        playwright_kwargs = {
            "name": "Primary Playwright",
            "llm_manager": self.llm_manager,
            "memory": self.memory,
            "capabilities": [
                PlaywrightCapability.BASIC,
                PlaywrightCapability.ITERATIVE_REFINEMENT,
                PlaywrightCapability.MEMORY_ENHANCEMENT,
                PlaywrightCapability.CHARACTER_TRACKING,
                PlaywrightCapability.NARRATIVE_STRUCTURE,
                PlaywrightCapability.COLLABORATIVE
            ],
            "quality_control": self.quality_control,
            # Configure enhanced behavior
            "max_iterations": 3,
            "refinement_quality_threshold": 0.85,
            "memory_integration_level": 3,
            "model_type": "ollama"
        }
        
        # Don't pass advisor_manager as both kwarg and through the factory function
        if hasattr(self, 'advisor_manager') and self.advisor_manager:
            playwright_kwargs["advisor_manager"] = self.advisor_manager
        
        self.main_playwright = create_playwright(**playwright_kwargs)
        
        # Secondary playwrights for collaborative mode, each with specialized focus
        # Dialogue specialist
        dialogue_kwargs = {
            "name": "Dialogue Specialist",
            "llm_manager": self.llm_manager,
            "memory": self.memory,
            "capabilities": [
                PlaywrightCapability.BASIC,
                PlaywrightCapability.COLLABORATIVE
            ],
            "quality_control": self.quality_control,
            "model_type": "ollama"
        }
        # Create a dedicated advisor manager instead of using the shared one
        dialogue_advisor_manager = AdvisorManager(
            llm_manager=self.llm_manager,
            memory=self.memory
        )
        dialogue_kwargs["advisor_manager"] = dialogue_advisor_manager
        self.dialogue_playwright = create_playwright(**dialogue_kwargs)
        
        # Character specialist
        character_kwargs = {
            "name": "Character Specialist",
            "llm_manager": self.llm_manager,
            "memory": self.memory,
            "capabilities": [
                PlaywrightCapability.BASIC,
                PlaywrightCapability.CHARACTER_TRACKING,
                PlaywrightCapability.COLLABORATIVE
            ],
            "quality_control": self.quality_control,
            "model_type": "ollama"
        }
        # Create a dedicated advisor manager instead of using the shared one
        character_advisor_manager = AdvisorManager(
            llm_manager=self.llm_manager,
            memory=self.memory
        )
        character_kwargs["advisor_manager"] = character_advisor_manager
        self.character_playwright = create_playwright(**character_kwargs)
        
        # Initialize run ID for tracking
        self.run_id = str(uuid.uuid4())
        
        # These will be set during setup
        self.story_outline = None
        self.character_profiles = {}
        self.base_requirements = {}
        self.output_dir = Path("output") / self.run_id
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def setup_production(self, title, theme, setting, period, style):
        """
        Set up the production with initial parameters.
        
        Args:
            title: The title of the production
            theme: Central theme of the story
            setting: The setting of the production
            period: Time period of the production
            style: Theatrical style
        """
        logger.info(f"Setting up production: {title}")
        
        # Base requirements for all scenes
        self.base_requirements = {
            "setting": setting,
            "style": style,
            "period": period,
            "target_audience": "Adult",
            "lighting": "Varied, scene-dependent",
            "sound": "Original score with period-appropriate motifs",
            "props": ["Various, scene-dependent"],
        }
        
        # Set up the run tracking
        self.run_manager.start_run(self.run_id)
        self.run_manager.save_artifact(self.run_id, "metadata", {
            "title": title,
            "theme": theme,
            "requirements": self.base_requirements,
            "start_time": datetime.now().isoformat(),
            "capabilities": [cap.value for cap in self.main_playwright.enabled_capabilities]
        })
        
        # Create story outline
        self.story_outline = self.main_playwright.create_story_outline(
            theme=theme,
            requirements=self.base_requirements
        )
        
        # Save outline to run artifacts - convert to dict if needed
        if hasattr(self.story_outline, "dict"):
            outline_data = self.story_outline.dict()
        else:
            # Manual conversion to dict for non-Pydantic StoryOutline
            outline_data = {
                "title": self.story_outline.title,
                "acts": self.story_outline.acts,
                "planning_discussions": getattr(self.story_outline, "planning_discussions", []),
                "themes": getattr(self.story_outline, "themes", [])
            }
            
        self.run_manager.save_artifact(self.run_id, "story_outline", outline_data)
        
        # Set story outline for all playwrights
        self.main_playwright.story_outline = self.story_outline
        self.dialogue_playwright.story_outline = self.story_outline
        self.character_playwright.story_outline = self.story_outline
        
        # Create character profiles from the outline
        self._setup_character_profiles()
        
        logger.info(f"Production setup complete: {title}")
        
    def _setup_character_profiles(self):
        """Create detailed character profiles from the story outline."""
        # Extract characters from the outline
        characters = []
        if hasattr(self.story_outline, "characters"):
            characters = self.story_outline.characters
        
        if not characters:
            # Generate default characters if none in outline
            characters = [
                {"name": "Protagonist", "description": "The main character"},
                {"name": "Antagonist", "description": "The opposing force"},
                {"name": "Supporting Character", "description": "A key ally"},
                {"name": "Secondary Character", "description": "Another important character"}
            ]
            
        # Create detailed profiles for each character
        for character in characters:
            char_name = character.get("name", character) if isinstance(character, dict) else character
            char_desc = character.get("description", "") if isinstance(character, dict) else ""
            
            # Generate more detailed background if description is minimal
            background = char_desc
            if len(background) < 100:
                prompt = f"""Create a detailed background for a character named {char_name} in a play.
                The play is titled "{self.story_outline.title}" and has themes of {', '.join(self.story_outline.themes) if hasattr(self.story_outline, 'themes') else 'various human experiences'}.
                Current description: {char_desc}
                
                Provide a rich paragraph of 150-200 words with:
                - Personality traits
                - Personal history
                - Motivations and goals
                - Key relationships
                - Internal conflicts"""
                
                response = self.llm_manager.get_llm("ollama").invoke(prompt)
                background = response.content
            
            # Create profile and store in memory
            profile = CharacterProfile(
                id=char_name.lower().replace(" ", "_"),
                name=char_name,
                description=char_desc,
                background=background,
                relationships={},
                goals=[],
                conflicts=[],
                motivations=[],
                development_arc=[]
            )
            
            self.memory.update_character_profile(profile.id, profile)
            self.character_profiles[profile.id] = profile
            
        logger.info(f"Created {len(self.character_profiles)} character profiles")
        
    def generate_complete_play(self):
        """Generate a complete three-act play with all scenes."""
        logger.info("Starting generation of complete play")
        
        # Track timing for the entire production
        start_time = time.time()
        all_scenes = []
        
        try:
            # Generate each act sequentially
            for act_number in range(1, 4):
                logger.info(f"Generating Act {act_number}")
                
                # Update run status
                self.run_manager.update_run_status(self.run_id, "in_progress", {
                    "current_act": act_number,
                    "current_scene": None
                })
                
                # Plan the act with advisors
                act_plan = self.main_playwright.plan_act(act_number)
                self.run_manager.save_act_plan(self.run_id, act_number, act_plan)
                
                # Set act status to in_progress
                self.story_outline.update_act_status(act_number, "in_progress")
                
                # Generate scenes for this act
                act_scenes = self.generate_act_scenes(act_number)
                all_scenes.extend(act_scenes)
                
                # Create act summary
                self.run_manager.save_artifact(self.run_id, f"act{act_number}_summary", {
                    "act_number": act_number,
                    "plan": act_plan["committed_outline"],
                    "scenes": [{
                        "scene_number": i + 1,
                        "evaluation": scene["evaluation"],
                        "timing_metrics": scene["timing_metrics"]
                    } for i, scene in enumerate(act_scenes)],
                    "character_development": act_plan.get("character_development", ""),
                    "thematic_elements": act_plan.get("thematic_elements", ""),
                    "timestamp": datetime.now().isoformat(),
                    "status": "completed"
                })
                
                # Update act status
                self.story_outline.update_act_status(act_number, "completed")
                
                # Update run status
                self.run_manager.update_run_status(self.run_id, "act_completed", {
                    "completed_act": act_number,
                    "current_act": None,
                    "current_scene": None
                })
                
            # Generate play summary
            self.run_manager.save_artifact(self.run_id, "play_summary", {
                "title": self.story_outline.title,
                "acts": [{
                    "act_number": i + 1,
                    "scenes": [{
                        "scene_number": j + 1,
                        "evaluation": scene["evaluation"],
                        "timing_metrics": scene["timing_metrics"]
                    } for j, scene in enumerate(all_scenes[i*5:(i+1)*5])]
                } for i in range(3)],
                "timestamp": datetime.now().isoformat(),
                "status": "completed",
                "total_time": time.time() - start_time
            })
            
            # Update final run status
            self.run_manager.update_run_status(self.run_id, "completed", {
                "end_time": datetime.now().isoformat(),
                "total_scenes": len(all_scenes),
                "completed_acts": list(range(1, 4))
            })
            
            # Save the consolidated play text
            self.save_consolidated_play(all_scenes)
            
            return all_scenes
            
        except Exception as e:
            logger.error(f"Error generating play: {str(e)}")
            
            # Update run status to failed
            self.run_manager.update_run_status(self.run_id, "failed", {
                "end_time": datetime.now().isoformat(),
                "error": str(e)
            })
            
            # Save any scenes generated so far
            if all_scenes:
                self.save_consolidated_play(all_scenes, partial=True)
            
            raise
            
    def generate_act_scenes(self, act_number):
        """
        Generate all scenes for a single act, using different generation approaches.
        
        For demonstration purposes, this function uses different playwright capabilities:
        - Scene 1: Basic generation with the main playwright
        - Scene 2: Collaborative generation between main and dialogue playwrights
        - Scene 3: Character-focused generation using character tracking capabilities
        - Scene 4: Memory-enhanced generation using previous scene context
        - Scene 5: Iterative refinement with multiple revisions
        
        Args:
            act_number: The act number to generate
            
        Returns:
            List of generated scenes with metadata
        """
        scenes = []
        scene_characters = self._get_characters_for_act(act_number)
        
        for scene_number in range(1, 6):
            logger.info(f"Generating Act {act_number}, Scene {scene_number}")
            
            # Update run status
            self.run_manager.update_run_status(self.run_id, "in_progress", {
                "current_act": act_number,
                "current_scene": scene_number
            })
            
            # Base requirements for all scenes
            scene_requirements = SceneRequirements(
                **self.base_requirements,
                characters=scene_characters,
                act_number=act_number,
                scene_number=scene_number
            )
            
            # Get previous scene for context if available
            previous_scene = scenes[-1]["scene"] if scenes else None
            
            try:
                # Different generation approach for each scene number
                if scene_number == 1:
                    # Scene 1: Basic generation
                    result = self.main_playwright.generate_scene(
                        requirements=scene_requirements,
                        previous_scene=previous_scene,
                        progress_callback=lambda data: logger.info(f"Progress: {data}"),
                        generation_type="basic"
                    )
                    result["generation_type"] = "basic"
                    
                elif scene_number == 2:
                    # Scene 2: Collaborative generation
                    result = self.main_playwright.collaborate_on_scene(
                        other_playwright=self.dialogue_playwright,
                        requirements=scene_requirements,
                        progress_callback=lambda data: logger.info(f"Progress: {data}")
                    )
                    result["generation_type"] = "collaborative"
                    
                elif scene_number == 3:
                    # Scene 3: Character-focused generation
                    focus_character_id = list(self.character_profiles.keys())[0]
                    character_development = {
                        "aspect": "emotional",
                        "moment_type": "revelation",
                        "reveal_aspect": "motivation",
                        "conflict_type": "internal conflict",
                        "emotional_journey": "From doubt to determination"
                    }
                    
                    result = self.main_playwright.create_scene_with_character_focus(
                        requirements=scene_requirements,
                        focus_character=focus_character_id,
                        character_development=character_development,
                        progress_callback=lambda data: logger.info(f"Progress: {data}")
                    )
                    result["generation_type"] = "character_focused"
                    
                elif scene_number == 4:
                    # Scene 4: Memory-enhanced generation
                    # The memory enhancement is automatically used when that capability is enabled
                    result = self.main_playwright.generate_scene(
                        requirements=scene_requirements,
                        previous_scene=previous_scene,
                        progress_callback=lambda data: logger.info(f"Progress: {data}"),
                        generation_type="memory_enhanced"
                    )
                    result["generation_type"] = "memory_enhanced"
                    
                else:  # scene_number == 5
                    # Scene 5: Iterative refinement with more iterations
                    # Temporarily increase max iterations
                    original_max = self.main_playwright.refinement_max_iterations
                    self.main_playwright.refinement_max_iterations = 5
                    
                    result = self.main_playwright.generate_scene(
                        requirements=scene_requirements,
                        previous_scene=previous_scene,
                        progress_callback=lambda data: logger.info(f"Progress: {data}"),
                        generation_type="iterative_refinement"
                    )
                    
                    # Restore original max
                    self.main_playwright.refinement_max_iterations = original_max
                    result["generation_type"] = "iterative_refinement"
                
                # Save scene to run manager
                self.run_manager.save_scene(self.run_id, act_number, scene_number, {
                    "scene": result["scene"],
                    "evaluation": result["evaluation"],
                    "timing_metrics": result["timing_metrics"],
                    "iterations": result["iterations"],
                    "iteration_metrics": result.get("iteration_metrics", []),
                    "generation_type": result["generation_type"],
                    "scene_number": scene_number,
                    "act_number": act_number,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Save scene to local file for easier access
                scene_path = self.output_dir / f"act{act_number}_scene{scene_number}.txt"
                with open(scene_path, "w") as f:
                    f.write(result["scene"])
                
                # Add scene to list
                scenes.append(result)
                
            except Exception as e:
                logger.error(f"Error generating Act {act_number}, Scene {scene_number}: {str(e)}")
                self.run_manager.save_error(self.run_id, e, {
                    "act_number": act_number,
                    "scene_number": scene_number,
                    "stage": "generation"
                })
                raise
                
        return scenes
    
    def _get_characters_for_act(self, act_number):
        """Get characters for a specific act based on outline and existing profiles."""
        # Get all character names from profiles
        all_character_names = [profile.name for profile in self.character_profiles.values()]
        
        if not all_character_names:
            return ["Character 1", "Character 2", "Character 3"]
        
        # For this example, we'll use different character subsets for each act
        if act_number == 1:
            # Act 1: Introduce all main characters
            return all_character_names[:min(5, len(all_character_names))]
        elif act_number == 2:
            # Act 2: Focus on main conflict characters
            return all_character_names[:min(4, len(all_character_names))]
        else:  # act_number == 3
            # Act 3: Resolution with most characters
            return all_character_names[:min(6, len(all_character_names))]
    
    def save_consolidated_play(self, scenes, partial=False):
        """Save all scenes to a consolidated text file."""
        try:
            # Create consolidated text
            scenes_by_act = {}
            for i, scene in enumerate(scenes):
                act_number = (i // 5) + 1
                scene_number = (i % 5) + 1
                
                if act_number not in scenes_by_act:
                    scenes_by_act[act_number] = {}
                    
                scenes_by_act[act_number][scene_number] = scene["scene"]
            
            # Create output text
            output_text = f"# {self.story_outline.title}\n\n"
            
            for act_num in sorted(scenes_by_act.keys()):
                act_desc = ""
                for act in self.story_outline.acts:
                    if act["act_number"] == act_num:
                        act_desc = act.get("description", "")
                        break
                
                output_text += f"## Act {act_num}: {act_desc}\n\n"
                
                for scene_num in sorted(scenes_by_act[act_num].keys()):
                    output_text += f"### Scene {scene_num}\n\n"
                    output_text += scenes_by_act[act_num][scene_num]
                    output_text += "\n\n"
            
            # Save to file
            filename = "consolidated_play.txt"
            if partial:
                filename = "partial_" + filename
                
            output_path = self.output_dir / filename
            with open(output_path, "w") as f:
                f.write(output_text)
                
            logger.info(f"Saved consolidated play to {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error saving consolidated play: {str(e)}")
            return None
    
    def get_memory_statistics(self):
        """Get statistics about the memory usage during generation."""
        if not isinstance(self.memory, EnhancedTheatricalMemory):
            return {"error": "Enhanced memory not enabled"}
        
        try:
            character_stats = {}
            for char_id, profile in self.memory.character_profiles.items():
                character_stats[profile.name] = {
                    "development_points": len(profile.development_arc),
                    "relationships": len(profile.relationships),
                    "emotions_tracked": len(self.memory.get_character_emotions(char_id))
                }
            
            return {
                "characters_tracked": len(self.memory.character_profiles),
                "narrative_elements_tracked": len(self.memory.get_narrative_elements()),
                "scenes_analyzed": len(self.memory.get_scene_ids()),
                "character_details": character_stats
            }
        except Exception as e:
            logger.error(f"Error getting memory statistics: {str(e)}")
            return {"error": str(e)}
    
    def generate_production_report(self):
        """Generate a comprehensive report about the production process."""
        if not self.run_id:
            return {"error": "No production run found"}
        
        try:
            # Get run metadata
            run_status = self.run_manager.get_run_status(self.run_id)
            
            # Get memory statistics
            memory_stats = self.get_memory_statistics()
            
            # Get advisor statistics
            advisor_stats = {
                advisor_name: {
                    "type": advisor.expertise,
                    "analyses_performed": 0  # In a real implementation, track this during generation
                }
                for advisor_name, advisor in self.advisor_manager.advisors.items()
            }
            
            # Generate the report
            report = {
                "title": self.story_outline.title,
                "run_id": self.run_id,
                "status": run_status.get("status", "unknown"),
                "start_time": run_status.get("start_time", "unknown"),
                "end_time": run_status.get("end_time"),
                "generation_statistics": {
                    "acts_completed": len([act for act in self.story_outline.acts if act["status"] == "completed"]),
                    "total_scenes": len(self.main_playwright.previous_scenes),
                    "playwright_capabilities": [cap.value for cap in self.main_playwright.enabled_capabilities],
                    "generation_types_used": ["basic", "collaborative", "character_focused", "memory_enhanced", "iterative_refinement"]
                },
                "memory_statistics": memory_stats,
                "advisor_statistics": advisor_stats,
                "timestamp": datetime.now().isoformat()
            }
            
            # Save to run artifacts
            self.run_manager.save_artifact(self.run_id, "production_report", report)
            
            # Save to local file
            report_path = self.output_dir / "production_report.json"
            with open(report_path, "w") as f:
                json.dump(report, f, indent=2)
                
            logger.info(f"Saved production report to {report_path}")
            return report
            
        except Exception as e:
            logger.error(f"Error generating production report: {str(e)}")
            return {"error": str(e)}


def main():
    """
    Run the comprehensive example.
    """
    try:
        logger.info("Starting comprehensive example")
        
        # Create production manager
        manager = ProductionManager()
        
        # Set up the production
        manager.setup_production(
            title="The Quantum Soliloquy",
            theme="The intersection of technology and human consciousness",
            setting="Near-future world where quantum computing enables consciousness transfers",
            period="2050s",
            style="Science fiction drama with philosophical elements"
        )
        
        # Generate the complete play
        scenes = manager.generate_complete_play()
        
        # Generate production report
        report = manager.generate_production_report()
        
        logger.info(f"Comprehensive example completed. Generated {len(scenes)} scenes.")
        logger.info(f"Output stored in {manager.output_dir}")
        
    except Exception as e:
        logger.error(f"Error in comprehensive example: {str(e)}")
        raise


if __name__ == "__main__":
    main()