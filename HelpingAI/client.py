"""HAI API client with OpenAI-like interface."""

import json
import platform
import os
from typing import Optional, Dict, Any, Union, Iterator, List, Literal, cast, TYPE_CHECKING

import requests

from .version import VERSION
from .error import (
    HAIError,
    InvalidRequestError,
    InvalidModelError,
    NoAPIKeyError,
    InvalidAPIKeyError,
    AuthenticationError,
    APIError,
    RateLimitError,
    TooManyRequestsError,
    ServiceUnavailableError,
    TimeoutError,
    APIConnectionError,
    ServerError,
    ContentFilterError
)
from .base_models import (
    BaseModel,
    ChatCompletion,
    ChatCompletionChunk,
    ChatCompletionMessage,
    Choice,
    ChoiceDelta,
    CompletionUsage,
    ToolCall,
    ToolFunction,
    FunctionCall
)
from .models import Models

if TYPE_CHECKING:
    from .client import HAI

class BaseClient:
    """Base client with common functionality for the HelpingAI API.

    Handles authentication, session management, and low-level HTTP requests.
    """
    def __init__(
        self,
        api_key: Optional[str] = None,
        organization: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 60.0,
    ) -> None:
        self.api_key: str = api_key or os.getenv("HAI_API_KEY")  # type: ignore
        if not self.api_key:
            raise NoAPIKeyError()
        self.organization: Optional[str] = organization
        self.base_url: str = (base_url or "https://api.helpingai.co/v1").rstrip("/")
        self.timeout: float = timeout
        self.session: requests.Session = requests.Session()

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        stream: bool = False,
        auth_required: bool = True,
    ) -> Any:
        """Make a request to the HAI API.

        Args:
            method: HTTP method (e.g., 'GET', 'POST').
            path: API endpoint path.
            params: Query parameters.
            json_data: JSON body data.
            stream: Whether to stream the response.
            auth_required: Whether authentication is required.
        Returns:
            The response data (parsed JSON or Response object if streaming).
        Raises:
            HAIError or its subclasses on error.
        """
        headers = {
            "Content-Type": "application/json"
        }
        
        if auth_required:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        # Only add optional headers if they might be needed
        # Some APIs are sensitive to extra headers
        if self.organization:
            headers["HAI-Organization"] = self.organization

        url = f"{self.base_url}{path}"

        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json_data,
                stream=stream,
                timeout=self.timeout,
            )
            
            if response.status_code != 200:
                try:
                    error_data = response.json()
                except:
                    error_data = {"error": {"message": "Unknown error occurred"}}
                
                # Handle different error response formats
                if isinstance(error_data.get("error"), dict):
                    # Nested format: {"error": {"message": "...", "type": "...", "code": "..."}}
                    error_message = error_data.get("error", {}).get("message", "Unknown error")
                    error_type = error_data.get("error", {}).get("type")
                    error_code = error_data.get("error", {}).get("code")
                elif isinstance(error_data.get("error"), str):
                    # Flat format: {"error": "Request failed with status code 400"}
                    error_message = error_data.get("error", "Unknown error")
                    error_type = None
                    error_code = None
                else:
                    # Fallback for other formats
                    error_message = error_data.get("message", "Unknown error")
                    error_type = error_data.get("type")
                    error_code = error_data.get("code")
                
                if response.status_code == 401:
                    raise InvalidAPIKeyError(response.status_code, response.headers)
                elif response.status_code == 400:
                    # More robust error handling for model errors
                    if "model" in error_message.lower():
                        # Try to extract model name, but fallback gracefully
                        import re
                        match = re.search(r"'(.*?)'", error_message)
                        model_name = match.group(1) if match else None
                        if model_name:
                            raise InvalidModelError(model_name, response.status_code, response.headers)
                        else:
                            raise InvalidModelError("Unknown model", response.status_code, response.headers)
                    
                    # Enhanced guidance for 400 errors
                    enhanced_message = error_message
                    if not stream:
                        # Check for various indicators that streaming might be required
                        streaming_indicators = [
                            "Request failed with status code",
                            "streaming",
                            "stream",
                            "tool",  # Some tool-related requests might require streaming
                            "function"  # Function calling might require streaming
                        ]
                        
                        if any(indicator in error_message.lower() for indicator in streaming_indicators):
                            enhanced_message += (
                                ". This model or endpoint might require streaming. "
                                "Try setting stream=True in your request."
                            )
                        else:
                            enhanced_message += (
                                ". If this error persists, try setting stream=True or "
                                "check your request parameters."
                            )
                    
                    raise InvalidRequestError(enhanced_message, status_code=response.status_code, headers=response.headers)
                elif response.status_code == 429:
                    raise TooManyRequestsError(response.status_code, response.headers)
                elif response.status_code == 503:
                    raise ServiceUnavailableError(response.status_code, response.headers)
                elif response.status_code >= 500:
                    raise ServerError(error_message, response.status_code, response.headers)
                elif "content_filter" in str(error_type).lower():
                    raise ContentFilterError(error_message, response.status_code, response.headers)
                else:
                    raise APIError(error_message, error_code, error_type, response.status_code, response.headers)

            return response if stream else response.json()

        except requests.exceptions.Timeout:
            raise TimeoutError()
        except requests.exceptions.ConnectionError as e:
            raise APIConnectionError(f"Error connecting to HAI API: {str(e)}", should_retry=True)
        except requests.exceptions.RequestException as e:
            raise APIError(f"Error communicating with HAI API: {str(e)}")

class ChatCompletions:
    """Chat completions API interface for the HelpingAI client.

    Use this to create chat completions, including streaming and function/tool calling.
    """
    def __init__(self, client: "HAI") -> None:
        self._client: "HAI" = client


    def _convert_messages_to_dicts(self, messages: List[Union[Dict[str, Any], BaseModel]]) -> List[Dict[str, Any]]:
        """Convert messages to dictionaries, handling BaseModel objects automatically."""
        converted_messages = []
        for message in messages:
            if hasattr(message, 'to_dict'):
                # Convert BaseModel objects to dict
                msg_dict = message.to_dict()
            elif isinstance(message, dict):
                # Already a dict, but ensure tool_calls are converted if they're BaseModel objects
                msg_dict = message.copy()
                if 'tool_calls' in msg_dict and msg_dict['tool_calls']:
                    converted_tool_calls = []
                    for tool_call in msg_dict['tool_calls']:
                        if hasattr(tool_call, 'to_dict'):
                            converted_tool_calls.append(tool_call.to_dict())
                        else:
                            converted_tool_calls.append(tool_call)
                    msg_dict['tool_calls'] = converted_tool_calls
            else:
                # Fallback: try to convert to dict
                try:
                    msg_dict = dict(message)
                except (TypeError, ValueError):
                    raise ValueError(f"Message must be a dict or BaseModel object, got {type(message)}")
            
            converted_messages.append(msg_dict)
        return converted_messages

    def create_assistant_message(
        self,
        content: Optional[str] = None,
        tool_calls: Optional[List[Union[ToolCall, Dict[str, Any]]]] = None,
        function_call: Optional[Union[FunctionCall, Dict[str, Any]]] = None
    ) -> ChatCompletionMessage:
        """Create an assistant message with automatic tool call conversion.
        
        This helper method makes it easy to create assistant messages that are
        fully compatible with OpenAI's format, automatically converting ToolCall
        objects to the proper dictionary format when needed.
        
        Args:
            content: The message content
            tool_calls: List of tool calls (ToolCall objects or dicts)
            function_call: Function call (FunctionCall object or dict)
            
        Returns:
            ChatCompletionMessage object that can be used in conversation history
        """
        # Convert tool calls to proper format
        converted_tool_calls = None
        if tool_calls:
            converted_tool_calls = []
            for tool_call in tool_calls:
                if hasattr(tool_call, 'to_dict'):
                    converted_tool_calls.append(tool_call.to_dict())
                else:
                    converted_tool_calls.append(tool_call)
        
        # Convert function call to proper format
        converted_function_call = None
        if function_call:
            if hasattr(function_call, 'to_dict'):
                converted_function_call = function_call.to_dict()
            else:
                converted_function_call = function_call
        
        return ChatCompletionMessage(
            role="assistant",
            content=content,
            tool_calls=converted_tool_calls,
            function_call=converted_function_call
        )

    def create(
        self,
        model: str,
        messages: List[Union[Dict[str, Any], BaseModel]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stop: Optional[Union[str, List[str]]] = None,
        stream: bool = False,
        user: Optional[str] = None,
        n: Optional[int] = None,
        logprobs: Optional[bool] = None,
        top_logprobs: Optional[int] = None,
        response_format: Optional[Dict[str, str]] = None,
        seed: Optional[int] = None,
        tools: Optional[Union[List[Dict[str, Any]], List, str]] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = "auto",
        hide_think: bool = False,
    ) -> Union[ChatCompletion, Iterator[ChatCompletionChunk]]:
        """Create a chat completion.

        Args:
            model: Model ID to use.
            messages: List of message dicts (role/content pairs).
            temperature: Sampling temperature.
            max_tokens: Maximum tokens to generate.
            top_p: Nucleus sampling parameter.
            frequency_penalty: Penalize frequent tokens.
            presence_penalty: Penalize repeated topics.
            stop: Stop sequence(s).
            stream: Whether to stream the response.
            user: User identifier.
            n: Number of completions.
            logprobs: Include logprobs in response.
            top_logprobs: Number of top logprobs to return.
            response_format: Response format options.
            seed: Random seed for deterministic results.
            tools: Tool/function call definitions. Supports multiple formats:
                - List[Dict]: OpenAI tool format (existing)
                - List[Fn]: Fn objects from @tools decorator
                - str: Category name to get tools from registry
            tool_choice: Tool selection strategy.
            hide_think: If True, the API will filter out <think> and <ser> blocks from the output (handled server-side).
        Returns:
            ChatCompletion or an iterator of ChatCompletionChunk (OpenAI-compatible objects).
        Raises:
            HAIError or its subclasses on error.
        """
        # Convert messages to dictionaries automatically
        converted_messages = self._convert_messages_to_dicts(messages)
        
        # Convert tools to OpenAI format
        converted_tools = self._convert_tools_parameter(tools)
        
        json_data = {
            "model": model,
            "messages": converted_messages,
            "stream": stream
        }
        
        optional_params = {
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "frequency_penalty": frequency_penalty,
            "presence_penalty": presence_penalty,
            "stop": stop,
            "user": user,
            "n": n,
            "logprobs": logprobs,
            "top_logprobs": top_logprobs,
            "response_format": response_format,
            "seed": seed,
            "tools": converted_tools,
            "tool_choice": tool_choice if converted_tools else None,
            "hideThink": hide_think,
        }
        json_data.update({k: v for k, v in optional_params.items() if v is not None})

        response = self._client._request(
            "POST",
            "/chat/completions",
            json_data=json_data,
            stream=stream
        )

        if stream:
            return self._handle_stream_response(cast(requests.Response, response))
        return self._handle_response(cast(Dict[str, Any], response))


    def _convert_tools_parameter(
        self,
        tools: Optional[Union[List[Dict[str, Any]], List, str]]
    ) -> Optional[List[Dict[str, Any]]]:
        """Convert various tools formats to OpenAI format.
        
        Args:
            tools: Tools in various formats
            
        Returns:
            List of OpenAI-compatible tool definitions or None
        """
        if tools is None:
            return None
        
        # Cache the tools configuration for direct calling
        # Store both in _tools_config (legacy) and _last_chat_tools_config (new fallback)
        self._client._last_chat_tools_config = tools
        self._client._mcp_manager = None  # Clear cached MCP manager
        
        try:
            from .tools.compatibility import ensure_openai_format
            return ensure_openai_format(tools)
        except ImportError:
            # Fallback if tools module not available - treat as legacy format
            import warnings
            warnings.warn(
                "Tools module not available. Install optional dependencies with: pip install 'HelpingAI[mcp]'. "
                "Using legacy tool format."
            )
            if isinstance(tools, list):
                return tools
            return None
        except Exception as e:
            # Enhanced error handling with better guidance
            import warnings
            error_msg = str(e)
            
            # Provide more helpful error messages based on the error type
            if "Unknown built-in tool" in error_msg:
                available_tools = "code_interpreter, web_search"
                warnings.warn(
                    f"Tool conversion failed: {e}. "
                    f"Available built-in tools: {available_tools}. "
                    f"For custom tools, use OpenAI tool format. Using legacy behavior."
                )
            elif "Unsupported tool item type" in error_msg:
                warnings.warn(
                    f"Tool conversion failed: {e}. "
                    f"Tools must be strings (built-in tool names), dicts (OpenAI format), "
                    f"or MCP server configs. Using legacy behavior."
                )
            elif "Unsupported tools format" in error_msg:
                warnings.warn(
                    f"Tool conversion failed: {e}. "
                    f"Supported formats: None, string (category), List[Dict] (OpenAI format), "
                    f"List[str] (built-in tools), or List[Fn]. Using legacy behavior."
                )
            elif "Failed to initialize MCP tools" in error_msg:
                # Handle MCP-specific errors with helpful guidance
                if "uvx" in error_msg:
                    warnings.warn(
                        f"Tool conversion failed: {e}. "
                        f"Install uvx with: pip install uvx. Using legacy behavior."
                    )
                elif "npx" in error_msg:
                    warnings.warn(
                        f"Tool conversion failed: {e}. "
                        f"Install Node.js and npm to use npx commands. Using legacy behavior."
                    )
                elif "fileno" in error_msg:
                    warnings.warn(
                        f"Tool conversion failed: {e}. "
                        f"This may be due to a subprocess issue. Check MCP server configuration. Using legacy behavior."
                    )
                else:
                    warnings.warn(f"Tool conversion failed: {e}. Using legacy behavior.")
            else:
                warnings.warn(f"Tool conversion failed: {e}. Using legacy behavior.")
            
            # Fallback to legacy behavior - filter out problematic items
            if isinstance(tools, list):
                # Filter out MCP server configs and other problematic items
                filtered_tools = []
                for item in tools:
                    if isinstance(item, str):
                        # Keep string tools (built-in tool names) but warn
                        filtered_tools.append({
                            "type": "function",
                            "function": {
                                "name": item,
                                "description": f"Built-in tool: {item}",
                                "parameters": {"type": "object", "properties": {}, "required": []}
                            }
                        })
                    elif isinstance(item, dict) and "type" in item and item.get("type") == "function":
                        # Keep valid OpenAI format tools
                        filtered_tools.append(item)
                    # Skip MCP server configs and other problematic items
                
                return filtered_tools if filtered_tools else None
            return None

    def execute_tool_calls(
        self,
        message: ChatCompletionMessage,
        registry=None
    ) -> List[Dict[str, Any]]:
        """Execute all tool calls in a message and return results.
        
        Args:
            message: Message containing tool calls
            registry: Tool registry to use (uses global if None)
            
        Returns:
            List of tool execution results with format:
            [{"tool_call_id": str, "result": Any, "error": str}]
        """
        if not message.tool_calls:
            return []

        results = []
        for tool_call in message.tool_calls:
            try:
                # Try to execute using enhanced ToolFunction if available
                if hasattr(tool_call.function, 'call_with_registry'):
                    result = tool_call.function.call_with_registry(registry)
                else:
                    # Fallback to basic execution (would need manual implementation)
                    result = {"error": "Tool execution not implemented for this tool"}
                
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

    def create_tool_response_message(
        self,
        tool_call_id: str,
        content: str
    ) -> Dict[str, Any]:
        """Create a tool response message for conversation history.
        
        Args:
            tool_call_id: ID of the tool call being responded to
            content: Tool execution result as string
            
        Returns:
            Message dict in OpenAI format
        """
        return {
            "role": "tool",
            "tool_call_id": tool_call_id,
            "content": content
        }

    def create_tool_response_messages(
        self,
        execution_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Create tool response messages from execution results.
        
        Args:
            execution_results: Results from execute_tool_calls
            
        Returns:
            List of tool response messages
        """
        import json
        messages = []
        for result in execution_results:
            if result["error"] is None:
                content = json.dumps(result["result"]) if result["result"] is not None else "null"
            else:
                content = f"Error: {result['error']}"
            
            messages.append(self.create_tool_response_message(
                result["tool_call_id"],
                content
            ))
        return messages

    def _handle_response(self, data: Dict[str, Any]) -> ChatCompletion:
        """Process a non-streaming response into a ChatCompletion object."""
        choices = []
        for choice_data in data.get("choices", []):
            message_data = choice_data.get("message", {})
            tool_calls = None
            if "tool_calls" in message_data and message_data["tool_calls"] is not None:
                tool_calls = []
                for tc in message_data["tool_calls"]:
                    if tc is not None and "function" in tc and tc["function"] is not None:
                        tool_calls.append(ToolCall(
                            id=tc.get("id", ""),
                            type=tc.get("type", "function"),
                            function=ToolFunction(
                                name=tc["function"].get("name", ""),
                                arguments=tc["function"].get("arguments", "")
                            )
                        ))

            function_call = None
            if "function_call" in message_data and message_data["function_call"] is not None:
                fc = message_data["function_call"]
                if fc is not None:
                    function_call = FunctionCall(
                        name=fc.get("name", ""),
                        arguments=fc.get("arguments", "")
                    )

            message = ChatCompletionMessage(
                role=message_data.get("role", ""),
                content=message_data.get("content"),
                function_call=function_call,
                tool_calls=tool_calls
            )
            
            choice = Choice(
                index=choice_data.get("index", 0),
                message=message,
                finish_reason=choice_data.get("finish_reason"),
                logprobs=choice_data.get("logprobs")
            )
            choices.append(choice)

        usage = None
        if "usage" in data:
            usage = CompletionUsage(
                completion_tokens=data["usage"].get("completion_tokens", 0),
                prompt_tokens=data["usage"].get("prompt_tokens", 0),
                total_tokens=data["usage"].get("total_tokens", 0)
            )

        return ChatCompletion(
            id=data.get("id", ""),
            created=data.get("created", 0),
            model=data.get("model", ""),
            choices=choices,
            system_fingerprint=data.get("system_fingerprint"),
            usage=usage
        )

    def _handle_stream_response(self, response: requests.Response) -> Iterator[ChatCompletionChunk]:
        """Handle streaming response and yield ChatCompletionChunk objects."""
        for line in response.iter_lines():
            if line:
                if line.strip() == b"data: [DONE]":
                    break
                try:
                    line = line.decode("utf-8")
                    if line.startswith("data: "):
                        data = json.loads(line[6:])
                        choices = []
                        for choice_data in data.get("choices", []):
                            delta_data = choice_data.get("delta", {})
                            
                            tool_calls = None
                            if "tool_calls" in delta_data and delta_data["tool_calls"] is not None:
                                tool_calls = []
                                for tc in delta_data["tool_calls"]:
                                    if tc is not None and "function" in tc and tc["function"] is not None:
                                        tool_calls.append(ToolCall(
                                            id=tc.get("id", ""),
                                            type=tc.get("type", "function"),
                                            function=ToolFunction(
                                                name=tc["function"].get("name", ""),
                                                arguments=tc["function"].get("arguments", "")
                                            )
                                        ))

                            function_call = None
                            if "function_call" in delta_data and delta_data["function_call"] is not None:
                                fc = delta_data["function_call"]
                                if fc is not None:
                                    function_call = FunctionCall(
                                        name=fc.get("name", ""),
                                        arguments=fc.get("arguments", "")
                                    )

                            delta = ChoiceDelta(
                                content=delta_data.get("content"),
                                function_call=function_call,
                                role=delta_data.get("role"),
                                tool_calls=tool_calls
                            )
                            
                            choice = Choice(
                                index=choice_data.get("index", 0),
                                delta=delta,
                                finish_reason=choice_data.get("finish_reason"),
                                logprobs=choice_data.get("logprobs")
                            )
                            choices.append(choice)

                        yield ChatCompletionChunk(
                            id=data.get("id", ""),
                            created=data.get("created", 0),
                            model=data.get("model", ""),
                            choices=choices,
                            system_fingerprint=data.get("system_fingerprint")
                        )
                except Exception as e:
                    raise HAIError(f"Error parsing stream: {str(e)}")


class Chat:
    """Chat API interface for the HelpingAI client.

    Access chat completions via the `completions` property.
    """
    def __init__(self, client: "HAI") -> None:
        self.completions: ChatCompletions = ChatCompletions(client)

class HAI(BaseClient):
    """HAI API client for the HelpingAI platform.

    This is the main entry point for interacting with the HelpingAI API.
    """
    
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        organization: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 60.0,
    ) -> None:
        """Initialize HAI client.

        Args:
            api_key: Your API key. Find it at https://helpingai.co/dashboard
            organization: Optional organization ID for API requests
            base_url: Override the default API base URL
            timeout: Timeout for API requests in seconds
        """
        super().__init__(api_key, organization, base_url, timeout)
        self.chat: Chat = Chat(self)
        self.models: Models = Models(self)
        self._tools_config: Optional[Union[List[Dict[str, Any]], List, str]] = None
        self._last_chat_tools_config: Optional[Union[List[Dict[str, Any]], List, str]] = None
        self._mcp_manager = None
        
    def configure_tools(self, tools: Optional[Union[List[Dict[str, Any]], List, str]]) -> None:
        """Configure tools for this client instance.
        
        This makes tools available for direct calling via client.call().
        
        Args:
            tools: Tools configuration in any supported format:
                - List containing MCP server configs, built-in tool names, OpenAI format tools
                - String identifier for built-in tools
                - None to clear tools configuration
                
        Example:
            client.configure_tools([
                {'mcpServers': {
                    'time': {'command': 'uvx', 'args': ['mcp-server-time']},
                    'fetch': {'command': 'uvx', 'args': ['mcp-server-fetch']}
                }},
                'code_interpreter',
                'web_search'
            ])
        """
        self._tools_config = tools
        # Clear cached MCP manager to force reinitialization
        self._mcp_manager = None
        # Clear cached chat tools since we're explicitly configuring tools
        self._last_chat_tools_config = None
    
    def _get_effective_tools_config(self) -> Optional[Union[List[Dict[str, Any]], List, str]]:
        """Get effective tools configuration from instance configuration or recent chat.completions.create() call.
        
        This method provides automatic fallback to tools used in the most recent chat.completions.create() call,
        enabling seamless tool calling workflow where users can call tools directly after using them in chat completions.
        
        Priority order:
        1. Instance-level tools configuration (set via configure_tools())
        2. Tools from most recent chat.completions.create() call (cached automatically)
        
        Returns:
            Tools configuration from instance, recent chat call, or None if not configured
        """
        # First priority: explicitly configured tools via configure_tools()
        if self._tools_config is not None:
            return self._tools_config
            
        # Second priority: tools from most recent chat.completions.create() call
        # This enables the workflow: chat.completions.create(tools=...) -> client.call(tool_name, args)
        if hasattr(self, '_last_chat_tools_config') and self._last_chat_tools_config is not None:
            return self._last_chat_tools_config
            
        return None
    
    
            
    def _convert_tools_parameter(
        self,
        tools: Optional[Union[List[Dict[str, Any]], List, str]]
    ) -> Optional[List[Dict[str, Any]]]:
        """Convenience method to access ChatCompletions tool conversion.
        
        Args:
            tools: Tools in various formats
            
        Returns:
            List of OpenAI-compatible tool definitions or None
        """
        return self.chat.completions._convert_tools_parameter(tools)
        
    def call(self, tool_name: str, arguments: Union[Dict[str, Any], str, set], tools: Optional[Union[List[Dict[str, Any]], List, str]] = None) -> Any:
        """
        Directly call a tool by name with the given arguments.
        
        This method provides a convenient way to execute tools without having to
        manually use get_registry() and Fn objects. It supports:
        - Tools registered via @tools decorator
        - Built-in tools (code_interpreter, web_search)
        - MCP tools (if configured)
        
        Args:
            tool_name: Name of the tool to call
            arguments: Arguments to pass to the tool (dict, JSON string, or other)
            tools: Optional tools configuration to automatically configure before calling
            
        Returns:
            Result of the tool execution
            
        Raises:
            ValueError: If the tool is not found or arguments are invalid
            ToolExecutionError: If the tool execution fails
        """
        import json
        from typing import Union
        
        # Automatically configure tools if provided
        if tools is not None:
            self.configure_tools(tools)
        
        # Import here to avoid circular imports
        from .tools import get_registry
        from .tools.builtin_tools import get_builtin_tool_class, is_builtin_tool
        from .tools.mcp_manager import MCPManager
        
        # Enhanced argument processing with better error handling
        processed_args = self._process_arguments(arguments, tool_name)
        
        # First, try to get the tool from the main registry
        tool = get_registry().get_tool(tool_name)
        if tool:
            result = tool.call(processed_args)
            return result
        
        # If not found, check if it's a built-in tool
        if is_builtin_tool(tool_name):
            builtin_class = get_builtin_tool_class(tool_name)
            if builtin_class:
                # Create an instance of the built-in tool
                builtin_tool = builtin_class()
                # Convert it to an Fn object and call it
                fn_tool = builtin_tool.to_fn()
                result = fn_tool.call(processed_args)
                return result
        
        # If not found, check if it's an MCP tool using effective configuration
        # MCP tools are named with pattern: {server_name}-{tool_name}
        effective_tools_config = self._get_effective_tools_config()
        if effective_tools_config:
            try:
                # Initialize MCP manager with effective configuration if needed
                if not self._mcp_manager:
                    self._mcp_manager = self._get_mcp_manager_for_tools(effective_tools_config)
                
                if self._mcp_manager and self._mcp_manager.clients:
                    # Check if any MCP client has this tool
                    for client_id, client in self._mcp_manager.clients.items():
                        if hasattr(client, 'tools'):
                            for mcp_tool in client.tools:
                                # Extract server name from client_id (format: {server_name}_{uuid})
                                server_name = client_id.split('_')[0]
                                expected_tool_name = f"{server_name}-{mcp_tool.name}"
                                
                                if expected_tool_name == tool_name:
                                    # Found the MCP tool, create an Fn and call it
                                    fn_tool = self._mcp_manager._create_mcp_tool_fn(
                                        name=tool_name,
                                        client_id=client_id,
                                        mcp_tool_name=mcp_tool.name,
                                        description=mcp_tool.description if hasattr(mcp_tool, 'description') else f"MCP tool: {tool_name}",
                                        parameters=mcp_tool.inputSchema if hasattr(mcp_tool, 'inputSchema') else {'type': 'object', 'properties': {}, 'required': []}
                                    )
                                    result = fn_tool.call(processed_args)
                                    return result
            except ImportError:
                # MCP package not available, skip MCP tool checking
                pass
        
        # If still not found, provide a helpful error message with guidance
        error_msg = f"Tool '{tool_name}' not found"
        
        # Check if this looks like an MCP tool name pattern
        if '-' in tool_name and effective_tools_config:
            error_msg += f". Tool '{tool_name}' appears to be an MCP tool but MCP servers may not be properly initialized. Check that the MCP server is running and accessible."
        elif '-' in tool_name and not effective_tools_config:
            error_msg += f". Tool '{tool_name}' appears to be an MCP tool but no tools are configured."
        elif not effective_tools_config:
            error_msg += ". No tools are currently configured."
        else:
            error_msg += " in registry, built-in tools, or configured MCP tools"
        
        # Add helpful guidance based on the situation
        if not effective_tools_config:
            error_msg += "\n\nTo use tools with client.call(), you have two options:"
            error_msg += "\n1. First call chat.completions.create() with tools, then call client.call():"
            error_msg += "\n   response = client.chat.completions.create(model='gpt-4', messages=[...], tools=[...])"
            error_msg += "\n   result = client.call('tool_name', {'arg': 'value'})"
            error_msg += "\n2. Configure tools directly on the client:"
            error_msg += "\n   client.configure_tools([...])  # Then use client.call()"
            
        raise ValueError(error_msg)
    
    def _get_mcp_manager_for_tools(self, tools_config: Optional[Union[List[Dict[str, Any]], List, str]] = None) -> Optional[Any]:
        """Get or create MCP manager using specified or cached tools configuration.
        
        Args:
            tools_config: Optional tools configuration to use. If None, uses effective config.
        
        Returns:
            MCPManager instance with tools configured, or None if no MCP config found
        """
        if tools_config is None:
            tools_config = self._get_effective_tools_config()
            
        if not tools_config:
            return None
            
        try:
            from .tools.mcp_manager import MCPManager
            
            # Find MCP server configs in the tools configuration
            mcp_configs = []
            if isinstance(tools_config, list):
                for item in tools_config:
                    if isinstance(item, dict) and "mcpServers" in item:
                        mcp_configs.append(item)
            
            if not mcp_configs:
                return None
            
            # Initialize MCP manager with the found configurations
            manager = MCPManager()
            
            # Initialize each MCP config (this populates manager.clients)
            for config in mcp_configs:
                try:
                    manager.init_config(config)  # This returns tools but also populates clients
                except Exception as e:
                    # If initialization fails, continue with other configs
                    print(f"Warning: Failed to initialize MCP config {config}: {e}")
                    continue
            
            return manager if manager.clients else None
            
        except ImportError:
            return None
    
    def _process_arguments(self, arguments: Union[Dict[str, Any], str, set], tool_name: str) -> Dict[str, Any]:
        """
        Process and validate arguments for tool execution.
        
        This method handles common user mistakes like:
        - Passing a set instead of a dict (from {json_string} syntax)
        - Passing a JSON string that needs parsing
        - Other argument format issues
        
        Args:
            arguments: Raw arguments in various formats
            tool_name: Name of the tool (for error messages)
            
        Returns:
            Processed arguments as a dictionary
            
        Raises:
            ValueError: If arguments cannot be processed
        """
        import json
        
        # Handle None or empty arguments
        if arguments is None:
            return {}
        
        # If it's already a dict, return as-is
        if isinstance(arguments, dict):
            return arguments
        
        # Handle common mistake: user used {json_string} which creates a set
        if isinstance(arguments, set):
            if len(arguments) == 1:
                # Try to extract and parse the single item
                json_str = next(iter(arguments))
                if isinstance(json_str, str):
                    try:
                        parsed = json.loads(json_str)
                        if isinstance(parsed, dict):
                            print(f"⚠️  Note: Detected set argument for '{tool_name}'. Use 'json.loads(tool_call.function.arguments)' instead of '{{tool_call.function.arguments}}'")
                            return parsed
                    except json.JSONDecodeError:
                        pass
            
            raise ValueError(
                f"Invalid arguments for tool '{tool_name}': received a set {arguments}. "
                f"Common mistake: use 'json.loads(tool_call.function.arguments)' instead of '{{tool_call.function.arguments}}'"
            )
        
        # Handle JSON string
        if isinstance(arguments, str):
            try:
                parsed = json.loads(arguments)
                if isinstance(parsed, dict):
                    return parsed
                else:
                    raise ValueError(f"Invalid arguments for tool '{tool_name}': JSON string must parse to a dictionary, got {type(parsed)}")
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON arguments for tool '{tool_name}': {e}")
        
        # Handle other types
        raise ValueError(
            f"Invalid arguments for tool '{tool_name}': expected dict, JSON string, but got {type(arguments)}. "
            f"Received: {arguments}"
        )