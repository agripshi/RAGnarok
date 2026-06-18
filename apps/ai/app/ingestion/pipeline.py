import hashlib
import json
from pathlib import Path

from app.ingestion.loaders import SUPPORTED

__all__ = [
    "SUPPORTED",
    "file_hash",
    "detect_office",
    "detect_language_from_file",
    "load_sidecar_metadata",
]


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
