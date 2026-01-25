# =============================================================================
# Stage 1: Build
# =============================================================================
FROM python:3.13-alpine AS builder

WORKDIR /app

# Install uv for fast dependency installation
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Create virtual environment and install production dependencies only
RUN uv sync --frozen --no-dev

# =============================================================================
# Stage 2: Runtime
# =============================================================================
FROM python:3.13-alpine

WORKDIR /app

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY --chown=appuser:appuser . .

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set database path to persistent volume location
ENV DATABASE_PATH=/app/data/db.sqlite3

# Collect static files
RUN python manage.py collectstatic --noinput

# Create data directory for SQLite database (will be mounted as volume)
RUN mkdir -p /app/data && chown appuser:appuser /app/data

# Make entrypoint executable
RUN chmod +x docker-entrypoint.sh

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Set entrypoint and default command
ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["gunicorn", "packing_project.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2"]
