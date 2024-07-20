import os
from autogen import AssistantAgent
import logging

import utils

logger = logging.getLogger(__name__)

llm_config = {"config_list": [{"model": "gpt-4o-mini", "api_key": os.environ.get("OPENAI_API_KEY")}]}

"""
Get list of statements from input.
"""
def get_statements(content):
    system_message = '''You are a helpful AI assistant.
Solve tasks using your fact extraction skills.
Extract single facts from given text.
Provide a list of the facts in array format.'''
    
    statement_extract_agent = AssistantAgent(
        name="statement_extract_agent",
        system_message=system_message,
        llm_config=llm_config,
        human_input_mode="NEVER",
    )
    
    reply = statement_extract_agent.generate_reply(messages=[{"content": content, "role": "user"}])
    logger.info(f"get_statements LLM reply type {type(reply)}: {reply}")
    return utils.llm2list(reply)

"""
Get search keywords from statements
"""
def get_search_keywords(statement):
    system_message = '''You are a helpful AI assistant.
Solve tasks using your searching skills.
Generate search keywords used for fact check on the given statement.
Include only the keywords in your response.'''
    
    search_keywords_agent = AssistantAgent(
        name="search_keywords_agent",
        system_message=system_message,
        llm_config=llm_config,
        human_input_mode="NEVER",
    )

    content = f"Statement: {statement}"
    reply = search_keywords_agent.generate_reply(messages=[{"content": content, "role": "user"}])
    return reply.strip()

def get_verdict(statement, contexts):
    # This prompt allows model to use their own knowedge
    system_message = '''You are a helpful AI assistant.
    Solve tasks using your fact check skills.
    You will be given a statement follows by some contexts.
    Use the contexts to check if the statement are true, false, or uncheckable.
    Generate the response as JSON with the structure:{verdict, reason}'''
    
    fact_check_agent = AssistantAgent(
        name="fact_check_agent",
        system_message=system_message,
        llm_config=llm_config,
        human_input_mode="NEVER",
    )
    
    content = f'''Statement: {statement}
    Contexts:'''
    
    for ind, node in enumerate(contexts):
        _text = node.get('text')
        if not _text:
            continue
        content = f"""{content}
    ```
    Context {ind + 1}:
    {_text}
    ```"""
    
    reply = fact_check_agent.generate_reply(messages=[{"content": content, "role": "user"}])
    verdict = utils.llm2json(reply)
    if verdict:
        verdict['statement'] = statement
    return verdict

