"""
Day 06 — FastAPI AI Backend
============================
This is the Python server that n8n will call.

What this does:
- Runs a web server on http://localhost:8000
- Exposes POST /chat endpoint
- Receives a message, sends to Groq, returns AI response
- n8n webhook connects to this endpoint

New concepts:
- FastAPI: Python web framework for building APIs
- uvicorn: ASGI server that runs FastAPI
- Pydantic: data validation library (comes with FastAPI)
- @app.post: decorator that creates an HTTP POST endpoint
"""

import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
# BaseModel is from Pydantic — it validates incoming request data
# If data doesn't match the model, FastAPI returns a 422 error automatically

from groq import Groq
from typing import Optional
import uvicorn

load_dotenv()

# ── SETUP ────────────────────────────────────────────────────
app = FastAPI(
    title="AI Bootcamp API",
    description="Day 06 — AI backend for n8n automation",
    version="1.0.0"
)

# CORS — Cross Origin Resource Sharing
# Allows requests from different origins (like n8n or React on different ports)
# Without this, browsers block requests from other domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # allow all origins (fine for development)
    allow_methods=["*"],      # allow all HTTP methods
    allow_headers=["*"],      # allow all headers
)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL  = "llama-3.3-70b-versatile"


# ── REQUEST/RESPONSE MODELS ──────────────────────────────────
# Pydantic models define the shape of data coming in and going out
# FastAPI uses these for automatic validation and documentation

class ChatRequest(BaseModel):
    """Shape of data we expect to receive in POST /chat"""
    message: str                          # required field
    user: Optional[str] = "anonymous"    # optional, defaults to "anonymous"
    system_prompt: Optional[str] = None  # optional custom system prompt

class ChatResponse(BaseModel):
    """Shape of data we send back"""
    response: str
    user: str
    model: str
    status: str


# ── ENDPOINTS ────────────────────────────────────────────────

@app.get("/")
async def root():
    """
    Health check endpoint.
    GET http://localhost:8000/
    Returns basic info about the API.
    """
    return {
        "name":    "AI Bootcamp API",
        "status":  "running",
        "version": "1.0.0",
        "endpoints": ["/chat", "/summarise", "/analyse-jd"]
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint.
    POST http://localhost:8000/chat
    
    Receives a message, gets AI response, returns it.
    n8n will call this endpoint from the webhook workflow.
    
    FastAPI automatically:
    - Validates that 'message' field exists and is a string
    - Returns 422 error if required fields are missing
    - Generates API documentation at /docs
    """
    system = request.system_prompt or (
        "You are a helpful AI assistant. "
        "Give clear, concise answers in 2-3 sentences maximum."
    )
    
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system",  "content": system},
                {"role": "user",    "content": request.message}
            ],
            max_tokens=512,
            temperature=0.7
        )
        
        ai_reply = response.choices[0].message.content
        
        return ChatResponse(
            response=ai_reply,
            user=request.user,
            model=MODEL,
            status="success"
        )
    
    except Exception as e:
        # HTTPException sends a proper HTTP error response
        # status_code=500 = Internal Server Error
        raise HTTPException(
            status_code=500,
            detail=f"AI call failed: {str(e)}"
        )


@app.post("/summarise")
async def summarise(request: ChatRequest):
    """
    Summarisation endpoint.
    POST http://localhost:8000/summarise
    
    Takes any text in 'message' field and returns a 3-bullet summary.
    """
    system = (
        "You are a summarisation engine. "
        "Return exactly 3 bullet points summarising the key points. "
        "Each bullet maximum 15 words. No intro text, just bullets."
    )
    
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": f"Summarise this: {request.message}"}
            ],
            max_tokens=256,
            temperature=0.3
        )
        
        return {
            "summary": response.choices[0].message.content,
            "user":    request.user,
            "status":  "success"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyse-jd")
async def analyse_jd(request: ChatRequest):
    """
    Job Description analyser — from Day 5's prompt template.
    POST http://localhost:8000/analyse-jd
    
    Send a job description, get back structured analysis.
    """
    system = (
        "You are a job description analyser. "
        "Return ONLY a JSON object with keys: "
        "role_title, required_skills (array), is_fresher_friendly (bool), "
        "match_score (0-100 for a Python+React developer), key_gaps (array). "
        "No text before or after the JSON."
    )
    
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": request.message}
            ],
            max_tokens=512,
            temperature=0.1   # low temp for JSON output
        )
        
        import json, re
        raw     = response.choices[0].message.content
        cleaned = re.sub(r'```(?:json)?\s*', '', raw).replace('```','').strip()
        start   = cleaned.find('{')
        end     = cleaned.rfind('}') + 1
        result  = json.loads(cleaned[start:end]) if start != -1 else {}
        
        return {"analysis": result, "status": "success"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── RUN SERVER ───────────────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run(
        "main:app",   # "filename:FastAPI_instance_name"
        host="0.0.0.0",       # listen on all network interfaces
        port=8000,             # port number
        reload=True            # auto-restart when you edit the file
    )