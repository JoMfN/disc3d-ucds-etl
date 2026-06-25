#!/usr/bin/env bash
set -euo pipefail

python -m disc3d_ucds.cli export-nerfstudio \
  --dataset ucds/specimen_001/dataset.json \
  --out exports/nerfstudio/specimen_001
