
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.schemas import AnalyzeRequest, AnalyzeResponse

app = FastAPI(
    title="Vietnamese AI Financial Assistant",
    version="0.1.0"
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

@app.post("/api/ai/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest):
    message = request.message.strip();
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
    return {
        "intent": "add_expense",
        "confidence": 0.95,
        "entities": {
            "amount": 50000,
            "category": "food",
            "date": "today",
            "merchant": None,
            "description": "ăn cơm",
            "payment_method": None,
            "duration": None,
            "target_amount": None,
            "period": None,
            "budget_limit": None
        },
        "status": "accepted",
        "needs_clarification": False,
        "clarification_question": None
    }