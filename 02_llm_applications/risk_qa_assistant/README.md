
# Financial Risk Q&A Assistant

Structured question-answering assistant for financial-risk concepts.

## Architecture

Question → LLM → Structured JSON → Pydantic validation → Formatted answer

## Setup

1. From repo root: `pip install openai pydantic python-dotenv`
2. Create `.env` at repo root with `OPENAI_API_KEY=sk-...`

## Usage

```powershell
python app.py "What is counterparty risk?"