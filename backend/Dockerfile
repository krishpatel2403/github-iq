# =============================================================================
# GitHubIQ — Backend Dockerfile
# Multi-stage: build dependencies, then run.
# =============================================================================
FROM python:3.13-slim AS builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt

# =============================================================================
# Runtime stage
# =============================================================================
FROM python:3.13-slim AS runtime

WORKDIR /app

# Create a non-root user
RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin appuser

# Install runtime dependencies only (ca-certificates for HTTPS)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY app ./app
COPY alembic.ini ./alembic.ini
COPY alembic ./alembic

# Create data directory for SQLite (dev) — production should use PostgreSQL
RUN mkdir -p data && chown -R appuser:appuser /app

USER appuser

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

EXPOSE 8000

# Run migrations then start the server
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
