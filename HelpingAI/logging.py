"""Custom logging system for HelpingAI SDK.

Provides structured logging with different levels and optional file output.
"""

import os
import sys
import datetime
from enum import Enum
from typing import Optional, TextIO, Any, Dict
from pathlib import Path


class LogLevel(Enum):
    """Log levels for the custom logging system."""
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4


class HAILogger:
    """Custom logger for HelpingAI SDK.
    
    Provides structured logging with console and optional file output.
    """
    
    def __init__(
        self, 
        name: str,
        level: LogLevel = LogLevel.WARNING,
        console_output: bool = True,
        file_path: Optional[str] = None,
        include_timestamp: bool = True,
        include_level: bool = True,
        include_name: bool = True
    ):
        """Initialize the HAI logger.
        
        Args:
            name: Logger name (usually module name)
            level: Minimum log level to output
            console_output: Whether to output to console
            file_path: Optional file path for log output
            include_timestamp: Whether to include timestamp in output
            include_level: Whether to include log level in output
            include_name: Whether to include logger name in output
        """
        self.name = name
        self.level = level
        self.console_output = console_output
        self.file_path = file_path
        self.include_timestamp = include_timestamp
        self.include_level = include_level
        self.include_name = include_name
        
        # Create file directory if needed
        if self.file_path:
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
    
    def _should_log(self, level: LogLevel) -> bool:
        """Check if message should be logged based on current log level."""
        return level.value >= self.level.value
    
    def _format_message(self, level: LogLevel, message: str, extra: Optional[Dict[str, Any]] = None) -> str:
        """Format log message with optional components.
        
        Args:
            level: Log level
            message: Message to log
            extra: Additional context data
            
        Returns:
            Formatted log message
        """
        parts = []
        
        # Add timestamp
        if self.include_timestamp:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            parts.append(f"[{timestamp}]")
        
        # Add log level
        if self.include_level:
            level_colors = {
                LogLevel.DEBUG: "\033[36m",    # Cyan
                LogLevel.INFO: "\033[32m",     # Green  
                LogLevel.WARNING: "\033[33m",  # Yellow
                LogLevel.ERROR: "\033[31m",    # Red
                LogLevel.CRITICAL: "\033[35m", # Magenta
            }
            reset_color = "\033[0m"
            
            # Use colors for console, plain text for file
            if self.console_output and sys.stdout.isatty():
                color = level_colors.get(level, "")
                parts.append(f"{color}{level.name:8}{reset_color}")
            else:
                parts.append(f"{level.name:8}")
        
        # Add logger name
        if self.include_name:
            parts.append(f"[{self.name}]")
        
        # Add main message
        parts.append(message)
        
        # Add extra context
        if extra:
            extra_parts = []
            for key, value in extra.items():
                extra_parts.append(f"{key}={value}")
            if extra_parts:
                parts.append(f"({', '.join(extra_parts)})")
        
        return " ".join(parts)
    
    def _write_log(self, level: LogLevel, message: str, extra: Optional[Dict[str, Any]] = None):
        """Write log message to configured outputs.
        
        Args:
            level: Log level
            message: Message to log
            extra: Additional context data
        """
        if not self._should_log(level):
            return
        
        formatted_message = self._format_message(level, message, extra)
        
        # Write to console
        if self.console_output:
            output_stream = sys.stderr if level.value >= LogLevel.ERROR.value else sys.stdout
            print(formatted_message, file=output_stream, flush=True)
        
        # Write to file
        if self.file_path:
            try:
                with open(self.file_path, 'a', encoding='utf-8') as f:
                    # Remove ANSI color codes for file output
                    import re
                    clean_message = re.sub(r'\033\[[0-9;]*m', '', formatted_message)
                    f.write(clean_message + '\n')
                    f.flush()
            except Exception as e:
                # Fallback to stderr if file writing fails
                print(f"Failed to write to log file {self.file_path}: {e}", file=sys.stderr)
    
    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self._write_log(LogLevel.DEBUG, message, kwargs if kwargs else None)
    
    def info(self, message: str, **kwargs):
        """Log info message.""" 
        self._write_log(LogLevel.INFO, message, kwargs if kwargs else None)
    
    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self._write_log(LogLevel.WARNING, message, kwargs if kwargs else None)
    
    def error(self, message: str, exc_info: bool = False, **kwargs):
        """Log error message.
        
        Args:
            message: Error message
            exc_info: Whether to include exception traceback
            **kwargs: Additional context
        """
        if exc_info:
            import traceback
            tb = traceback.format_exc()
            message = f"{message}\nTraceback:\n{tb}"
        
        self._write_log(LogLevel.ERROR, message, kwargs if kwargs else None)
    
    def critical(self, message: str, exc_info: bool = False, **kwargs):
        """Log critical message.
        
        Args:
            message: Critical message
            exc_info: Whether to include exception traceback
            **kwargs: Additional context
        """
        if exc_info:
            import traceback
            tb = traceback.format_exc()
            message = f"{message}\nTraceback:\n{tb}"
        
        self._write_log(LogLevel.CRITICAL, message, kwargs if kwargs else None)
    
    def set_level(self, level: LogLevel):
        """Set the minimum log level."""
        self.level = level
    
    def set_console_output(self, enabled: bool):
        """Enable or disable console output."""
        self.console_output = enabled
    
    def set_file_output(self, file_path: Optional[str]):
        """Set file output path."""
        self.file_path = file_path
        if self.file_path:
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)


class LoggerManager:
    """Manages multiple loggers with shared configuration."""
    
    _loggers: Dict[str, HAILogger] = {}
    _default_level: LogLevel = LogLevel.WARNING
    _default_console_output: bool = True
    _default_file_path: Optional[str] = None
    
    @classmethod
    def get_logger(cls, name: str) -> HAILogger:
        """Get or create a logger with the given name.
        
        Args:
            name: Logger name
            
        Returns:
            HAILogger instance
        """
        if name not in cls._loggers:
            cls._loggers[name] = HAILogger(
                name=name,
                level=cls._default_level,
                console_output=cls._default_console_output,
                file_path=cls._default_file_path
            )
        return cls._loggers[name]
    
    @classmethod
    def set_global_level(cls, level: LogLevel):
        """Set log level for all loggers."""
        cls._default_level = level
        for logger in cls._loggers.values():
            logger.set_level(level)
    
    @classmethod
    def set_global_console_output(cls, enabled: bool):
        """Enable/disable console output for all loggers."""
        cls._default_console_output = enabled
        for logger in cls._loggers.values():
            logger.set_console_output(enabled)
    
    @classmethod
    def set_global_file_output(cls, file_path: Optional[str]):
        """Set file output for all loggers."""
        cls._default_file_path = file_path
        for logger in cls._loggers.values():
            logger.set_file_output(file_path)
    
    @classmethod
    def configure_from_env(cls):
        """Configure logging from environment variables.
        
        Environment variables:
        - HAI_LOG_LEVEL: debug, info, warning, error, critical
        - HAI_LOG_FILE: path to log file
        - HAI_LOG_CONSOLE: true/false for console output
        """
        # Set log level from environment
        env_level = os.getenv('HAI_LOG_LEVEL', '').lower()
        level_map = {
            'debug': LogLevel.DEBUG,
            'info': LogLevel.INFO, 
            'warning': LogLevel.WARNING,
            'error': LogLevel.ERROR,
            'critical': LogLevel.CRITICAL
        }
        if env_level in level_map:
            cls.set_global_level(level_map[env_level])
        
        # Set file output from environment
        env_file = os.getenv('HAI_LOG_FILE')
        if env_file:
            cls.set_global_file_output(env_file)
        
        # Set console output from environment
        env_console = os.getenv('HAI_LOG_CONSOLE', 'true').lower()
        if env_console in ('false', '0', 'no', 'off'):
            cls.set_global_console_output(False)


# Initialize from environment variables on import
LoggerManager.configure_from_env()


def get_logger(name: str) -> HAILogger:
    """Get a logger instance.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        HAILogger instance
    """
    return LoggerManager.get_logger(name)