"""HAI API client with OpenAI-like interface."""

import json
import platform
import os
from typing import Optional, Dict, Any, Union, Iterator, List, Literal, cast

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

class BaseClient:
    """Base client with common functionality."""
    def __init__(
        self,
        api_key: Optional[str] = None,
        organization: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 60.0,
    ) -> None:
        self.api_key = api_key or os.getenv("HAI_API_KEY")
        if not self.api_key:
            raise NoAPIKeyError()
        
        self.organization = organization
        self.base_url = (base_url or "https://api.helpingai.co/v1").rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()

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
        """Make a request to the HAI API."""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": f"hai-python/{VERSION} "
                         f"Python/{platform.python_version()} "
                         f"{platform.system()}/{platform.release()}"
        }
        
        if auth_required:
            headers["Authorization"] = f"Bearer {self.api_key}"
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
                
                error_message = error_data.get("error", {}).get("message", "Unknown error")
                error_type = error_data.get("error", {}).get("type")
                error_code = error_data.get("error", {}).get("code")
                
                if response.status_code == 401:
                    raise InvalidAPIKeyError(response.status_code, response.headers)
                elif response.status_code == 400:
                    if "model" in error_message.lower():
                        raise InvalidModelError(error_message.split("'")[1], response.status_code, response.headers)
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
    """Chat completions API interface."""
    def __init__(self, client: "HAI") -> None:
        self._client = client

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
    ) -> Union[ChatCompletion, Iterator[ChatCompletionChunk]]:
        """Create a chat completion."""
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
            return self._handle_stream_response(cast(requests.Response, response))
        return self._handle_response(cast(Dict[str, Any], response))

    def _handle_response(self, data: Dict[str, Any]) -> ChatCompletion:
        """Process a non-streaming response."""
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
        """Handle streaming response."""
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

class Chat:
    """Chat API interface."""
    def __init__(self, client: "HAI") -> None:
        self.completions = ChatCompletions(client)

class HAI(BaseClient):
    """HAI API client."""
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
        self.chat = Chat(self)
        self.models = Models(self)
