import asyncio
import logging
from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse, StreamingResponse

import pipeline
import utils
import web
from settings import settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()

# TODO: multi-stage response
async def stream_response(path):
    pipeline_check = pipeline.Check(path)
    task = asyncio.create_task(pipeline_check.final())
    
    # Stream response to prevent timeout, return multi-stage responses
    elapsed_time = 0
    _check_interval = 0.2
    while not task.done():
        if elapsed_time > settings.STREAM_TIME_OUT:  # waiting timeout
            raise Exception(f"Waiting fact check results reached time limit: {settings.STREAM_TIME_OUT} seconds")
        if elapsed_time % 30 == 0:  # return wait messages from time to time
            yield utils.get_stream(stage='processing', content='### Processing ...')
        await asyncio.sleep(_check_interval)
        elapsed_time = round(elapsed_time + _check_interval, 1)
    
    result = await task
    yield utils.get_stream(stage='final', content=result)
     
@app.on_event("startup")
async def startup_event():
    pass

"""Redirect /doc to /docs"""
@app.get("/doc", include_in_schema=False)
async def _doc_redirect():
    return RedirectResponse(url="/docs")
    
@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/status")
async def status():
    _status = utils.get_status()
    return _status

# TODO: integrate error handle with output
@app.get("/{input:path}", response_class=PlainTextResponse)
async def catch_all(input: str, accept: str = Header(None)):
    try:
        if not utils.check_input(input):
            return HTMLResponse(status_code=404, content='not found')  # filter browser background requests
            
        if accept == "text/markdown":
            if not input:
                return utils.get_stream(stage='final', content=web.get_homepage())
            return StreamingResponse(stream_response(input), media_type="text/event-stream")
        else:
            return HTMLResponse(content=web.html_browser)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Failed generate reports: {e}")
        raise HTTPException(status_code=500, detail="Service not available")