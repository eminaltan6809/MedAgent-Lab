# Med-AgentLab

Med-AgentLab is a FastAPI-based qualitative analysis prototype for clinical interview text. The system accepts Excel, TXT, and PDF uploads on the backend, converts readable content into text, redacts common personally identifiable patterns, extracts themes with a model pool, validates themes with PubMed-assisted context, and produces Excel, Markdown, and DOCX outputs.

The current active application entry point is `app.py`. The frontend is a single-page HTML interface in `frontend/index.html`.

## Features

- FastAPI backend with upload, status, result, download, cancel, and health endpoints.
- Background analysis jobs with progress tracking and SQLite-backed job persistence.
- Ollama-based privacy preprocessing with regex fallback for Turkish ID number, phone, and email patterns.
- Model pool routing for theme extraction, validation, and report synthesis.
- PubMed ESearch/ESummary integration for literature-aware validation.
- Frontend job history, progress view, result tabs, router/privacy panel, and download buttons.
- Excel, Markdown, and DOCX result export paths.

## Project Structure

```text
.
├── app.py                 # Active FastAPI backend
├── main.py                # Earlier pipeline implementation kept for reference
├── frontend/index.html    # Browser UI
├── requirements.txt       # Python dependencies
├── create_demo_data.py    # Synthetic demo data generator
├── Knowledge-Base/        # Project notes and earlier documentation
└── tools/                 # Report/build helper scripts
```

Runtime folders such as `uploads/`, `outputs/`, logs, local database files, `.env`, and patient-like spreadsheet files are intentionally excluded from Git.

## Setup

Create and activate a Python environment, then install dependencies:

```bash
pip install -r requirements.txt
```

Create `.env` from the example file and add your provider keys:

```bash
cp .env.example .env
```

Install and start Ollama locally, then pull the configured model if needed:

```bash
ollama pull qwen3:4b
```

## Run

Start the backend:

```bash
uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

Open the interface:

```text
http://127.0.0.1:8000
```

Health check:

```text
http://127.0.0.1:8000/health
```

## Notes

This project is a graduation project prototype. It is not a clinical decision support system. Outputs should be reviewed by a domain expert before any academic or clinical use.
