from __future__ import annotations

import json
from pathlib import Path


def validate_dataset(dataset_path: str | Path) -> list[str]:
    dataset_path = Path(dataset_path)
    root = dataset_path.parent
    errors: list[str] = []
    if not dataset_path.exists():
        return [f"dataset.json does not exist: {dataset_path}"]

    dataset = json.loads(dataset_path.read_text(encoding="utf-8"))
    for key in ["calibration_file", "poses_file", "metadata_file", "image_dir"]:
        if key not in dataset:
            errors.append(f"dataset.json missing key: {key}")

    if errors:
        return errors

    image_dir = root / dataset["image_dir"]
    if not image_dir.exists():
        errors.append(f"image_dir missing: {image_dir}")

    poses_path = root / dataset["poses_file"]
    if poses_path.exists():
        poses = json.loads(poses_path.read_text(encoding="utf-8")).get("poses", [])
        for pose in poses:
            if not (image_dir / pose["image_name"]).exists():
                errors.append(f"missing image: {pose['image_name']}")
    else:
        errors.append(f"poses file missing: {poses_path}")

    return errors
