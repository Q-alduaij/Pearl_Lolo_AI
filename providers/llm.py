import time
import httpx
from core.contracts import Provider, Capability, Task, ProviderResult, Health, Usage
from core.settings import load_settings
from core.logs import log

SETTINGS = load_settings()


class LlmProvider(Provider):
    name = "llm"
    capabilities = [Capability.CHAT]

    def health(self) -> Health:
        ok = True
        details = {}
        try:
            with httpx.Client(timeout=2.0) as client:
                response = client.get(f"{SETTINGS.llm.url}/api/tags")
                ok = response.status_code == 200
                details["models"] = [
                    tag["name"] for tag in (response.json().get("models", []))
                ] if ok else {}
        except Exception as exc:  # noqa: BLE001
            ok = False
            details["error"] = str(exc)
        return Health(name=self.name, ok=ok, details=details)

    def invoke(self, task: Task) -> ProviderResult:
        start = time.time()
        messages = [{"role": m.role, "content": m.content} for m in task.messages]
        last_err = None
        for model in (SETTINGS.llm.primary_model, SETTINGS.llm.fallback_model):
            try:
                with httpx.Client(timeout=SETTINGS.llm.timeout_s) as client:
                    response = client.post(
                        f"{SETTINGS.llm.url}/v1/chat/completions",
                        json={"model": model, "messages": messages},
                    )
                    response.raise_for_status()
                    content = response.json()["choices"][0]["message"]["content"]
                    usage = Usage(latency_ms=int((time.time() - start) * 1000))
                    log("llm.invoke", model=model, latency_ms=usage.latency_ms)
                    return ProviderResult(ok=True, text=content, usage=usage)
            except Exception as exc:  # noqa: BLE001
                last_err = str(exc)
        return ProviderResult(
            ok=False,
            text="LLM not reachable. Start Ollama and pull models.",
            warnings=[f"LLM failed: {last_err}" if last_err else "LLM failed"],
        )
