from typing import Dict
from .contracts import Task, ProviderResult, Capability, Provider


class Router:
    def __init__(self, providers: Dict[Capability, Provider]):
        self.providers = providers

    def route(self, task: Task) -> ProviderResult:
        if task.intent in self.providers:
            return self.providers[task.intent].invoke(task)
        want_sources = any(
            "source" in m.content.lower() or "citation" in m.content.lower()
            for m in task.messages
        )
        if want_sources and Capability.RAG in self.providers:
            return self.providers[Capability.RAG].invoke(task)
        last = task.messages[-1].content.strip().lower()
        if (
            (last.startswith("net:") or last.startswith("search:"))
            and Capability.SEARCH in self.providers
        ):
            return self.providers[Capability.SEARCH].invoke(task)
        return self.providers[Capability.CHAT].invoke(task)
