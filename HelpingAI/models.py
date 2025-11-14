"""HAI Models API client."""
from dataclasses import dataclass
from typing import List, Optional, Dict, Any, Union, TYPE_CHECKING

from .base_models import BaseModel

if TYPE_CHECKING:
    from .client import HAI

@dataclass
class Model(BaseModel):
    """A model available through the HAI API."""
    id: str
    name: str
    version: Optional[str] = None
    description: Optional[str] = None
    object: str = "model"

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        result = {
            "id": self.id,
            "name": self.name,
            "object": self.object,
        }
        if self.version:
            result["version"] = self.version
        if self.description:
            result["description"] = self.description
        return result

    @classmethod
    def from_api_data(cls, data: Union[str, Dict[str, Any]]) -> 'Model':
        """Create a Model instance from API data.
        
        Args:
            data: Either a string (HelpingAI format) or dict (v1/models schema)
        """
        if isinstance(data, str):
            # HelpingAI format: just model ID string
            return cls(
                id=data,
                name=data
            )
        elif isinstance(data, dict):
            # v1/models schema: dict with id, object, etc.
            return cls(
                id=data["id"],
                name=data.get("id", data["id"]),  # Use id as name if no separate name
                description=data.get("description"),
                object=data.get("object", "model")
            )
        else:
            raise ValueError(f"Unsupported data format: {type(data)}")

    @classmethod
    def from_v1_models_data(cls, data: Dict[str, Any]) -> 'Model':
        """Create a Model instance from the v1/models schema data."""
        return cls.from_api_data(data)

class Models:
    """Models API interface."""
    def __init__(self, client: "HAI"):
        self._client = client

    def list(self) -> List[Model]:
        """List all available models.
        
        Supports both HelpingAI format (array of strings) and v1/models schema.

        Returns:
            List[Model]: A list of available models.

        Raises:
            APIError: If the request fails.
            AuthenticationError: If authentication fails.
        """
        response = self._client._request(
            "GET",
            "/models",
            auth_required=True  # Models endpoint is public
        )
        
        # Handle different response formats
        if isinstance(response, list):
            # HelpingAI format: ["model1", "model2", ...] or [{"id": "model1", ...}, ...]
            return [Model.from_api_data(model_data) for model_data in response]
        elif isinstance(response, dict) and "data" in response:
            # v1/models schema: {"object": "list", "data": [{"id": "model1", ...}, ...]}
            return [Model.from_api_data(model_data) for model_data in response["data"]]
        else:
            raise ValueError(f"Unsupported response format: {type(response)}")

    def retrieve(self, model_id: str) -> Model:
        """Retrieve a specific model.

        Args:
            model_id (str): The ID of the model to retrieve.

        Returns:
            Model: The requested model.
            
        Raises:
            ValueError: If the model doesn't exist.
        """
        # Get models from API
        models = self.list()
        for model in models:
            if model.id == model_id:
                return model
                
        # Get available model IDs for error message
        available_model_ids = [model.id for model in models]
        raise ValueError(f"Model '{model_id}' not found. Available models: {available_model_ids}")
