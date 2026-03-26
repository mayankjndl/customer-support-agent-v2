"""
Prompt Builder module.
Constructs the 3-layer message array (system + FAQ context + user query)
for the LLM call.
"""

SYSTEM_PROMPT = """You are a friendly and professional customer support assistant for a digital marketing agency.

Your goal is to:
- Provide clear and helpful answers
- Keep responses consistent in tone
- Guide the user towards next steps (call, demo, pricing)

Response Structure:
1. Direct answer
2. Short explanation
3. Suggest next step (CTA)

Style:
- Friendly, professional, and natural
- Not robotic
- Keep responses short and clear

Rules:
- Do not make up information
- If unsure, use fallback and connect to human support
- Handle short or unclear queries by asking follow-up questions
- Always try to help the user move forward
- ONLY use information from the FAQ context provided below"""


def build_messages(faq_context: str, user_message: str) -> list[dict]:
    """
    Constructs the messages array for the LLM API call.

    Args:
        faq_context: Pre-formatted FAQ text block from faq_loader.
        user_message: The raw user query string.

    Returns:
        List of message dicts with 'role' and 'content' keys.
    """
    system_content = (
        f"{SYSTEM_PROMPT}\n\n"
        f"--- FAQ Context ---\n"
        f"Use the following FAQ data to answer the user's question:\n\n"
        f"{faq_context}"
    )

    return [
        {"role": "system", "content": system_content},
        {"role": "user", "content": user_message},
    ]
