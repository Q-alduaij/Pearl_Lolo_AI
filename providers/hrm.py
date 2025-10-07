import re
import time
import httpx
from core.contracts import Provider, Capability, Task, ProviderResult, Health, Usage
from core.settings import load_settings
from core.logs import log
from core.utils import retry
from core.sudoku import pretty, is_valid_sudoku
from core.cache import get as cache_get, set_ as cache_set

SETTINGS = load_settings()
SUDOKU_BLOCK = re.compile(r"```sudoku\s+([\s\S]*?)```", re.IGNORECASE)


def _extract_sudoku_block(text: str) -> str | None:
    match = SUDOKU_BLOCK.search(text)
    if not match:
        return None
    raw = "".join(ch for ch in match.group(1) if ch.isdigit() or ch in ".0")
    digits = "".join("0" if ch == "." else ch for ch in raw if ch.isdigit() or ch == "0")
    return digits if len(digits) == 81 else None


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
        prompt = task.messages[-1].content
        block = _extract_sudoku_block(prompt)

        if SETTINGS.hrm.enforce_fenced_block and not block:
            return ProviderResult(
                ok=False,
                text="Include a fenced ```sudoku``` block.",
                warnings=["no_fenced_block"],
            )
        if block and not is_valid_sudoku(block):
            return ProviderResult(
                ok=False,
                text="Malformed Sudoku (duplicates/length).",
                warnings=["invalid_sudoku"],
            )

        cache_key = f"hrm:{block or prompt}"
        cached = cache_get(cache_key)
        if cached:
            text = "# HRM Solution (cache)\n"
            if (
                "solution" in cached
                and isinstance(cached["solution"], str)
                and len(cached["solution"]) == 81
            ):
                text += f"\n```text\n{pretty(cached['solution'])}\n```\n"
            if "steps" in cached:
                steps = cached["steps"]
                text += "\n**Steps**\n" + (
                    "\n".join(f"- {step}" for step in steps)
                    if isinstance(steps, list)
                    else str(steps)
                )
            return ProviderResult(
                ok=True,
                text=text,
                data=cached,
                warnings=["cached"],
                usage=Usage(latency_ms=int((time.time() - start) * 1000)),
            )

        payload = {"prompt": prompt, "task": "auto"}
        if block:
            payload["grid"] = block

        try:
            def call():
                with httpx.Client(timeout=SETTINGS.hrm.timeout_s) as client:
                    return client.post(SETTINGS.hrm.url + SETTINGS.hrm.solve_path, json=payload)

            response = retry(call, attempts=3, base_delay=0.4)
            response.raise_for_status()
            data = response.json()
            cache_set(cache_key, data)
            text = "# HRM Solution\n"
            if (
                "solution" in data
                and isinstance(data["solution"], str)
                and len(data["solution"]) == 81
            ):
                text += f"\n```text\n{pretty(data['solution'])}\n```\n"
            if "steps" in data:
                steps = data["steps"]
                text += "\n**Steps**\n" + (
                    "\n".join(f"- {step}" for step in steps)
                    if isinstance(steps, list)
                    else str(steps)
                )
            warnings = [] if block else ["No fenced ```sudoku``` block; auto-mode."]
            usage = Usage(latency_ms=int((time.time() - start) * 1000))
            log("hrm.invoke", has_block=bool(block), latency_ms=usage.latency_ms)
            return ProviderResult(ok=True, text=text, data=data, warnings=warnings, usage=usage)
        except Exception as exc:  # noqa: BLE001
            return ProviderResult(ok=False, text="", warnings=[f"HRM failed: {exc}"])
