# Research Paper Scout — Implementation Plan

## Outcome

Deliver a friendly Streamlit research web app that reuses the existing agent loop, supports OpenAI, OpenRouter, Gemini (and the existing Anthropic adapter), exposes complete tool traces and artifact versions, and satisfies the Day 04 submission contract.

## Workstreams

1. **Prompt & provider integration**
   - Replace the unsafe baseline prompt with research-specific routing, clarification, citation, and confirmation rules.
   - Make provider setup discover keys safely from `starter_v0/.env` or the repository-level `.env`.
   - Keep model selection configurable and never render or log API keys.

2. **Research tool capability**
   - Add a team-authored `citation_generator` tool with APA and BibTeX output.
   - Register it in Python and `artifacts/tools.yaml` with a strict schema.
   - Smoke-test the tool contract locally.

3. **Research UI**
   - Build `starter_v0/app.py` with an editorial cream/ink/red visual language inspired by the supplied reference.
   - Reuse `chat.run_model_tool_loop`; provide chat history, sample prompts, provider/model/version controls, tool trace, artifact hashes, transcript persistence, and clear error/empty states.
   - Add Streamlit and supporting configuration to dependencies.

4. **QA, eval, and handoff**
   - Author exactly 10 group cases (5 single-turn + 5 multi-turn).
   - Fill the report sections that can be supported without fabricating live-run evidence; clearly mark evidence that requires real paid/API runs.
   - Run static compilation, schema checks, local tool smoke tests, provider preflight where configured, and a Streamlit startup health check.

## Guardrails

- Do not expose, copy, commit, or print API-key values.
- Do not invent v0–v3 metrics, run files, or public deployment URLs.
- External send/publish actions require explicit confirmation.
- Preserve the existing agent loop and provider abstraction instead of creating a second implementation.

