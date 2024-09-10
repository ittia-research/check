True, false, or just opinions? Maybe not binary, but a percentage.

Fact-checking tools to combat disinformation.

## Get Started
Online demo: `https://check.ittia.net`

Use pip package `ittia-check` to connect to API: https://github.com/ittia-research/check/tree/main/packages/ittia_check

API docs: `https://check.ittia.net/docs`

### Search backend
- Using `search.ittia.net` for better optimization.
- API doc: `https://search.ittia.net/docs`
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
- irrelevant: context processed irrelevant to the statement

## References
### Fact-check
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
