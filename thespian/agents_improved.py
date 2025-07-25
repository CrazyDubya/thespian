"""
Refactored agent interfaces with better dependency management.

This module provides cleaner agent implementations that reduce dependency on
LangChain and provide better testability and modularity.
"""

from typing import Dict, Any, List, Optional, Protocol, Union
from pydantic import BaseModel, Field
from abc import ABC, abstractmethod
import logging

from thespian.llm import LLMManager
from thespian.llm.error_handling import (
    with_error_handling, 
    PlaywrightError, 
    global_error_handler,
    ErrorSeverity
)

logger = logging.getLogger(__name__)


class LLMProvider(Protocol):
    """Protocol for LLM providers to ensure consistent interface."""
    
    def invoke(self, prompt: str) -> Any:
        """Invoke the LLM with a prompt."""
        ...


class BaseAgent(BaseModel, ABC):
    """
    Refactored base class for all theatrical agents.
    
    This version reduces LangChain dependencies and provides better
    error handling and testability.
    """
    
    name: str = Field(..., description="Name of the agent")
    role: str = Field(..., description="Role of the agent in the production")
    llm_manager: Optional[LLMManager] = None
    model_type: str = Field(default="default", description="LLM model type to use")
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, **data):
        super().__init__(**data)
        if not self.llm_manager:
            self.llm_manager = LLMManager()
    
    @with_error_handling(global_error_handler, severity=ErrorSeverity.HIGH)
    def get_llm(self) -> LLMProvider:
        """Get the LLM instance with error handling."""
        if not self.llm_manager:
            raise PlaywrightError("LLM manager not initialized")
        return self.llm_manager.get_llm(self.model_type)
    
    @abstractmethod
    def perform_role(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform the agent's specific role in the production."""
        pass
    
    def validate_input(self, data: Dict[str, Any]) -> bool:
        """Validate input data for the agent."""
        return isinstance(data, dict)


class ImprovedPlaywrightAgent(BaseAgent):
    """
    Improved playwright agent with better error handling and modularity.
    """
    
    def __init__(self, **data):
        super().__init__(name="Playwright", role="Writer", **data)
    
    @with_error_handling(global_error_handler, severity=ErrorSeverity.MEDIUM)
    def generate_concept(self, theme: str) -> Dict[str, Any]:
        """Generate a play concept based on the theme."""
        if not theme or not theme.strip():
            raise PlaywrightError("Theme cannot be empty")
        
        prompt = self._build_concept_prompt(theme)
        
        try:
            llm = self.get_llm()
            response = llm.invoke(prompt)
            content = self._extract_content(response)
            
            return {
                "concept": content,
                "theme": theme,
                "agent": self.name,
                "timestamp": None  # Will be set by framework
            }
        except Exception as e:
            raise PlaywrightError(f"Failed to generate concept: {str(e)}")
    
    @with_error_handling(global_error_handler, severity=ErrorSeverity.MEDIUM)
    def write_script(self, concept: Dict[str, Any]) -> Dict[str, Any]:
        """Write a complete script based on the concept."""
        if not concept or 'concept' not in concept:
            raise PlaywrightError("Invalid concept data provided")
        
        prompt = self._build_script_prompt(concept['concept'])
        
        try:
            llm = self.get_llm()
            response = llm.invoke(prompt)
            content = self._extract_content(response)
            
            return {
                "script": content,
                "concept": concept,
                "agent": self.name,
                "timestamp": None
            }
        except Exception as e:
            raise PlaywrightError(f"Failed to write script: {str(e)}")
    
    def perform_role(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform the playwright's role in the production."""
        if 'theme' in context:
            concept = self.generate_concept(context['theme'])
            script = self.write_script(concept)
            return {"concept": concept, "script": script}
        elif 'concept' in context:
            script = self.write_script(context['concept'])
            return {"script": script}
        else:
            raise PlaywrightError("No valid context provided for playwright")
    
    def _build_concept_prompt(self, theme: str) -> str:
        """Build prompt for concept generation."""
        return f"""You are a professional playwright tasked with creating a theatrical concept.

Create a detailed concept for a play based on the theme: {theme}

Include:
1. A compelling title
2. Brief synopsis (2-3 paragraphs)
3. Main characters (3-5 characters with brief descriptions)
4. Setting and time period
5. Genre and tone
6. Central conflict or dramatic question
7. Target audience

Format your response clearly with appropriate headings."""
    
    def _build_script_prompt(self, concept: str) -> str:
        """Build prompt for script generation."""
        return f"""You are a professional playwright writing a complete theatrical script.

Based on this concept: {concept}

Write a complete script that includes:
1. Title page with cast list and synopsis
2. Clear act and scene divisions
3. Detailed stage directions and character movements
4. Rich dialogue with emotional depth
5. Technical notes for lighting, sound, and special effects
6. Character development through actions and dialogue
7. Clear scene transitions and timing notes
8. Detailed descriptions of settings and atmosphere

Format the script professionally with proper spacing and indentation."""
    
    def _extract_content(self, response: Any) -> str:
        """Extract content from LLM response with error handling."""
        if hasattr(response, 'content'):
            return str(response.content)
        elif isinstance(response, (str, bytes)):
            return str(response)
        else:
            return str(response)


class ImprovedDirectorAgent(BaseAgent):
    """Improved director agent with cleaner interface."""
    
    def __init__(self, **data):
        super().__init__(name="Director", role="Director", **data)
    
    @with_error_handling(global_error_handler, severity=ErrorSeverity.MEDIUM)
    def provide_direction(self, script: Dict[str, Any]) -> Dict[str, Any]:
        """Provide directorial guidance for the script."""
        if not script or 'script' not in script:
            raise PlaywrightError("Invalid script data provided")
        
        prompt = f"""You are a theatrical director reviewing this script:

{script['script']}

Provide directorial notes including:
1. Overall vision and interpretation
2. Character direction and motivation notes
3. Staging and blocking suggestions
4. Pacing and rhythm guidance
5. Technical requirements (lighting, sound, effects)
6. Set design considerations
7. Costume and makeup notes

Format your response with clear sections for each element."""
        
        try:
            llm = self.get_llm()
            response = llm.invoke(prompt)
            content = self._extract_content(response)
            
            return {
                "direction": content,
                "script": script,
                "agent": self.name,
                "timestamp": None
            }
        except Exception as e:
            raise PlaywrightError(f"Failed to provide direction: {str(e)}")
    
    def perform_role(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform the director's role in the production."""
        if 'script' in context:
            return self.provide_direction(context['script'])
        else:
            raise PlaywrightError("No script provided for director")
    
    def _extract_content(self, response: Any) -> str:
        """Extract content from LLM response."""
        if hasattr(response, 'content'):
            return str(response.content)
        elif isinstance(response, (str, bytes)):
            return str(response)
        else:
            return str(response)


# Factory function for agent creation
def create_agent(agent_type: str, **kwargs) -> BaseAgent:
    """Factory function to create agents with proper error handling."""
    agent_classes = {
        "playwright": ImprovedPlaywrightAgent,
        "director": ImprovedDirectorAgent,
    }
    
    agent_class = agent_classes.get(agent_type.lower())
    if not agent_class:
        raise ValueError(f"Unknown agent type: {agent_type}")
    
    return agent_class(**kwargs)