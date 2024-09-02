True, false, or just opinions? Maybe not binary, but a percentage.

Fact-checking tools to combat disinformation.

## Get Started
Fact-check:
  - Online demo: `https://check.ittia.net`
  - API docs: `https://check.ittia.net/doc`

Search backend:
  - Using self-hosted search backend for better optimization.
  - API doc: `https://search.ittia.net/doc`
  - Features:
    - Use first-class search engine, Google at this moment.
    - Customize count of sources.
    - Supports search session: streaming, resume.

## Design
Input something.

Analize percentage of facts and opnions.

Factcheck like what a researcher will do:
  * Use search engine as data source and AI as the verdit.

Output analysis:
  * MARKDOWN as the default format, JSON optional. 

### Pholosophy:
- For new information, doubts as default, factcheck follows.

### Elements
Input types:
- facts
- opnions
- questions

Verdits:
- false
- true
- irrelevant: context processed irrelevant to the statement

## Todo
### Frontend
- [ ] API: Input string or url, output analysis
- [ ] Optional more detailed output: correction, explannation, references

### Backend
- [ ] Get list of facts from input, improve performance
- [ ] Get search results of each facts and check if they are true or false
- [ ] Get weight of facts and opnions
- [ ] Compare different search engines.
- [ ] Add support for URL input
- [ ] Performance benchmark.

LLM
- [ ] Better way to handle LLM output formating: list, JSON.

Embedding:
- [ ] chunk size optimize

Contexts
- [ ] Filter out non-related contexts before send for verdict

Retrieval
- [ ] Retrieve the latest info when facts might change

### pipeline
DSPy:
- [ ] choose the right LLM temperature
- [ ] better training datasets

### Retrival
- [ ] Better retrival solution: high performance, concurrency, multiple index, index editable.
- [ ] Getting more sources when needed.

### Verdict
- [ ] Set final verdict standards.

### Toolchain
- [ ] Evaluate MLOps pipeline
  - https://kitops.ml
- [ ] Evaluate data quality of searching and url fetching. Better error handle.
- [ ] Use multiple sources for factcheck.

### Stability
- [ ] Stress test.

### Extend
- [ ] To other types of media: image, audio, video, etc.
- [ ] Shall we try to anser questions if provided.
- [ ] Multi-language support.
- [ ] Add logging and long-term memory.
- [ ] Intergrate with other factcheck services.

### Calculate
- [ ] Shall we calculate percentage of true and false in the input? Any better calculation than items count?

### Logging
- [ ] Full logging on chain of events for re-producing and debugging.

### Checkout
- [ ] Chroma #retrieve

## Issues
- [ ] Uses many different types of models, diffcult for performance optimization and maintenance.
- [ ] LLM verdit wrong contradict to context provided.

## References
### Reports
- [ ] AI-generated misinformation

### Factcheck
- https://www.snopes.com
- https://www.bmi.bund.de/SharedDocs/schwerpunkte/EN/disinformation/examples-of-russian-disinformation-and-the-facts.html

### Resources
Inference
  - https://console.groq.com/docs/ (free tier)
Search and fetch:
  - https://jina.ai/read

## Acknowledgements
- TPU Research Cloud team at Google
- Google Search
- Jina Reader
