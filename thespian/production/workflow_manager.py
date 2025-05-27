"""
Production Workflow Manager - Orchestrates the complete enhanced production process.
"""

from typing import Dict, Any, List, Optional, Tuple
import time
import json
from datetime import datetime
from dataclasses import dataclass, field

from thespian.llm.collaborative_playwright import CollaborativePlaywright
from thespian.llm.detail_enhancer import SceneDetailEnhancer
from thespian.llm.enhanced_memory import EnhancedTheatricalMemory
from thespian.protocols import (
    InteractionCoordinator,
    FeedbackAggregator,
    ComprehensiveFeedback,
    AgentMessage,
    MessageType,
    Priority
)
from thespian.config.enhanced_prompts import get_enhanced_scene_prompt
import logging

logger = logging.getLogger(__name__)


@dataclass
class WorkflowStage:
    """Represents a stage in the production workflow."""
    name: str
    description: str
    duration: float = 0.0
    status: str = "pending"  # pending, in_progress, completed, failed
    artifacts: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProductionMetrics:
    """Tracks metrics throughout the production process."""
    total_scenes: int = 0
    scenes_completed: int = 0
    total_iterations: int = 0
    agent_contributions: Dict[str, int] = field(default_factory=dict)
    scene_lengths: List[int] = field(default_factory=list)
    workshop_rounds: List[int] = field(default_factory=list)
    quality_scores: List[float] = field(default_factory=list)
    total_duration: float = 0.0
    stage_durations: Dict[str, float] = field(default_factory=dict)


class ProductionWorkflowManager:
    """Manages the complete enhanced theatrical production workflow."""
    
    def __init__(
        self,
        target_scene_length: int = 5000,
        max_workshop_iterations: int = 3,
        enable_all_enhancements: bool = True,
        track_metrics: bool = True
    ):
        """Initialize the workflow manager.
        
        Args:
            target_scene_length: Target character count for each scene
            max_workshop_iterations: Maximum workshop rounds per scene
            enable_all_enhancements: Use all enhancement systems
            track_metrics: Track detailed production metrics
        """
        self.target_scene_length = target_scene_length
        self.max_workshop_iterations = max_workshop_iterations
        self.enable_all_enhancements = enable_all_enhancements
        self.track_metrics = track_metrics
        
        # Initialize components
        self.memory = EnhancedTheatricalMemory()
        self.playwright = CollaborativePlaywright(
            memory=self.memory,
            enable_pre_production=True,
            enable_workshops=True,
            iteration_limit=max_workshop_iterations
        )
        self.detail_enhancer = SceneDetailEnhancer(target_length=target_scene_length)
        self.interaction_coordinator = InteractionCoordinator()
        
        # Workflow stages
        self.stages: List[WorkflowStage] = []
        self.current_stage: Optional[WorkflowStage] = None
        
        # Metrics
        self.metrics = ProductionMetrics()
        
        # Production artifacts
        self.production_artifacts = {
            "story_outline": None,
            "pre_production_notes": None,
            "scenes": [],
            "final_script": None,
            "production_bible": {}
        }
    
    def _initialize_workflow_stages(self, num_acts: int, scenes_per_act: int) -> None:
        """Initialize the workflow stages for a production."""
        self.stages = [
            WorkflowStage(
                name="story_development",
                description="Develop story outline and character profiles"
            ),
            WorkflowStage(
                name="pre_production",
                description="Conduct pre-production meetings with all agents"
            )
        ]
        
        # Add stage for each scene
        for act in range(1, num_acts + 1):
            for scene in range(1, scenes_per_act + 1):
                self.stages.append(WorkflowStage(
                    name=f"act_{act}_scene_{scene}",
                    description=f"Generate and workshop Act {act}, Scene {scene}"
                ))
        
        self.stages.extend([
            WorkflowStage(
                name="integration",
                description="Integrate all scenes into cohesive script"
            ),
            WorkflowStage(
                name="final_review",
                description="Final review and quality assurance"
            )
        ])
    
    def _start_stage(self, stage: WorkflowStage) -> None:
        """Start a workflow stage."""
        stage.status = "in_progress"
        self.current_stage = stage
        logger.info(f"Starting stage: {stage.name} - {stage.description}")
        print(f"\n{'=' * 60}")
        print(f"STAGE: {stage.name.upper()}")
        print(f"Description: {stage.description}")
        print(f"{'=' * 60}\n")
    
    def _complete_stage(self, stage: WorkflowStage, artifacts: Dict[str, Any] = None) -> None:
        """Complete a workflow stage."""
        stage.status = "completed"
        if artifacts:
            stage.artifacts.update(artifacts)
        
        if self.track_metrics:
            stage.metrics["duration"] = stage.duration
            self.metrics.stage_durations[stage.name] = stage.duration
        
        logger.info(f"Completed stage: {stage.name} in {stage.duration:.2f}s")
        print(f"\n✓ Stage '{stage.name}' completed in {stage.duration:.2f} seconds\n")
    
    def generate_enhanced_production(
        self,
        premise: str,
        themes: List[str] = None,
        num_acts: int = 2,
        scenes_per_act: int = 4,
        style: str = "contemporary drama"
    ) -> Dict[str, Any]:
        """Generate a complete theatrical production with all enhancements.
        
        Returns:
            Complete production with enhanced scenes and metrics
        """
        start_time = time.time()
        print("\n🎭 ENHANCED THEATRICAL PRODUCTION WORKFLOW 🎭")
        print(f"\nPremise: {premise}")
        print(f"Themes: {', '.join(themes or [])}")
        print(f"Structure: {num_acts} acts, {scenes_per_act} scenes per act")
        print(f"Target scene length: {self.target_scene_length} characters\n")
        
        # Initialize workflow
        self._initialize_workflow_stages(num_acts, scenes_per_act)
        self.metrics.total_scenes = num_acts * scenes_per_act
        
        try:
            # Stage 1: Story Development
            story_outline = self._execute_story_development(premise, themes, style)
            
            # Stage 2: Pre-Production
            pre_production_notes = self._execute_pre_production(story_outline)
            
            # Stage 3-N: Scene Generation
            scenes = self._execute_scene_generation(story_outline, num_acts, scenes_per_act)
            
            # Stage N+1: Integration
            integrated_script = self._execute_integration(scenes)
            
            # Stage N+2: Final Review
            final_production = self._execute_final_review(integrated_script)
            
            # Calculate final metrics
            self.metrics.total_duration = time.time() - start_time
            
            # Prepare final output
            result = {
                "status": "completed",
                "production": final_production,
                "metrics": self._get_metrics_summary(),
                "artifacts": self.production_artifacts,
                "workflow_stages": [
                    {
                        "name": stage.name,
                        "status": stage.status,
                        "duration": stage.duration,
                        "metrics": stage.metrics
                    }
                    for stage in self.stages
                ]
            }
            
            print(f"\n{'=' * 60}")
            print("🎭 PRODUCTION COMPLETE! 🎭")
            print(f"{'=' * 60}")
            self._print_production_summary(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Production workflow failed: {e}")
            if self.current_stage:
                self.current_stage.status = "failed"
            raise
    
    def _execute_story_development(self, premise: str, themes: List[str], style: str) -> Dict[str, Any]:
        """Execute story development stage."""
        stage = next(s for s in self.stages if s.name == "story_development")
        self._start_stage(stage)
        stage_start = time.time()
        
        # Create story outline with enhanced playwright
        print("📝 Developing story outline...")
        story_outline = self.playwright.create_story_outline(premise, themes)
        
        # Store in artifacts
        self.production_artifacts["story_outline"] = story_outline
        
        # Register agents for interaction
        self._register_production_agents(story_outline.get('characters', []))
        
        stage.duration = time.time() - stage_start
        self._complete_stage(stage, {"story_outline": story_outline})
        
        return story_outline
    
    def _execute_pre_production(self, story_outline: Dict[str, Any]) -> Dict[str, Any]:
        """Execute pre-production meetings."""
        stage = next(s for s in self.stages if s.name == "pre_production")
        self._start_stage(stage)
        stage_start = time.time()
        
        print("🎬 Conducting pre-production meetings...")
        
        # Conduct pre-production meeting if enabled
        if self.playwright.enable_pre_production:
            pre_production_notes = self.playwright.conduct_pre_production_meeting(
                self.production_artifacts["story_outline"].get("premise", ""),
                story_outline.get('characters', []),
                story_outline.get('themes', [])
            )
            self.production_artifacts["pre_production_notes"] = pre_production_notes
        else:
            pre_production_notes = {"skipped": True}
        
        stage.duration = time.time() - stage_start
        self._complete_stage(stage, {"pre_production_notes": pre_production_notes})
        
        return pre_production_notes
    
    def _execute_scene_generation(self, story_outline: Dict[str, Any], num_acts: int, scenes_per_act: int) -> List[Dict[str, Any]]:
        """Execute scene generation for all scenes."""
        scenes = []
        
        for act_num in range(1, num_acts + 1):
            act_scenes = []
            
            for scene_num in range(1, scenes_per_act + 1):
                stage_name = f"act_{act_num}_scene_{scene_num}"
                stage = next(s for s in self.stages if s.name == stage_name)
                self._start_stage(stage)
                stage_start = time.time()
                
                print(f"\n📄 Generating Act {act_num}, Scene {scene_num}...")
                
                # Get scene guide from outline
                scene_guide = self._get_scene_guide(story_outline, act_num, scene_num)
                
                # Generate scene with collaborative playwright
                scene = self._generate_enhanced_scene(
                    act_num, scene_num, scene_guide, scenes
                )
                
                # Track metrics
                if self.track_metrics:
                    self.metrics.scenes_completed += 1
                    self.metrics.scene_lengths.append(len(scene.get('content', '')))
                    self.metrics.workshop_rounds.append(scene.get('workshop_iterations', 0))
                    if 'quality_score' in scene:
                        self.metrics.quality_scores.append(scene['quality_score'])
                
                act_scenes.append(scene)
                scenes.append(scene)
                
                stage.duration = time.time() - stage_start
                self._complete_stage(stage, {"scene": scene})
            
            # Store act
            self.production_artifacts[f"act_{act_num}_scenes"] = act_scenes
        
        self.production_artifacts["scenes"] = scenes
        return scenes
    
    def _generate_enhanced_scene(
        self,
        act_number: int,
        scene_number: int,
        scene_guide: Dict[str, Any],
        previous_scenes: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate a single enhanced scene with all systems."""
        
        # Step 1: Generate base scene with collaborative playwright
        print("  1️⃣ Collaborative generation...")
        scene = self.playwright.generate_scene(
            act_number=act_number,
            scene_number=scene_number,
            scene_guide=scene_guide,
            previous_scenes=previous_scenes,
            word_count=self.target_scene_length // 5  # Approximate words
        )
        
        # Step 2: Apply detail enhancement if needed
        current_length = len(scene.get('content', ''))
        if current_length < self.target_scene_length:
            print(f"  2️⃣ Enhancing detail ({current_length} → {self.target_scene_length} chars)...")
            enhanced_content = self.detail_enhancer.enhance_scene(
                scene['content'],
                self.detail_enhancer.analyze_scene(scene['content'])
            )
            scene['content'] = enhanced_content
            scene['enhancement_applied'] = True
            scene['length_before_enhancement'] = current_length
            scene['length_after_enhancement'] = len(enhanced_content)
        
        # Step 3: Agent interaction and feedback
        if self.enable_all_enhancements:
            print("  3️⃣ Collecting agent feedback...")
            feedback_thread = self._conduct_scene_feedback_session(scene)
            scene['feedback_thread'] = feedback_thread
            
            # Apply high-priority feedback
            refined_content = self._apply_feedback_refinements(scene['content'], feedback_thread)
            if refined_content != scene['content']:
                scene['content'] = refined_content
                scene['feedback_applied'] = True
        
        # Step 4: Final length check and quality metrics
        final_length = len(scene['content'])
        scene['final_length'] = final_length
        scene['meets_target'] = final_length >= self.target_scene_length
        
        print(f"  ✅ Scene complete: {final_length} characters")
        
        return scene
    
    def _conduct_scene_feedback_session(self, scene: Dict[str, Any]) -> Dict[str, Any]:
        """Conduct feedback session with all agents."""
        thread = self.interaction_coordinator.create_thread(
            topic=f"Feedback for {scene.get('metadata', {}).get('scene_id', 'scene')}",
            initial_participants=list(self.interaction_coordinator.agents.keys())
        )
        
        # Each agent provides feedback
        feedback_messages = []
        for agent_name, agent in self.interaction_coordinator.agents.items():
            if hasattr(agent, 'provide_feedback'):
                feedback = agent.provide_feedback(scene['content'])
                msg = AgentMessage(
                    sender=agent_name,
                    recipient="all",
                    message_type=MessageType.FEEDBACK,
                    priority=Priority.MEDIUM,
                    content=feedback,
                    context={"thread_id": thread.id}
                )
                self.interaction_coordinator.route_message(msg)
                feedback_messages.append(msg)
        
        # Resolve any conflicts
        resolution = self.interaction_coordinator.resolve_conflicts(thread.id)
        
        return {
            "thread_id": thread.id,
            "feedback_count": len(feedback_messages),
            "resolution": resolution,
            "summary": self.interaction_coordinator.get_thread_summary(thread.id)
        }
    
    def _apply_feedback_refinements(self, content: str, feedback_thread: Dict[str, Any]) -> str:
        """Apply high-priority feedback to refine content."""
        # In a real implementation, this would use LLM to integrate feedback
        # For now, return content as-is
        return content
    
    def _execute_integration(self, scenes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Integrate all scenes into cohesive script."""
        stage = next(s for s in self.stages if s.name == "integration")
        self._start_stage(stage)
        stage_start = time.time()
        
        print("🔧 Integrating scenes into complete script...")
        
        # Combine all scene content
        full_script = []
        
        for i, scene in enumerate(scenes):
            act = (i // 4) + 1  # Assuming 4 scenes per act
            scene_num = (i % 4) + 1
            
            full_script.append(f"\n{'=' * 60}")
            full_script.append(f"ACT {act}, SCENE {scene_num}")
            full_script.append(f"{'=' * 60}\n")
            full_script.append(scene['content'])
        
        integrated_script = {
            "content": '\n'.join(full_script),
            "total_length": sum(len(s['content']) for s in scenes),
            "scene_count": len(scenes),
            "integration_notes": "Scenes combined with act/scene markers"
        }
        
        self.production_artifacts["final_script"] = integrated_script
        
        stage.duration = time.time() - stage_start
        self._complete_stage(stage, {"integrated_script": integrated_script})
        
        return integrated_script
    
    def _execute_final_review(self, integrated_script: Dict[str, Any]) -> Dict[str, Any]:
        """Execute final review and quality assurance."""
        stage = next(s for s in self.stages if s.name == "final_review")
        self._start_stage(stage)
        stage_start = time.time()
        
        print("🎭 Conducting final review...")
        
        # Calculate quality metrics
        quality_report = {
            "total_length": integrated_script["total_length"],
            "average_scene_length": integrated_script["total_length"] / integrated_script["scene_count"],
            "meets_length_targets": all(
                length >= self.target_scene_length 
                for length in self.metrics.scene_lengths
            ),
            "workshop_effectiveness": {
                "total_workshops": sum(self.metrics.workshop_rounds),
                "average_iterations": sum(self.metrics.workshop_rounds) / len(self.metrics.workshop_rounds) if self.metrics.workshop_rounds else 0
            },
            "agent_participation": self.metrics.agent_contributions,
            "quality_scores": {
                "average": sum(self.metrics.quality_scores) / len(self.metrics.quality_scores) if self.metrics.quality_scores else 0,
                "min": min(self.metrics.quality_scores) if self.metrics.quality_scores else 0,
                "max": max(self.metrics.quality_scores) if self.metrics.quality_scores else 0
            }
        }
        
        final_production = {
            "script": integrated_script["content"],
            "metadata": {
                "title": self.production_artifacts["story_outline"].get("title", "Untitled"),
                "premise": self.production_artifacts["story_outline"].get("premise", ""),
                "themes": self.production_artifacts["story_outline"].get("themes", []),
                "characters": self.production_artifacts["story_outline"].get("characters", []),
                "generation_date": datetime.now().isoformat(),
                "workflow_version": "1.0"
            },
            "quality_report": quality_report,
            "production_notes": self.memory.production_bible
        }
        
        stage.duration = time.time() - stage_start
        self._complete_stage(stage, {"final_production": final_production})
        
        return final_production
    
    def _register_production_agents(self, characters: List[Dict[str, Any]]) -> None:
        """Register all agents with the interaction coordinator."""
        # Register core agents
        self.interaction_coordinator.register_agent("Director", self.playwright.director)
        self.interaction_coordinator.register_agent("Designer", self.playwright.designer)
        self.interaction_coordinator.register_agent("StageManager", self.playwright.stage_manager)
        
        # Register character actors
        for char in characters:
            if isinstance(char, dict) and 'name' in char:
                char_name = char['name']
                if char_name in self.playwright.actors:
                    self.interaction_coordinator.register_agent(
                        f"Actor_{char_name}",
                        self.playwright.actors[char_name]
                    )
    
    def _get_scene_guide(self, story_outline: Dict[str, Any], act_num: int, scene_num: int) -> Dict[str, Any]:
        """Get scene guide from story outline."""
        acts = story_outline.get('acts', [])
        if act_num <= len(acts):
            scenes = acts[act_num - 1].get('scenes', [])
            if scene_num <= len(scenes):
                return scenes[scene_num - 1]
        
        # Fallback scene guide
        return {
            "description": f"Act {act_num}, Scene {scene_num}",
            "location": "Unspecified",
            "characters": [],
            "purpose": "Advance the story"
        }
    
    def _get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of production metrics."""
        return {
            "production_stats": {
                "total_scenes": self.metrics.total_scenes,
                "scenes_completed": self.metrics.scenes_completed,
                "completion_rate": f"{(self.metrics.scenes_completed / self.metrics.total_scenes * 100):.1f}%"
            },
            "length_metrics": {
                "target_length": self.target_scene_length,
                "average_length": sum(self.metrics.scene_lengths) / len(self.metrics.scene_lengths) if self.metrics.scene_lengths else 0,
                "min_length": min(self.metrics.scene_lengths) if self.metrics.scene_lengths else 0,
                "max_length": max(self.metrics.scene_lengths) if self.metrics.scene_lengths else 0,
                "total_length": sum(self.metrics.scene_lengths)
            },
            "collaboration_metrics": {
                "total_iterations": self.metrics.total_iterations,
                "average_workshop_rounds": sum(self.metrics.workshop_rounds) / len(self.metrics.workshop_rounds) if self.metrics.workshop_rounds else 0,
                "agent_contributions": self.metrics.agent_contributions
            },
            "timing_metrics": {
                "total_duration": f"{self.metrics.total_duration:.2f} seconds",
                "average_scene_time": f"{self.metrics.total_duration / self.metrics.scenes_completed:.2f} seconds" if self.metrics.scenes_completed else "N/A",
                "stage_durations": self.metrics.stage_durations
            }
        }
    
    def _print_production_summary(self, result: Dict[str, Any]) -> None:
        """Print a summary of the production."""
        metrics = result["metrics"]
        
        print("\n📊 PRODUCTION SUMMARY")
        print("=" * 50)
        
        print(f"\n📝 Script Statistics:")
        print(f"  • Total length: {metrics['length_metrics']['total_length']:,} characters")
        print(f"  • Average scene: {metrics['length_metrics']['average_length']:,.0f} characters")
        print(f"  • Target achievement: {metrics['length_metrics']['average_length'] / self.target_scene_length * 100:.1f}%")
        
        print(f"\n🎭 Collaboration Metrics:")
        print(f"  • Workshop rounds: {metrics['collaboration_metrics']['average_workshop_rounds']:.1f} per scene")
        print(f"  • Agent types involved: {len(metrics['collaboration_metrics']['agent_contributions'])}")
        
        print(f"\n⏱️  Performance:")
        print(f"  • Total time: {metrics['timing_metrics']['total_duration']}")
        print(f"  • Per scene: {metrics['timing_metrics']['average_scene_time']}")
        
        print(f"\n✅ Quality Indicators:")
        if result['production']['quality_report']['meets_length_targets']:
            print(f"  • All scenes meet target length ✓")
        else:
            print(f"  • Some scenes below target length ✗")
        
        print("\n" + "=" * 50)