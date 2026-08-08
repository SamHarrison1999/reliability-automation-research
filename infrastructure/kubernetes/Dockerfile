FROM python:3.12-slim

WORKDIR /app

COPY system/orderflow/service.py /app/service.py
COPY infrastructure/kubernetes/entrypoint.sh /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
