#!/usr/bin/env python3
"""Mirror OrderFlow structured events into the bounded Phase 4 OpenTelemetry trace path."""

from __future__ import annotations

import os
from collections.abc import Callable
from typing import Any

from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

from system.orderflow import service

RUNTIME_VERSION = "orderflow-otel-runtime-v1"


def run_service() -> int:
    """Run OrderFlow with optional OTel mirroring enabled by environment."""
    endpoint = os.environ.get("ORDERFLOW_OTEL_ENDPOINT", "").strip()
    if not endpoint:
        return service.main()

    role = os.environ.get("ORDERFLOW_ROLE", "unknown")
    version = os.environ.get("ORDERFLOW_VERSION", "unknown")
    provider = TracerProvider(
        resource=Resource.create(
            {
                "service.name": f"orderflow-{role}",
                "service.version": version,
                "orderflow.telemetry.runtime": RUNTIME_VERSION,
            }
        )
    )
    provider.add_span_processor(SimpleSpanProcessor(OTLPSpanExporter(endpoint=endpoint)))
    tracer = provider.get_tracer(RUNTIME_VERSION)

    original_emit: Callable[..., dict[str, Any]] = service.ServiceState.emit

    def instrumented_emit(
        state: service.ServiceState,
        event_type: str,
        **fields: Any,
    ) -> dict[str, Any]:
        event = original_emit(state, event_type, **fields)
        with tracer.start_as_current_span(f"orderflow.{event_type}") as span:
            for key in (
                "event_id",
                "run_id",
                "scenario_id",
                "source_component",
                "event_type",
                "software_version",
                "trace_id",
                "span_id",
                "order_id",
            ):
                value = event.get(key)
                if value is not None:
                    span.set_attribute(f"orderflow.{key}", str(value))
            span.set_attribute("orderflow.telemetry_contract", "otel-compatible-structured-event-v1")
        return event

    # Intentional process-local instrumentation hook. Dynamic setattr avoids
    # mypy's method-assignment restriction; B010 is suppressed narrowly here.
    setattr(service.ServiceState, "emit", instrumented_emit)  # noqa: B010
    try:
        return service.main()
    finally:
        provider.shutdown()


if __name__ == "__main__":
    raise SystemExit(run_service())
