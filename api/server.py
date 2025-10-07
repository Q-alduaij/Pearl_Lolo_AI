from fastapi import FastAPI
from typing import Dict
from core.contracts import Task, ProviderResult, Capability, Health
from core.router import Router
from core.settings import load_settings
from providers.llm import LlmProvider
from providers.llm_openai import OpenAiLlmProvider
from providers.rag import RagProvider
from providers.hrm import HrmProvider
from providers.stt import SttProvider
from providers.tts import TtsProvider
from providers.websearch import WebSearchProvider
import uvicorn

SETTINGS = load_settings()
app = FastAPI(title="LoLo Local API", version="0.1.0")

llm_provider = LlmProvider() if SETTINGS.llm_mode.mode == "local" else OpenAiLlmProvider()

providers = {
    Capability.CHAT: llm_provider,
    Capability.RAG: RagProvider(),
    Capability.SOLVE: HrmProvider(),
    Capability.STT: SttProvider(),
    Capability.TTS: TtsProvider(),
}
providers[Capability.SEARCH] = WebSearchProvider()
router = Router(providers)


@app.get("/health", response_model=Dict[str, Health])
def health() -> Dict[str, Health]:
    return {cap.name: provider.health() for cap, provider in providers.items()}


@app.post("/invoke", response_model=ProviderResult)
def invoke(task: Task) -> ProviderResult:
    return router.route(task)


if __name__ == "__main__":
    uvicorn.run(app, host=SETTINGS.api.host, port=SETTINGS.api.port)
