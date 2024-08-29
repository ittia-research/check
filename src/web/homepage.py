import utils
from settings import settings

def get_homepage():
    # get tech stack
    stack = utils.get_stack()
    md = f"## Tech stack\n"
    lines = [md]
    lines.extend([f"**{key}**: {value}" for key, value in stack.items()])
    md = "\n\n".join(lines)
        
    md = f"""# Fact-check API

**Usage**: {settings.PROJECT_HOSTING_BASE_URL}/YOUR_FACT_CHECK_QUERY

**Source**: https://github.com/ittia-research/check

{md}
"""
    return md