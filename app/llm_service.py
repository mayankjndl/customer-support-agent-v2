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


def get_llm_response(messages: list[dict]) -> str:
    """
    Sends the constructed messages to Groq and returns the LLM response.
    Includes retry logic for transient errors.

    Args:
        messages: The messages array from prompt_builder.

    Returns:
        The validated response string from the LLM.

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
            )

            latency_ms = round((time.time() - start_time) * 1000)

            # Extract the response text
            response_text = completion.choices[0].message.content.strip()

            logger.info(
                f"LLM response received | {len(response_text)} chars | {latency_ms}ms"
            )

            # Run sanity check before returning
            validated_response = validate_response(response_text)
            return validated_response

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
