"""
Day 05 — Prompt Template System
Building LangChain's PromptTemplate from scratch.
This is what happens inside LangChain when you use PromptTemplate.
"""

import os
import json
import re
from dotenv import load_dotenv
from groq import Groq
from typing import Optional, Any

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL  = "llama-3.3-70b-versatile"


# ── PROMPT TEMPLATE CLASS ────────────────────────────────────

class PromptTemplate:
    """
    A reusable prompt with variable placeholders.
    
    This is exactly what LangChain's PromptTemplate does.
    Variables are marked with {curly_braces}.
    
    Usage:
        template = PromptTemplate(
            "Explain {topic} to a {audience}",
            input_variables=["topic", "audience"]
        )
        prompt = template.format(topic="RAG", audience="fresher")
    """
    
    def __init__(self, template: str, input_variables: list[str]):
        self.template        = template
        self.input_variables = input_variables
        self._validate()
    
    def _validate(self):
        """Check all declared variables exist in the template."""
        for var in self.input_variables:
            if "{" + var + "}" not in self.template:
                raise ValueError(
                    f"Variable '{var}' declared but not found in template.\n"
                    f"Template: {self.template[:100]}"
                )
    
    def format(self, **kwargs) -> str:
        """
        Fill in the template variables.
        **kwargs lets you pass any keyword arguments.
        e.g. template.format(topic="RAG", audience="fresher")
        """
        # Check all required variables are provided
        missing = [v for v in self.input_variables if v not in kwargs]
        if missing:
            raise ValueError(f"Missing variables: {missing}")
        
        result = self.template
        for key, value in kwargs.items():
            result = result.replace("{" + key + "}", str(value))
        
        return result
    
    def __repr__(self) -> str:
        return (f"PromptTemplate("
                f"variables={self.input_variables}, "
                f"template='{self.template[:50]}...')")


# ── LLM CALLER WITH STRUCTURED OUTPUT ───────────────────────

def call_llm(
    prompt: str,
    system: str  = "You are a helpful AI assistant.",
    temperature: float = 0.7,
    max_tokens: int    = 1024
) -> str:
    """Clean wrapper for Groq API calls."""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system",  "content": system},
            {"role": "user",    "content": prompt}
        ],
        temperature=temperature,
        max_tokens=max_tokens
    )
    return response.choices[0].message.content


def call_llm_json(
    prompt: str,
    system: str = "You are a data extraction engine. Return only valid JSON."
) -> Optional[dict]:
    """
    Calls LLM and parses the response as JSON.
    Returns a dict on success, None on failure.
    
    Uses temperature=0.1 — lower temperature = more predictable,
    consistent output. Critical for JSON generation.
    """
    raw_response = call_llm(
        prompt,
        system=system,
        temperature=0.1   # low temperature for structured output
    )
    
    try:
        # Clean common LLM JSON mistakes:
        
        # 1. Remove markdown code blocks if present
        # Some models wrap JSON in ```json ... ``` even when told not to
        cleaned = re.sub(r'```(?:json)?\s*', '', raw_response)
        cleaned = cleaned.replace('```', '').strip()
        
        # 2. Find the JSON object (sometimes models add text before/after)
        # Look for content between first { and last }
        start = cleaned.find('{')
        end   = cleaned.rfind('}') + 1
        
        if start == -1 or end == 0:
            print(f"No JSON found in response: {cleaned[:200]}")
            return None
        
        json_str = cleaned[start:end]
        return json.loads(json_str)
    
    except json.JSONDecodeError as e:
        print(f"JSON parse failed: {e}")
        print(f"Raw response was: {raw_response[:300]}")
        return None


# ── DEFINE YOUR PROMPT TEMPLATES ────────────────────────────

# Template 1: Concept explainer
EXPLAINER_TEMPLATE = PromptTemplate(
    template="""Explain {concept} to a {audience}.

Use this structure:
1. What it is (1 sentence, plain language)
2. Why it matters in real projects (1-2 sentences)
3. Simple code example with comments
4. One common mistake beginners make

Keep total response under 250 words.""",
    input_variables=["concept", "audience"]
)


# Template 2: Code reviewer
CODE_REVIEW_TEMPLATE = PromptTemplate(
    template="""Review this Python code as a senior engineer.

CODE:
```python
{code}
```

Return ONLY a JSON object with these exact keys:
{{
  "overall_rating": "good/needs_improvement/poor",
  "issues": [list of specific issues found],
  "suggestions": [list of concrete improvements],
  "security_concerns": [list or empty array if none],
  "score": number from 1-10
}}""",
    input_variables=["code"]
)


# Template 3: Job description analyser
JD_ANALYSER_TEMPLATE = PromptTemplate(
    template="""Analyse this job description for an entry-level AI engineering role.

JOB DESCRIPTION:
{job_description}

Return ONLY a JSON object:
{{
  "role_title": string,
  "required_skills": [array of strings],
  "nice_to_have_skills": [array of strings],
  "experience_required": string,
  "is_fresher_friendly": boolean,
  "match_score_for_python_react_developer": number from 0-100,
  "key_gaps_to_fill": [array of strings]
}}""",
    input_variables=["job_description"]
)


# Template 4: Summariser with length control
SUMMARISER_TEMPLATE = PromptTemplate(
    template="""Summarise the following text.

TARGET AUDIENCE: {audience}
MAX WORDS: {max_words}
FOCUS ON: {focus}

TEXT:
{text}

Write the summary now:""",
    input_variables=["audience", "max_words", "focus", "text"]
)


# ── DEMO FUNCTIONS ───────────────────────────────────────────

def demo_explainer():
    print("\n" + "="*50)
    print("DEMO 1: Concept Explainer")
    print("="*50)
    
    prompt = EXPLAINER_TEMPLATE.format(
        concept="Python decorators",
        audience="JavaScript developer learning Python"
    )
    
    print(f"Prompt preview: {prompt[:100]}...\n")
    response = call_llm(prompt)
    print(response)


def demo_code_review():
    print("\n" + "="*50)
    print("DEMO 2: Code Review → Structured JSON")
    print("="*50)
    
    # Deliberately bad code with issues
    bad_code = '''
import os
api_key = "sk-ant-123456789"  # hardcoded key
def get_data(url):
    import requests
    r = requests.get(url)
    return r.json()

def process(items):
    result = []
    for i in range(len(items)):
        result.append(items[i] * 2)
    return result
'''
    
    prompt = CODE_REVIEW_TEMPLATE.format(code=bad_code)
    result = call_llm_json(prompt)
    
    if result:
        print(f"Rating:    {result.get('overall_rating')}")
        print(f"Score:     {result.get('score')}/10")
        print(f"Issues:    {result.get('issues')}")
        print(f"Security:  {result.get('security_concerns')}")
        print(f"\nFull JSON:\n{json.dumps(result, indent=2)}")
    else:
        print("JSON parsing failed")


def demo_jd_analyser():
    print("\n" + "="*50)
    print("DEMO 3: JD Analyser → Match Score")
    print("="*50)
    
    job_description = """
    We are hiring an AI Automation Engineer (Fresher/0-1 years) 
    for our Bengaluru office.
    
    Requirements:
    - Python programming (required)
    - LangChain or LlamaIndex experience (preferred)
    - REST API development with FastAPI or Flask
    - Basic understanding of LLMs and prompt engineering
    - React.js knowledge is a plus
    - Familiarity with vector databases (Chroma, Pinecone)
    - n8n or Make.com automation experience (bonus)
    
    We welcome fresh graduates with strong project portfolios.
    CTC: 4-7 LPA based on skills demonstrated.
    """
    
    prompt = EXPLAINER_TEMPLATE.format(
        concept="RAG (Retrieval Augmented Generation)",
        audience="non-technical business stakeholder"
    )
    
    jd_prompt = JD_ANALYSER_TEMPLATE.format(
        job_description=job_description
    )
    
    result = call_llm_json(jd_prompt)
    
    if result:
        print(f"Role:          {result.get('role_title')}")
        print(f"Fresher OK:    {result.get('is_fresher_friendly')}")
        print(f"Match Score:   {result.get('match_score_for_python_react_developer')}/100")
        print(f"Required:      {result.get('required_skills')}")
        print(f"Gaps to fill:  {result.get('key_gaps_to_fill')}")


def demo_summariser():
    print("\n" + "="*50)
    print("DEMO 4: Controlled Summarisation")
    print("="*50)
    
    long_text = """
    LangChain is an open-source framework designed to simplify the creation 
    of applications using large language models. It provides a standard interface 
    for chains, lots of integrations with other tools, and end-to-end chains 
    for common applications. The framework allows AI engineers to connect 
    language models to other sources of data and allows a language model to 
    interact with its environment. LangChain's components include model I/O 
    (working with language models), retrieval (document loaders, text splitters, 
    vector stores, retrievers), chains (sequences of calls), agents (LLMs making 
    decisions about which tools to use), and memory (persisting state between 
    chain runs). It has become the most popular framework for building 
    production AI applications in Python.
    """
    
    prompt = SUMMARISER_TEMPLATE.format(
        audience="engineering fresher",
        max_words="50",
        focus="what LangChain does and why it matters",
        text=long_text
    )
    
    response = call_llm(prompt, temperature=0.3)
    print(f"Summary (≤50 words):\n{response}")


# ── TOKEN COUNTER ────────────────────────────────────────────

def estimate_tokens(text: str) -> int:
    """
    Rough token estimation: 1 token ≈ 4 characters in English.
    Real tokenisers are more complex but this is useful for quick checks.
    For exact counts use: tiktoken library (OpenAI's tokeniser).
    """
    return len(text) // 4


def token_budget_check(system: str, user: str, max_budget: int = 4000) -> dict:
    """
    Check if your prompt fits within token budget before sending.
    Prevents expensive or failed API calls.
    """
    system_tokens = estimate_tokens(system)
    user_tokens   = estimate_tokens(user)
    total         = system_tokens + user_tokens
    
    return {
        "system_tokens":  system_tokens,
        "user_tokens":    user_tokens,
        "total_tokens":   total,
        "budget":         max_budget,
        "within_budget":  total < max_budget,
        "remaining":      max_budget - total
    }


# ── MAIN ─────────────────────────────────────────────────────

def main():
    print("Day 05 — Prompt Engineering Demo")
    print("All calls use Groq (free) with Llama 3.3 70B\n")
    
    # Run all demos
    demo_explainer()
    demo_code_review()
    demo_jd_analyser()
    demo_summariser()
    
    # Token budget demo
    print("\n" + "="*50)
    print("BONUS: Token Budget Check")
    print("="*50)
    
    system = CUSTOMER_SUPPORT_PROMPT = """You are a senior AI tutor."""
    user   = EXPLAINER_TEMPLATE.format(
        concept="vector embeddings",
        audience="Python developer"
    )
    
    budget = token_budget_check(system, user)
    print(f"System prompt tokens:  {budget['system_tokens']}")
    print(f"User prompt tokens:    {budget['user_tokens']}")
    print(f"Total tokens:          {budget['total_tokens']}")
    print(f"Within 4000 budget:    {budget['within_budget']}")
    print(f"Remaining budget:      {budget['remaining']}")


if __name__ == "__main__":
    main()