# syntax=docker/dockerfile:1

# =============================================================================
# Stage 1 — builder
#
# Compiles dependencies into wheels. Build tools live only in this stage, so
# they never reach the shipped image.
# =============================================================================
FROM python:3.12-slim AS builder

WORKDIR /build

COPY src/requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip wheel --no-cache-dir --wheel-dir /build/wheels -r requirements.txt


# =============================================================================
# Stage 2 — runtime
#
# Starts from a clean base and installs only the prebuilt wheels. The result is
# roughly a third the size of a single-stage build.
# =============================================================================
FROM python:3.12-slim AS runtime

# Build metadata, supplied by the CI pipeline via --build-arg. The app reads
# these at runtime and displays them, which is how a deploy becomes visible.
ARG GIT_SHA=local-dev
ARG BUILD_TIME=unknown
ARG IMAGE_TAG=local
ARG APP_VERSION=0.0.0-local

ENV GIT_SHA=${GIT_SHA} \
    BUILD_TIME=${BUILD_TIME} \
    IMAGE_TAG=${IMAGE_TAG} \
    APP_VERSION=${APP_VERSION} \
    APP_ENV=production \
    PORT=5000 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Labels let the registry and `docker inspect` report where an image came from.
LABEL org.opencontainers.image.title="Autonomous Deployment Demo" \
      org.opencontainers.image.description="Flask service demonstrating an end-to-end CI/CD pipeline" \
      org.opencontainers.image.source="https://github.com/connorf88/autonomous-deployment-demo" \
      org.opencontainers.image.revision="${GIT_SHA}" \
      org.opencontainers.image.version="${APP_VERSION}" \
      org.opencontainers.image.licenses="MIT"

WORKDIR /app

COPY --from=builder /build/wheels /wheels
RUN pip install --no-cache-dir --no-index --find-links=/wheels /wheels/* \
    && rm -rf /wheels

COPY src/ /app/

# Run as an unprivileged user. Containers that run as root are a routine audit
# finding, and fixing it costs one line.
RUN useradd --create-home --shell /usr/sbin/nologin appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 5000

# Lets Docker and orchestrators see whether the container is actually serving,
# not merely running.
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request,os,sys; sys.exit(0 if urllib.request.urlopen(f'http://127.0.0.1:{os.environ.get(\"PORT\",5000)}/health', timeout=2).status == 200 else 1)"

# gunicorn rather than Flask's dev server: the dev server is single-threaded and
# explicitly not for production.
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 2 --threads 4 --timeout 60 --access-logfile - app:app"]
