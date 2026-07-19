"""
config.py
All configuration constants for the AI Bootcamp project.
A constant is a variable that never changes while the program runs.
By convention, constants are written in ALL_CAPS.
"""

import os
from dotenv import load_dotenv

# Load environment variables when this module is imported
load_dotenv()

# ── API Configuration ────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME   = "llama-3.3-70b-versatile"
MAX_TOKENS   = 1024
TEMPERATURE  = 0.7

# ── File Paths ───────────────────────────────────────────────
HISTORY_FILE   = "data/chat_history.json"
EXPORT_FOLDER  = "data/exports/"

# ── System Prompts ───────────────────────────────────────────
TUTOR_SYSTEM_PROMPT = """You are an expert AI engineering tutor helping 
a Computer Science fresher in India learn to build AI systems.
Be practical, clear, and always include code examples."""

SUMMARISER_SYSTEM_PROMPT = """You are a technical analyst. 
Summarise content concisely, focusing on practical insights."""

# ── Validate critical values on import ──────────────────────
if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY missing from .env file.\n"
        "Get your free key at: console.groq.com"
    )