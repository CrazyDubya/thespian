"""
Fix for story outline creation method signature mismatch.
"""

from typing import Dict, Any, List, Optional


def create_story_outline_wrapper(playwright_instance, premise: str, themes: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Wrapper to handle the signature mismatch between collaborative and base playwright.
    
    The base EnhancedPlaywright.create_story_outline expects (theme: str, requirements: Dict)
    but CollaborativePlaywright calls it with (premise: str, themes: List[str])
    """
    # Convert premise and themes to the expected format
    requirements = {
        'setting': 'Contemporary',
        'style': 'Drama',
        'period': 'Present',
        'target_audience': 'General',
        'themes': themes or []
    }
    
    # Use premise as the main theme
    return playwright_instance.create_story_outline(premise, requirements)


def patch_create_story_outline(playwright_class):
    """
    Monkey patch to fix the create_story_outline method.
    This should be applied to EnhancedPlaywright to make it compatible.
    """
    original_method = playwright_class.create_story_outline
    
    def flexible_create_story_outline(self, theme_or_premise: str, requirements_or_themes: Any = None) -> Dict[str, Any]:
        """
        Flexible version that handles both signatures:
        - create_story_outline(theme: str, requirements: Dict)
        - create_story_outline(premise: str, themes: List[str])
        """
        # Check if second parameter is a list (themes) or dict (requirements)
        if isinstance(requirements_or_themes, list):
            # Called with (premise, themes) signature
            requirements = {
                'setting': 'Contemporary',
                'style': 'Drama', 
                'period': 'Present',
                'target_audience': 'General',
                'themes': requirements_or_themes
            }
            theme = theme_or_premise
        elif isinstance(requirements_or_themes, dict):
            # Called with (theme, requirements) signature
            theme = theme_or_premise
            requirements = requirements_or_themes
        else:
            # No second parameter or None
            theme = theme_or_premise
            requirements = {
                'setting': 'Contemporary',
                'style': 'Drama',
                'period': 'Present', 
                'target_audience': 'General',
                'themes': []
            }
        
        # Call original method with proper signature
        return original_method(self, theme, requirements)
    
    # Replace the method
    playwright_class.create_story_outline = flexible_create_story_outline
    
    return playwright_class