from __future__ import annotations

import os
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable


SCAN_DIR_RE = re.compile(
    r"^(?P<timestamp>\d{8}T\d{6})__(?P<object_id>[A-Za-z0-9]+)__(?P<label>.+)__DISC3D$"
)

EDOF_DIR_RE = re.compile(r"^(?P<object_id>[A-Za-z0-9]+)__edof$", re.IGNORECASE)
CAMPOS_RE = re.compile(
    r"^(?P<timestamp>\d{8}T\d{6})__(?P<object_id>[A-Za-z0-9]+)__(?P<label>.+)__CamPos\.txt$",
    re.IGNORECASE,
)
CALIBRATED_XML_RE = re.compile(
    r"^(?P<prefix>.+)_Calibrated_Cameras_(?P<object_id>[A-Za-z0-9]+)_(?P<timestamp>\d{8}T\d{6})\.xml$",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Disc3DScan:
    specimen_id: str
    scan_dir: str
    timestamp: str
    object_id: str
    label: str
    images: str
    campos: str
    xml: str


def _iter_child_dirs(path: Path) -> Iterable[Path]:
    with os.scandir(path) as it:
        for entry in it:
            if entry.is_dir(follow_symlinks=False):
                yield Path(entry.path)


def _iter_child_files(path: Path) -> Iterable[Path]:
    with os.scandir(path) as it:
        for entry in it:
            if entry.is_file(follow_symlinks=False):
                yield Path(entry.path)


def _find_edof(scan_dir: Path, object_id: str) -> Path | None:
    exact: list[Path] = []
    fallback: list[Path] = []

    for child in _iter_child_dirs(scan_dir):
        m = EDOF_DIR_RE.match(child.name)
        if m and m.group("object_id") == object_id:
            exact.append(child)
        elif "edof" in child.name.lower():
            fallback.append(child)

    if exact:
        return sorted(exact)[0]
    if fallback:
        return sorted(fallback)[0]
    return None


def _find_campos(scan_dir: Path, timestamp: str, object_id: str) -> Path | None:
    exact: list[Path] = []
    fallback: list[Path] = []

    for child in _iter_child_files(scan_dir):
        m = CAMPOS_RE.match(child.name)
        if m and m.group("timestamp") == timestamp and m.group("object_id") == object_id:
            exact.append(child)
        elif child.name.lower().endswith("campos.txt"):
            fallback.append(child)

    if exact:
        return sorted(exact)[0]
    if fallback:
        return sorted(fallback)[0]
    return None


def _find_xml(scan_dir: Path, timestamp: str, object_id: str) -> Path | None:
    candidates: list[Path] = []

    models = scan_dir / "models"
    search_roots = [models, scan_dir] if models.exists() else [scan_dir]

    for root in search_roots:
        for child in _iter_child_files(root):
            if child.suffix.lower() != ".xml":
                continue

            m = CALIBRATED_XML_RE.match(child.name)
            if m and m.group("timestamp") == timestamp and m.group("object_id") == object_id:
                candidates.insert(0, child)
            elif "calibrated_cameras" in child.name.lower():
                candidates.append(child)
            else:
                candidates.append(child)

    return sorted(candidates)[0] if candidates else None


def discover_scans(source_root: str | Path) -> tuple[list[Disc3DScan], list[dict]]:
    """Discover DISC3D scan folders using compiled regular expressions.

    This intentionally scans only one directory level below source_root. For 961
    properly named scan folders this is faster and less error-prone than recursive
    globbing.
    """
    source_root = Path(source_root)
    scans: list[Disc3DScan] = []
    errors: list[dict] = []

    for scan_dir in sorted(_iter_child_dirs(source_root)):
        m = SCAN_DIR_RE.match(scan_dir.name)
        if not m:
            continue

        timestamp = m.group("timestamp")
        object_id = m.group("object_id")
        label = m.group("label")
        specimen_id = f"{timestamp}__{object_id}__{label}"

        images = _find_edof(scan_dir, object_id)
        campos = _find_campos(scan_dir, timestamp, object_id)
        xml = _find_xml(scan_dir, timestamp, object_id)

        missing = []
        if images is None:
            missing.append("images/*__edof")
        if campos is None:
            missing.append("*__CamPos.txt")
        if xml is None:
            missing.append("models/*Calibrated_Cameras*.xml")

        if missing:
            errors.append(
                {
                    "specimen_id": specimen_id,
                    "scan_dir": str(scan_dir),
                    "missing": missing,
                }
            )
            continue

        scans.append(
            Disc3DScan(
                specimen_id=specimen_id,
                scan_dir=str(scan_dir),
                timestamp=timestamp,
                object_id=object_id,
                label=label,
                images=str(images),
                campos=str(campos),
                xml=str(xml),
            )
        )

    return scans, errors


def scan_to_dict(scan: Disc3DScan) -> dict:
    return asdict(scan)
