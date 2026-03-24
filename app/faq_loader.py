"""
FAQ Loader module.
Parses the FAQ dataset from final_faq.txt into structured data
and formats it for prompt injection. Loads once at startup.
"""

import re
import logging
from functools import lru_cache

from app.config import FAQ_FILE_PATH

logger = logging.getLogger(__name__)


def _parse_faq_file(file_path: str) -> list[dict]:
    """
    Reads the FAQ text file and parses it into a list of
    {"question": "...", "answer": "..."} dictionaries.

    Expected format in the file:
        1. What services do you offer?
        We offer a full range of digital marketing services...
    """
    faq_list = []

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Split into blocks by the numbered question pattern (e.g., "1.", "2.", ...)
    # Each block starts with a number followed by a dot and the question
    blocks = re.split(r"\n(?=\d+\.)", content.strip())

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        lines = block.split("\n", 1)
        if len(lines) < 2:
            continue

        # Remove the number prefix (e.g., "1. " -> "")
        question = re.sub(r"^\d+\.\s*", "", lines[0]).strip()
        answer = lines[1].strip()

        if question and answer:
            faq_list.append({"question": question, "answer": answer})

    return faq_list


@lru_cache(maxsize=1)
def load_faq() -> list[dict]:
    """
    Loads and parses the FAQ dataset. Cached so it only runs once.
    Returns a list of {"question": "...", "answer": "..."} dicts.
    """
    faq_data = _parse_faq_file(FAQ_FILE_PATH)
    logger.info(f"FAQ loaded successfully: {len(faq_data)} items")
    return faq_data


def format_faq_for_prompt(faq_data: list[dict]) -> str:
    """
    Formats the parsed FAQ data into a clean text block
    suitable for injection into the LLM prompt.

    Output format:
        Q: What services do you offer?
        A: We offer a full range of digital marketing services...

        Q: Do you provide SEO services?
        A: Yes, we do offer SEO services...
    """
    formatted_pairs = []
    for item in faq_data:
        formatted_pairs.append(f"Q: {item['question']}\nA: {item['answer']}")

    return "\n\n".join(formatted_pairs)
