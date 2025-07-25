"""
Centralized configuration management for the Thespian framework.

This module provides a unified configuration system that consolidates
all the scattered configuration patterns in the codebase.
"""

import os
import json
from typing import Dict, Any, Optional, Union, List
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class LLMConfig:
    """Configuration for LLM providers."""
    provider: str = "openai"
    model_name: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    timeout: int = 30
    api_key: Optional[str] = None
    base_url: Optional[str] = None


@dataclass
class PerformanceConfig:
    """Configuration for performance optimizations."""
    cache_enabled: bool = True
    cache_size: int = 128
    batch_processing: bool = True
    max_batch_size: int = 10
    timeout_seconds: int = 60
    max_retries: int = 3
    backoff_factor: float = 1.5


@dataclass
class QualityConfig:
    """Configuration for quality control."""
    quality_threshold: float = 0.7
    similarity_threshold: float = 0.5
    max_iterations: int = 5
    improvement_threshold: float = 0.1
    enable_advisor_feedback: bool = True
    enable_iterative_refinement: bool = True


@dataclass
class MemoryConfig:
    """Configuration for memory and tracking."""
    enable_character_tracking: bool = True
    enable_narrative_tracking: bool = True
    db_path: Optional[str] = None
    max_memory_items: int = 1000
    cleanup_threshold: int = 0.8


@dataclass
class LoggingConfig:
    """Configuration for logging."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    max_file_size: int = 10485760  # 10MB
    backup_count: int = 5


class ThespianConfig(BaseModel):
    """Main configuration class for the Thespian framework."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    # Core configurations
    llm: LLMConfig = Field(default_factory=LLMConfig)
    performance: PerformanceConfig = Field(default_factory=PerformanceConfig)
    quality: QualityConfig = Field(default_factory=QualityConfig)
    memory: MemoryConfig = Field(default_factory=MemoryConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    
    # Framework settings
    debug_mode: bool = False
    output_directory: str = "output"
    checkpoint_directory: str = "checkpoints"
    temp_directory: str = "temp"
    
    # Production settings
    default_theme: str = "A tale of adventure and discovery"
    default_style: str = "Contemporary"
    default_period: str = "Modern"
    target_audience: str = "General"
    
    @classmethod
    def from_file(cls, config_path: Union[str, Path]) -> "ThespianConfig":
        """Load configuration from a JSON file."""
        config_path = Path(config_path)
        
        if not config_path.exists():
            logger.warning(f"Config file {config_path} not found, using defaults")
            return cls()
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Convert nested dictionaries to appropriate dataclasses
            if 'llm' in data:
                data['llm'] = LLMConfig(**data['llm'])
            if 'performance' in data:
                data['performance'] = PerformanceConfig(**data['performance'])
            if 'quality' in data:
                data['quality'] = QualityConfig(**data['quality'])
            if 'memory' in data:
                data['memory'] = MemoryConfig(**data['memory'])
            if 'logging' in data:
                data['logging'] = LoggingConfig(**data['logging'])
            
            return cls(**data)
            
        except Exception as e:
            logger.error(f"Error loading config from {config_path}: {e}")
            logger.info("Using default configuration")
            return cls()
    
    @classmethod
    def from_env(cls) -> "ThespianConfig":
        """Load configuration from environment variables."""
        config = cls()
        
        # LLM configuration
        if os.getenv("THESPIAN_LLM_PROVIDER"):
            config.llm.provider = os.getenv("THESPIAN_LLM_PROVIDER")
        if os.getenv("THESPIAN_LLM_MODEL"):
            config.llm.model_name = os.getenv("THESPIAN_LLM_MODEL")
        if os.getenv("THESPIAN_LLM_TEMPERATURE"):
            config.llm.temperature = float(os.getenv("THESPIAN_LLM_TEMPERATURE"))
        if os.getenv("OPENAI_API_KEY"):
            config.llm.api_key = os.getenv("OPENAI_API_KEY")
        
        # Performance configuration
        if os.getenv("THESPIAN_CACHE_ENABLED"):
            config.performance.cache_enabled = os.getenv("THESPIAN_CACHE_ENABLED").lower() == "true"
        if os.getenv("THESPIAN_MAX_RETRIES"):
            config.performance.max_retries = int(os.getenv("THESPIAN_MAX_RETRIES"))
        
        # Quality configuration
        if os.getenv("THESPIAN_QUALITY_THRESHOLD"):
            config.quality.quality_threshold = float(os.getenv("THESPIAN_QUALITY_THRESHOLD"))
        
        # Directory configuration
        if os.getenv("THESPIAN_OUTPUT_DIR"):
            config.output_directory = os.getenv("THESPIAN_OUTPUT_DIR")
        if os.getenv("THESPIAN_CHECKPOINT_DIR"):
            config.checkpoint_directory = os.getenv("THESPIAN_CHECKPOINT_DIR")
        
        # Debug mode
        if os.getenv("THESPIAN_DEBUG"):
            config.debug_mode = os.getenv("THESPIAN_DEBUG").lower() == "true"
        
        return config
    
    def to_file(self, config_path: Union[str, Path]) -> None:
        """Save configuration to a JSON file."""
        config_path = Path(config_path)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert dataclasses to dictionaries for JSON serialization
        data = {
            "llm": {
                "provider": self.llm.provider,
                "model_name": self.llm.model_name,
                "temperature": self.llm.temperature,
                "max_tokens": self.llm.max_tokens,
                "timeout": self.llm.timeout,
                "base_url": self.llm.base_url
                # Note: API key not saved for security
            },
            "performance": {
                "cache_enabled": self.performance.cache_enabled,
                "cache_size": self.performance.cache_size,
                "batch_processing": self.performance.batch_processing,
                "max_batch_size": self.performance.max_batch_size,
                "timeout_seconds": self.performance.timeout_seconds,
                "max_retries": self.performance.max_retries,
                "backoff_factor": self.performance.backoff_factor
            },
            "quality": {
                "quality_threshold": self.quality.quality_threshold,
                "similarity_threshold": self.quality.similarity_threshold,
                "max_iterations": self.quality.max_iterations,
                "improvement_threshold": self.quality.improvement_threshold,
                "enable_advisor_feedback": self.quality.enable_advisor_feedback,
                "enable_iterative_refinement": self.quality.enable_iterative_refinement
            },
            "memory": {
                "enable_character_tracking": self.memory.enable_character_tracking,
                "enable_narrative_tracking": self.memory.enable_narrative_tracking,
                "db_path": self.memory.db_path,
                "max_memory_items": self.memory.max_memory_items,
                "cleanup_threshold": self.memory.cleanup_threshold
            },
            "logging": {
                "level": self.logging.level,
                "format": self.logging.format,
                "file_path": self.logging.file_path,
                "max_file_size": self.logging.max_file_size,
                "backup_count": self.logging.backup_count
            },
            "debug_mode": self.debug_mode,
            "output_directory": self.output_directory,
            "checkpoint_directory": self.checkpoint_directory,
            "temp_directory": self.temp_directory,
            "default_theme": self.default_theme,
            "default_style": self.default_style,
            "default_period": self.default_period,
            "target_audience": self.target_audience
        }
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Configuration saved to {config_path}")
        except Exception as e:
            logger.error(f"Error saving config to {config_path}: {e}")
    
    def ensure_directories(self) -> None:
        """Ensure all configured directories exist."""
        directories = [
            self.output_directory,
            self.checkpoint_directory,
            self.temp_directory
        ]
        
        for directory in directories:
            path = Path(directory)
            path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Ensured directory exists: {path}")
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of issues."""
        issues = []
        
        # Validate LLM configuration
        if not self.llm.provider:
            issues.append("LLM provider not specified")
        
        if not self.llm.model_name:
            issues.append("LLM model name not specified")
        
        if self.llm.temperature < 0 or self.llm.temperature > 2:
            issues.append("LLM temperature should be between 0 and 2")
        
        # Validate performance configuration
        if self.performance.cache_size < 1:
            issues.append("Cache size must be at least 1")
        
        if self.performance.max_retries < 0:
            issues.append("Max retries cannot be negative")
        
        # Validate quality configuration
        if self.quality.quality_threshold < 0 or self.quality.quality_threshold > 1:
            issues.append("Quality threshold must be between 0 and 1")
        
        if self.quality.max_iterations < 1:
            issues.append("Max iterations must be at least 1")
        
        return issues
    
    def get_merged_config(self, overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get a merged configuration dictionary with optional overrides."""
        base_config = {
            "llm": self.llm.__dict__,
            "performance": self.performance.__dict__,
            "quality": self.quality.__dict__,
            "memory": self.memory.__dict__,
            "logging": self.logging.__dict__,
            "debug_mode": self.debug_mode,
            "output_directory": self.output_directory,
            "checkpoint_directory": self.checkpoint_directory,
            "temp_directory": self.temp_directory,
            "default_theme": self.default_theme,
            "default_style": self.default_style,
            "default_period": self.default_period,
            "target_audience": self.target_audience
        }
        
        if overrides:
            # Deep merge overrides
            for key, value in overrides.items():
                if key in base_config and isinstance(base_config[key], dict) and isinstance(value, dict):
                    base_config[key].update(value)
                else:
                    base_config[key] = value
        
        return base_config


# Global configuration instance
_global_config: Optional[ThespianConfig] = None


def get_config() -> ThespianConfig:
    """Get the global configuration instance."""
    global _global_config
    if _global_config is None:
        # Try to load from environment first, then default config file
        config_file = Path("thespian_config.json")
        if config_file.exists():
            _global_config = ThespianConfig.from_file(config_file)
        else:
            _global_config = ThespianConfig.from_env()
        
        # Ensure directories exist
        _global_config.ensure_directories()
    
    return _global_config


def set_config(config: ThespianConfig) -> None:
    """Set the global configuration instance."""
    global _global_config
    _global_config = config
    _global_config.ensure_directories()


def reset_config() -> None:
    """Reset the global configuration to default."""
    global _global_config
    _global_config = None