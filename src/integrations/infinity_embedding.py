# reference: https://github.com/ollama/ollama-python/blob/main/ollama/_client.py

import os
import httpx
from typing import Any, List
from llama_index.core.base.embeddings.base import BaseEmbedding
from llama_index.core.bridge.pydantic import PrivateAttr
from tenacity import retry, stop_after_attempt, wait_fixed

import utils
from _types import ResponseError

DEFAULT_INFINITY_BASE_URL = "http://localhost:7997"

class InfinityEmbedding(BaseEmbedding):
    """Class for Infinity embeddings.

    Using retry here cause one failed request could crash the whole embedding process.

    Args:
        api_key (str): Server API key.
        model_name (str): Model for embedding.
        base_url (str): Infinity url. Defaults to http://localhost:7997.
    """

    _aclient: httpx.AsyncClient = PrivateAttr()
    _client: httpx.Client = PrivateAttr()
    _settings: dict = PrivateAttr()
    _url: str = PrivateAttr()

    def __init__(
        self,
        model_name: str,
        api_key: str = "key",
        base_url: str = DEFAULT_INFINITY_BASE_URL,
        http2: bool = True,
        follow_redirects: bool = True,
        timeout: Any = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            model_name=model_name,
            **kwargs,
        )

        self._settings = {
            'follow_redirects': follow_redirects,
            'headers': {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': f"Bearer {api_key}",
            },
            'http2': http2,
            'timeout': timeout,
        }

        self._url = os.path.join(base_url, "embeddings")

    @classmethod
    def class_name(cls) -> str:
        return "InfinityEmbedding"

    def _get_client(self, _async: bool = False):
        """Set and return httpx sync or async client"""
        if _async:
            if not hasattr(self, "_aclient"):
                self._aclient = httpx.AsyncClient(**self._settings)
            return self._aclient
        else:
            if not hasattr(self, "_client"):
                self._client = httpx.Client(**self._settings)
            return self._client
    
    def _process_response(self, response: httpx.Response) -> List[List[float]]:
        embeddings = [item['embedding'] for item in response.json()['data']]
        return embeddings

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(0.5), before_sleep=utils.retry_log_warning, reraise=True)
    def _get_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get text embeddings."""
        client = self._get_client()
        response = client.request(
            'POST',
            self._url,
            json={
                "input": texts, 
                "model": self.model_name,
            },
        )
    
        try:
          response.raise_for_status()
        except httpx.HTTPStatusError as e:
          raise ResponseError(e.response.text, e.response.status_code) from None
    
        return self._process_response(response)

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(0.5), before_sleep=utils.retry_log_warning, reraise=True)   
    async def _aget_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Asynchronously get text embeddings."""
        client = self._get_client(_async=True)
        response = await client.request(
            'POST',
            self._url,
            json={
                "input": texts, 
                "model": self.model_name,
            },
        )
    
        try:
          response.raise_for_status()
        except httpx.HTTPStatusError as e:
          raise ResponseError(e.response.text, e.response.status_code) from None
    
        return self._process_response(response)

    def _get_query_embedding(self, query: str) -> List[float]:
        """Get query embedding."""
        return self._get_text_embeddings([query])[0]

    async def _aget_query_embedding(self, query: str) -> List[float]:
        """The asynchronous version of _get_query_embedding."""
        return await self._aget_text_embeddings([query])[0]

    def _get_text_embedding(self, text: str) -> List[float]:
        """Get text embedding."""
        return self._get_text_embeddings([text])[0]

    async def _aget_text_embedding(self, text: str) -> List[float]:
        """Asynchronously get text embedding."""
        return await self._aget_text_embeddings([text])[0]