from __future__ import annotations

from typing import Any


class EcosystemLegalMemory:
    def __init__(self) -> None:
        self.memory: list[dict[str, Any]] = []

    def store(self, item: dict[str, Any]) -> None:
        self.memory.append(item)

    def latest(self) -> list[dict[str, Any]]:
        return self.memory[-20:]
