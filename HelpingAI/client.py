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
                    # Add hint for generic 400 errors when not streaming
                    if not stream and "Request failed with status code" in error_message:
                        error_message += ". This model or endpoint might require streaming. Try setting stream=True."
                    raise InvalidRequestError(error_message, status_code=response.status_code, headers=response.headers)
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

    def _filter_think_ser_blocks(self, text: Optional[str]) -> Optional[str]:
        """Remove <think>...</think> and <ser>...</ser> blocks from text and clean up excessive line gaps."""
        if not text:
            return text
        import re
        
        # Remove think and ser blocks
        text = re.sub(r"<think>[\s\S]*?</think>", "", text)
        text = re.sub(r"<ser>[\s\S]*?</ser>", "", text)
        
        # Fix broken words that may have been split across lines
        text = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", text)
        
        # Remove excessive empty lines (more than 2 consecutive newlines become 2)
        text = re.sub(r"\n{3,}", "\n\n", text)
        
        # Remove extra spaces that might be left behind
        text = re.sub(r" {2,}", " ", text)
        text = text.strip()

        return text

    def _filter_completion(self, completion: ChatCompletion) -> ChatCompletion:
        """Return a ChatCompletion with <think> and <ser> blocks removed from message content."""
        filtered_choices = []
        for choice in completion.choices:
            message = choice.message
            filtered_content = self._filter_think_ser_blocks(message.content)
            filtered_message = ChatCompletionMessage(
                role=message.role,
                content=filtered_content,
                function_call=message.function_call,
                tool_calls=message.tool_calls
            )
            filtered_choice = Choice(
                index=choice.index,
                message=filtered_message,
                finish_reason=choice.finish_reason,
                logprobs=choice.logprobs
            )
            filtered_choices.append(filtered_choice)
        return ChatCompletion(
            id=completion.id,
            created=completion.created,
            model=completion.model,
            choices=filtered_choices,
            system_fingerprint=completion.system_fingerprint,            
            usage=completion.usage
        )

    def _filter_stream_chunk(self, chunk: ChatCompletionChunk, state: Dict[str, bool]) -> ChatCompletionChunk:
        """Return a ChatCompletionChunk with <think> and <ser> blocks removed from delta content."""
        filtered_choices = []
        for choice in chunk.choices:
            delta = choice.delta
            content = delta.content
            filtered_content = self._filter_streaming_content(content, state) if content else content
            
            filtered_delta = ChoiceDelta(
                content=filtered_content,
                function_call=delta.function_call,
                role=delta.role,
                tool_calls=delta.tool_calls
            )
            filtered_choice = Choice(
                index=choice.index,
                delta=filtered_delta,
                finish_reason=choice.finish_reason,
                logprobs=choice.logprobs
            )
            filtered_choices.append(filtered_choice)
        return ChatCompletionChunk(
            id=chunk.id,
            created=chunk.created,
            model=chunk.model,
            choices=filtered_choices,
            system_fingerprint=chunk.system_fingerprint
        )

    def _filter_streaming_content(self, content: str, state: Dict[str, bool]) -> Optional[str]:
        """Filter streaming content based on reasoning state, similar to the webscout example."""
        if not content:
            return content
        
        result = ""
        i = 0
        while i < len(content):
            # Check for opening tags - including partial matches at chunk boundaries
            remaining = content[i:]
            
            if remaining.startswith("<think>"):
                state["is_reasoning"] = True
                i += 7
                continue
            elif remaining.startswith("</think>"):
                state["is_reasoning"] = False
                i += 8
                continue
            elif remaining.startswith("<ser>"):
                state["is_ser"] = True
                i += 5
                continue
            elif remaining.startswith("</ser>"):
                state["is_ser"] = False
                i += 6
                continue
            # Handle partial tag matches that might be split across chunks
            elif remaining.startswith("<think") or remaining.startswith("<ser") or remaining.startswith("</think") or remaining.startswith("</ser"):
                # If we find a partial tag, assume we're entering a reasoning/ser block
                if remaining.startswith("<think") or remaining.startswith("<ser"):
                    if remaining.startswith("<think"):
                        state["is_reasoning"] = True
                    else:
                        state["is_ser"] = True
                else:  # closing tags
                    if remaining.startswith("</think"):
                        state["is_reasoning"] = False
                    else:
                        state["is_ser"] = False
                # Skip the rest of this chunk to avoid partial content
                break
                
            # If we're not in reasoning or ser mode, add the character
            if not state["is_reasoning"] and not state["is_ser"]:
                result += content[i]
            
            i += 1
        
        # Return None if result is empty or whitespace-only to avoid sending empty chunks
        return result.strip() if result.strip() else None

    def create(
        self,
        model: str,
        messages: List[Dict[str, str]],
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
        tools: Optional[List[Dict[str, Any]]] = None,
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
            tools: Tool/function call definitions.
            tool_choice: Tool selection strategy.
            hide_think: If True, filter out <think> and <ser> blocks from the output (streaming or not).
        Returns:
            ChatCompletion or an iterator of ChatCompletionChunk (OpenAI-compatible objects).
        Raises:
            HAIError or its subclasses on error.
        """
        json_data = {
            "model": model,
            "messages": messages,
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
            "tools": tools,
            "tool_choice": tool_choice if tools else None,
        }
        json_data.update({k: v for k, v in optional_params.items() if v is not None})

        response = self._client._request(
            "POST",
            "/chat/completions",
            json_data=json_data,
            stream=stream
        )

        if stream:
            stream_iter = self._handle_stream_response(cast(requests.Response, response))
            if hide_think:
                return self._create_filtered_stream_generator(stream_iter)
            return stream_iter
        completion = self._handle_response(cast(Dict[str, Any], response))
        if hide_think:
            return self._filter_completion(completion)
        return completion

    def _hide_think_from_completion(self, completion: ChatCompletion) -> str:
        # Deprecated: no longer used, kept for backward compatibility if needed
        def remove_blocks(text: Optional[str]) -> str:
            if not text:
                return ""
            import re
            text = re.sub(r"<think>[\s\S]*?</think>", "", text)
            text = re.sub(r"<ser>[\s\S]*?</ser>", "", text)
            return text
        visible = []
        for choice in completion.choices:
            if choice.message and choice.message.content:
                visible.append(remove_blocks(choice.message.content))
        return "\n".join(visible)

    def _handle_response(self, data: Dict[str, Any]) -> ChatCompletion:
        """Process a non-streaming response into a ChatCompletion object."""
        choices = []
        for choice_data in data.get("choices", []):
            message_data = choice_data.get("message", {})
            tool_calls = None
            if "tool_calls" in message_data:
                tool_calls = [
                    ToolCall(
                        id=tc.get("id", ""),
                        type=tc.get("type", "function"),
                        function=ToolFunction(
                            name=tc["function"]["name"],
                            arguments=tc["function"]["arguments"]
                        )
                    )
                    for tc in message_data["tool_calls"]
                ]

            function_call = None
            if "function_call" in message_data:
                function_call = FunctionCall(
                    name=message_data["function_call"]["name"],
                    arguments=message_data["function_call"]["arguments"]
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
                            if "tool_calls" in delta_data:
                                tool_calls = [
                                    ToolCall(
                                        id=tc.get("id", ""),
                                        type=tc.get("type", "function"),
                                        function=ToolFunction(
                                            name=tc["function"]["name"],
                                            arguments=tc["function"]["arguments"]
                                        )
                                    )
                                    for tc in delta_data["tool_calls"]
                                ]

                            function_call = None
                            if "function_call" in delta_data:
                                function_call = FunctionCall(
                                    name=delta_data["function_call"]["name"],
                                    arguments=delta_data["function_call"]["arguments"]
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

    def _create_filtered_stream_generator(self, stream_iter: Iterator[ChatCompletionChunk]) -> Iterator[ChatCompletionChunk]:
        """Create a generator that filters streaming chunks, cleans up whitespace, and handles partial tags."""
        is_in_think = False
        is_in_ser = False
        buffer = ""
        
        consecutive_newlines = 0
        last_char_was_space = False
        stream_started = False

        for chunk in stream_iter:
            new_choices = []
            should_yield_chunk = False

            for choice in chunk.choices:
                if choice.delta and choice.delta.content:
                    buffer += choice.delta.content
                    output_content = ""
                    processed_len = 0

                    while processed_len < len(buffer):
                        remaining = buffer[processed_len:]

                        if is_in_think:
                            if remaining.startswith("</think>"):
                                is_in_think = False
                                processed_len += 8
                                last_char_was_space = True
                                continue
                            if "</think>".startswith(remaining):
                                break
                            processed_len += 1
                            continue

                        if is_in_ser:
                            if remaining.startswith("</ser>"):
                                is_in_ser = False
                                processed_len += 6
                                last_char_was_space = True
                                continue
                            if "</ser>".startswith(remaining):
                                break
                            processed_len += 1
                            continue

                        if remaining.startswith("<think>"):
                            is_in_think = True
                            processed_len += 7
                            continue
                        
                        if remaining.startswith("<ser>"):
                            is_in_ser = True
                            processed_len += 5
                            continue

                        if "<think>".startswith(remaining) or "<ser>".startswith(remaining):
                            break

                        char = buffer[processed_len]
                        
                        if not stream_started and char.isspace():
                            processed_len += 1
                            continue
                        stream_started = True

                        if char == '\n':
                            consecutive_newlines += 1
                            if consecutive_newlines <= 2:
                                output_content += char
                            last_char_was_space = False
                        elif char.isspace():
                            if not last_char_was_space:
                                output_content += ' '
                            last_char_was_space = True
                        else:
                            consecutive_newlines = 0
                            last_char_was_space = False
                            output_content += char
                        
                        processed_len += 1

                    buffer = buffer[processed_len:]

                    if output_content:
                        should_yield_chunk = True
                        new_delta = ChoiceDelta(
                            content=output_content,
                            role=choice.delta.role,
                            function_call=choice.delta.function_call,
                            tool_calls=choice.delta.tool_calls
                        )
                        new_choice = Choice(
                            index=choice.index,
                            delta=new_delta,
                            finish_reason=choice.finish_reason,
                            logprobs=choice.logprobs
                        )
                        new_choices.append(new_choice)
                    elif choice.finish_reason:
                        should_yield_chunk = True
                        new_delta = ChoiceDelta(content=None, role=choice.delta.role, function_call=choice.delta.function_call, tool_calls=choice.delta.tool_calls)
                        new_choice = Choice(index=choice.index, delta=new_delta, finish_reason=choice.finish_reason, logprobs=choice.logprobs)
                        new_choices.append(new_choice)

                else:
                    should_yield_chunk = True
                    new_choices.append(choice)
            
            if should_yield_chunk:
                yield ChatCompletionChunk(
                    id=chunk.id,
                    created=chunk.created,
                    model=chunk.model,
                    choices=new_choices,
                    system_fingerprint=chunk.system_fingerprint
                )

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
