import httpx
from tenacity import retry, stop_after_attempt, wait_fixed

import utils
from settings import settings

client = httpx.AsyncClient(http2=True, follow_redirects=True)

class ReadUrl():
    """
    Read one single url via API fetch endpoint.
    Retry failed read at API server end not here.
    
    API response status:
      - ok
      - error
      - not_implemented: fetch ok but not able to read content
    """
    
    def __init__(self, url: str):
        self.url = url
        self.api = settings.SEARCH_BASE_URL + '/read'
        self.timeout = 120  # api request timeout, set higher cause api backend might need to try a few times

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(0.1), before_sleep=utils.retry_log_warning, reraise=True)
    async def get(self):
        _data = {
            'url': self.url,
        }
        response = await client.post(self.api, json=_data, timeout=self.timeout)
        return response.json()
