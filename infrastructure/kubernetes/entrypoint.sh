#!/bin/sh
set -eu

common_args="--role ${ORDERFLOW_ROLE} --port ${ORDERFLOW_PORT} --version ${ORDERFLOW_VERSION} --event-file /tmp/orderflow-events.jsonl --run-id ${ORDERFLOW_RUN_ID} --scenario-id ${ORDERFLOW_SCENARIO_ID} --host 0.0.0.0"

if [ "${ORDERFLOW_ROLE}" = "order-api" ]; then
  # shellcheck disable=SC2086
  exec python /app/service.py ${common_args} --dependency-url "${ORDERFLOW_DEPENDENCY_URL}"
fi

# shellcheck disable=SC2086
exec python /app/service.py ${common_args}
