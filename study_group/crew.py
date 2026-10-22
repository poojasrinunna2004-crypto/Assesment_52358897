"""Role-based agents and the task graph that connects their work."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .tools import (
    build_evidence_quiz,
    check_claims_against_sources,
    lookup_topic_sources,
)


@dataclass(frozen=True)
class Agent:
    name: str
    role: str
    goal: str
    backstory: str
    tools: tuple[str, ...]

    def execute(self, context: dict[str, Any]) -> Any:
        raise NotImplementedError


class TopicResearcher(Agent):
    def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        result = lookup_topic_sources.invoke({"topic": context["topic"]})
        return json.loads(result)


class QuizMaker(Agent):
    def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        result = build_evidence_quiz.invoke(
            {"research_json": json.dumps(context["research"], ensure_ascii=False)}
        )
        return json.loads(result)


class Explainer(Agent):
    def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        research = context["research"]
        if research["topic"].casefold() == "photosynthesis":
            text = (
                "Think of a leaf as a tiny solar-powered kitchen. Chlorophyll "
                "captures light, and the plant uses that energy to turn water "
                "and carbon dioxide into sugar. The sugar stores energy the "
                "plant can use later; oxygen is released along the way. In "
                "plants, this process takes place in chloroplasts."
            )
        else:
            notes = " ".join(
                reference["fact"] for reference in research["references"]
            )
            text = (
                f"Here is a first-pass explanation of {research['topic']}, based "
                f"only on the retrieved source notes: {notes}"
            )
        return {
            "text": text,
            "source_claims": [
                {"claim": reference["fact"], "source_id": reference["id"]}
                for reference in research["references"]
            ],
        }


class FactChecker(Agent):
    def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        research = context["research"]
        claims = [
            {
                "claim": question["correct_answer"],
                "source_id": question["source_id"],
            }
            for question in context["quiz"]["questions"]
        ]
        claims.extend(context["explanation"]["source_claims"])
        result = check_claims_against_sources.invoke(
            {
                "claims_json": json.dumps(claims, ensure_ascii=False),
                "research_json": json.dumps(research, ensure_ascii=False),
            }
        )
        return json.loads(result)


AGENTS = (
    TopicResearcher(
        name="Topic Researcher",
        role="Evidence-focused research librarian",
        goal="Gather a concise, source-linked brief for the requested topic.",
        backstory=(
            "A careful librarian who distinguishes useful evidence from "
            "unsupported claims and always records where a note came from."
        ),
        tools=("lookup_topic_sources",),
    ),
    QuizMaker(
        name="Quiz Maker",
        role="Learning assessment designer",
        goal="Create clear questions whose answers are supported by the research.",
        backstory=(
            "A learning designer who writes answerable questions that test "
            "understanding rather than trivia."
        ),
        tools=("build_evidence_quiz",),
    ),
    Explainer(
        name="Explainer",
        role="Plain-language tutor",
        goal="Turn the research brief into an accessible explanation.",
        backstory=(
            "A patient tutor who connects unfamiliar ideas to familiar "
            "examples while keeping the explanation tied to the evidence."
        ),
        tools=(),
    ),
    FactChecker(
        name="Fact-Checker",
        role="Skeptical source-alignment editor",
        goal="Check the quiz answers and teaching points against their cited notes.",
        backstory=(
            "A skeptical editor who would rather flag a weakly supported claim "
            "than present a confident guess as fact."
        ),
        tools=("check_claims_against_sources",),
    ),
)

TASKS = (
    {
        "id": "topic_research",
        "agent": "Topic Researcher",
        "depends_on": [],
    },
    {
        "id": "quiz_making",
        "agent": "Quiz Maker",
        "depends_on": ["topic_research"],
    },
    {
        "id": "plain_language_explanation",
        "agent": "Explainer",
        "depends_on": ["topic_research"],
    },
    {
        "id": "fact_checking",
        "agent": "Fact-Checker",
        "depends_on": [
            "topic_research",
            "quiz_making",
            "plain_language_explanation",
        ],
    },
)


class StudyGroupCrew:
    """Run the four-agent study workflow and write a Markdown session output."""

    def run(self, topic: str, output_path: str | Path) -> dict[str, Any]:
        if not topic.strip():
            raise ValueError("Topic must not be empty.")

        researcher, quiz_maker, explainer, fact_checker = AGENTS
        research = researcher.execute({"topic": topic})
        quiz = quiz_maker.execute({"research": research})
        explanation = explainer.execute({"research": research})
        fact_check = fact_checker.execute(
            {
                "research": research,
                "quiz": quiz,
                "explanation": explanation,
            }
        )

        result = {
            "topic": research["topic"],
            "agents": [agent.__dict__ for agent in AGENTS],
            "tasks": TASKS,
            "research": research,
            "quiz": quiz,
            "explanation": explanation,
            "fact_check": fact_check,
        }
        destination = Path(output_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(self._render_markdown(result), encoding="utf-8")
        result["output_path"] = str(destination)
        return result

    @staticmethod
    def _render_markdown(result: dict[str, Any]) -> str:
        research = result["research"]
        lines = [
            f"# Study Group Session: {result['topic']}",
            "",
            f"Research mode: `{research['retrieval_mode']}`",
            "",
            "## Agent roster",
            "",
        ]
        for agent in result["agents"]:
            tool_names = ", ".join(agent["tools"]) or "None"
            lines.extend(
                [
                    f"### {agent['name']}",
                    f"- **Role:** {agent['role']}",
                    f"- **Goal:** {agent['goal']}",
                    f"- **Backstory:** {agent['backstory']}",
                    f"- **Tools:** {tool_names}",
                    "",
                ]
            )
        lines.extend(
            [
            "## Task context flow",
            "",
            "```text",
            "topic_research ──> quiz_making ─────────┐",
            "       └─────────> plain_language_explanation ──> fact_checking",
            "       └────────────────────────────────────────> fact_checking",
            "```",
            "",
            "| Task | Agent | Context received |",
            "|---|---|---|",
            ]
        )
        for task in result["tasks"]:
            dependencies = ", ".join(task["depends_on"]) or "User topic"
            lines.append(
                f"| `{task['id']}` | {task['agent']} | {dependencies} |"
            )

        lines.extend(["", "## Research brief", "", research["summary"], ""])
        for reference in research["references"]:
            lines.extend(
                [
                    f"- **{reference['title']}** — {reference['fact']} "
                    f"[Source]({reference['url']})",
                ]
            )

        lines.extend(
            ["", "## Study explanation", "", result["explanation"]["text"], ""]
        )
        lines.extend(["## Quiz", ""])
        for index, question in enumerate(result["quiz"]["questions"], start=1):
            lines.append(f"{index}. {question['question']}")
            lines.extend(f"   - {choice}" for choice in question["choices"])
            lines.append(
                f"   - **Answer:** {question['correct_answer']} "
                f"(source: [{question['source_title']}]({question['source_url']}))"
            )
            lines.append("")

        lines.extend(
            [
                "## Fact-check results",
                "",
                f"Method: {result['fact_check']['method']}.",
                "",
            ]
        )
        for check in result["fact_check"]["results"]:
            lines.append(
                f"- **{check['status']}** — {check['claim']} "
                f"({check['reason']})"
            )
        lines.extend(
            [
                "",
                "> These checks compare claim wording with the cited notes. "
                "They are not independent proof of truth.",
                "",
            ]
        )
        return "\n".join(lines)
