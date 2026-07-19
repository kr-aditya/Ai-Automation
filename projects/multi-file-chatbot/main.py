"""
main.py
Entry point for the AI Bootcamp chatbot.
This file ONLY handles user interaction — no AI logic, no file logic.
Each concern lives in its own file. This is professional code structure.
"""

from config import TUTOR_SYSTEM_PROMPT
from ai_client import AIClient
from file_manager import load_history, save_history, export_to_txt, clear_history


def show_welcome(loaded_count: int):
    print("\n" + "=" * 55)
    print("  AI Engineering Bootcamp — Professional Edition")
    print(f"  Loaded {loaded_count} messages from previous session")
    print("=" * 55)
    print("  quit | history | stats | export | clear")
    print("=" * 55 + "\n")


def main():
    # Create AI client instance
    ai = AIClient(system_prompt=TUTOR_SYSTEM_PROMPT)
    
    # Load previous history into the client
    ai.history = load_history()
    show_welcome(len(ai.history))
    
    while True:
        user_input = input("You: ").strip()
        
        if not user_input:
            continue
        
        cmd = user_input.lower()
        
        if cmd == "quit":
            save_history(ai.history)
            print(f"\nSaved. {ai.get_stats()['messages_sent']} exchanges this session.\n")
            break
        
        elif cmd == "history":
            if not ai.history:
                print("\n[No history yet]\n")
            else:
                for msg in ai.history[-6:]:   # last 6 messages
                    role = msg["role"].upper()
                    print(f"\n[{msg.get('timestamp','')}] {role}:")
                    print(msg["content"][:200])
                print()
        
        elif cmd == "stats":
            stats = ai.get_stats()
            for key, val in stats.items():
                print(f"  {key}: {val}")
            print()
        
        elif cmd == "export":
            filename = export_to_txt(ai.history)
            print(f"\nExported to: {filename}\n")
        
        elif cmd == "clear":
            confirm = input("Clear all history? (yes/no): ")
            if confirm.lower() == "yes":
                ai.clear()
                clear_history()
                print("Cleared.\n")
        
        else:
            try:
                print("\nAI: ", end="", flush=True)
                response = ai.chat(user_input)
                print(response + "\n")
                save_history(ai.history)   # auto-save after each exchange
            except Exception as e:
                print(f"\nError: {e}\n")


if __name__ == "__main__":
    main()