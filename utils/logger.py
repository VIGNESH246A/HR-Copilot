"""
Logging configuration and utilities
"""
import logging
import sys
from pathlib import Path
from datetime import datetime
from config import settings


def setup_logger(name: str = "hr_copilot") -> logging.Logger:
    """Setup logger with file and console handlers"""
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)
    
    # File handler
    if settings.LOG_FILE:
        log_path = Path(settings.LOG_FILE)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(settings.LOG_FILE)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
    
    return logger


def log_agent_action(
    logger: logging.Logger,
    agent_name: str,
    action: str,
    details: str = ""
):
    """Log agent action"""
    message = f"[{agent_name}] {action}"
    if details:
        message += f" - {details}"
    logger.info(message)


def log_error(
    logger: logging.Logger,
    error: Exception,
    context: str = ""
):
    """Log error with context"""
    message = f"Error: {str(error)}"
    if context:
        message = f"{context} - {message}"
    logger.error(message, exc_info=True)


def log_task_execution(
    logger: logging.Logger,
    task_id: str,
    task_type: str,
    status: str,
    duration: float = None
):
    """Log task execution"""
    message = f"Task {task_id} ({task_type}): {status}"
    if duration:
        message += f" - {duration:.2f}s"
    logger.info(message)


# Global logger instance
logger = setup_logger()