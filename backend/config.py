"""Configuration helpers for the contact agent.

The workflow only needs a small amount of configuration for now, so this file
keeps the settings intentionally lightweight and environment-driven.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv


load_dotenv()

BASE_DIR = Path(__file__).resolve().parent


@dataclass(frozen=True)
class AppConfig:
    """Runtime settings for the agent workflow."""

    max_retries: int = 3
    rag_raw_dir: str = str(BASE_DIR / "data/rag/raw/course_materials")
    rag_index_path: str = str(BASE_DIR / "data/rag/processed/rag_index.json")
    rag_chunks_dir: str = str(BASE_DIR / "data/rag/processed/chunks")
    rag_embeddings_model: str = os.getenv("OPENAI_EMBEDDINGS_MODEL", "text-embedding-3-large")
    rag_similarity_threshold: float = float(os.getenv("RAG_SIMILARITY_THRESHOLD", "0.35"))
    rag_max_chunk_chars: int = int(os.getenv("RAG_MAX_CHUNK_CHARS", "3000"))


def get_config() -> AppConfig:
    """Return the runtime configuration loaded from environment variables."""

    raw_max_retries = os.getenv("MAX_RETRIES", "3")
    try:
        max_retries = max(0, int(raw_max_retries))
    except ValueError:
        max_retries = 3

    return AppConfig(max_retries=max_retries)