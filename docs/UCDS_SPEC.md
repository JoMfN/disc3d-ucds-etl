# Universal Camera Dataset Specification (UCDS) v0.1

UCDS is a minimal JSON-based representation of a calibrated image set.

## Required files

```text
dataset.json
calibration.json
poses.json
metadata.json
images/
```

## dataset.json

```json
{
  "ucds_version": "0.1",
  "dataset_id": "specimen_001",
  "image_dir": "images",
  "calibration_file": "calibration.json",
  "poses_file": "poses.json",
  "metadata_file": "metadata.json"
}
```

## calibration.json

```json
{
  "camera_model": "PINHOLE",
  "width": 4096,
  "height": 3008,
  "fx": 11159.5957,
  "fy": 11159.5957,
  "cx": 2048.0,
  "cy": 1504.0,
  "distortion": null
}
```

## poses.json

Each pose stores the camera center and the world-to-camera transform.

```json
{
  "coordinate_system": "disc3d_world_mm",
  "rotation_convention": "world_to_camera",
  "poses": [
    {
      "image_name": "image_0396_70_321.2.png",
      "camera_center": [31.1189, -25.0202, 109.7064],
      "opk_degrees": [12.8474, 15.4590, 49.4490],
      "qvec_wxyz": [1, 0, 0, 0],
      "tvec": [0, 0, 0]
    }
  ]
}
```

## Coordinate note

DISC3D / photogrammetric OPK rotations and COLMAP/Nerfstudio camera
conventions are not identical. UCDS stores the original OPK values and the
derived transform. This makes conversion choices auditable.
