
from pydantic import BaseModel, Field
from typing import Optional
from typing import Literal, Any, Optional
from datetime import datetime

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
    model_config = {"from_attributes": True}

class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str

class ChatRequest(BaseModel):
    message: str
    conversation_history: list[ChatMessage] = []
    stream: bool = False

class ChatResponse(BaseModel):
    response: str

class StudyActionToggleRequest(BaseModel):
    completed: Optional[bool] = None

class StudyActionResponse(BaseModel):
    id: str
    title: str
    description: str
    due_date: str
    due_label: str
    completed: bool
    completed_at: Optional[str] = None

class StudyPlanResponse(BaseModel):
    id: str
    topic: str
    topic_badge: str
    target_label: str
    start_date: str
    target_date: str
    days_total: int
    days_remaining: int
    progress_percent: int
    completed_actions: int
    total_actions: int
    status_label: str
    last_source_message: str
    actions: list[StudyActionResponse]

class StudyRoadmapResponse(BaseModel):
    has_plans: bool
    total_plans: int
    total_actions: int
    total_completed_actions: int
    plans: list[StudyPlanResponse]
    empty_state_message: str
    updated_at: Optional[str] = None

class UserContextRequest(BaseModel):
    profile: Optional[dict[str, Any]] = None
    goals: Optional[dict[str, Any]] = None
    study: Optional[dict[str, Any]] = None
    time: Optional[dict[str, Any]] = None
    current: Optional[dict[str, Any]] = None

class UserContextResponse(BaseModel):
    id: int
    profile: dict[str, Any]
    goals: dict[str, Any]
    study: dict[str, Any]
    time: dict[str, Any]
    current: dict[str, Any]
    updated_at: datetime
    model_config = {"from_attributes": True}

