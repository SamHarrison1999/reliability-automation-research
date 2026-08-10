#!/bin/sh
set -eu

if [ "${ORDERFLOW_ROLE}" = "telemetry-sink" ]; then
  exec python /app/telemetry_sink.py --host 0.0.0.0 --port 4319 --output-dir /tmp/orderflow-otel-sink
fi

common_args="--role ${ORDERFLOW_ROLE} --port ${ORDERFLOW_PORT} --version ${ORDERFLOW_VERSION} --event-file /tmp/orderflow-events.jsonl --run-id ${ORDERFLOW_RUN_ID} --scenario-id ${ORDERFLOW_SCENARIO_ID} --host 0.0.0.0"

if [ "${ORDERFLOW_ROLE}" = "order-api" ]; then
  # shellcheck disable=SC2086
  exec python -m system.orderflow.otel_runtime ${common_args} --dependency-url "${ORDERFLOW_DEPENDENCY_URL}"
fi

# shellcheck disable=SC2086
exec python -m system.orderflow.otel_runtime ${common_args}
