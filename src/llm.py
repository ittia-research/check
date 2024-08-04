from openai import OpenAI
import logging

import utils
from settings import settings

"""
About models:
  - Gemma 2 does not support system rule
"""

llm_client = OpenAI(
    base_url=settings.OPENAI_BASE_URL,
    api_key="token",
)

def get_llm_reply(prompt, temperature=0):
    completion = llm_client.chat.completions.create(
        model=settings.LLM_MODEL_NAME,
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=temperature,
    )
    return completion.choices[0].message.content

"""
Get list of statements from input.
"""
def get_statements(input):
    system_message = '''You are a helpful AI assistant.
Solve tasks using your fact extraction skills.
Extract key statements from the given content.
Provide in array format as response only.'''
    
    prompt = f'''{system_message}
```
Content:
{input}
```'''
    
    reply = get_llm_reply(prompt)
    logging.debug(f"get_statements LLM reply: {reply}")
    return utils.llm2list(reply)

"""
Get search keywords from statements
"""
def get_search_keywords(statement):
    system_message = '''You are a helpful AI assistant.
Solve tasks using your searching skills.
Generate search keyword used for fact check on the given statement.
Include only the keyword in your response.'''
    
    prompt = f'''{system_message}
```
Statement:
{statement}
```'''
    reply = get_llm_reply(prompt)
    return reply.strip()

def get_verdict(statement, contexts):
    # This prompt allows model to use their own knowedge
    system_message = '''You are a helpful AI assistant.
Solve tasks using your fact-check skills.
You will be given a statement followed by some contexts.
Use the contexts and facts you know to check if the statements are true, false, or uncheckable.
Ignore contexts that are irrelevant or stale.
Provide detailed reasons for your verdict, ensuring that each reason is supported by corresponding facts.
Be thorough in your explanations, avoiding any duplication of information.
Provide the response as JSON with the structure:{verdict, reason}'''
    
    prompt = f'''{system_message}
```
Statement:
{statement}
```
Contexts:'''
    
    for ind, node in enumerate(contexts):
        _text = node.get('text')
        if not _text:
            continue
        prompt = f"""{prompt}
    ```
    Context {ind + 1}:
    {_text}
    ```"""
    
    reply = get_llm_reply(prompt)
    logging.info(f"Verdict reply from LLM: {reply}")
    verdict = utils.llm2json(reply)
    if verdict:
        verdict['statement'] = statement
    return verdict
