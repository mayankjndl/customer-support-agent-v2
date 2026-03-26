"""
Database module.
Handles basic I/O for storing leads in a JSONL file and generating analytics.
"""

import json
import logging
from collections import Counter
from datetime import datetime, timezone
from app.config import LEADS_FILE_PATH, LOG_FILE_PATH

logger = logging.getLogger(__name__)

def save_lead(name: str, phone: str, requirement: str) -> bool:
    """
    Appends a captured lead to leads.jsonl.
    """
    try:
        lead_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "name": name,
            "phone": phone,
            "requirement": requirement
        }
        with open(LEADS_FILE_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(lead_entry) + "\n")
        logger.info(f"Lead saved successfully for {phone}")
        return True
    except Exception as e:
        logger.error(f"Failed to save lead: {e}")
        return False

def get_leads() -> list[dict]:
    """
    Retrieves all captured leads.
    """
    leads = []
    try:
        with open(LEADS_FILE_PATH, "r", encoding="utf-8") as f:
            for line in f:
                leads.append(json.loads(line.strip()))
    except FileNotFoundError:
        pass
    except Exception as e:
        logger.error(f"Failed to read leads: {e}")
    return leads

def get_analytics() -> dict:
    """
    Parses logs.jsonl to calculate total queries, failures, average latency,
    and common queries (top 5).
    """
    total_queries = 0
    failure_count = 0
    total_latency = 0
    queries_list = []

    try:
        with open(LOG_FILE_PATH, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    total_queries += 1
                    
                    if entry.get("status") in ["error", "api_timeout"]:
                        failure_count += 1
                        
                    total_latency += entry.get("latency_ms", 0)
                    
                    q = entry.get("query", "").strip()
                    if q:
                        queries_list.append(q)
                except json.JSONDecodeError:
                    continue
                    
        avg_lat = round(total_latency / total_queries) if total_queries > 0 else 0
        
        # Calculate top 5 common queries
        common_queries_raw = Counter(queries_list).most_common(5)
        common_queries = [{"query": k, "count": v} for k, v in common_queries_raw]

        return {
            "total_queries": total_queries,
            "failure_count": failure_count,
            "average_latency_ms": avg_lat,
            "common_queries": common_queries
        }
        
    except FileNotFoundError:
        return {
            "total_queries": 0,
            "failure_count": 0,
            "average_latency_ms": 0,
            "common_queries": []
        }
    except Exception as e:
        logger.error(f"Error calculating analytics: {e}")
        return {"error": "Failed to calculate analytics"}
