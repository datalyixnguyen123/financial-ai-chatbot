
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.db import SessionLocal
from app.schemas import (TransactionCreate, TransactionResponse, AnalyzeRequest, AnalyzeResponse, EntityExtractionResponse,)
from app.services.transaction_service import (
    create_transaction,
    get_transaction,
    get_transactions,
    update_transaction,
    delete_transaction,
)

from app.services.transaction_integration_service import (
    save_normalized_transaction,
)
from app.services.financial_integration_service import (
    get_current_balance,
    get_expense_summary,
)
from app.services.context_builder import build_context
from app.services.llm_service import generate_response
from app.schemas import ChatRequest, ChatResponse

from app.services.normalization_service import normalize_amount
from app.services.validation_service import (
    validate_ai_output,
)
from app.services.ai_service import (analyze_message, extract_entities,)
from app.services.decision_service import decide

app = FastAPI(title="Vietnamese AI Financial Assistant", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
    return JSONResponse(
        status_code=400,
        content={
            "error": {
                "code": "INVALID_REQUEST",
                "message": "Message cannot be empty"
            }
        }
    )

@app.get("/")
def root():
    return {
        "message": "Financial AI API is running"
    }

@app.post("/api/ai/extract-entities", response_model=EntityExtractionResponse, )
def extract_entities_endpoint(request: AnalyzeRequest):
    entities = extract_entities(request.message)
    return {
        "text": request.message,
        "entities": entities,
    }

@app.post("/api/ai/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest):
    message = request.message.strip()
    if not message:
        return JSONResponse(
            status_code=400,
            content={
                "error": {
                    "code": "INVALID_REQUEST",
                    "message": "Message cannot be empty"
                }
            }
        )

    # Temporary AI output for integration testing
    ai_output = analyze_message(message)
    intent = ai_output["intent"]
    confidence = ai_output["confidence"]
    entities = ai_output["entities"]
    raw_entities = ai_output.get("raw_entities", [])

    # Validate AI output before any database operation
    normalized_amount = normalize_amount(entities["amount"])
    validation = validate_ai_output(
    intent=intent,
    confidence=confidence,
    amount=normalized_amount,
    )
    raw_amount = next(
        (entity["text"]
            for entity in raw_entities
            if entity.get("type") == "AMOUNT"
        ),
        None,
    )

    # Decision layer: validation is a safety/schema gate;
    # decision_service determines accept / clarification / unknown.
    if not validation["valid"]:
        return {
            "intent": "unknown",
            "confidence": confidence,
            "entities": {
                "amount": None,
                "category": None,
                "date": None,
                "merchant": None,
                "description": message,
                "payment_method": None,
                "duration": None,
                "target_amount": None,
                "period": None,
                "budget_limit": None,
            },
            "status": "rejected",
            "needs_clarification": True,
            "clarification_question": (
                "Mình chưa hiểu rõ thông tin bạn vừa nhập. "
                "Bạn nói rõ hơn giúp mình nhé?"
            ),
            "financial_result": None,
        }

    decision = decide(
        message=message,
        intent=intent,
        confidence=confidence,
        entities=entities,
        raw_amount=raw_amount,
    )

    if decision["decision"] == "clarification":
        return {
            "intent": intent,
            "confidence": confidence,
            "entities": entities,
            "status": "clarification",
            "needs_clarification": True,
            "clarification_question": decision["clarification_question"],
            "financial_result": None,
        }

    if decision["decision"] == "unknown":
        return {
            "intent": "unknown",
            "confidence": confidence,
            "entities": {
                "amount": None,
                "category": None,
                "date": None,
                "merchant": None,
                "description": message,
                "payment_method": None,
                "duration": None,
                "target_amount": None,
                "period": None,
                "budget_limit": None,
            },
            "status": "unknown",
            "needs_clarification": True,
            "clarification_question": decision["clarification_question"],
            "financial_result": None,
        }

    status = "accepted"
    financial_result = None
    db = SessionLocal()
    try:
        if intent == "add_expense":
            save_normalized_transaction(
                db=db,
                transaction_type="expense",
                amount=entities["amount"],
                category=entities["category"],
                date_value=entities["date"],
                merchant=entities["merchant"],
                description=entities["description"],
                payment_method=entities["payment_method"],
                period=entities["period"],
            )
        elif intent == "add_income":
            save_normalized_transaction(
                db=db,
                transaction_type="income",
                amount=entities["amount"],
                category=entities["category"],
                date_value=entities["date"],
                merchant=entities["merchant"],
                description=entities["description"],
                payment_method=entities["payment_method"],
                period=entities["period"],
            )
        elif intent == "query_balance":
            financial_result = get_current_balance(db)
        elif intent == "query_expense":
            financial_result = get_expense_summary(db)

    finally:
        db.close()

    return {
        "intent": intent,
        "confidence": confidence,
        "entities": {
            "amount": entities["amount"],
            "category": entities["category"],
            "date": entities["date"],
            "merchant": entities["merchant"],
            "description": message,
            "payment_method": entities["payment_method"],
            "duration": entities["duration"],
            "target_amount": entities["target_amount"],
            "period": entities["period"],
            "budget_limit": entities["budget_limit"],
        },
        "status": status,
        "needs_clarification": False,
        "clarification_question": None,
        "financial_result": financial_result,
    }

@app.post("/api/transactions",response_model=TransactionResponse,)
def create_transaction_api(request: TransactionCreate):
    db = SessionLocal()
    try:
        transaction = create_transaction(
            db=db,
            transaction_type=request.transaction_type,
            amount=request.amount,
            category=request.category,
            date=request.date,
            merchant=request.merchant,
            description=request.description,
            payment_method=request.payment_method,
        )
        return transaction
    finally:
        db.close()


@app.get("/api/transactions/{transaction_id}", response_model=TransactionResponse,)
def get_transaction_api(transaction_id: int):
    db = SessionLocal()
    try:
        transaction = get_transaction(
            db=db,
            transaction_id=transaction_id,
        )

        if transaction is None:
            return JSONResponse(
                status_code=404,
                content={
                    "error": {
                        "code": "TRANSACTION_NOT_FOUND",
                        "message": "Transaction not found",
                    }
                },
            )
        return transaction

    finally:
        db.close()

@app.get("/api/transactions", response_model=list[TransactionResponse], )
def get_transactions_api():
    db = SessionLocal()
    try:
        return get_transactions(db)
    finally:
        db.close()


@app.put("/api/transactions/{transaction_id}", response_model=TransactionResponse,)
def update_transaction_api(
    transaction_id: int,
    request: TransactionCreate,
):
    db = SessionLocal()
    try:
        transaction = update_transaction(
            db=db,
            transaction_id=transaction_id,
            transaction_type=request.transaction_type,
            amount=request.amount,
            category=request.category,
            date=request.date,
            merchant=request.merchant,
            description=request.description,
            payment_method=request.payment_method,
        )
        if transaction is None:
            return JSONResponse(
                status_code=404,
                content={
                    "error": {
                        "code": "TRANSACTION_NOT_FOUND",
                        "message": "Transaction not found",
                    }
                },
            )
        return transaction

    finally:
        db.close()

@app.delete("/api/transactions/{transaction_id}")
def delete_transaction_api(transaction_id: int):
    db = SessionLocal()
    try:
        deleted = delete_transaction(
            db=db,
            transaction_id=transaction_id,
        )
        if not deleted:
            return JSONResponse(
                status_code=404,
                content={
                    "error": {
                        "code": "TRANSACTION_NOT_FOUND",
                        "message": "Transaction not found",
                    }
                },
            )

        return {
            "message": "Transaction deleted successfully"
        }
    finally:
        db.close()

@app.get("/api/financial/balance")
def get_balance():
    db = SessionLocal()
    try:
        return get_current_balance(db)
    finally:
        db.close()


@app.post("/api/ai/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    db = SessionLocal()
    try:
        financial_result = get_current_balance(db)
        conversation_history = [
            message.model_dump()
            for message in request.conversation_history
        ]
        context = build_context(
            conversation_history=conversation_history,
            financial_result=financial_result,
        )
        system_instruction = """
    Bạn là trợ lý tài chính cá nhân của người dùng. Hãy trả lời bằng tiếng Việt, tự nhiên, gần gũi và giống một cuộc trò chuyện đời thường.
    Quy tắc:
    1.Xưng hô "mình" và "bạn".
    2.Không phán xét tình hình tài chính.
    3.Financial data là số liệu chính thức từ hệ thống.
    4.Không tự thay đổi hoặc bịa số liệu.
    5.Không tự tạo giao dịch.
    6.Sử dụng conversation history để hiểu câu hỏi tiếp theo.
    7.Không hỏi lại thông tin đã có trong context.
    8.Nếu thiếu thông tin quan trọng, hãy hỏi lại.
    9.Không tự tạo số liệu tài chính hoặc numerical recommendation.
    10.Financial Engine quyết định số liệu.
    11.Bạn chỉ chịu trách nhiệm giải thích và diễn đạt.
    12.Trả lời tự nhiên, ngắn gọn và dễ hiểu.
    13.Có thể dùng "nha", "nhé" và emoji một cách tiết chế.
    """
        response = generate_response(
            user_message=request.message,
            system_instruction=system_instruction,
            context=context,
        )
        return ChatResponse(
            response=response,
        )
    finally:
        db.close()
