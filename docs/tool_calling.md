# Tool Calling Guide

This guide provides a comprehensive overview of the tool calling capabilities of the HelpingAI Python SDK.

## Introduction

Tool calling allows you to extend the capabilities of the HelpingAI models by giving them access to external tools and functions. You can define custom tools, and the model will intelligently decide when to use them to answer user queries.

## Built-in Tools

The HelpingAI SDK comes with powerful built-in tools that provide essential capabilities out of the box. These tools are professionally developed, thoroughly tested, and ready to use without any setup or configuration.

### Available Built-in Tools

The SDK currently includes two sophisticated built-in tools:

- **`code_interpreter`**: Advanced Python code execution sandbox with data science capabilities
- **`web_search`**: Real-time web search using advanced search APIs

### Built-in Tools Overview

Built-in tools are designed to be:

- **Zero-configuration**: Ready to use immediately with sensible defaults
- **Secure**: Execute in sandboxed environments with proper isolation
- **Reliable**: Professional-grade implementations with comprehensive error handling
- **Compatible**: Work seamlessly with all tool calling patterns and workflows

### Using Built-in Tools

Built-in tools can be included in your tool configurations using simple string identifiers:

```python
from HelpingAI import HAI

client = HAI()

# Include built-in tools in chat completions
response = client.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[{"role": "user", "content": "Calculate the fibonacci sequence and search for recent AI news"}],
    tools=[
        "code_interpreter",  # Built-in Python execution
        "web_search"         # Built-in web search
    ]
)
```

### Code Interpreter Tool

The **code interpreter** provides a secure Python execution environment with comprehensive data science capabilities:

**Key Features:**
- **Secure Sandbox**: Isolated execution environment with timeout protection
- **Data Science Libraries**: Pre-configured with numpy, pandas, matplotlib, seaborn
- **Automatic Plot Handling**: Saves and references generated visualizations
- **Comprehensive Output**: Captures stdout, stderr, and generated files
- **Error Recovery**: Robust error handling with detailed diagnostics

**Use Cases:**
- Mathematical calculations and analysis
- Data processing and visualization
- Algorithm implementation and testing
- Scientific computing tasks
- Educational programming examples

**Example Usage:**

```python
# Using code interpreter for data analysis
response = client.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[{
        "role": "user",
        "content": "Create a bar chart showing population growth over decades"
    }],
    tools=["code_interpreter"]
)

# The model will automatically generate and execute Python code like:
# import matplotlib.pyplot as plt
# years = [1990, 2000, 2010, 2020]
# population = [5.3, 6.1, 6.9, 7.8]
# plt.bar(years, population)
# plt.title('Population Growth Over Decades')
# plt.show()  # Automatically saved as image
```

**Configuration Options:**

```python
# Direct tool calling with custom configuration
result = client.call("code_interpreter", {
    "code": """
import numpy as np
import matplotlib.pyplot as plt

# Generate sample data
x = np.linspace(0, 10, 100)
y = np.sin(x)

# Create plot
plt.figure(figsize=(10, 6))
plt.plot(x, y, 'b-', linewidth=2)
plt.title('Sine Wave')
plt.xlabel('X values')
plt.ylabel('Y values')
plt.grid(True)
plt.show()
"""
})
```

### Web Search Tool

The **web search** tool provides real-time access to current information from the web using advanced search APIs:

**Key Features:**
- **Real-time Results**: Access to current web information
- **Comprehensive Data**: Titles, snippets, URLs, and source information
- **Configurable Results**: Control number of results returned (1-10)
- **Quality Filtering**: Advanced algorithms for relevant, high-quality results
- **Structured Output**: Well-formatted results with metadata

**Use Cases:**
- Current events and news research
- Fact-checking and verification
- Market research and trends
- Technical documentation lookup
- Real-time data gathering

**Example Usage:**

```python
# Using web search for current information
response = client.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[{
        "role": "user",
        "content": "What are the latest developments in AI safety research?"
    }],
    tools=["web_search"]
)

# Direct tool calling with parameters
search_results = client.call("web_search", {
    "query": "latest AI safety research 2024",
    "max_results": 5
})
```

**Search Result Format:**

```python
# Example search result structure
{
    "results": [
        {
            "title": "Recent Advances in AI Safety Research",
            "snippet": "Overview of latest developments in AI alignment and safety...",
            "url": "https://example.com/ai-safety-research",
            "source": "AI Research Institute",
            "position": 1
        }
        # ... more results
    ]
}
```

## Defining Tools

The HelpingAI SDK offers flexible ways to define tools, allowing you to integrate external functionalities seamlessly with your AI models. You can choose the method that best suits your needs:

1.  **`@tools` decorator**: The most straightforward way to define a tool directly from a Python function.
2.  **`Fn` class**: Provides a programmatic approach for creating tool definitions, especially useful for tools that don't map directly to a single Python function or require dynamic creation.
3.  **OpenAI JSON schema**: For direct compatibility with existing tool definitions in the OpenAI format.

### Method 1: The `@tools` Decorator

The `@tools` decorator simplifies tool definition by automatically generating the necessary JSON schema from your Python function's signature and docstring. This means you can define a tool just like a regular Python function, and the SDK handles the conversion for the AI model.

**How it works:**

-   **Function Signature**: The decorator inspects the function's parameters and their type hints to infer the data types for the tool's input schema.
-   **Docstring**: The function's docstring is used to provide the `description` for the tool. For parameters, the decorator attempts to extract descriptions from the docstring (supporting Google, Sphinx, and NumPy style docstrings).
-   **Return Type**: While the return type hint is not directly used in the tool's schema, it's good practice to include it for code clarity.
-   **Automatic Registration**: Tools are automatically registered in the global registry and can be retrieved using [`get_tools()`](HelpingAI/tools/core.py:193).

**Basic Examples:**

```python
from HelpingAI.tools import tools
from typing import Literal, Optional, Union
import json

@tools
def get_weather(
    city: str,
    unit: Literal["celsius", "fahrenheit"] = "celsius"
) -> dict:
    """Get the current weather in a given city.

    Args:
        city (str): The name of the city for which to retrieve weather information.
        unit (Literal["celsius", "fahrenheit"], optional): The unit of temperature to use.
            Defaults to "celsius". Can be "celsius" or "fahrenheit".

    Returns:
        dict: A dictionary containing the city, temperature, and unit.
    """
    # In a real application, this would call an external weather API
    if city.lower() == "paris":
        temperature = 22 if unit == "celsius" else 71.6
    elif city.lower() == "london":
        temperature = 15 if unit == "celsius" else 59.0
    else:
        temperature = "N/A"
        
    print(f"[Tool Call] get_weather(city='{city}', unit='{unit}')")
    return {"city": city, "temperature": temperature, "unit": unit}

@tools
def send_email(recipient: str, subject: str, body: str, attachment_paths: list[str] = None):
    """Sends an email to the specified recipient.

    Args:
        recipient (str): The email address of the recipient.
        subject (str): The subject line of the email.
        body (str): The main content of the email.
        attachment_paths (list[str], optional): A list of file paths to attach to the email.
            Defaults to None.
    """
    print(f"[Tool Call] Sending email to {recipient} with subject '{subject}'")
    print(f"Body: {body}")
    if attachment_paths:
        print(f"Attachments: {', '.join(attachment_paths)}")
    return {"status": "success", "message": f"Email sent to {recipient}"}
```

**Advanced Examples:**

```python
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum

# Complex data structures
@dataclass
class SearchFilter:
    category: str
    min_price: float
    max_price: float

class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

@tools
def advanced_search(
    query: str,
    filters: Optional[Dict[str, Any]] = None,
    sort_by: Literal["relevance", "date", "price"] = "relevance",
    limit: int = 10,
    include_metadata: bool = False
) -> List[Dict[str, Any]]:
    """Perform an advanced search with filtering and sorting options.
    
    This tool demonstrates complex parameter handling including optional
    dictionaries, enums, and nested data structures.

    Args:
        query (str): The search query string
        filters (Dict[str, Any], optional): Search filters including:
            - category (str): Product category to filter by
            - price_range (Dict[str, float]): Min/max price range
            - tags (List[str]): Tags to include in search
        sort_by (Literal): How to sort results - relevance, date, or price
        limit (int): Maximum number of results to return (1-100)
        include_metadata (bool): Whether to include detailed metadata

    Returns:
        List[Dict[str, Any]]: Search results with optional metadata
    """
    # Validate limit
    if not 1 <= limit <= 100:
        raise ValueError("Limit must be between 1 and 100")
    
    # Process filters
    processed_filters = filters or {}
    
    # Simulate search logic
    results = [
        {
            "id": i,
            "title": f"Result {i} for '{query}'",
            "relevance_score": 0.9 - (i * 0.1),
            "category": processed_filters.get("category", "general"),
            "metadata": {"source": "search_engine"} if include_metadata else None
        }
        for i in range(1, min(limit + 1, 6))
    ]
    
    return results

@tools
def create_task(
    title: str,
    description: str = "",
    priority: Literal["low", "medium", "high"] = "medium",
    assignee: Optional[str] = None,
    due_date: Optional[str] = None,
    tags: List[str] = None
) -> Dict[str, Any]:
    """Create a new task with comprehensive options.
    
    Demonstrates handling of optional parameters, lists, and enums.

    Args:
        title (str): Task title (required)
        description (str): Detailed task description
        priority (Literal): Task priority level
        assignee (str, optional): Person assigned to the task
        due_date (str, optional): Due date in YYYY-MM-DD format
        tags (List[str], optional): List of tags for categorization

    Returns:
        Dict[str, Any]: Created task details with generated ID
    """
    import uuid
    from datetime import datetime
    
    task = {
        "id": str(uuid.uuid4()),
        "title": title,
        "description": description,
        "priority": priority,
        "assignee": assignee,
        "due_date": due_date,
        "tags": tags or [],
        "created_at": datetime.now().isoformat(),
        "status": "pending"
    }
    
    print(f"[Tool Call] Created task: {task['title']} (Priority: {priority})")
    return task

@tools
def batch_process_data(
    data_items: List[Dict[str, Any]],
    operation: Literal["validate", "transform", "filter"] = "validate",
    config: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Process a batch of data items with configurable operations.
    
    Shows handling of complex list and dictionary parameters.

    Args:
        data_items (List[Dict[str, Any]]): List of data items to process
        operation (Literal): Type of operation to perform
        config (Dict[str, Any], optional): Operation-specific configuration

    Returns:
        Dict[str, Any]: Processing results with statistics
    """
    if not data_items:
        return {"error": "No data items provided", "processed": 0}
    
    config = config or {}
    processed_count = 0
    errors = []
    
    for i, item in enumerate(data_items):
        try:
            if operation == "validate":
                # Validate required fields
                required_fields = config.get("required_fields", ["id"])
                for field in required_fields:
                    if field not in item:
                        raise ValueError(f"Missing required field: {field}")
            elif operation == "transform":
                # Apply transformations
                transformations = config.get("transformations", {})
                for field, transform in transformations.items():
                    if field in item and transform == "uppercase":
                        item[field] = str(item[field]).upper()
            elif operation == "filter":
                # Apply filters
                filter_conditions = config.get("filters", {})
                for field, condition in filter_conditions.items():
                    if field in item and item[field] != condition:
                        continue
            
            processed_count += 1
            
        except Exception as e:
            errors.append(f"Item {i}: {str(e)}")
    
    return {
        "operation": operation,
        "total_items": len(data_items),
        "processed": processed_count,
        "errors": errors,
        "success_rate": processed_count / len(data_items)
    }
```

**Schema Generation Features:**

The `@tools` decorator automatically handles:

- **Type Validation**: Converts Python type hints to JSON schema types
- **Enum Support**: `Literal` types become `enum` constraints in the schema
- **Optional Parameters**: Properly marks optional parameters and default values
- **Complex Types**: Supports `List`, `Dict`, `Union`, and nested structures
- **Docstring Parsing**: Extracts parameter descriptions from various docstring formats
- **Error Handling**: Provides clear error messages for invalid schemas

**Accessing Registered Tools:**

```python
from HelpingAI.tools import get_tools, get_registry

# Get all registered tools
all_tools = get_tools()
print(f"Registered tools: {[tool.name for tool in all_tools]}")

# Get specific tools by name
specific_tools = get_tools(["get_weather", "send_email"])

# Access the registry directly for advanced operations
registry = get_registry()
weather_tool = registry.get_tool("get_weather")

# Call tools directly
result = weather_tool.call({"city": "Paris", "unit": "celsius"})
```

### Method 2: The `Fn` Class

The [`Fn`](HelpingAI/tools/core.py:12) class provides a more explicit and programmatic way to define tools. This is particularly useful when:

-   You need to define a tool dynamically at runtime.
-   The tool's logic is not encapsulated in a single, straightforward Python function.
-   You are integrating with systems that provide tool definitions in a format that needs to be mapped to the SDK's `Fn` object.
-   You require custom validation or error handling logic.

When using `Fn`, you manually provide the `name`, `description`, `parameters` (as a JSON schema dictionary), and the `function` (a callable Python object) that the tool will execute.

**Basic Usage:**

```python
from HelpingAI.tools import Fn, get_registry

# Define a calculator tool using the Fn class
calculator_tool = Fn(
    name="calculate",
    description="Perform a simple arithmetic calculation (add, subtract, multiply, divide).",
    parameters={
        "type": "object",
        "properties": {
            "operation": {
                "type": "string",
                "description": "The arithmetic operation to perform.",
                "enum": ["add", "subtract", "multiply", "divide"]
            },
            "a": {"type": "number", "description": "The first number for the operation."},
            "b": {"type": "number", "description": "The second number for the operation."}
        },
        "required": ["operation", "a", "b"]
    },
    function=lambda operation, a, b: {
        "add": a + b,
        "subtract": a - b,
        "multiply": a * b,
        "divide": a / b if b != 0 else "Error: Division by zero"
    }[operation] # The actual Python function to execute
)

# Register the tool with the global registry
get_registry().register(calculator_tool)

# Example of a tool that might not map directly to a simple function
class DatabaseClient:
    def query(self, sql_query: str) -> list[dict]:
        print(f"[Tool Call] Executing SQL query: {sql_query}")
        # Simulate database interaction
        if "users" in sql_query.lower():
            return [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
        return []

db_client = DatabaseClient()

database_query_tool = Fn(
    name="execute_sql_query",
    description="Executes a SQL query against the database and returns the results.",
    parameters={
        "type": "object",
        "properties": {
            "sql_query": {
                "type": "string",
                "description": "The SQL query string to execute."
            }
        },
        "required": ["sql_query"]
    },
    function=db_client.query # Reference to a method of an instantiated class
)
get_registry().register(database_query_tool)
```

**Advanced Fn Usage with Validation and Error Handling:**

```python
from HelpingAI.tools import Fn, get_registry
from HelpingAI.tools.errors import ToolExecutionError, SchemaValidationError
import json
import re
from typing import Dict, Any, List

class AdvancedFileProcessor:
    """Example of a complex tool implementation with validation."""
    
    def __init__(self, allowed_extensions: List[str] = None):
        self.allowed_extensions = allowed_extensions or ['.txt', '.json', '.csv']
    
    def process_file(self, file_path: str, operation: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process a file with comprehensive validation and error handling."""
        options = options or {}
        
        # Validate file extension
        if not any(file_path.endswith(ext) for ext in self.allowed_extensions):
            raise ToolExecutionError(
                f"Unsupported file type. Allowed extensions: {self.allowed_extensions}",
                tool_name="process_file"
            )
        
        # Validate operation
        valid_operations = ["read", "analyze", "transform"]
        if operation not in valid_operations:
            raise ToolExecutionError(
                f"Invalid operation '{operation}'. Must be one of: {valid_operations}",
                tool_name="process_file"
            )
        
        try:
            # Simulate file processing
            result = {
                "file_path": file_path,
                "operation": operation,
                "status": "success",
                "timestamp": "2024-01-01T12:00:00Z"
            }
            
            if operation == "read":
                result["content"] = f"Content of {file_path}"
                result["size_bytes"] = 1024
            elif operation == "analyze":
                result["analysis"] = {
                    "line_count": 50,
                    "word_count": 500,
                    "encoding": "utf-8"
                }
            elif operation == "transform":
                transform_type = options.get("transform_type", "uppercase")
                result["transform_applied"] = transform_type
                result["output_path"] = f"{file_path}.transformed"
            
            return result
            
        except Exception as e:
            raise ToolExecutionError(
                f"Failed to process file '{file_path}': {str(e)}",
                tool_name="process_file",
                original_error=e
            )

# Create the file processor instance
file_processor = AdvancedFileProcessor()

# Define the Fn tool with comprehensive schema
file_processor_tool = Fn(
    name="process_file",
    description="Process files with validation and comprehensive error handling. Supports reading, analyzing, and transforming text files.",
    parameters={
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path to the file to process",
                "pattern": r"^.+\.(txt|json|csv)$"  # Regex validation in schema
            },
            "operation": {
                "type": "string",
                "description": "Operation to perform on the file",
                "enum": ["read", "analyze", "transform"]
            },
            "options": {
                "type": "object",
                "description": "Optional parameters for the operation",
                "properties": {
                    "transform_type": {
                        "type": "string",
                        "description": "Type of transformation to apply",
                        "enum": ["uppercase", "lowercase", "title_case"],
                        "default": "uppercase"
                    },
                    "encoding": {
                        "type": "string",
                        "description": "File encoding to use",
                        "default": "utf-8"
                    }
                },
                "additionalProperties": False
            }
        },
        "required": ["file_path", "operation"],
        "additionalProperties": False
    },
    function=file_processor.process_file
)

# Register the advanced tool
get_registry().register(file_processor_tool)

# Example of dynamic tool creation
def create_api_tool(api_name: str, base_url: str, endpoints: Dict[str, str]) -> Fn:
    """Dynamically create API tools based on configuration."""
    
    def api_caller(endpoint: str, method: str = "GET", data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generic API calling function."""
        if endpoint not in endpoints:
            raise ToolExecutionError(
                f"Unknown endpoint '{endpoint}'. Available: {list(endpoints.keys())}",
                tool_name=f"{api_name}_api"
            )
        
        full_url = f"{base_url}{endpoints[endpoint]}"
        
        # Simulate API call
        return {
            "api": api_name,
            "endpoint": endpoint,
            "method": method,
            "url": full_url,
            "status": "success",
            "data": data or {},
            "response": f"Mock response from {full_url}"
        }
    
    return Fn(
        name=f"{api_name}_api",
        description=f"Call {api_name} API endpoints with validation and error handling.",
        parameters={
            "type": "object",
            "properties": {
                "endpoint": {
                    "type": "string",
                    "description": f"API endpoint to call. Available: {list(endpoints.keys())}",
                    "enum": list(endpoints.keys())
                },
                "method": {
                    "type": "string",
                    "description": "HTTP method to use",
                    "enum": ["GET", "POST", "PUT", "DELETE"],
                    "default": "GET"
                },
                "data": {
                    "type": "object",
                    "description": "Data to send with the request",
                    "additionalProperties": True
                }
            },
            "required": ["endpoint"]
        },
        function=api_caller
    )

# Create and register a dynamic API tool
weather_api_tool = create_api_tool(
    api_name="weather",
    base_url="https://api.weather.com",
    endpoints={
        "current": "/v1/current",
        "forecast": "/v1/forecast",
        "historical": "/v1/historical"
    }
)
get_registry().register(weather_api_tool)
```

**Fn Class Key Features:**

- **Manual Schema Control**: Complete control over parameter validation and schema definition
- **Built-in Validation**: Automatic parameter validation against the provided schema using [`_validate_arguments()`](HelpingAI/tools/core.py:98)
- **Error Handling**: Comprehensive error handling with [`ToolExecutionError`](HelpingAI/tools/errors.py) and [`SchemaValidationError`](HelpingAI/tools/errors.py)
- **Flexible Function Binding**: Support for functions, methods, lambdas, and callables
- **OpenAI Compatibility**: Converts to standard OpenAI tool format via [`to_tool_format()`](HelpingAI/tools/core.py:29)
- **Direct Execution**: Call tools directly with [`call()`](HelpingAI/tools/core.py:51) method

**Converting Functions to Fn Objects:**

```python
# Convert existing functions to Fn objects
def existing_function(param1: str, param2: int = 10) -> str:
    """An existing function to convert."""
    return f"Processed {param1} with value {param2}"

# Automatic conversion using from_function
fn_tool = Fn.from_function(existing_function)
get_registry().register(fn_tool)

# Manual conversion with custom schema
manual_fn_tool = Fn(
    name="existing_function_custom",
    description="Custom description for the existing function",
    parameters={
        "type": "object",
        "properties": {
            "param1": {"type": "string", "description": "First parameter"},
            "param2": {"type": "integer", "description": "Second parameter", "default": 10}
        },
        "required": ["param1"]
    },
    function=existing_function
)
get_registry().register(manual_fn_tool)
```

**Error Handling Best Practices:**

```python
from HelpingAI.tools.errors import ToolExecutionError

def robust_tool_function(data: Dict[str, Any]) -> Dict[str, Any]:
    """Example of robust error handling in tool functions."""
    try:
        # Validate input data
        if not isinstance(data, dict):
            raise ValueError("Input must be a dictionary")
        
        if "required_field" not in data:
            raise ValueError("Missing required field: required_field")
        
        # Process data
        result = {"processed": True, "input": data}
        return result
        
    except ValueError as e:
        # Re-raise validation errors as ToolExecutionError
        raise ToolExecutionError(
            f"Validation error: {str(e)}",
            tool_name="robust_tool",
            original_error=e
        )
    except Exception as e:
        # Handle unexpected errors
        raise ToolExecutionError(
            f"Unexpected error during processing: {str(e)}",
            tool_name="robust_tool",
            original_error=e
        )

robust_tool = Fn(
    name="robust_tool",
    description="Example tool with comprehensive error handling",
    parameters={
        "type": "object",
        "properties": {
            "data": {
                "type": "object",
                "description": "Data to process",
                "properties": {
                    "required_field": {"type": "string"}
                },
                "required": ["required_field"]
            }
        },
        "required": ["data"]
    },
    function=robust_tool_function
)
```

### Method 3: OpenAI JSON Schema

For maximum compatibility and integration with existing systems, you can define tools directly using the standard OpenAI JSON schema format. This is useful if you already have tool definitions in this format or if you prefer to define your schemas explicitly.

When using this method, you typically don't provide a `function` callable directly within the tool definition itself. Instead, you would map the tool's `name` to your internal Python functions when handling the tool calls from the model.

**Basic OpenAI Format Examples:**

```python
from typing import Dict, Any

# Define a tool using the OpenAI JSON schema format
openai_tools_list = [
    {
        "type": "function",
        "function": {
            "name": "get_stock_price",
            "description": "Retrieves the current stock price for a given stock symbol.",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "The stock ticker symbol (e.g., GOOG, AAPL)."
                    }
                },
                "required": ["symbol"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Gets the current time in a specified timezone.",
            "parameters": {
                "type": "object",
                "properties": {
                    "timezone": {
                        "type": "string",
                        "description": "The timezone to get the current time for (e.g., 'America/New_York', 'Europe/London')."
                    }
                },
                "required": ["timezone"]
            }
        }
    }
]

# You would typically have a mapping for these tools to actual functions
def _get_stock_price_impl(symbol: str) -> Dict[str, Any]:
    print(f"[Tool Call] get_stock_price(symbol='{symbol}')")
    # Simulate fetching stock price
    prices = {"GOOG": 170.00, "AAPL": 180.50}
    return {"symbol": symbol, "price": prices.get(symbol.upper(), "N/A")}

def _get_current_time_impl(timezone: str) -> Dict[str, Any]:
    import datetime
    import pytz
    print(f"[Tool Call] get_current_time(timezone='{timezone}')")
    try:
        tz = pytz.timezone(timezone)
        current_time = datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S %Z%z")
        return {"timezone": timezone, "current_time": current_time}
    except pytz.UnknownTimeZoneError:
        return {"error": "Unknown timezone", "timezone": timezone}

# This mapping would be used when handling tool_calls from the model
openai_tool_implementations = {
    "get_stock_price": _get_stock_price_impl,
    "get_current_time": _get_current_time_impl,
}
```

**Advanced OpenAI Schema Examples:**

```python
# Complex tool with nested objects and arrays
complex_openai_tools = [
    {
        "type": "function",
        "function": {
            "name": "create_calendar_event",
            "description": "Create a calendar event with comprehensive details and attendees.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Event title"
                    },
                    "start_time": {
                        "type": "string",
                        "description": "Start time in ISO 8601 format (e.g., '2024-01-15T14:30:00Z')",
                        "pattern": r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$"
                    },
                    "duration_minutes": {
                        "type": "integer",
                        "description": "Event duration in minutes",
                        "minimum": 15,
                        "maximum": 1440
                    },
                    "attendees": {
                        "type": "array",
                        "description": "List of attendees",
                        "items": {
                            "type": "object",
                            "properties": {
                                "email": {
                                    "type": "string",
                                    "format": "email",
                                    "description": "Attendee email address"
                                },
                                "name": {
                                    "type": "string",
                                    "description": "Attendee name"
                                },
                                "required": {
                                    "type": "boolean",
                                    "description": "Whether attendance is required",
                                    "default": False
                                }
                            },
                            "required": ["email"]
                        },
                        "minItems": 1,
                        "maxItems": 50
                    },
                    "location": {
                        "type": "object",
                        "description": "Event location details",
                        "properties": {
                            "venue": {"type": "string", "description": "Venue name"},
                            "address": {"type": "string", "description": "Full address"},
                            "room": {"type": "string", "description": "Room number or name"},
                            "virtual_link": {"type": "string", "format": "uri", "description": "Virtual meeting link"}
                        },
                        "anyOf": [
                            {"required": ["venue"]},
                            {"required": ["virtual_link"]}
                        ]
                    },
                    "recurrence": {
                        "type": "object",
                        "description": "Recurrence settings",
                        "properties": {
                            "frequency": {
                                "type": "string",
                                "enum": ["daily", "weekly", "monthly", "yearly"],
                                "description": "Recurrence frequency"
                            },
                            "interval": {
                                "type": "integer",
                                "minimum": 1,
                                "maximum": 99,
                                "description": "Interval between recurrences"
                            },
                            "end_date": {
                                "type": "string",
                                "pattern": r"^\d{4}-\d{2}-\d{2}$",
                                "description": "End date for recurrence (YYYY-MM-DD)"
                            }
                        },
                        "required": ["frequency"]
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "urgent"],
                        "default": "medium",
                        "description": "Event priority level"
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Event tags for categorization",
                        "uniqueItems": True
                    }
                },
                "required": ["title", "start_time", "duration_minutes"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_document",
            "description": "Analyze a document and extract key information with configurable analysis options.",
            "parameters": {
                "type": "object",
                "properties": {
                    "document_url": {
                        "type": "string",
                        "format": "uri",
                        "description": "URL to the document to analyze"
                    },
                    "analysis_options": {
                        "type": "object",
                        "description": "Configuration for document analysis",
                        "properties": {
                            "extract_entities": {
                                "type": "boolean",
                                "default": True,
                                "description": "Extract named entities (people, places, organizations)"
                            },
                            "sentiment_analysis": {
                                "type": "boolean",
                                "default": False,
                                "description": "Perform sentiment analysis"
                            },
                            "summarize": {
                                "type": "boolean",
                                "default": True,
                                "description": "Generate document summary"
                            },
                            "language_detection": {
                                "type": "boolean",
                                "default": True,
                                "description": "Detect document language"
                            },
                            "key_phrases": {
                                "type": "integer",
                                "minimum": 0,
                                "maximum": 20,
                                "default": 5,
                                "description": "Number of key phrases to extract"
                            }
                        },
                        "additionalProperties": False
                    },
                    "output_format": {
                        "type": "string",
                        "enum": ["json", "markdown", "plain_text"],
                        "default": "json",
                        "description": "Format for analysis results"
                    }
                },
                "required": ["document_url"]
            }
        }
    }
]

# Implementation functions for complex tools
def _create_calendar_event_impl(**kwargs) -> Dict[str, Any]:
    """Implementation for calendar event creation."""
    print(f"[Tool Call] create_calendar_event with {len(kwargs)} parameters")
    
    # Validate required fields
    required_fields = ["title", "start_time", "duration_minutes"]
    for field in required_fields:
        if field not in kwargs:
            return {"error": f"Missing required field: {field}"}
    
    # Process attendees
    attendees = kwargs.get("attendees", [])
    processed_attendees = []
    for attendee in attendees:
        processed_attendees.append({
            "email": attendee["email"],
            "name": attendee.get("name", attendee["email"].split("@")[0]),
            "required": attendee.get("required", False)
        })
    
    # Create event
    event = {
        "id": f"event_{hash(kwargs['title'] + kwargs['start_time']) % 10000}",
        "title": kwargs["title"],
        "start_time": kwargs["start_time"],
        "duration_minutes": kwargs["duration_minutes"],
        "attendees": processed_attendees,
        "location": kwargs.get("location", {}),
        "recurrence": kwargs.get("recurrence"),
        "priority": kwargs.get("priority", "medium"),
        "tags": kwargs.get("tags", []),
        "status": "created"
    }
    
    return {"event": event, "message": f"Event '{kwargs['title']}' created successfully"}

def _analyze_document_impl(**kwargs) -> Dict[str, Any]:
    """Implementation for document analysis."""
    document_url = kwargs["document_url"]
    options = kwargs.get("analysis_options", {})
    output_format = kwargs.get("output_format", "json")
    
    print(f"[Tool Call] analyze_document: {document_url}")
    
    # Simulate document analysis
    analysis_results = {
        "document_url": document_url,
        "analysis_timestamp": "2024-01-15T10:30:00Z",
        "document_info": {
            "title": "Sample Document",
            "pages": 5,
            "word_count": 1250
        }
    }
    
    if options.get("language_detection", True):
        analysis_results["language"] = "en"
        analysis_results["confidence"] = 0.98
    
    if options.get("extract_entities", True):
        analysis_results["entities"] = [
            {"text": "John Smith", "type": "PERSON", "confidence": 0.95},
            {"text": "New York", "type": "LOCATION", "confidence": 0.92},
            {"text": "Microsoft", "type": "ORGANIZATION", "confidence": 0.89}
        ]
    
    if options.get("sentiment_analysis", False):
        analysis_results["sentiment"] = {
            "overall": "positive",
            "score": 0.7,
            "confidence": 0.85
        }
    
    if options.get("summarize", True):
        analysis_results["summary"] = "This document discusses key strategies for business growth and market expansion."
    
    if options.get("key_phrases", 5) > 0:
        analysis_results["key_phrases"] = [
            "business growth", "market expansion", "strategic planning",
            "competitive analysis", "customer acquisition"
        ][:options.get("key_phrases", 5)]
    
    # Format output based on requested format
    if output_format == "markdown":
        return {"format": "markdown", "content": f"# Document Analysis\n\n**URL:** {document_url}\n\n**Summary:** {analysis_results.get('summary', 'N/A')}"}
    elif output_format == "plain_text":
        return {"format": "plain_text", "content": f"Document: {document_url}\nSummary: {analysis_results.get('summary', 'N/A')}"}
    else:
        return analysis_results

# Extended tool implementations mapping
extended_openai_tool_implementations = {
    "get_stock_price": _get_stock_price_impl,
    "get_current_time": _get_current_time_impl,
    "create_calendar_event": _create_calendar_event_impl,
    "analyze_document": _analyze_document_impl,
}
```

**Integration Patterns:**

```python
from HelpingAI import HAI

# Pattern 1: Direct usage with manual tool call handling
def handle_openai_tools_manually():
    client = HAI()
    
    response = client.chat.completions.create(
        model="Dhanishtha-2.0-preview",
        messages=[{"role": "user", "content": "What's the current stock price of AAPL?"}],
        tools=openai_tools_list  # Use OpenAI format directly
    )
    
    # Handle tool calls manually
    if response.choices[0].message.tool_calls:
        for tool_call in response.choices[0].message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)
            
            # Execute using our implementation mapping
            if tool_name in openai_tool_implementations:
                result = openai_tool_implementations[tool_name](**tool_args)
                print(f"Tool {tool_name} result: {result}")

# Pattern 2: Convert OpenAI tools to Fn objects for unified handling
def convert_openai_to_fn_objects():
    from HelpingAI.tools import Fn, get_registry
    
    # Convert OpenAI format to Fn objects
    for tool_def in openai_tools_list:
        func_def = tool_def["function"]
        tool_name = func_def["name"]
        
        if tool_name in openai_tool_implementations:
            fn_tool = Fn(
                name=tool_name,
                description=func_def["description"],
                parameters=func_def["parameters"],
                function=openai_tool_implementations[tool_name]
            )
            get_registry().register(fn_tool)
    
    print("OpenAI tools converted and registered as Fn objects")

# Pattern 3: Mixed tool usage (combining formats)
def use_mixed_tool_formats():
    from HelpingAI.tools import get_tools
    
    client = HAI()
    
    # Combine different tool formats
    all_tools = (
        get_tools() +  # @tools decorated and Fn registered tools
        openai_tools_list +  # OpenAI format tools
        ["code_interpreter", "web_search"]  # Built-in tools
    )
    
    response = client.chat.completions.create(
        model="Dhanishtha-2.0-preview",
        messages=[{"role": "user", "content": "Analyze the weather data and create a calendar event"}],
        tools=all_tools
    )
    
    return response
```

**Schema Validation Best Practices:**

```python
# Example of comprehensive schema validation
def create_robust_openai_tool(name: str, description: str, parameters: Dict[str, Any], implementation: callable) -> Dict[str, Any]:
    """Create a robust OpenAI tool with validation."""
    
    # Validate schema structure
    required_schema_keys = ["type", "properties"]
    if not all(key in parameters for key in required_schema_keys):
        raise ValueError(f"Schema must contain: {required_schema_keys}")
    
    # Ensure proper parameter types
    for prop_name, prop_def in parameters.get("properties", {}).items():
        if "type" not in prop_def:
            raise ValueError(f"Property '{prop_name}' missing type definition")
        if "description" not in prop_def:
            print(f"Warning: Property '{prop_name}' missing description")
    
    tool_def = {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": parameters
        }
    }
    
    # Test the implementation with sample data
    try:
        sample_args = {}
        for prop_name, prop_def in parameters.get("properties", {}).items():
            if prop_name in parameters.get("required", []):
                # Generate sample value based on type
                prop_type = prop_def["type"]
                if prop_type == "string":
                    sample_args[prop_name] = "test_value"
                elif prop_type == "integer":
                    sample_args[prop_name] = 1
                elif prop_type == "boolean":
                    sample_args[prop_name] = True
                elif prop_type == "array":
                    sample_args[prop_name] = []
                elif prop_type == "object":
                    sample_args[prop_name] = {}
        
        # Test implementation
        test_result = implementation(**sample_args)
        print(f"Tool '{name}' validation successful")
        
    except Exception as e:
        print(f"Warning: Tool '{name}' implementation test failed: {e}")
    
    return tool_def
```

### Tool Format Compatibility

The HelpingAI SDK provides seamless compatibility between different tool definition formats, allowing you to mix and match approaches based on your needs. The SDK automatically converts all formats to a unified internal representation.

**Supported Tool Formats:**

1. **String Identifiers**: Built-in tool names (`"code_interpreter"`, `"web_search"`)
2. **`@tools` Decorated Functions**: Automatically registered in global registry
3. **`Fn` Objects**: Programmatically created tools with full control
4. **OpenAI JSON Schema**: Standard OpenAI-compatible tool definitions
5. **MCP Server Configurations**: Model Context Protocol server integrations

**Format Conversion Examples:**

```python
from HelpingAI import HAI
from HelpingAI.tools import tools, Fn, get_tools

# Define tools using different methods
@tools
def calculate_tip(bill_amount: float, tip_percentage: float = 15.0) -> dict:
    """Calculate tip amount and total bill."""
    tip = bill_amount * (tip_percentage / 100)
    total = bill_amount + tip
    return {"bill_amount": bill_amount, "tip": tip, "total": total}

# Fn object
currency_converter = Fn(
    name="convert_currency",
    description="Convert between different currencies",
    parameters={
        "type": "object",
        "properties": {
            "amount": {"type": "number", "description": "Amount to convert"},
            "from_currency": {"type": "string", "description": "Source currency code"},
            "to_currency": {"type": "string", "description": "Target currency code"}
        },
        "required": ["amount", "from_currency", "to_currency"]
    },
    function=lambda amount, from_currency, to_currency: {
        "original_amount": amount,
        "from_currency": from_currency,
        "to_currency": to_currency,
        "converted_amount": amount * 1.1,  # Simplified conversion
        "exchange_rate": 1.1
    }
)

# OpenAI format
openai_format_tool = {
    "type": "function",
    "function": {
        "name": "get_weather_forecast",
        "description": "Get weather forecast for a location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "Location name"},
                "days": {"type": "integer", "description": "Number of days", "default": 3}
            },
            "required": ["location"]
        }
    }
}

# All formats can be used together seamlessly
client = HAI()

# Method 1: Mixed list with automatic conversion
mixed_tools = [
    "code_interpreter",           # Built-in tool
    "web_search",                # Built-in tool
    calculate_tip,               # @tools decorated function
    currency_converter,          # Fn object
    openai_format_tool          # OpenAI format
]

response = client.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[{"role": "user", "content": "Calculate a 20% tip on $50 and convert it to EUR"}],
    tools=mixed_tools
)
```

**Automatic Format Detection:**

The SDK's [`ensure_openai_format()`](HelpingAI/tools/compatibility.py) function handles automatic conversion:

```python
from HelpingAI.tools.compatibility import ensure_openai_format

# Example of how the SDK processes different tool formats
def demonstrate_format_conversion():
    # Mixed input formats
    mixed_tools = [
        "code_interpreter",                    # String identifier
        {"type": "function", "function": {...}}, # OpenAI format
        Fn(name="test", description="...", parameters={}, function=lambda: None),  # Fn object
        calculate_tip,                         # Decorated function
    ]
    
    # SDK automatically converts all to OpenAI format
    openai_compatible_tools = ensure_openai_format(mixed_tools)
    
    # All tools are now in standard format:
    # [
    #     {"type": "function", "function": {"name": "code_interpreter", ...}},
    #     {"type": "function", "function": {"name": "original_tool", ...}},
    #     {"type": "function", "function": {"name": "test", ...}},
    #     {"type": "function", "function": {"name": "calculate_tip", ...}}
    # ]
    
    return openai_compatible_tools
```

**Best Practices for Tool Format Selection:**

```python
# When to use each format:

# 1. Use string identifiers for built-in tools
basic_tools = ["code_interpreter", "web_search"]

# 2. Use @tools decorator for simple, standalone functions
@tools
def simple_calculation(x: float, y: float) -> float:
    """Simple arithmetic operation."""
    return x + y

# 3. Use Fn objects for complex tools with custom logic
complex_tool = Fn(
    name="complex_processor",
    description="Complex data processing with validation",
    parameters={...},  # Detailed schema
    function=lambda **kwargs: complex_processing_logic(**kwargs)
)

# 4. Use OpenAI format when integrating with existing systems
legacy_integration_tools = [
    {
        "type": "function",
        "function": {
            "name": "legacy_system_call",
            "description": "Call legacy system API",
            "parameters": existing_openai_schema
        }
    }
]

# 5. Combine formats based on tool source
def create_comprehensive_toolset():
    return [
        # Core built-in capabilities
        "code_interpreter",
        "web_search",
        
        # Custom business logic (@tools decorated)
        *get_tools(["business_calculator", "report_generator"]),
        
        # Advanced custom tools (Fn objects)
        *[tool for tool in get_registry().list_tools() if "advanced_" in tool.name],
        
        # External system integrations (OpenAI format)
        *load_external_tool_definitions(),
        
        # MCP server tools
        {"mcpServers": {"weather": {"command": "uvx", "args": ["mcp-server-weather"]}}}
    ]

def load_external_tool_definitions():
    """Load tool definitions from external systems."""
    # This could load from files, APIs, databases, etc.
    return [
        {
            "type": "function",
            "function": {
                "name": "external_api_call",
                "description": "Call external service API",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "endpoint": {"type": "string"},
                        "data": {"type": "object"}
                    },
                    "required": ["endpoint"]
                }
            }
        }
    ]
```

## Using Tools

Once you have defined your tools using any of the methods above, you can make them available to the AI model by passing them to the `tools` parameter of the [`client.chat.completions.create()`](HelpingAI/client/completions.py:110) method. The SDK automatically handles the conversion of different tool formats into a unified structure that the model can understand.

### Enhanced Tool Parameter Formats

The HelpingAI SDK supports multiple flexible formats for the `tools` parameter, making it easy to integrate tools from various sources:

**Supported Tool Parameter Formats:**

1. **Mixed Lists**: Combine different tool types in a single list
2. **String Categories**: Use category names to load tool groups
3. **Function References**: Pass decorated functions directly
4. **Fn Objects**: Include programmatically created tools
5. **OpenAI Format**: Standard OpenAI tool definitions
6. **MCP Configurations**: Model Context Protocol server setups

```python
from HelpingAI import HAI
from HelpingAI.tools import get_tools, tools
import json

client = HAI()

# Example 1: Mixed format list
@tools
def custom_calculator(operation: str, a: float, b: float) -> float:
    """Perform basic arithmetic operations."""
    operations = {
        "add": a + b,
        "subtract": a - b,
        "multiply": a * b,
        "divide": a / b if b != 0 else float('inf')
    }
    return operations.get(operation, 0)

mixed_tools = [
    "code_interpreter",              # Built-in tool string
    "web_search",                   # Built-in tool string
    custom_calculator,              # @tools decorated function
    {                              # OpenAI format tool
        "type": "function",
        "function": {
            "name": "format_currency",
            "description": "Format number as currency",
            "parameters": {
                "type": "object",
                "properties": {
                    "amount": {"type": "number"},
                    "currency": {"type": "string", "default": "USD"}
                },
                "required": ["amount"]
            }
        }
    },
    {                              # MCP server configuration
        "mcpServers": {
            "filesystem": {
                "command": "uvx",
                "args": ["mcp-server-filesystem", "/path/to/allowed"]
            }
        }
    }
]

# Example 2: Using tool categories and registry
financial_tools = get_tools(["currency_converter", "tax_calculator", "investment_analyzer"])
analysis_tools = ["code_interpreter", "web_search"]
custom_tools = [custom_calculator]

# Combine different sources
comprehensive_toolset = financial_tools + analysis_tools + custom_tools

# Example 3: Context-aware tool selection
def get_tools_for_task(task_type: str) -> list:
    """Get appropriate tools based on task type."""
    base_tools = ["code_interpreter"]  # Always include
    
    tool_mapping = {
        "data_analysis": ["code_interpreter", "web_search"] + get_tools(["data_processor"]),
        "financial": ["code_interpreter", custom_calculator] + get_tools(["currency_converter"]),
        "research": ["web_search", "code_interpreter"] + get_tools(["document_analyzer"]),
        "development": ["code_interpreter"] + get_tools(["code_formatter", "test_runner"]),
        "general": ["code_interpreter", "web_search"]
    }
    
    return tool_mapping.get(task_type, tool_mapping["general"])

# Use context-aware selection
task_specific_tools = get_tools_for_task("financial")
```

### Tool Choice Strategies

The `tool_choice` parameter provides fine-grained control over tool usage:

```python
# Automatic tool selection (default)
response = client.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[{"role": "user", "content": "Calculate compound interest"}],
    tools=mixed_tools,
    tool_choice="auto"  # Let model decide
)

# Force tool usage
response = client.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[{"role": "user", "content": "What's 15% of 200?"}],
    tools=mixed_tools,
    tool_choice="required"  # Must use at least one tool
)

# Disable tool usage
response = client.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[{"role": "user", "content": "Just chat normally"}],
    tools=mixed_tools,
    tool_choice="none"  # Don't use any tools
)

# Force specific tool
response = client.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[{"role": "user", "content": "Run some Python code"}],
    tools=mixed_tools,
    tool_choice={
        "type": "function",
        "function": {"name": "code_interpreter"}
    }
)
```

### Advanced Tool Configuration

```python
# Dynamic tool loading based on user permissions
def get_user_tools(user_id: str, permissions: list) -> list:
    """Get tools based on user permissions."""
    available_tools = ["code_interpreter"]  # Basic tools for everyone
    
    if "web_access" in permissions:
        available_tools.append("web_search")
    
    if "financial_tools" in permissions:
        available_tools.extend(get_tools(["currency_converter", "stock_analyzer"]))
    
    if "admin" in permissions:
        available_tools.extend([
            {"mcpServers": {"filesystem": {"command": "uvx", "args": ["mcp-server-filesystem"]}}},
            {"mcpServers": {"database": {"command": "uvx", "args": ["mcp-server-postgres"]}}}
        ])
    
    return available_tools

# Environment-based tool configuration
def get_environment_tools(environment: str) -> list:
    """Get tools appropriate for the deployment environment."""
    base_tools = ["code_interpreter"]
    
    if environment == "development":
        return base_tools + [
            "web_search",
            {"mcpServers": {"dev_db": {"command": "uvx", "args": ["mcp-server-sqlite", "dev.db"]}}},
            *get_tools(["debug_helper", "test_runner"])
        ]
    elif environment == "production":
        return base_tools + [
            "web_search",
            {"mcpServers": {"prod_db": {"command": "uvx", "args": ["mcp-server-postgres"]}}},
            *get_tools(["monitoring", "analytics"])
        ]
    else:  # staging
        return base_tools + ["web_search"]

# Use environment-specific tools
current_env = "development"  # Could be from config
env_tools = get_environment_tools(current_env)

# Tool configuration with error handling
def safe_tool_configuration(tools: list) -> list:
    """Safely configure tools with fallback."""
    try:
        # Attempt to use full tool configuration
        response = client.chat.completions.create(
            model="Dhanishtha-2.0-preview",
            messages=[{"role": "user", "content": "Test message"}],
            tools=tools
        )
        return tools
    except Exception as e:
        print(f"Tool configuration failed: {e}")
        # Fallback to basic tools
        return ["code_interpreter"]

safe_tools = safe_tool_configuration(mixed_tools)
```

### Practical Usage Examples

```python
# Example 1: Data analysis workflow
def data_analysis_session():
    tools = [
        "code_interpreter",
        "web_search",
        *get_tools(["data_validator", "chart_generator"])
    ]
    
    response = client.chat.completions.create(
        model="Dhanishtha-2.0-preview",
        messages=[{
            "role": "user",
            "content": "Analyze this sales data and create visualizations"
        }],
        tools=tools,
        tool_choice="auto"
    )
    
    return response

# Example 2: Research and documentation
def research_session():
    tools = [
        "web_search",
        "code_interpreter",
        {
            "type": "function",
            "function": {
                "name": "save_research_note",
                "description": "Save research findings",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "content": {"type": "string"},
                        "tags": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["title", "content"]
                }
            }
        }
    ]
    
    messages = [{
        "role": "user",
        "content": "Research the latest developments in quantum computing and save key findings"
    }]
    
    response = client.chat.completions.create(
        model="Dhanishtha-2.0-preview",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )
    
    return response

# Example 3: Multi-step workflow with tool progression
def progressive_tool_usage():
    # Start with basic tools
    basic_response = client.chat.completions.create(
        model="Dhanishtha-2.0-preview",
        messages=[{"role": "user", "content": "I need help with a complex calculation"}],
        tools=["code_interpreter"]
    )
    
    # Add more tools based on the response
    if "research" in basic_response.choices[0].message.content.lower():
        enhanced_tools = ["code_interpreter", "web_search"]
    else:
        enhanced_tools = ["code_interpreter", *get_tools(["advanced_math"])]
    
    # Continue with enhanced toolset
    enhanced_response = client.chat.completions.create(
        model="Dhanishtha-2.0-preview",
        messages=[
            {"role": "user", "content": "I need help with a complex calculation"},
            basic_response.choices[0].message,
            {"role": "user", "content": "Please provide more detailed analysis"}
        ],
        tools=enhanced_tools
    )
    
    return enhanced_response
```

## Advanced Usage Patterns

This section demonstrates sophisticated patterns for using tools in complex scenarios, including error handling, conditional logic, and multi-step workflows.

### Conditional Tool Execution

Execute tools based on dynamic conditions and user context:

```python
from HelpingAI import HAI
from HelpingAI.tools import tools
from typing import Dict, Any, List

@tools
def risk_assessment(investment_amount: float, risk_tolerance: str) -> dict:
    """Assess investment risk based on amount and tolerance."""
    risk_multipliers = {"low": 0.02, "medium": 0.05, "high": 0.12}
    risk_score = investment_amount * risk_multipliers.get(risk_tolerance, 0.05)
    
    return {
        "investment_amount": investment_amount,
        "risk_tolerance": risk_tolerance,
        "risk_score": risk_score,
        "recommendation": "proceed" if risk_score < 1000 else "review_required"
    }

def conditional_financial_advisor(user_query: str, user_profile: Dict[str, Any]):
    """Provide financial advice with conditional tool usage."""
    client = HAI()
    
    # Base tools always available
    base_tools = ["code_interpreter"]
    
    # Add tools based on user profile and query content
    if user_profile.get("premium_user", False):
        base_tools.extend(["web_search", risk_assessment])
    
    if "market" in user_query.lower() or "stock" in user_query.lower():
        base_tools.append("web_search")
    
    if "calculate" in user_query.lower() or "compute" in user_query.lower():
        base_tools.extend([risk_assessment])
    
    # Add regulatory compliance tools for large amounts
    if any(amount in user_query for amount in ["million", "$1M", "large investment"]):
        compliance_tool = {
            "type": "function",
            "function": {
                "name": "compliance_check",
                "description": "Check regulatory compliance for large investments",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "amount": {"type": "number"},
                        "jurisdiction": {"type": "string"}
                    },
                    "required": ["amount"]
                }
            }
        }
        base_tools.append(compliance_tool)
    
    response = client.chat.completions.create(
        model="Dhanishtha-2.0-preview",
        messages=[
            {"role": "system", "content": f"User profile: {user_profile}"},
            {"role": "user", "content": user_query}
        ],
        tools=base_tools,
        tool_choice="auto"
    )
    
    return response

# Example usage
user_profile = {"premium_user": True, "risk_tolerance": "medium", "jurisdiction": "US"}
result = conditional_financial_advisor("Calculate risk for $50,000 stock investment", user_profile)
```

### Multi-Step Tool Workflows

Chain multiple tools together for complex operations:

```python
@tools
def data_validator(data_source: str, validation_rules: List[str]) -> dict:
    """Validate data against specified rules."""
    # Simulate validation logic
    issues = []
    if "completeness" in validation_rules and "incomplete" in data_source:
        issues.append("Missing required fields")
    if "format" in validation_rules and "malformed" in data_source:
        issues.append("Invalid data format")
    
    return {
        "data_source": data_source,
        "validation_passed": len(issues) == 0,
        "issues": issues,
        "checked_rules": validation_rules
    }

@tools
def data_transformer(data_source: str, transformations: List[str]) -> dict:
    """Transform data according to specified rules."""
    applied_transformations = []
    for transform in transformations:
        if transform == "normalize":
            applied_transformations.append("Normalized numerical values")
        elif transform == "clean":
            applied_transformations.append("Removed invalid characters")
        elif transform == "standardize":
            applied_transformations.append("Standardized date formats")
    
    return {
        "original_source": data_source,
        "transformations_applied": applied_transformations,
        "status": "completed"
    }

def automated_data_pipeline(data_source: str):
    """Execute a multi-step data processing pipeline."""
    client = HAI()
    
    # Configure tools for the pipeline
    pipeline_tools = [
        "code_interpreter",
        "web_search",
        data_validator,
        data_transformer
    ]
    
    # Step 1: Initial analysis
    analysis_response = client.chat.completions.create(
        model="Dhanishtha-2.0-preview",
        messages=[{
            "role": "user",
            "content": f"Analyze this data source and recommend validation rules: {data_source}"
        }],
        tools=pipeline_tools
    )
    
    conversation = [
        {"role": "user", "content": f"Analyze this data source and recommend validation rules: {data_source}"},
        analysis_response.choices[0].message
    ]
    
    # Step 2: Execute validation based on recommendations
    if analysis_response.choices[0].message.tool_calls:
        # Handle any tool calls from analysis
        for tool_call in analysis_response.choices[0].message.tool_calls:
            if tool_call.function.name == "data_validator":
                validation_result = client.call("data_validator", {
                    "data_source": data_source,
                    "validation_rules": ["completeness", "format", "consistency"]
                })
                
                conversation.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(validation_result)
                })
    
    # Step 3: Apply transformations if validation passed
    transformation_response = client.chat.completions.create(
        model="Dhanishtha-2.0-preview",
        messages=conversation + [{
            "role": "user",
            "content": "If validation passed, apply appropriate transformations to clean the data"
        }],
        tools=pipeline_tools
    )
    
    return {
        "analysis": analysis_response,
        "transformations": transformation_response,
        "pipeline_status": "completed"
    }
```

### Error Handling and Recovery

Implement robust error handling with graceful fallbacks:

```python
def robust_tool_execution(user_request: str, preferred_tools: List[str], fallback_tools: List[str]):
    """Execute tools with comprehensive error handling and fallbacks."""
    client = HAI()
    
    def attempt_with_tools(tools: List[str], attempt_name: str) -> Dict[str, Any]:
        """Attempt execution with given tools."""
        try:
            response = client.chat.completions.create(
                model="Dhanishtha-2.0-preview",
                messages=[{"role": "user", "content": user_request}],
                tools=tools,
                tool_choice="auto"
            )
            
            # Execute any tool calls
            if response.choices[0].message.tool_calls:
                execution_results = []
                for tool_call in response.choices[0].message.tool_calls:
                    try:
                        tool_name = tool_call.function.name
                        args = json.loads(tool_call.function.arguments)
                        result = client.call(tool_name, args)
                        execution_results.append({
                            "tool": tool_name,
                            "success": True,
                            "result": result
                        })
                    except Exception as tool_error:
                        execution_results.append({
                            "tool": tool_name,
                            "success": False,
                            "error": str(tool_error)
                        })
                
                return {
                    "attempt": attempt_name,
                    "success": True,
                    "response": response,
                    "tool_results": execution_results
                }
            else:
                return {
                    "attempt": attempt_name,
                    "success": True,
                    "response": response,
                    "tool_results": []
                }
                
        except Exception as e:
            return {
                "attempt": attempt_name,
                "success": False,
                "error": str(e),
                "tool_results": []
            }
    
    # Try preferred tools first
    result = attempt_with_tools(preferred_tools, "preferred")
    
    if result["success"]:
        return result
    
    # Try fallback tools
    print(f"Preferred tools failed: {result['error']}. Trying fallback tools...")
    fallback_result = attempt_with_tools(fallback_tools, "fallback")
    
    if fallback_result["success"]:
        return fallback_result
    
    # Final fallback to basic tools
    print(f"Fallback tools failed: {fallback_result['error']}. Using basic tools...")
    basic_result = attempt_with_tools(["code_interpreter"], "basic")
    
    return basic_result

# Example usage with error handling
preferred = ["code_interpreter", "web_search", "advanced_calculator"]
fallback = ["code_interpreter", "basic_calculator"]

result = robust_tool_execution(
    "Calculate compound interest for $10,000 at 5% for 10 years",
    preferred,
    fallback
)

print(f"Execution completed with {result['attempt']} tools")
```

### Dynamic Tool Loading

Load and configure tools dynamically based on runtime conditions:

```python
def dynamic_tool_loader(task_description: str, available_resources: Dict[str, Any]):
    """Dynamically load appropriate tools based on task and resources."""
    
    # Analyze task requirements
    task_keywords = task_description.lower().split()
    
    # Base tools always available
    tools = ["code_interpreter"]
    
    # Add tools based on task analysis
    tool_mapping = {
        "web": ["web_search"],
        "search": ["web_search"],
        "internet": ["web_search"],
        "calculate": [get_tools(["calculator", "math_helper"])],
        "data": [get_tools(["data_processor", "chart_generator"])],
        "file": [{"mcpServers": {"filesystem": {"command": "uvx", "args": ["mcp-server-filesystem"]}}}],
        "database": [{"mcpServers": {"database": {"command": "uvx", "args": ["mcp-server-sqlite"]}}}],
        "api": [get_tools(["api_client", "http_helper"])],
    }
    
    # Add tools based on keywords
    for keyword, keyword_tools in tool_mapping.items():
        if keyword in task_keywords:
            tools.extend(keyword_tools)
    
    # Add resource-based tools
    if available_resources.get("has_internet", True):
        if "web_search" not in tools:
            tools.append("web_search")
    
    if available_resources.get("database_access", False):
        tools.append({"mcpServers": {"database": {"command": "uvx", "args": ["mcp-server-postgres"]}}})
    
    if available_resources.get("premium_apis", False):
        tools.extend([
            get_tools(["premium_calculator", "advanced_analyzer"]),
            {
                "type": "function",
                "function": {
                    "name": "premium_api_call",
                    "description": "Access premium API services",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "service": {"type": "string"},
                            "params": {"type": "object"}
                        },
                        "required": ["service"]
                    }
                }
            }
        ])
    
    # Remove duplicates and flatten nested lists
    flattened_tools = []
    for tool in tools:
        if isinstance(tool, list):
            flattened_tools.extend(tool)
        else:
            flattened_tools.append(tool)
    
    # Remove duplicates (for string tools)
    unique_tools = []
    seen_strings = set()
    for tool in flattened_tools:
        if isinstance(tool, str):
            if tool not in seen_strings:
                unique_tools.append(tool)
                seen_strings.add(tool)
        else:
            unique_tools.append(tool)
    
    return unique_tools

# Example usage
resources = {
    "has_internet": True,
    "database_access": True,
    "premium_apis": False,
    "compute_resources": "high"
}

dynamic_tools = dynamic_tool_loader(
    "Analyze web data and create database reports with calculations",
    resources
)

client = HAI()
response = client.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[{"role": "user", "content": "Analyze web data and create database reports with calculations"}],
    tools=dynamic_tools
)
```

### Tool Performance Monitoring

Monitor and optimize tool usage for better performance:

```python
import time
from typing import Dict, List, Any

class ToolPerformanceMonitor:
    """Monitor tool performance and usage patterns."""
    
    def __init__(self):
        self.tool_stats = {}
        self.execution_history = []
    
    def track_tool_call(self, tool_name: str, execution_time: float, success: bool, result_size: int = 0):
        """Track individual tool call performance."""
        if tool_name not in self.tool_stats:
            self.tool_stats[tool_name] = {
                "total_calls": 0,
                "successful_calls": 0,
                "total_time": 0,
                "avg_time": 0,
                "success_rate": 0,
                "avg_result_size": 0
            }
        
        stats = self.tool_stats[tool_name]
        stats["total_calls"] += 1
        stats["total_time"] += execution_time
        stats["avg_time"] = stats["total_time"] / stats["total_calls"]
        
        if success:
            stats["successful_calls"] += 1
        
        stats["success_rate"] = stats["successful_calls"] / stats["total_calls"]
        
        # Track result size for optimization
        if result_size > 0:
            if "total_result_size" not in stats:
                stats["total_result_size"] = 0
                stats["result_count"] = 0
            stats["total_result_size"] += result_size
            stats["result_count"] += 1
            stats["avg_result_size"] = stats["total_result_size"] / stats["result_count"]
        
        self.execution_history.append({
            "tool": tool_name,
            "timestamp": time.time(),
            "execution_time": execution_time,
            "success": success,
            "result_size": result_size
        })
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate performance report."""
        return {
            "tool_statistics": self.tool_stats,
            "total_executions": len(self.execution_history),
            "overall_success_rate": sum(1 for h in self.execution_history if h["success"]) / len(self.execution_history) if self.execution_history else 0,
            "most_used_tool": max(self.tool_stats.keys(), key=lambda k: self.tool_stats[k]["total_calls"]) if self.tool_stats else None,
            "fastest_tool": min(self.tool_stats.keys(), key=lambda k: self.tool_stats[k]["avg_time"]) if self.tool_stats else None
        }
    
    def optimize_tool_selection(self, task_type: str) -> List[str]:
        """Suggest optimal tools based on performance history."""
        if not self.tool_stats:
            return ["code_interpreter"]  # Default fallback
        
        # Sort tools by success rate and speed
        sorted_tools = sorted(
            self.tool_stats.items(),
            key=lambda x: (x[1]["success_rate"], -x[1]["avg_time"]),
            reverse=True
        )
        
        # Return top performing tools
        return [tool[0] for tool in sorted_tools[:5]]

# Usage example with performance monitoring
def monitored_tool_execution(user_request: str):
    """Execute tools with performance monitoring."""
    monitor = ToolPerformanceMonitor()
    client = HAI()
    
    tools = ["code_interpreter", "web_search"]
    
    start_time = time.time()
    
    try:
        response = client.chat.completions.create(
            model="Dhanishtha-2.0-preview",
            messages=[{"role": "user", "content": user_request}],
            tools=tools
        )
        
        # Track tool calls if any
        if response.choices[0].message.tool_calls:
            for tool_call in response.choices[0].message.tool_calls:
                tool_start = time.time()
                try:
                    tool_name = tool_call.function.name
                    args = json.loads(tool_call.function.arguments)
                    result = client.call(tool_name, args)
                    
                    execution_time = time.time() - tool_start
                    result_size = len(str(result)) if result else 0
                    
                    monitor.track_tool_call(tool_name, execution_time, True, result_size)
                    
                except Exception as e:
                    execution_time = time.time() - tool_start
                    monitor.track_tool_call(tool_name, execution_time, False)
                    print(f"Tool {tool_name} failed: {e}")
        
        total_time = time.time() - start_time
        
        return {
            "response": response,
            "performance_report": monitor.get_performance_report(),
            "total_execution_time": total_time,
            "optimized_tools": monitor.optimize_tool_selection("general")
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "performance_report": monitor.get_performance_report(),
            "total_execution_time": time.time() - start_time
        }

# Example usage
result = monitored_tool_execution("Calculate fibonacci sequence and search for related algorithms")
print("Performance Report:", result["performance_report"])
```

## Enhanced Workflow and Tool Caching

The HelpingAI SDK provides an enhanced workflow that significantly simplifies tool calling through automatic tool configuration caching and helper methods. This reduces boilerplate code and makes tool integration more seamless.

### Automatic Tool Caching

When you use tools in a [`chat.completions.create()`](HelpingAI/client/completions.py:110) call, the SDK automatically caches the tool configuration. This enables a simplified workflow where you can call tools directly using [`client.call()`](HelpingAI/client/main.py:107) without reconfiguring them.

**How Tool Caching Works:**

1. **Configuration Storage**: Tools passed to `chat.completions.create()` are automatically cached in [`_last_chat_tools_config`](HelpingAI/client/main.py:39)
2. **Automatic Fallback**: [`client.call()`](HelpingAI/client/main.py:107) uses cached tools when no explicit configuration is provided
3. **Priority System**: Explicit [`configure_tools()`](HelpingAI/client/main.py:42) takes precedence over cached configuration

**Basic Enhanced Workflow:**

```python
from HelpingAI import HAI

client = HAI()

# Step 1: Use tools in chat completion (automatically cached)
response = client.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[{"role": "user", "content": "Calculate 15% tip on $80"}],
    tools=["code_interpreter", "web_search"]  # Automatically cached
)

# Step 2: Call tools directly using cached configuration
tip_result = client.call("code_interpreter", {
    "code": "bill = 80; tip_percent = 15; tip = bill * (tip_percent / 100); print(f'Tip: ${tip:.2f}, Total: ${bill + tip:.2f}')"
})

# Step 3: No need to reconfigure tools for subsequent calls
search_result = client.call("web_search", {
    "query": "average restaurant tip percentage 2024",
    "max_results": 3
})
```

### Helper Methods

The SDK provides several helper methods that simplify tool call handling and reduce boilerplate code:

#### [`create_assistant_message()`](HelpingAI/client/completions.py:65)

Creates properly formatted assistant messages with tool calls:

```python
# Traditional approach
assistant_message = {
    "role": "assistant",
    "content": "I'll help you with that calculation.",
    "tool_calls": [
        {
            "id": "call_123",
            "type": "function",
            "function": {
                "name": "calculate",
                "arguments": '{"x": 10, "y": 20}'
            }
        }
    ]
}

# Enhanced approach using helper
assistant_message = client.chat.completions.create_assistant_message(
    content="I'll help you with that calculation.",
    tool_calls=[
        {
            "id": "call_123",
            "type": "function",
            "function": {
                "name": "calculate",
                "arguments": '{"x": 10, "y": 20}'
            }
        }
    ]
)
```

#### [`execute_tool_calls()`](HelpingAI/client/completions.py:305)

Executes multiple tool calls and returns structured results:

```python
# Traditional approach - manual execution
def handle_tool_calls_manually(message):
    results = []
    for tool_call in message.tool_calls:
        try:
            tool_name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            result = client.call(tool_name, args)
            results.append({
                "tool_call_id": tool_call.id,
                "result": result,
                "error": None
            })
        except Exception as e:
            results.append({
                "tool_call_id": tool_call.id,
                "result": None,
                "error": str(e)
            })
    return results

# Enhanced approach using helper
results = client.chat.completions.execute_tool_calls(message)
# Returns the same structured format automatically
```

#### [`create_tool_response_messages()`](HelpingAI/client/completions.py:367)

Converts tool execution results to properly formatted response messages:

```python
# Traditional approach
def create_responses_manually(execution_results):
    messages = []
    for result in execution_results:
        content = json.dumps(result["result"]) if result["error"] is None else f"Error: {result['error']}"
        messages.append({
            "role": "tool",
            "tool_call_id": result["tool_call_id"],
            "content": content
        })
    return messages

# Enhanced approach using helper
tool_response_messages = client.chat.completions.create_tool_response_messages(execution_results)
```

### Complete Enhanced Workflow Example

```python
from HelpingAI import HAI
from HelpingAI.tools import tools

@tools
def analyze_data(data_type: str, sample_size: int = 100) -> dict:
    """Analyze sample data and return statistics."""
    import random
    
    if data_type == "sales":
        samples = [random.randint(100, 1000) for _ in range(sample_size)]
    elif data_type == "temperature":
        samples = [random.uniform(-10, 40) for _ in range(sample_size)]
    else:
        samples = [random.random() for _ in range(sample_size)]
    
    return {
        "data_type": data_type,
        "sample_size": len(samples),
        "mean": sum(samples) / len(samples),
        "min": min(samples),
        "max": max(samples)
    }

def enhanced_workflow_demo():
    client = HAI()
    
    # Step 1: Initial chat with tool configuration (automatically cached)
    initial_response = client.chat.completions.create(
        model="Dhanishtha-2.0-preview",
        messages=[{
            "role": "user",
            "content": "I need to analyze sales data and create visualizations. Can you help?"
        }],
        tools=[
            "code_interpreter",
            "web_search",
            analyze_data  # Custom function
        ]
    )
    
    # Step 2: Handle tool calls if present using helper methods
    if initial_response.choices[0].message.tool_calls:
        # Use helper method to execute all tool calls
        execution_results = client.chat.completions.execute_tool_calls(
            initial_response.choices[0].message
        )
        
        # Use helper method to create response messages
        tool_response_messages = client.chat.completions.create_tool_response_messages(
            execution_results
        )
    
    # Step 3: Direct tool calling using cached configuration
    # No need to specify tools again - they're cached from step 1
    
    # Analyze sales data
    sales_analysis = client.call("analyze_data", {
        "data_type": "sales",
        "sample_size": 200
    })
    
    # Create visualization using cached code_interpreter
    visualization = client.call("code_interpreter", {
        "code": f"""
import matplotlib.pyplot as plt
import numpy as np

# Use analysis results
mean_sales = {sales_analysis['mean']}
min_sales = {sales_analysis['min']}
max_sales = {sales_analysis['max']}

# Create visualization
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# Bar chart of statistics
stats = ['Mean', 'Min', 'Max']
values = [mean_sales, min_sales, max_sales]
ax1.bar(stats, values)
ax1.set_title('Sales Statistics')
ax1.set_ylabel('Sales Amount')

# Histogram simulation
np.random.seed(42)
sales_data = np.random.normal(mean_sales, (max_sales - min_sales) / 6, 200)
ax2.hist(sales_data, bins=20, alpha=0.7)
ax2.set_title('Sales Distribution')
ax2.set_xlabel('Sales Amount')
ax2.set_ylabel('Frequency')

plt.tight_layout()
plt.show()
print(f"Analysis complete: Mean sales = ${mean_sales:.2f}")
"""
    })
    
    return {
        "analysis": sales_analysis,
        "visualization": visualization
    }

# Run the enhanced workflow
results = enhanced_workflow_demo()
print("Enhanced workflow completed successfully!")
```

### Benefits of Enhanced Workflow

1. **Reduced Boilerplate**: Helper methods eliminate repetitive code
2. **Automatic Caching**: No need to reconfigure tools for subsequent calls
3. **Error Handling**: Built-in error handling in helper methods
4. **Type Safety**: Proper type conversion and validation
5. **Consistency**: Standardized message formats across all tool interactions
6. **Flexibility**: Can override cached configuration when needed

## Handling Tool Calls

When the AI model determines that a tool is necessary to fulfill a user's request, it will generate a `tool_calls` object within its response message. Your application is then responsible for executing these tool calls and providing the results back to the model in a subsequent turn of the conversation.

Here's a typical workflow for handling tool calls:

1.  **Check for `tool_calls`**: After receiving a response from `client.chat.completions.create()`, inspect `response.choices[0].message.tool_calls`.
2.  **Execute Tools**: If `tool_calls` exist, iterate through them. For each `tool_call`:
    *   Extract the `function.name` and `function.arguments`.
    *   Parse the `function.arguments` (which are a JSON string) into a Python dictionary.
    *   Execute the corresponding tool using `client.call(function_name, function_args)`.
3.  **Create Tool Response Messages**: Format the results of each tool execution into a `tool` role message. This message includes the `tool_call_id` (to link it back to the original tool call) and the `content` (the tool's output).
4.  **Continue Conversation**: Send the original user message, the model's tool call message, and the new tool response messages back to the model in a new `client.chat.completions.create()` call. This allows the model to use the tool's output to generate a final, informed response.

```python
# ... (assuming client, messages, response, registered_tools, openai_tool_implementations are defined from previous examples) ...

message = response.choices[0].message

# Check if the model made any tool calls
if message.tool_calls:
    print("\nModel wants to call tools:")
    tool_messages_for_follow_up = [] # To store tool outputs for the next API call

    for tool_call in message.tool_calls:
        function_name = tool_call.function.name
        function_args_str = tool_call.function.arguments
        
        print(f"- Tool Name: {function_name}")
        print(f"  Arguments: {function_args_str}")

        try:
            # Parse the arguments from JSON string to Python dictionary
            function_args = json.loads(function_args_str)
            
            result = None
            # Execute the tool based on its name
            if function_name in registered_tools.keys(): # Check tools defined with @tools or Fn
                # Use client.call() for tools registered with the client
                result = client.call(function_name, function_args)
            elif function_name in openai_tool_implementations: # Check tools defined with OpenAI JSON schema
                # For OpenAI JSON schema tools, call their direct Python implementation
                result = openai_tool_implementations[function_name](**function_args)
            else:
                print(f"  Error: Tool '{function_name}' not found in any registry.")
                result = {"error": f"Tool '{function_name}' not found."}

            print(f"  Tool Result: {result}")
            
            # Create a tool message to send back to the model
            tool_messages_for_follow_up.append({
                "role": "tool",
                "tool_call_id": tool_call.id, # Important: Link to the original tool call
                "name": function_name,
                "content": json.dumps(result) # Tool output must be a string
            })

        except json.JSONDecodeError:
            print(f"  Error: Invalid JSON arguments for tool '{function_name}': {function_args_str}")
            tool_messages_for_follow_up.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": function_name,
                "content": f"Error: Invalid JSON arguments: {function_args_str}"
            })
        except Exception as e:
            print(f"  Error executing tool '{function_name}': {e}")
            tool_messages_for_follow_up.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": function_name,
                "content": f"Error executing tool: {e}"
            })

    # Continue the conversation with the tool results
    # The messages list should include:
    # 1. Original user message
    # 2. Model's response with tool_calls
    # 3. Tool outputs
    follow_up_response = client.chat.completions.create(
        model="Dhanishtha-2.0-preview",
        messages=messages + [message] + tool_messages_for_follow_up,
        tools=all_available_tools, # Tools should still be available for the model
        tool_choice="auto"
    )

    print("\nFinal model response after tool execution:")
    print(follow_up_response.choices[0].message.content)

else:
    print("\nModel did not call any tools.")
    print(f"Model's response: {message.content}")
```

### Simplified Tool Call Handling

The HelpingAI SDK provides helper methods that significantly simplify tool call handling. Here's how to use the enhanced workflow:

#### Using Helper Methods

```python
from HelpingAI import HAI
import json

def simplified_tool_handling():
    """Demonstrate simplified tool call handling using helper methods."""
    client = HAI()
    
    # Initial request
    response = client.chat.completions.create(
        model="Dhanishtha-2.0-preview",
        messages=[{"role": "user", "content": "Calculate 20% tip on $150 and search for tipping etiquette"}],
        tools=["code_interpreter", "web_search"]
    )
    
    conversation = [
        {"role": "user", "content": "Calculate 20% tip on $150 and search for tipping etiquette"},
        response.choices[0].message
    ]
    
    # Handle tool calls if present
    if response.choices[0].message.tool_calls:
        # Use helper method to execute all tool calls
        execution_results = client.chat.completions.execute_tool_calls(
            response.choices[0].message
        )
        
        # Use helper method to create response messages
        tool_response_messages = client.chat.completions.create_tool_response_messages(
            execution_results
        )
        
        # Add tool responses to conversation
        conversation.extend(tool_response_messages)
        
        # Continue conversation with results
        final_response = client.chat.completions.create(
            model="Dhanishtha-2.0-preview",
            messages=conversation,
            tools=["code_interpreter", "web_search"]
        )
        
        return final_response
    
    return response

# Example usage
result = simplified_tool_handling()
print("Final response:", result.choices[0].message.content)
```

#### One-Line Tool Execution

For even simpler scenarios, you can use direct tool calling:

```python
# Direct tool execution (uses cached configuration from previous chat.completions.create calls)
def direct_tool_usage():
    client = HAI()
    
    # Configure tools once
    client.chat.completions.create(
        model="Dhanishtha-2.0-preview",
        messages=[{"role": "user", "content": "Setup tools"}],
        tools=["code_interpreter", "web_search"]
    )
    
    # Now use tools directly
    calculation = client.call("code_interpreter", {
        "code": "tip_percent = 20; bill = 150; tip = bill * (tip_percent / 100); print(f'Tip: ${tip}, Total: ${bill + tip}')"
    })
    
    search_results = client.call("web_search", {
        "query": "restaurant tipping etiquette guidelines",
        "max_results": 3
    })
    
    return {
        "calculation": calculation,
        "search": search_results
    }

results = direct_tool_usage()
```

## Traditional vs Enhanced Patterns

The HelpingAI SDK offers both traditional OpenAI-compatible patterns and enhanced workflows. Here's a comprehensive comparison:

### Pattern Comparison Overview

| Aspect | Traditional Pattern | Enhanced Pattern |
|--------|-------------------|------------------|
| **Tool Configuration** | Manual tool mapping | Automatic caching & conversion |
| **Tool Execution** | Manual iteration & parsing | Helper methods |
| **Error Handling** | Custom implementation | Built-in error handling |
| **Message Creation** | Manual message formatting | Helper methods |
| **Code Complexity** | High boilerplate | Minimal boilerplate |
| **Type Safety** | Manual validation | Automatic validation |

### Detailed Comparison Examples

#### Tool Configuration

**Traditional Approach:**
```python
# Manual tool definition and mapping
def traditional_tool_setup():
    openai_tools = [
        {
            "type": "function",
            "function": {
                "name": "calculate",
                "description": "Perform calculations",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {"type": "string"}
                    },
                    "required": ["expression"]
                }
            }
        }
    ]
    
    # Manual implementation mapping
    tool_implementations = {
        "calculate": lambda expression: eval(expression)  # Simplified
    }
    
    return openai_tools, tool_implementations

tools, implementations = traditional_tool_setup()
```

**Enhanced Approach:**
```python
# Automatic tool definition with decorators
from HelpingAI.tools import tools

@tools
def calculate(expression: str) -> float:
    """Perform mathematical calculations safely."""
    # Safe evaluation logic here
    return eval(expression)  # Simplified for example

# Tools automatically registered and available
```

### Best Practices Summary

1. **Use Enhanced Patterns for New Projects**: Start with `@tools` decorators and helper methods
2. **Gradual Migration**: Migrate existing code incrementally using compatibility layers
3. **Error Handling**: Rely on built-in error handling in enhanced patterns
4. **Performance**: Use tool caching for better performance
5. **Maintainability**: Enhanced patterns reduce code complexity and improve maintainability

The enhanced patterns provide the same functionality as traditional approaches while significantly reducing complexity and improving developer experience.