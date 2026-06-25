#!/usr/bin/env bash
set -euo pipefail

python -m disc3d_ucds.cli export-colmap \
  --dataset ucds/specimen_001/dataset.json \
  --out exports/colmap/specimen_001/sparse/0
