from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from study_group.crew import AGENTS, TASKS, StudyGroupCrew
from study_group.tools import (
    build_evidence_quiz,
    check_claims_against_sources,
    lookup_topic_sources,
)
from app import app as web_app


class StudyGroupWorkflowTests(unittest.TestCase):
    def test_default_workflow_writes_output_and_checks_claims(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            output_path = Path(temporary_directory) / "session.md"
            result = StudyGroupCrew().run("photosynthesis", output_path)

            self.assertTrue(output_path.is_file())
            output = output_path.read_text(encoding="utf-8")
            self.assertIn("## Agent roster", output)
            self.assertIn("Task context flow", output)
            self.assertIn("## Quiz", output)
            self.assertIn("## Fact-check results", output)
            self.assertEqual(len(result["agents"]), 4)
            self.assertTrue(
                all(
                    check["status"] == "aligned_with_source_note"
                    for check in result["fact_check"]["results"]
                )
            )

    def test_context_dependencies_capture_information_flow(self) -> None:
        task_dependencies = {task["id"]: task["depends_on"] for task in TASKS}
        self.assertEqual(task_dependencies["topic_research"], [])
        self.assertEqual(task_dependencies["quiz_making"], ["topic_research"])
        self.assertEqual(
            task_dependencies["fact_checking"],
            ["topic_research", "quiz_making", "plain_language_explanation"],
        )

    def test_agents_have_distinct_roles_goals_and_backstories(self) -> None:
        self.assertEqual(len(AGENTS), 4)
        self.assertEqual(len({agent.name for agent in AGENTS}), 4)
        for agent in AGENTS:
            self.assertTrue(agent.role)
            self.assertTrue(agent.goal)
            self.assertTrue(agent.backstory)

    def test_langchain_tools_are_called_and_return_structured_data(self) -> None:
        research_json = lookup_topic_sources.invoke({"topic": "photosynthesis"})
        research = json.loads(research_json)
        quiz = json.loads(
            build_evidence_quiz.invoke({"research_json": research_json})
        )
        self.assertEqual(len(quiz["questions"]), 3)
        self.assertEqual(research["retrieval_mode"], "bundled_reference_pack")

        claims_json = json.dumps(
            [
                {
                    "claim": "Chloroplasts",
                    "source_id": "photosynthesis-1",
                }
            ]
        )
        checked = json.loads(
            check_claims_against_sources.invoke(
                {"claims_json": claims_json, "research_json": research_json}
            )
        )
        self.assertEqual(
            checked["results"][0]["status"], "aligned_with_source_note"
        )

    @patch("study_group.tools.requests.get")
    def test_other_topics_use_wikipedia_and_surface_api_errors(
        self, get: Mock
    ) -> None:
        search_response = Mock()
        search_response.json.return_value = {
            "query": {"search": [{"pageid": 42, "title": "Ocean tide"}]}
        }
        pages_response = Mock()
        pages_response.json.return_value = {
            "query": {
                "pages": {
                    "42": {
                        "pageid": 42,
                        "title": "Ocean tide",
                        "fullurl": "https://en.wikipedia.org/wiki/Ocean_tide",
                        "extract": "Ocean tides are the rise and fall of sea levels.",
                    }
                }
            }
        }
        get.side_effect = [search_response, pages_response]

        research = json.loads(lookup_topic_sources.invoke({"topic": "ocean tides"}))
        self.assertEqual(research["retrieval_mode"], "wikipedia_api")
        self.assertIn("rise and fall", research["references"][0]["fact"])
        self.assertEqual(get.call_count, 2)

        get.side_effect = RuntimeError("service unavailable")
        with self.assertRaisesRegex(RuntimeError, "service unavailable"):
            lookup_topic_sources.invoke({"topic": "ocean tides"})


class StudyGroupWebsiteTests(unittest.TestCase):
    def setUp(self) -> None:
        web_app.config["TESTING"] = True
        self.client = web_app.test_client()

    def test_home_page_explains_team_and_shows_sample_session(self) -> None:
        response = self.client.get("/")
        page = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("MEET YOUR STUDY PARTNERS", page)
        self.assertIn("Topic Researcher", page)
        self.assertIn("Quiz Maker", page)
        self.assertIn("Fact-Checker", page)
        self.assertIn("Context links", page)
        self.assertIn("What was checked?", page)
        self.assertNotIn("Everything your assignment asks for.", page)
        self.assertIn("Download guide", page)

    def test_study_form_validates_topic_and_generates_session(self) -> None:
        empty_response = self.client.post("/study", data={"topic": " "})
        self.assertEqual(empty_response.status_code, 400)
        self.assertIn(
            b"Please enter a topic before starting",
            empty_response.data,
        )

        response = self.client.post(
            "/study", data={"topic": "photosynthesis"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Quick knowledge check", response.data)

    def test_health_check(self) -> None:
        response = self.client.get("/healthz")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"status": "ok"})

    def test_session_can_be_downloaded(self) -> None:
        self.client.get("/")
        response = self.client.get("/download")
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "attachment; filename=study_group_session.md",
            response.headers["Content-Disposition"],
        )


if __name__ == "__main__":
    unittest.main()
