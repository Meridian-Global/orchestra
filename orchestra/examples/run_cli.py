#!/usr/bin/env python3
"""
CLI demo for Orchestra multi-agent content system.
Usage: python examples/run_cli.py "your content idea here"
"""

import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Add parent directory to path so we can import backend modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.core.orchestrator import run_full_pipeline


def print_section(title: str, content: str):
    print(f"\n{'─'*60}")
    print(f"  {title}")
    print(f"{'─'*60}")
    print(content)


def main():
    if len(sys.argv) < 2:
        print("Usage: python run_cli.py \"your content idea here\"")
        sys.exit(1)

    idea = " ".join(sys.argv[1:])

    print("\n🎼 ORCHESTRA — Multi-Agent Content System")
    print(f"   Idea: {idea}")

    # Pipeline runs and prints thinking live
    result = run_full_pipeline(idea)

    # Final outputs
    cr = result["critic_review"]

    print(f"\n\n{'═'*60}")
    print("  CRITIC NOTES")
    print(f"{'═'*60}")
    print(cr.notes)

    print_section("INSTAGRAM — final", cr.instagram_improved)
    print_section("THREADS — final", cr.threads_improved)
    print_section("LINKEDIN — final", cr.linkedin_improved)

    print(f"\n{'═'*60}")
    print("  Pipeline complete.")
    print(f"{'═'*60}\n")


if __name__ == "__main__":
    main()
