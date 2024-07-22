True, false, or just opinions? Maybe not binary, but a percentage.

Fact-checking tools to combat disinformation.

## Design
1. Input something.
2. Analize percentage of facts and opnions.
3. Factcheck like what a researcher will do:
  * Use search engine as data source and AI as the verdit.
4. Output analysis:
  * MARKDOWN as the default format, JSON as one option. 

Pholosophy:
- For new information, doubts as default, factcheck follows.

## Get Started
Online demo: https://check.ittia.net
* Due to limited GPU resources, availbility of this demo are limited.

## Support
Please contact if you can provide resources for this project:
- AI API access
- Hardware for hosting
- Data sources

## Elements
Input types:
- facts
- opnions
- questions

Verdits:
- true
- false
- uncheckable: can't check without more background
- unavailable: service unavailable

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

Contexts
- [ ] Filter out non-related contexts before send for verdict

### Toolchain
- [ ] Evaluate data quality of searching and url fetching. Better error handle.
- [ ] Use multiple sources for factcheck.

### Extend
- [ ] To other types of media: image, audio, video, etc.
- [ ] Shall we try to anser questions if provided.
- [ ] Multi-language support.
- [ ] Add logging and long-term memory.
- [ ] Intergrate with other factcheck services.

### Calculate
- [ ] Shall we calculate percentage of true and false in the input? Any better calculation than items count?

## References
### Reports
- [ ] AI-generated misinformation
### Factcheck
- https://www.bmi.bund.de/SharedDocs/schwerpunkte/EN/disinformation/examples-of-russian-disinformation-and-the-facts.html

## Thanks
- Jina Reader: https://jina.ai
