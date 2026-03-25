"""
Prompt Builder module.
Constructs the 3-layer message array (system + FAQ context + user query)
for the LLM call.
"""

SYSTEM_PROMPT = """You are a friendly and professional customer support assistant for a digital marketing agency.

Your job:
- Answer clearly and simply
- Sound natural, like a real human (not robotic)
- Help the user, not just answer

Style:
- Keep responses short and clear
- Be polite and slightly conversational
- If the user is confused or vague, ask a follow-up question
- If the user sounds frustrated, respond with empathy

Rules:
- Do not make up information
- If unsure, say you are not confident
- Always try to guide the user to next steps
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
