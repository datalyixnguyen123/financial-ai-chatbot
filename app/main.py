
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from dotenv import load_dotenv
load_dotenv()

from app.db import SessionLocal
from app.schemas import (
    TransactionCreate,
    TransactionResponse,
    AnalyzeRequest,
    AnalyzeResponse,
    EntityExtractionResponse,
    UserContextRequest,
    UserContextResponse,
    StudyRoadmapResponse,
    StudyActionToggleRequest,
    StudyPlanResponse,
)

from app.services.transaction_service import (
    create_transaction,
    get_transaction,
    get_transactions,
    update_transaction,
    delete_transaction,
    get_total_expense,
)

from app.services.transaction_integration_service import (
    save_normalized_transaction,
    update_latest_transaction_amount,
)
from app.services.financial_integration_service import (
    get_current_balance,
    get_expense_summary,
    get_expense_by_category,
    get_monthly_financial_summary,
)

from app.services.context_builder import build_context
from app.services.context_service import (
    get_or_create_context,
    update_context,
)

from app.services.llm_service import generate_response, generate_chat_response, generate_chat_response_stream
from app.schemas import ChatRequest, ChatResponse, UserContextRequest, UserContextResponse

from app.services.normalization_service import (normalize_amount, format_vnd,)
from app.services.validation_service import (validate_ai_output,)
from app.services.ai_service import (analyze_message, extract_entities,)
from app.services.decision_service import decide

from app.services.context_resolver import resolve_context, resolve_follow_up

from app.services.conversational_context import (
    detect_conversational_context,
)
from app.services.study_plan_service import (
    build_study_plan_context,
    get_study_roadmap,
    process_study_goal_message,
    toggle_study_action,
)

app = FastAPI(title="Vietnamese AI Financial Assistant", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    return JSONResponse(
        status_code=400,
        content={
            "error": {
                "code": "INVALID_REQUEST",
                "message": "Invalid message request",
                "detail":errors
            }
        }
    )

@app.get("/")
def root():
    return {
        "message": "Financial AI API is running"
    }

@app.post("/api/ai/extract-entities", response_model = EntityExtractionResponse,)
def extract_entities_endpoint(request: AnalyzeRequest):
    entities = extract_entities(request.message)
    return {
        "text": request.message,
        "entities": entities,
    }

@app.post("/api/ai/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest):
    print("[ANALYZE] RAW MESSAGE:", repr(request.message), flush=True)
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

    ai_output = analyze_message(message)
    intent = ai_output["intent"]
    confidence = ai_output["confidence"]
    entities = ai_output["entities"]
    raw_entities = ai_output.get("raw_entities", [])

    # Validate AI output before any database operation
    normalized_amount = normalize_amount(entities["amount"])
    validation = validate_ai_output(
    intent = intent,
    confidence = confidence,
    amount = normalized_amount,
    )
    raw_amount = next((entity["text"]
            for entity in raw_entities
            if entity.get("type") == "AMOUNT"
        ),
        None,
    )

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
        message = message,
        intent = intent,
        confidence = confidence,
        entities = entities,
        raw_amount = raw_amount,
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

    if decision["decision"] in ["unknown", "general_conversation"]:
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
            "clarification_question": decision.get("clarification_question") or "Mình chưa đủ chắc chắn về yêu cầu này. Bạn có thể nói rõ hơn giúp mình nhé?",
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

@app.get("/api/financial/monthly-summary")
def get_monthly_summary(month: str | None = None):
    db = SessionLocal()
    try:
        return get_monthly_financial_summary(db, month=month)
    finally:
        db.close()


@app.get("/api/context", response_model = UserContextResponse,)
def get_user_context():
    db = SessionLocal()
    try:
        return get_or_create_context(db)
    finally:
        db.close()


@app.put("/api/context", response_model = UserContextResponse,)
def update_user_context(request: UserContextRequest):
    db = SessionLocal()
    try:
        return update_context(
            db,
            profile = request.profile,
            goals = request.goals,
            study = request.study,
            time = request.time,
            current = request.current,
        )
    finally:
        db.close()


@app.get("/api/study-roadmap", response_model = StudyRoadmapResponse,)
def get_study_roadmap_api():
    return get_study_roadmap()


@app.post("/api/study-roadmap/{plan_id}/actions/{action_id}", response_model = StudyPlanResponse,)
def toggle_study_action_api(
    plan_id: str,
    action_id: str,
    request: StudyActionToggleRequest,
):
    updated_plan = toggle_study_action(
        plan_id=plan_id,
        action_id=action_id,
        completed=request.completed,
    )
    if updated_plan is None:
        return JSONResponse(
            status_code=404,
            content={
                "error": {
                    "code": "STUDY_ACTION_NOT_FOUND",
                    "message": "Study plan action not found",
                }
            },
        )
    return updated_plan


# Helper generator for formatting SSE
def _sse_generator(generator):
    for chunk in generator:
        if chunk:
            import json
            yield f"data: {json.dumps({'response': chunk}, ensure_ascii=False)}\n\n"
    yield "data: [DONE]\n\n"

@app.post("/api/ai/chat")
def chat(request: ChatRequest):
    db = SessionLocal()
    print("[CHAT] RAW MESSAGE:", repr(request.message), flush=True)
    print("[CHAT] RAW MESSAGE HEX:", request.message.encode("utf-8").hex(), flush=True)

    try:
        general_system_prompt = """
Bạn là một trợ lý AI thông minh và thân thiện, chuyên về tài chính cá nhân
nhưng cũng có thể trò chuyện tự nhiên về mọi chủ đề.
TÍNH CÁCH:
- Xưng hô "mình" và "bạn", thân thiện như một người bạn.
- Trả lời tự nhiên, vui vẻ, gần gũi.
- Có thể trả lời dài nhiều câu khi cần, không nhất thiết phải ngắn gọn.
- Thể hiện sự quan tâm, đồng cảm khi bạn chia sẻ.
- Có thể đùa nhẹ nhàng, dùng emoji phù hợp.
KHẢ NĂNG:
- Trò chuyện tự nhiên về cuộc sống, học tập, công việc, sức khỏe, v.v.
- Tư vấn tài chính cá nhân: tiết kiệm, đầu tư, quản lý chi tiêu.
- Giúp lập kế hoạch tài chính, ngân sách.
- Trả lời câu hỏi học thuật về tài chính, kinh tế.
- Ghi nhận và theo dõi giao dịch thu chi.
QUY TẮC CHUNG:
1. Luôn trả lời bằng tiếng Việt.
2. Không phán xét tình hình tài chính của người dùng.
3. Khi không biết, hãy thành thật nói là mình không chắc.
4. Trả lời phù hợp với ngữ cảnh cuộc trò chuyện.
"""

        # ============================================================
        # CONVERSATIONAL CONTEXT
        # ============================================================

        conversational_result = detect_conversational_context(request.message,)

        print(f"[CHAT] CONVERSATIONAL CONTEXT: {conversational_result}", flush=True,)

        conversation_history = [
            message.model_dump()
            for message in request.conversation_history
        ]
        study_plan_update = process_study_goal_message(request.message)
        study_context = build_study_plan_context(
            request.message,
            updated_plan=study_plan_update,
        )

        if not conversational_result["should_route_to_financial_nlu"]:
            if conversational_result.get("should_route_to_llm"):
                if request.stream:
                    generator = generate_chat_response_stream(
                        user_message=request.message,
                        system_instruction=general_system_prompt,
                        conversation_history=conversation_history,
                        context=study_context or None,
                    )
                    return StreamingResponse(_sse_generator(generator), media_type="text/event-stream")
                else:
                    response = generate_chat_response(
                        user_message=request.message,
                        system_instruction=general_system_prompt,
                        conversation_history=conversation_history,
                        context=study_context or None,
                    )
                    return ChatResponse(response=response)

            # Edge case: no NLU and no LLM (empty message)
            if request.stream:
                return StreamingResponse(_sse_generator(["Mình hiểu rồi. Bạn cứ chia sẻ thêm nhé."]), media_type="text/event-stream")
            return ChatResponse(
                response="Mình hiểu rồi. Bạn cứ chia sẻ thêm nhé.",
            )

        # ============================================================
        # NLU
        # ============================================================
        print("[CHAT] 1 analyze_message START", flush=True)

        ai_result = analyze_message(request.message)

        print("[CHAT] 2 analyze_message DONE", flush=True)

        intent = ai_result.get("intent", "unknown")
        confidence = float(ai_result.get("confidence", 0.0))
        entities = ai_result.get("entities", {})
        raw_entities = ai_result.get("raw_entities", [])
    
        print(f"[CHAT] HISTORY COUNT: {len(request.conversation_history)}", flush=True,)

        print(f"[CHAT] HISTORY: {request.conversation_history}", flush=True,)

        previous_user_message = None
        previous_ai_result = None
        follow_up_resolved = False
        is_transaction_correction = False

        if request.conversation_history:
            for message in reversed(request.conversation_history):
                if message.role == "user":
                    previous_user_message = message.content
                    break

        if previous_user_message:
            previous_ai_result = analyze_message(previous_user_message)
            follow_up_result = resolve_follow_up(
                previous_turn={
                    "intent": previous_ai_result.get("intent"),
                    "entities": previous_ai_result.get("entities", {}),
                },
                current_turn={
                    "intent": intent,
                    "confidence": confidence,
                    "entities": entities,
                    "message": request.message,
                },
            )

            print(f"[CHAT] FOLLOW-UP RESULT: {follow_up_result}", flush=True,)
            is_transaction_correction = False
            if follow_up_result.get("resolved"):
                intent = follow_up_result["intent"]
                entities = follow_up_result["entities"]
                follow_up_resolved = True
                is_transaction_correction = (follow_up_result.get("reason") == "transaction_correction")

        print(
            f"[CHAT] NLU RESULT: intent={intent}, confidence={confidence}, entities={entities}",
            flush=True,
        )
        
        # ============================================================
        # Validation
        # ============================================================
        print("[CHAT] 3 VALIDATION START", flush=True)
        validation_result = validate_ai_output(
            intent=intent,
            confidence=confidence,
            amount=entities.get("amount"),
        )
        print(
            f"[CHAT] 4 VALIDATION DONE: {validation_result}",
            flush=True,
        )
        if not validation_result.get("valid"):
            # If validation fails, try LLM for a conversational response
            if conversational_result.get("should_route_to_llm"):
                if request.stream:
                    generator = generate_chat_response_stream(
                        user_message=request.message,
                        system_instruction=general_system_prompt,
                        conversation_history=conversation_history,
                        context=study_context or None,
                    )
                    return StreamingResponse(_sse_generator(generator), media_type="text/event-stream")
                else:
                    response = generate_chat_response(
                        user_message=request.message,
                        system_instruction=general_system_prompt,
                        conversation_history=conversation_history,
                        context=study_context or None,
                    )
                    return ChatResponse(response=response)

            fallback_msg = "Mình chưa thể xử lý yêu cầu này một cách an toàn. Bạn thử diễn đạt lại giúp mình nhé."
            if request.stream:
                return StreamingResponse(_sse_generator([fallback_msg]), media_type="text/event-stream")
            return ChatResponse(response=fallback_msg)


        # Get raw amount for Decision Layer
        raw_amount = None
        for entity in raw_entities:
            if (isinstance(entity, dict) and entity.get("type") == "AMOUNT"):
                raw_amount = entity.get("text")
                break

        # Evidence-Based Decision
        if follow_up_resolved:
            decision_result = {
                "decision": "accept",
                "reason": "conversation_context_resolved",
                "needs_clarification": False,
                "clarification_question": None,
        }
        else:
            decision_result = decide(
                message=request.message,
                intent=intent,
                confidence=confidence,
                entities=entities,
                raw_amount=raw_amount,
        )


        # Clarification
        print(f"[CHAT] DECISION RESULT: {decision_result}", flush=True,)

        # Route general conversation to LLM
        if decision_result.get("decision") == "general_conversation":
            if request.stream:
                generator = generate_chat_response_stream(
                    user_message=request.message,
                    system_instruction=general_system_prompt,
                    conversation_history=conversation_history,
                    context=study_context or None,
                )
                return StreamingResponse(_sse_generator(generator), media_type="text/event-stream")
            else:
                response = generate_chat_response(
                    user_message=request.message,
                    system_instruction=general_system_prompt,
                    conversation_history=conversation_history,
                    context=study_context or None,
                )
                return ChatResponse(response=response)

        if decision_result.get("needs_clarification"):
            clarif_msg = decision_result.get(
                "clarification_question",
                "Mình cần thêm một chút thông tin để xử lý chính xác nhé.",
            )
            if request.stream:
               return StreamingResponse(_sse_generator([clarif_msg]), media_type="text/event-stream")
            return ChatResponse(response=clarif_msg)


        # Save transaction ONLY for transaction intents
        transaction_result = None
        if intent in {"add_expense", "add_income"}:
            print("[CHAT] 3 transaction SAVE START", flush=True)
            if is_transaction_correction:
                transaction_result = update_latest_transaction_amount(
                    db=db,
                    transaction_type=intent.replace("add_", ""),
                    amount=float(entities["amount"]),
                )
                if transaction_result is None:
                    raise ValueError("No previous transaction found for correction")

                print("[CHAT] transaction CORRECTION DONE", flush=True,)

            else:
                transaction_result = save_normalized_transaction(
                    db=db,
                    transaction_type= intent.replace("add_", ""),
                    amount=raw_amount,
                    category=entities.get("category"),
                    date_value=entities.get("date"),
                    merchant=entities.get("merchant"),
                    description=entities.get("description"),
                    payment_method=entities.get("payment_method"),
                    period=entities.get("period"),
                )
                print("[CHAT] 4 transaction SAVE DONE", flush=True)

            print(
                f"[CHAT] transaction_result TYPE: {type(transaction_result)}",
                flush=True,
            )
            print(
                f"[CHAT] transaction_result VALUE: {transaction_result}",
                flush=True,
            )


        # Financial facts — only when needed

        financial_result = None
        if intent == "query_balance":
            financial_result = {
                "balance": get_current_balance(db),
            }
        elif intent == "query_expense":
            financial_result = {
                "total_expense": get_total_expense(db),
        }
        elif intent == "query_category":
            category = entities.get("category")
            financial_result = get_expense_by_category(
                db,
                category=category,
                period=entities.get("period"),
            )
        elif intent == "financial_advice":
            financial_result = {
                "balance": get_current_balance(db),
        }


        # Build context for LLM
        context = build_context(
            conversation_history = conversation_history,
            financial_result = financial_result,
        )

        # Structured context
        structured_context = f"""
        === CONVERSATIONAL CONTEXT ===
            conversation_type: {conversational_result.get("conversation_type")}
            financial_relevance: {conversational_result.get("financial_relevance")}
            should_resolve_context: {conversational_result.get("should_resolve_context")}
            reason: {conversational_result.get("reason")}

        === NLU RESULT ===
            intent: {intent}
            confidence: {confidence}
            entities: {entities}

        === DECISION RESULT ===
            decision: {decision_result.get("decision")}
            reason: {decision_result.get("reason")}
    """

        if transaction_result is not None:
            structured_context += f"""
            === TRANSACTION RESULT ===
                    status: success
                    type: {transaction_result.transaction_type}
                    amount: {transaction_result.amount}
                    amount_display: {format_vnd(transaction_result.amount)}
                    category: {transaction_result.category}
                    date: {transaction_result.date}
                    merchant: {transaction_result.merchant}
                    description: {transaction_result.description}
                    payment_method: {transaction_result.payment_method}

            The transaction has been saved successfully.
    """

        if financial_result is not None:
            structured_context += f"""
        === FINANCIAL FACTS ===
                total_income: {financial_result.get("total_income")}
                total_expense: {financial_result.get("total_expense")}
                balance: {financial_result.get("balance")}

            These values are authoritative. Do not recalculate them. 
            Use Vietnamese currency format:
            "80.000 đồng", "400.000 đồng", "2.000.000 đồng". Never use "$", "USD", or decimal ".0".
        """
        full_context = "\n\n".join(
            part
            for part in [context, structured_context, study_context]
            if part
        )

        # LLM — Financial mode
        print("[CHAT] 7 OLLAMA START", flush=True)
        financial_system_prompt = general_system_prompt + """
            QUY TẮC TÀI CHÍNH (chỉ áp dụng khi có dữ liệu tài chính trong context):
                1. Không tự tạo giao dịch.
                2. Chỉ nói giao dịch đã được ghi nhận khi TRANSACTION RESULT tồn tại.
                3. TRANSACTION RESULT là nguồn sự thật về giao dịch vừa xử lý.
                    3a. Khi TRANSACTION RESULT có status success, hãy xác nhận giao dịch bằng ít nhất một thông tin cụ thể từ TRANSACTION RESULT, ưu tiên số tiền và loại giao dịch.
                    3b. Không được thay thế thông tin giao dịch cụ thể bằng câu xác nhận chung như "Giao dịch đã được ghi nhận."
                    3c. Không tự tạo hoặc suy diễn category, date, merchant nếu TRANSACTION RESULT không cung cấp.
                4. FINANCIAL FACTS là nguồn sự thật về số liệu tài chính.
                5. Giữ nguyên chính xác mọi số tiền được cung cấp.
                6. Không thêm hoặc bớt chữ số.
                7. Không tự tính lại số tiền.
                8. Không làm tròn số tiền.
                9. Không tự suy diễn số liệu.
                10. Không đưa số liệu tài chính nếu context không cung cấp.
                11. Mọi số tiền phải hiển thị bằng đồng Việt Nam.
                12. Luôn dùng định dạng "80.000 đồng", "2.000.000 đồng".
                13. Không dùng "$", "USD" hoặc dạng "80000.0". Nếu người dùng vừa ghi nhận một giao dịch, chỉ cần xác nhận giao dịch đó. Không cần đưa tổng thu nhập, tổng chi tiêu hoặc số dư.
        """

        if request.stream:
            generator = generate_chat_response_stream(
                user_message = request.message,
                system_instruction = financial_system_prompt,
                conversation_history = conversation_history,
                context = full_context,
            )
            return StreamingResponse(_sse_generator(generator), media_type="text/event-stream")
        else:
            response = generate_chat_response(
                user_message = request.message,
                system_instruction = financial_system_prompt,
                conversation_history = conversation_history,
                context = full_context,
            )

            print("[CHAT] 8 OLLAMA DONE", flush=True)
            print("[CHAT] 9 RESPONSE GENERATED", flush=True)
            print(f"[CHAT] 9 RESPONSE LENGTH: {len(response)}", flush=True)
            return ChatResponse(response = response)
    except Exception:
        db.rollback()
        raise

    finally:
        print("[CHAT] 10 DB CLOSE", flush=True)
        db.close()
