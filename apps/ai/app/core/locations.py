from collections.abc import Iterator
from pathlib import Path
from typing import Literal

from app.ingestion.loaders import SUPPORTED

LocationCode = Literal["al", "sr"]

VALID_LOCATIONS: tuple[LocationCode, ...] = ("al", "sr")

_LOCATION_LANGUAGE: dict[LocationCode, str] = {
    "al": "sq",
    "sr": "sr",
}

_LOCATION_OFFICE: dict[LocationCode, str] = {
    "al": "albania",
    "sr": "serbia",
}


def location_to_language(location: LocationCode) -> str:
    return _LOCATION_LANGUAGE[location]


def location_to_office(location: LocationCode) -> str:
    return _LOCATION_OFFICE[location]


def iter_location_files(
    source: Path,
    location: LocationCode | None = None,
) -> Iterator[tuple[Path, LocationCode]]:
    locations: tuple[LocationCode, ...] = (location,) if location else VALID_LOCATIONS
    for loc in locations:
        loc_dir = source / loc
        if not loc_dir.is_dir():
            continue
        for path in sorted(loc_dir.iterdir()):
            if path.is_file() and path.suffix.lower() in SUPPORTED:
                yield path, loc
