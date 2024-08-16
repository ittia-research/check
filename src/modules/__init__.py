import dspy

from settings import settings

# set DSPy default language model
llm = dspy.OpenAI(model=settings.LLM_MODEL_NAME, api_base=f"{settings.OPENAI_BASE_URL}/", max_tokens=200, stop='\n\n')
dspy.settings.configure(lm=llm)

from .citation import Citation
from .ollama_embedding import OllamaEmbedding
from .retrieve import LlamaIndexRM
from .search_query import SearchQuery
from .statements import Statements
from .verdict import Verdict