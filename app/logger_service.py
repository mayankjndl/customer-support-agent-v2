"""
Logger Service module.
Handles structured logging of user interactions to a local JSONL file.
"""

import json
import logging
from datetime import datetime, timezone

from app.config import LOG_FILE_PATH

logger = logging.getLogger(__name__)

def log_interaction(query: str, response: str, latency_ms: int) -> None:
    """
    Appends a successful chat interaction (query, response, latency, timestamp)
    as a JSON line to the logs file.
    """
    try:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "query": query,
            "response": response,
            "latency_ms": latency_ms,
        }
        with open(LOG_FILE_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")
    except Exception as e:
        logger.error(f"Failed to write to interaction log: {e}")
