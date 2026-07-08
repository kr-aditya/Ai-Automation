import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    print("ERROR: GROQ_API_KEY not found!")
    exit()

# Initialize Groq client
client = Groq(api_key=api_key)

# Configuration
MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """
You are an expert AI engineering tutor helping a Computer Science graduate
from India learn AI systems from scratch.

Guidelines:
- Give clear and practical explanations
- Include Python examples when needed
- Keep responses concise unless asked for more
- Use beginner-friendly analogies
"""

# Stores conversation memory
conversation_history = []


def send_message(user_message: str) -> str:
    """Send message to AI and return response."""
    conversation_history.append({
        "role": "user",
        "content": user_message
    })

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                *conversation_history
            ],
            max_tokens=1024,
            temperature=0.7
        )

        ai_reply = response.choices[0].message.content

        conversation_history.append({
            "role": "assistant",
            "content": ai_reply
        })

        return ai_reply

    except Exception as e:
        print(f"\nERROR: {str(e)}")
        conversation_history.pop()
        return "Something went wrong. Please try again."


def show_welcome():
    print("\n" + "=" * 55)
    print("      AI Engineering Tutor — Powered by Groq")
    print(f"      Model: {MODEL}")
    print("=" * 55)
    print("Commands:")
    print("  history  -> Show conversation history")
    print("  clear    -> Clear conversation")
    print("  quit     -> Exit chatbot")
    print("=" * 55 + "\n")


def show_history():
    if not conversation_history:
        print("\n[No conversation yet]\n")
        return

    print(f"\n--- Conversation History ({len(conversation_history)} messages) ---")

    for i, message in enumerate(conversation_history):
        role = message["role"].upper()
        preview = message["content"][:150]

        if len(message["content"]) > 150:
            preview += "..."

        print(f"\n[{i + 1}] {role}: {preview}")

    print()


def main():
    show_welcome()

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() == "quit":
            print("\nGoodbye!\n")
            break

        if user_input.lower() == "history":
            show_history()
            continue

        if user_input.lower() == "clear":
            conversation_history.clear()
            print("\nConversation cleared.\n")
            continue

        if not user_input:
            continue

        print("\nAI: ", end="", flush=True)
        response = send_message(user_input)
        print(response)
        print()


if __name__ == "__main__":
    main()