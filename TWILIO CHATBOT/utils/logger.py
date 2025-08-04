"""
Logging Utilities
Centralized logging configuration and utilities
"""

import os
import logging
import logging.handlers
from datetime import datetime
from config.settings import LOGGING_SETTINGS

def setup_logger(name: str = "callbot", level: str = None) -> logging.Logger:
    """
    Set up and configure the logger
    
    Args:
        name (str): Logger name
        level (str): Logging level
        
    Returns:
        logging.Logger: Configured logger
    """
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(LOGGING_SETTINGS['file'])
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Get logger
    logger = logging.getLogger(name)
    
    # Set level
    log_level = level or LOGGING_SETTINGS.get('level', 'INFO')
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(LOGGING_SETTINGS.get('format'))
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler with rotation
    if LOGGING_SETTINGS.get('file'):
        file_handler = logging.handlers.RotatingFileHandler(
            LOGGING_SETTINGS['file'],
            maxBytes=LOGGING_SETTINGS.get('max_size', 10 * 1024 * 1024),  # 10MB
            backupCount=LOGGING_SETTINGS.get('backup_count', 5)
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger

def get_logger(name: str = None) -> logging.Logger:
    """
    Get a logger instance
    
    Args:
        name (str): Logger name
        
    Returns:
        logging.Logger: Logger instance
    """
    return logging.getLogger(name or "callbot")

def log_call_event(logger: logging.Logger, event_type: str, call_sid: str, **kwargs):
    """
    Log a call-related event
    
    Args:
        logger (logging.Logger): Logger instance
        event_type (str): Type of event
        call_sid (str): Twilio call SID
        **kwargs: Additional event data
    """
    event_data = {
        'timestamp': datetime.now().isoformat(),
        'event_type': event_type,
        'call_sid': call_sid,
        **kwargs
    }
    
    logger.info(f"Call Event: {event_type} - {call_sid}", extra=event_data)

def log_conversation_event(logger: logging.Logger, event_type: str, call_sid: str, **kwargs):
    """
    Log a conversation-related event
    
    Args:
        logger (logging.Logger): Logger instance
        event_type (str): Type of event
        call_sid (str): Twilio call SID
        **kwargs: Additional event data
    """
    event_data = {
        'timestamp': datetime.now().isoformat(),
        'event_type': event_type,
        'call_sid': call_sid,
        **kwargs
    }
    
    logger.info(f"Conversation Event: {event_type} - {call_sid}", extra=event_data)

def log_error(logger: logging.Logger, error: Exception, context: str = None, **kwargs):
    """
    Log an error with context
    
    Args:
        logger (logging.Logger): Logger instance
        error (Exception): The error that occurred
        context (str): Context where the error occurred
        **kwargs: Additional error data
    """
    error_data = {
        'timestamp': datetime.now().isoformat(),
        'error_type': type(error).__name__,
        'error_message': str(error),
        'context': context,
        **kwargs
    }
    
    logger.error(f"Error in {context}: {str(error)}", extra=error_data, exc_info=True)

def log_performance(logger: logging.Logger, operation: str, duration: float, **kwargs):
    """
    Log performance metrics
    
    Args:
        logger (logging.Logger): Logger instance
        operation (str): Operation name
        duration (float): Duration in seconds
        **kwargs: Additional performance data
    """
    perf_data = {
        'timestamp': datetime.now().isoformat(),
        'operation': operation,
        'duration_seconds': duration,
        **kwargs
    }
    
    logger.info(f"Performance: {operation} took {duration:.3f}s", extra=perf_data)

def log_api_call(logger: logging.Logger, api_name: str, endpoint: str, status_code: int = None, **kwargs):
    """
    Log API call details
    
    Args:
        logger (logging.Logger): Logger instance
        api_name (str): Name of the API
        endpoint (str): API endpoint
        status_code (int): HTTP status code
        **kwargs: Additional API call data
    """
    api_data = {
        'timestamp': datetime.now().isoformat(),
        'api_name': api_name,
        'endpoint': endpoint,
        'status_code': status_code,
        **kwargs
    }
    
    status_text = f" ({status_code})" if status_code else ""
    logger.info(f"API Call: {api_name} - {endpoint}{status_text}", extra=api_data)

def create_structured_log(logger: logging.Logger, level: str, message: str, **kwargs):
    """
    Create a structured log entry
    
    Args:
        logger (logging.Logger): Logger instance
        level (str): Log level
        message (str): Log message
        **kwargs: Structured data
    """
    log_data = {
        'timestamp': datetime.now().isoformat(),
        'message': message,
        **kwargs
    }
    
    log_method = getattr(logger, level.lower(), logger.info)
    log_method(message, extra=log_data) 