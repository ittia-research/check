import re, json, ast, os
import aiohttp
import itertools
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
                response_code = response_data.get('code')
                if response_code != 200:
                    raise Exception(f"Search response code: {response_code}")
                text = "\n\n".join([doc['content'] for doc in response_data['data']])
                result = clear_md_links(text)
        except Exception as e:
            logger.error(f"Search '{keywords}' failed: {e}")
            result =  ''
            
    return result

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

def get_homepage():
    md = f"""(preview only)

Fact-check API

[Usage] {os.environ.get("HOSTING_CHECK_BASE_URL")}/YOUR_FACT_CHECK_QUERY
"""
    return md