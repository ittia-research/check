## Goals
This topic is very complicated. Here we try to define some clean goals:
- Ability to fact-check given information.
- A open source database of facts, with connections and hierarchy between facts. Build a foundation.
- Open access tools for real-time fact-checking.
- Broad media entity quality assess, including social media.
- Enrich first-hand facts. Make facts afloat.

## Roadmap
- [ ] Check one line of single statement.
- [ ] Check long paragraphs or a content source (URL, file, etc.)
  - [ ] What's the ultimate goals?
- [ ] Long-term memory and caching.
- [ ] Fact-check standards and database.

## Alphabet
context:
  - Every sides (it's question and answer in QA setup) has context.
  - There might be multiple points, for example social context.
  - It can be commonly accepted knowledge or extra facts.

- [ ] How to handle context in RAG? Needs to ensure integrity.

## Work
### Frontend
- [ ] API: Input string or url, output analysis
- [ ] Optional more detailed output: correction, explanation, references

### Backend
- [ ] Get list of facts from input, improve performance
- [ ] Get search results of each facts and check if they are true or false
- [ ] Get weight of facts and opinions
- [ ] Compare different search engines.
- [ ] Add support for URL input
- [ ] Performance benchmark.

LLM
- [ ] Better way to handle LLM output formatting: list, JSON.

Embedding:
- [ ] chunk size optimize

Contexts
- [ ] Filter out non-related contexts before send for verdict

Retrieval
- [ ] Retrieve the latest info when facts might change

### pipeline
DSPy
  - [ ] choose the right LLM temperature
  - [ ] better training datasets

### Retrieval
- [ ] Better retrieval solution: high performance, concurrency, multiple index, index editable.
- [ ] Getting more sources when needed.

### Verdict
- [ ] Set final verdict standards.

### Toolchain
- [ ] Evaluate MLOps pipeline: https://kitops.ml
- [ ] Evaluate data quality of searching and url fetching. Better error handle.
- [ ] Use multiple sources for fact-check.

### Infra
- [ ] Stress test
- [ ] Meaningful health endpoint
- [ ] Monitoring service health

### Calculate
- [ ] Shall we calculate percentage of true and false in the input? Any better calculation than items count?

### Logging
- [ ] Full logging on chain of events for re-producing and debugging.

### Issues
- [ ] Uses many different types of models, difficult for performance optimization and maintenance.
- [ ] LLM verdict wrong contradict to context provided.

### Data
- [ ] A standard on save fact-check related data.
- [ ] Store fact-check data with standards.

### Research
- [ ] Chroma #retrieve
- [ ] AI-generated misinformation

### Extend 
- [ ] To other types of media: image, audio, video, etc.
- [ ] Shall we try to answer questions if provided.
- [ ] Multi-language support.
- [ ] Add logging and long-term memory.
- [ ] Integrate with other fact-check services.
 
### Legal
- [ ] Copyright: citations, etc.

## Considerations
RAG:
  - Order-Preserve RAG

## References
- [ ] https://github.com/ICTMCG/LLM-for-misinformation-research