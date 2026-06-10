# Walkthrough

This walkthrough describes a simple end-to-end demo flow.

## 1. Start Services

Start the backend:

```bash
uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

If Ollama is installed, the backend can attempt to start it before analysis. For a controlled demo, start it manually:

```bash
ollama serve
```

## 2. Open the Interface

Open:

```text
http://127.0.0.1:8000
```

The frontend is `frontend/index.html`, served by the FastAPI `/` endpoint.

## 3. Upload a File

Supported input formats:

- `.xlsx`
- `.xls`
- `.txt`
- `.pdf`

For Excel files, the backend expects a readable text column. In the current code path, `text_data` is the preferred column name.

## 4. Watch Analysis Progress

The status panel shows:

- Current job state.
- Progress percentage.
- Processed/total segment count.
- Analysis logs.
- Router events.
- Privacy metrics.

## 5. Read Router and Privacy Panel

Router events show which model was tried for each task, whether it succeeded, and whether fallback was used.

Privacy metrics summarize redaction tags detected in the processed text. These metrics are helper signals; they are not a formal privacy guarantee.

## 6. Review Outputs

After completion, the interface can show:

- Structured per-segment results.
- Generated report text.
- Model and fallback metadata.

## 7. Download Results

Available downloads:

- XLSX analysis output.
- Markdown report.
- DOCX academic report.

## 8. Human Review

Before using the output in a thesis, article or clinical context:

- Review every generated theme.
- Check PubMed-supported validation reasons.
- Correct incomplete or inaccurate themes.
- Confirm that no sensitive identifier remains in the final output.

