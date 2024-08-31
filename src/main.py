import asyncio
import json
from fastapi import FastAPI, HTTPException, Request, Header
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import Response, JSONResponse, HTMLResponse, PlainTextResponse, FileResponse, StreamingResponse
import logging

import pipeline, utils, web
from modules import Search
from settings import settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()

# """
# Process input string, fact-check and output MARKDOWN
# """
# async def fact_check(input):
#     status = 500
#     logger.info(f"Fact checking: {input}")

#     # get list of statements
#     try:
#         statements = await run_in_threadpool(pipeline.get_statements, input)
#         logger.info(f"statements: {statements}")
#     except Exception as e:
#         logger.error(f"Get statements failed: {e}")
#         raise HTTPException(status_code=status, detail="No statements found")

#     verdicts = []
#     fail_search = False
#     for statement in statements:
#         if not statement:
#             continue
#         logger.info(f"Statement: {statement}")

#         # get search query
#         try:
#             query = await run_in_threadpool(pipeline.get_search_query, statement)
#             logger.info(f"Search query: {query}")
#         except Exception as e:
#             logger.error(f"Getting search query from statement '{statement}' failed: {e}")
#             continue

#         # searching
#         try:
#             search = await Search(query)
#             logger.info(f"Head of search results: {json.dumps(search)[0:500]}")
#         except Exception as e:
#             fail_search = True
#             logger.error(f"Search '{query}' failed: {e}")
#             continue

#         # get verdict
#         try:
#             verdict = await run_in_threadpool(pipeline.get_verdict, search_json=search, statement=statement)
#             logger.info(f"Verdict: {verdict}")
#         except Exception as e:
#             logger.error(f"Getting verdict for statement '{statement}' failed: {e}")
#             continue
            
#         verdicts.append(verdict)

#     if not verdicts:
#         if fail_search:
#             raise HTTPException(status_code=status, detail="Search not available")
#         else:
#             raise HTTPException(status_code=status, detail="No verdicts found")

#     report = utils.generate_report_markdown(input, verdicts)
#     return report

# TODO: multi-stage response
async def stream_response(path):
    union = pipeline.Union(path)
    task = asyncio.create_task(union.final())
    
    # Stream response to prevent timeout, return multi-stage reponses
    elapsed_time = 0
    _check_interval = 0.2
    while not task.done():
        if elapsed_time > settings.STREAM_TIME_OUT:  # waitting timeout
            raise Exception(f"Waitting fact check results reached time limit: {settings.STREAM_TIME_OUT} seconds")
        if elapsed_time % 30 == 0:  # return wait messages from time to time
            yield utils.get_stream(stage='processing', content='### Processing ...')
        await asyncio.sleep(_check_interval)
        elapsed_time = round(elapsed_time + _check_interval, 1)
    
    result = await task
    yield utils.get_stream(stage='final', content=result)
     
@app.on_event("startup")
async def startup_event():
    pass

@app.get("/robots.txt", response_class=FileResponse)
async def robots():
    return "web/robots.txt"

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/status")
async def status():
    _status = utils.get_status()
    return _status

# TODO: integrade error handle with output
@app.get("/{path:path}", response_class=PlainTextResponse)
async def catch_all(path: str, accept: str = Header(None)):
    try:
        if not utils.check_input(path):
            return HTMLResponse(status_code=404, content="Invalid request")  # filter brower background requests
            
        if accept == "text/markdown":
            if not path:
                return utils.get_stream(stage='final', content=web.get_homepage())
            return StreamingResponse(stream_response(path), media_type="text/event-stream")
        else:
            return HTMLResponse(content=web.html_browser)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Failed generate reports: {e}")
        raise HTTPException(status_code=500, detail="Service not available")