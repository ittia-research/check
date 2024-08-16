import logging
import utils
from modules import SearchQuery, Statements
from .verdict_citation import VerdictCitation

def get_statements(content):
    """Get list of statements from a text string"""
    try:
        statements = Statements()(content=content)
    except Exception as e:
        logging.error(f"Getting statements failed: {e}")
        statements = []

    return statements

def get_search_query(statement):
    """Get search query from one statement"""

    try:
        query = SearchQuery()(statement=statement)
    except Exception as e:
        logging.error(f"Getting search query from statement '{statement}' failed: {e}")
        query = ""

    return query
    
def get_verdict(search_json, statement):
    docs = utils.search_json_to_docs(search_json)
    rep = VerdictCitation(docs=docs).get(statement=statement)

    return {
        "verdict": rep[0],
        "citation": rep[1],
        "statement": statement,
    }
    