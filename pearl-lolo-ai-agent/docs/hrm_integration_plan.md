# Integrating Sapient HRM with Pearl Lolo AI Agent

## 1. What HRM Provides

Sapient's [Hierarchical Reasoning Model (HRM)](https://github.com/sapientinc/HRM) is a 27M-parameter recurrent architecture that pairs slow, abstract planning with fast, detailed computation to solve compositional reasoning tasks in a single forward pass. The public checkpoints cover domains such as Sudoku, ARC-AGI, and large mazes and can be fine-tuned on small (~1K example) datasets. HRM requires a CUDA-enabled GPU, PyTorch, Hydra/OmegaConf, and optional W&B logging.

The accompanying arXiv paper (arXiv:2506.21734) emphasizes:

- **Hierarchical controller design** – a top-level planner and low-level worker with shared recurrent state.
- **Strong generalization** from tiny supervised datasets without chain-of-thought traces.
- **Competitive ARC performance** against much larger transformer baselines.

These characteristics make HRM a natural candidate for structured reasoning micro-services inside Pearl Lolo AI.

## 2. Opportunities for Pearl Lolo AI

Pearl Lolo AI already abstracts LLM providers in `core/ai_engine.py` and exposes configuration-driven model selection via `config.yaml`.【F:core/ai_engine.py†L14-L118】【F:config.yaml†L1-L40】 HRM can enrich this stack in several ways:

1. **Specialist puzzle/tool solver** – route grid- or logic-based tasks (Sudoku, mazes, ARC-style) to a hosted HRM checkpoint instead of a general LLM.
2. **Deliberate reasoning aide** – use HRM outputs to seed or critique Ollama/OpenAI completions when the user enables a "deep reasoning" mode.
3. **Offline expansion** – HRM's small footprint and local training recipes align with Pearl's offline-first ethos.

## 3. Recommended Architecture

### 3.1 Service Layout

- **Inference microservice**: Wrap HRM's `evaluate.py` into a lightweight API (FastAPI/Flask) that loads a chosen checkpoint once and exposes `/solve` endpoints for each supported domain. Use GPU-backed worker; add a CPU fallback that streams intermediate logits if needed.
- **Agent tool hook**: Extend `AIEngine` with a `hrm` provider that sends structured prompts or raw puzzle encodings to the microservice. Leverage Pearl's existing routing logic so users can pick `hrm` via configuration.
- **Task router**: Create heuristics (regex, UI toggle, or classification model) that recognize when a request matches HRM-capable domains, then call HRM first and feed its result back into the conversation context.

### 3.2 Data Interface

- HRM checkpoints expect tensor inputs (e.g., Sudoku grids). Provide conversion utilities (Python module under `core/tools/hrm_adapter.py`) that translate between user-friendly formats and HRM tensors.
- Persist puzzle metadata alongside responses so Pearl's RAG system can index solved examples for future retrieval.

### 3.3 Deployment Options

| Mode | Description | Pros | Cons |
| --- | --- | --- | --- |
| **Local GPU** | Bundle HRM into the same host as Pearl via Docker Compose. | Lowest latency, offline. | Requires CUDA-capable hardware. |
| **Remote GPU service** | Deploy HRM inference to a separate GPU VM; Pearl calls via HTTPS. | Scales independently. | Adds network latency, requires auth. |
| **On-demand training** | Trigger HRM fine-tunes on user-supplied puzzles using repo's `pretrain.py`. | Custom specialization. | Long-running jobs; needs job queue + monitoring. |

## 4. Implementation Steps

1. **Vendor HRM**
   - Add HRM as a git submodule or download tagged release into `external/hrm`.
   - Mirror `requirements.txt` entries into Pearl's optional extras.
2. **Environment setup**
   - Validate CUDA availability, install FlashAttention variant, and expose `CUDA_HOME` for runtime builds.
   - Prepare `scripts/setup_hrm.sh` to automate dependency installation and checkpoint download.
3. **Inference wrapper**
   - Implement `scripts/run_hrm_service.py` that loads `evaluate.py` utilities, deserializes Hugging Face checkpoints, and serves a JSON API.
   - Cache model instances per domain to avoid reload cost.
4. **Core integration**
   - Extend `config.yaml` with an `ai.models.hrm` entry containing endpoint URL, default domain, and timeout.
   - Update `core/ai_engine.py` to detect `provider == 'hrm'` and call the microservice, wrapping errors similar to other providers.【F:core/ai_engine.py†L52-L115】
   - Register HRM as a callable tool in the UI so users can switch providers or auto-route via new "Reasoning" toggle.
5. **Task routing & UX**
   - Add heuristics in `bilingual_processor` (or a new middleware) to parse puzzle inputs (e.g., 9x9 grid) and dispatch to HRM.
   - Surface HRM explanations in both Arabic and English; optionally prompt a general LLM to translate/expand HRM's concise outputs.
6. **Testing & Monitoring**
   - Use HRM's `evaluate.py` to validate inference accuracy after integration.
   - Log service latency and success metrics; integrate with W&B if GPU host has internet, or store locally.

## 5. Example Workflow

1. User pastes an unsolved Sudoku grid in Pearl UI.
2. Router detects the grid format and posts JSON payload to the HRM service: `{ "task": "sudoku", "grid": [[0,0,3,...]] }`.
3. HRM returns the solved grid and optional step reasoning.
4. Pearl formats the response bilingually and includes the solved grid plus explanation, attributing HRM as the solver.
5. Conversation history stores both the user prompt and HRM output for future retrieval via RAG.

## 6. Future Enhancements

- **Multi-domain HRM ensemble**: Train additional checkpoints for logic word problems or planning tasks.
- **Hybrid reasoning**: Feed HRM intermediate states (halt logits) into a transformer model to verbalize reasoning steps.
- **User-generated datasets**: Leverage Pearl's bilingual interface to collect puzzles/solutions that fine-tune HRM, closing the loop.

By encapsulating HRM as a specialized reasoning provider, Pearl Lolo AI can offer high-accuracy solutions on structured tasks while preserving its bilingual, offline-friendly experience.
