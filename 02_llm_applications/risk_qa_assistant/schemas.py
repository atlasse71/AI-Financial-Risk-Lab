from pydantic import BaseModel, Field, field_validator
from typing import Literal


class RiskAnswer(BaseModel):
    topic: str = Field(..., min_length=2, max_length=100)
    definition: str = Field(..., min_length=20)
    why_it_matters: str = Field(..., min_length=20)
    key_components: list[str] = Field(..., min_length=3)
    financial_services_example: str = Field(..., min_length=20)
    risks_and_limitations: list[str] = Field(..., min_length=2)
    practical_application: str = Field(..., min_length=20)
    confidence: Literal["high", "medium", "low"]

    @field_validator("key_components", "risks_and_limitations")
    @classmethod
    def no_empty_items(cls, v: list[str]) -> list[str]:
        if any(not item.strip() for item in v):
            raise ValueError("List items must not be empty")
        return v