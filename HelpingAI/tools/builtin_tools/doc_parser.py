"""
Document Parser Tool for HelpingAI SDK

This tool provides document parsing capabilities for various file formats,
inspired by Qwen-Agent's DocParser tool.
"""

import os
from typing import Dict, Any, Optional

from .base import BuiltinToolBase
from ..errors import ToolExecutionError


class DocParserTool(BuiltinToolBase):
    """Document parsing tool for various file formats.
    
    This tool can parse text from various document formats including
    TXT, PDF, DOCX, and more.
    """
    
    name = "doc_parser"
    description = "Parse and extract text content from various document formats (TXT, PDF, DOCX, etc.)"
    parameters = {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path or URL to the document file to parse"
            },
            "max_length": {
                "type": "integer", 
                "description": "Maximum length of extracted text (default: 10000)",
                "default": 10000
            }
        },
        "required": ["file_path"]
    }
    
    def execute(self, **kwargs) -> str:
        """Parse a document and extract text content.
        
        Args:
            file_path: Path or URL to document
            max_length: Maximum text length to extract
            
        Returns:
            Extracted text content
        """
        self._validate_parameters(kwargs)
        file_path = kwargs['file_path']
        max_length = kwargs.get('max_length', 10000)
        
        try:
            # For now, implement basic text file reading
            # In a full implementation, this would support PDF, DOCX, etc.
            content = self._read_file(file_path)
            
            if len(content) > max_length:
                content = content[:max_length] + "...\n[Content truncated]"
            
            return f"Extracted text from {os.path.basename(file_path)}:\n\n{content}"
            
        except Exception as e:
            raise ToolExecutionError(
                f"Document parsing failed: {e}",
                tool_name=self.name,
                original_error=e
            )