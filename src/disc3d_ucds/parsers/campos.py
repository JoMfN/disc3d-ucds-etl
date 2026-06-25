from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class CamPosRecord:
    image_name: str
    x: float
    y: float
    z: float
    omega: float
    phi: float
    kappa: float
    accuracy: float | None = None


def parse_campos(path: str | Path) -> List[CamPosRecord]:
    path = Path(path)
    records: List[CamPosRecord] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 7:
            raise ValueError(f"Malformed CamPos line {line_no}: {line}")
        accuracy = float(parts[7]) if len(parts) >= 8 else None
        records.append(
            CamPosRecord(
                image_name=parts[0],
                x=float(parts[1]),
                y=float(parts[2]),
                z=float(parts[3]),
                omega=float(parts[4]),
                phi=float(parts[5]),
                kappa=float(parts[6]),
                accuracy=accuracy,
            )
        )
    if not records:
        raise ValueError(f"No camera records found in {path}")
    return records
