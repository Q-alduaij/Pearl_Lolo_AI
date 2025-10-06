# HRM Service Setup Guide

This guide walks you through hosting Sapient's Hierarchical Reasoning Model (HRM) alongside the Pearl Lolo AI Agent.

## 1. Prerequisites

- Python 3.10+
- CUDA-capable GPU (recommended) with the appropriate NVIDIA drivers installed
- `git` and `python3 -m pip`

## 2. Bootstrap the HRM repository

Run the helper script to clone the upstream HRM project and download the official checkpoints:

```bash
cd pearl-lolo-ai-agent
./scripts/setup_hrm.sh  # optional: provide a custom install directory
```

The script performs the following actions:

1. Clones `https://github.com/sapientinc/HRM` into `external/hrm` (or your custom directory)
2. Installs HRM Python dependencies into the active environment
3. Downloads the default HRM checkpoints via `scripts/download_models.py`

## 3. Launch the HRM microservice

HRM ships with Hydra-powered evaluation utilities. To expose them over HTTP for Pearl Lolo, use the minimal FastAPI service below (save as `external/hrm/service.py` or similar):

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from hrm.evaluate import load_model, run_inference  # Refer to the HRM repo utilities

app = FastAPI()
model_cache = {}

class SolveRequest(BaseModel):
    task: str
    prompt: str
    grid: list[list[int]] | None = None
    metadata: dict | None = None

@app.on_event("startup")
async def startup():
    model_cache["sudoku"] = load_model(task="sudoku")

@app.get("/health")
async def health():
    return {"status": "ok", "tasks": list(model_cache)}

@app.post("/solve")
async def solve(payload: SolveRequest):
    if payload.task not in model_cache:
        model_cache[payload.task] = load_model(task=payload.task)

    try:
        result = run_inference(model_cache[payload.task], payload.dict())
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    return {"task": payload.task, **result}
```

Run the service with:

```bash
cd external/hrm
uvicorn service:app --host 0.0.0.0 --port 8008
```

You can containerize the service later; for an initial test, running it locally is sufficient.

## 4. Configure Pearl Lolo to call HRM

Update `config.yaml` so that Pearl knows how to reach the service:

```yaml
ai:
  default_model: "hrm"  # or switch via the UI when supported
  models:
    hrm:
      enabled: true
      base_url: "http://localhost:8008"
      default_task: "sudoku"
      timeout: 45
      health_endpoint: "/health"
      check_health_on_startup: true
```

The defaults are already present in the repository; toggling `enabled` to `true` and pointing `base_url` to your service is enough.

## 5. Verify the integration

1. Start the Pearl Lolo AI Agent.
2. Ask Lolo to solve a Sudoku grid. The new HRM client (see `core/hrm_client.py`) auto-detects 9x9 grids and forwards them to the HRM service.
3. The returned JSON is rendered as a bilingual-friendly message, including optional reasoning steps.

If the service cannot be reached, the agent surfaces a friendly error message so you can diagnose connectivity or GPU issues quickly.

## 6. Next steps

- Extend the FastAPI service with additional HRM checkpoints (ARC, mazes, etc.).
- Persist the HRM outputs to Pearl's RAG store for retrieval-augmented tutoring on puzzles.
- Add authentication (API keys, mTLS) before exposing the service beyond localhost.
