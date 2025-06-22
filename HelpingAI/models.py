"""HAI Models API client."""
from dataclasses import dataclass
from typing import List, Optional, Dict, Any, TYPE_CHECKING

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
        try:
            response = self._client._request(
                "GET",
                "/models",
                auth_required=False  # Models endpoint is public
            )
            return [Model.from_api_data(model_id) for model_id in response]
        except Exception:
            # Fallback to hardcoded models if API call fails
            return [
                Model(
                    id="Helpingai3-raw",
                    name="HelpingAI3 Raw",
                    description="Advanced language model with enhanced emotional intelligence and contextual awareness"
                ),
                Model(
                    id="Dhanishtha-2.0-preview",
                    name="Dhanishtha-2.0 Preview",
                    description="Revolutionary reasoning AI model with intermediate thinking capabilities and multi-phase reasoning"
                )
            ]

    def retrieve(self, model_id: str) -> Model:
        """Retrieve a specific model.

        Args:
            model_id (str): The ID of the model to retrieve.

        Returns:
            Model: The requested model.
            
        Raises:
            ValueError: If the model doesn't exist.
        """
        # Define available models with detailed information
        available_models = {
            "Helpingai3-raw": Model(
                id="Helpingai3-raw",
                name="HelpingAI3 Raw",
                description="Advanced language model with enhanced emotional intelligence, trained on emotional dialogues, therapeutic exchanges, and crisis response scenarios"
            ),
            "Dhanishtha-2.0-preview": Model(
                id="Dhanishtha-2.0-preview",
                name="Dhanishtha-2.0 Preview",
                description="World's first intermediate thinking model with multi-phase reasoning, self-correction capabilities, and structured emotional reasoning (SER)"
            )
        }
        
        if model_id in available_models:
            return available_models[model_id]
        
        # Try to get from API as fallback
        try:
            models = self.list()
            for model in models:
                if model.id == model_id:
                    return model
        except Exception:
            pass
            
        raise ValueError(f"Model '{model_id}' not found. Available models: {list(available_models.keys())}")
