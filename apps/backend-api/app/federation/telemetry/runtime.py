from __future__ import annotations

from typing import Any

from app.federation.observability.tracing import UnifiedObservability


class TelemetryRuntime:
    def snapshot(self) -> dict[str, Any]:
        return UnifiedObservability.snapshot()
