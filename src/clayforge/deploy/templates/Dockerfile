# ClayForge — Production Dockerfile (recommended)
# Clean, slim, secure defaults. Works great on Railway, Fly.io, Docker, ECS, etc.
#
# Build & run:
#   docker build -t myapp .
#   docker run -p 8000:8000 -e XAI_API_KEY=... myapp
#
# For platforms that provide $PORT (Railway, Fly, Render...):
#   CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "$PORT"]
# Most platforms accept the fixed 8000 form below and remap automatically.

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Only the absolute minimum system packages. Add more only if your
# dependencies truly require them (e.g. for some scientific libs).
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# Layer caching: install deps first
COPY requirements.txt .

# PRODUCTION TIP:
# Use the exact extras your app needs. Most real apps want:
#   RUN pip install --no-cache-dir "clayforge[viz,grok]"
# Or pin versions in requirements.txt / pyproject.toml.
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# App code last (keeps rebuilds fast when only code changes)
COPY . .

# Run as non-root for better security posture
RUN useradd --create-home appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Standard production entrypoint.
# If you use `clayforge run` in dev, switch to direct uvicorn here.
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
