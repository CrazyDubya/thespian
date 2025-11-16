"""
Prompt Manager Backend API

Provides management and optimization of prompts for LLM interactions.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import uuid


class PromptCategory(str, Enum):
    """Categories of prompts."""
    SCENE_GENERATION = "scene_generation"
    CHARACTER_DEVELOPMENT = "character_development"
    DIALOGUE = "dialogue"
    STAGE_DIRECTIONS = "stage_directions"
    CRITIQUE = "critique"
    REVISION = "revision"


@dataclass
class PromptTemplate:
    """Represents a prompt template."""
    template_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    category: PromptCategory = PromptCategory.SCENE_GENERATION
    template: str = ""
    variables: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    usage_count: int = 0
    average_quality: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PromptExecution:
    """Represents a single execution of a prompt."""
    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    template_id: str = ""
    rendered_prompt: str = ""
    variables_used: Dict[str, str] = field(default_factory=dict)
    executed_at: datetime = field(default_factory=datetime.now)
    quality_score: Optional[float] = None
    token_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


class PromptManager:
    """
    Backend API for prompt management and optimization.

    Features:
    - Prompt template library
    - Variable substitution
    - Usage tracking and analytics
    - A/B testing of prompt variations
    - Quality correlation analysis
    """

    def __init__(self):
        """Initialize the prompt manager."""
        self.templates: Dict[str, PromptTemplate] = {}
        self.executions: List[PromptExecution] = []

    def create_template(
        self,
        name: str,
        template: str,
        category: PromptCategory,
        variables: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> PromptTemplate:
        """Create a new prompt template."""
        prompt_template = PromptTemplate(
            name=name,
            template=template,
            category=category,
            variables=variables or [],
            metadata=metadata or {},
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        self.templates[prompt_template.template_id] = prompt_template
        return prompt_template

    def update_template(
        self,
        template_id: str,
        template: Optional[str] = None,
        variables: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update an existing template."""
        if template_id not in self.templates:
            return False

        tmpl = self.templates[template_id]

        if template is not None:
            tmpl.template = template

        if variables is not None:
            tmpl.variables = variables

        if metadata is not None:
            tmpl.metadata.update(metadata)

        tmpl.updated_at = datetime.now()
        return True

    def render_template(
        self,
        template_id: str,
        variables: Dict[str, str]
    ) -> Optional[str]:
        """Render a template with the provided variables."""
        if template_id not in self.templates:
            return None

        template = self.templates[template_id]

        try:
            rendered = template.template.format(**variables)
            return rendered
        except KeyError as e:
            print(f"Missing variable in template: {e}")
            return None

    def execute_template(
        self,
        template_id: str,
        variables: Dict[str, str],
        quality_score: Optional[float] = None,
        token_count: int = 0
    ) -> Optional[PromptExecution]:
        """Execute a template and record the execution."""
        rendered = self.render_template(template_id, variables)
        if not rendered:
            return None

        execution = PromptExecution(
            template_id=template_id,
            rendered_prompt=rendered,
            variables_used=variables,
            executed_at=datetime.now(),
            quality_score=quality_score,
            token_count=token_count
        )

        self.executions.append(execution)

        # Update template usage statistics
        template = self.templates[template_id]
        template.usage_count += 1

        if quality_score is not None:
            # Update rolling average
            total_quality = template.average_quality * (template.usage_count - 1)
            template.average_quality = (total_quality + quality_score) / template.usage_count

        return execution

    def get_template(self, template_id: str) -> Optional[PromptTemplate]:
        """Get a template by ID."""
        return self.templates.get(template_id)

    def get_templates_by_category(
        self,
        category: PromptCategory
    ) -> List[PromptTemplate]:
        """Get all templates in a category."""
        return [
            t for t in self.templates.values()
            if t.category == category
        ]

    def get_best_template(
        self,
        category: PromptCategory,
        min_usage: int = 5
    ) -> Optional[PromptTemplate]:
        """
        Get the best-performing template in a category.

        Args:
            category: The category to search in
            min_usage: Minimum usage count to be considered

        Returns:
            The template with the highest average quality score
        """
        templates = [
            t for t in self.get_templates_by_category(category)
            if t.usage_count >= min_usage
        ]

        if not templates:
            return None

        return max(templates, key=lambda t: t.average_quality)

    def get_template_analytics(
        self,
        template_id: str
    ) -> Dict[str, Any]:
        """Get analytics for a specific template."""
        template = self.templates.get(template_id)
        if not template:
            return {"error": "Template not found"}

        executions = [
            e for e in self.executions
            if e.template_id == template_id
        ]

        quality_scores = [
            e.quality_score for e in executions
            if e.quality_score is not None
        ]

        return {
            "template_id": template_id,
            "name": template.name,
            "category": template.category.value,
            "total_executions": len(executions),
            "usage_count": template.usage_count,
            "average_quality": template.average_quality,
            "quality_scores": quality_scores,
            "token_usage": sum(e.token_count for e in executions),
            "last_used": max((e.executed_at for e in executions), default=None),
        }
