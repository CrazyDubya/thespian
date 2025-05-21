"""Scene processing and validation functionality."""

from typing import Dict, List, Optional, Any, Union, Tuple
import logging
import re
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ValidationError(Exception):
    """Custom exception for scene validation errors."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.details = details or {}

class SceneFormat(Enum):
    """Supported scene formats."""
    STANDARD = "standard"
    MODERN = "modern"
    EXPERIMENTAL = "experimental"

@dataclass
class ValidationResult:
    """Result of scene validation."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    details: Dict[str, Any]

class SceneProcessor:
    """Handles scene content processing and validation."""
    
    def __init__(
        self, 
        min_length: int = 2350, 
        max_length: int = 5000,
        format: SceneFormat = SceneFormat.STANDARD
    ) -> None:
        self.min_length: int = min_length
        self.max_length: int = max_length
        self.format: SceneFormat = format
        self._cache: Dict[str, Any] = {}
    
    def _strip_markdown(self, content: str) -> str:
        """Strip markdown formatting from content with improved handling."""
        # Remove bold/italic markers with better handling of nested formats
        content = re.sub(r'\*\*(.*?)\*\*', r'\1', content)
        content = re.sub(r'\*(.*?)\*', r'\1', content)
        
        # Remove headers with better handling of different levels
        content = re.sub(r'^#+\s+', '', content, flags=re.MULTILINE)
        
        # Remove code blocks with better handling of nested blocks
        content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
        content = re.sub(r'`(.*?)`', r'\1', content)
        
        # Remove links with better handling of complex URLs
        content = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', content)
        
        # Remove horizontal rules
        content = re.sub(r'^[-*_]{3,}$', '', content, flags=re.MULTILINE)
        
        # Remove blockquotes
        content = re.sub(r'^>\s+', '', content, flags=re.MULTILINE)
        
        return content.strip()
    
    def _validate_content_structure(self, content: str) -> Tuple[bool, List[str], List[str]]:
        """Validate the structure of scene content."""
        errors = []
        warnings = []
        
        lines = content.split("\n")
        has_character = False
        has_stage_direction = False
        has_technical_cue = False
        has_dialogue = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if line.isupper() and "(" not in line and "[" not in line:
                has_character = True
            elif line.startswith("(") and line.endswith(")"):
                has_stage_direction = True
            elif line.startswith("[") and line.endswith("]"):
                has_technical_cue = True
            elif not line.isupper() and not line.startswith(("(", "[")):
                has_dialogue = True
        
        if not has_character:
            errors.append("Scene content must include character names in ALL CAPS")
        if not has_stage_direction:
            errors.append("Scene content must include stage directions in (parentheses)")
        if not has_technical_cue:
            errors.append("Scene content must include technical cues in [brackets]")
        if not has_dialogue:
            errors.append("Scene content must include dialogue")
        
        return len(errors) == 0, errors, warnings
    
    def _validate_content_length(self, content: str) -> Tuple[bool, List[str], List[str]]:
        """Validate the length of scene content."""
        errors = []
        warnings = []
        
        if len(content) < self.min_length:
            errors.append(f"Scene content is too short ({len(content)} chars, minimum {self.min_length})")
        elif len(content) > self.max_length:
            errors.append(f"Scene content is too long ({len(content)} chars, maximum {self.max_length})")
        
        # Add warnings for content approaching limits
        if len(content) < self.min_length * 1.1:
            warnings.append("Scene content is approaching minimum length")
        elif len(content) > self.max_length * 0.9:
            warnings.append("Scene content is approaching maximum length")
        
        return len(errors) == 0, errors, warnings
    
    def _validate_content_format(self, content: str) -> Tuple[bool, List[str], List[str]]:
        """Validate the format of scene content."""
        errors = []
        warnings = []
        
        if "**" in content:
            errors.append("Scene content contains markdown formatting")
        
        if not any(char in content for char in [".", "!", "?"]):
            errors.append("Scene content must contain complete sentences")
        
        # Check for common formatting issues
        if re.search(r'\n{3,}', content):
            warnings.append("Scene contains multiple consecutive empty lines")
        
        if re.search(r' {2,}', content):
            warnings.append("Scene contains multiple consecutive spaces")
        
        return len(errors) == 0, errors, warnings
    
    def process_scene_content(self, response: Union[str, bytes, Any]) -> Dict[str, str]:
        """Process the generated scene content with improved validation."""
        try:
            # Validate response
            if response is None:
                raise ValidationError("Response cannot be None")
            
            # Convert response to string with validation
            try:
                if hasattr(response, 'content'):
                    content = str(response.content)
                elif isinstance(response, (str, bytes)):
                    content = str(response)
                else:
                    content = str(response)
            except Exception as e:
                raise ValidationError(f"Failed to convert response to string: {str(e)}")
            
            if not content.strip():
                raise ValidationError("Generated scene content is empty")
            
            # Check content length
            if len(content) > 100000:  # 100KB limit
                raise ValidationError("Generated scene content is too long")
            
            # Strip markdown formatting
            content = self._strip_markdown(content)
            
            # Initialize result dictionary
            result: Dict[str, str] = {
                "scene": "",
                "narrative_analysis": "",
                "raw_content": content
            }
            
            # Extract sections with flexible parsing
            sections: Dict[str, str] = {
                "SCENE CONTENT": "scene",
                "NARRATIVE ANALYSIS": "narrative_analysis"
            }
            
            current_section: Optional[str] = None
            current_content: List[str] = []
            
            # Split content into lines and process
            lines = content.split("\n")
            for i, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue
                    
                # Check for section headers
                found_section = False
                for header, field in sections.items():
                    if header.upper() in line.upper():
                        if current_section:
                            result[sections[current_section]] = "\n".join(current_content).strip()
                        current_section = header
                        current_content = []
                        found_section = True
                        break
                
                if not found_section and current_section:
                    current_content.append(line)
            
            # Add the last section
            if current_section and current_content:
                result[sections[current_section]] = "\n".join(current_content).strip()
            
            # Validate required sections
            missing_sections = [section for section, field in sections.items() 
                              if not result[field]]
            if missing_sections:
                # Try to recover by looking for content without headers
                if not result["scene"] and not result["narrative_analysis"]:
                    # If no sections found, assume first part is scene content
                    parts = content.split("\n\n", 1)
                    if len(parts) >= 2:
                        result["scene"] = parts[0].strip()
                        result["narrative_analysis"] = parts[1].strip()
                    else:
                        raise ValidationError(
                            f"Missing required sections: {', '.join(missing_sections)}",
                            {"missing_sections": missing_sections}
                        )
                else:
                    raise ValidationError(
                        f"Missing required sections: {', '.join(missing_sections)}",
                        {"missing_sections": missing_sections}
                    )
            
            # Perform comprehensive validation
            structure_valid, structure_errors, structure_warnings = self._validate_content_structure(result["scene"])
            length_valid, length_errors, length_warnings = self._validate_content_length(result["scene"])
            format_valid, format_errors, format_warnings = self._validate_content_format(result["scene"])
            
            # Combine all validation results
            all_errors = structure_errors + length_errors + format_errors
            all_warnings = structure_warnings + length_warnings + format_warnings
            
            if all_errors:
                raise ValidationError(
                    "Scene validation failed",
                    {
                        "errors": all_errors,
                        "warnings": all_warnings,
                        "scene_length": len(result["scene"]),
                        "narrative_length": len(result["narrative_analysis"])
                    }
                )
            
            # Log warnings if any
            if all_warnings:
                logger.warning(f"Scene validation warnings: {all_warnings}")
            
            return result
            
        except ValidationError as ve:
            logger.error(f"Validation error: {str(ve)}", extra=ve.details)
            raise
        except Exception as e:
            logger.error(f"Error processing scene content: {str(e)}", exc_info=True)
            raise ValidationError(f"Failed to process scene content: {str(e)}")
    
    def analyze_scene_structure(self, content: str) -> Dict[str, List[str]]:
        """Analyze scene structure with improved categorization."""
        lines = content.split("\n")
        dialogue_lines: List[str] = []
        stage_directions: List[str] = []
        technical_cues: List[str] = []
        character_entries: List[str] = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.isupper() and "(" not in line and "[" not in line:
                character_entries.append(line)
            elif line.startswith("(") and line.endswith(")"):
                stage_directions.append(line)
            elif line.startswith("[") and line.endswith("]"):
                technical_cues.append(line)
            elif not line.isupper() and not line.startswith(("(", "[")):
                dialogue_lines.append(line)
        
        return {
            "dialogue": dialogue_lines,
            "stage_directions": stage_directions,
            "technical_cues": technical_cues,
            "character_entries": character_entries
        }
    
    def validate_scene_length(self, content: str) -> ValidationResult:
        """Validate scene length with detailed feedback."""
        is_valid, errors, warnings = self._validate_content_length(content)
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            details={
                "length": len(content),
                "min_length": self.min_length,
                "max_length": self.max_length
            }
        ) 