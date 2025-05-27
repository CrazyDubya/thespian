"""
Production metrics tracking system for detailed performance analysis.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json
import statistics


@dataclass
class SceneMetrics:
    """Metrics for a single scene."""
    scene_id: str
    act_number: int
    scene_number: int
    
    # Length metrics
    initial_length: int = 0
    workshop_length: int = 0
    enhanced_length: int = 0
    final_length: int = 0
    
    # Time metrics
    generation_time: float = 0.0
    workshop_time: float = 0.0
    enhancement_time: float = 0.0
    total_time: float = 0.0
    
    # Collaboration metrics
    workshop_iterations: int = 0
    agent_feedback_count: int = 0
    feedback_applied_count: int = 0
    conflicts_resolved: int = 0
    
    # Quality metrics
    dialogue_ratio: float = 0.0
    technical_cue_count: int = 0
    character_consistency_score: float = 0.0
    atmosphere_richness_score: float = 0.0
    overall_quality_score: float = 0.0
    
    # Agent contributions
    agent_contributions: Dict[str, int] = field(default_factory=dict)


@dataclass
class AgentMetrics:
    """Metrics for a single agent's contributions."""
    agent_name: str
    agent_type: str
    
    # Activity metrics
    messages_sent: int = 0
    feedback_provided: int = 0
    suggestions_made: int = 0
    conflicts_raised: int = 0
    
    # Impact metrics
    suggestions_accepted: int = 0
    influence_score: float = 0.0
    collaboration_score: float = 0.0
    
    # Time metrics
    total_active_time: float = 0.0
    average_response_time: float = 0.0


class ProductionMetricsTracker:
    """Comprehensive metrics tracking for theatrical productions."""
    
    def __init__(self):
        """Initialize the metrics tracker."""
        self.production_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.start_time = None
        self.end_time = None
        
        # Scene metrics
        self.scene_metrics: Dict[str, SceneMetrics] = {}
        
        # Agent metrics
        self.agent_metrics: Dict[str, AgentMetrics] = {}
        
        # Overall production metrics
        self.production_summary = {
            "total_scenes": 0,
            "completed_scenes": 0,
            "failed_scenes": 0,
            "total_length": 0,
            "total_workshops": 0,
            "total_enhancements": 0
        }
        
        # Timeline tracking
        self.timeline_events: List[Dict[str, Any]] = []
    
    def start_production(self, premise: str, num_acts: int, scenes_per_act: int) -> None:
        """Mark the start of production."""
        self.start_time = datetime.now()
        self.production_summary["total_scenes"] = num_acts * scenes_per_act
        
        self.add_timeline_event("production_started", {
            "premise": premise[:100] + "..." if len(premise) > 100 else premise,
            "structure": f"{num_acts} acts, {scenes_per_act} scenes per act"
        })
    
    def end_production(self) -> None:
        """Mark the end of production."""
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()
        
        self.add_timeline_event("production_completed", {
            "duration": f"{duration:.2f} seconds",
            "success_rate": f"{self.production_summary['completed_scenes'] / self.production_summary['total_scenes'] * 100:.1f}%"
        })
    
    def start_scene(self, scene_id: str, act_number: int, scene_number: int) -> SceneMetrics:
        """Start tracking a new scene."""
        metrics = SceneMetrics(
            scene_id=scene_id,
            act_number=act_number,
            scene_number=scene_number
        )
        self.scene_metrics[scene_id] = metrics
        
        self.add_timeline_event("scene_started", {
            "scene_id": scene_id,
            "act": act_number,
            "scene": scene_number
        })
        
        return metrics
    
    def update_scene_metrics(self, scene_id: str, updates: Dict[str, Any]) -> None:
        """Update metrics for a specific scene."""
        if scene_id in self.scene_metrics:
            metrics = self.scene_metrics[scene_id]
            for key, value in updates.items():
                if hasattr(metrics, key):
                    setattr(metrics, key, value)
    
    def complete_scene(self, scene_id: str, final_length: int, quality_score: float) -> None:
        """Mark a scene as completed."""
        if scene_id in self.scene_metrics:
            metrics = self.scene_metrics[scene_id]
            metrics.final_length = final_length
            metrics.overall_quality_score = quality_score
            
            self.production_summary["completed_scenes"] += 1
            self.production_summary["total_length"] += final_length
            
            self.add_timeline_event("scene_completed", {
                "scene_id": scene_id,
                "final_length": final_length,
                "quality_score": f"{quality_score:.2f}"
            })
    
    def track_agent_activity(self, agent_name: str, activity_type: str, details: Dict[str, Any] = None) -> None:
        """Track agent activity."""
        if agent_name not in self.agent_metrics:
            self.agent_metrics[agent_name] = AgentMetrics(
                agent_name=agent_name,
                agent_type=details.get("agent_type", "unknown") if details else "unknown"
            )
        
        metrics = self.agent_metrics[agent_name]
        
        if activity_type == "message_sent":
            metrics.messages_sent += 1
        elif activity_type == "feedback_provided":
            metrics.feedback_provided += 1
        elif activity_type == "suggestion_made":
            metrics.suggestions_made += 1
        elif activity_type == "conflict_raised":
            metrics.conflicts_raised += 1
        elif activity_type == "suggestion_accepted":
            metrics.suggestions_accepted += 1
    
    def track_workshop_round(self, scene_id: str, round_number: int, feedback_count: int, changes_made: int) -> None:
        """Track a workshop round for a scene."""
        if scene_id in self.scene_metrics:
            metrics = self.scene_metrics[scene_id]
            metrics.workshop_iterations = round_number
            metrics.agent_feedback_count += feedback_count
            metrics.feedback_applied_count += changes_made
            
            self.production_summary["total_workshops"] += 1
            
            self.add_timeline_event("workshop_round", {
                "scene_id": scene_id,
                "round": round_number,
                "feedback_items": feedback_count,
                "changes_applied": changes_made
            })
    
    def track_enhancement(self, scene_id: str, before_length: int, after_length: int, strategy: str) -> None:
        """Track scene enhancement."""
        if scene_id in self.scene_metrics:
            metrics = self.scene_metrics[scene_id]
            metrics.enhanced_length = after_length
            
            self.production_summary["total_enhancements"] += 1
            
            self.add_timeline_event("scene_enhanced", {
                "scene_id": scene_id,
                "length_increase": after_length - before_length,
                "strategy": strategy
            })
    
    def add_timeline_event(self, event_type: str, details: Dict[str, Any]) -> None:
        """Add an event to the production timeline."""
        self.timeline_events.append({
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "details": details
        })
    
    def get_production_report(self) -> Dict[str, Any]:
        """Generate comprehensive production report."""
        # Scene statistics
        scene_lengths = [m.final_length for m in self.scene_metrics.values() if m.final_length > 0]
        scene_times = [m.total_time for m in self.scene_metrics.values() if m.total_time > 0]
        quality_scores = [m.overall_quality_score for m in self.scene_metrics.values() if m.overall_quality_score > 0]
        
        # Agent statistics
        most_active_agent = max(
            self.agent_metrics.values(),
            key=lambda a: a.messages_sent,
            default=None
        )
        
        most_influential_agent = max(
            self.agent_metrics.values(),
            key=lambda a: a.suggestions_accepted,
            default=None
        )
        
        report = {
            "production_id": self.production_id,
            "duration": {
                "start": self.start_time.isoformat() if self.start_time else None,
                "end": self.end_time.isoformat() if self.end_time else None,
                "total_seconds": (self.end_time - self.start_time).total_seconds() if self.start_time and self.end_time else 0
            },
            "scene_statistics": {
                "total": self.production_summary["total_scenes"],
                "completed": self.production_summary["completed_scenes"],
                "failed": self.production_summary["failed_scenes"],
                "completion_rate": f"{self.production_summary['completed_scenes'] / self.production_summary['total_scenes'] * 100:.1f}%" if self.production_summary['total_scenes'] > 0 else "0%",
                "lengths": {
                    "total": sum(scene_lengths),
                    "average": statistics.mean(scene_lengths) if scene_lengths else 0,
                    "min": min(scene_lengths) if scene_lengths else 0,
                    "max": max(scene_lengths) if scene_lengths else 0,
                    "std_dev": statistics.stdev(scene_lengths) if len(scene_lengths) > 1 else 0
                },
                "generation_times": {
                    "average": statistics.mean(scene_times) if scene_times else 0,
                    "total": sum(scene_times)
                },
                "quality": {
                    "average_score": statistics.mean(quality_scores) if quality_scores else 0,
                    "min_score": min(quality_scores) if quality_scores else 0,
                    "max_score": max(quality_scores) if quality_scores else 0
                }
            },
            "collaboration_statistics": {
                "total_workshops": self.production_summary["total_workshops"],
                "total_enhancements": self.production_summary["total_enhancements"],
                "average_workshop_rounds": statistics.mean([m.workshop_iterations for m in self.scene_metrics.values()]) if self.scene_metrics else 0,
                "total_feedback_items": sum(m.agent_feedback_count for m in self.scene_metrics.values()),
                "feedback_application_rate": f"{sum(m.feedback_applied_count for m in self.scene_metrics.values()) / max(sum(m.agent_feedback_count for m in self.scene_metrics.values()), 1) * 100:.1f}%"
            },
            "agent_statistics": {
                "total_agents": len(self.agent_metrics),
                "most_active": {
                    "name": most_active_agent.agent_name if most_active_agent else "N/A",
                    "messages": most_active_agent.messages_sent if most_active_agent else 0
                } if most_active_agent else None,
                "most_influential": {
                    "name": most_influential_agent.agent_name if most_influential_agent else "N/A",
                    "accepted_suggestions": most_influential_agent.suggestions_accepted if most_influential_agent else 0
                } if most_influential_agent else None,
                "total_interactions": sum(a.messages_sent for a in self.agent_metrics.values())
            },
            "timeline_summary": {
                "total_events": len(self.timeline_events),
                "event_types": self._count_event_types()
            }
        }
        
        return report
    
    def _count_event_types(self) -> Dict[str, int]:
        """Count occurrences of each event type."""
        counts = {}
        for event in self.timeline_events:
            event_type = event["event_type"]
            counts[event_type] = counts.get(event_type, 0) + 1
        return counts
    
    def save_metrics(self, filepath: str) -> None:
        """Save all metrics to a JSON file."""
        data = {
            "production_report": self.get_production_report(),
            "scene_metrics": {
                scene_id: {
                    "scene_id": m.scene_id,
                    "act_number": m.act_number,
                    "scene_number": m.scene_number,
                    "final_length": m.final_length,
                    "workshop_iterations": m.workshop_iterations,
                    "overall_quality_score": m.overall_quality_score
                }
                for scene_id, m in self.scene_metrics.items()
            },
            "agent_metrics": {
                agent_name: {
                    "agent_name": m.agent_name,
                    "agent_type": m.agent_type,
                    "messages_sent": m.messages_sent,
                    "feedback_provided": m.feedback_provided,
                    "suggestions_accepted": m.suggestions_accepted
                }
                for agent_name, m in self.agent_metrics.items()
            },
            "timeline": self.timeline_events
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def print_summary(self) -> None:
        """Print a formatted summary of metrics."""
        report = self.get_production_report()
        
        print("\n" + "=" * 60)
        print("📊 PRODUCTION METRICS SUMMARY")
        print("=" * 60)
        
        print(f"\nProduction ID: {report['production_id']}")
        print(f"Duration: {report['duration']['total_seconds']:.2f} seconds")
        
        print(f"\n📝 Scene Statistics:")
        print(f"  • Completed: {report['scene_statistics']['completed']}/{report['scene_statistics']['total']} ({report['scene_statistics']['completion_rate']})")
        print(f"  • Total length: {report['scene_statistics']['lengths']['total']:,} characters")
        print(f"  • Average length: {report['scene_statistics']['lengths']['average']:,.0f} characters")
        print(f"  • Quality score: {report['scene_statistics']['quality']['average_score']:.2f}/1.0")
        
        print(f"\n🤝 Collaboration:")
        print(f"  • Workshop rounds: {report['collaboration_statistics']['total_workshops']}")
        print(f"  • Feedback items: {report['collaboration_statistics']['total_feedback_items']}")
        print(f"  • Application rate: {report['collaboration_statistics']['feedback_application_rate']}")
        
        print(f"\n🎭 Agent Activity:")
        print(f"  • Total agents: {report['agent_statistics']['total_agents']}")
        if report['agent_statistics']['most_active']:
            print(f"  • Most active: {report['agent_statistics']['most_active']['name']} ({report['agent_statistics']['most_active']['messages']} messages)")
        if report['agent_statistics']['most_influential']:
            print(f"  • Most influential: {report['agent_statistics']['most_influential']['name']} ({report['agent_statistics']['most_influential']['accepted_suggestions']} accepted)")
        
        print("\n" + "=" * 60)