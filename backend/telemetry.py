"""OpenTelemetry setup for VacanceAI Backend"""

import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor


def init_telemetry(app):
    """Initialize OpenTelemetry tracing and instrument the FastAPI app."""
    otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://jaeger:4318")

    resource = Resource.create({
        "service.name": "vacanceai-backend",
        "service.version": "1.0.0",
    })

    provider = TracerProvider(resource=resource)

    exporter = OTLPSpanExporter(endpoint=f"{otlp_endpoint}/v1/traces")
    provider.add_span_processor(BatchSpanProcessor(exporter))

    trace.set_tracer_provider(provider)

    # Auto-instrument all FastAPI routes
    FastAPIInstrumentor.instrument_app(app)

    print(f"OpenTelemetry initialized — exporting to {otlp_endpoint}")


def get_tracer(name: str = "vacanceai"):
    """Get a tracer instance for custom spans."""
    return trace.get_tracer(name)
