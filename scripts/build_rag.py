from __future__ import annotations

import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

# Ensure backend is importable when running from the repository root.
ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"
sys.path.insert(0, str(BACKEND_DIR))

load_dotenv(ROOT_DIR / ".env")
load_dotenv(BACKEND_DIR / ".env")

from services.rag_service import RAGService


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the RAG index for the agent.")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Rebuild the index even if one already exists.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    service = RAGService()
    chunks = service.build_index(force=args.force)
    print(f"Built {len(chunks)} chunks into {service.index_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
