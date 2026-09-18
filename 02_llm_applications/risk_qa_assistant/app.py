
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import ValidationError

from prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from schemas import RiskAnswer

# Load .env from repo root (two levels up from this file)
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL = "gpt-4o-mini"  # cheap + good for structured output


def _call_llm(question: str) -> str:
    """Raw LLM call. Returns the text content."""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_PROMPT_TEMPLATE.format(question=question)},
        ],
        temperature=0.2,  # low temp for factual consistency
        response_format={"type": "json_object"},  # forces valid JSON
    )
    return response.choices[0].message.content


def answer_question(question: str) -> RiskAnswer:
    """Public API: returns a validated RiskAnswer or raises."""
    raw = _call_llm(question)

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"LLM did not return valid JSON: {e}\nRaw: {raw}") from e

    try:
        return RiskAnswer(**data)
    except ValidationError as e:
        raise ValueError(f"LLM output failed schema validation: {e}\nRaw: {raw}") from e


def format_answer(answer: RiskAnswer) -> str:
    """Pretty-print for CLI / display."""
    lines = [
        f"Topic: {answer.topic}",
        f"Confidence: {answer.confidence}",
        "",
        "Definition:",
        f"  {answer.definition}",
        "",
        "Why it matters:",
        f"  {answer.why_it_matters}",
        "",
        "Key components:",
        *[f"  - {c}" for c in answer.key_components],
        "",
        "Financial-services example:",
        f"  {answer.financial_services_example}",
        "",
        "Risks and limitations:",
        *[f"  - {r}" for r in answer.risks_and_limitations],
        "",
        "Practical application:",
        f"  {answer.practical_application}",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        q = " ".join(sys.argv[1:])
        try:
            print(format_answer(answer_question(q)))
        except Exception as e:
            print(f"ERROR: {e}")
    else:
        # Interactive mode
        print("Financial Risk Q&A Assistant (type 'quit' to exit)\n")
        while True:
            q = input("Question: ").strip()
            if q.lower() in {"quit", "exit", "q"}:
                break
            if not q:
                continue
            try:
                print("\n" + format_answer(answer_question(q)) + "\n")
            except Exception as e:
                print(f"ERROR: {e}\n")