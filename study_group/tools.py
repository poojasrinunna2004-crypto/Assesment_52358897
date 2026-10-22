"""LangChain tools used by the study-group agents."""

from __future__ import annotations

import json
import re
from typing import Any
from urllib.parse import quote

import requests
from langchain_core.tools import tool

PHOTOSYNTHESIS_REFERENCES: list[dict[str, Any]] = [
    {
        "id": "photosynthesis-1",
        "title": "OpenStax Biology 2e: Overview of Photosynthesis",
        "url": "https://openstax.org/books/biology-2e/pages/8-1-overview-of-photosynthesis",
        "fact": (
            "In plants, photosynthesis takes place in chloroplasts. "
            "Chlorophyll in these structures absorbs light energy."
        ),
        "question": "Which cell structures are the main site of photosynthesis in plants?",
        "choices": ["Chloroplasts", "Ribosomes", "Mitochondria"],
        "answer": "Chloroplasts",
    },
    {
        "id": "photosynthesis-2",
        "title": "OpenStax Biology 2e: The Light-Dependent Reactions",
        "url": "https://openstax.org/books/biology-2e/pages/8-2-the-light-dependent-reactions-of-photosynthesis",
        "fact": (
            "During photosynthesis, plants use light energy to convert water "
            "and carbon dioxide into sugars, releasing oxygen."
        ),
        "question": "Which two inputs are used to make sugars during photosynthesis?",
        "choices": [
            "Water and carbon dioxide",
            "Oxygen and nitrogen",
            "Glucose and sunlight",
        ],
        "answer": "Water and carbon dioxide",
    },
    {
        "id": "photosynthesis-3",
        "title": "OpenStax Biology 2e: Using Light Energy to Make Organic Molecules",
        "url": "https://openstax.org/books/biology-2e/pages/8-3-using-light-energy-to-make-organic-molecules",
        "fact": (
            "Photosynthesis captures light energy and stores it as chemical "
            "energy in sugar molecules."
        ),
        "question": "In what form is captured light energy stored?",
        "choices": [
            "Chemical energy in sugar molecules",
            "Sound energy in leaves",
            "Kinetic energy in roots",
        ],
        "answer": "Chemical energy in sugar molecules",
    },
]

_STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "in",
    "into", "is", "it", "of", "on", "or", "that", "the", "this", "to",
    "use", "used", "what", "which", "with",
}


def _wikipedia_results(topic: str) -> list[dict[str, str]]:
    search_response = requests.get(
        "https://en.wikipedia.org/w/api.php",
        params={
            "action": "query",
            "list": "search",
            "srsearch": topic,
            "srlimit": 3,
            "format": "json",
        },
        headers={"User-Agent": "StudyGroupCrew/1.0 (educational project)"},
        timeout=15,
    )
    search_response.raise_for_status()
    search_items = search_response.json().get("query", {}).get("search", [])
    if not search_items:
        raise ValueError(f"No Wikipedia articles found for topic: {topic}")

    page_ids = "|".join(str(item["pageid"]) for item in search_items)
    pages_response = requests.get(
        "https://en.wikipedia.org/w/api.php",
        params={
            "action": "query",
            "pageids": page_ids,
            "prop": "extracts|info",
            "exintro": 1,
            "explaintext": 1,
            "inprop": "url",
            "format": "json",
        },
        headers={"User-Agent": "StudyGroupCrew/1.0 (educational project)"},
        timeout=15,
    )
    pages_response.raise_for_status()
    pages = pages_response.json().get("query", {}).get("pages", {})

    results = []
    for page in pages.values():
        extract = re.sub(r"\s+", " ", page.get("extract", "")).strip()
        if extract:
            results.append(
                {
                    "id": f"wikipedia-{page['pageid']}",
                    "title": page["title"],
                    "url": page.get(
                        "fullurl",
                        "https://en.wikipedia.org/wiki/" + quote(page["title"].replace(" ", "_")),
                    ),
                    "fact": extract[:1200],
                }
            )
    if not results:
        raise ValueError(f"Wikipedia returned no usable extracts for topic: {topic}")
    return results


@tool
def lookup_topic_sources(topic: str) -> str:
    """Find concise source notes for a study topic and return them as JSON."""
    normalized_topic = topic.strip().casefold()
    if not normalized_topic:
        raise ValueError("Topic must not be empty.")

    if normalized_topic == "photosynthesis":
        return json.dumps(
            {
                "topic": topic.strip(),
                "retrieval_mode": "bundled_reference_pack",
                "summary": (
                    "Photosynthesis uses light energy to make energy-rich sugars "
                    "from water and carbon dioxide, with oxygen released."
                ),
                "references": PHOTOSYNTHESIS_REFERENCES,
            },
            ensure_ascii=False,
        )

    references = _wikipedia_results(topic.strip())
    return json.dumps(
        {
            "topic": topic.strip(),
            "retrieval_mode": "wikipedia_api",
            "summary": "Research notes retrieved from Wikipedia search results.",
            "references": references,
        },
        ensure_ascii=False,
    )


@tool
def build_evidence_quiz(research_json: str) -> str:
    """Build a quiz from source-backed questions in the research JSON."""
    research = json.loads(research_json)
    references = research.get("references", [])
    questions = [
        {
            "id": f"question-{index}",
            "source_id": reference["id"],
            "source_title": reference["title"],
            "question": reference.get(
                "question",
                f"Which source is the source note for: {reference['fact']}",
            ),
            "choices": reference.get(
                "choices",
                [reference["title"], "Not stated in the retrieved source", "A different source"],
            ),
            "correct_answer": reference.get("answer", reference["title"]),
            "supporting_fact": reference["fact"],
            "source_url": reference["url"],
        }
        for index, reference in enumerate(references, start=1)
    ]
    if not questions:
        raise ValueError("The research brief contains no source notes for a quiz.")
    return json.dumps({"questions": questions}, ensure_ascii=False)


@tool
def check_claims_against_sources(claims_json: str, research_json: str) -> str:
    """Check whether each claim's key terms appear in its cited research note."""
    claims = json.loads(claims_json)
    references = json.loads(research_json).get("references", [])
    by_id = {reference["id"]: reference for reference in references}
    results = []

    for item in claims:
        reference = by_id.get(item["source_id"])
        if reference is None:
            results.append(
                {
                    "claim": item["claim"],
                    "source_id": item["source_id"],
                    "status": "not_checked",
                    "reason": "The cited source is missing from the research brief.",
                }
            )
            continue

        note_terms = set(re.findall(r"[a-z0-9]+", reference["fact"].casefold()))
        claim_terms = {
            word
            for word in re.findall(r"[a-z0-9]+", item["claim"].casefold())
            if word not in _STOP_WORDS
        }
        supported = bool(claim_terms) and claim_terms.issubset(note_terms)
        results.append(
            {
                "claim": item["claim"],
                "source_id": item["source_id"],
                "source_title": reference["title"],
                "source_url": reference["url"],
                "status": "aligned_with_source_note" if supported else "needs_review",
                "reason": (
                    "All meaningful claim terms appear in the cited note."
                    if supported
                    else "The claim is not fully supported by the cited note text."
                ),
            }
        )

    return json.dumps(
        {
            "method": "keyword alignment against the cited notes; not independent fact verification",
            "results": results,
        },
        ensure_ascii=False,
    )
