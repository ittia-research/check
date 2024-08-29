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

def get_verdict_summary(verdicts_data, statement):
    """
    Calculate and summarize the verdicts of multiple sources.
    Introduce some weights:
      - total: the number of total verdicts
      - valid: the number of verdicts in the desired categories
      - winning: the count of the winning verdict
      - and count of verdicts of each desiered categories
    """
    
    weight_total = 0
    weight_valid = 0
    sum_score = 0
    sum_citation = {
        "true": {"citation": [], "weight": 0},
        "false": {"citation": [], "weight": 0},
        "irrelevant": {"citation": [], "weight": 0},
    }

    for hostname, verdict in verdicts_data.items():
        weight_total += 1
        v = verdict['verdict'].lower()
        if v in sum_citation:
            weight_valid += 1
            citation = f"{verdict['citation']}  *source: {hostname}*\n\n"
            sum_citation[v]['citation'].append(citation)
            sum_citation[v]['weight'] += 1
            if v == 'true':
                sum_score += 1
            elif v == 'false':
                sum_score -= 1

    if sum_score > 0:
        verdict = "true"
    elif sum_score < 0:
        verdict = "false"
    else:
        verdict = "irrelevant"

    citation = ''.join(sum_citation[verdict]['citation'])
    if not citation:
        raise Exception("No citation found after summarize")

    weights = {"total": weight_total, "valid": weight_valid, "winning": sum_citation[verdict]['weight']}
    for key in sum_citation.keys():
        weights[key] = sum_citation[key]['weight']
        
    return {"verdict": verdict, "citation": citation, "weights": weights, "statement": statement}
    
def get_verdict(search_json, statement):
    _verdict_citation = VerdictCitation(search_json=search_json)
    verdicts_data = _verdict_citation.get(statement=statement)
    
    summary = get_verdict_summary(verdicts_data, statement)
    return summary
    