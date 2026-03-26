"""
LLM Service module.
Handles all communication with the Groq API, including
retry logic, timeouts, and response validation.
"""

import time
import logging

from groq import Groq
from groq import APITimeoutError, APIConnectionError, RateLimitError, APIStatusError

from app.config import (
    GROQ_API_KEY,
    GROQ_MODEL,
    GROQ_TEMPERATURE,
    GROQ_MAX_TOKENS,
    GROQ_TIMEOUT,
    MAX_RETRIES,
    RETRY_DELAYS,
    MIN_RESPONSE_LENGTH,
    MAX_RESPONSE_LENGTH,
    BLOCKED_PHRASES,
    FALLBACK_RESPONSE,
)

logger = logging.getLogger(__name__)

# Initialize the Groq client
client = Groq(api_key=GROQ_API_KEY, timeout=GROQ_TIMEOUT)


def validate_response(response_text: str) -> str:
    """
    Lightweight sanity check on the LLM response.
    Returns the response if it passes, or the fallback if it fails.

    Checks:
    - Not empty or too short (< 10 chars)
    - Not too long (> 1500 chars — LLM went on a tangent)
    - Doesn't contain blocked phrases (LLM broke character)
    """
    # Check: empty or too short
    if not response_text or len(response_text.strip()) < MIN_RESPONSE_LENGTH:
        logger.warning("Response sanity check failed: too short or empty")
        return FALLBACK_RESPONSE

    # Check: too long
    if len(response_text) > MAX_RESPONSE_LENGTH:
        logger.warning(
            f"Response sanity check failed: too long ({len(response_text)} chars)"
        )
        return FALLBACK_RESPONSE

    # Check: blocked phrases (LLM broke character)
    response_lower = response_text.lower()
    for phrase in BLOCKED_PHRASES:
        if phrase in response_lower:
            logger.warning(
                f"Response sanity check failed: blocked phrase detected '{phrase}'"
            )
            return FALLBACK_RESPONSE

    return response_text


def get_llm_response(messages: list[dict]) -> tuple[str, str]:
    """
    Sends the constructed messages to Groq and returns the LLM response along with a status string.
    Includes lightweight intent detection for lead capturing via tool calling.

    Args:
        messages: The messages array from prompt_builder.

    Returns:
        Tuple of (Validated Response String, Status Enum String).

    Raises:
        Exception: If all retries are exhausted or a permanent error occurs.
    """
    last_error = None

    for attempt in range(MAX_RETRIES + 1):
        try:
            logger.debug(
                f"LLM call attempt {attempt + 1}/{MAX_RETRIES + 1} | "
                f"model={GROQ_MODEL}, temp={GROQ_TEMPERATURE}"
            )

            start_time = time.time()

            completion = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=messages,
                temperature=GROQ_TEMPERATURE,
                max_tokens=GROQ_MAX_TOKENS,
                tools=[{
                    "type": "function",
                    "function": {
                        "name": "capture_lead",
                        "description": "ONLY call this tool if the user explicitly provides their phone number, email, or name to be contacted. Do NOT call this for general inquiries.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "description": "User's name, or 'Unknown'"},
                                "phone": {"type": "string", "description": "User's phone number or email"},
                                "requirement": {"type": "string", "description": "Brief summary of their need"}
                            },
                            "required": ["name", "phone", "requirement"]
                        }
                    }
                }],
                tool_choice="auto"
            )

            latency_ms = round((time.time() - start_time) * 1000)
            message = completion.choices[0].message
            
            # Lightweight Tool Processing (Lead Capture)
            if message.tool_calls:
                for tool_call in message.tool_calls:
                    if tool_call.function.name == "capture_lead":
                        import json
                        from app.db.database import save_lead
                        args = json.loads(tool_call.function.arguments)
                        save_lead(args.get("name", "Unknown"), args.get("phone", "Unknown"), args.get("requirement", "Unknown"))
                        logger.info(f"Lead captured via tool logic | {latency_ms}ms")
                        return ("Thank you! I've saved your details. Our team will contact you shortly.", "lead_captured")

            # Extract the normal response text
            response_text = message.content or ""
            response_text = response_text.strip()

            logger.info(
                f"LLM response received | {len(response_text)} chars | {latency_ms}ms"
            )

            # Run sanity check before returning
            validated_response = validate_response(response_text)
            status = "fallback_triggered" if validated_response == FALLBACK_RESPONSE else "success"
            return (validated_response, status)

        except (APITimeoutError, APIConnectionError) as e:
            last_error = e
            logger.warning(
                f"LLM transient error (attempt {attempt + 1}): {type(e).__name__}"
            )

        except RateLimitError as e:
            last_error = e
            logger.warning(
                f"LLM rate limited (attempt {attempt + 1}): {e}"
            )

        except APIStatusError as e:
            # Permanent errors (401, 403, etc.) — don't retry
            if e.status_code in (401, 403):
                logger.error(f"LLM auth error: {e.status_code} — not retrying")
                raise
            # Other status errors — treat as transient
            last_error = e
            logger.warning(
                f"LLM API error (attempt {attempt + 1}): {e.status_code}"
            )

        # Wait before retrying (if we have retries left)
        if attempt < MAX_RETRIES:
            delay = RETRY_DELAYS[attempt]
            logger.info(f"Retrying in {delay}s...")
            time.sleep(delay)

    # All retries exhausted
    logger.error(f"LLM call failed after {MAX_RETRIES + 1} attempts: {last_error}")
    raise Exception(f"LLM service unavailable after {MAX_RETRIES + 1} attempts")
