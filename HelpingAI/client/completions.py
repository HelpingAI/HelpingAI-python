"""Chat completions API interface for the HelpingAI client.

Use this to create chat completions, including streaming and function/tool calling.
"""

import json
from typing import Optional, Dict, Any, Union, Iterator, List, cast, TYPE_CHECKING

import requests

from ..error import HAIError
from ..base_models import (
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

if TYPE_CHECKING:
    from .main import HAI


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
        
        This helper method makes it easy to create assistant messages that follow
        the standard function-calling format, automatically converting ToolCall
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
        hide_think: Optional[bool] = None,
        **kwargs
    ) -> Union[ChatCompletion, Iterator[ChatCompletionChunk]]:
        """
        Create a chat completion (compatible with standard function-calling SDK patterns).
        Accepts all standard function-calling parameters via explicit arguments and **kwargs for future compatibility.
        Required:
            model: Model ID to use.
            messages: List of message dicts (role/content pairs).
        Optional:
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
                - List[Dict]: Standard tool definition format (existing)
                - List[Fn]: Fn objects from @tools decorator
                - str: Category name to get tools from registry
            tool_choice: Tool selection strategy.
            hide_think: If True, the API will filter out <think> and <ser> blocks from the output (handled server-side).
            Any other standard function-calling parameter via **kwargs.
        Returns:
            ChatCompletion or an iterator of ChatCompletionChunk (standard completion objects).
        Raises:
            HAIError or its subclasses on error.
        """
        # Convert messages to dictionaries automatically
        converted_messages = self._convert_messages_to_dicts(messages)

        # Convert tools to the standard tool calling format
        converted_tools = self._convert_tools_parameter(tools)

        json_data = {
            "model": model,
            "messages": converted_messages,
            "stream": stream,
        }

        # Only add tools/tool_choice if tools were converted to a valid list
        if converted_tools is not None:
            json_data["tools"] = converted_tools
            # Normalize tool_choice if tools compatibility helpers are available
            normalized_tool_choice = tool_choice
            try:
                from ..tools.compatibility import normalize_tool_choice
                normalized_tool_choice = normalize_tool_choice(tool_choice, converted_tools)
            except Exception:
                # If compatibility helpers aren't available, use the original value
                normalized_tool_choice = tool_choice

            if normalized_tool_choice is not None:
                json_data["tool_choice"] = normalized_tool_choice

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
            "hideThink": hide_think,
        }
        json_data.update({k: v for k, v in optional_params.items() if v is not None})

        # Add all other kwargs except None values
        for k, v in kwargs.items():
            if v is not None:
                json_data[k] = v

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
        """Convert various tools formats to the standard tool calling format.
        
        Args:
            tools: Tools in various formats
            
            Returns:
            List of standard tool definitions or None
        """
        if tools is None:
            return None
        
        # Cache the tools configuration for direct calling
        # Store both in _tools_config (legacy) and _last_chat_tools_config (new fallback)
        self._client._last_chat_tools_config = tools
        self._client._mcp_manager = None  # Clear cached MCP manager
        
        try:
            from ..tools.compatibility import ensure_tool_call_format
            return ensure_tool_call_format(tools)
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
                    f"For custom tools, use the standard tool definition format. Using legacy behavior."
                )
            elif "Unsupported tool item type" in error_msg:
                warnings.warn(
                    f"Tool conversion failed: {e}. "
                    f"Tools must be strings (built-in tool names), dicts (standard tool definition schema), "
                    f"or MCP server configs. Using legacy behavior."
                )
            elif "Unsupported tools format" in error_msg:
                warnings.warn(
                    f"Tool conversion failed: {e}. "
                    f"Supported formats: None, string (category), List[Dict] (standard tool definitions), "
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
                        # Keep valid standard tool definitions
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
            Message dict in the standard tool calling format
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