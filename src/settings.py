import ast
import os

class Settings:
    def __init__(self):
        # set model names
        self.LLM_MODEL_NAME = os.environ.get("LLM_MODEL_NAME") or "google/gemma-2-27b-it"
        self.EMBEDDING_MODEL_NAME = os.environ.get("EMBEDDING_MODEL_NAME") or "jinaai/jina-embeddings-v2-base-en"
        self.RERANK_MODEL_NAME = os.environ.get("RERANK_MODEL_NAME") or "BAAI/bge-reranker-v2-m3"

        # set server url
        self.OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL") or "https://api.openai.com/v1"
        self.EMBEDDING_BASE_URL = os.environ.get("EMBEDDING_BASE_URL") or "http://ollama:11434"
        self.RERANK_BASE_URL = os.environ.get("RERANK_BASE_URL") or "http://xinference:9997/v1"
        self.PROJECT_HOSTING_BASE_URL = os.environ.get("PROJECT_HOSTING_BASE_URL") or "https://check.ittia.net"
        self.SEARCH_BASE_URL = os.environ.get("SEARCH_BASE_URL") or "https://search.ittia.net"

        # set RAG models deploy mode
        self.EMBEDDING_MODEL_DEPLOY = os.environ.get("EMBEDDING_MODEL_DEPLOY") or "local"
        self.RERANK_MODEL_DEPLOY = os.environ.get("RERANK_MODEL_DEPLOY") or "local"

        # keys
        self.EMBEDDING_API_KEY = os.environ.get("EMBEDDING_API_KEY") or ""
        self.RERANK_API_KEY = os.environ.get("RERANK_API_KEY") or ""

        # tools select
        self.EMBEDDING_SERVER_TYPE = os.environ.get("EMBEDDING_SERVER_TYPE") or "infinity"

        # set Index chunk sizes
        try:
            self.INDEX_CHUNK_SIZES = ast.literal_eval(os.environ.get("INDEX_CHUNK_SIZES"))
        except (ValueError, SyntaxError):
            self.INDEX_CHUNK_SIZES = [1024, 256]

        """
        embedding batch:
            - set higher to improve performance: overcome network latency, etc.
            - embedding servers usually have the capacity to divide too large batch on their own
        """
        self.EMBEDDING_BATCH_SIZE = os.environ.get("EMBEDDING_BATCH_SIZE") or 1024

        # optimizer
        self.OPTIMIZER_FILE_NAME = os.environ.get("OPTIMIZER_FILE_NAME") or "verdict_MIPROv2.json"

        # concurrency
        self.CONCURRENCY_VERDICT = os.environ.get("CONCURRENCY_VERDICT") or 8

        # web
        self.STREAM_TIME_OUT = os.environ.get("STREAM_TIME_OUT") or 300  # in seconds
    
settings = Settings()