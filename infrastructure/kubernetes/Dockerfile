FROM python:3.12-slim@sha256:229a2c5bfa27522db7815ea81f9bed70af17ccb9de9fc7ad142b1877b5830d36

WORKDIR /app

COPY observability/opentelemetry/phase4-requirements.lock /tmp/phase4-requirements.lock
RUN python -m pip install --no-cache-dir --only-binary=:all: -r /tmp/phase4-requirements.lock \
    && rm /tmp/phase4-requirements.lock

COPY system/orderflow/service.py /app/system/orderflow/service.py
COPY system/orderflow/otel_runtime.py /app/system/orderflow/otel_runtime.py
COPY observability/opentelemetry/telemetry_sink.py /app/telemetry_sink.py
COPY infrastructure/kubernetes/entrypoint.sh /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
