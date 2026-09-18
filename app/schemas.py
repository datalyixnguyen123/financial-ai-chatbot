
from pydantic import BaseModel
from typing import Optional


class AnalyzeRequest(BaseModel):
    message: str

class Entities(BaseModel):
    amount: Optional[float] = None
    category: Optional[str] = None
    date: Optional[str] = None
    merchant: Optional[str] = None
    description: Optional[str] = None
    payment_method: Optional[str] = None
    duration: Optional[str] = None
    target_amount: Optional[float] = None
    period: Optional[str] = None
    budget_limit: Optional[float] = None


class AnalyzeResponse(BaseModel):
    intent: str
    confidence: float
    entities: Entities
    status: str
    needs_clarification: bool
    clarification_question: Optional[str] = None