"""
LLM model management for Thespian framework.
"""

from typing import Dict, Any, Optional, Union
from pydantic import BaseModel, Field, ConfigDict
import requests
import json
from openai import OpenAI
from .config import LLMConfig


class LLMManager(BaseModel):
    """Manager for LLM model interactions."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    config: LLMConfig = Field(default_factory=LLMConfig)
    openai_client: Optional[OpenAI] = None

    def __init__(self, **data):
        super().__init__(**data)
        # Configure OpenAI client for Grok if API key is available
        if self.config.grok_api_key:
            self.openai_client = OpenAI(
                api_key=self.config.grok_api_key, base_url=self.config.grok_api_base
            )

    def get_model_info(self, agent_id: str) -> Dict[str, str]:
        """Determine which model to use based on agent ID."""
        # Use agent ID hash to consistently assign models
        agent_hash = sum(ord(c) for c in agent_id)
        use_ollama = (agent_hash % 100) < (self.config.ollama_usage_percentage * 100)

        if use_ollama:
            return {"type": "ollama", "model": self.config.ollama_model}
        elif self.openai_client:
            return {"type": "grok", "model": self.config.grok_model}
        else:
            # Default to Ollama if Grok is not available
            return {"type": "ollama", "model": self.config.ollama_model}

    def generate_response(self, prompt: str, agent_id: str, **kwargs: Any) -> Dict[str, Any]:
        """Generate a response using the appropriate model."""
        model_info = self.get_model_info(agent_id)

        if model_info["type"] == "ollama":
            return self._generate_ollama_response(prompt, **kwargs)
        else:
            return self._generate_grok_response(prompt, **kwargs)

    def _generate_ollama_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate a response using Ollama."""
        url = f"{self.config.ollama_base_url}/api/generate"

        data = {
            "model": self.config.ollama_model,
            "prompt": prompt,
            "stream": False,  # We'll handle streaming manually
            **kwargs,
        }

        response = requests.post(url, json=data)
        response.raise_for_status()

        # Collect the full response
        full_response = ""
        for line in response.iter_lines():
            if line:
                chunk = json.loads(line)
                if "response" in chunk:
                    full_response += chunk["response"]

        return {"response": full_response.strip(), "model": self.config.ollama_model}

    def _generate_grok_response(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate a response using Grok."""
        if not self.openai_client:
            raise ValueError("Grok API key not configured")

        # Convert common kwargs to OpenAI format
        openai_kwargs = {
            "model": self.config.grok_model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 150),
            "stream": False,
        }

        response = self.openai_client.chat.completions.create(**openai_kwargs)

        return {
            "response": response.choices[0].message.content.strip(),
            "model": self.config.grok_model,
        }
