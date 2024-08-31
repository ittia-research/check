import asyncio
import httpx
import json

from settings import settings

class SearchWeb():
    """
    Web search with a query with session support:
      - get more links following the previous searches
      - get all links of this session
    """
    def __init__(self, query: str):
        self.query = query
        self.api = settings.SEARCH_BASE_URL + '/search'
        self.timeout = 600  # api request timeout, set higher cause search backend might need to try a few times

        self.client = httpx.AsyncClient(http2=True, follow_redirects=True, timeout=self.timeout)
        
    """
    Get JSON data from API stream output.
    
    TODO: 
      - Is there a more standard way to process streamed JSON?
      - Add retry.
    """
    async def get(self, num: int = 10, all: bool = False):
        _data = {
            'query': self.query,
            'num': num,  # how many more urls to get
            'all': all,
        }
        async with self.client.stream("POST", self.api, json=_data) as response:
            buffer = ""
            async for chunk in response.aiter_text():
                if chunk.strip():  # Only process non-empty chunks
                    buffer += chunk
                    
                    # Attempt to load the buffer as JSON
                    try:
                        # Keep loading JSON until all data is consumed
                        while buffer:
                            # Try to load a complete JSON object
                            rep, index = json.JSONDecoder().raw_decode(buffer)
                            yield rep
                            
                            # Remove the processed part from the buffer
                            buffer = buffer[index:].lstrip()  # Remove processed JSON and any leading whitespace
                    except json.JSONDecodeError:
                        # If we encounter an error, we may not have a complete JSON object yet
                        continue  # Continue to read more data
