from __future__ import annotations

import json
import shutil
from pathlib import Path

import numpy as np

from ..geometry import world_to_camera_to_camera_to_world


def export_nerfstudio(dataset_path: str | Path, out: str | Path, copy_images: bool = True) -> Path:
    """Export a Nerfstudio-native transforms.json from UCDS.

    This avoids depending on the moving surface of trainer-side data conversion commands.
    """
    dataset_path = Path(dataset_path)
    root = dataset_path.parent
    dataset = json.loads(dataset_path.read_text(encoding="utf-8"))
    calib = json.loads((root / dataset["calibration_file"]).read_text(encoding="utf-8"))
    poses = json.loads((root / dataset["poses_file"]).read_text(encoding="utf-8"))["poses"]

    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    img_out = out / "images"
    img_out.mkdir(exist_ok=True)

    frames = []
    for pose in poses:
        qw, qx, qy, qz = pose["qvec_wxyz"]
        r = np.array([
            [1 - 2*qy*qy - 2*qz*qz, 2*qx*qy - 2*qz*qw, 2*qx*qz + 2*qy*qw],
            [2*qx*qy + 2*qz*qw, 1 - 2*qx*qx - 2*qz*qz, 2*qy*qz - 2*qx*qw],
            [2*qx*qz - 2*qy*qw, 2*qy*qz + 2*qx*qw, 1 - 2*qx*qx - 2*qy*qy],
        ], dtype=float)
        c2w = world_to_camera_to_camera_to_world(r, pose["tvec"])

        src = root / dataset["image_dir"] / pose["image_name"]
        dst_rel = Path("images") / pose["image_name"]
        dst = out / dst_rel
        if copy_images and not dst.exists():
            shutil.copy2(src, dst)

        frames.append({
            "file_path": str(dst_rel).replace("\\", "/"),
            "transform_matrix": c2w.tolist(),
            "image_id": pose["image_id"],
        })

    transforms = {
        "camera_model": "OPENCV",
        "w": calib["width"],
        "h": calib["height"],
        "fl_x": calib["fx"],
        "fl_y": calib["fy"],
        "cx": calib["cx"],
        "cy": calib["cy"],
        "k1": 0.0,
        "k2": 0.0,
        "p1": 0.0,
        "p2": 0.0,
        "frames": frames,
        "disc3d_ucds_note": "Generated directly from UCDS. Validate axis conventions visually before publication.",
    }
    (out / "transforms.json").write_text(json.dumps(transforms, indent=2), encoding="utf-8")
    return out / "transforms.json"
