# Study Group Crew

A friendly blue-and-pink website for a four-agent study team. It researches a topic, makes a quiz, explains the key ideas, and checks claims against cited notes. The site makes each agent's role and the flow of information easy to see.

## Run the website locally

Requires Python 3.10 or newer.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000`. The page starts with a photosynthesis sample from a bundled reference pack, so it needs no API key or network access. Enter another topic to look it up online using Wikipedia. Each run saves a Markdown study guide to `outputs/study_group_session.md`.

The command-line version is available too:

```powershell
python -m study_group
python -m study_group --topic "ocean tides"
```

## Assignment requirements

- **Four agents:** Topic Researcher, Quiz Maker, Explainer, and Fact-Checker each have a meaningful role, goal, and backstory.
- **LangChain tools:** Three `@tool` tools handle research, evidence-based quiz construction, and source-note alignment checks.
- **Task context:** The task graph shows the research brief passed to the Quiz Maker and Explainer, and the results passed to the Fact-Checker.
- **Saved output:** The completed session is written to `outputs/study_group_session.md`.
- **Reflection:** See [REFLECTION.md](REFLECTION.md).

The workflow is repeatable and tool-using, but is not an LLM-driven autonomous crew. Fact-checking compares claim wording with the cited notes; it does not independently prove claims.

## Tests

```powershell
python -m unittest discover -s tests -v
```

## Deploy to Render

The repository includes a Render Blueprint in `render.yaml`. In the Render dashboard, choose **New + → Blueprint**, connect `poojasrinunna2004-crypto/Assesment_52358897`, and deploy. The Blueprint installs requirements, runs the Flask site with Gunicorn, and checks `/healthz`. The default example works without API keys. Other topics use Wikipedia and need outbound network access.
