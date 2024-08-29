import hashlib
import itertools
import json
import logging
import re
from llama_index.core import Document

from settings import settings

def llm2json(text):
    json_object = {}
    try:
        # find the first JSON object
        match = re.search(r'\{.*?\}', text, re.DOTALL)
        if match:
            json_object = json.loads(match.group())
    except Exception as e:
        logging.warning(f"Failed convert LLM response to JSON: {e}")
        pass
    return json_object

def clear_md_links(text):
    """
    Removes:
      - markdown links: keep `[text]`
      - standalone URLs
    """
    # match markdown links
    pattern = r'\[([^\]]+)\]\([^\)]+\)'
    text = re.sub(pattern, r'\1', text)
    
    # match standalone URLs
    pattern = r'http[s]?://[^\s]+'
    text = re.sub(pattern, '', text)
    
    return text

def generate_report_markdown(input_text, verdicts):
    markdown = []

    # Add original input
    markdown.append("## Original Input\n")
    markdown.append("```\n" + input_text + "\n```\n")

    # Add verdicts
    markdown.append("## Fact Check\n")
    for i, verdict in enumerate(verdicts, start=1):
        markdown.append(f"### Statement {i}\n")
        markdown.append(f"**Statement**: {verdict['statement']}\n")
        markdown.append(f"**Verdict**: `{verdict['verdict']}`\n")
        markdown.append(f"**Weight**: {verdict['weights']['winning']} out of {verdict['weights']['valid']} ({verdict['weights']['irrelevant']} irrelevant)\n")
        markdown.append(f"**Citation**:\n\n{verdict['citation']}\n")

    markdown_str = "\n".join(markdown)
    return markdown_str

def check_input(input):
    """
    Check if the input are checkable.

    :return: False if not readable, True otherwise.
    """

    # check invalid whole query
    invalid_path = ['YOUR_FACT_CHECK_QUERY']
    common_web_requests = ["favicon.ico"]
    if input in itertools.chain(invalid_path, common_web_requests):
        return False
    
    # check query of unsupported files
    doc_ext = ['.html', '.htm', '.json', '.xml', '.txt']
    image_ext = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg', '.webp']
    not_nature_language_ext = ['.css', '.js', '.php', '.asp', '.aspx', '.woff', '.woff2', '.ttf', '.eot', '.otf']
    if any(input.lower().endswith(ext) for ext in itertools.chain(doc_ext, image_ext, not_nature_language_ext)):
        return False
    
    return True

def get_stack():
    # current tech stack
    stack = {
        "LLM model": settings.LLM_MODEL_NAME,
        "Embedding model": settings.EMBEDDING_MODEL_NAME,
        "Rerank model": settings.RERANK_MODEL_NAME,
        "Index chunk sizes": settings.INDEX_CHUNK_SIZES,
        "Embedding deploy mode": settings.EMBEDDING_MODEL_DEPLOY,
        "Rerank deploy mode": settings.RERANK_MODEL_DEPLOY,
    }
    return stack
    
def get_status():
    stack = get_stack()
    status = {
        "stack": stack
    }
    return status

def llama_index_nodes_to_list(nodes):
    nodes_list = []
    for node in nodes:
        _sub = {
            'id': node.node_id,
            'score': node.score,
            'text': node.get_content().strip(),
            'metadata': node.metadata,
        }
        nodes_list.append(_sub)
    return nodes_list

def search_json_to_docs(search_json):
    """
    Search JSON results to Llama-Index documents

    Do not add metadata for now
    cause LlamaIndex uses `node.get_content(metadata_mode=MetadataMode.EMBED)` which addeds metadata to text for generate embeddings

    TODO: pr to llama-index for metadata_mode setting
    """
    documents = []
    for result in search_json['data']:
        content = clear_md_links(result.get('content'))
        # metadata = {
        #     "url": result.get('url'),
        #     "title": result.get('title'),
        # }
        document = Document(text=content)  #  metadata=metadata
        documents.append(document)
    return documents

def search_result_to_doc(search_result):
    """
    Search result to Llama-Index document

    Do not add metadata for now
    cause LlamaIndex uses `node.get_content(metadata_mode=MetadataMode.EMBED)` which addeds metadata to text for generate embeddings

    TODO: pr to llama-index for metadata_mode setting
    """
    content = clear_md_links(search_result.get('content'))
    # metadata = {
    #     "url": result.get('url'),
    #     "title": result.get('title'),
    # }
    document = Document(text=content)  #  metadata=metadata
    return document
    
def retry_log_warning(retry_state):
    logging.warning(f"Retrying attempt {retry_state.attempt_number} due to: {retry_state.outcome.exception()}")

def get_md5(input):
    """Get MD5 from string"""
    md5_hash = hashlib.md5(input.encode())
    return md5_hash.hexdigest()

# generate str for stream
def get_stream(stage: str = 'wait', content = None):
    message = {"stage": stage, "content": content}
    return json.dumps(message)