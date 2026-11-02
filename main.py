"""
Universal Entry Point for Rule-Based Conversational Chatbot (Terminal-Based).

Usage:
    python main.py          # Launch clean conversational chatbot
    python main.py --debug  # Launch with developer debug telemetry
    python main.py --test   # Run automated test suite
"""
import sys
import argparse
import unittest

# Ensure UTF-8 output encoding on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def run_tests():
    print("[*] Running Automated Test Suite...")
    loader = unittest.TestLoader()
    suite = loader.discover(".", pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)


def main():
    parser = argparse.ArgumentParser(
        description="Terminal-Based Rule-Based Chatbot with Regex, Keyword Scoring & Fallbacks."
    )
    parser.add_argument("--test", action="store_true", help="Run automated test suite and exit")
    parser.add_argument("--debug", action="store_true", help="Display developer regex & keyword telemetry")

    args = parser.parse_args()

    if args.test:
        run_tests()
        return

    # Direct launch into clean terminal chatbot
    from cli import ChatbotCLI
    cli = ChatbotCLI(debug_mode=args.debug)
    cli.run()


if __name__ == "__main__":
    main()
