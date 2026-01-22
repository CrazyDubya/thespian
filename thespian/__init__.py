"""
Thespian - AI-Powered Theatrical Production Framework

Thespian is a comprehensive framework for generating theatrical productions using
Large Language Models (LLMs) and multi-agent collaboration. It orchestrates various
creative agents to produce complete theatrical works including scripts, staging,
character development, and production elements.

Key Features:
    - Multi-agent theatrical production system
    - LLM-powered script generation with multiple playwright variants
    - Character analysis and development tracking
    - Memory management for narrative continuity
    - Quality control and iterative refinement
    - Advanced story structure support
    - TUI (Terminal User Interface) for interactive productions
    - Comprehensive testing and validation

Main Components:
    - Theatre: Main orchestration class
    - Agents: Specialized agents for different theatrical roles
    - LLM: Language model integration and playwright variants
    - Processors: Scene and act processing utilities
    - Memory: Narrative and character continuity management
    - TUI: Interactive terminal interface

Quick Start:
    >>> from thespian import Theatre
    >>> 
    >>> # Create a new theatre with a theme
    >>> theatre = Theatre(theme="A comedy about mistaken identity")
    >>> 
    >>> # Generate a production
    >>> production = theatre.create_production()
    >>> 
    >>> # Access the generated script
    >>> print(production.script)

For more information, see the documentation in the docs/ directory and the
comprehensive code review report in COMPREHENSIVE_CODE_REVIEW.md.
"""

from .theatre import Theatre
from .production import Production
from .performance import Performance

__version__ = "0.1.0"
__all__ = ["Theatre", "Production", "Performance"]
