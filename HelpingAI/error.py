"""Exceptions for HAI API client."""

from typing import Dict, Optional, Any, TypeVar

T = TypeVar("T", bound=Dict[str, Any])

class HAIError(Exception):
    """Base exception for HAI API errors."""
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        headers: Optional[Dict[str, Any]] = None,
        body: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message)
        self.message: str = message
        self.status_code: Optional[int] = status_code
        self.headers: Dict[str, Any] = headers or {}
        self.body: Dict[str, Any] = body or {}

    def __str__(self) -> str:
        status = f" (HTTP {self.status_code})" if self.status_code else ""
        return f"{self.message}{status}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(message={self.message!r}, status_code={self.status_code!r})"

class AuthenticationError(HAIError):
    """Raised when API key authentication fails."""
    pass

class NoAPIKeyError(AuthenticationError):
    """Raised when no API key is provided."""
    def __init__(self) -> None:
        super().__init__(
            "No API key provided. Set your API key using `hai = HAI(api_key=...)` "
            "or by setting the HAI_API_KEY environment variable. You can generate API keys "
            "in the HelpingAI dashboard at https://helpingai.co/dashboard"
        )

class InvalidAPIKeyError(AuthenticationError):
    """Raised when the API key is invalid."""
    def __init__(self, status_code: Optional[int] = None, headers: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            "Invalid API key. Check your API key at https://helpingai.co/dashboard",
            status_code,
            headers
        )

class PermissionDeniedError(AuthenticationError):
    """Raised when the API key doesn't have permission for the requested operation."""
    pass

class InvalidRequestError(HAIError):
    """Raised when the request parameters are invalid."""
    def __init__(
        self,
        message: str,
        param: Optional[str] = None,
        code: Optional[str] = None,
        status_code: Optional[int] = None,
        headers: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message, status_code, headers)
        self.param: Optional[str] = param
        self.code: Optional[str] = code

    def __str__(self) -> str:
        msg = super().__str__()
        if self.param:
            msg = f"{msg} (Parameter: {self.param})"
        if self.code:
            msg = f"{msg} (Error Code: {self.code})"
        return msg

class InvalidModelError(InvalidRequestError):
    """Raised when an invalid model is specified."""
    def __init__(
        self,
        model: str,
        status_code: Optional[int] = None,
        headers: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(
            f"Model '{model}' not found. Available models can be found at "
            "https://api.helpingai.co/v1/models",
            param="model",
            status_code=status_code,
            headers=headers
        )

class RateLimitError(HAIError):
    """Raised when rate limit is exceeded."""
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        headers: Optional[Dict[str, Any]] = None,
        retry_after: Optional[int] = None
    ) -> None:
        super().__init__(message, status_code, headers)
        self.retry_after: Optional[int] = retry_after or self._get_retry_after_from_headers()

    def _get_retry_after_from_headers(self) -> Optional[int]:
        """Extract retry-after value from headers."""
        if "retry-after" in self.headers:
            try:
                return int(self.headers["retry-after"])
            except (ValueError, TypeError):
                return None
        return None

    def __str__(self) -> str:
        msg = super().__str__()
        if self.retry_after:
            msg = f"{msg} (Retry after: {self.retry_after} seconds)"
        return msg

class TooManyRequestsError(RateLimitError):
    """Raised when too many requests are made within a time window."""
    def __init__(
        self,
        status_code: Optional[int] = None,
        headers: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(
            "Rate limit exceeded. Please try again later.",
            status_code=status_code,
            headers=headers
        )

class ServiceUnavailableError(HAIError):
    """Raised when the API service is unavailable."""
    def __init__(
        self,
        status_code: Optional[int] = None,
        headers: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(
            "HelpingAI API is temporarily unavailable. Please try again later.",
            status_code=status_code,
            headers=headers
        )

class TimeoutError(HAIError):
    """Raised when a request times out."""
    def __init__(self, message: str = "Request timed out") -> None:
        super().__init__(message)

class APIConnectionError(HAIError):
    """Raised when there are network issues connecting to the API."""
    def __init__(
        self,
        message: str,
        should_retry: bool = False,
        status_code: Optional[int] = None,
        headers: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message, status_code, headers)
        self.should_retry: bool = should_retry

class APIError(HAIError):
    """Generic API error."""
    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        type: Optional[str] = None,
        status_code: Optional[int] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, status_code, headers)
        self.code: Optional[str] = code
        self.type: Optional[str] = type

    def __str__(self) -> str:
        msg = super().__str__()
        if self.code:
            msg = f"{msg} (Code: {self.code})"
        if self.type:
            msg = f"{msg} (Type: {self.type})"
        return msg

class ServerError(APIError):
    """Raised when the API server encounters an error."""
    def __init__(
        self,
        message: str = "Internal server error",
        status_code: Optional[int] = None,
        headers: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(
            message,
            code="server_error",
            status_code=status_code,
            headers=headers
        )

class ContentFilterError(InvalidRequestError):
    """Raised when content is flagged by moderation filters."""
    def __init__(
        self,
        message: str = "Content violates content policy",
        status_code: Optional[int] = None,
        headers: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(
            message,
            code="content_filter",
            status_code=status_code,
            headers=headers
        )

class TokenLimitError(InvalidRequestError):
    """Raised when the token limit is exceeded."""
    def __init__(
        self,
        message: str = "Token limit exceeded",
        status_code: Optional[int] = None,
        headers: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(
            message,
            code="token_limit",
            status_code=status_code,
            headers=headers
        )

class InvalidContentError(InvalidRequestError):
    """Raised when the provided content is invalid."""
    def __init__(
        self,
        message: str,
        param: Optional[str] = None,
        status_code: Optional[int] = None,
        headers: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(
            message,
            param=param,
            code="invalid_content",
            status_code=status_code,
            headers=headers
        )
