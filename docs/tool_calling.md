# Tool Calling Guide

This guide provides a comprehensive overview of the tool calling capabilities of the HelpingAI Python SDK.

## Introduction

Tool calling allows you to extend the capabilities of the HelpingAI models by giving them access to external tools and functions. You can define custom tools, and the model will intelligently decide when to use them to answer user queries.

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

```python
from HelpingAI.tools import tools
from typing import Literal

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

### Method 2: The `Fn` Class

The `Fn` class provides a more explicit and programmatic way to define tools. This is particularly useful when:

-   You need to define a tool dynamically at runtime.
-   The tool's logic is not encapsulated in a single, straightforward Python function.
-   You are integrating with systems that provide tool definitions in a format that needs to be mapped to the SDK's `Fn` object.

When using `Fn`, you manually provide the `name`, `description`, `parameters` (as a JSON schema dictionary), and the `function` (a callable Python object) that the tool will execute.

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

### Method 3: OpenAI JSON Schema

For maximum compatibility and integration with existing systems, you can define tools directly using the standard OpenAI JSON schema format. This is useful if you already have tool definitions in this format or if you prefer to define your schemas explicitly.

When using this method, you typically don't provide a `function` callable directly within the tool definition itself. Instead, you would map the tool's `name` to your internal Python functions when handling the tool calls from the model.

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

## Using Tools

Once you have defined your tools using any of the methods above, you can make them available to the AI model by passing them to the `tools` parameter of the `client.chat.completions.create()` method. The SDK automatically handles the conversion of different tool formats into a unified structure that the model can understand.

You can combine tools defined by different methods into a single list. The `get_tools()` function is particularly useful as it retrieves all tools registered via the `@tools` decorator and `Fn` class.

```python
from HelpingAI import HAI
from HelpingAI.tools import get_tools
import json # Needed for handling tool arguments and results

client = HAI()

# Retrieve tools defined with @tools and Fn class
registered_tools = get_tools()

# Combine with tools defined using OpenAI JSON schema
# (assuming openai_tools_list is defined as in Method 3 example)
all_available_tools = registered_tools + openai_tools_list

# Example conversation where the model might use tools
messages = [
    {"role": "user", "content": "What's the weather in London and the current stock price of AAPL? Also, what's the time in Europe/London?"}
]

response = client.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=messages,
    tools=all_available_tools, # Pass the combined list of tools
    tool_choice="auto" # Let the model decide whether to call a tool
)

print(f"Initial model response: {response.choices[0].message.content}")
```

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