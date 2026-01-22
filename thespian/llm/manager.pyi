"""
Type stubs for thespian.llm.manager module.

This stub file provides type information for IDEs and type checkers.
"""

from typing import Dict, Any, Optional, List

class LLMManager:
    """
    Manager for LLM provider interactions.
    """
    def __init__(
        self,
        provider: str = ...,
        model_name: str = ...,
        api_key: Optional[str] = ...,
        **kwargs: Any
    ) -> None: ...
    
    def generate(
        self,
        prompt: str,
        temperature: float = ...,
        max_tokens: Optional[int] = ...,
        **kwargs: Any
    ) -> str: ...
    
    def generate_batch(
        self,
        prompts: List[str],
        **kwargs: Any
    ) -> List[str]: ...
    
    def set_provider(self, provider: str) -> None: ...
    def set_model(self, model_name: str) -> None: ...
