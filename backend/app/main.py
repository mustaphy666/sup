import os
from dotenv import load_dotenv

load_dotenv()
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.auth.dependencies import get_current_user
from app.services.llm_service import llm_service
from memory.conversation_memory import conversation_memory
from app.database import init_database
from app.auth.routes import router as auth_router
import time
from collections import defaultdict, deque
from fastapi import Request
# ============================================================
# APP
# ============================================================

app = FastAPI(
    title="SupportFlow AI",
    version="1.0.0",
)

from app.core.logging_config import configure_logging

configure_logging()

import logging

logger = logging.getLogger(__name__)
logger.info("SupportFlow AI application started")
# ============================================================
# CORS
# ============================================================
frontend_origins = os.getenv("FRONTEND_URL", "")

allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

allowed_origins.extend(
    origin.strip()
    for origin in frontend_origins.split(",")
    if origin.strip()
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)
request_tracker = defaultdict(deque)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    if request.method == "OPTIONS":
        return await call_next(request)

    path = request.url.path

    if path.startswith("/auth/"):
        limit = 10
    elif path == "/chat":
        limit = 20
    else:
        return await call_next(request)

    client_ip = request.client.host if request.client else "unknown"
    key = f"{client_ip}:{path}"

    now = time.time()
    window = 60

    requests = request_tracker[key]

    while requests and now - requests[0] > window:
        requests.popleft()

    if len(requests) >= limit:
        return JSONResponse(
            status_code=429,
            content={
                "success": False,
                "error": "Too many requests. Please try again later."
            }
        )

    requests.append(now)

    return await call_next(request)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": "Invalid request data.",
            "details": exc.errors(),
        },
    )

@app.on_event("startup")
async def startup_event():
    init_database()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# REQUEST / RESPONSE MODELS
# ============================================================

class ChatRequest(BaseModel):
    conversation_id: str = Field(min_length=1, max_length=100)
    message: str = Field(min_length=1, max_length=5000)


class ChatResponse(BaseModel):
    customer_id: str
    conversation_id: str
    response: str
    actions: list[str] = Field(default_factory=list)


# ============================================================
# ROOT
# ============================================================

@app.get("/")
async def root():

    return {
        "status": "online",
        "service": "SupportFlow AI",
        "version": "0.6.0",
    }


# ============================================================
# CHAT
# ============================================================

@app.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user),
):

    customer_id = current_user["customer_id"]
    conversation_id = request.conversation_id
    customer_message = request.message

    # --------------------------------------------------------
    # GET PREVIOUS CONVERSATION
    # --------------------------------------------------------

    history = conversation_memory.get_history(
        conversation_id=conversation_id,
        customer_id=customer_id,
        limit=20,
    )

    # --------------------------------------------------------
    # SAVE USER MESSAGE
    # --------------------------------------------------------

    conversation_memory.save_message(
        conversation_id=conversation_id,
        customer_id=customer_id,
        role="user",
        content=customer_message,
    )

    # --------------------------------------------------------
    # RUN AI AGENT
    # --------------------------------------------------------

    result = await llm_service.generate_response(
        customer_id=customer_id,
        customer_message=customer_message,
        conversation_history=history,
    )

    # --------------------------------------------------------
    # EXTRACT RESULT
    # --------------------------------------------------------

    response_text = result["response"]
    actions = result.get("actions", [])

    # --------------------------------------------------------
    # SAVE ASSISTANT MESSAGE
    # --------------------------------------------------------

    conversation_memory.save_message(
        conversation_id=conversation_id,
        customer_id=customer_id,
        role="assistant",
        content=response_text,
    )

    # --------------------------------------------------------
    # RETURN
    # --------------------------------------------------------

    return ChatResponse(
        customer_id=customer_id,
        conversation_id=conversation_id,
        response=response_text,
        actions=actions,
    )

@app.get("/auth/me")
async def get_authenticated_user(
    current_user: dict = Depends(get_current_user)
):
    return {
        "user_id": current_user["user_id"],
        "email": current_user["email"],
        "customer_id": current_user["customer_id"],
    }
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "application": "SupportFlow AI",
        "version": "1.0.0"
    }
# ============================================================
# GET CONVERSATION
# ============================================================
@app.get("/customers/{customer_id}/refunds")
async def get_refunds(
    customer_id: str,
    current_user: dict = Depends(get_current_user),
):
    if customer_id != current_user["customer_id"]:
        raise HTTPException(
            status_code=403,
            detail="You cannot access another customer's refunds.",
        )

    return llm_service.execute_tool(
        "get_customer_refunds",
        {"customer_id": current_user["customer_id"]},
        current_user["customer_id"],
    )


@app.get("/customers/{customer_id}/tickets")
async def get_tickets(
    customer_id: str,
    current_user: dict = Depends(get_current_user),
):
    if customer_id != current_user["customer_id"]:
        raise HTTPException(
            status_code=403,
            detail="You cannot access another customer's tickets.",
        )

    return llm_service.execute_tool(
        "get_customer_tickets",
        {"customer_id": customer_id},
        customer_id,
    )
@app.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user),
):
    customer_id = current_user["customer_id"]

    history = conversation_memory.get_history(
        conversation_id=conversation_id,
        customer_id=customer_id,
        limit=100,
    )

    return {
        "conversation_id": conversation_id,
        "customer_id": customer_id,
        "messages": history,
    }

    
# ============================================================
# CUSTOMER
# ============================================================

@app.get("/customers/{customer_id}")
async def get_customer(
    customer_id: str,
    current_user: dict = Depends(get_current_user),
):
    if customer_id != current_user["customer_id"]:
        raise HTTPException(
            status_code=403,
            detail="You cannot access another customer's information.",
        )

    authenticated_customer_id = current_user["customer_id"]

    customer = llm_service.execute_tool(
        "check_customer",
        {"customer_id": authenticated_customer_id},
        authenticated_customer_id,
    )

    transactions = llm_service.execute_tool(
        "get_transactions",
        {"customer_id": authenticated_customer_id},
        authenticated_customer_id,
    )

    return {
        "customer": customer,
        "transactions": transactions,
    }

   
# ============================================================
# DELETE CONVERSATION
# ============================================================

@app.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user),
):
    customer_id = current_user["customer_id"]

    conversation_memory.clear_conversation(
        conversation_id=conversation_id,
        customer_id=customer_id,
    )

    return {
        "success": True,
        "conversation_id": conversation_id,
        "message": "Conversation cleared.",
    }