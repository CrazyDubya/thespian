"""
Utility functions for theatrical advisors.

This module provides shared utilities used by various advisor types
to reduce code duplication and improve maintainability.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import re


def extract_key_phrases(text: str, max_phrases: int = 10) -> List[str]:
    """
    Extract key phrases from text for analysis.
    
    Args:
        text: The text to analyze
        max_phrases: Maximum number of phrases to extract
        
    Returns:
        List of key phrases
    """
    # Simple extraction based on capitalized phrases
    phrases = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
    return list(set(phrases))[:max_phrases]


def calculate_feedback_score(
    metrics: Dict[str, float],
    weights: Optional[Dict[str, float]] = None
) -> float:
    """
    Calculate weighted feedback score from multiple metrics.
    
    Args:
        metrics: Dictionary of metric names to values (0.0-1.0)
        weights: Optional weights for each metric (defaults to equal weights)
        
    Returns:
        Weighted score between 0.0 and 1.0
    """
    if not metrics:
        return 0.0
        
    if weights is None:
        weights = {key: 1.0 for key in metrics.keys()}
    
    total_weight = sum(weights.values())
    if total_weight == 0:
        return 0.0
    
    weighted_sum = sum(metrics[key] * weights.get(key, 1.0) for key in metrics.keys())
    return min(1.0, max(0.0, weighted_sum / total_weight))


def prioritize_suggestions(
    suggestions: List[str],
    importance_keywords: List[str] = None
) -> List[str]:
    """
    Prioritize suggestions based on importance keywords.
    
    Args:
        suggestions: List of suggestion strings
        importance_keywords: Keywords that indicate high importance
        
    Returns:
        Sorted list with high-priority suggestions first
    """
    if importance_keywords is None:
        importance_keywords = [
            'critical', 'essential', 'must', 'important',
            'major', 'significant', 'crucial'
        ]
    
    def get_priority(suggestion: str) -> int:
        """Calculate priority score for a suggestion."""
        suggestion_lower = suggestion.lower()
        return sum(1 for keyword in importance_keywords if keyword in suggestion_lower)
    
    return sorted(suggestions, key=get_priority, reverse=True)


def format_advisor_response(
    score: float,
    feedback: str,
    suggestions: List[str],
    examples: List[str],
    priority: int = 3
) -> Dict[str, Any]:
    """
    Format advisor response in standard structure.
    
    Args:
        score: Quality score (0.0-1.0)
        feedback: General feedback text
        suggestions: List of actionable suggestions
        examples: Specific examples from content
        priority: Priority level (1-5, 1 being highest)
        
    Returns:
        Formatted response dictionary
    """
    return {
        'score': max(0.0, min(1.0, score)),
        'feedback': feedback,
        'suggestions': prioritize_suggestions(suggestions),
        'specific_examples': examples[:5],  # Limit to top 5
        'priority': max(1, min(5, priority))
    }


def validate_content_length(
    content: str,
    min_length: int = 50,
    max_length: int = 50000
) -> tuple[bool, Optional[str]]:
    """
    Validate content length for analysis.
    
    Args:
        content: Content to validate
        min_length: Minimum acceptable length
        max_length: Maximum acceptable length
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    length = len(content)
    
    if length < min_length:
        return False, f"Content too short ({length} chars, minimum {min_length})"
    
    if length > max_length:
        return False, f"Content too long ({length} chars, maximum {max_length})"
    
    return True, None


class AdvisorMetrics(BaseModel):
    """
    Standard metrics tracked by advisors.
    """
    clarity_score: float = Field(ge=0.0, le=1.0)
    coherence_score: float = Field(ge=0.0, le=1.0)
    engagement_score: float = Field(ge=0.0, le=1.0)
    technical_score: float = Field(ge=0.0, le=1.0)
    
    def overall_score(self, weights: Optional[Dict[str, float]] = None) -> float:
        """Calculate weighted overall score."""
        metrics = {
            'clarity': self.clarity_score,
            'coherence': self.coherence_score,
            'engagement': self.engagement_score,
            'technical': self.technical_score
        }
        return calculate_feedback_score(metrics, weights)
