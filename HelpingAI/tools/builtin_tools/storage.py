"""
Storage Tool for HelpingAI SDK

This tool provides file storage and management capabilities,
inspired by Qwen-Agent's Storage tool.
"""

import os
import shutil
from typing import Dict, Any, Optional

from .base import BuiltinToolBase
from ..errors import ToolExecutionError


class StorageTool(BuiltinToolBase):
    """File storage and management tool.
    
    This tool provides capabilities for storing, retrieving, and managing
    files in a designated storage area.
    """
    
    name = "storage"
    description = "Store, retrieve, and manage files in a designated storage area"
    parameters = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "description": "Action to perform: 'store', 'retrieve', 'list', 'delete'",
                "enum": ["store", "retrieve", "list", "delete"]
            },
            "filename": {
                "type": "string",
                "description": "Name of the file (required for store, retrieve, delete)"
            },
            "content": {
                "type": "string",
                "description": "File content (required for store action)"
            }
        },
        "required": ["action"]
    }
    
    def execute(self, **kwargs) -> str:
        """Perform storage operations.
        
        Args:
            action: Storage action to perform
            filename: File name (if applicable)
            content: File content (for store action)
            
        Returns:
            Result of the storage operation
        """
        self._validate_parameters(kwargs)
        action = kwargs['action']
        filename = kwargs.get('filename')
        content = kwargs.get('content')
        
        try:
            if action == "store":
                if not filename or not content:
                    raise ValueError("Both filename and content are required for store action")
                return self._store_file(filename, content)
            
            elif action == "retrieve":
                if not filename:
                    raise ValueError("Filename is required for retrieve action")
                return self._retrieve_file(filename)
            
            elif action == "list":
                return self._list_files()
            
            elif action == "delete":
                if not filename:
                    raise ValueError("Filename is required for delete action")
                return self._delete_file(filename)
            
            else:
                raise ValueError(f"Unknown action: {action}")
                
        except Exception as e:
            raise ToolExecutionError(
                f"Storage operation failed: {e}",
                tool_name=self.name,
                original_error=e
            )
    
    def _store_file(self, filename: str, content: str) -> str:
        """Store content in a file.
        
        Args:
            filename: Name of the file
            content: Content to store
            
        Returns:
            Success message
        """
        file_path = self._write_file(content, filename)
        return f"File '{filename}' stored successfully at {file_path}"
    
    def _retrieve_file(self, filename: str) -> str:
        """Retrieve content from a file.
        
        Args:
            filename: Name of the file
            
        Returns:
            File content
        """
        file_path = os.path.join(self.work_dir, filename)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File '{filename}' not found in storage")
        
        content = self._read_file(file_path)
        return f"Content of '{filename}':\n\n{content}"
    
    def _list_files(self) -> str:
        """List all files in storage.
        
        Returns:
            List of stored files
        """
        if not os.path.exists(self.work_dir):
            return "Storage directory is empty."
        
        files = [f for f in os.listdir(self.work_dir) if os.path.isfile(os.path.join(self.work_dir, f))]
        
        if not files:
            return "No files found in storage."
        
        file_list = "\n".join(f"- {f}" for f in sorted(files))
        return f"Files in storage:\n{file_list}"
    
    def _delete_file(self, filename: str) -> str:
        """Delete a file from storage.
        
        Args:
            filename: Name of the file to delete
            
        Returns:
            Success message
        """
        file_path = os.path.join(self.work_dir, filename)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File '{filename}' not found in storage")
        
        os.remove(file_path)
        return f"File '{filename}' deleted successfully."