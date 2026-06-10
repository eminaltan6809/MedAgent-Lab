# Med-AgentLab Final Knowledge Base

Last updated: 2026-06-10

This file is the canonical knowledge base for future LLM-assisted work on Med-AgentLab. When another human or AI contributor needs to understand the project, this file should be read together with `README.md`, `docs/agents.md`, `docs/installation.md` and the active source code.

## Project Summary

Med-AgentLab is a graduation project prototype for qualitative analysis of clinical interview text. It accepts Excel, TXT and PDF inputs, converts readable content into text, applies local privacy preprocessing, extracts themes, validates themes with PubMed-assisted context and produces downloadable XLSX, Markdown and DOCX outputs.

The project is not a clinical decision support system. Outputs are draft academic analysis artifacts that require human researcher and supervisor review.

## Active Code

- `app.py`: active FastAPI backend, pipeline, agents, model routing, persistence and download endpoints.
- `frontend/index.html`: static browser interface served by FastAPI.
- `create_demo_data.py`: synthetic demo data generator.
- `requirements.txt`: Python dependencies.
- `.env.example`: environment variable template.

`main.py` was an older reference implementation and has been removed from the active repository.

## Repository Documentation

- `README.md`: GitHub landing page.
- `docs/TODO.md`: current work plan and future roadmap.
- `docs/agents.md`: human + AI agent guide.
- `docs/CHANGELOG.md`: project history.
- `docs/commercial.md`: commercialization model.
- `docs/SWOT.md`: competitor-aware SWOT analysis.
- `docs/installation.md`: local setup guide.
- `docs/walkthrough.md`: usage and demo walkthrough.
- `docs/idea.md`: current idea summary.
- `docs/project-text.md`: short project text.
- `docs/reports/`: graduation reports.
- `docs/slides/`: final presentation deck.
- `docs/poster/`: project poster.
- `docs/assets/graphical-abstract.svg`: graphical abstract used by README.
- `docs/knowledge-base/idea.md`: early project idea note.
- `docs/knowledge-base/pitchdeck_compressed.pdf`: early pitch deck.

## Runtime Files

The following are local runtime artifacts and should not be committed:

- `.env`
- `uploads/`
- `outputs/`
- `*.db`
- `*.sqlite`
- `*.log`
- `__pycache__/`
- patient-like spreadsheet files

## Backend Behavior

The FastAPI backend in `app.py` exposes these main endpoints:

| Endpoint | Method | Purpose |
| --- | --- | --- |
| `/` | GET | Serves `frontend/index.html` |
| `/upload` | POST | Uploads a file and starts background analysis |
| `/jobs` | GET | Lists persisted jobs |
| `/status/{job_id}` | GET | Returns progress, logs, router events and privacy metrics |
| `/results/{job_id}` | GET | Returns structured result data |
| `/download/{job_id}` | GET | Downloads XLSX output |
| `/download/report/{job_id}` | GET | Downloads Markdown report |
| `/download/report/docx/{job_id}` | GET | Generates/downloads DOCX report |
| `/cancel/{job_id}` | POST | Cancels a running job |
| `/health` | GET | Health check |

Jobs are held in memory and persisted to `med_agentlab.db` through SQLite.

## Input Handling

Supported upload extensions:

- `.xlsx`
- `.xls`
- `.txt`
- `.pdf`

Excel files are read with pandas. The preferred text column in the current implementation is `text_data`. TXT and PDF content can be split into overlapping chunks before analysis.

## Agent Workflow

### Agent A: Privacy Scrubber

Implemented as `AgentA_PrivacyScrubber`.

- Uses the configured Ollama model.
- Attempts to redact obvious personally identifiable information.
- Applies regex-based `PatternGuard` after the LLM step.
- If Ollama/model access fails, regex fallback still runs.

### Agent B: Thematic Mapper

Implemented as `AgentB_ThematicMapper`.

- Extracts qualitative/clinical themes from redacted text.
- Uses the `theme_mapping` model pool.
- Falls back to local keyword rules when the API pool fails.

### Agent C: PubMed Validator

Implemented as `AgentC_PubMedValidator`.

- Searches PubMed through NCBI ESearch/ESummary.
- Uses PubMed titles as context for validation.
- Uses the `validation` model pool.
- Falls back to a demo-safe heuristic when needed.

### Agent D: Academic Reducer

Implemented as `AgentD_AcademicReducer`.

- Synthesizes segment-level results into an academic report.
- Uses the `reduction` model pool.
- Falls back to a deterministic demo-safe report when needed.

## Model Router

The router is implemented by `call_model_pool` in `app.py`.

It detects common provider/model failures such as quota, rate limit, 429, timeout, unavailable service and invalid model conditions. When possible, it records the failure and moves to the next configured model.

Router events are persisted in job metadata and displayed in the frontend.

## Ollama Role

Ollama is intentionally assigned the lighter privacy/preprocessing role because the local model can be weaker than external hosted models. The current code can attempt to start `ollama serve` before analysis if the `ollama` command is available.

If Ollama is not available, the pipeline continues with regex-based Pattern Guard for basic PII masking.

## Outputs

The system can produce:

- XLSX analysis table.
- Markdown academic report.
- DOCX academic report.

Generated files are written under `outputs/` and ignored by Git.

## Environment Variables

Important variables:

- `GROQ_API_KEY`
- `GEMINI_API_KEY`
- `OLLAMA_API_BASE`
- `OLLAMA_MODEL`
- `GROQ_MODEL`
- `GEMINI_FAST_MODEL`
- `GEMINI_LITE_MODEL`
- `THEME_MODEL_POOL`
- `VALIDATION_MODEL_POOL`
- `REDUCTION_MODEL_POOL`
- `AGENT_C_MODEL`
- `AGENT_D_MODEL`

## Development Rules for Future LLMs

1. Do not invent features that are not visible in code or documentation.
2. Treat `app.py` as the active backend.
3. Treat `frontend/index.html` as the active frontend.
4. Keep generated outputs, database files, logs and secrets out of Git.
5. Update `README.md`, `docs/CHANGELOG.md` and this file after meaningful behavior changes.
6. Preserve the human-in-the-loop framing: the system drafts analysis, humans approve interpretation.
