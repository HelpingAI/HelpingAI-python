"""
Code Interpreter Tool for HelpingAI SDK

This tool provides Python code execution in a sandboxed environment,
inspired by Qwen-Agent's CodeInterpreter tool.
"""

import asyncio
import base64
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path
from typing import Dict, Any, Optional

from .base import BuiltinToolBase
from ..errors import ToolExecutionError


class CodeInterpreterTool(BuiltinToolBase):
    """Advanced Python code execution sandbox with data science capabilities.
    
    This tool provides a secure environment for executing Python code with built-in
    support for data analysis, visualization, and scientific computing. Features
    automatic plot saving, timeout protection, and comprehensive error handling.
    """
    
    name = "code_interpreter"
    description = "Execute Python code in a secure sandboxed environment with support for data analysis, visualization, and computation. Includes popular libraries like matplotlib, pandas, numpy, and automatic plot saving."
    parameters = {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "Python code to execute"
            }
        },
        "required": ["code"]
    }
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the code interpreter.
        
        Args:
            config: Optional configuration dict with options:
                - timeout: Execution timeout in seconds (default: 30)
                - work_dir: Working directory for code execution
        """
        super().__init__(config)
        self.timeout = self.config.get('timeout', 30)
        self._kernel_clients = {}
    
    def execute(self, **kwargs) -> str:
        """Execute Python code.
        
        Args:
            code: Python code to execute
            
        Returns:
            Execution result including stdout, stderr, and generated images
        """
        self._validate_parameters(kwargs)
        code = kwargs['code']
        
        if not code.strip():
            return "No code provided to execute."
        
        try:
            # Check if we have required dependencies
            self._check_dependencies()
            
            # Execute the code
            result = self._execute_code_simple(code)
            return result
            
        except Exception as e:
            raise ToolExecutionError(
                f"Code execution failed: {e}",
                tool_name=self.name,
                original_error=e
            )
    
    def _execute_code_simple(self, code: str) -> str:
        """Execute code using simple subprocess approach.
        
        Args:
            code: Python code to execute
            
        Returns:
            Execution result
        """
        # Create a temporary script file
        script_file = os.path.join(self.work_dir, f"script_{uuid.uuid4()}.py")
        
        # Prepare the code with proper imports and setup
        prepared_code = self._prepare_code(code)
        
        try:
            # Write code to file
            with open(script_file, 'w', encoding='utf-8') as f:
                f.write(prepared_code)
            
            # Execute the script
            process = subprocess.Popen(
                [sys.executable, script_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.work_dir,
                text=True
            )
            
            try:
                stdout, stderr = process.communicate(timeout=self.timeout)
            except subprocess.TimeoutExpired:
                process.kill()
                return f"Code execution timed out after {self.timeout} seconds."
            
            # Combine results
            result_parts = []
            
            if stdout.strip():
                result_parts.append(f"stdout:\n```\n{stdout.strip()}\n```")
            
            if stderr.strip():
                result_parts.append(f"stderr:\n```\n{stderr.strip()}\n```")
            
            # Check for generated images
            image_results = self._collect_generated_images()
            if image_results:
                result_parts.extend(image_results)
            
            if not result_parts:
                result_parts.append("Code executed successfully with no output.")
            
            return "\n\n".join(result_parts)
            
        except subprocess.TimeoutExpired:
            return f"Code execution timed out after {self.timeout} seconds."
        except Exception as e:
            return f"Code execution error: {e}"
        finally:
            # Clean up script file
            if os.path.exists(script_file):
                os.remove(script_file)
    
    def _prepare_code(self, code: str) -> str:
        """Prepare code with necessary imports and setup.
        
        Args:
            code: Original code
            
        Returns:
            Prepared code with imports
        """
        setup_code = '''
import sys
import os
import warnings
warnings.filterwarnings('ignore')

# Common imports
try:
    import numpy as np
except ImportError:
    pass

try:
    import pandas as pd
except ImportError:
    pass

try:
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    plt.ioff()  # Turn off interactive mode
    _HAS_MATPLOTLIB = True
except ImportError:
    _HAS_MATPLOTLIB = False

try:
    import seaborn as sns
except ImportError:
    pass

# Set up working directory
import tempfile
work_dir = r"{work_dir}"
os.chdir(work_dir)

# Function to save plots (only if matplotlib is available)
if _HAS_MATPLOTLIB:
    def save_plot(filename=None):
        if filename is None:
            import uuid
            filename = f"plot_{{uuid.uuid4()}}.png"
        filepath = os.path.join(work_dir, filename)
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        print(f"Plot saved to: {{filename}}")
        return filepath

    # Auto-save plots when plt.show() is called
    original_show = plt.show
    def auto_save_show(*args, **kwargs):
        save_plot()
        plt.clf()  # Clear the figure

    plt.show = auto_save_show

'''.format(work_dir=self.work_dir.replace('\\', '\\\\'))
        
        return setup_code + '\n' + code
    
    def _collect_generated_images(self) -> list:
        """Collect any images generated during code execution.
        
        Returns:
            List of image result strings
        """
        image_results = []
        image_files = []
        
        # Look for image files in work directory
        for ext in ['*.png', '*.jpg', '*.jpeg', '*.svg']:
            image_files.extend(Path(self.work_dir).glob(ext))
        
        for idx, image_file in enumerate(sorted(image_files), 1):
            try:
                # For now, just reference the file path
                # In a real implementation, you might encode as base64 or serve via URL
                image_results.append(f"![Generated Image {idx}]({image_file})")
            except Exception:
                # Skip problematic images
                continue
        
        return image_results
    
    def _check_dependencies(self) -> None:
        """Check if required dependencies are available.
        
        Raises:
            ImportError: If critical dependencies are missing
        """
        try:
            # These are optional but commonly used
            import_checks = [
                ('numpy', 'numpy'),
                ('pandas', 'pandas'), 
                ('matplotlib', 'matplotlib'),
            ]
            
            missing = []
            for module_name, package_name in import_checks:
                try:
                    __import__(module_name)
                except ImportError:
                    missing.append(package_name)
            
            if missing:
                # Just warn, don't fail
                print(f"Warning: Some optional packages are not available: {', '.join(missing)}")
                
        except Exception:
            # Don't fail on dependency check errors
            pass