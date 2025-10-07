import os
import time
import httpx
from typing import List
from core.contracts import Provider, Capability, Task, ProviderResult, Health, Usage, Citation
from core.settings import load_settings
from core.logs import log

SETTINGS = load_settings()
TAVILY_KEY = os.getenv("TAVILY_API_KEY", "")
SERPAPI_KEY = os.getenv("SERPAPI_API_KEY", "")


class WebSearchProvider(Provider):
    name = "websearch"
    capabilities = [Capability.SEARCH]

    def health(self) -> Health:
        ok = SETTINGS.search.enabled
        details = {"provider": SETTINGS.search.provider, "enabled": SETTINGS.search.enabled}
        if not ok:
            details["note"] = "search disabled"
        else:
            if SETTINGS.search.provider == "tavily" and not TAVILY_KEY:
                ok = False
                details["error"] = "Missing TAVILY_API_KEY"
            if SETTINGS.search.provider == "serpapi" and not SERPAPI_KEY:
                ok = False
                details["error"] = "Missing SERPAPI_API_KEY"
        return Health(name=self.name, ok=ok, details=details)

    def _tavily(self, query: str, k: int) -> List[Citation]:
        url = "https://api.tavily.com/search"
        payload = {"api_key": TAVILY_KEY, "query": query, "max_results": k}
        with httpx.Client(timeout=SETTINGS.search.timeout_s) as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
        citations: List[Citation] = []
        for item in data.get("results", [])[:k]:
            citations.append(
                Citation(
                    source=item.get("url", ""),
                    snippet=item.get("content", "")[:400],
                    score=None,
                )
            )
        return citations

    def _serpapi(self, query: str, k: int) -> List[Citation]:
        url = "https://serpapi.com/search.json"
        params = {"engine": "google", "q": query, "api_key": SERPAPI_KEY}
        with httpx.Client(timeout=SETTINGS.search.timeout_s) as client:
            response = client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
        citations: List[Citation] = []
        for item in (data.get("organic_results") or [])[:k]:
            citations.append(
                Citation(
                    source=item.get("link", ""),
                    snippet=(item.get("snippet") or "")[:400],
                    score=None,
                )
            )
        return citations

    def invoke(self, task: Task) -> ProviderResult:
        if not SETTINGS.search.enabled:
            return ProviderResult(
                ok=False,
                text="Search disabled. Enable in config.",
                warnings=["search_disabled"],
            )
        query = task.messages[-1].content
        k = int(task.params.get("k", SETTINGS.search.max_results))
        start = time.time()
        try:
            if SETTINGS.search.provider == "tavily":
                if not TAVILY_KEY:
                    return ProviderResult(ok=False, text="Missing TAVILY_API_KEY.")
                citations = self._tavily(query, k)
            elif SETTINGS.search.provider == "serpapi":
                if not SERPAPI_KEY:
                    return ProviderResult(ok=False, text="Missing SERPAPI_API_KEY.")
                citations = self._serpapi(query, k)
            else:
                return ProviderResult(ok=False, text="Unknown search provider.")
            text = "Top results:\n" + "\n".join(
                f"- {citation.source}: {citation.snippet}" for citation in citations
            )
            usage = Usage(latency_ms=int((time.time() - start) * 1000))
            log(
                "websearch.invoke",
                provider=SETTINGS.search.provider,
                k=k,
                got=len(citations),
                latency_ms=usage.latency_ms,
            )
            return ProviderResult(ok=True, text=text, citations=citations, usage=usage)
        except Exception as exc:  # noqa: BLE001
            return ProviderResult(ok=False, text="Search failed.", warnings=[str(exc)])
