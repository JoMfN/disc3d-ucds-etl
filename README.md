# disc3d-ucds-etl

**DISC3D → Universal Camera Dataset Specification (UCDS)**

This repository is the stable part of the workflow. It does **not** train Gaussian
Splatting models. It converts DISC3D / Metashape acquisition metadata into a
small, explicit, versioned camera-dataset representation and exports that
representation to downstream formats.

The purpose is to keep museum/scientific acquisition metadata independent from
rapidly changing Gaussian Splatting and NeRF training frameworks.

## Core idea

```text
DISC3D images + CamPos.txt + Metashape XML
        │
        ▼
Universal Camera Dataset Specification
        │
        ├── export COLMAP TXT
        ├── export Nerfstudio transforms.json
        ├── export trainer-specific manifests
        └── validate camera/image consistency
```

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .

python -m disc3d_ucds.cli build-ucds \
  --images input/images \
  --campos input/CamPos.txt \
  --xml input/dataset.xml \
  --out ucds/specimen_001

python -m disc3d_ucds.cli validate \
  --dataset ucds/specimen_001/dataset.json

python -m disc3d_ucds.cli export-colmap \
  --dataset ucds/specimen_001/dataset.json \
  --out exports/colmap/specimen_001/sparse/0

python -m disc3d_ucds.cli export-nerfstudio \
  --dataset ucds/specimen_001/dataset.json \
  --out exports/nerfstudio/specimen_001
```

## Repository boundaries

This repository owns:

- parsing `CamPos.txt`;
- parsing Metashape camera calibration XML;
- converting OPK rotations into explicit camera matrices;
- validating image names and camera records;
- exporting stable interchange formats.

This repository does **not** own:

- Gaussian Splatting optimization;
- Nerfstudio CLI compatibility;
- renderer-specific hyperparameters;
- mesh reconstruction;
- benchmarking across external trainers.

Those responsibilities belong in the companion repository:

```text
disc3d-gs-experiments
```

## Input format assumption

`CamPos.txt` is expected to have columns:

```text
#Label X Y Z Omega Phi Kappa Accuracy
image_0001_-70_0.png 39.9299 0.0000 -109.7064 ...
```

The image filename must match a file in the image directory.

## Output layout

```text
ucds/specimen_001/
├── dataset.json
├── calibration.json
├── poses.json
├── metadata.json
└── images/
```

## Why UCDS?

The GS ecosystem changes quickly. Trainer CLIs and expected folder layouts can
change from release to release. Camera acquisition metadata from DISC3D should
not be rewritten every time a training package changes.

UCDS keeps the invariant part stable:

```text
image identity + intrinsics + extrinsics + acquisition metadata
```

Everything else is an exporter.
