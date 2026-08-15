"""
Autonomous Deployment Demo
==========================

A small Flask service whose entire job is to prove that the pipeline works.

It reads build metadata that the CI pipeline bakes into the Docker image
(commit SHA, image tag, build timestamp) and displays it on the page. When you
push a change, the pipeline rebuilds the image and the values on the live page
change. That visible change is the demo.

Routes:
    GET /          Human-readable deployment manifest
    GET /health    Liveness probe used by the pipeline's verify job
    GET /api/info  Same metadata as JSON, for scripts and monitoring
"""

import os
import socket
from datetime import datetime, timezone

from flask import Flask, jsonify, render_template

app = Flask(__name__)

# Recorded once at process start so we can report container uptime.
PROCESS_STARTED_AT = datetime.now(timezone.utc)


def build_info():
    """Collect build metadata injected by the Dockerfile at image build time.

    Falls back to obvious local-development values so the app still runs
    correctly with `python src/app.py` on your own machine.
    """
    commit = os.environ.get("GIT_SHA", "local-dev")
    return {
        "app_version": os.environ.get("APP_VERSION", "0.0.0-local"),
        "commit_sha": commit,
        "commit_short": commit[:7] if commit != "local-dev" else commit,
        "image_tag": os.environ.get("IMAGE_TAG", "not-built-by-ci"),
        "built_at": os.environ.get("BUILD_TIME", "not-built-by-ci"),
        "environment": os.environ.get("APP_ENV", "development"),
        "container_host": socket.gethostname(),
        "started_at": PROCESS_STARTED_AT.isoformat(timespec="seconds"),
        "uptime_seconds": int(
            (datetime.now(timezone.utc) - PROCESS_STARTED_AT).total_seconds()
        ),
    }


def pipeline_stages():
    """The five pipeline jobs, in the order they run.

    Kept here rather than hard-coded in the template so the page and the
    workflow file describe the same process.
    """
    return [
        ("Lint", "Checks code style before anything is built."),
        ("Test", "Runs the test suite against the source."),
        ("Build", "Builds the image and pushes it to the registry."),
        ("Deploy", "Tells the host to pull and run the new image."),
        ("Verify", "Calls /health until the new version answers."),
    ]


@app.route("/")
def index():
    return render_template(
        "index.html",
        info=build_info(),
        stages=pipeline_stages(),
    )


@app.route("/health")
def health():
    """Liveness probe.

    The pipeline's verify job polls this after deploying. Returning the commit
    SHA lets the job confirm the *new* build is live, not just that something
    is answering.
    """
    info = build_info()
    return jsonify(
        status="healthy",
        commit_sha=info["commit_sha"],
        app_version=info["app_version"],
        uptime_seconds=info["uptime_seconds"],
    ), 200


@app.route("/api/info")
def api_info():
    return jsonify(build_info()), 200


if __name__ == "__main__":
    # Render (and most hosts) provide the port to bind through $PORT.
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("APP_ENV", "development") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)
