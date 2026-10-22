"""Web interface for the Study Group Crew."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import requests
from flask import Flask, abort, render_template, request, send_file

from study_group.crew import AGENTS, TASKS, StudyGroupCrew

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_PATH = BASE_DIR / "outputs" / "study_group_session.md"
DEFAULT_TOPIC = "photosynthesis"

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 1024


def make_session(topic: str) -> dict[str, Any]:
    return StudyGroupCrew().run(topic, OUTPUT_PATH)


@app.get("/")
def home() -> str:
    try:
        session = make_session(DEFAULT_TOPIC)
        error = None
    except (ValueError, OSError, KeyError, TypeError, requests.RequestException) as exc:
        session = None
        error = f"We couldn't prepare the sample session: {exc}"

    return render_template(
        "index.html",
        session=session,
        error=error,
        agents=AGENTS,
        tasks=TASKS,
        topic=DEFAULT_TOPIC,
    )


@app.post("/study")
def study() -> tuple[str, int] | str:
    topic = request.form.get("topic", "").strip()
    if not topic:
        return render_template(
            "index.html",
            session=None,
            error="Please enter a topic before starting your study session.",
            agents=AGENTS,
            tasks=TASKS,
            topic="",
        ), 400
    if len(topic) > 120:
        return render_template(
            "index.html",
            session=None,
            error="Please keep your topic under 120 characters.",
            agents=AGENTS,
            tasks=TASKS,
            topic=topic[:120],
        ), 400

    try:
        session = make_session(topic)
        error = None
        status = 200
    except (ValueError, OSError, KeyError, TypeError, requests.RequestException) as exc:
        session = None
        error = f"We couldn't create this study session: {exc}"
        status = 502

    return render_template(
        "index.html",
        session=session,
        error=error,
        agents=AGENTS,
        tasks=TASKS,
        topic=topic,
    ), status


@app.get("/healthz")
def healthz() -> tuple[dict[str, str], int]:
    return {"status": "ok"}, 200


@app.get("/download")
def download() -> Any:
    if not OUTPUT_PATH.is_file():
        abort(404)
    return send_file(
        OUTPUT_PATH,
        as_attachment=True,
        download_name="study_group_session.md",
        mimetype="text/markdown",
    )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "5000")),
        debug=False,
    )
