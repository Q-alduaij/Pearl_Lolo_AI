# LoLo (Local-first Desktop Aide)

Private, offline-first aide with LLM (Ollama), Hybrid RAG (Chroma+BM25), HRM solver, and a PySide6 UI.

## Quickstart
```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .
python scripts/pull_models.py              # ensure Ollama models (optional)
python scripts/build_indexes.py --path data/*.md --tags "UN-Habitat Kuwait"
python scripts/run_desktop.py              # launches UI (spawns backend if needed)
```

HRM best practice

- Use the **solve** intent for structured reasoning and planning tasks.
- Provide context, constraints, and desired outputs in natural language; the provider
  sends the full conversation to the HRM microservice for hierarchical planning.
- Pass optional knobs in `params`, e.g. `{ "hrm_task": "plan" }` or `{ "strategy": "cot" }` to
  steer the upstream service.
- Configure defaults in `config/config.yaml` under the `hrm` section if you want a preferred
  `default_task` or `default_strategy` applied automatically.

Notes
• All data/logs in ~/.lolo/
• No telemetry; local only

---

## Optional: Online Search + External LLM

LoLo is offline-first. To enable online features:

### Web Search
1. In `config/config.yaml` set:
   ```yaml
   search:
     enabled: true
     provider: "tavily"   # or "serpapi"
     max_results: 5
   ```
2. Put your key in .env.local:
   ```
   # For Tavily
   TAVILY_API_KEY=sk-...
   # OR for SerpAPI
   SERPAPI_API_KEY=...
   ```
3. In the UI, pick template “Web Search (NET)” or set intent to search.

### External LLM (OpenAI)
1. In `config/config.yaml` set:
   ```yaml
   llm_mode:
     mode: "openai"
   ```
2. Put your key in .env.local:
   ```
   OPENAI_API_KEY=sk-...
   OPENAI_MODEL=gpt-4o-mini   # optional
   OPENAI_BASE_URL=           # optional, e.g. a compatible gateway
   ```
3. Restart LoLo. /health should show llm_openai OK.

---

## Security & privacy notes (operational)

- Keys **never** live in git; only `.env.local`.
- Keep **search disabled** by default to remain fully offline.
- If you use a custom OpenAI-compatible gateway, set `OPENAI_BASE_URL`.
- The web search provider returns **URLs + snippets** only; if you plan to summarise externally, keep that through your LLM provider (local or external).

---

## Operational runbook

```bash
# 1) Create and activate env
python -m venv .venv && source .venv/bin/activate

# 2) Install
pip install -e .

# 3) (Optional) Pull LLMs for Ollama (make sure `ollama serve` running)
python scripts/pull_models.py

# 4) Build a tiny RAG index
python scripts/build_indexes.py --path data/*.md --tags "UN-Habitat Kuwait"

# 5) Launch desktop (spawns backend if needed)
python scripts/run_desktop.py
```

Smoke tests

```bash
pytest -q
curl -s http://127.0.0.1:8777/health | jq
```
