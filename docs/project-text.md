# Project Text

Med-AgentLab is a FastAPI-based graduation project prototype for qualitative analysis of clinical interview data. The application accepts Excel, TXT and PDF files, extracts readable text, applies a local privacy/preprocessing layer, maps clinical or qualitative themes, validates them with PubMed-assisted context and produces downloadable analysis outputs.

The system is organized as a hybrid human + AI workflow. AI agents accelerate repetitive analysis steps, but the final interpretation belongs to the researcher and supervisor. This design is important because clinical text can contain sensitive information and because qualitative findings require contextual human judgment.

The active backend is `app.py`. The active frontend is `frontend/index.html`. The repository also includes documentation for installation, walkthrough, agent responsibilities, commercial direction, SWOT analysis and future work.

