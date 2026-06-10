# Agents Guide

Med-AgentLab is designed as a hybrid human + AI workflow. The system does not treat AI output as final truth; it produces structured intermediate artifacts that a human researcher can inspect, revise and approve.

## Human Roles

### Researcher

The researcher prepares the dataset, checks whether the uploaded content is appropriate for analysis, starts the workflow and reviews the outputs. The researcher is responsible for deciding whether the generated themes are meaningful in the research context.

### Supervisor or Domain Expert

The supervisor/domain expert reviews the report, checks whether the interpretation is academically and clinically reasonable, and approves or rejects the final use of the generated analysis.

### Repository Maintainer

The maintainer keeps documentation, dependencies, environment setup and GitHub repository structure understandable for future users.

## AI and System Agents

### Agent A: Privacy Scrubber

- Implemented in `app.py` as `AgentA_PrivacyScrubber`.
- Uses the configured Ollama model through LiteLLM.
- Attempts to redact obvious personally identifiable information.
- Uses `PatternGuard` regex fallback for Turkish ID number, phone and email patterns.
- Does not perform clinical interpretation.

### Agent B: Thematic Mapper

- Implemented in `app.py` as `AgentB_ThematicMapper`.
- Extracts short clinical/qualitative themes from redacted text.
- Uses the `theme_mapping` model pool.
- Falls back to deterministic keyword-based theme extraction if the API pool cannot be used.

### Agent C: PubMed Validator

- Implemented in `app.py` as `AgentC_PubMedValidator`.
- Searches PubMed with ESearch/ESummary.
- Uses the `validation` model pool to judge whether extracted themes are supported, unsupported or partially supported.
- Falls back to a demo-safe PubMed heuristic when model calls fail.

### Agent D: Academic Reducer

- Implemented in `app.py` as `AgentD_AcademicReducer`.
- Synthesizes per-segment results into an academic Markdown report.
- Uses the `reduction` model pool.
- Falls back to a deterministic demo-safe report if the model pool cannot be used.

## Router Agent Behavior

The router is not a separate LLM agent. It is implemented through `call_model_pool` in `app.py`.

For each task, the router:

1. Reads the configured model pool.
2. Tries the first model.
3. Detects quota, rate limit, timeout and provider/model errors.
4. Switches to the next model when possible.
5. Records router events for the frontend panel.

## Human-in-the-Loop Rule

Generated outputs should be treated as draft analysis artifacts. The final academic interpretation belongs to the human researcher and supervisor.

## Future Agent Directions

- Add a human approval agent/view for accepting or rejecting themes.
- Add a cost-aware router policy.
- Add a model quality memory per task.
- Add a reviewer workflow for supervisor comments.

