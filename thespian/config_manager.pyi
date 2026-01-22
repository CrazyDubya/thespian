"""
Type stubs for thespian.config_manager module.

This stub file provides type information for IDEs and type checkers.
"""

from typing import Dict, Any, Optional, Union, List
from pathlib import Path
from dataclasses import dataclass

@dataclass
class LLMConfig:
    """Configuration for LLM providers."""
    provider: str
    model_name: str
    temperature: float
    max_tokens: Optional[int]
    timeout: int
    api_key: Optional[str]
    base_url: Optional[str]

@dataclass
class PerformanceConfig:
    """Configuration for performance optimizations."""
    cache_enabled: bool
    cache_size: int
    batch_processing: bool
    max_batch_size: int
    timeout_seconds: int
    max_retries: int
    backoff_factor: float

@dataclass
class QualityConfig:
    """Configuration for quality control."""
    quality_threshold: float
    similarity_threshold: float
    max_iterations: int
    improvement_threshold: float
    enable_advisor_feedback: bool

@dataclass
class ThespianConfig:
    """Main configuration class."""
    llm: LLMConfig
    performance: PerformanceConfig
    quality: QualityConfig

def get_config() -> ThespianConfig: ...
def update_config(config_dict: Dict[str, Any]) -> None: ...
def load_config_from_file(filepath: Union[str, Path]) -> ThespianConfig: ...
def save_config_to_file(filepath: Union[str, Path]) -> None: ...
def reset_config() -> None: ...
