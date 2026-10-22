"""Command-line entry point for the study-group crew."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import requests

from .crew import StudyGroupCrew


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run a four-agent, source-linked study-group session."
    )
    parser.add_argument(
        "--topic",
        default="photosynthesis",
        help="Study topic (default: photosynthesis)",
    )
    parser.add_argument(
        "--output",
        default="outputs/study_group_session.md",
        help="Markdown output path (default: outputs/study_group_session.md)",
    )
    args = parser.parse_args()

    try:
        result = StudyGroupCrew().run(args.topic, Path(args.output))
    except (ValueError, OSError, KeyError, TypeError, requests.RequestException) as exc:
        print(f"Study session failed: {exc}", file=sys.stderr)
        return 1

    print(f"Study session saved to {result['output_path']}")
    print(f"Topic: {result['topic']}")
    print(f"Fact-check claims: {len(result['fact_check']['results'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
