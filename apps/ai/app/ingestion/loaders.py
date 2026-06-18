from pathlib import Path

from langchain_community.document_loaders import Docx2txtLoader, PyPDFLoader, TextLoader
from langchain_core.document_loaders import BaseLoader

SUPPORTED = {".pdf", ".docx", ".txt", ".md"}


def get_document_loader(path: Path) -> BaseLoader:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return PyPDFLoader(str(path))
    if suffix in {".txt", ".md"}:
        return TextLoader(str(path), encoding="utf-8")
    if suffix == ".docx":
        return Docx2txtLoader(str(path))
    raise ValueError(f"Unsupported document type: {suffix}")
