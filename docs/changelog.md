## application
2024/8/3:
  - Change from AutoGen to plain OpenAI, since AutoGen AssistantAgent adds system role which are not compateble with Gemma 2 + vllm.

## pipeline
2024/8/26:
  - Changed to multi-sources mode (divide sources based on hostname), instead of use all web search results as one single source.
2024/8/13:
  - Introduce DSPy to replace the get verdict part, with multi-step reasoning.