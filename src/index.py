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

Settings.llm = None  # retrieve only, do not use LLM for synthesize

import llama_index.postprocessor.jinaai_rerank.base as jinaai_rerank  # todo: shall we lock package version?
jinaai_rerank.API_URL = os.environ.get("LLM_LOCAL_BASE_URL") + "/rerank"  # switch to on-premise

# todo: high lantency between client and the ollama embedding server will slow down embedding a lot
from llama_index.embeddings.ollama import OllamaEmbedding

# set RAG model deploy mode
RAG_MODEL_DEPLOY = os.environ.get("RAG_MODEL_DEPLOY") or "local"

def build_automerging_index(
    documents,
    llm,
    chunk_sizes=None,
):
    chunk_sizes = chunk_sizes or [2048, 512, 128]

    if RAG_MODEL_DEPLOY == "local":
        embed_model="local:jinaai/jina-embeddings-v2-base-en"
    else:
        embed_model = OllamaEmbedding(
            model_name="jina/jina-embeddings-v2-base-en",
            base_url=os.environ.get("OLLAMA_BASE_URL"),  # todo: any other configs here?
        )
        
    node_parser = HierarchicalNodeParser.from_defaults(chunk_sizes=chunk_sizes)
    nodes = node_parser.get_nodes_from_documents(documents)
    leaf_nodes = get_leaf_nodes(nodes)
    merging_context = ServiceContext.from_defaults(
        llm=llm,
        embed_model=embed_model,
    )
    storage_context = StorageContext.from_defaults()
    storage_context.docstore.add_documents(nodes)

    automerging_index = VectorStoreIndex(
        leaf_nodes, storage_context=storage_context, service_context=merging_context
    )
    return automerging_index

def get_automerging_query_engine(
    automerging_index,
    similarity_top_k=12,
    rerank_top_n=6,
):
    base_retriever = automerging_index.as_retriever(similarity_top_k=similarity_top_k)
    retriever = AutoMergingRetriever(
        base_retriever, automerging_index.storage_context, verbose=True
    )

    if RAG_MODEL_DEPLOY == "local":
        rerank = SentenceTransformerRerank(
            top_n=rerank_top_n, model="BAAI/bge-reranker-v2-m3",
        )  # todo: add support `trust_remote_code=True`
    else:
        rerank = jinaai_rerank.JinaRerank(api_key='', top_n=rerank_top_n, model="jina-reranker-v2")
    
    auto_merging_engine = RetrieverQueryEngine.from_args(
        retriever, node_postprocessors=[rerank]
    )

    return auto_merging_engine

def nodes2list(nodes):
    nodes_list = []
    for ind, source_node in enumerate(nodes):
        _i = _sub = {}
        _sub['id'] = source_node.node.node_id
        _sub['score'] = source_node.score
        _sub['text'] = source_node.node.get_content().strip()
        nodes_list.append(_sub)
    return nodes_list
    
def get_contexts(statement, keywords, text):
    """
    Get list of contexts.

    Todo: resources re-use for multiple run.
    """
    document = Document(text=text)
    index = build_automerging_index(
        [document],
        llm=None,
        chunk_sizes=[2048, 512],
    )  # todo: will it better to use retriever directly?
    
    query_engine = get_automerging_query_engine(index, similarity_top_k=16)
    query = f"{keywords} | {statement}"  # todo: better way
    auto_merging_response = query_engine.query(query)
    contexts = nodes2list(auto_merging_response.source_nodes)

    return contexts