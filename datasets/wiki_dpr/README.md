## About
- Dataset: https://github.com/facebookresearch/DPR/blob/main/dpr/data/download_data.py
    - direct downlaod link: `https://dl.fbaipublicfiles.com/dpr/wikipedia_split/psgs_w100.tsv.gz`
- Generate index for the ColBERTv2 model
- Downlaod the generated index: https://huggingface.co/datasets/ittia/wiki_dpr
- Start a retrieve server

## How-to
### Indexing
1. Run container via Dockerfile.indexing;
2. Add the .tsv dataset to `/data/datasets/wiki/psgs_w100.tsv`;
3. Run `python3 indexing.py`.

### Serve
1. Run the GPU or CPU container via docker-compose.yml based on your hardware;
2. Add required files: .tsv dataset, model checkpoint, index;
    * Default locations of these files are within: `prepare_files.py`
    * You may add existing files or download from HuggingFace via `python3 prepare_files.py`
3. Start the server: `python3 server.py`.

Test the server: `curl "http://localhost:8893/api/search?query=Who%20won%20the%202022%20FIFA%20world%20cup&k=3"`