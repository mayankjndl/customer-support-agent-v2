"""
FAQ Loader module.
Reads structured Q&A data from a JSON file to build the system context for the LLM.
"""

import json
import logging
from app.config import FAQ_FILE_PATH

logger = logging.getLogger(__name__)

# Cache variable
_CACHED_FAQ_DATA: str = ""

def load_faq() -> str:
    """
    Loads JSON FAQ data from disk. 
    Returns the raw stringified representation for system prompt injection.
    Caches the result in memory to avoid repetitive disk I/O.
    """
    global _CACHED_FAQ_DATA
    if _CACHED_FAQ_DATA:
        return _CACHED_FAQ_DATA

    try:
        with open(FAQ_FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        formatted_lines = []
        for index, item in enumerate(data, 1):
            q = item.get("query", "").strip()
            a = item.get("response", "").strip()
            if q and a:
                formatted_lines.append(f"Q{index}: {q}\nA: {a}")
                
        _CACHED_FAQ_DATA = "\n\n".join(formatted_lines)
        logger.info(f"Loaded {len(formatted_lines)} structured Q&A pairs from JSON dataset.")
        return _CACHED_FAQ_DATA

    except FileNotFoundError:
        logger.error(f"FAQ JSON file not found at {FAQ_FILE_PATH}. Returning empty context.")
        return ""
    except json.JSONDecodeError as e:
        logger.error(f"Malformed JSON in FAQ dataset: {e}")
        return ""
    except Exception as e:
        logger.error(f"Unexpected error loading JSON FAQ data: {e}")
        return ""

def format_faq_for_prompt() -> str:
    """
    Returns the cached data. 
    Included to maintain interface compatibility with existing router.
    """
    return load_faq()
