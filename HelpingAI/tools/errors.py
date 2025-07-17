"""Error classes for HelpingAI tool utilities."""

from ..error import HAIError


class ToolExecutionError(HAIError):
    """Raised when tool execution fails."""
    
    def __init__(self, message: str, tool_name: str = None, original_error: Exception = None):
        super().__init__(message)
        self.tool_name = tool_name
        self.original_error = original_error


class SchemaValidationError(HAIError):
    """Raised when tool schema validation fails."""
    
    def __init__(self, message: str, schema: dict = None, value: any = None):
        super().__init__(message)
        self.schema = schema
        self.value = value


class ToolRegistrationError(HAIError):
    """Raised when tool registration fails."""
    
    def __init__(self, message: str, tool_name: str = None):
        super().__init__(message)
        self.tool_name = tool_name


class SchemaGenerationError(HAIError):
    """Raised when automatic schema generation fails."""
    
    def __init__(self, message: str, function_name: str = None, type_hint: any = None):
        super().__init__(message)
        self.function_name = function_name
        self.type_hint = type_hint