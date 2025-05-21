"""
LLM manager for handling different language models.
"""

import os
from typing import Dict, Any, Optional
import requests
import httpx
import json
from openai import OpenAI
from pydantic import BaseModel, Field, ConfigDict
from rich.console import Console, ConsoleRenderable
from rich.text import Text
from datetime import datetime
from langchain_openai import ChatOpenAI
import logging

logger = logging.getLogger(__name__)

class LLMResponseEncoder(json.JSONEncoder):
    """Custom JSON encoder for LLMResponse objects."""

    def default(self, obj):
        if isinstance(obj, LLMResponse):
            return obj.to_dict()
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


class LLMResponse:
    """Response from an LLM model."""

    def __init__(self, content: str):
        self.content = content

    def __str__(self):
        return self.content

    def __rich_console__(self, console: Console, options: Any) -> ConsoleRenderable:
        """Support Rich rendering."""
        return Text(self.content)

    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary for JSON serialization."""
        return {"content": self.content}

    def __dict__(self) -> Dict[str, str]:
        """Support direct dictionary conversion."""
        return self.to_dict()

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"LLMResponse(content={repr(self.content)})"


class OllamaLLM:
    """Ollama LLM integration."""

    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url

    def invoke(self, prompt: str) -> LLMResponse:
        """Generate a response using Ollama."""
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={"model": "long-gemma", "prompt": prompt, "stream": False},
        )
        response.raise_for_status()
        return LLMResponse(response.json()["response"])


class GrokLLM:
    """Grok LLM integration using OpenAI protocol."""

    def __init__(self, api_key: Optional[str] = None, api_base: str = "https://api.x.ai/v1"):
        self.api_key = api_key or os.getenv("XAI_API_KEY")
        self.api_base = api_base
        self.client = None
        if self.api_key:
            try:
                self.client = OpenAI(
                    api_key=self.api_key,
                    base_url=api_base,
                    http_client=httpx.Client(),  # Use default client without proxies
                )
            except Exception as e:
                print(f"Warning: Failed to initialize Grok client: {e}")

    def invoke(self, prompt: str) -> LLMResponse:
        """Generate a response using Grok."""
        if not self.client:
            return LLMResponse(
                "Note: Grok model is not available. Please ensure XAI_API_KEY is set. "
                "Using placeholder response."
            )

        try:
            response = self.client.chat.completions.create(
                model="grok-3-beta", messages=[{"role": "user", "content": prompt}]
            )
            return LLMResponse(response.choices[0].message.content)
        except Exception as e:
            return LLMResponse(
                f"Note: Error using Grok model: {str(e)}. " "Using placeholder response."
            )


class LLMManager(BaseModel):
    """Manager for handling different LLM models."""

    model_config = ConfigDict(arbitrary_types_allowed=True, protected_namespaces=())

    ollama_base_url: str = Field(default="http://localhost:11434")
    grok_api_base: str = Field(default="https://api.x.ai/v1")
    grok_api_key: Optional[str] = Field(default=None)
    ollama_model: str = Field(default="long-gemma")
    grok_model: str = Field(default="grok-3-beta")

    _ollama: Optional[OllamaLLM] = None
    _grok: Optional[GrokLLM] = None

    llm: Optional[ChatOpenAI] = Field(default=None, description="The language model instance")

    def __init__(self, **data):
        super().__init__(**data)
        self._ollama = OllamaLLM(self.ollama_base_url)
        self._grok = GrokLLM(self.grok_api_key, self.grok_api_base)
        self._initialize_llm()

    def _initialize_llm(self) -> None:
        """Initialize the language model."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        
        self.llm = ChatOpenAI(
            model_name="gpt-4",
            temperature=0.7,
            openai_api_key=api_key
        )

    @property
    def config(self):
        class ConfigShim:
            def __init__(self, ollama_model, grok_model):
                self.ollama_model = ollama_model
                self.grok_model = grok_model

        return ConfigShim(self.ollama_model, self.grok_model)

    def get_llm(self, model_type: str):
        """Get the appropriate LLM model."""
        if model_type == "ollama":
            return self._ollama
        elif model_type == "grok":
            return self._grok
        else:
            raise ValueError(f"Unknown model type: {model_type}")

    def get_model_info(self, agent_id: str) -> dict:
        """Determine which model to use based on agent ID (hash-based distribution)."""
        # Use agent ID hash to consistently assign models
        agent_hash = sum(ord(c) for c in agent_id)
        ollama_pct = 0.5  # Default 50% Ollama, can be adjusted
        try:
            ollama_pct = float(getattr(self, "ollama_usage_percentage", 0.5))
        except Exception:
            pass
        use_ollama = (agent_hash % 100) < (ollama_pct * 100)
        if use_ollama:
            return {"type": "ollama", "model": self.ollama_model}
        elif self._grok is not None:
            return {"type": "grok", "model": self.grok_model}
        else:
            return {"type": "ollama", "model": self.ollama_model}

    def generate_response(self, prompt: str, agent_id: str) -> Dict[str, Any]:
        """Generate a response using the appropriate model based on agent ID."""
        # For now, use Ollama for all responses
        response = self._ollama.invoke(prompt)
        return {"response": str(response), "model": "ollama"}

    def generate(self, prompt: str) -> str:
        """Generate text using the language model."""
        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            logger.error(f"Error generating text: {str(e)}")
            raise
