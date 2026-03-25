"""
AI Customer Support Agent — Main API
FastAPI application with the /chat endpoint.
"""

import time
import logging

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.config import MAX_MESSAGE_LENGTH, GROQ_MODEL
from app.faq_loader import load_faq, format_faq_for_prompt
from app.prompt_builder import build_messages
from app.llm_service import get_llm_response
from app.logger_service import log_interaction

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)-5s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# --- FastAPI App ---
app = FastAPI(
    title="AI Customer Support Agent",
    description="A backend API for an AI-powered customer support assistant for a digital marketing agency.",
    version="1.0.0",
)


# --- Request/Response Models ---
class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=0,
        max_length=MAX_MESSAGE_LENGTH,
        description="The user's question or message",
        examples=["Do you offer SEO services?"],
    )


class ChatResponse(BaseModel):
    reply: str = Field(
        description="The AI assistant's response",
    )


class ErrorResponse(BaseModel):
    error: str


# --- Load FAQ at startup ---
@app.on_event("startup")
def startup_event():
    """Load FAQ data once when the server starts."""
    faq_data = load_faq()
    logger.info(
        f"Server ready | FAQ: {len(faq_data)} items | Model: {GROQ_MODEL}"
    )


# --- Health Check ---
@app.get("/", tags=["Health"])
def health_check():
    """Simple health check endpoint."""
    return {"status": "ok", "service": "AI Customer Support Agent"}


# --- Chat Endpoint ---
@app.post(
    "/chat",
    response_model=ChatResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Server error"},
    },
    tags=["Chat"],
)
def chat(request: ChatRequest):
    """
    Main chat endpoint. Receives a user message, processes it through
    the FAQ-grounded LLM pipeline, and returns the AI response.
    """
    user_message = request.message.strip()
    logger.info(f'POST /chat | "{user_message[:100]}"')

    # Handle empty input natively to completely bypass the LLM
    if not user_message:
        return ChatResponse(reply="Please enter your query")

    try:
        start_time = time.time()

        # Step 1: Load FAQ data (cached — no I/O after first call)
        faq_data = load_faq()
        faq_context = format_faq_for_prompt(faq_data)

        # Step 2: Build the prompt (system + FAQ context + user query)
        messages = build_messages(faq_context, user_message)

        # Step 3: Call the LLM (with retry + sanity check)
        reply = get_llm_response(messages)

        latency_ms = round((time.time() - start_time) * 1000)

        # Step 4: Log the interaction via the new logger service
        log_interaction(user_message, reply, latency_ms)

        logger.info(f"POST /chat | 200 | {latency_ms}ms")

        return ChatResponse(reply=reply)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"POST /chat | 500 | Error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Something went wrong. Please try again in a moment.",
        )
