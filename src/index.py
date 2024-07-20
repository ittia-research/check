from llama_index.core import (
    Document,
    ServiceContext,
    StorageContext,
    VectorStoreIndex,
    load_index_from_storage,
)
from llama_index.core.node_parser import HierarchicalNodeParser, get_leaf_nodes
from llama_index.core.retrievers import AutoMergingRetriever
from llama_index.core.indices.postprocessor import SentenceTransformerRerank
from llama_index.core.query_engine import RetrieverQueryEngine

def build_automerging_index(
    documents,
    llm,
    embed_model="local:BAAI/bge-small-en-v1.5",
    chunk_sizes=None,
):
    chunk_sizes = chunk_sizes or [2048, 512, 128]
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
    rerank = SentenceTransformerRerank(
        top_n=rerank_top_n, model="BAAI/bge-reranker-base"
    )
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
    )  # todo: any resources waste here?
    
    query_engine = get_automerging_query_engine(index, similarity_top_k=12)
    query = f"{keywords} | {statement}"  # todo: better way
    auto_merging_response = query_engine.query(query)
    contexts = nodes2list(auto_merging_response.source_nodes)
    return contexts