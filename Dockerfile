# Multi-stage build for OptionAlpha Autonomous Trading Agent
# Stage 1: Build C++ and Rust engines
FROM python:3.11-slim as builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Stage 2: Final Runtime Image
FROM python:3.11-slim

LABEL maintainer="OptionAlpha Team"
LABEL description="OptionAlpha Autonomous AI Options Trading Agent"

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Environment Defaults
ENV PYTHONUNBUFFERED=1
ENV ALPACA_PAPER=true
ENV WEB_PORT=8080

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -f http://localhost:8080/api/status || exit 1

ENTRYPOINT ["python", "run_agent.py"]
