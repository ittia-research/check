from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import Response, JSONResponse, HTMLResponse, PlainTextResponse
import logging

import llm, index, utils

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

"""
Process input string, fact-check and output MARKDOWN
"""
def fact_check(input):
    status = 500
    logger.info(f"Fact checking: {input}")
    statements = llm.get_statements(input)
    logger.info(f"statements: {statements}")
    if not statements:
        raise HTTPException(status_code=status, detail="No statements found")

    verdicts = []
    for statement in statements:
        if not statement:
            continue
        logger.info(f"statement: {statement}")
        keywords = llm.get_search_keywords(statement)
        if not keywords:
            continue
        logger.info(f"keywords: {keywords}")
        search = utils.search(keywords)
        if not search:
            continue
        logger.info(f"search: {search}")
        contexts = index.get_contexts(statement, keywords, search)
        if not contexts:
            continue
        logger.info(f"contexts: {contexts}")
        verdict = llm.get_verdict(statement, contexts)
        if not verdict:
            continue
        verdicts.append(verdict)

    if not verdicts:
        raise HTTPException(status_code=status, detail="No verdicts found")

    report = utils.generate_report_html(input, verdicts)
    return report

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    pass
    
@app.get("/{path:path}", response_class=PlainTextResponse)
async def catch_all(path: str):
    try:
        result = fact_check(path)
        return HTMLResponse(content=result)
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Failed generate reports: {e}")
        raise HTTPException(status_code=500, detail=str(e))