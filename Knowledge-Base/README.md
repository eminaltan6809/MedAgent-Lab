# Zero-Cost Multi-Agent Qualitative Data Analysis Pipeline

A sophisticated qualitative data analysis system that processes interview transcripts or open-ended survey responses through a sequential multi-agent pipeline using free-tier LLM APIs and local models.

## 🏗️ Architecture Overview

The pipeline consists of three specialized agents working in sequence:

### Agent A: Open Coder (Cloud)
- **Model**: `groq/llama3-8b-8192` via LiteLLM
- **Task**: Extract basic semantic codes/themes from raw text
- **Special Feature**: Aggressive retry mechanism with exponential backoff for Groq's strict rate limits

### Agent B: Axial Coder (Cloud)
- **Model**: `gemini/gemini-1.5-flash` via LiteLLM
- **Task**: Synthesize and group codes into broader parent categories
- **Special Feature**: Optimized for hierarchical thematic organization

### Agent C: Cross-Validator (Local)
- **Model**: `ollama/qwen2.5:3b` via LiteLLM
- **Task**: Validate categorization accuracy against original text
- **Special Feature**: Runs locally on limited hardware (4GB VRAM), optimized for speed

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+** installed
2. **Ollama** installed and running locally for Agent C
3. **Free API keys** for Groq and Gemini

### Setup Instructions

#### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 2. Setup Local Model (Ollama)
```bash
# Install Ollama (if not already installed)
# Visit: https://ollama.ai/download

# Pull the required model
ollama pull qwen3:4b

# Start Ollama service
ollama serve
```

#### 3. Configure API Keys
```bash
# Copy the environment template
cp .env.example .env

# Edit .env with your actual API keys
# Get Groq key: https://console.groq.com/
# Get Gemini key: https://makersuite.google.com/app/apikey
```

#### 4. Prepare Input Data
Create an Excel file named `input_data.xlsx` with a column called `text_data` containing your qualitative data:

| text_data |
|-----------|
| "Interview response 1..." |
| "Survey answer 2..." |
| "Focus group comment..." |

#### 5. Run the Pipeline
```bash
python main.py
```

## 📊 Output

The pipeline generates `output_analysis.xlsx` with the following columns:

- **Original Text**: The input qualitative data
- **Open Codes**: Initial themes extracted by Agent A
- **Axial Categories**: Broader categories synthesized by Agent B
- **Local Validation**: YES/NO validation from Agent C
- **Validation Reason**: One-sentence explanation for validation

## 🔧 Technical Features

### Rate Limit Management
- **Exponential backoff** with `tenacity` library
- **Batch processing** to respect API limits
- **Configurable retry attempts** per agent
- **Automatic delays** between batches

### Error Handling
- **Graceful degradation** - continues processing if individual agents fail
- **Comprehensive logging** to both console and file
- **Structured error reporting** in output

### Performance Optimizations
- **Asynchronous processing** with `asyncio`
- **Parallel agent execution** where possible
- **Memory-efficient** batch processing
- **Local model optimization** for limited hardware

### Logging & Monitoring
- **Real-time progress updates** in terminal
- **Detailed log file** (`analysis_pipeline.log`)
- **Row-by-row tracking** of agent progress
- **Success/failure statistics**

## 📁 Project Structure

```
├── main.py                 # Main pipeline script
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── README.md              # This file
├── input_data.xlsx        # Your qualitative data (create this)
├── output_analysis.xlsx   # Generated results (after running)
└── analysis_pipeline.log  # Detailed execution log
```

## 🎯 Use Cases

- **Academic Research**: Analyze interview transcripts for thesis research
- **Market Research**: Process open-ended survey responses at scale
- **User Experience Research**: Code qualitative feedback from user studies
- **Social Science Research**: Analyze focus group discussions
- **Content Analysis**: Extract themes from textual data sources

## ⚡ Performance Tips

1. **Batch Size**: Adjust `batch_size` in `process_batch()` method (default: 5)
2. **Rate Limits**: Monitor logs for 429 errors and increase delays if needed
3. **Local Model**: Ensure Ollama has sufficient RAM for the qwen2.5:3b model
4. **Concurrent Processing**: Pipeline automatically handles async operations

## 🐛 Troubleshooting

### Common Issues

**"Missing required environment variables"**
- Ensure `.env` file exists with valid API keys
- Check that keys are correctly copied without extra spaces

**"Input file not found"**
- Create `input_data.xlsx` with `text_data` column
- Ensure file is in the same directory as `main.py`

**"Ollama connection failed"**
- Verify Ollama is running: `ollama serve`
- Check model is installed: `ollama list`
- Ensure qwen2.5:3b model is pulled

**"Rate limit hit"**
- Pipeline automatically retries with exponential backoff
- Consider reducing batch size if persistent
- Check API key quotas on provider dashboards

### Debug Mode
For detailed debugging, check the `analysis_pipeline.log` file which contains:
- Timestamped agent operations
- Error messages and stack traces
- API response details
- Performance metrics

## 🔐 API Key Setup

### Groq (Agent A)
1. Visit https://console.groq.com/
2. Sign up for free account
3. Generate API key
4. Add to `.env` as `GROQ_API_KEY`

### Gemini (Agent B)
1. Visit https://makersuite.google.com/app/apikey
2. Sign up for free account
3. Create new API key
4. Add to `.env` as `GEMINI_API_KEY`

## 📈 Scaling Considerations

- **Large Datasets**: Increase batch size and monitor memory usage
- **Multiple Files**: Modify `load_data()` method to handle multiple Excel files
- **Custom Models**: Update agent model strings in respective classes
- **Additional Agents**: Extend pipeline by adding new agent classes

## 🤝 Contributing

This is a university final project. The code is structured for:
- **Modularity**: Easy to add new agents or modify existing ones
- **Extensibility**: Simple to integrate additional LLM providers
- **Maintainability**: Clear separation of concerns and comprehensive logging

## 📄 License

This project is for educational purposes as part of a university final project.

---

**Note**: Always respect the terms of service of the API providers and use responsibly for academic research purposes.
