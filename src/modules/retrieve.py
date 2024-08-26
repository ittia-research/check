import concurrent.futures
import logging
from typing import Optional

from llama_index.core import (
    Document,
    Settings,
    StorageContext,
    VectorStoreIndex,
)
from llama_index.core.node_parser import HierarchicalNodeParser, get_leaf_nodes
from llama_index.core.retrievers import AutoMergingRetriever
from llama_index.core.indices.postprocessor import SentenceTransformerRerank
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.llms import MockLLM

Settings.llm = MockLLM(max_tokens=256)  # retrieve only, do not use LLM for synthesize

import utils
from settings import settings

from llama_index.postprocessor.jinaai_rerank import JinaRerank

from integrations import InfinityEmbedding

if settings.EMBEDDING_MODEL_DEPLOY == "local":
    embed_model="local:" + settings.EMBEDDING_MODEL_NAME
else:  # TODO: best batch size
    if settings.EMBEDDING_SERVER_TYPE == "infinity":
        embed_model = InfinityEmbedding(
            api_key=settings.EMBEDDING_API_KEY,
            base_url=settings.EMBEDDING_BASE_URL,
            embed_batch_size=settings.EMBEDDING_BATCH_SIZE,
            model_name=settings.EMBEDDING_MODEL_NAME,
        )
    elif settings.EMBEDDING_SERVER_TYPE == "ollama":
        embed_model = OllamaEmbedding(
            api_key=settings.EMBEDDING_API_KEY,
            base_url=settings.EMBEDDING_BASE_URL,
            embed_batch_size=settings.EMBEDDING_BATCH_SIZE,
            model_name=settings.EMBEDDING_MODEL_NAME,
        )
    else:
        raise ValueError(f"Embedding server {settings.EMBEDDING_SERVER_TYPE} not supported")
        
Settings.embed_model = embed_model

class LlamaIndexCustomRetriever():
    def __init__(
        self,
        docs = None,
        similarity_top_k: Optional[int] = 6,
    ):
        self.similarity_top_k = similarity_top_k
        if docs:
            self.build_index(docs)
        
    def build_automerging_index(
        self,
        documents,
        chunk_sizes=[2048, 512, 128],
    ):            
        node_parser = HierarchicalNodeParser.from_defaults(chunk_sizes=chunk_sizes)
        self.nodes = node_parser.get_nodes_from_documents(documents)
        leaf_nodes = get_leaf_nodes(self.nodes)

        storage_context = StorageContext.from_defaults()
        storage_context.docstore.add_documents(self.nodes)

        # TODO: enable async
        automerging_index = VectorStoreIndex(
            leaf_nodes, storage_context=storage_context, use_async=False
        )
                
        return automerging_index
    
    def get_automerging_query_engine(
        self,
        automerging_index,
        similarity_top_k=6,
        rerank_top_n=3,
    ):
        base_retriever = automerging_index.as_retriever(similarity_top_k=similarity_top_k)
        retriever = AutoMergingRetriever(
            base_retriever, automerging_index.storage_context, verbose=True
        )

        # TODO: load model files at app start
        if settings.RERANK_MODEL_DEPLOY == "local":
            rerank = SentenceTransformerRerank(
                top_n=rerank_top_n, model=settings.RERANK_MODEL_NAME,
            )  # TODO: add support `trust_remote_code=True`
        else:
            rerank = JinaRerank(
                base_url = settings.RERANK_BASE_URL,
                api_key=settings.RERANK_API_KEY, 
                top_n=rerank_top_n, 
                model=settings.RERANK_MODEL_NAME,
            )
        
        auto_merging_engine = RetrieverQueryEngine.from_args(
            retriever, node_postprocessors=[rerank]
        )
    
        return auto_merging_engine

    def build_index(self, docs):
        """Initiate index or build a new one."""
        
        if docs:
            self.index = self.build_automerging_index(
                docs,
                chunk_sizes=settings.INDEX_CHUNK_SIZES,
            )  # TODO: try to retrieve directly
        
    def retrieve(self, query):
        # TODO: get query engine performance costs
        rerank_top_n=self.similarity_top_k
        query_engine = self.get_automerging_query_engine(
            automerging_index=self.index,
            similarity_top_k=rerank_top_n * 3,
            rerank_top_n=rerank_top_n
        )
        self.query_engine = query_engine
        auto_merging_response = self.query_engine.query(query)
        contexts = utils.llama_index_nodes_to_list(auto_merging_response.source_nodes)

        # select top_n here because some rerank services does not support the feature
        if len(contexts) > rerank_top_n:
            contexts.sort(key=lambda x: x['score'], reverse=True)  # sort by score in descending order
            contexts = contexts[:rerank_top_n]
            
        return contexts

import dspy

NO_TOP_K_WARNING = "The underlying LlamaIndex retriever does not support top k retrieval. Ignoring k value."

class LlamaIndexRM(dspy.Retrieve):
    """Implements a retriever which wraps over a LlamaIndex retriever.

    This is done to bridge LlamaIndex and DSPy and allow the various retrieval
    abstractions in LlamaIndex to be used in DSPy.

    Args:
        retriever (LlamaIndexCustomRetriever): A LlamaIndex retriever object - text based only
        k (int): Optional; the number of examples to retrieve (similarity_top_k)
        docs (list): list of documents for building index

    Returns:
        DSPy RM Object - this is a retriever object that can be used in DSPy
    """
    
    retriever: LlamaIndexCustomRetriever

    def __init__(
        self,
        docs,
        k: Optional[int] = None,
    ):
        self.retriever = LlamaIndexCustomRetriever(docs=docs)

        if k:
            self.k = k

    @property
    def k(self) -> Optional[int]:
        """Get similarity top k of retriever."""
        if not hasattr(self.retriever, "similarity_top_k"):
            logging.warning(NO_TOP_K_WARNING)
            return None

        return self.retriever.similarity_top_k
        
    @k.setter
    def k(self, k: int) -> None:
        """Set similarity top k of retriever."""
        if hasattr(self.retriever, "similarity_top_k"):
            self.retriever.similarity_top_k = k
        else:
            logging.warning(NO_TOP_K_WARNING)

    def forward(self, query: str, k: Optional[int] = None, text_only = False) -> list[dspy.Example]:
        """Forward function for the LI retriever.

        This is the function that is called to retrieve the top k examples for a given query.
        Top k is set via the setter similarity_top_k or at LI instantiation.

        Args:
            query (str): The query to retrieve examples for
            k (int): Optional; the number of examples to retrieve (similarity_top_k)

            If the underlying LI retriever does not have the property similarity_top_k, k will be ignored.

        Returns:
            List[dspy.Example]: A list of examples retrieved by the retriever
        """
        if k:
            self.k = k

        raw = self.retriever.retrieve(query)

        if text_only:
            rep = [result['text'] for result in raw]
        else:
            # change key text to long_text as required by DSPy
            rep = [
                dspy.Example(**{'long_text': result.pop('text', None), **result})
                for result in raw
            ]
        return rep