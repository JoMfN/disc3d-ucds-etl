# Optional COLMAP triangulation with Docker

This step turns the pose-only UCDS COLMAP seed model into a triangulated
sparse model that Splatfacto can use for point initialization.

## Input

```text
SPECIMEN_EXPORT/
├── calibration.json
├── images/
└── colmap/sparse/0/
    ├── cameras.txt
    ├── images.txt
    └── points3D.txt
```

`points3D.txt` is initially empty by design.

## Run

```bash
bash scripts/triangulate_colmap_docker.sh \
  /path/to/disc3d_exports/SPECIMEN_ID
```

## Output

```text
colmap/sparse_triangulated/0/
```

This path can be used with:

```bash
ns-train splatfacto ... colmap \
  --colmap-path colmap/sparse_triangulated/0 \
  --masks-path masks \
  --downscale-factor 2
```
