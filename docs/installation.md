# Installation Guide

This guide explains how to run Med-AgentLab locally.

## Requirements

- Windows, Linux or macOS.
- Python 3.10 or newer is recommended.
- Ollama installed locally if Agent A should use the local privacy model.
- API keys for external model providers if full model-pool analysis is desired.

## 1. Clone the Repository

```bash
git clone https://github.com/eminaltan6809/MedAgent-Lab.git
cd MedAgent-Lab
```

## 2. Create a Virtual Environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

Linux/macOS:

```bash
python -m venv .venv
source .venv/bin/activate
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## 4. Configure Environment Variables

Copy the example environment file:

```powershell
copy .env.example .env
```

On Linux/macOS:

```bash
cp .env.example .env
```

Then edit `.env` and add provider keys where available.

```text
GROQ_API_KEY=
GEMINI_API_KEY=
OLLAMA_API_BASE=http://127.0.0.1:11434
OLLAMA_MODEL=ollama/qwen3:4b
```

## 5. Prepare Ollama

Install Ollama from its official distribution channel, then pull the configured model:

```bash
ollama pull qwen3:4b
```

The backend attempts to start `ollama serve` before analysis if Ollama is installed but not already running. If the model is missing, the application continues with regex-based Pattern Guard fallback.

## 6. Start the Application

```bash
uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

Open:

```text
http://127.0.0.1:8000
```

Health check:

```text
http://127.0.0.1:8000/health
```

## 7. Runtime Files

The following files/folders are generated locally and should not be committed:

- `.env`
- `uploads/`
- `outputs/`
- `med_agentlab.db`
- `analysis_pipeline.log`
- `__pycache__/`

## Troubleshooting

### Ollama is not detected

Install Ollama and ensure the `ollama` command is available in the terminal. Then run:

```bash
ollama serve
```

### Model is missing

Run:

```bash
ollama pull qwen3:4b
```

### External API model fails

Check `.env` keys and model names. The application can switch to fallback models for quota, timeout and provider errors, but all providers can still fail if no valid key/model is configured.

