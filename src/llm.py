import os
from autogen import AssistantAgent
import logging

import utils

logger = logging.getLogger(__name__)

config_list_openai = [{"model": "gpt-4o-mini", "api_key": os.environ.get("OPENAI_API_KEY")}]

"""
About models:
  - Gemma 2 does not support system rule

Todo:
  - With xinference + Gemma 2 + AutoGen, why 'system message' does not work well
"""
config_list_local = [
    {"model": "gemma-2-it", "base_url": os.environ.get("LLM_LOCAL_BASE_URL"), "tags": ["gemma", "local"]},
]

llm_config = {"config_list": config_list_local}

"""
Get list of statements from input.
"""
def get_statements(input):
    system_message = '''You are a helpful AI assistant.
Solve tasks using your fact extraction skills.
Extract key facts from the given content.
Provide a list of the facts in array format as response only.'''
    
    statement_extract_agent = AssistantAgent(
        name="statement_extract_agent",
        system_message='',
        llm_config=llm_config,
        human_input_mode="NEVER",
    )

    content = f'''{system_message}
```
Content:
{input}
```'''
    
    reply = statement_extract_agent.generate_reply(messages=[{"content": content, "role": "user"}])
    logger.debug(f"get_statements LLM reply: {reply}")
    return utils.llm2list(reply)

"""
Get search keywords from statements
"""
def get_search_keywords(statement):
    system_message = '''You are a helpful AI assistant.
Solve tasks using your searching skills.
Generate search keyword used for fact check on the given statement.
Include only the keyword in your response.'''
    
    search_keywords_agent = AssistantAgent(
        name="search_keywords_agent",
        system_message='',
        llm_config=llm_config,
        human_input_mode="NEVER",
    )

    content = f'''{system_message}
```
Statement:
{statement}
```'''
    reply = search_keywords_agent.generate_reply(messages=[{"content": content, "role": "user"}])
    return reply.strip()

def get_verdict(statement, contexts):
    # This prompt allows model to use their own knowedge
    system_message = '''You are a helpful AI assistant.
Solve tasks using your fact check skills.
You will be given a statement follows by some contexts.
Use the contexts to check if the statement are true, false, or uncheckable.
Provide the response as JSON with the structure:{verdict, reason}'''
    
    fact_check_agent = AssistantAgent(
        name="fact_check_agent",
        system_message='',
        llm_config=llm_config,
        human_input_mode="NEVER",
    )
    
    content = f'''{system_message}
```
Statement:
{statement}
```
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
