# Web Search Agent

An AI-powered research agent that performs deep web searches to find industry-specific success stories and AI implementation cases using Google's Gemini AI and Tavily search API.

## 🎯 Overview

This agent combines Google's Gemini 2.5 Flash with the Tavily Search API to research AI use cases by industry and technology. It runs as an interactive CLI where you can type queries and receive streamed responses.

## ✨ Features

- **Interactive CLI**: Type queries; type `quit` to exit
- **Industry-Specific Research**: `IndustrySearchContext` guides search focus
- **Personalized Instructions**: Mock `UserProfile` is fetched and used to tailor responses
- **Real-Time Web Search**: Tavily API via an async tool `deep_search`
- **Streaming Output**: Token-by-token output via `delta` events

## 🏗️ Architecture

- **Agent**: `DeepSearchAgent` using model `gemini-2.5-flash`
- **Context**: `IndustrySearchContext(industry, technology, intent)`
- **Personalization**: `UserProfile` (Pydantic) injected into `agent.context` on first turn
- **Tool**: `deep_search` uses `AsyncTavilyClient.search()`
- **Runner**: Streams events; prints deltas and selected item outputs

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Google Gemini API key (`GEMINI_API_KEY`)
- Tavily API key (`TAVILY_API_KEY`)

### Install

Using uv (recommended):
```bash
# From project root
uv sync
# Ensure these are available if not pulled transitively
uv add python-dotenv pydantic
```

Using pip:
```bash
pip install .
pip install python-dotenv pydantic
```

### Configure environment
Create a `.env` file in the project root:
```env
GEMINI_API_KEY=your_gemini_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

### Run
```bash
python web_search_agent.py
```
You will see:
```
What do you want to research today?
```
- Type your research request and press Enter.
- Type `quit` to exit.

## 📖 Usage

### Default context
The script sets a default context:
```python
context = IndustrySearchContext(industry="Telecom", technology="5G", intent="AI use cases")
```
You can change this in `web_search_agent.py` before running, or adapt it for programmatic use.

### Programmatic use (optional)
```python
import asyncio
from web_search_agent import call_agent, context

# Optionally adjust context
context.industry = "Finance"
context.technology = "Fraud Detection"
context.intent = "Success Stories"

# Provide a user_input variable globally (matches current script expectations)
user_input = "Research recent fraud detection success stories in finance"
asyncio.run(call_agent())
```

## 🔧 Configuration

- **Model**: `gemini-2.5-flash` via an OpenAI-compatible base URL: `https://generativelanguage.googleapis.com/v1beta/openai/`
- **Environment**: `GEMINI_API_KEY`, `TAVILY_API_KEY` from `.env`
- **Personalization**: A mock `fetch_user_profile()` seeds `agent.context.user_profile` on first turn

## 📊 Output

The runner emits streamed events. The script currently handles:
- `delta`: token-by-token streaming (printed as they arrive)
- `agent_updated_stream_event`: agent lifecycle updates
- `run_item_stream_event`: tool and message items

Example (abridged):
```
What do you want to research today?
> Explain AI implementation in 5G telecom
A...I... i...m...p...l...e...m...e...n...t...a...t...i...o...n...
Agent updated: DeepSearchAgent
-- Tool was called
-- Message output:
 ...
=== Run complete ===
```

## 🛠️ Development

### Project Structure
```
news_agent/
├── web_search_agent.py    # Main agent (interactive CLI)
├── pyproject.toml         # Project dependencies
├── README.md              # This file
├── .env                   # Environment variables (create this)
└── .gitignore             # Git ignore rules
```

### Dependencies

Declared in `pyproject.toml`:
- `openai-agents>=0.2.4`
- `tavily-python>=0.7.10`
- `langchain-core>=0.3.74`

Used in code (install if missing):
- `python-dotenv`
- `pydantic`

### Extend
- Add new tools with `@function_tool`
- Extend `IndustrySearchContext` for more dimensions
- Adjust `research_instructions(agent, user_input)` for different prompting strategies

## 🤝 Contributing

- Branch from main, open PRs with clear descriptions
- Include reproducible steps for any bug reports

## 📄 License

MIT (see `LICENSE` if present)

---

Note: This project requires valid API keys for both Gemini and Tavily services.
