from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.services.llm_service import llm_service
from memory.conversation_memory import conversation_memory


# ============================================================
# APP
# ============================================================

app = FastAPI(
    title="SupportFlow AI",
    version="0.6.0",
)


# ============================================================
# CORS
# ============================================================

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
    customer_id: str
    conversation_id: str
    message: str


class ChatResponse(BaseModel):
    customer_id: str
    conversation_id: str
    response: str
    actions: list[str] = []


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
async def chat(request: ChatRequest):

    customer_id = request.customer_id
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


# ============================================================
# GET CONVERSATION
# ============================================================
@app.get("/customers/{customer_id}/refunds")
async def get_refunds(customer_id: str):
    return llm_service.execute_tool(
        "get_customer_refunds",
        {"customer_id": customer_id},
        customer_id,
    )


@app.get("/customers/{customer_id}/tickets")
async def get_tickets(customer_id: str):
    return llm_service.execute_tool(
        "get_customer_tickets",
        {"customer_id": customer_id},
        customer_id,
    )
@app.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    customer_id: str,
):

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
async def get_customer(customer_id: str):

    customer = llm_service.execute_tool(
        "check_customer",
        {"customer_id": customer_id},
        customer_id,
    )

    transactions = llm_service.execute_tool(
        "get_transactions",
        {"customer_id": customer_id},
        customer_id,
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
    customer_id: str,
):

    conversation_memory.clear_conversation(
        conversation_id=conversation_id,
        customer_id=customer_id,
    )

    return {
        "success": True,
        "conversation_id": conversation_id,
        "message": "Conversation cleared.",
    }