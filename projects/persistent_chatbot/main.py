import os
import json
from datetime import datetime

from dotenv import load_dotenv
from groq import Groq


load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")

if not API_KEY:
    raise ValueError("GROQ_API_KEY not found in environment variables.")


MODEL = "llama-3.3-70b-versatile"
HISTORY_FILE = "chat_history.json"

SYSTEM_PROMPT = """
You are an AI engineering tutor helping a Computer Science graduate
learn AI systems and automation engineering.

Provide practical, code-focused, concise answers.
"""


client = Groq(api_key=API_KEY)


def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data.get("messages", [])
    except json.JSONDecodeError:
        return []


def save_history(messages):
    payload = {
        "last_saved": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_messages": len(messages),
        "messages": messages,
    }

    with open(HISTORY_FILE, "w", encoding="utf-8") as file:
        json.dump(
            payload,
            file,
            indent=2,
            ensure_ascii=False
        )


def export_conversation(messages):
    if not messages:
        print("No conversation available.")
        return

    filename = (
        f"conversation_"
        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    )

    with open(filename, "w", encoding="utf-8") as file:
        file.write("AI Conversation Export\n")
        file.write(
            f"Generated: "
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        )

        for message in messages:
            role = message["role"].upper()
            content = message["content"]
            timestamp = message.get("timestamp", "")

            file.write(
                f"[{timestamp}] {role}\n"
            )
            file.write(
                f"{content}\n\n"
            )

    print(f"Conversation exported to {filename}")


def chat(user_message, history):
    timestamp = datetime.now().strftime("%H:%M:%S")

    history.append({
        "role": "user",
        "content": user_message,
        "timestamp": timestamp
    })

    try:
        api_messages = [
            {
                "role": message["role"],
                "content": message["content"]
            }
            for message in history
        ]

        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                *api_messages
            ],
            temperature=0.7,
            max_tokens=1024,
        )

        ai_response = (
            response
            .choices[0]
            .message
            .content
        )

        history.append({
            "role": "assistant",
            "content": ai_response,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })

        save_history(history)

        return ai_response

    except Exception as error:
        history.pop()
        return f"Error: {error}"


def show_stats(messages):
    user_messages = [
        message
        for message in messages
        if message["role"] == "user"
    ]

    print("\nConversation Statistics")
    print("-" * 30)
    print(f"User messages : {len(user_messages)}")
    print(f"Total messages: {len(messages)}")

    if os.path.exists(HISTORY_FILE):
        size = os.path.getsize(HISTORY_FILE)
        print(f"File size     : {size} bytes")

    print()


def main():
    history = load_history()

    print("\nPersistent AI Tutor")
    print("Commands: history, stats, export, clear, quit\n")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() == "quit":
            save_history(history)
            break

        elif user_input.lower() == "history":
            for message in history[-10:]:
                role = message["role"].upper()
                timestamp = message.get("timestamp", "")
                print(
                    f"\n[{timestamp}] "
                    f"{role}: "
                    f"{message['content'][:200]}"
                )

        elif user_input.lower() == "stats":
            show_stats(history)

        elif user_input.lower() == "export":
            export_conversation(history)

        elif user_input.lower() == "clear":
            confirm = input(
                "Delete all history? (yes/no): "
            )

            if confirm.lower() == "yes":
                history.clear()

                if os.path.exists(HISTORY_FILE):
                    os.remove(HISTORY_FILE)

                print("History cleared.\n")

        elif user_input:
            print("\nAI:", end=" ", flush=True)

            response = chat(
                user_input,
                history
            )

            print(response)
            print()


if __name__ == "__main__":
    main()