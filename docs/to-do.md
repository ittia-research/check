
## Frontend
- [ ] API: Input string or url, output analysis
- [ ] Optional more detailed output: correction, explanation, references

## Backend
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

## pipeline
DSPy:
- [ ] choose the right LLM temperature
- [ ] better training datasets

## Retrieval
- [ ] Better retrieval solution: high performance, concurrency, multiple index, index editable.
- [ ] Getting more sources when needed.

## Verdict
- [ ] Set final verdict standards.

## Toolchain
- [ ] Evaluate MLOps pipeline
  - https://kitops.ml
- [ ] Evaluate data quality of searching and url fetching. Better error handle.
- [ ] Use multiple sources for fact-check.

## Infra
- [ ] Stress test
- [ ] Meaningful health endpoint
- [ ] Monitoring service health

## Extend 
- [ ] To other types of media: image, audio, video, etc.
- [ ] Shall we try to answer questions if provided.
- [ ] Multi-language support.
- [ ] Add logging and long-term memory.
- [ ] Integrate with other fact-check services.

## Calculate
- [ ] Shall we calculate percentage of true and false in the input? Any better calculation than items count?

## Logging
- [ ] Full logging on chain of events for re-producing and debugging.

## Checkout
- [ ] Chroma #retrieve

## Issues
- [ ] Uses many different types of models, difficult for performance optimization and maintenance.
- [ ] LLM verdict wrong contradict to context provided.

## Research
- [ ] AI-generated misinformation