# Camera conventions

## DISC3D / photogrammetry input

`CamPos.txt` stores:

```text
X Y Z Omega Phi Kappa
```

The current implementation assumes:

- `X Y Z` are camera centers in the DISC3D object coordinate frame;
- units are millimetres unless metadata states otherwise;
- Omega, Phi, Kappa are degrees;
- OPK sequence is represented explicitly in code.

## COLMAP export

COLMAP `images.txt` expects:

```text
IMAGE_ID QW QX QY QZ TX TY TZ CAMERA_ID NAME
```

where the quaternion and translation encode a **world-to-camera** transform:

```text
x_cam = R_world_to_camera * x_world + t
t = -R_world_to_camera * C_world
```

## Nerfstudio export

Nerfstudio `transforms.json` stores camera-to-world matrices.

The exporter in this repository derives camera-to-world from the UCDS
world-to-camera pose. The exporter is intentionally separate from training
commands because Nerfstudio CLI conventions change across releases.
