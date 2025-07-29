"""Base client with common functionality for the HelpingAI API.

Handles authentication, session management, and low-level HTTP requests.
"""

import os
import platform
from typing import Optional, Dict, Any

import requests

from ..version import VERSION
from ..error import (
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