True, false, or just opinions? Maybe not binary, but a percentage.

Fact-checking tools to combat disinformation.

## Get Started
Online demo: https://check.ittia.net

## Design
Input something.

Analize percentage of facts and opnions.

Factcheck like what a researcher will do:
  * Use search engine as data source and AI as the verdit.

Output analysis:
  * MARKDOWN as the default format, JSON as one option. 

### Pholosophy:
- For new information, doubts as default, factcheck follows.

### Elements
Input types:
- facts
- opnions
- questions

Verdits:
- true
- false
- uncheckable: can't check without more background
- unavailable: service unavailable

## Support
Please contact if you can provide resources for this project:
- AI API access
- Hardware for hosting
- Data sources

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
- [ ] Ollama embedding performance

Contexts
- [ ] Filter out non-related contexts before send for verdict

Retrieval
- [ ] Retrieve the latest info when facts might change

### pipeline
DSPy:
- [ ] make dspy.settings apply to sessions only in order to support multiple retrieve index

### Toolchain
- [ ] Evaluate MLOps pipeline
  - https://kitops.ml
- [ ] Evaluate data quality of searching and url fetching. Better error handle.
- [ ] Use multiple sources for factcheck.

### Stability
- [ ] AI backend stress test, especially xinference.

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

### Doc
- [ ] Show current tech stack.

### Checkout
- [ ] Chroma #retrieve

## Issues
- [ ] Uses many different types of models, diffcult for performance optimization and maintenance.
- [ ] LLM verdit wrong contradict to context provided.

## References
### Reports
- [ ] AI-generated misinformation
### Factcheck
- https://www.bmi.bund.de/SharedDocs/schwerpunkte/EN/disinformation/examples-of-russian-disinformation-and-the-facts.html
### Resources
#### Inference
- https://console.groq.com/docs/ (free tier)

## Acknowledgements
- TPU Research Cloud team at Google
- Google Search
- Jina Reader
