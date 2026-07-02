"""
ingest.py
Loads RBI policy documents and splits them into overlapping chunks for
embedding. Chunking is pure Python (no external deps) so it's testable
anywhere; the embedding step in rag.py is what needs sentence-transformers.

WHY OVERLAPPING CHUNKS:
If we cut a document into non-overlapping blocks, a sentence describing
"inflation was revised up to 5.1%" could get split with its subject in
one chunk and the number in the next -- retrieval would then miss the
connection entirely. A small overlap (chunk_overlap) keeps context that
straddles a cut point intact in at least one chunk.
"""

import re
from pathlib import Path
from dataclasses import dataclass

KB_DIR = Path(__file__).parent.parent / "knowledge_base"


@dataclass
class Chunk:
    text: str
    source: str
    chunk_id: int


def _find_kb_dir() -> Path:
    """Locate the knowledge_base folder regardless of exact repo layout
    (handles the intended src/ + knowledge_base/ structure, and a
    flattened single-folder layout where .txt files sit right next to
    this script -- common after uploading via GitHub mobile)."""
    here = Path(__file__).parent
    candidates = [
        here.parent / "knowledge_base",
        here / "knowledge_base",
        here,
    ]
    for c in candidates:
        if c.exists() and list(c.glob("*.txt")):
            return c
    return here.parent / "knowledge_base"


def load_documents(kb_dir: Path = None) -> dict[str, str]:
    """Load every .txt file in the knowledge base directory."""
    if kb_dir is None:
        kb_dir = _find_kb_dir()
    docs = {}
    for path in sorted(kb_dir.glob("*.txt")):
        docs[path.name] = path.read_text(encoding="utf-8")
    return docs


def split_into_chunks(text: str, source: str, chunk_size: int = 800, chunk_overlap: int = 150) -> list[Chunk]:
    """
    Split text into overlapping chunks, breaking on paragraph boundaries
    where possible rather than mid-sentence.

    chunk_size and chunk_overlap are measured in characters here (simple
    and dependency-free). Production RAG setups often measure in tokens
    instead, since that's what the embedding model actually consumes --
    worth switching to a tokenizer-based length function if you find
    chunks are inconsistent in "true" size.
    """
    # Normalize whitespace, split into paragraphs first
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]

    chunks = []
    current = ""
    for para in paragraphs:
        if len(current) + len(para) + 1 <= chunk_size:
            current = f"{current}\n{para}".strip()
        else:
            if current:
                chunks.append(current)
            # start new chunk, carrying over the tail of the previous one
            overlap_text = current[-chunk_overlap:] if current else ""
            current = f"{overlap_text}\n{para}".strip()
    if current:
        chunks.append(current)

    return [Chunk(text=c, source=source, chunk_id=i) for i, c in enumerate(chunks)]


def build_chunk_index(kb_dir: Path = None) -> list[Chunk]:
    """Load all documents and chunk them into one flat list, ready for
    embedding in rag.py."""
    docs = load_documents(kb_dir)
    all_chunks = []
    for source, text in docs.items():
        all_chunks.extend(split_into_chunks(text, source=source))
    return all_chunks


if __name__ == "__main__":
    chunks = build_chunk_index()
    print(f"Loaded and chunked {len(chunks)} chunks from knowledge base:\n")
    for c in chunks:
        preview = c.text.replace("\n", " ")[:90]
        print(f"[{c.source} #{c.chunk_id}] ({len(c.text)} chars) {preview}...")
