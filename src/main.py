import asyncio
import logging
from fastapi import FastAPI, HTTPException, Request
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
async def stream_response(input: str, format: str):
    pipeline_check = pipeline.Check(input=input, format=format)
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


@app.get("/{input:path}", response_class=PlainTextResponse)
async def catch_all(input: str, request: Request):
    """
    Headers:
      - Accept: text/event-stream (Without this header returns the basic HTML page)
      - X-Return-Format: markdown | json (Choose the return format, default markdown)
    """
    # Catch all exception to avoid inner error message expose to public
    try:
        headers = request.headers

        # Filter out browser automated and other invalid requests
        if not utils.check_input(input):
            return HTMLResponse(status_code=404, content='not found')
            
        # Return static HTML page if not requesting stream.
        # The HTML page will fetch the same URL with stream header and render the result.
        if headers.get('accept') != "text/event-stream":
            return HTMLResponse(content=web.html_browser)
        
        # Homepage
        if not input:
            return utils.get_stream(stage='final', content=web.get_homepage())
        
        # Get return format, default `markdown`
        return_format = headers.get("X-Return-Format")
        if return_format not in ['markdown', 'json']:
            return_format = 'markdown'

        # Streaming content
        return StreamingResponse(stream_response(input=input, format=return_format), media_type="text/event-stream")
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Failed generate reports: {e}")
        raise HTTPException(status_code=500, detail="Service not available")