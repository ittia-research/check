## application
2024/8/3:
  - Change from AutoGen to plain OpenAI, since AutoGen AssistantAgent adds system role which are not compatible with Gemma 2 + vllm.

## pipeline
2028/9/2:
  - Changed search backend to `https://search.ittia.net` for better optimization.
2024/8/26:
  - Changed to multi-sources mode (divide sources based on hostname), instead of use all web search results as one single source.
2024/8/13:
  - Introduce DSPy to replace the get verdict part, with multi-step reasoning.