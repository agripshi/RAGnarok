import hashlib
import json
import re
import uuid
from datetime import datetime
from pathlib import Path

SUPPORTED = {".pdf", ".docx", ".txt", ".md"}


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def detect_office(filename: str) -> str:
    lower = filename.lower()
    if any(k in lower for k in ("albania", "albanian", "tirana", "shqip")):
        return "albania"
    if any(k in lower for k in ("serbia", "belgrade", "serbian", "srb")):
        return "serbia"
    if any(k in lower for k in ("italy", "italian", "italia")):
        return "italy"
    return "unknown"


def detect_language_from_file(filename: str, text: str) -> str | None:
    lower = filename.lower()
    if "albania" in lower or "shqip" in lower:
        return "sq"
    if "italy" in lower or "italia" in lower:
        return "it"
    if "serbia" in lower or "srb" in lower:
        return "sr"
    try:
        from langdetect import detect

        return detect(text[:2000])
    except Exception:
        return None


def load_sidecar_metadata(path: Path) -> dict:
    sidecar = path.with_suffix(path.suffix + ".metadata.json")
    if sidecar.exists():
        return json.loads(sidecar.read_text(encoding="utf-8"))
    return {}


def extract_text(path: Path) -> list[tuple[str, int | None, str | None]]:
    suffix = path.suffix.lower()
    if suffix in {".txt", ".md"}:
        text = path.read_text(encoding="utf-8")
        return [(text, None, None)]
    if suffix == ".pdf":
        from pypdf import PdfReader

        reader = PdfReader(str(path))
        blocks = []
        for i, page in enumerate(reader.pages, start=1):
            t = page.extract_text() or ""
            if t.strip():
                blocks.append((t, i, None))
        return blocks
    if suffix == ".docx":
        from docx import Document

        doc = Document(str(path))
        text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        return [(text, None, None)]
    return []


def split_text(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    if len(text) <= chunk_size:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        if end >= len(text):
            break
        start = end - chunk_overlap
    return chunks
