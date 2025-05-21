"""Prompt management module for the IDE."""
from typing import Dict, List, Optional, Any, Union, TypedDict
from dataclasses import dataclass
from datetime import datetime
import json
import os

@dataclass
class PromptTemplate:
    """Represents a prompt template."""
    name: str
    template: str
    description: str
    parameters: Dict[str, str]
    version: str
    last_modified: datetime

class TemplateMetadata(TypedDict):
    """Type definition for template metadata."""
    name: str
    description: str
    version: str
    last_modified: datetime

class PromptManager:
    """Manages prompt templates and their versions."""
    
    def __init__(self, template_dir: str) -> None:
        """Initialize the prompt manager.
        
        Args:
            template_dir: Directory containing prompt templates
        """
        self.template_dir = template_dir
        self.templates: Dict[str, PromptTemplate] = {}
        self._load_templates()
    
    def _load_templates(self) -> None:
        """Load all prompt templates from the template directory."""
        for filename in os.listdir(self.template_dir):
            if filename.endswith('.json'):
                with open(os.path.join(self.template_dir, filename), 'r') as f:
                    data = json.load(f)
                    template = PromptTemplate(
                        name=data['name'],
                        template=data['template'],
                        description=data['description'],
                        parameters=data['parameters'],
                        version=data['version'],
                        last_modified=datetime.fromisoformat(data['last_modified'])
                    )
                    self.templates[template.name] = template
    
    def get_template(self, name: str) -> Optional[PromptTemplate]:
        """Get a prompt template by name.
        
        Args:
            name: The name of the template
            
        Returns:
            The prompt template, or None if not found
        """
        return self.templates.get(name)
    
    def save_template(self, template: PromptTemplate) -> None:
        """Save a prompt template.
        
        Args:
            template: The template to save
        """
        self.templates[template.name] = template
        data: Dict[str, Union[str, Dict[str, str]]] = {
            'name': template.name,
            'template': template.template,
            'description': template.description,
            'parameters': template.parameters,
            'version': template.version,
            'last_modified': template.last_modified.isoformat()
        }
        with open(os.path.join(self.template_dir, f"{template.name}.json"), 'w') as f:
            json.dump(data, f, indent=2)
    
    def format_prompt(self, template_name: str, **kwargs: Any) -> Optional[str]:
        """Format a prompt using a template.
        
        Args:
            template_name: The name of the template to use
            **kwargs: Parameters to format the template with
            
        Returns:
            The formatted prompt, or None if template not found
        """
        template = self.get_template(template_name)
        if template is None:
            return None
        
        try:
            return template.template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing required parameter: {e}")
    
    def list_templates(self) -> List[TemplateMetadata]:
        """List all available templates.
        
        Returns:
            List of template metadata
        """
        return [
            {
                'name': template.name,
                'description': template.description,
                'version': template.version,
                'last_modified': template.last_modified
            }
            for template in self.templates.values()
        ] 