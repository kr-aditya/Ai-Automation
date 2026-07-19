import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from groq import Groq
from typing import Optional
import uvicorn

load_dotenv()

app = FastAPI(
    title="AI Bootcamp API",
    description="Day 06 — AI backend for n8n automation",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      
    allow_methods=["*"],     
    allow_headers=["*"],      
)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL  = "llama-3.3-70b-versatile"



class ChatRequest(BaseModel):
    """Shape of data we expect to receive in POST /chat"""
    message: str                          
    user: Optional[str] = "anonymous"    
    system_prompt: Optional[str] = None  

class ChatResponse(BaseModel):
    """Shape of data we send back"""
    response: str
    user: str
    model: str
    status: str



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
       
        raise HTTPException(
            status_code=500,
            detail=f"AI call failed: {str(e)}"
        )


@app.post("/summarise")
async def summarise(request: ChatRequest):
   
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
            temperature=0.1  
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


if __name__ == "__main__":
    uvicorn.run(
        "main:app",   
        host="0.0.0.0",     
        port=8000,             
        reload=True           
    )