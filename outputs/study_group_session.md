# Study Group Session: photosynthesis

Research mode: `bundled_reference_pack`

## Agent roster

### Topic Researcher
- **Role:** Evidence-focused research librarian
- **Goal:** Gather a concise, source-linked brief for the requested topic.
- **Backstory:** A careful librarian who distinguishes useful evidence from unsupported claims and always records where a note came from.
- **Tools:** lookup_topic_sources

### Quiz Maker
- **Role:** Learning assessment designer
- **Goal:** Create clear questions whose answers are supported by the research.
- **Backstory:** A learning designer who writes answerable questions that test understanding rather than trivia.
- **Tools:** build_evidence_quiz

### Explainer
- **Role:** Plain-language tutor
- **Goal:** Turn the research brief into an accessible explanation.
- **Backstory:** A patient tutor who connects unfamiliar ideas to familiar examples while keeping the explanation tied to the evidence.
- **Tools:** None

### Fact-Checker
- **Role:** Skeptical source-alignment editor
- **Goal:** Check the quiz answers and teaching points against their cited notes.
- **Backstory:** A skeptical editor who would rather flag a weakly supported claim than present a confident guess as fact.
- **Tools:** check_claims_against_sources

## Task context flow

```text
topic_research ──> quiz_making ─────────┐
       └─────────> plain_language_explanation ──> fact_checking
       └────────────────────────────────────────> fact_checking
```

| Task | Agent | Context received |
|---|---|---|
| `topic_research` | Topic Researcher | User topic |
| `quiz_making` | Quiz Maker | topic_research |
| `plain_language_explanation` | Explainer | topic_research |
| `fact_checking` | Fact-Checker | topic_research, quiz_making, plain_language_explanation |

## Research brief

Photosynthesis uses light energy to make energy-rich sugars from water and carbon dioxide, with oxygen released.

- **OpenStax Biology 2e: Overview of Photosynthesis** — In plants, photosynthesis takes place in chloroplasts. Chlorophyll in these structures absorbs light energy. [Source](https://openstax.org/books/biology-2e/pages/8-1-overview-of-photosynthesis)
- **OpenStax Biology 2e: The Light-Dependent Reactions** — During photosynthesis, plants use light energy to convert water and carbon dioxide into sugars, releasing oxygen. [Source](https://openstax.org/books/biology-2e/pages/8-2-the-light-dependent-reactions-of-photosynthesis)
- **OpenStax Biology 2e: Using Light Energy to Make Organic Molecules** — Photosynthesis captures light energy and stores it as chemical energy in sugar molecules. [Source](https://openstax.org/books/biology-2e/pages/8-3-using-light-energy-to-make-organic-molecules)

## Study explanation

Think of a leaf as a tiny solar-powered kitchen. Chlorophyll captures light, and the plant uses that energy to turn water and carbon dioxide into sugar. The sugar stores energy the plant can use later; oxygen is released along the way. In plants, this process takes place in chloroplasts.

## Quiz

1. Which cell structures are the main site of photosynthesis in plants?
   - Chloroplasts
   - Ribosomes
   - Mitochondria
   - **Answer:** Chloroplasts (source: [OpenStax Biology 2e: Overview of Photosynthesis](https://openstax.org/books/biology-2e/pages/8-1-overview-of-photosynthesis))

2. Which two inputs are used to make sugars during photosynthesis?
   - Water and carbon dioxide
   - Oxygen and nitrogen
   - Glucose and sunlight
   - **Answer:** Water and carbon dioxide (source: [OpenStax Biology 2e: The Light-Dependent Reactions](https://openstax.org/books/biology-2e/pages/8-2-the-light-dependent-reactions-of-photosynthesis))

3. In what form is captured light energy stored?
   - Chemical energy in sugar molecules
   - Sound energy in leaves
   - Kinetic energy in roots
   - **Answer:** Chemical energy in sugar molecules (source: [OpenStax Biology 2e: Using Light Energy to Make Organic Molecules](https://openstax.org/books/biology-2e/pages/8-3-using-light-energy-to-make-organic-molecules))

## Fact-check results

Method: keyword alignment against the cited notes; not independent fact verification.

- **aligned_with_source_note** — Chloroplasts (All meaningful claim terms appear in the cited note.)
- **aligned_with_source_note** — Water and carbon dioxide (All meaningful claim terms appear in the cited note.)
- **aligned_with_source_note** — Chemical energy in sugar molecules (All meaningful claim terms appear in the cited note.)
- **aligned_with_source_note** — In plants, photosynthesis takes place in chloroplasts. Chlorophyll in these structures absorbs light energy. (All meaningful claim terms appear in the cited note.)
- **aligned_with_source_note** — During photosynthesis, plants use light energy to convert water and carbon dioxide into sugars, releasing oxygen. (All meaningful claim terms appear in the cited note.)
- **aligned_with_source_note** — Photosynthesis captures light energy and stores it as chemical energy in sugar molecules. (All meaningful claim terms appear in the cited note.)

> These checks compare claim wording with the cited notes. They are not independent proof of truth.
