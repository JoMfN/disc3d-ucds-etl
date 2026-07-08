#!/usr/bin/env bash
set -euo pipefail

SOURCE_ROOT="${1:?Usage: bash scripts/04_prepare_exports_regex.sh /path/to/MetashapeDisc3D /path/to/exports [workers]}"
EXPORT_ROOT="${2:?Usage: bash scripts/04_prepare_exports_regex.sh /path/to/MetashapeDisc3D /path/to/exports [workers]}"
WORKERS="${3:-4}"
IMAGE_MODE="${IMAGE_MODE:-hardlink}"

python -m disc3d_ucds.cli prepare-exports \
  --source-root "${SOURCE_ROOT}" \
  --export-root "${EXPORT_ROOT}" \
  --workers "${WORKERS}" \
  --image-mode "${IMAGE_MODE}"
