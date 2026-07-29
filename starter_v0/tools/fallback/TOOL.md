---
name: fallback
track: core
kind: live_api
provider: OpenAI
requires_env: [OPENAI_API_KEY]
inputs: [question]
outputs: [response]
side_effect: false
---

# fallback

Calls the OpenAI chat API directly to answer general questions that cannot be handled by the existing research tools (coding, math, general knowledge, conceptual explanations, etc.).

Use only when:
- The user asks a question OUTSIDE the scope of research/news/social tools
- No other tool (papers, lookup, fetch, etc.) is appropriate
- The question is conceptual, requires general knowledge, or is about coding/math

Do NOT use when a research tool could handle the request (e.g. searching papers, fetching URLs, looking up news).
