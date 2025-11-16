"""
IDE Integration Module for Thespian

This module provides backend APIs and components for IDE integration,
enabling collaborative script editing, rehearsal sandboxing, performance
analytics, and agent visualization.
"""

from .script_editor import ScriptEditor
from .rehearsal_sandbox import RehearsalSandbox
from .performance_dashboard import PerformanceDashboard
from .agent_visualizer import AgentVisualizer
from .prompt_manager import PromptManager

__all__ = [
    'ScriptEditor',
    'RehearsalSandbox',
    'PerformanceDashboard',
    'AgentVisualizer',
    'PromptManager',
]
