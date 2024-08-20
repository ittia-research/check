import aiohttp
from tenacity import retry, stop_after_attempt, wait_fixed

from settings import settings
import utils

@retry(stop=stop_after_attempt(3), wait=wait_fixed(0.1), before_sleep=utils.retry_log_warning, reraise=True)
async def Search(keywords):
    """
    Search and get a list of websites content.

    Todo:
      - Enhance response clear.
    """
    constructed_url = settings.SEARCH_BASE_URL + '/' + keywords

    headers = {
        "Accept": "application/json"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(constructed_url, headers=headers) as response:
            rep = await response.json()
            if not rep:
                raise Exception(f"Search '{keywords}' result empty")
            rep_code = rep.get('code')
            if rep_code != 200:
                raise Exception(f"Search '{keywords}' response code: {rep_code}")
      
    return rep