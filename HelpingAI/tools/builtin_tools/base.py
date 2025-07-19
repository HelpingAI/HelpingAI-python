"""
Base class for built-in tools inspired by Qwen-Agent.

This module provides the base infrastructure for implementing built-in tools
that are compatible with the HelpingAI tools framework.
"""

import os
import tempfile
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Union, Optional
from urllib.parse import urlparse
from urllib.request import urlopen

from ..core import Fn
from ..errors import ToolExecutionError


class BuiltinToolBase(ABC):
    """Base class for built-in tools.
    
    This class provides common functionality for built-in tools including
    file handling, parameter validation, and integration with HelpingAI's tool framework.
    """
    
    # To be overridden by subclasses
    name: str = ""
    description: str = ""
    parameters: Dict[str, Any] = {}
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the built-in tool.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        
        # Set up working directory
        default_work_dir = os.path.join(tempfile.gettempdir(), 'helpingai_tools', self.name)
        self.work_dir = self.config.get('work_dir', default_work_dir)
        os.makedirs(self.work_dir, exist_ok=True)
        
        if not self.name:
            raise ValueError(f"Tool class {self.__class__.__name__} must define a 'name' attribute")
        
        if not self.description:
            raise ValueError(f"Tool class {self.__class__.__name__} must define a 'description' attribute")
    
    @abstractmethod
    def execute(self, **kwargs) -> str:
        """Execute the tool with given parameters.
        
        Args:
            **kwargs: Tool parameters
            
        Returns:
            Tool execution result as string
            
        Raises:
            ToolExecutionError: If execution fails
        """
        raise NotImplementedError
    
    def to_fn(self) -> Fn:
        """Convert this built-in tool to an Fn object.
        
        Returns:
            Fn object that can be used with HelpingAI's tool framework
        """
        def tool_function(**kwargs) -> str:
            """Wrapper function for tool execution."""
            try:
                return self.execute(**kwargs)
            except Exception as e:
                raise ToolExecutionError(
                    f"Failed to execute built-in tool '{self.name}': {e}",
                    tool_name=self.name,
                    original_error=e
                )
        
        return Fn(
            name=self.name,
            description=self.description,
            parameters=self.parameters,
            function=tool_function
        )
    
    def _validate_parameters(self, params: Dict[str, Any]) -> None:
        """Validate tool parameters against schema.
        
        Args:
            params: Parameters to validate
            
        Raises:
            ValueError: If validation fails
        """
        # Check required parameters
        required_params = self.parameters.get('required', [])
        for param in required_params:
            if param not in params:
                raise ValueError(f"Missing required parameter '{param}' for tool '{self.name}'")
        
        # Check for unknown parameters
        allowed_params = set(self.parameters.get('properties', {}).keys())
        provided_params = set(params.keys())
        unknown_params = provided_params - allowed_params
        
        if unknown_params:
            raise ValueError(f"Unknown parameters for tool '{self.name}': {', '.join(unknown_params)}")
    
    def _download_file(self, url: str, filename: str = None) -> str:
        """Download a file from URL to working directory.
        
        Args:
            url: URL to download from
            filename: Optional filename, will be inferred from URL if not provided
            
        Returns:
            Path to downloaded file
            
        Raises:
            ToolExecutionError: If download fails
        """
        try:
            if not filename:
                parsed_url = urlparse(url)
                filename = os.path.basename(parsed_url.path) or 'downloaded_file'
            
            file_path = os.path.join(self.work_dir, filename)
            
            with urlopen(url) as response:
                with open(file_path, 'wb') as f:
                    f.write(response.read())
            
            return file_path
            
        except Exception as e:
            raise ToolExecutionError(
                f"Failed to download file from {url}: {e}",
                tool_name=self.name,
                original_error=e
            )
    
    def _read_file(self, file_path: str) -> str:
        """Read file content as text.
        
        Args:
            file_path: Path to file
            
        Returns:
            File content as string
            
        Raises:
            ToolExecutionError: If reading fails
        """
        try:
            if file_path.startswith(('http://', 'https://')):
                # Download the file first
                local_path = self._download_file(file_path)
                file_path = local_path
            
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
                
        except Exception as e:
            raise ToolExecutionError(
                f"Failed to read file {file_path}: {e}",
                tool_name=self.name,
                original_error=e
            )
    
    def _write_file(self, content: str, filename: str) -> str:
        """Write content to file in working directory.
        
        Args:
            content: Content to write
            filename: Filename
            
        Returns:
            Path to written file
            
        Raises:
            ToolExecutionError: If writing fails
        """
        try:
            file_path = os.path.join(self.work_dir, filename)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return file_path
            
        except Exception as e:
            raise ToolExecutionError(
                f"Failed to write file {filename}: {e}",
                tool_name=self.name,
                original_error=e
            )
    
    def _cleanup_work_dir(self) -> None:
        """Clean up the working directory."""
        try:
            import shutil
            if os.path.exists(self.work_dir):
                shutil.rmtree(self.work_dir)
        except Exception:
            # Ignore cleanup errors
            pass