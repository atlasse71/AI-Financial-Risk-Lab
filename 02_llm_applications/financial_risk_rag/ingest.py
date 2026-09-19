"""
ingest.py — Load PDFs, chunk them, embed them, and store in ChromaDB.

Usage:
    python ingest.py                    # ingest all PDFs in data/docs/
    python ingest.py --rebuild          # wipe collection and re-ingest
    python ingest.py --file SR11-7.pdf  # ingest only one file

Design principles:
- Preserve page numbers (for citations)
- Preserve section headings (SR 11-7 has numbered sections)
- Chunk by tokens, not characters (matches embedding model's unit)
- Overlap chunks so context isn't cut mid-thought
- Idempotent: same file re-ingested won't create duplicates
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import chromadb
from chromadb.config import Settings
from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader
import tiktoken

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Resolve paths relative to repo root (.env lives there)
THIS_FILE = Path(__file__).resolve()
REPO_ROOT = THIS_FILE.parents[2]
load_dotenv(REPO_ROOT / ".env")

DOCS_DIR = THIS_FILE.parent / "data" / "docs"
CHROMA_DIR = THIS_FILE.parent / "data" / "chroma"

COLLECTION_NAME = "sr11_7_docs"  # one collection per corpus for now
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIM = 1536  # dimension for text-embedding-3-small

CHUNK_TOKENS = 500
CHUNK_OVERLAP = 50

# SR 11-7 uses headings like "I. Purpose", "II. Scope", "III.1 ...", etc.
# This regex matches top-level roman numerals and numbered subsections.
SECTION_HEADING_RE = re.compile(
    r"^\s*(?P<num>(?:[IVX]+\.\d*|[A-Z]\.\d*|\d+(?:\.\d+)*))\s+(?P<title>[A-Z][^\n]{2,80})\s*$",
    re.MULTILINE,
)

# ---------------------------------------------------------------------------
# Clients
# ---------------------------------------------------------------------------

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

chroma_client = chromadb.PersistentClient(
    path=str(CHROMA_DIR),
    settings=Settings(anonymized_telemetry=False, allow_reset=True),
)

# Tokenizer matching the embedding model family
tokenizer = tiktoken.get_encoding("cl100k_base")


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class PageText:
    """Extracted text for a single PDF page."""
    page_number: int          # 1-indexed (matching what a reader would cite)
    text: str


@dataclass
class Chunk:
    """A single chunk ready for embedding and storage."""
    chunk_id: str             # deterministic hash — used for idempotency
    text: str
    doc: str                  # source filename (e.g., "SR11-7.pdf")
    page: int
    section: str | None       # e.g., "III. Model Development"


# ---------------------------------------------------------------------------
# Step 1 — Extract text from PDF, page by page
# ---------------------------------------------------------------------------

def extract_pages(pdf_path: Path) -> list[PageText]:
    """
    Read a PDF and return one PageText per page.

    Why page-by-page?
    - Preserves page numbers for citations
    - Later we can map chunk → page directly
    """
    reader = PdfReader(str(pdf_path))
    pages: list[PageText] = []
    for i, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        # Normalize whitespace: collapse runs of spaces, remove form feeds
        text = text.replace("\x0c", "\n")
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        pages.append(PageText(page_number=i, text=text.strip()))
    return pages


# ---------------------------------------------------------------------------
# Step 2 — Track section headings across pages
# ---------------------------------------------------------------------------

def annotate_sections(pages: list[PageText]) -> list[tuple[int, str | None, str]]:
    """
    Walk pages in order, tracking the most recent section heading.

    Returns a list of (page_number, section_title, page_text) tuples where
    each page inherits the last-seen section heading. This gives every chunk
    a section label even if the section started on an earlier page.
    """
    annotated: list[tuple[int, str | None, str]] = []
    current_section: str | None = None

    for page in pages:
        # Find all headings on this page
        headings = list(SECTION_HEADING_RE.finditer(page.text))
        if headings:
            # Use the last heading on the page as the "current" one for
            # chunks that follow; the earlier headings will be captured
            # naturally because we chunk the page in order.
            last = headings[-1]
            current_section = f"{last.group('num')} {last.group('title').strip()}"

        annotated.append((page.page_number, current_section, page.text))

    return annotated


# ---------------------------------------------------------------------------
# Step 3 — Split text into token-sized chunks with overlap
# ---------------------------------------------------------------------------

def split_into_chunks(text: str, max_tokens: int, overlap: int) -> list[str]:
    """
    Split text into chunks of <= max_tokens, with `overlap` tokens shared
    between consecutive chunks.

    Strategy: split into paragraphs first (preserves semantic units),
    then greedily pack paragraphs into chunks. If a single paragraph
    exceeds max_tokens, split it by sentences as a fallback.
    """
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: list[str] = []
    current: list[str] = []
    current_tokens = 0

    def token_len(s: str) -> int:
        return len(tokenizer.encode(s))

    def flush() -> str | None:
        if not current:
            return None
        chunk_text = "\n\n".join(current)
        chunks.append(chunk_text)
        return chunk_text

    for para in paragraphs:
        para_tokens = token_len(para)

        # Oversized paragraph — split by sentence
        if para_tokens > max_tokens:
            flush()
            current = []
            current_tokens = 0
            sentences = re.split(r"(?<=[.!?])\s+", para)
            buffer: list[str] = []
            buffer_tokens = 0
            for sent in sentences:
                s_tokens = token_len(sent)
                if buffer_tokens + s_tokens > max_tokens and buffer:
                    chunks.append(" ".join(buffer))
                    # keep last `overlap` tokens as seed
                    buffer = buffer[-1:]
                    buffer_tokens = token_len(buffer[0]) if buffer else 0
                buffer.append(sent)
                buffer_tokens += s_tokens
            if buffer:
                chunks.append(" ".join(buffer))
            continue

        # Normal case — pack paragraphs
        if current_tokens + para_tokens > max_tokens and current:
            flush()
            # overlap: carry the last paragraph forward
            overlap_text = current[-1]
            overlap_tokens = token_len(overlap_text)
            if overlap_tokens <= overlap:
                current = [overlap_text]
                current_tokens = overlap_tokens
            else:
                current = []
                current_tokens = 0

        current.append(para)
        current_tokens += para_tokens

    flush()
    return chunks


# ---------------------------------------------------------------------------
# Step 4 — Build chunks with metadata
# ---------------------------------------------------------------------------

def build_chunks(pdf_path: Path) -> list[Chunk]:
    """
    End-to-end pipeline for a single PDF: extract → annotate → chunk.

    Each chunk carries (doc, page, section) metadata so it can be cited.
    The chunk_id is a deterministic hash, which makes re-ingestion
    idempotent: same input → same id → ChromaDB upsert overwrites.
    """
    doc_name = pdf_path.name
    pages = extract_pages(pdf_path)
    annotated = annotate_sections(pages)

    chunks: list[Chunk] = []
    for page_number, section, page_text in annotated:
        if not page_text.strip():
            continue

        for i, chunk_text in enumerate(split_into_chunks(page_text, CHUNK_TOKENS, CHUNK_OVERLAP)):
            # Deterministic ID from content + location
            fingerprint = f"{doc_name}|{page_number}|{section}|{i}|{chunk_text[:200]}"
            chunk_id = hashlib.sha256(fingerprint.encode("utf-8")).hexdigest()[:24]

            chunks.append(Chunk(
                chunk_id=chunk_id,
                text=chunk_text,
                doc=doc_name,
                page=page_number,
                section=section,
            ))

    return chunks


# ---------------------------------------------------------------------------
# Step 5 — Embed chunks via OpenAI
# ---------------------------------------------------------------------------

def embed_texts(texts: list[str], batch_size: int = 64) -> list[list[float]]:
    """
    Embed a list of texts using OpenAI's embedding endpoint.

    Batching keeps requests small and reduces rate-limit risk.
    """
    embeddings: list[list[float]] = []
    for start in range(0, len(texts), batch_size):
        batch = texts[start:start + batch_size]
        response = openai_client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=batch,
        )
        embeddings.extend([item.embedding for item in response.data])
    return embeddings


# ---------------------------------------------------------------------------
# Step 6 — Store chunks in ChromaDB
# ---------------------------------------------------------------------------

def store_chunks(chunks: list[Chunk], rebuild: bool = False) -> None:
    """
    Persist chunks (text + embedding + metadata) in ChromaDB.

    If rebuild=True, the collection is deleted first (fresh start).
    Otherwise, chunks are upserted by id — re-running is safe.
    """
    if rebuild:
        try:
            chroma_client.delete_collection(COLLECTION_NAME)
            print(f"[chroma] deleted existing collection '{COLLECTION_NAME}'")
        except Exception:
            pass

    collection = chroma_client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    if not chunks:
        print("[chroma] no chunks to store")
        return

    texts = [c.text for c in chunks]
    print(f"[embed] embedding {len(texts)} chunks...")
    embeddings = embed_texts(texts)

    ids = [c.chunk_id for c in chunks]
    metadatas = [
        {
            "doc": c.doc,
            "page": c.page,
            "section": c.section or "",
        }
        for c in chunks
    ]

    collection.upsert(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas,
    )
    print(f"[chroma] stored {len(chunks)} chunks in '{COLLECTION_NAME}'")
    print(f"[chroma] collection now has {collection.count()} total chunks")


# ---------------------------------------------------------------------------
# Step 7 — CLI
# ---------------------------------------------------------------------------

def find_pdfs(docs_dir: Path, only_file: str | None) -> list[Path]:
    if not docs_dir.exists():
        print(f"[error] docs directory not found: {docs_dir}")
        sys.exit(1)

    pdfs = sorted(docs_dir.glob("*.pdf"))
    if only_file:
        pdfs = [p for p in pdfs if p.name == only_file]
    if not pdfs:
        print(f"[error] no PDFs found in {docs_dir}")
        sys.exit(1)
    return pdfs


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest PDFs into ChromaDB")
    parser.add_argument("--rebuild", action="store_true",
                        help="Delete the collection before ingesting")
    parser.add_argument("--file", type=str, default=None,
                        help="Ingest only this filename (e.g., SR11-7.pdf)")
    args = parser.parse_args()

    pdfs = find_pdfs(DOCS_DIR, args.file)
    print(f"[ingest] found {len(pdfs)} PDF(s): {[p.name for p in pdfs]}")

    all_chunks: list[Chunk] = []
    for pdf in pdfs:
        print(f"\n[ingest] processing {pdf.name}")
        chunks = build_chunks(pdf)
        print(f"[ingest] produced {len(chunks)} chunks from {pdf.name}")
        all_chunks.extend(chunks)

    store_chunks(all_chunks, rebuild=args.rebuild)


if __name__ == "__main__":
    main()