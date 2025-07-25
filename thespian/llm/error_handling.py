"""
Enhanced error handling and logging for the Thespian framework.

This module provides centralized error handling, logging, and monitoring
capabilities for better reliability and debugging.
"""

import logging
import traceback
import time
import functools
from typing import Any, Callable, Dict, Optional, TypeVar, Union
from datetime import datetime
from enum import Enum

F = TypeVar('F', bound=Callable[..., Any])


class ThespianError(Exception):
    """Base exception for Thespian framework errors."""
    
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.context = context or {}
        self.timestamp = datetime.now()


class PlaywrightError(ThespianError):
    """Exceptions specific to playwright operations."""
    pass


class MemoryError(ThespianError):
    """Exceptions specific to memory operations."""
    pass


class QualityControlError(ThespianError):
    """Exceptions specific to quality control operations."""
    pass


class ErrorSeverity(str, Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorHandler:
    """Centralized error handling and logging."""
    
    def __init__(self, logger_name: str = "thespian"):
        self.logger = logging.getLogger(logger_name)
        self.error_counts = {}
        self.last_errors = []
        self.max_recent_errors = 10
        
    def log_error(self, error: Exception, context: Optional[Dict[str, Any]] = None,
                  severity: ErrorSeverity = ErrorSeverity.MEDIUM) -> None:
        """Log an error with context and severity."""
        error_type = type(error).__name__
        error_msg = str(error)
        
        # Track error frequency
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        
        # Store recent errors
        error_info = {
            "type": error_type,
            "message": error_msg,
            "context": context or {},
            "severity": severity,
            "timestamp": datetime.now(),
            "traceback": traceback.format_exc() if self.logger.isEnabledFor(logging.DEBUG) else None
        }
        
        self.last_errors.append(error_info)
        if len(self.last_errors) > self.max_recent_errors:
            self.last_errors.pop(0)
            
        # Log based on severity
        if severity == ErrorSeverity.CRITICAL:
            self.logger.critical(f"{error_type}: {error_msg}", extra={"context": context})
        elif severity == ErrorSeverity.HIGH:
            self.logger.error(f"{error_type}: {error_msg}", extra={"context": context})
        elif severity == ErrorSeverity.MEDIUM:
            self.logger.warning(f"{error_type}: {error_msg}", extra={"context": context})
        else:
            self.logger.info(f"{error_type}: {error_msg}", extra={"context": context})
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of recent errors."""
        return {
            "error_counts": self.error_counts.copy(),
            "recent_errors": self.last_errors.copy(),
            "total_errors": sum(self.error_counts.values())
        }


def with_error_handling(
    error_handler: Optional[ErrorHandler] = None,
    reraise: bool = True,
    default_return: Any = None,
    severity: ErrorSeverity = ErrorSeverity.MEDIUM
) -> Callable[[F], F]:
    """Decorator to add error handling to functions.
    
    Args:
        error_handler: ErrorHandler instance to use
        reraise: Whether to reraise the exception after logging
        default_return: Value to return if exception occurs and reraise=False
        severity: Error severity level
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Get context from function args if possible
                context = {
                    "function": func.__name__,
                    "args_count": len(args),
                    "kwargs_keys": list(kwargs.keys()) if kwargs else []
                }
                
                # Add specific context for known objects
                for i, arg in enumerate(args):
                    if hasattr(arg, '__class__') and hasattr(arg.__class__, '__name__'):
                        context[f"arg_{i}_type"] = arg.__class__.__name__
                
                if error_handler:
                    error_handler.log_error(e, context, severity)
                else:
                    # Fallback logging
                    logging.getLogger("thespian").error(f"Error in {func.__name__}: {e}")
                
                if reraise:
                    raise
                return default_return
        return wrapper
    return decorator


def with_timeout_and_retry(
    timeout_seconds: int = 30,
    max_retries: int = 3,
    backoff_factor: float = 1.5,
    error_handler: Optional[ErrorHandler] = None
) -> Callable[[F], F]:
    """Decorator to add timeout and retry logic to functions.
    
    Args:
        timeout_seconds: Maximum time to wait for function completion
        max_retries: Maximum number of retry attempts
        backoff_factor: Factor to multiply wait time between retries
        error_handler: ErrorHandler instance for logging
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            wait_time = 1.0
            
            for attempt in range(max_retries + 1):
                try:
                    start_time = time.time()
                    result = func(*args, **kwargs)
                    elapsed = time.time() - start_time
                    
                    # Check timeout
                    if elapsed > timeout_seconds:
                        raise TimeoutError(f"Function {func.__name__} exceeded timeout of {timeout_seconds}s")
                    
                    if attempt > 0 and error_handler:
                        error_handler.logger.info(f"Function {func.__name__} succeeded on attempt {attempt + 1}")
                    
                    return result
                    
                except Exception as e:
                    last_exception = e
                    
                    if error_handler:
                        context = {
                            "function": func.__name__,
                            "attempt": attempt + 1,
                            "max_retries": max_retries,
                            "elapsed_time": time.time() - start_time if 'start_time' in locals() else 0
                        }
                        error_handler.log_error(e, context, ErrorSeverity.MEDIUM)
                    
                    # Don't retry on the last attempt
                    if attempt < max_retries:
                        if error_handler:
                            error_handler.logger.info(f"Retrying {func.__name__} in {wait_time:.1f}s (attempt {attempt + 1}/{max_retries})")
                        time.sleep(wait_time)
                        wait_time *= backoff_factor
                    
            # All retries exhausted
            if error_handler:
                error_handler.log_error(
                    Exception(f"Function {func.__name__} failed after {max_retries + 1} attempts"),
                    {"last_exception": str(last_exception)},
                    ErrorSeverity.HIGH
                )
            
            raise last_exception
            
        return wrapper
    return decorator


# Global error handler instance
global_error_handler = ErrorHandler("thespian.global")


def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None) -> None:
    """Setup centralized logging configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for log output
    """
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Setup root logger
    root_logger = logging.getLogger("thespian")
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Add console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Add file handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    root_logger.info(f"Logging setup complete - Level: {log_level}, File: {log_file or 'Console only'}")