from __future__ import annotations

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def setup_runtime_tracing() -> None:
    provider = trace.get_tracer_provider()
    if isinstance(provider, TracerProvider):
        return

    trace.set_tracer_provider(TracerProvider())
    tracer_provider = trace.get_tracer_provider()
    processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="tempo:4317", insecure=True))
    tracer_provider.add_span_processor(processor)


setup_runtime_tracing()
tracer = trace.get_tracer("juridicotech")
