"""HAI Models API client."""
from dataclasses import dataclass
from typing import List, Optional, Dict, Any

from .base_models import BaseModel

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
    def from_api_data(cls, data: str) -> 'Model':
        """Create a Model instance from API data."""
        return cls(
            id=data,
            name=data
        )

class Models:
    """Models API interface."""
    def __init__(self, client: "HAI"):
        self._client = client

    def list(self) -> List[Model]:
        """List all available models.

        Returns:
            List[Model]: A list of available models.

        Raises:
            APIError: If the request fails.
            AuthenticationError: If authentication fails.
        """
        response = self._client._request(
            "GET",
            "/models",
            auth_required=False  # Models endpoint is public
        )
        return [Model.from_api_data(model_id) for model_id in response]

    def retrieve(self, model_id: str) -> Model:
        """Retrieve a specific model.

        Args:
            model_id: The ID of the model to retrieve.

        Returns:
            Model: The requested model.
            
        Raises:
            APIError: If the model doesn't exist or the request fails.
            AuthenticationError: If authentication fails.
        """
        # Since HAI API currently doesn't support individual model retrieval,
        # we'll get the list and find the requested model
        models = self.list()
        for model in models:
            if model.id == model_id:
                return model
        raise ValueError(f"Model '{model_id}' not found")
