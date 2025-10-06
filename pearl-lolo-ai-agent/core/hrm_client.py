#!/usr/bin/env python3
"""HTTP client helpers for interacting with Sapient's HRM service."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import requests


class HRMClientError(RuntimeError):
    """Raised when an HRM service request fails."""


@dataclass
class HRMRequest:
    """Container describing the outbound payload sent to the HRM service."""

    task: str
    body: Dict[str, Any]


class HRMClient:
    """Lightweight HTTP client for the HRM microservice."""

    def __init__(
        self,
        base_url: str,
        default_task: str = "sudoku",
        timeout: int = 30,
        health_endpoint: str = "/health",
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.default_task = default_task
        self.timeout = timeout
        self.health_endpoint = health_endpoint
        self.logger = logger or logging.getLogger(__name__)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def check_health(self) -> bool:
        """Ensure the remote HRM service is reachable."""

        url = f"{self.base_url}{self.health_endpoint}"
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            return True
        except requests.RequestException as exc:  # pragma: no cover - network failure handling
            raise HRMClientError(f"HRM health check failed: {exc}") from exc

    def should_route(self, prompt: str) -> bool:
        """Heuristic to determine if the prompt matches an HRM-friendly puzzle."""

        if not prompt:
            return False

        grid = self._extract_sudoku_grid(prompt)
        if grid is not None:
            return True

        lowered = prompt.lower()
        keywords = ("sudoku", "maze", "grid", "arc", "puzzle", "logic")
        return any(keyword in lowered for keyword in keywords)

    def solve(
        self,
        prompt: str,
        task: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Submit a puzzle request to the HRM service and return the JSON response."""

        request = self._build_request(prompt, task, metadata)
        url = f"{self.base_url}/solve"
        try:
            response = requests.post(url, json=request.body, timeout=self.timeout)
            response.raise_for_status()
            data: Dict[str, Any] = response.json()
        except requests.RequestException as exc:  # pragma: no cover - network failure handling
            raise HRMClientError(f"HRM request failed: {exc}") from exc
        except ValueError as exc:
            raise HRMClientError("HRM response was not valid JSON") from exc

        if not isinstance(data, dict):
            raise HRMClientError("HRM response payload must be a JSON object")

        return data

    def format_response(self, response: Dict[str, Any]) -> str:
        """Render an HRM JSON response into user-facing markdown."""

        if not isinstance(response, dict):
            return str(response)

        solved_task = response.get("task", self.default_task)
        solution = response.get("result") or response.get("solution")
        steps: Optional[List[str]] = None
        raw_steps = response.get("steps") or response.get("reasoning")
        if isinstance(raw_steps, list):
            steps = [str(step) for step in raw_steps]
        elif isinstance(raw_steps, str):
            steps = [raw_steps]

        lines = [f"🧠 **HRM ({solved_task}) Solution**"]
        if solution is not None:
            if isinstance(solution, list):
                pretty = self._render_grid(solution)
                if pretty:
                    lines.append("\n" + pretty)
                else:
                    lines.append(f"\n{solution}")
            else:
                lines.append(f"\n{solution}")
        else:
            lines.append("\nNo solution field returned by the HRM service.")

        if steps:
            lines.append("\n**Reasoning Steps:**")
            for idx, step in enumerate(steps, start=1):
                lines.append(f"{idx}. {step}")

        diagnostics = response.get("diagnostics")
        if diagnostics:
            lines.append("\n**Diagnostics:**")
            if isinstance(diagnostics, dict):
                for key, value in diagnostics.items():
                    lines.append(f"- {key}: {value}")
            else:
                lines.append(f"- {diagnostics}")

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _build_request(
        self,
        prompt: str,
        task: Optional[str],
        metadata: Optional[Dict[str, Any]],
    ) -> HRMRequest:
        detected_task = task or self._detect_task(prompt)
        body: Dict[str, Any] = {
            "task": detected_task,
            "prompt": prompt,
        }
        grid = self._extract_sudoku_grid(prompt)
        if grid is not None:
            body["grid"] = grid
        if metadata:
            body["metadata"] = metadata

        return HRMRequest(task=detected_task, body=body)

    def _detect_task(self, prompt: str) -> str:
        if not prompt:
            return self.default_task
        if self._extract_sudoku_grid(prompt) is not None:
            return "sudoku"
        lowered = prompt.lower()
        if "maze" in lowered:
            return "maze"
        if "arc" in lowered:
            return "arc"
        if "puzzle" in lowered:
            return "logic"
        return self.default_task

    def _extract_sudoku_grid(self, prompt: str) -> Optional[List[List[int]]]:
        digits = [char for char in prompt if char.isdigit()]
        if len(digits) != 81:
            return None

        try:
            numbers = [int(char) for char in digits]
        except ValueError:
            return None

        grid = [numbers[index : index + 9] for index in range(0, 81, 9)]
        return grid

    def _render_grid(self, grid: Any) -> str:
        try:
            rows = [
                " ".join(str(cell) for cell in row)
                for row in grid
                if isinstance(row, (list, tuple))
            ]
            if not rows:
                return ""
            separator = "\n"
            return separator.join(rows)
        except Exception:  # pragma: no cover - formatting fallback
            return ""
