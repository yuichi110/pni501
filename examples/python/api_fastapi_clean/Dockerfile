FROM python:3.12.6-slim-bookworm

WORKDIR /app
RUN groupadd -r appgroup && useradd -r -g appgroup -u 10001 appuser

COPY pyproject.toml uv.lock README.md ./
COPY src ./src

RUN pip install --no-cache-dir . && chown -R appuser:appgroup /app

USER appuser
EXPOSE 8080

CMD ["uvicorn", "order_dispatch.main:create_app", "--factory", "--host", "127.0.0.1", "--port", "8080"]
