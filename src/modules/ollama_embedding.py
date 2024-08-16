"""
Added API key support.

Source: https://github.com/run-llama/llama_index/blob/main/llama-index-integrations/embeddings/llama-index-embeddings-ollama/llama_index/embeddings/ollama/base.py
"""

import httpx
from typing import Any, Dict, List, Optional

from llama_index.core.base.embeddings.base import BaseEmbedding
from llama_index.core.bridge.pydantic import Field
from llama_index.core.callbacks.base import CallbackManager
from llama_index.core.constants import DEFAULT_EMBED_BATCH_SIZE

from settings import settings

class OllamaEmbedding(BaseEmbedding):
    """Class for Ollama embeddings."""

    base_url: str = Field(description="Base url the model is hosted by Ollama")
    model_name: str = Field(description="The Ollama model to use.")
    embed_batch_size: int = Field(
        default=DEFAULT_EMBED_BATCH_SIZE,
        description="The batch size for embedding calls.",
        gt=0,
        lte=2048,
    )
    ollama_additional_kwargs: Dict[str, Any] = Field(
        default_factory=dict, description="Additional kwargs for the Ollama API."
    )

    def __init__(
        self,
        model_name: str,
        base_url: str = "http://localhost:11434",
        embed_batch_size: int = DEFAULT_EMBED_BATCH_SIZE,
        ollama_additional_kwargs: Optional[Dict[str, Any]] = None,
        callback_manager: Optional[CallbackManager] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            model_name=model_name,
            base_url=base_url,
            embed_batch_size=embed_batch_size,
            ollama_additional_kwargs=ollama_additional_kwargs or {},
            callback_manager=callback_manager,
        )

    @classmethod
    def class_name(cls) -> str:
        return "OllamaEmbedding"

    def _get_query_embedding(self, query: str) -> List[float]:
        """Get query embedding."""
        return self.get_general_text_embedding(query)

    async def _aget_query_embedding(self, query: str) -> List[float]:
        """The asynchronous version of _get_query_embedding."""
        return await self.aget_general_text_embedding(query)

    def _get_text_embedding(self, text: str) -> List[float]:
        """Get text embedding."""
        return self.get_general_text_embedding(text)

    async def _aget_text_embedding(self, text: str) -> List[float]:
        """Asynchronously get text embedding."""
        return await self.aget_general_text_embedding(text)

    def _get_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get text embeddings."""
        embeddings_list: List[List[float]] = []
        for text in texts:
            embeddings = self.get_general_text_embedding(text)
            embeddings_list.append(embeddings)

        return embeddings_list

    async def _aget_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Asynchronously get text embeddings."""
        return self._aget_text_embeddings(texts)

    def get_general_text_embedding(self, prompt: str) -> List[float]:
        """Get Ollama embedding."""
        try:
            import requests
        except ImportError:
            raise ImportError(
                "Could not import requests library."
                "Please install requests with `pip install requests`"
            )

        ollama_request_body = {
            "prompt": prompt,
            "model": self.model_name,
            "options": self.ollama_additional_kwargs,
        }

        response = requests.post(
            url=f"{self.base_url}/api/embeddings",
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {settings.EMBEDDING_API_KEY}"},
            json=ollama_request_body,
        )
        response.encoding = "utf-8"
        if response.status_code != 200:
            optional_detail = response.json().get("error")
            raise ValueError(
                f"Ollama call failed with status code {response.status_code}."
                f" Details: {optional_detail}"
            )

        try:
            return response.json()["embedding"]
        except requests.exceptions.JSONDecodeError as e:
            raise ValueError(
                f"Error raised for Ollama Call: {e}.\nResponse: {response.text}"
            )

    async def aget_general_text_embedding(self, prompt: str) -> List[float]:
        """Asynchronously get Ollama embedding."""
        async with httpx.AsyncClient() as client:
            ollama_request_body = {
                "prompt": prompt,
                "model": self.model_name,
                "options": self.ollama_additional_kwargs,
            }

            response = await client.post(
                url=f"{self.base_url}/api/embeddings",
                headers={"Content-Type": "application/json", "Authorization": f"Bearer {settings.EMBEDDING_API_KEY}"},
                json=ollama_request_body,
            )
            response.encoding = "utf-8"
            if response.status_code != 200:
                optional_detail = response.json().get("error")
                raise ValueError(
                    f"Ollama call failed with status code {response.status_code}."
                    f" Details: {optional_detail}"
                )

            try:
                return response.json()["embedding"]
            except httpx.HTTPStatusError as e:
                raise ValueError(
                    f"Error raised for Ollama Call: {e}.\nResponse: {response.text}"
                )