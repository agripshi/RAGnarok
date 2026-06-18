import pytest
from pathlib import Path

from app.core.locations import iter_location_files, location_to_language, location_to_office


def test_location_mappings():
    assert location_to_language("al") == "sq"
    assert location_to_language("sr") == "sr"
    assert location_to_office("al") == "albania"
    assert location_to_office("sr") == "serbia"


def test_iter_location_files(tmp_path: Path):
    al_dir = tmp_path / "al"
    sr_dir = tmp_path / "sr"
    al_dir.mkdir()
    sr_dir.mkdir()
    (al_dir / "policy.txt").write_text("albania", encoding="utf-8")
    (sr_dir / "policy.txt").write_text("serbia", encoding="utf-8")
    (tmp_path / "ignored.txt").write_text("root", encoding="utf-8")

    files = list(iter_location_files(tmp_path))
    assert len(files) == 2
    assert {loc for _, loc in files} == {"al", "sr"}


def test_iter_location_files_single_branch(tmp_path: Path):
    al_dir = tmp_path / "al"
    al_dir.mkdir()
    (al_dir / "policy.txt").write_text("albania", encoding="utf-8")

    files = list(iter_location_files(tmp_path, location="al"))
    assert len(files) == 1
    assert files[0][1] == "al"
