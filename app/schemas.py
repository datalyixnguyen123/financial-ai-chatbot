
from pydantic import BaseModel, Field
from typing import Optional
from typing import Literal

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

class EntityExtractionItem(BaseModel):
    type: str
    text: str
    start: int
    end: int

class EntityExtractionResponse(BaseModel):
    text: str
    entities: list[EntityExtractionItem]


class FinancialResult(BaseModel):
    total_income: Optional[float] = None
    total_expense: Optional[float] = None
    balance: Optional[float] = None

class AnalyzeResponse(BaseModel):
    intent: str
    confidence: float
    entities: Entities
    status: str
    needs_clarification: bool
    clarification_question: Optional[str] = None
    financial_result: Optional[FinancialResult] = None


class TransactionCreate(BaseModel):
    transaction_type: Literal["income", "expense"]
    amount: float = Field(gt=0)
    category: Optional[str] = None
    date: Optional[str] = None
    merchant: Optional[str] = None
    description: Optional[str] = None
    payment_method: Optional[str] = None


class TransactionResponse(BaseModel):
    id: int
    transaction_type: str
    amount: float
    category: Optional[str] = None
    date: Optional[str] = None
    merchant: Optional[str] = None
    description: Optional[str] = None
    payment_method: Optional[str] = None

    model_config = {
        "from_attributes": True
    }

class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str

class ChatRequest(BaseModel):
    message: str
    conversation_history: list[ChatMessage] = []

class ChatResponse(BaseModel):
    response: str
