from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from config import get_config
from models import RetrievedDocument
from services.llm_service import client, EMBEDDINGS_MODEL


@dataclass
class SemanticChunk:
    id: str
    source: str
    text: str
    embedding: list[float] | None = None
    metadata: dict[str, str] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "source": self.source,
            "text": self.text,
            "metadata": self.metadata or {},
            "embedding": self.embedding or [],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SemanticChunk":
        return cls(
            id=data["id"],
            source=data["source"],
            text=data["text"],
            embedding=data.get("embedding", []),
            metadata=data.get("metadata", {}),
        )


class RAGService:
    """Semantic RAG service for course materials."""

    def __init__(
        self,
        raw_dir: str | None = None,
        index_path: str | None = None,
        chunks_dir: str | None = None,
        embeddings_model: str | None = None,
        similarity_threshold: float | None = None,
        max_chunk_chars: int | None = None,
    ):
        config = get_config()
        self.raw_dir = Path(raw_dir or config.rag_raw_dir)
        # use correct semantic chunks directory from config
        self.chunks_dir = Path(chunks_dir or config.rag_chunks_dir)
        self.index_path = Path(index_path or config.rag_index_path)
        self.embeddings_model = embeddings_model or config.rag_embeddings_model
        self.similarity_threshold = (
            similarity_threshold if similarity_threshold is not None
            else config.rag_similarity_threshold
        )
        self.max_chunk_chars = (
            max_chunk_chars if max_chunk_chars is not None
            else config.rag_max_chunk_chars
        )
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        self.chunks: list[SemanticChunk] = []
        self.load_index()

    def load_index(self) -> None:
        if not self.index_path.exists():
            self.chunks = []
            return

        with self.index_path.open("r", encoding="utf8") as handle:
            payload = json.load(handle)

        self.chunks = [SemanticChunk.from_dict(item) for item in payload.get("chunks", [])]

    def build_index(self, force: bool = False) -> list[SemanticChunk]:
        if self.chunks and not force:
            return self.chunks

        # Try to load from semantic chunks first
        if self.chunks_dir.exists():
            chunks = self._load_semantic_chunks()
            if chunks:
                self.chunks = chunks
                self._embed_chunks()
                self._save_index()
                return self.chunks

        # Fallback to raw files
        raw_files = self._find_raw_files()
        chunks: list[SemanticChunk] = []

        for raw_file in raw_files:
            text = self._read_text(raw_file)
            document_chunks = self.segment_document(text, raw_file)
            chunks.extend(document_chunks)

        if not chunks:
            self.chunks = []
            self._save_index()
            return []

        self.chunks = chunks
        self._embed_chunks()
        self._save_index()

        return self.chunks

    def query(self, question: str, top_k: int = 5) -> list[RetrievedDocument]:
        if not self.chunks:
            self.build_index(force=False)

        if not self.chunks:
            return []

        question_embedding = self._embed_texts([question])[0]
        scored = [
            (
                chunk,
                self._cosine_similarity(question_embedding, chunk.embedding or []),
            )
            for chunk in self.chunks
        ]
        scored.sort(key=lambda pair: pair[1], reverse=True)

        return [
            RetrievedDocument(
                source=chunk.source,
                content=chunk.text,
                score=score,
            )
            for chunk, score in scored[:top_k]
        ]

    def segment_document(self, text: str, source: Path) -> list[SemanticChunk]:
        blocks = self._document_blocks(text)
        blocks = [block.strip() for block in blocks if block.strip()]
        blocks = self._split_long_blocks(blocks)
        return self._group_semantic_chunks(blocks, source)

    def _find_raw_files(self) -> list[Path]:
        allowed = {".md", ".mdx", ".txt", ".html"}
        return sorted(
            path
            for path in self.raw_dir.rglob("*")
            if path.is_file() and path.suffix.lower() in allowed
        )

    def _read_text(self, path: Path) -> str:
        return path.read_text(encoding="utf8", errors="ignore")

    def _document_blocks(self, text: str) -> list[str]:
        lines = text.splitlines()
        blocks: list[str] = []
        current: list[str] = []

        for line in lines:
            if re.match(r"^\s*#{1,6}\s+", line):
                if current:
                    blocks.append("\n".join(current).strip())
                    current = []
                current = [line.strip()]
                continue

            if not line.strip():
                if current:
                    blocks.append("\n".join(current).strip())
                    current = []
                continue

            current.append(line)

        if current:
            blocks.append("\n".join(current).strip())

        return blocks

    def _split_long_blocks(self, blocks: list[str]) -> list[str]:
        result: list[str] = []

        for block in blocks:
            if len(block) <= self.max_chunk_chars:
                result.append(block)
                continue

            paragraphs = [paragraph.strip() for paragraph in re.split(r"\n\s*\n", block) if paragraph.strip()]
            buffer = ""
            for paragraph in paragraphs:
                if not buffer:
                    buffer = paragraph
                    continue

                if len(buffer) + len(paragraph) + 2 > self.max_chunk_chars:
                    result.append(buffer.strip())
                    buffer = paragraph
                else:
                    buffer = f"{buffer}\n\n{paragraph}"

            if buffer:
                result.append(buffer.strip())
        return result

    def _group_semantic_chunks(self, blocks: list[str], source: Path) -> list[SemanticChunk]:
        if not blocks:
            return []

        block_embeddings = self._embed_texts(blocks)
        chunks: list[SemanticChunk] = []

        current_text = blocks[0]
        current_embedding = block_embeddings[0]
        chunk_index = 0

        for next_text, next_embedding in zip(blocks[1:], block_embeddings[1:]):
            if self._is_heading(next_text) or self._cosine_similarity(current_embedding, next_embedding) < self.similarity_threshold:
                chunks.append(
                    SemanticChunk(
                        id=f"{source.name}:{chunk_index}",
                        source=source.name,
                        text=current_text,
                        metadata={"source_path": str(source)},
                    )
                )
                chunk_index += 1
                current_text = next_text
                current_embedding = next_embedding
            else:
                current_text = f"{current_text}\n\n{next_text}"
                current_embedding = self._average_embeddings(current_embedding, next_embedding)

        chunks.append(
            SemanticChunk(
                id=f"{source.name}:{chunk_index}",
                source=source.name,
                text=current_text,
                metadata={"source_path": str(source)},
            )
        )

        texts = [chunk.text for chunk in chunks]
        embeddings = self._embed_texts(texts)
        for chunk, embedding in zip(chunks, embeddings):
            chunk.embedding = embedding

        return chunks

    def _is_heading(self, text: str) -> bool:
        return bool(re.match(r"^\s*#{1,6}\s+", text))

    def _cosine_similarity(self, a: list[float], b: list[float]) -> float:
        if not a or not b or len(a) != len(b):
            return 0.0

        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(y * y for y in b))
        return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0

    def _average_embeddings(self, a: list[float], b: list[float]) -> list[float]:
        return [(x + y) / 2.0 for x, y in zip(a, b)]

    def _embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        response = client.embeddings.create(
            model=self.embeddings_model,
            input=texts,
        )

        return [item.embedding for item in response.data]

    def _embed_chunks(self) -> None:
        if not self.chunks:
            return

        texts = [chunk.text for chunk in self.chunks]
        embeddings = self._embed_texts(texts)
        for chunk, vector in zip(self.chunks, embeddings):
            chunk.embedding = vector

    def _save_index(self) -> None:
        payload = {
            "chunks": [chunk.to_dict() for chunk in self.chunks]
        }
        with self.index_path.open("w", encoding="utf8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)

    def _load_semantic_chunks(self) -> list[SemanticChunk]:
        """Load manually created semantic chunks from chunks directory."""
        if not self.chunks_dir.exists():
            return []

        chunks: list[SemanticChunk] = []
        chunk_files = sorted(
            path
            for path in self.chunks_dir.glob("*.txt")
            if path.is_file()
        )

        for chunk_file in chunk_files:
            try:
                text = chunk_file.read_text(encoding="utf8", errors="ignore")
                chunk = self._parse_semantic_chunk_file(text, chunk_file.stem)
                if chunk:
                    chunks.append(chunk)
            except Exception as e:
                print(f"Warning: Failed to load chunk {chunk_file.name}: {e}")
                continue

        return chunks

    def _parse_semantic_chunk_file(self, text: str, filename: str) -> SemanticChunk | None:
        """Parse a semantic chunk file with metadata header."""
        lines = text.split("\n")
        metadata: dict[str, str] = {"source_file": filename}
        chunk_id = filename
        content_start = 0

        # Parse metadata header
        for i, line in enumerate(lines):
            if line.strip() == "---":
                if content_start == 0:
                    content_start = i + 1
                else:
                    content_start = i + 1
                    break

            if ":" in line and i < 10:
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip()
                if key == "ID":
                    chunk_id = value
                else:
                    metadata[key.lower()] = value

        # Extract content (skip metadata and separators)
        content_lines = [line for line in lines[content_start:] if line.strip()]
        content = "\n".join(content_lines).strip()

        if not content:
            return None

        return SemanticChunk(
            id=chunk_id,
            source=filename,
            text=content,
            metadata=metadata,
        )


