# TODO

This file tracks the current and future repository-level work needed to keep Med-AgentLab usable, reviewable and understandable for future human and AI contributors.

## Completed

- Active backend consolidated around `app.py`.
- Static frontend served from `frontend/index.html`.
- Excel, TXT and PDF upload paths implemented.
- Background jobs and SQLite job persistence implemented.
- Ollama-based privacy preprocessing and regex fallback implemented.
- Quota-aware model pools implemented for theme mapping, validation and report synthesis.
- PubMed-assisted validation implemented.
- XLSX, Markdown and DOCX export paths implemented.
- Router and privacy metadata added to frontend status view.
- Graduation reports and final presentation moved under `docs/`.
- Repository documentation consolidated under `docs/`.
- Old `Knowledge-Base/` directory removed; knowledge base files moved to `docs/knowledge-base/`.
- Unlisted YouTube demo video link added to `README.md`.
- Project poster added under `docs/poster/`.

## Immediate Tasks

- Verify the README links after every document move.
- Keep `.env`, database, logs, uploads and generated outputs out of Git.
- Record future feature changes in `docs/CHANGELOG.md`.
- Keep `docs/knowledge-base/final-knowledge-base.md` synchronized with the final code behavior.

## Short-Term Engineering Tasks

- Add automated smoke tests for `/health`, `/upload`, `/status/{job_id}` and download endpoints.
- Add clearer frontend error messages for missing API keys and missing Ollama model.
- Add sample synthetic TXT/PDF inputs that do not contain patient data.
- Add a small CLI or script for a local demo health check.
- Improve report formatting for DOCX downloads.

## Academic Product Tasks

- Add screenshots of the running application to `docs/assets/`.
- Keep final report and final presentation versions under `docs/`.

## Human Review Tasks

- Validate example outputs with a domain expert.
- Review privacy masking limits before using any sensitive real-world data.
- Document known failure modes and human review responsibilities.

## Future Work: Multi-User Productization

- Add user accounts and role-based access.
- Separate researcher, reviewer and administrator workflows.
- Add project/workspace-level analysis history.
- Add exportable audit logs for institutional review.

## Future Work: Stronger Privacy and Compliance

- Add configurable PII patterns for Turkish and international datasets.
- Add a privacy evaluation benchmark with synthetic cases.
- Add manual redaction review before external API calls.
- Add deployment guidance for KVKK/GDPR-sensitive environments.

## Future Work: Model and Agent Improvements

- Add model performance tracking per task.
- Add cost and token accounting for each provider.
- Add smarter router policies based on quota, latency and task quality.
- Add stronger local model support for privacy-sensitive deployments.

## Future Work: Research Workflow Improvements

- Add codebook editing and human approval screens.
- Add inter-coder agreement support for qualitative research.
- Add versioned theme trees.
- Add richer PubMed evidence summaries.

## Future Work: Deployment Improvements

- Add Docker support.
- Add production deployment guide.
- Add reverse proxy and HTTPS notes.
- Add backup/restore instructions for analysis history.
