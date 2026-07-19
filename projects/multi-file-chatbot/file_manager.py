"""
file_manager.py
Handles all file reading and writing for the project.
Keeping file operations separate from business logic is 
a core software engineering principle called Separation of Concerns.
"""

import os
import json
from datetime import datetime
from config import HISTORY_FILE, EXPORT_FOLDER


def ensure_directories():
    """
    Create required directories if they don't exist.
    os.makedirs with exist_ok=True won't error if folder already exists.
    """
    os.makedirs("data", exist_ok=True)
    os.makedirs(EXPORT_FOLDER, exist_ok=True)


def load_history() -> list:
    """Load conversation history from JSON file."""
    if not os.path.exists(HISTORY_FILE):
        return []
    
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("messages", [])
    except (json.JSONDecodeError, KeyError):
        print("Warning: History file corrupted. Starting fresh.")
        return []


def save_history(messages: list) -> bool:
    """
    Save conversation history to JSON file.
    Returns True if successful, False if it failed.
    """
    ensure_directories()
    
    payload = {
        "last_saved":     datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "message_count":  len(messages),
        "messages":       messages
    }
    
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Save failed: {e}")
        return False


def export_to_txt(messages: list) -> str:
    """
    Export conversation to a timestamped .txt file.
    Returns the filename created.
    """
    ensure_directories()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename  = f"{EXPORT_FOLDER}conversation_{timestamp}.txt"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write("AI Engineering Bootcamp — Conversation Export\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 50 + "\n\n")
        
        for msg in messages:
            role      = msg["role"].upper()
            content   = msg["content"]
            timestamp = msg.get("timestamp", "")
            f.write(f"[{timestamp}] {role}:\n{content}\n\n{'─'*30}\n\n")
    
    return filename


def clear_history() -> bool:
    """Delete the history file. Returns True if deleted, False if didn't exist."""
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)
        return True
    return False