# Exporters

## COLMAP TXT

```bash
disc3d-ucds export-colmap --dataset ucds/specimen/dataset.json --out exports/colmap/specimen/sparse/0
```

Writes:

```text
cameras.txt
images.txt
points3D.txt
```

## Nerfstudio transforms.json

```bash
disc3d-ucds export-nerfstudio --dataset ucds/specimen/dataset.json --out exports/nerfstudio/specimen
```

Writes:

```text
transforms.json
images/
```

This bypasses fragile trainer-side data conversion commands. It creates the
stable dataset file that `ns-train` expects when using Nerfstudio-native data.
