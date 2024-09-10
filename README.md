True, false, or just opinions? Maybe not binary, but a percentage.

Fact-checking tools to combat disinformation.

## How It Works
Extract a list of statements from given text.  
For each statement search via search engine and read the top URLs.  
For each hostname as one source, extract most related info from the read content.  
For each sources, generate one verdict and citation with the extracted content.  
Combine all verdicts of one statements into a final verdict.  
Return a list of statements with verdicts, citations and others related.

## Get Started
Online demo: https://check.ittia.net

Using existing API: https://github.com/ittia-research/check/tree/main/packages/ittia_check

### Self-hosting API Server
Main components:
  - Check server: see docker-compose.yml
  - LLM: any OpenAI compatible API, self-hosting via vllm or Ollama
  - Embedding: self-hosting via Ollama or Infinity
  - Rerank: self-hosting via Infinity
  - Search: https://search.ittia.net

### Other Tools
- Start a wiki_dpr retrieval server (ColBERTv2) for development: https://github.com/ittia-research/check/tree/main/datasets/wiki_dpr

### Search backend
- Using `search.ittia.net` for better optimization.
- Features:
  - Customizable source count.
  - Supports search sessions: streaming, resuming.
  - Utilizes state-of-the-art search engine (currently Google).

## Design
Input something.

Analyze percentage of facts and opinions.

Fact-check like what a researcher will do:
  * Use search engine as data source and AI as the verdict.

Output analysis:
  * MARKDOWN as the default format, JSON optional. 

### Philosophy:
- For new information, doubts as default, fact-check follows.

### Elements
Input types:
- facts
- opinions
- questions

Verdicts:
- false
- true
- tie: false and true verdicts counts are the same and above zero
- irrelevant: context processed irrelevant to the statement

## References
### Fact-check
- https://www.snopes.com
- https://www.bmi.bund.de/SharedDocs/schwerpunkte/EN/disinformation/examples-of-russian-disinformation-and-the-facts.html

## Acknowledgements
- TPU Research Cloud team at Google
- Google Search
- Jina Reader
