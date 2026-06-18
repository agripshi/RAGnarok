import os
import sys
from pathlib import Path

os.environ.setdefault("VECTOR_DB", "memory")
os.environ.setdefault("LLM_MOCK_ENABLED", "true")
os.environ.setdefault("LLM_API_KEY", "")
os.environ.setdefault("TEST_MODE", "false")
os.environ.setdefault(
    "HR_DOCS_LOCAL_DIR",
    str(Path(__file__).resolve().parent / "fixtures" / "hr-docs"),
)

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
