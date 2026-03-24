"""
Configuration module for the AI Customer Support Agent.
Centralizes all settings, environment variables, and constants.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# --- Groq API Configuration ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_TEMPERATURE = 0.3
GROQ_MAX_TOKENS = 300
GROQ_TIMEOUT = 10  # seconds

# --- Retry Configuration ---
MAX_RETRIES = 2
RETRY_DELAYS = [1, 2]  # seconds between retries (exponential backoff)

# --- Input Validation ---
MAX_MESSAGE_LENGTH = 500

# --- FAQ Data Path ---
FAQ_FILE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "final_faq.txt")

# --- Response Sanity Check ---
MIN_RESPONSE_LENGTH = 10
MAX_RESPONSE_LENGTH = 1500
BLOCKED_PHRASES = [
    "as an ai",
    "as a language model",
    "i don't have access",
    "i cannot browse",
    "i'm just a computer program",
    "as an artificial intelligence",
]

FALLBACK_RESPONSE = (
    "I'm not confident about this. Would you like to connect with human support?"
)
