"""
Performance Dashboard Backend API

Provides analytics and metrics tracking for theatrical productions.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import uuid


@dataclass
class PerformanceMetric:
    """Represents a single performance metric."""
    metric_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    metric_name: str = ""
    value: float = 0.0
    unit: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    scene_id: Optional[str] = None
    category: str = "general"
    metadata: Dict[str, Any] = field(default_factory=dict)


class PerformanceDashboard:
    """
    Backend API for performance analytics and metrics tracking.

    Features:
    - Real-time metrics collection
    - Historical trend analysis
    - Quality score tracking
    - Generation performance metrics
    - Agent contribution analytics
    """

    def __init__(self):
        """Initialize the performance dashboard."""
        self.metrics: List[PerformanceMetric] = []
        self.metric_categories = {
            "quality": ["overall_score", "dialogue_quality", "character_consistency"],
            "performance": ["generation_time", "iterations_count", "token_usage"],
            "collaboration": ["agent_interactions", "feedback_rounds", "consensus_score"],
        }

    def record_metric(
        self,
        metric_name: str,
        value: float,
        unit: str = "",
        scene_id: Optional[str] = None,
        category: str = "general",
        metadata: Optional[Dict[str, Any]] = None
    ) -> PerformanceMetric:
        """Record a new performance metric."""
        metric = PerformanceMetric(
            metric_name=metric_name,
            value=value,
            unit=unit,
            scene_id=scene_id,
            category=category,
            metadata=metadata or {},
            timestamp=datetime.now()
        )

        self.metrics.append(metric)
        return metric

    def get_metrics(
        self,
        category: Optional[str] = None,
        scene_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[PerformanceMetric]:
        """Get metrics with optional filtering."""
        filtered = self.metrics

        if category:
            filtered = [m for m in filtered if m.category == category]

        if scene_id:
            filtered = [m for m in filtered if m.scene_id == scene_id]

        if start_time:
            filtered = [m for m in filtered if m.timestamp >= start_time]

        if end_time:
            filtered = [m for m in filtered if m.timestamp <= end_time]

        return filtered

    def get_metric_summary(
        self,
        metric_name: str,
        time_period: Optional[timedelta] = None
    ) -> Dict[str, Any]:
        """Get a statistical summary for a specific metric."""
        start_time = None
        if time_period:
            start_time = datetime.now() - time_period

        metrics = self.get_metrics(start_time=start_time)
        metric_values = [m.value for m in metrics if m.metric_name == metric_name]

        if not metric_values:
            return {"error": "No data found for metric"}

        return {
            "metric_name": metric_name,
            "count": len(metric_values),
            "average": sum(metric_values) / len(metric_values),
            "min": min(metric_values),
            "max": max(metric_values),
            "latest": metric_values[-1],
            "trend": "improving" if len(metric_values) > 1 and metric_values[-1] > metric_values[0] else "declining"
        }

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data."""
        return {
            "total_metrics": len(self.metrics),
            "categories": list(self.metric_categories.keys()),
            "recent_metrics": [
                {
                    "name": m.metric_name,
                    "value": m.value,
                    "timestamp": m.timestamp.isoformat()
                }
                for m in sorted(self.metrics, key=lambda x: x.timestamp, reverse=True)[:10]
            ],
        }
