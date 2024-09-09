import httpx
import json
import logging

API_BASE_URL = "https://check.ittia.net"

class Check():
    """
    Fact-check a string and returns verdicts in markdown or JSON formats.
    """
    def __init__(self,
                 base_url: str = API_BASE_URL,
                 format: str = 'markdown',
                 timeout: int = 600,
                 ):
        """
        Args:
          - base_url: API base URL
          - format: markdown | json, return format
        """
        self.base_url = base_url
        self.format = format
        self.timeout = timeout  # api request timeout, set higher cause the process might take a long time

        self.headers = {
            "X-Return-Format": self.format,
            "Accept": "text/event-stream",
        }
        self.client = httpx.AsyncClient(follow_redirects=True, timeout=self.timeout)

    async def __call__(self, query: str):
        """
        Args:
          - query: text to check
        """
        url = self.base_url + '/' + query
        result = None
        
        async with self.client.stream("GET", url, headers=self.headers) as response:
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

                            # Select the `final` stage only
                            if rep['stage'] != 'final':
                                logging.debug(f"Stage {rep['stage']}: {rep['content']}")
                            else:
                                result = rep['content']
                                
                            # Remove processed JSON and any leading whitespace from the buffer
                            buffer = buffer[index:].lstrip()
                    except json.JSONDecodeError:
                        # If we encounter an error, we may not have a complete JSON object yet
                        continue  # Continue to read more data
                        
        if not result:
            logging.warning("No result found")

        return result