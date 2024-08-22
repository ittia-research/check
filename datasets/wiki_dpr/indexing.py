from colbert.infra import Run, RunConfig, ColBERTConfig
from colbert import Indexer

GPU_NUMBER = 1
PROJECT_NAME = "wiki"
TSV_PATH = "/data/datasets/wiki/psgs_w100.tsv"
CHECKPOINT_PATH = "/data/checkpoint/colbertv2.0"

if __name__=='__main__':
    with Run().context(RunConfig(nranks=GPU_NUMBER, experiment=PROJECT_NAME)):

        config = ColBERTConfig(
            nbits=2,
            doc_maxlen=220,
        )
        indexer = Indexer(checkpoint=CHECKPOINT_PATH, config=config)
        indexer.index(name=PROJECT_NAME, collection=TSV_PATH, overwrite=True)

        indexer.get_index() # get the absolute path of the index
