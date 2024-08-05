"""
llama-index
"""
import os

from llama_index.core import (
    Document,
    ServiceContext,
    Settings,
    StorageContext,
    VectorStoreIndex,
    load_index_from_storage,
)
from llama_index.core.node_parser import HierarchicalNodeParser, get_leaf_nodes
from llama_index.core.retrievers import AutoMergingRetriever
from llama_index.core.indices.postprocessor import SentenceTransformerRerank
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.llms import MockLLM

Settings.llm = MockLLM(max_tokens=256)  # retrieve only, do not use LLM for synthesize

from settings import settings

import llama_index.postprocessor.jinaai_rerank.base as jinaai_rerank  # todo: shall we lock package version?
jinaai_rerank.API_URL = settings.RERANK_BASE_URL + "/rerank"  # switch to on-premise

# todo: high lantency between client and the ollama embedding server will slow down embedding a lot
from llama_index.embeddings.ollama import OllamaEmbedding

# todo: improve embedding performance
if settings.EMBEDDING_MODEL_DEPLOY == "local":
    embed_model="local:" + settings.EMBEDDING_MODEL_NAME
else:
    embed_model = OllamaEmbedding(
        model_name=settings.EMBEDDING_MODEL_NAME,
        base_url=os.environ.get("OLLAMA_BASE_URL"),  # todo: any other configs here?
    )
Settings.embed_model = embed_model
    
def nodes2list(nodes):
    nodes_list = []
    for ind, source_node in enumerate(nodes):
        _i = _sub = {}
        _sub['id'] = source_node.node.node_id
        _sub['score'] = source_node.score
        _sub['text'] = source_node.node.get_content().strip()
        nodes_list.append(_sub)
    return nodes_list

class Index():
    def build_automerging_index(
        self,
        documents,
        chunk_sizes=None,
    ):
        chunk_sizes = chunk_sizes or [2048, 512, 128]
            
        node_parser = HierarchicalNodeParser.from_defaults(chunk_sizes=chunk_sizes)
        nodes = node_parser.get_nodes_from_documents(documents)
        leaf_nodes = get_leaf_nodes(nodes)

        storage_context = StorageContext.from_defaults()
        storage_context.docstore.add_documents(nodes)
    
        automerging_index = VectorStoreIndex(
            leaf_nodes, storage_context=storage_context
        )
        return automerging_index
    
    def get_automerging_query_engine(
        self,
        automerging_index,
        similarity_top_k=12,
        rerank_top_n=6,
    ):
        base_retriever = automerging_index.as_retriever(similarity_top_k=similarity_top_k)
        retriever = AutoMergingRetriever(
            base_retriever, automerging_index.storage_context, verbose=True
        )
    
        if settings.RERANK_MODEL_DEPLOY == "local":
            rerank = SentenceTransformerRerank(
                top_n=rerank_top_n, model=settings.RERANK_MODEL_NAME,
            )  # todo: add support `trust_remote_code=True`
        else:
            rerank = jinaai_rerank.JinaRerank(api_key='', top_n=rerank_top_n, model=settings.RERANK_MODEL_NAME)
        
        auto_merging_engine = RetrieverQueryEngine.from_args(
            retriever, node_postprocessors=[rerank]
        )
    
        return auto_merging_engine
        
    def get_contexts(self, statement, keywords, text):
        """
        Get list of contexts.
    
        Todo: resources re-use for multiple run.
        """
        document = Document(text=text)
        index = self.build_automerging_index(
            [document],
            chunk_sizes=settings.RAG_CHUNK_SIZES,
        )  # todo: will it better to use retriever directly?
        
        query_engine = self.get_automerging_query_engine(index, similarity_top_k=16, rerank_top_n=3)
        query = f"{keywords} | {statement}"  # todo: better way
        auto_merging_response = query_engine.query(query)
        contexts = nodes2list(auto_merging_response.source_nodes)
    
        return contexts