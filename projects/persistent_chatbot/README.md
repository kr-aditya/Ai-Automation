# 💾 Persistent Chatbot

A Python chatbot that stores conversation history in a JSON file, allowing previous chats to be loaded in future sessions.

---

# Overview

Unlike a basic chatbot, this project saves conversations locally and restores them when the application starts.

This demonstrates how AI applications can maintain persistent state.

---

# Features

- Groq LLM integration
- JSON conversation storage
- Load previous conversations
- Save conversations automatically
- Environment variable support

---

# Tech Stack

- Python
- Groq API
- JSON
- python-dotenv

---

# Project Structure

```text
persistent-chatbot/
│
├── main.py
├── conversations.json
├── .env
└── README.md
```

---

# Getting Started

```bash
pip install -r requirements.txt
python main.py
```

---

# Learning Outcomes

- JSON file handling
- Persistent storage
- File management
- AI conversation history

---

# Future Improvements

- SQLite database
- User profiles
- Chat search
- Conversation export