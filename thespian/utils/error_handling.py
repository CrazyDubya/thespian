"""
Error handling utilities for the Thespian framework.
"""

import json
import logging
from typing import Any, Dict, Optional, Callable
from functools import wraps
import time

logger = logging.getLogger(__name__)


def parse_llm_json_response(response: Any, fallback: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Safely parse JSON response from LLM.
    
    Args:
        response: The LLM response (could be string, object with content, etc.)
        fallback: Fallback dictionary if parsing fails
        
    Returns:
        Parsed dictionary or fallback
    """
    # Extract content from response object if needed
    if hasattr(response, 'content'):
        content = response.content
    elif hasattr(response, 'text'):
        content = response.text
    else:
        content = str(response)
    
    # Try to parse JSON
    try:
        # Sometimes LLMs wrap JSON in markdown code blocks
        if '```json' in content:
            start = content.find('```json') + 7
            end = content.find('```', start)
            content = content[start:end].strip()
        elif '```' in content:
            start = content.find('```') + 3
            end = content.find('```', start)
            content = content[start:end].strip()
        
        result = json.loads(content)
        if isinstance(result, dict):
            return result
        else:
            logger.warning(f"LLM response was not a dictionary: {type(result)}")
            return fallback or {"error": "Response was not a dictionary", "content": str(result)}
            
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM JSON response: {e}")
        logger.debug(f"Response content: {content[:500]}...")
        return fallback or {"error": "JSON parse error", "raw_content": content}
    except Exception as e:
        logger.error(f"Unexpected error parsing LLM response: {e}")
        return fallback or {"error": str(e), "raw_content": str(response)}


def with_retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    Decorator to retry function calls on failure.
    
    Args:
        max_attempts: Maximum number of attempts
        delay: Initial delay between attempts in seconds
        backoff: Multiplier for delay after each attempt
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_attempts} failed for {func.__name__}: {e}"
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(
                            f"All {max_attempts} attempts failed for {func.__name__}: {e}"
                        )
            
            raise last_exception
        
        return wrapper
    return decorator


def safe_llm_call(llm_func: Callable, prompt: str, fallback: Any = None) -> Any:
    """
    Safely call an LLM function with error handling.
    
    Args:
        llm_func: The LLM function to call
        prompt: The prompt to send
        fallback: Value to return if call fails
        
    Returns:
        LLM response or fallback value
    """
    try:
        return llm_func(prompt)
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        return fallback


def validate_scene_content(scene: str, min_length: int = 100) -> bool:
    """
    Validate that scene content meets basic requirements.
    
    Args:
        scene: The scene content
        min_length: Minimum acceptable length
        
    Returns:
        True if valid, False otherwise
    """
    if not scene or not isinstance(scene, str):
        logger.error("Scene content is empty or not a string")
        return False
    
    if len(scene.strip()) < min_length:
        logger.warning(f"Scene content too short: {len(scene.strip())} chars (min: {min_length})")
        return False
    
    # Check for basic dialogue structure
    if not any(marker in scene for marker in [':', '\n', 'SCENE', 'ACT']):
        logger.warning("Scene lacks basic theatrical structure markers")
        return False
    
    return True


def log_agent_error(agent_name: str, method_name: str, error: Exception, context: Dict[str, Any] = None):
    """
    Log errors from agent methods with context.
    
    Args:
        agent_name: Name of the agent
        method_name: Method that failed
        error: The exception that occurred
        context: Additional context information
    """
    error_info = {
        "agent": agent_name,
        "method": method_name,
        "error_type": type(error).__name__,
        "error_message": str(error),
        "context": context or {}
    }
    
    logger.error(f"Agent error: {json.dumps(error_info, indent=2)}")
    
    # Also log to a file for later analysis
    try:
        with open("agent_errors.log", "a") as f:
            f.write(f"{json.dumps(error_info)}\n")
    except:
        pass  # Don't fail if we can't write to log file