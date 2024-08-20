import logging
import utils
from tenacity import retry, stop_after_attempt, wait_fixed

from modules import SearchQuery, Statements
from .verdict_citation import VerdictCitation

# Statements has retry set already, do not retry here
def get_statements(content):
    """Get list of statements from a text string"""
    
    statements = Statements()(content=content)
    return statements

@retry(stop=stop_after_attempt(3), wait=wait_fixed(0.1), before_sleep=utils.retry_log_warning, reraise=True)
def get_search_query(statement):
    """Get search query from one statement"""
    
    query = SearchQuery()(statement=statement)
    return query

@retry(stop=stop_after_attempt(3), wait=wait_fixed(0.1), before_sleep=utils.retry_log_warning, reraise=True)
def get_verdict(search_json, statement):
    docs = utils.search_json_to_docs(search_json)
    rep = VerdictCitation(docs=docs).get(statement=statement)

    return {
        "verdict": rep[0],
        "citation": rep[1],
        "statement": statement,
    }
    