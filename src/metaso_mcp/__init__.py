"""Metaso MCP server package."""

from __future__ import annotations

from importlib import import_module
from typing import Any

__all__ = ["app", "main"]


def __getattr__(name: str) -> Any:  # pragma: no cover - passthrough helper
    if name in {"app", "main"}:
        module = import_module(".app", __name__)
        return getattr(module, name)
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


def __dir__() -> list[str]:  # pragma: no cover - runtime nicety
    return sorted(set(globals()) | {"app", "main"})
