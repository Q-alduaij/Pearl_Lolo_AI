import os
import time
import httpx
from core.contracts import Provider, Capability, Task, ProviderResult, Health, Usage
from core.logs import log

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", os.getenv("OPENAI_CHAT_MODEL", ""))

DEFAULT_MODEL = OPENAI_MODEL or "gpt-4o-mini"


class OpenAiLlmProvider(Provider):
    name = "llm_openai"
    capabilities = [Capability.CHAT]

    def health(self) -> Health:
        ok = True
        details = {"base_url": OPENAI_BASE_URL, "model": DEFAULT_MODEL}
        if not OPENAI_API_KEY:
            ok = False
            details["error"] = "Missing OPENAI_API_KEY"
        return Health(name=self.name, ok=ok, details=details)

    def invoke(self, task: Task) -> ProviderResult:
        if not OPENAI_API_KEY:
            return ProviderResult(ok=False, text="Set OPENAI_API_KEY in .env.local.")
        start = time.time()
        messages = [{"role": m.role, "content": m.content} for m in task.messages]
        headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
        payload = {"model": DEFAULT_MODEL, "messages": messages}
        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    f"{OPENAI_BASE_URL}/chat/completions",
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                usage = Usage(latency_ms=int((time.time() - start) * 1000))
                log("llm_openai.invoke", model=DEFAULT_MODEL, latency_ms=usage.latency_ms)
                return ProviderResult(ok=True, text=content, usage=usage)
        except Exception as exc:  # noqa: BLE001
            return ProviderResult(
                ok=False,
                text="OpenAI call failed.",
                warnings=[str(exc)],
            )
