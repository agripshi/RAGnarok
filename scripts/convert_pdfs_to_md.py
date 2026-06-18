#!/usr/bin/env python3
"""
PDF → Markdown pre-processing script.

For each PDF in data/hr-docs/al/ and data/hr-docs/sr/:
  - If text-based: extract via pymupdf4llm → save as <name>.md
  - If scanned (< MIN_CHARS threshold): OCR each page via OpenAI vision → save as <name>.md

Existing .md files are skipped unless --force is passed.

Usage:
    python scripts/convert_pdfs_to_md.py
    python scripts/convert_pdfs_to_md.py --force
    python scripts/convert_pdfs_to_md.py --location al
"""

import argparse
import base64
import os
import sys
from pathlib import Path

# Min chars per page to consider a PDF text-based (not scanned)
MIN_CHARS_PER_PAGE = 50

REPO_ROOT = Path(__file__).parent.parent
DOCS_ROOT = REPO_ROOT / "data" / "hr-docs"
LOCATIONS = ["al", "sr"]


def is_scanned(pdf_path: Path) -> bool:
    import fitz  # PyMuPDF

    doc = fitz.open(str(pdf_path))
    total_chars = sum(len(page.get_text().strip()) for page in doc)
    avg = total_chars / max(len(doc), 1)
    return avg < MIN_CHARS_PER_PAGE


def convert_text_pdf(pdf_path: Path) -> str:
    import pymupdf4llm

    md = pymupdf4llm.to_markdown(str(pdf_path))
    # Strip pymupdf4llm image markers — keep only text
    lines = [l for l in md.splitlines() if "intentionally omitted" not in l]
    return "\n".join(lines).strip()


def convert_scanned_pdf(pdf_path: Path, api_key: str) -> str:
    """OCR scanned PDF pages using OpenAI vision (gpt-4o)."""
    import fitz
    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    doc = fitz.open(str(pdf_path))
    pages_md = []

    print(f"    Scanned PDF — OCR via OpenAI vision ({len(doc)} pages)...")

    for i, page in enumerate(doc):
        # Render page to PNG at 150 DPI
        mat = fitz.Matrix(150 / 72, 150 / 72)
        pix = page.get_pixmap(matrix=mat)
        img_bytes = pix.tobytes("png")
        b64 = base64.b64encode(img_bytes).decode()

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "Extract all text from this HR document page. "
                                "Preserve headings, bullet points, tables, and structure as Markdown. "
                                "Output only the extracted text, no commentary."
                            ),
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{b64}", "detail": "high"},
                        },
                    ],
                }
            ],
            max_tokens=4096,
        )
        page_text = response.choices[0].message.content or ""
        pages_md.append(f"<!-- Page {i + 1} -->\n{page_text}")
        print(f"    Page {i + 1}/{len(doc)} done")

    return "\n\n".join(pages_md)


def process_location(location: str, force: bool, api_key: str) -> None:
    loc_dir = DOCS_ROOT / location
    if not loc_dir.exists():
        print(f"[SKIP] {loc_dir} does not exist")
        return

    pdfs = sorted(loc_dir.glob("*.pdf"))
    print(f"\n=== {location.upper()} — {len(pdfs)} PDFs ===")

    for pdf in pdfs:
        md_path = pdf.with_suffix(".md")
        if md_path.exists() and not force:
            print(f"  [SKIP] {pdf.name} (already converted)")
            continue

        print(f"  [{location}] {pdf.name}")
        try:
            if is_scanned(pdf):
                if not api_key:
                    print(f"    ⚠️  Scanned PDF — no API key, skipping")
                    continue
                md_text = convert_scanned_pdf(pdf, api_key)
            else:
                md_text = convert_text_pdf(pdf)

            if not md_text.strip():
                print(f"    ⚠️  Empty output — skipping")
                continue

            md_path.write_text(md_text, encoding="utf-8")
            print(f"    ✅ Saved → {md_path.name} ({len(md_text)} chars)")

        except Exception as e:
            print(f"    ❌ ERROR: {e}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert HR PDFs to Markdown")
    parser.add_argument("--force", action="store_true", help="Re-convert even if .md exists")
    parser.add_argument("--location", choices=["al", "sr"], help="Process one location only")
    args = parser.parse_args()

    # Load API key from apps/ai/.env
    env_path = REPO_ROOT / "apps" / "ai" / ".env"
    api_key = ""
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if line.startswith("LLM_API_KEY="):
                api_key = line.split("=", 1)[1].strip()
                break

    if not api_key:
        api_key = os.environ.get("OPENAI_API_KEY", "")

    if not api_key:
        print("⚠️  No API key found — scanned PDFs will be skipped")

    locations = [args.location] if args.location else LOCATIONS
    for loc in locations:
        process_location(loc, args.force, api_key)

    print("\n✅ Done. Re-run ingest after conversion to embed the .md files.")


if __name__ == "__main__":
    main()
