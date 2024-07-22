import re, json, ast, os
import aiohttp
import logging

logger = logging.getLogger(__name__)

def llm2list(text):
    list_obj = []
    try:
        # find the first pair of square brackets and their content
        match = re.search(r'\[.*?\]', text, re.DOTALL)
        
        if match:
            list_obj = ast.literal_eval(match.group())
    except Exception as e:
        logger.warning(f"Failed convert LLM response to list: {e}")
        pass
    return list_obj

def llm2json(text):
    json_object = {}
    try:
        # find the first JSON object
        match = re.search(r'\{.*?\}', text, re.DOTALL)
        if match:
            json_object = json.loads(match.group())
    except Exception as e:
        logger.warning(f"Failed convert LLM response to JSON: {e}")
        pass
    return json_object
    
async def search(keywords):
    """
    Constructs a URL from given keywords and search via Jina Reader.

    Todo:
      - Enhance response clear.
    """
    base_url = 'https://s.jina.ai/'
    constructed_url = base_url + keywords

    headers = {
        "Accept": "application/json"
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(constructed_url, headers=headers) as response:
                response_data = await response.json()
                if response_data.get('code') != 200:
                    raise Exception("Search return code not 200")
                text = "\n\n".join([doc['content'] for doc in response_data['data']])
                result = clear_md_links(text)
        except Exception as e:
            logger.error(f"Search '{keywords}' failed: {e}")
            result =  ''
            
    return result

def clear_md_links(md_content):
    """
    Removes all Markdown links from the document and keeps only the text.
    Special handling for cases like [\[note 1\]](url) to keep 'note 1' text.

    Args:
    md_content (str): The Markdown content as a string.

    Returns:
    str: The Markdown content with links removed and only the text retained.
    """
    # General pattern to match Markdown links of the form [text](url)
    general_link_pattern = re.compile(r'\[([^\]]+)\]\([^\)]+\)')
    
    # Specific pattern to match cases like [\[note 1\]](url)
    special_link_pattern = re.compile(r'\[\\\[(.*?)\\\]\]\([^\)]+\)')

    # Replace the matched special links with the text inside double brackets
    processed_content = re.sub(special_link_pattern, r'\1', md_content)
    
    # Replace the matched general links with just the link text
    processed_content = re.sub(general_link_pattern, r'\1', processed_content)
    
    return processed_content

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
        markdown.append(f"**Reason**: {verdict['reason']}\n")

    markdown_str = "\n".join(markdown)
    return markdown_str

def generate_report_html(input_text, verdicts):
    html = []

    # Add basic HTML structure and styles
    html.append("""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {
                font-family: Arial, sans-serif;
                line-height: 1.6;
                margin: 20px;
            }
            h2 {
                color: #2c3e50;
            }
            pre {
                background-color: #f5f5f5;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
                white-space: pre-wrap;
            }
            .verdict {
                margin-bottom: 20px;
            }
            .statement {
                font-weight: bold;
                margin-top: 10px;
            }
            .verdict-label {
                font-weight: bold;
            }
            .reason {
                margin-top: 5px;
            }
        </style>
    </head>
    <body>
    """)

    # Add original input
    html.append("<h2>Original Input</h2>\n")
    html.append("<pre>" + input_text + "</pre>\n")

    # Add verdicts
    html.append("<h2>Fact Check</h2>\n")
    for i, verdict in enumerate(verdicts, start=1):
        html.append(f'<div class="verdict">\n')
        html.append(f'<h3>Statement {i}</h3>\n')
        html.append(f'<div class="statement">Statement: {verdict["statement"]}</div>\n')
        html.append(f'<div class="verdict-label">Verdict: <code>{verdict["verdict"]}</code></div>\n')
        html.append(f'<div class="reason">Reason: {verdict["reason"]}</div>\n')
        html.append('</div>\n')

    # Close HTML structure
    html.append("""
    </body>
    </html>
    """)

    html_str = "\n".join(html)
    return html_str

def check_input(input_string):
    """
    Check if the input are checkable.

    :return: False if not readable, True otherwise.
    """
    
    if input_string in ["favicon.ico"]:
        return False
    
    # Does not support image search
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg']
    if any(input_string.lower().endswith(ext) for ext in image_extensions):
        return False
    
    # Check if the string ends with any non-nature-language file extensions
    non_human_readable_extensions = ['.css', '.js', '.woff', '.woff2', '.ttf', '.eot']
    if any(input_string.lower().endswith(ext) for ext in non_human_readable_extensions):
        return False
        
    return True

def get_homepage():
    md = f"""(preview only)

Fact-check API

[Usage] {os.environ.get("HOSTING_CHECK_BASE_URL")}/YOUR_FACT_CHECK_QUERY
"""
    return md