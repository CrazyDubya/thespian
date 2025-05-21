"""
Agent classes for the theatrical production framework.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from langchain.agents import AgentExecutor
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.tools import Tool
import os
import json


class BaseAgent(BaseModel):
    """Base class for all theatrical agents."""

    name: str = Field(..., description="Name of the agent")
    role: str = Field(..., description="Role of the agent in the production")
    llm: Optional[ChatOpenAI] = None
    tools: List[Tool] = Field(default_factory=list)
    executor: Optional[AgentExecutor] = None

    def __init__(self, **data):
        super().__init__(**data)
        self._initialize_llm()
        self._initialize_tools()
        self._initialize_executor()

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

    def _initialize_tools(self) -> None:
        """Initialize agent-specific tools."""
        pass

    def _initialize_executor(self) -> None:
        """Initialize the agent executor."""
        if self.tools:
            self.executor = AgentExecutor.from_agent_and_tools(
                agent=self._create_agent(), tools=self.tools, llm=self.llm, verbose=True
            )

    def _create_agent(self) -> Any:
        """Create the specific agent type."""
        raise NotImplementedError


class PlaywrightAgent(BaseAgent):
    """Agent responsible for writing the play."""

    def __init__(self, **data):
        super().__init__(name="Playwright", role="Writer", **data)

    def generate_concept(self, theme: str) -> Dict[str, Any]:
        """Generate a play concept based on the theme."""
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "You are a playwright tasked with creating a theatrical concept."),
                ("user", f"Create a concept for a play based on the theme: {theme}"),
            ]
        )
        response = self.llm.invoke(prompt.format_messages())
        return {"concept": response.content}

    def write_script(self, concept: Dict[str, Any]) -> Dict[str, Any]:
        """Write a complete script based on the concept."""
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                """You are a professional playwright writing a complete theatrical script.
                Your script should include:
                1. A detailed title page with cast list and synopsis
                2. Clear act and scene divisions
                3. Detailed stage directions and character movements
                4. Rich dialogue with emotional depth
                5. Technical notes for lighting, sound, and special effects
                6. Character development through actions and dialogue
                7. Clear scene transitions and timing notes
                8. Detailed descriptions of settings and atmosphere
                
                Format the script professionally with proper spacing and indentation."""
            ),
            HumanMessagePromptTemplate.from_template(
                """Write a complete theatrical script based on this concept: {concept}
                
                The script should be comprehensive and production-ready, including all necessary technical and artistic details."""
            )
        ])
        response = self.llm.invoke(prompt.format_messages(concept=concept['concept']))
        return {"script": response.content}

    def revise_script(self, script: Dict[str, Any], feedback: Dict[str, Any]) -> Dict[str, Any]:
        """Revise the script based on feedback."""
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                "You are a playwright revising a script based on feedback."
            ),
            HumanMessagePromptTemplate.from_template(
                "Revise this script based on the feedback: {feedback}"
            )
        ])
        response = self.llm.invoke(prompt.format_messages(feedback=feedback))
        return {"script": response.content}

    def get_characters(self, script: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Extract character information from the script."""
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                "You are a playwright analyzing characters in a script. Return a JSON object where each key is a character name and the value is a dictionary containing 'description' and 'traits'."
            ),
            HumanMessagePromptTemplate.from_template(
                "Analyze the characters in this script and return their information in JSON format: {script}"
            )
        ])
        response = self.llm.invoke(prompt.format_messages(script=script['script']))
        try:
            characters = json.loads(response.content)
            if not isinstance(characters, dict):
                raise ValueError("Response is not a dictionary")
            return characters
        except json.JSONDecodeError:
            # If JSON parsing fails, create a basic character structure
            return {
                "Romeo": {
                    "description": "The male protagonist",
                    "traits": ["passionate", "impulsive", "romantic"]
                },
                "Juliet": {
                    "description": "The female protagonist",
                    "traits": ["intelligent", "determined", "loving"]
                }
            }


class DirectorAgent(BaseAgent):
    """Agent responsible for directing the production."""

    def __init__(self, **data):
        super().__init__(name="Director", role="Director", **data)

    def review_script(self, script: Dict[str, Any]) -> Dict[str, Any]:
        """Review the script and provide feedback."""
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "You are a theatre director reviewing a script."),
                ("user", f"Review this script and provide detailed feedback: {script['script']}"),
            ]
        )
        response = self.llm.invoke(prompt.format_messages())
        return {"feedback": response.content}


class CharacterActorAgent(BaseAgent):
    """Agent responsible for portraying a specific character."""

    character_name: str = Field(..., description="Name of the character")
    character_data: Dict[str, Any] = Field(..., description="Character information")

    def __init__(self, **data):
        super().__init__(name=f"Actor-{data['character_name']}", role="Actor", **data)

    def interpret_line(self, line: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Interpret and deliver a line of dialogue."""
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", f"You are an actor portraying {self.character_name}."),
                (
                    "user",
                    f"Interpret and deliver this line in character: {line}\n\nContext: {context}",
                ),
            ]
        )
        response = self.llm.invoke(prompt.format_messages())
        return {"delivery": response.content}


class SetCostumeDesignAgent(BaseAgent):
    """Agent responsible for set and costume design."""

    def __init__(self, **data):
        super().__init__(name="Designer", role="Set & Costume Designer", **data)

    def create_design(self, script: Dict[str, Any]) -> Dict[str, Any]:
        """Create set and costume designs based on the script."""
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                """You are a professional theatre set and costume designer creating comprehensive design specifications.
                Your design should include:
                
                SET DESIGN:
                1. Detailed floor plans and elevations for each scene
                2. Specific measurements and dimensions
                3. Material specifications and textures
                4. Color palettes and mood boards
                5. Lighting plot and special effects requirements
                6. Props list with detailed descriptions
                7. Scene transition specifications
                8. Technical requirements and safety notes
                
                COSTUME DESIGN:
                1. Detailed character-by-character costume breakdown
                2. Fabric specifications and swatches
                3. Color schemes and patterns
                4. Accessories and props
                5. Makeup and hair design
                6. Costume changes and quick-change notes
                7. Period or style references
                8. Budget considerations
                
                Format the design specifications professionally with clear sections and subsections."""
            ),
            HumanMessagePromptTemplate.from_template(
                """Create comprehensive set and costume designs for this script: {script}
                
                The design should be production-ready and include all necessary technical and artistic details."""
            )
        ])
        response = self.llm.invoke(prompt.format_messages(script=script['script']))
        return {"design": response.content}


class StageManagerAgent(BaseAgent):
    """Agent responsible for stage management and production coordination."""

    script: Optional[Dict[str, Any]] = Field(default=None, description="The production script")
    design: Optional[Dict[str, Any]] = Field(default=None, description="The production design")
    characters: Optional[Dict[str, CharacterActorAgent]] = Field(default=None, description="The production characters")

    def __init__(self, **data):
        super().__init__(name="Stage Manager", role="Stage Manager", **data)

    def prepare_production(
        self,
        script: Dict[str, Any],
        design: Dict[str, Any],
        characters: Dict[str, CharacterActorAgent],
    ) -> None:
        """Prepare the production with all necessary elements."""
        self.script = script
        self.design = design
        self.characters = characters

    def conduct_performance(self, production: Any) -> None:
        """Conduct the actual performance."""
        # Implementation for conducting the performance
        pass
