"""Command-line entry point for the contact agent."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


sys.path.insert(0, str(Path(__file__).parent))

from workflow import ContactAgentWorkflow


def main() -> int:
    """Run the workflow from the command line."""

    parser = argparse.ArgumentParser(description="Run the contact agent workflow")
    parser.add_argument("message", nargs="?", help="Incoming contact message")
    args = parser.parse_args()

    message = args.message or input("Enter a contact message: ").strip()
    if not message:
        print("Error: message is required.")
        return 1

    try:
        workflow = ContactAgentWorkflow()
        output = workflow.run(message)
    except Exception as exc:  # pragma: no cover - CLI safeguard
        print(f"Error while running workflow: {exc}")
        return 1

    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())