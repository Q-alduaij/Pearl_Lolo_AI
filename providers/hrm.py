"""HRM provider that forwards Pearl LoLo tasks to the Sapient HRM service."""

from __future__ import annotations

import json
import time
from typing import Any, Dict, Iterable

import httpx

from core.cache import get as cache_get, set_ as cache_set
from core.contracts import Capability, Health, Provider, ProviderResult, Task, Usage
from core.logs import log
from core.settings import load_settings
from core.utils import retry

SETTINGS = load_settings()


def _flatten_messages(task: Task) -> str:
    """Render the conversational history into a single prompt string."""

    parts = []
    for msg in task.messages:
        role = msg.role.capitalize()
        content = msg.content.strip()
        parts.append(f"[{role}] {content}")
    return "\n\n".join(parts)


def _format_iterable(items: Iterable[Any]) -> str:
    lines = []
    for item in items:
        if isinstance(item, dict):
            lines.append("- " + json.dumps(item, ensure_ascii=False))
        else:
            lines.append(f"- {item}")
    return "\n".join(lines)


def _summarise_payload(data: Dict[str, Any]) -> str:
    """Create a human readable markdown summary of HRM response payloads."""

    sections: list[str] = []
    preferred_text_fields = [
        "answer",
        "final_answer",
        "solution",
        "response",
        "output",
        "text",
    ]

    for field in preferred_text_fields:
        value = data.get(field)
        if isinstance(value, str) and value.strip():
            sections.append(f"**{field.replace('_', ' ').title()}**\n{value.strip()}")

    if isinstance(data.get("steps"), list) and data["steps"]:
        sections.append("**Steps**\n" + _format_iterable(data["steps"]))

    if isinstance(data.get("plan"), list) and data["plan"]:
        sections.append("**Plan**\n" + _format_iterable(data["plan"]))

    if isinstance(data.get("insights"), list) and data["insights"]:
        sections.append("**Insights**\n" + _format_iterable(data["insights"]))

    if not sections:
        pretty = json.dumps(data, ensure_ascii=False, indent=2)
        sections.append(f"```json\n{pretty}\n```")

    return "\n\n".join(sections)


class HrmProvider(Provider):
    name = "hrm"
    capabilities = [Capability.SOLVE]

    def health(self) -> Health:
        try:
            def call():
                with httpx.Client(timeout=3.0) as client:
                    return client.get(SETTINGS.hrm.url + SETTINGS.hrm.health_path)

            response = retry(call, attempts=2, base_delay=0.2)
            ok = response.status_code == 200
            details = response.json() if ok else {"status_code": response.status_code}
            return Health(name=self.name, ok=ok, details=details)
        except Exception as exc:  # noqa: BLE001
            return Health(name=self.name, ok=False, details={"error": str(exc)})

    def invoke(self, task: Task) -> ProviderResult:
        start = time.time()

        prompt = _flatten_messages(task)
        hrm_task = str(task.params.get("hrm_task", SETTINGS.hrm.default_task))
        strategy = task.params.get("strategy", SETTINGS.hrm.default_strategy)
        payload: Dict[str, Any] = {
            "prompt": prompt,
            "task": hrm_task,
            "metadata": {
                "locale": task.locale,
                "tz": task.tz,
                "tags": task.user_tags,
            },
        }

        if isinstance(strategy, str) and strategy:
            payload["strategy"] = strategy

        cache_key = f"hrm:{json.dumps(payload, ensure_ascii=False, sort_keys=True)}"
        cached = cache_get(cache_key)
        if cached:
            usage = Usage(latency_ms=int((time.time() - start) * 1000))
            return ProviderResult(
                ok=True,
                text="# HRM Result (cached)\n\n" + _summarise_payload(cached),
                data=cached,
                warnings=["cached"],
                usage=usage,
            )

        try:
            def call():
                with httpx.Client(timeout=SETTINGS.hrm.timeout_s) as client:
                    return client.post(SETTINGS.hrm.url + SETTINGS.hrm.solve_path, json=payload)

            response = retry(call, attempts=3, base_delay=0.4)
            response.raise_for_status()
            data = response.json()
            cache_set(cache_key, data)

            usage = Usage(latency_ms=int((time.time() - start) * 1000))
            log("hrm.invoke", task=hrm_task, latency_ms=usage.latency_ms)
            return ProviderResult(
                ok=True,
                text="# HRM Result\n\n" + _summarise_payload(data),
                data=data,
                usage=usage,
            )
        except Exception as exc:  # noqa: BLE001, pragma: no cover - network failure surface
            return ProviderResult(ok=False, text="HRM request failed.", warnings=[str(exc)])
