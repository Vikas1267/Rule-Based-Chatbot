"""
Interactive Command Line Interface (CLI) for Rule-Based Chatbot.
Clean, natural conversational interface for terminal users.
"""
import sys
from typing import Dict, Any

# Ensure UTF-8 output encoding on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
except ImportError:
    class DummyColor:
        def __getattr__(self, name):
            return ""
    Fore = Style = DummyColor()

from chatbot.engine import RuleBasedChatbot
from chatbot.rules import TOPICS


BANNER = f"""
============================================================
              RULE-BASED CONVERSATIONAL BOT
============================================================
(Type your message naturally. Type 'topics' to see topics, or 'exit' to quit.)
"""


def safe_print(*args, **kwargs):
    """Safely prints text on all consoles, preventing Unicode charmap crashes on Windows."""
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        sep = kwargs.get("sep", " ")
        text = sep.join(str(a) for a in args)
        safe_text = text.encode("ascii", errors="replace").decode("ascii")
        clean_kwargs = {k: v for k, v in kwargs.items() if k != "sep"}
        print(safe_text, **clean_kwargs)


class ChatbotCLI:
    def __init__(self, debug_mode: bool = False):
        self.bot = RuleBasedChatbot()
        self.debug_mode = debug_mode

    def display_topics(self):
        safe_print("\n=== Supported Topics ===")
        for key, topic in TOPICS.items():
            safe_print(f"\n{topic['name']}: {topic['description']}")
            safe_print("  Sample queries:")
            for prompt in topic["sample_prompts"]:
                safe_print(f"    - {prompt}")
        safe_print()

    def print_bot_message(self, result: Dict[str, Any]):
        response = result.get("response", "")
        confidence = result.get("confidence", 0.0)
        topic = result.get("topic", "general")
        intent = result.get("intent", "unknown")
        matched_rule = result.get("matched_rule", "")
        entities = result.get("entities", {})
        user_keywords = result.get("user_keywords", [])

        # Debug metadata banner ONLY if debug_mode is explicitly turned on
        if self.debug_mode:
            conf_color = Fore.GREEN if confidence >= 0.7 else (Fore.YELLOW if confidence >= 0.3 else Fore.RED)
            safe_print(f"{Fore.LIGHTBLACK_EX}+- [DEBUG] Topic: {topic} | Intent: {intent} | Match: {conf_color}{matched_rule} ({int(confidence*100)}%){Style.RESET_ALL}")
            if user_keywords:
                safe_print(f"{Fore.LIGHTBLACK_EX}|  Keywords: {user_keywords}{Style.RESET_ALL}")
            if entities:
                ent_str = ", ".join(f"{k}='{v}'" for k, v in entities.items())
                safe_print(f"{Fore.LIGHTBLACK_EX}|  Entities: {ent_str}{Style.RESET_ALL}")
            safe_print(f"{Fore.LIGHTBLACK_EX}+--------------------------------------------------------------------------{Style.RESET_ALL}")

        # Clean, natural bot response without debug noise or quick options clutter
        safe_print(f"{Fore.GREEN}{Style.BRIGHT}Bot:{Style.RESET_ALL} {response}\n")

    def run(self):
        safe_print(BANNER)

        # Initial friendly greeting from bot
        safe_print(f"{Fore.GREEN}{Style.BRIGHT}Bot:{Style.RESET_ALL} Hello! Welcome to our support desk. How can I help you today?\n")

        while True:
            try:
                user_input = input(f"{Fore.CYAN}{Style.BRIGHT}You:{Style.RESET_ALL} ").strip()
            except (KeyboardInterrupt, EOFError):
                safe_print(f"\n{Fore.GREEN}{Style.BRIGHT}Bot:{Style.RESET_ALL} Goodbye! Have a wonderful day.")
                break

            if not user_input:
                continue

            # Command routing
            cmd = user_input.lower()
            if cmd in ("exit", "quit", "bye", "/quit", "/exit"):
                safe_print(f"{Fore.GREEN}{Style.BRIGHT}Bot:{Style.RESET_ALL} Goodbye! Have a wonderful day.")
                break
            elif cmd in ("topics", "/topics", "help", "/help"):
                self.display_topics()
                continue
            elif cmd in ("/debug", "--debug", "debug"):
                self.debug_mode = not self.debug_mode
                status = "ENABLED" if self.debug_mode else "DISABLED"
                safe_print(f"[!] Diagnostics view is now {status}.\n")
                continue
            elif cmd in ("reset", "/reset", "clear", "/clear"):
                self.bot.reset_session()
                safe_print(f"{Fore.GREEN}{Style.BRIGHT}Bot:{Style.RESET_ALL} Conversation reset! How can I help you today?\n")
                continue

            # Process input through rule engine
            result = self.bot.process_message(user_input)
            self.print_bot_message(result)


def main():
    cli = ChatbotCLI()
    cli.run()


if __name__ == "__main__":
    main()
