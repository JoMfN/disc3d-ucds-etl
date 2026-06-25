#!/usr/bin/env bash
set -euo pipefail

python -m disc3d_ucds.cli build-ucds \
  --images input/images \
  --campos input/CamPos.txt \
  --xml input/dataset.xml \
  --out ucds/specimen_001 \
  --dataset-id specimen_001
