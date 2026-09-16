import json
import os

from dotenv import load_dotenv
from pathlib import Path
from openai import OpenAI
from pydantic import BaseModel

# Load the project-root .env regardless of where the script is run from
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class RiskQuestionClassification(BaseModel):
    category: str
    question_type: str
    requires_documents: bool
    requires_quantitative_analysis: bool
    requires_human_review: bool
    risk_level: str
    explanation: str


SYSTEM_PROMPT = """
You are a senior financial-services risk analyst.

Classify the user's question into a relevant financial-risk category.

Possible categories include:
- Credit Risk
- Credit Underwriting
- Portfolio Management
- CECL / Loss Forecasting
- CCAR / Stress Testing
- Model Risk Management
- Fraud Risk
- Counterparty Risk
- Liquidity Risk
- Market Risk
- Operational Risk
- Regulatory Compliance
- AI Governance
- Other

Determine:
1. The question type.
2. Whether supporting documents are likely required.
3. Whether quantitative analysis is required.
4. Whether human review is required.
5. The risk level: low, medium, or high.

Return only a structured response matching the required schema.
"""


def classify_question(question: str) -> RiskQuestionClassification:
    response = client.responses.parse(
        model="gpt-4.1-mini",
        input=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": question,
            },
        ],
        text_format=RiskQuestionClassification,
    )

    return response.output_parsed


def main():
    question = input("Enter a financial-risk question: ").strip()

    if not question:
        print("Please enter a question.")
        return

    result = classify_question(question)

    print("\nClassification:")
    print(json.dumps(result.model_dump(), indent=2))


if __name__ == "__main__":
    main()