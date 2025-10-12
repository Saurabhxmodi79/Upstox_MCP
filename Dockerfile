FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy project files
COPY pyproject.toml uv.lock ./
COPY *.py ./

# Install dependencies
RUN uv sync --frozen

# Create directory for tokens
RUN mkdir -p /app/data

# Expose port for potential web interface
EXPOSE 8080

# Set environment variables
ENV PYTHONPATH=/app
ENV UV_PROJECT_ENVIRONMENT=/app/.venv

# Default command - run the MCP server
CMD ["uv", "run", "upstox_server.py"]
