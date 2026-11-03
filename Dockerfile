# Multi-stage production container for Ojas Ops (Django-Bolt engine)
FROM python:3.14-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./
COPY packages/ojas-ops/pyproject.toml packages/ojas-ops/

RUN pip install --no-cache-dir uv && \
    uv sync --frozen --no-dev

FROM python:3.14-slim AS runner

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY packages/ojas-ops /app/packages/ojas-ops
COPY apps/sandbox /app/apps/sandbox

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app/packages/ojas-ops/src:/app/apps/sandbox" \
    PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["python", "apps/sandbox/manage.py", "runbolt", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

