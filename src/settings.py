import os, ast

class Settings:
    def __init__(self):
        # set model names
        self.LLM_MODEL_NAME = os.environ.get("LLM_MODEL_NAME") or "google/gemma-2-27b-it"
        self.EMBEDDING_MODEL_NAME = os.environ.get("EMBEDDING_MODEL_NAME") or "jinaai/jina-embeddings-v2-base-en"
        self.RERANK_MODEL_NAME = os.environ.get("RERANK_MODEL_NAME") or "BAAI/bge-reranker-v2-m3"
        
        self.OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL") or "https://api.openai.com/v1"
        self.RERANK_BASE_URL = os.environ.get("RERANK_BASE_URL") or "http://xinference:9997/v1"
        self.PROJECT_HOSTING_BASE_URL = os.environ.get("PROJECT_HOSTING_BASE_URL") or "https://check.ittia.net"
        self.SEARCH_BASE_URL = os.environ.get("SEARCH_BASE_URL") or "https://s.jina.ai"

        # set RAG model deploy mode
        self.RAG_MODEL_DEPLOY = os.environ.get("RAG_MODEL_DEPLOY") or "local"

        # set RAG chunk sizes
        self.RAG_CHUNK_SIZES = [4096, 1024, 256]
        _chunk_sizes = os.environ.get("RAG_CHUNK_SIZES")
        try:
            self.RAG_CHUNK_SIZES = ast.literal_eval(_chunk_sizes)
        except:
            pass
    
settings = Settings()