# ⚡ FastAPI AI Backend

A FastAPI backend exposing REST API endpoints for AI-powered chat, summarization, and job description analysis.

---

# Overview

This project demonstrates how to build AI-powered backend services using FastAPI and Groq.

The backend is designed to integrate with n8n workflows and other applications.

---

# Features

- REST API
- FastAPI
- Swagger UI
- AI Chat Endpoint
- Text Summarization
- Job Description Analysis
- Environment Variable Support

---

# API Endpoints

| Method | Endpoint | Description |
|---------|----------|-------------|
| GET | / | Health Check |
| POST | /chat | AI Chat |
| POST | /summarise | Text Summarization |
| POST | /analyse-jd | Job Description Analysis |

---

# Tech Stack

- Python
- FastAPI
- Uvicorn
- Groq API
- Pydantic

---

# Getting Started

```bash
uvicorn main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

---

# Learning Outcomes

- FastAPI
- REST APIs
- Swagger
- Backend Development
- AI Integration

---

# Future Improvements

- Authentication
- Docker
- Deployment
- Database integration