from pydantic import BaseModel, Field, field_validator
from typing import Literal


class Citation(BaseModel):
    doc: str
    section: str | None = None
    page: int | None = None
    snippet: str = Field(..., min_length=20)


class RiskAnswer(BaseModel):
    topic: str
    definition: str
    why_it_matters: str
    key_components: list[str]
    financial_services_example: str
    risks_and_limitations: list[str]
    practical_application: str
    confidence: Literal["high", "medium", "low"]
    citations: list[Citation]       # ← NEW
    grounded: bool                  # ← NEW: did the model find support?

    @field_validator("key_components", "risks_and_limitations")
    @classmethod
    def no_empty_items(cls, v):
        if any(not item.strip() for item in v):
            raise ValueError("List items must not be empty")
        return v