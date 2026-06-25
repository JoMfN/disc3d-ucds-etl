from __future__ import annotations

import json
from pathlib import Path


def export_colmap(dataset_path: str | Path, out: str | Path) -> Path:
    dataset_path = Path(dataset_path)
    root = dataset_path.parent
    dataset = json.loads(dataset_path.read_text(encoding="utf-8"))
    calib = json.loads((root / dataset["calibration_file"]).read_text(encoding="utf-8"))
    poses = json.loads((root / dataset["poses_file"]).read_text(encoding="utf-8"))["poses"]

    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)

    with (out / "cameras.txt").open("w", encoding="utf-8") as f:
        f.write("# CAMERA_ID MODEL WIDTH HEIGHT PARAMS[]\n")
        f.write(f"1 PINHOLE {calib['width']} {calib['height']} {calib['fx']} {calib['fy']} {calib['cx']} {calib['cy']}\n")

    with (out / "images.txt").open("w", encoding="utf-8") as f:
        f.write("# IMAGE_ID QW QX QY QZ TX TY TZ CAMERA_ID NAME\n")
        f.write("# POINTS2D[] as (X Y POINT3D_ID)\n")
        for pose in poses:
            qw, qx, qy, qz = pose["qvec_wxyz"]
            tx, ty, tz = pose["tvec"]
            f.write(f"{pose['image_id']} {qw} {qx} {qy} {qz} {tx} {ty} {tz} 1 {pose['image_name']}\n\n")

    with (out / "points3D.txt").open("w", encoding="utf-8") as f:
        f.write("# Empty by design. Some trainers can initialize without sparse 3D points.\n")

    return out
