from openai import OpenAI
import concurrent.futures
import logging

import utils
from index import Index
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

def get_context_prompt(contexts):
    prompt = "Context:"
    
    for ind, node in enumerate(contexts):
        _text = node.get('text')
        if not _text:
            continue
        prompt = f"""{prompt}
        
```
{_text}
```"""
    return prompt

def get_verdict_single(statement, contexts):
    # This prompt allows model to use their own knowedge
    system_message = '''You are a helpful AI assistant.
Solve tasks using your fact-check skills.
You will be given a statement followed by context.
Use the contexts and facts you know to check if the statements are true, false, irrelevant.
Provide detailed reason for your verdict, ensuring that each reason is supported by corresponding facts.
Provide the response as JSON with the structure:{verdict, reason}'''
    
    prompt = f'''{system_message}
    
```
Statement:
{statement}
```

{get_context_prompt(contexts)}'''
        
    reply = get_llm_reply(prompt)
    logging.debug(f"Verdict reply from LLM: {reply}")
    verdict = utils.llm2json(reply)

    return verdict

def get_verdict_summary(verdicts, statement):
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
    sum_reason = {
        "true": {"reason": [], "weight": 0},
        "false": {"reason": [], "weight": 0},
        "irrelevant": {"reason": [], "weight": 0},
    }

    for verdict in verdicts:
        weight_total += 1
        v = verdict['verdict']
        if v in sum_reason:
            weight_valid += 1
            reason = f"{verdict['reason']}\nsource url: {verdict['url']}\nsource title: {verdict['title']}\n\n"
            sum_reason[v]['reason'].append(reason)
            sum_reason[v]['weight'] += 1
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

    reason = ''.join(sum_reason[verdict]['reason'])
    if not reason:
        raise Exception("No reason found after summary")

    weights = {"total": weight_total, "valid": weight_valid, "winning": sum_reason[verdict]['weight']}
    for key in sum_reason.keys():
        weights[key] = sum_reason[key]['weight']
        
    return {"verdict": verdict, "reason": reason, "weights": weights, "statement": statement}

def get_verdict(statement, keywords, search_json):
    """
    Get verdit from every one of the context sources
    """
    verdicts = []

    def process_result(result):
        content = utils.clear_md_links(result.get('content'))
        metadata = {
            "url": result.get('url'),
            "title": result.get('title'),
        }
        
        try:
            contexts = Index().get_contexts(statement, keywords, content, metadata)
        except Exception as e:
            logging.warning(f"Getting contexts failed: {e}")
            return None
            
        try:
            verdict = get_verdict_single(statement, contexts)
        except Exception as e:
            logging.warning(f"Getting verdit failed: {e}")
            return None

        verdict = {
            "verdict": verdict.get('verdict', '').lower(),
            "reason": verdict.get('reason'),
            "url": result.get('url'),
            "title": result.get('title'),
        }

        logging.debug(f"single source verdict: {verdict}")
        return verdict
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
        # Use a list comprehension to submit tasks and collect results
        future_to_result = {executor.submit(process_result, result): result for result in search_json['data']}

        for future in concurrent.futures.as_completed(future_to_result):
            verdict = future.result()
            if verdict is not None:
                verdicts.append(verdict)

    summary = get_verdict_summary(verdicts, statement)
    return summary
    