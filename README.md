# Study Group Crew

A small, reproducible study-group workflow built with LangChain tools. Four role-based agents research a topic, make a quiz, explain the core ideas, and check the work against its sources. The workflow records which task outputs were passed to each later task.

## Requirements

- Python 3.10 or newer
- Dependencies in `requirements.txt`

## Run

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m study_group
```

By default, the project runs a photosynthesis lesson using a small, bundled reference pack, so the sample works without an API key or network connection. It writes the completed session to `outputs/study_group_session.md`.

To research another topic, use the Wikipedia search API:

```powershell
python -m study_group --topic "ocean tides"
```

The live lookup requires network access. If the service is unavailable or returns no results, the program reports the error instead of silently substituting sample research. A different output path can be provided with `--output`.

## Agents and context flow

| Agent | Goal | Backstory | LangChain tool |
|---|---|---|---|
| Topic Researcher | Gather concise, source-linked evidence. | A careful librarian who distinguishes useful evidence from unsupported claims. | `lookup_topic_sources` |
| Quiz Maker | Turn the gathered evidence into a short, answerable quiz. | A learning designer who writes questions that test understanding, not trivia. | `build_evidence_quiz` |
| Explainer | Teach the topic in plain language using the research brief. | A patient tutor who connects new ideas to familiar examples. | Uses the research brief passed from the Topic Researcher. |
| Fact-Checker | Check quiz answers and teaching points against the cited notes. | A skeptical editor who flags claims that the available evidence cannot support. | `check_claims_against_sources` |

The workflow is sequential where it needs to be, and the information flow is explicit:

```text
topic_research ──> quiz_making ─────────┐
       └─────────> plain_language_explanation ──> fact_checking
       └────────────────────────────────────────> fact_checking
```

The same dependency links and the context each task received are included in the saved session output.

## LangChain tools

The three tools in `study_group/tools.py` are LangChain `@tool` tools. The Researcher uses a bundled photosynthesis reference pack or, for other topics, the Wikipedia API. The Quiz Maker builds questions from the Researcher's source records. The Fact-Checker checks each claim's meaningful terms against the text of its cited source note; it labels this as a source-alignment check, not independent proof of truth.

## Tests

```powershell
python -m unittest discover -s tests -v
```

## Reflection

See [REFLECTION.md](REFLECTION.md) for a short reflection on what worked, what did not, and what could be improved.
