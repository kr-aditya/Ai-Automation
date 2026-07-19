# 🤖 AI Chatbot

A simple AI chatbot built using **Python** and the **Groq LLM API**.

This project demonstrates the fundamentals of interacting with a Large Language Model (LLM) through an API. It serves as the starting point of the AI Automation Engineering portfolio.

---

# Overview

The chatbot accepts user input from the terminal, sends it to the Groq API, and displays AI-generated responses.

This project introduces:

- API integration
- Prompt-based interaction
- Environment variables
- Python scripting

---

# Features

- Interactive terminal chatbot
- Groq LLM integration
- Secure API key management using `.env`
- Continuous conversation loop
- Simple and beginner-friendly implementation

---

# Tech Stack

- Python
- Groq API
- python-dotenv

---

# Project Structure

```text
chatbot/
│
├── main.py
├── .env
├── requirements.txt
└── README.md
```

---

# Getting Started

## Install dependencies

```bash
pip install -r requirements.txt
```

## Configure environment variables

Create a `.env` file.

```env
GROQ_API_KEY=your_api_key
```

## Run the chatbot

```bash
python main.py
```

---

# Sample Interaction

```text
You: Hello

AI: Hello! How can I help you today?
```

---

# Learning Outcomes

This project demonstrates:

- API integration
- Environment variables
- Basic prompt engineering
- Python fundamentals

---

# Future Improvements

- Conversation history
- Streaming responses
- Multiple AI models
- GUI version