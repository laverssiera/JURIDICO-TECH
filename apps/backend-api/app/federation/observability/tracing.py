from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Iterator

from app.federation.config import settings

try:
    from opentelemetry import trace
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider

    _OTEL_AVAILABLE = True
except Exception:
    _OTEL_AVAILABLE = False

try:
    from prometheus_client import CollectorRegistry, Counter, Gauge, generate_latest

    _PROM_AVAILABLE = True
except Exception:
    _PROM_AVAILABLE = False


class _NoOpSpan:
    def set_attribute(self, *_: Any, **__: Any) -> None:
        return None


class _NoOpTracer:
    @contextmanager
    def start_as_current_span(self, _: str) -> Iterator[_NoOpSpan]:
        yield _NoOpSpan()


tracer = _NoOpTracer()


def _should_use_otel() -> bool:
    backend = settings.FEDERATION_OBSERVABILITY_BACKEND.lower()
    return backend in {"auto", "otel"} and _OTEL_AVAILABLE and _PROM_AVAILABLE


if _should_use_otel():
    resource = Resource.create(
        {
            "service.name": settings.MONOLITH_NAME,
            "service.version": "6.0",
            "liceu.layer": "legal-runtime",
        }
    )
    trace.set_tracer_provider(TracerProvider(resource=resource))
    tracer = trace.get_tracer("juridicotech.federation")


class UnifiedObservability:
    _events_total: dict[str, int] = {}
    _domain_health: dict[str, int] = {}
    _real_mode = _should_use_otel()
    _registry = CollectorRegistry() if _real_mode else None
    _counter = (
        Counter(
            "juridicotech_federation_events_total",
            "Total federation events",
            ["domain"],
            registry=_registry,
        )
        if _real_mode
        else None
    )
    _gauge = (
        Gauge(
            "juridicotech_federation_domain_health",
            "Current federation domain health",
            ["domain"],
            registry=_registry,
        )
        if _real_mode
        else None
    )

    @classmethod
    def record(cls, domain: str, status: str = "ok") -> dict[str, Any]:
        cls._events_total[domain] = cls._events_total.get(domain, 0) + 1
        cls._domain_health[domain] = 1 if status == "ok" else 0

        if cls._real_mode and cls._counter is not None and cls._gauge is not None:
            cls._counter.labels(domain=domain).inc()
            cls._gauge.labels(domain=domain).set(1 if status == "ok" else 0)

        with tracer.start_as_current_span(f"federation.{domain}") as span:
            span.set_attribute("federation.domain", domain)
            span.set_attribute("federation.status", status)
        return {"domain": domain, "status": status}

    @classmethod
    def snapshot(cls) -> dict[str, Any]:
        if cls._real_mode and cls._registry is not None:
            metrics = generate_latest(cls._registry).decode("utf-8")
        else:
            metrics_lines = [
                f'juridicotech_federation_events_total{{domain="{domain}"}} {count}'
                for domain, count in sorted(cls._events_total.items())
            ]
            metrics_lines.extend(
                f'juridicotech_federation_domain_health{{domain="{domain}"}} {value}'
                for domain, value in sorted(cls._domain_health.items())
            )
            metrics = "\n".join(metrics_lines)

        return {
            "service": settings.MONOLITH_NAME,
            "backend": "otel" if cls._real_mode else "memory",
            "metrics": metrics,
            "events_total": dict(cls._events_total),
            "domain_health": dict(cls._domain_health),
        }

    @classmethod
    def reset(cls) -> None:
        cls._events_total = {}
        cls._domain_health = {}
        if cls._real_mode:
            cls._registry = CollectorRegistry()
            cls._counter = Counter(
                "juridicotech_federation_events_total",
                "Total federation events",
                ["domain"],
                registry=cls._registry,
            )
            cls._gauge = Gauge(
                "juridicotech_federation_domain_health",
                "Current federation domain health",
                ["domain"],
                registry=cls._registry,
            )
