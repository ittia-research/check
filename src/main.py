import json
from fastapi import FastAPI, HTTPException, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import Response, JSONResponse, HTMLResponse, PlainTextResponse, FileResponse
import logging

import llm, utils, pipeline

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

"""
Process input string, fact-check and output MARKDOWN
"""
async def fact_check(input):
    status = 500
    logger.info(f"Fact checking: {input}")
    statements = await run_in_threadpool(llm.get_statements, input)
    logger.info(f"statements: {statements}")
    if not statements:
        raise HTTPException(status_code=status, detail="No statements found")

    verdicts = []
    fail_search = False
    for statement in statements:
        if not statement:
            continue
        logger.info(f"statement: {statement}")
        keywords = await run_in_threadpool(llm.get_search_keywords, statement)
        if not keywords:
            continue
        logger.info(f"keywords: {keywords}")
        search = await utils.search(keywords)
        if not search:
            fail_search = True
            continue
        logger.info(f"head of search results: {json.dumps(search)[0:500]}")
        verdict = await run_in_threadpool(pipeline.get_verdict, search_json=search, statement=statement)
        if not verdict:
            continue
        logger.info(f"final verdict: {verdict}")
        verdicts.append(verdict)

    if not verdicts:
        if fail_search:
            raise HTTPException(status_code=status, detail="Search not available")
        else:
            raise HTTPException(status_code=status, detail="No verdicts found")

    report = utils.generate_report_markdown(input, verdicts)
    return report

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    pass

@app.get("/robots.txt", response_class=FileResponse)
async def robots():
    return "assets/robots.txt"

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/status")
async def status():
    _status = await utils.get_status()
    return _status
    
@app.get("/{path:path}", response_class=PlainTextResponse)
async def catch_all(path: str):
    try:
        if not path:
            return await utils.get_homepage()
        if not utils.check_input(path):
            return HTMLResponse(status_code=404, content="Invalid request")  # filter brower background requests
        result = await fact_check(path)
        return result  # HTMLResponse(content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Failed generate reports: {e}")
        raise HTTPException(status_code=500, detail="Service not available")