import utils
from dspy_modules import VerdictCitation

def get_verdict(search_json, statement):
    docs = utils.search_json_to_docs(search_json)
    rep = VerdictCitation(docs=docs).get(statement=statement)

    return {
        "verdict": rep[0],
        "citation": rep[1],
        "statement": statement,
    }
    