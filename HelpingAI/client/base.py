"""Base client with common functionality for the HelpingAI API.

Handles authentication, session management, and low-level HTTP requests.
"""

import os
import platform
import re
from typing import Optional, Dict, Any, Tuple, Union

import requests

from ..version import VERSION
from ..logging import get_logger
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
        self.logger = get_logger(__name__)

    def _parse_error_response(self, response: requests.Response) -> Tuple[str, Optional[str], Optional[str]]:
        """Parse error response and extract message, type, and code.
        
        Args:
            response: The HTTP response object
            
        Returns:
            Tuple of (error_message, error_type, error_code)
        """
        try:
            error_data = response.json()
        except (ValueError, requests.exceptions.JSONDecodeError):
            # If we can't parse JSON, try to get meaningful info from response
            content_preview = response.text[:200] if response.text else "No response content"
            return (
                f"HTTP {response.status_code}: {response.reason}. Response: {content_preview}",
                None,
                str(response.status_code)
            )
        
        # Handle different error response formats
        error_message = "Unknown error occurred"
        error_type = None
        error_code = None
        
        if isinstance(error_data.get("error"), dict):
            # Nested format: {"error": {"message": "...", "type": "...", "code": "..."}}
            error_obj = error_data.get("error", {})
            error_message = error_obj.get("message", error_message)
            error_type = error_obj.get("type")
            error_code = error_obj.get("code")
        elif isinstance(error_data.get("error"), str):
            # Flat format: {"error": "Request failed with status code 400"}
            error_message = error_data.get("error", error_message)
        else:
            # Alternative formats
            error_message = (
                error_data.get("message") or 
                error_data.get("detail") or 
                error_data.get("error_message") or
                str(error_data) if error_data else error_message
            )
            error_type = error_data.get("type") or error_data.get("error_type")
            error_code = error_data.get("code") or error_data.get("error_code")
        
        return error_message, error_type, error_code

    def _extract_model_name(self, error_message: str) -> Optional[str]:
        """Extract model name from error message using various patterns.
        
        Args:
            error_message: The error message to parse
            
        Returns:
            Model name if found, None otherwise
        """
        # Common patterns for model names in error messages
        patterns = [
            r"model\s+['\"]([^'\"]+)['\"]",  # model "name" or model 'name'
            r"['\"]([^'\"]*(?:preview|raw|nsfw|helvete|dhanishtha)[^'\"]*)['\"]",  # quoted model names with keywords
            r"Model\s+([^\s]+)\s+(?:not found|unavailable|invalid)",  # Model xyz not found
            r"Invalid model:\s*([^\s,]+)",  # Invalid model: xyz
            r"model_id['\"]?\s*:\s*['\"]([^'\"]+)['\"]",  # model_id: "name"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, error_message, re.IGNORECASE)
            if match:
                model_name = match.group(1).strip()
                if model_name and len(model_name) > 0:
                    return model_name
        
        return None

    def _should_suggest_streaming(self, error_message: str, stream: bool) -> bool:
        """Determine if streaming should be suggested based on error patterns.
        
        Args:
            error_message: The error message to analyze
            stream: Whether streaming was already enabled
            
        Returns:
            True if streaming should be suggested
        """
        if stream:  # Already streaming, don't suggest again
            return False
            
        # Comprehensive streaming indicators
        streaming_indicators = [
            "stream",
            "tool_call",
            "function_call", 
            "tools",
            "functions",
            "timeout",
            "too large",
            "response size",
            "buffer",
            "partial",
            "chunk",
            "incomplete",
            "connection",
            "network",
            "502",
            "503",
            "504"
        ]
        
        return any(indicator in error_message.lower() for indicator in streaming_indicators)

    def _enhance_error_message(self, error_message: str, status_code: int, stream: bool, path: str) -> str:
        """Enhance error message with helpful suggestions and context.
        
        Args:
            error_message: Original error message
            status_code: HTTP status code
            stream: Whether streaming was enabled
            path: API endpoint path
            
        Returns:
            Enhanced error message with suggestions
        """
        enhanced_message = error_message
        suggestions = []
        
        # Add specific suggestions based on error patterns and context
        if status_code == 400:
            if self._should_suggest_streaming(error_message, stream):
                suggestions.append("Try setting stream=True in your request")
            
            if "model" in error_message.lower():
                suggestions.append("Verify the model name is correct and available")
                suggestions.append("Use hai.models.list() to see available models")
            
            if "token" in error_message.lower() or "length" in error_message.lower():
                suggestions.append("Try reducing the input length or using a different model")
            
            if "/chat/completions" in path:
                suggestions.append("Check that your messages format is correct")
                suggestions.append("Ensure all required fields are provided")
        
        elif status_code == 401:
            suggestions.append("Check your API key is valid and properly set")
            suggestions.append("Make sure you're using the correct authentication header")
        
        elif status_code == 429:
            suggestions.append("Wait a moment before retrying")
            suggestions.append("Consider implementing exponential backoff")
        
        elif status_code >= 500:
            suggestions.append("This is a server-side issue - try again in a few moments")
            suggestions.append("Contact support if the issue persists")
        
        # Add suggestions to the message
        if suggestions:
            enhanced_message += f"\n\nSuggestions:\n" + "\n".join(f"• {s}" for s in suggestions)
        
        return enhanced_message

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
                # Parse error response using helper method
                error_message, error_type, error_code = self._parse_error_response(response)
                
                # Log error details for debugging
                self.logger.debug(
                    f"API Error - Status: {response.status_code}, Path: {path}, "
                    f"Message: {error_message}, Type: {error_type}, Code: {error_code}"
                )
                
                # Handle specific status codes with appropriate exceptions
                if response.status_code == 401:
                    # Authentication errors
                    enhanced_message = self._enhance_error_message(error_message, 401, stream, path)
                    raise InvalidAPIKeyError(response.status_code, response.headers)
                
                elif response.status_code == 400:
                    # Bad request errors - check for specific patterns
                    enhanced_message = self._enhance_error_message(error_message, 400, stream, path)
                    
                    # Handle model-specific errors
                    if "model" in error_message.lower():
                        model_name = self._extract_model_name(error_message)
                        if model_name:
                            raise InvalidModelError(model_name, response.status_code, response.headers)
                        else:
                            # Generic model error without extractable name
                            raise InvalidModelError("Unknown or invalid model", response.status_code, response.headers)
                    
                    raise InvalidRequestError(enhanced_message, status_code=response.status_code, headers=response.headers)
                
                elif response.status_code == 429:
                    # Rate limiting
                    enhanced_message = self._enhance_error_message(error_message, 429, stream, path)
                    raise TooManyRequestsError(response.status_code, response.headers)
                
                elif response.status_code == 503:
                    # Service unavailable
                    enhanced_message = self._enhance_error_message(error_message, 503, stream, path)
                    raise ServiceUnavailableError(response.status_code, response.headers)
                
                elif response.status_code >= 500:
                    # Server errors
                    enhanced_message = self._enhance_error_message(error_message, response.status_code, stream, path)
                    raise ServerError(enhanced_message, response.status_code, response.headers)
                
                elif response.status_code == 403:
                    # Forbidden - could be content filter or permission issue
                    if "content_filter" in str(error_type).lower() or "content" in error_message.lower():
                        raise ContentFilterError(error_message, response.status_code, response.headers)
                    else:
                        enhanced_message = self._enhance_error_message(error_message, 403, stream, path)
                        raise APIError(enhanced_message, error_code, error_type, response.status_code, response.headers)
                
                else:
                    # Generic API error for other status codes
                    enhanced_message = self._enhance_error_message(error_message, response.status_code, stream, path)
                    raise APIError(enhanced_message, error_code, error_type, response.status_code, response.headers)

            return response if stream else response.json()

        except requests.exceptions.Timeout as e:
            self.logger.warning(f"Request timeout for {method} {path} after {self.timeout}s")
            raise TimeoutError(f"Request timed out after {self.timeout} seconds. Try increasing the timeout or check your connection.")
        
        except requests.exceptions.ConnectionError as e:
            error_msg = f"Failed to connect to HAI API at {self.base_url}. "
            
            # Provide more specific connection error guidance
            if "getaddrinfo failed" in str(e).lower() or "name resolution" in str(e).lower():
                error_msg += "DNS resolution failed. Check your internet connection and the base URL."
            elif "connection refused" in str(e).lower():
                error_msg += "Connection was refused. The API server may be down or unreachable."
            elif "ssl" in str(e).lower() or "certificate" in str(e).lower():
                error_msg += "SSL/TLS connection failed. Check your network security settings."
            else:
                error_msg += f"Network error: {str(e)}"
            
            self.logger.error(f"Connection error: {error_msg}")
            raise APIConnectionError(error_msg, should_retry=True)
        
        except requests.exceptions.HTTPError as e:
            # This shouldn't normally happen since we handle status codes above,
            # but just in case
            self.logger.error(f"HTTP error not caught by status code handling: {e}")
            raise APIError(f"HTTP error: {str(e)}")
        
        except requests.exceptions.RequestException as e:
            # Catch-all for other requests errors
            error_msg = f"Unexpected error communicating with HAI API: {str(e)}"
            self.logger.error(error_msg)
            raise APIError(error_msg)
        
        except HAIError:
            # Re-raise HAI errors as-is (from our error handling above)
            raise
        
        except Exception as e:
            # Catch any other unexpected errors
            error_msg = f"Unexpected error in API request: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise APIError(error_msg)