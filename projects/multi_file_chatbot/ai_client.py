"""
ai_client.py
Wraps the Groq API in a clean Python class.

This is the pattern LangChain uses internally.
When you write ChatGroq(...) on Day 8, it's doing exactly
what this class does — just with more features.
"""

from datetime import datetime
from groq import Groq
from config import GROQ_API_KEY, MODEL_NAME, MAX_TOKENS, TEMPERATURE


class AIClient:
    """
    A wrapper class around the Groq API.
    
    Why use a class here instead of just functions?
    - The client object (self.client) persists across calls
    - The system prompt and model are set once, used everywhere
    - Easy to swap out Groq for OpenAI later — just change this file
    - Mirrors how LangChain structures its LLM classes
    """
    
    def __init__(self, system_prompt: str):
        """
        Initialise the AI client with a system prompt.
        
        Args:
            system_prompt: The role/instructions for the AI
        """
        # Create the Groq connection once — reuse across all calls
        self.client        = Groq(api_key=GROQ_API_KEY)
        self.system_prompt = system_prompt
        self.model         = MODEL_NAME
        self.history       = []      # conversation history
        self.total_tokens  = 0       # track usage across session
    
    def chat(self, user_message: str) -> str:
        """
        Send a message and get a response.
        Manages history automatically.
        
        Args:
            user_message: What the user typed
            
        Returns:
            The AI's response as a string
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Store with timestamp (for saving to file)
        self.history.append({
            "role":      "user",
            "content":   user_message,
            "timestamp": timestamp
        })
        
        try:
            # Build clean messages for the API
            # (API doesn't accept 'timestamp' field)
            api_messages = [
                {"role": m["role"], "content": m["content"]}
                for m in self.history
            ]
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    *api_messages
                ],
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE
            )
            
            reply = response.choices[0].message.content
            
            # Track token usage
            self.total_tokens += (
                response.usage.prompt_tokens +
                response.usage.completion_tokens
            )
            
            # Store response
            self.history.append({
                "role":      "assistant",
                "content":   reply,
                "timestamp": datetime.now().strftime("%H:%M:%S")
            })
            
            return reply
        
        except Exception as e:
            self.history.pop()   # remove the failed message
            raise Exception(f"API call failed: {str(e)}")
    
    def get_stats(self) -> dict:
        """Return usage statistics for this session."""
        user_msgs = sum(1 for m in self.history if m["role"] == "user")
        return {
            "messages_sent":  user_msgs,
            "total_messages": len(self.history),
            "tokens_used":    self.total_tokens,
            "model":          self.model
        }
    
    def clear(self):
        """Reset conversation history."""
        self.history.clear()
        self.total_tokens = 0