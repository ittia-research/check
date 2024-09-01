import httpx
import json
from tenacity import retry, stop_after_attempt, wait_fixed

import utils
from settings import settings

client = httpx.AsyncClient(http2=True, follow_redirects=True)

class ReadUrl():
    """Read one single url via API fetch endpoint"""
    
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
        _r = response.json()
        if _r['status'] != 'ok':
            raise Exception(f"Read url return status not ok: {self.url}")  # TODO: avoid duplicated retry
        return _r['data']