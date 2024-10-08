__all__ = ['Citation', 'ContextVerdict', 'LlamaIndexRM', 'Search', 'SearchQuery', 'Statements']

from .citation import Citation
from .context_verdict import ContextVerdict
from .retrieve import LlamaIndexRM
from .search import Search
from .search_query import SearchQuery
from .statements import Statements

import dspy

from settings import settings

# set DSPy default language model
llm = dspy.OpenAI(model=settings.LLM_MODEL_NAME, api_base=f"{settings.OPENAI_BASE_URL}/", max_tokens=200, stop='\n\n')
dspy.settings.configure(lm=llm)

# LM with higher token limits
llm_long = dspy.OpenAI(model=settings.LLM_MODEL_NAME, api_base=f"{settings.OPENAI_BASE_URL}/", max_tokens=500, stop='\n\n')
