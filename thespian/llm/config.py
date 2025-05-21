"""
LLM configuration management for Thespian framework.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
import os
import random


class LLMConfig(BaseModel):
    """Configuration for LLM models used in Thespian."""

    # Ollama configuration
    ollama_base_url: str = Field(default="http://localhost:11434")
    ollama_model: str = Field(default="long-gemma")

    # Grok configuration
    grok_api_key: Optional[str] = Field(default=None)
    grok_api_base: str = Field(default="https://api.x.ai/v1")
    grok_model: str = Field(default="grok-3-beta")

    # Model distribution
    ollama_usage_percentage: float = Field(default=0.5)  # 50% of agents use Ollama

    def __init__(self, **data):
        super().__init__(**data)
        # Load API keys from environment variables
        self.grok_api_key = os.getenv("XAI_API_KEY", self.grok_api_key)

    def should_use_ollama(self, agent_id: str) -> bool:
        """Determine if an agent should use Ollama based on distribution."""
        if not self.grok_api_key:
            return True

        # Use agent_id to ensure consistent model assignment
        random.seed(agent_id)
        return random.random() < self.ollama_usage_percentage

    def get_model_config(self, model_type: str) -> Dict[str, Any]:
        """Get configuration for a specific model type."""
        if model_type == "ollama":
            return {"base_url": self.ollama_base_url, "model": self.ollama_model}
        elif model_type == "grok":
            return {
                "api_key": self.grok_api_key,
                "api_base": self.grok_api_base,
                "model": self.grok_model,
            }
        else:
            raise ValueError(f"Unknown model type: {model_type}")
