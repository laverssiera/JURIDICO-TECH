from __future__ import annotations

from contextlib import nullcontext

try:
    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
except Exception:
    trace = None
    OTLPSpanExporter = None
    TracerProvider = None
    BatchSpanProcessor = None


class _NoopTracer:
    def start_as_current_span(self, _: str):
        return nullcontext()


def setup_runtime_tracing() -> None:
    if trace is None or TracerProvider is None or BatchSpanProcessor is None or OTLPSpanExporter is None:
        return

    provider = trace.get_tracer_provider()
    if isinstance(provider, TracerProvider):
        return

    trace.set_tracer_provider(TracerProvider())
    tracer_provider = trace.get_tracer_provider()
    processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="tempo:4317", insecure=True))
    tracer_provider.add_span_processor(processor)


setup_runtime_tracing()
tracer = trace.get_tracer("juridicotech") if trace is not None else _NoopTracer()
