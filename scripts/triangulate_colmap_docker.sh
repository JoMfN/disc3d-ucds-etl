#!/usr/bin/env bash
set -euo pipefail

DATASET_DIR="${1:?Usage: triangulate_colmap_docker.sh DATASET_DIR [GPU_REQUEST] [COLMAP_IMAGE]}"
GPU_REQUEST="${2:-all}"
COLMAP_IMAGE="${3:-colmap/colmap}"

DATASET_DIR="$(cd "${DATASET_DIR}" && pwd)"
EXPORTS_ROOT="$(cd "$(dirname "${DATASET_DIR}")" && pwd)"
SPECIMEN_ID="$(basename "${DATASET_DIR}")"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

test -f "${DATASET_DIR}/calibration.json"
test -d "${DATASET_DIR}/images"
test -f "${DATASET_DIR}/colmap/sparse/0/images.txt"

CAMERA_PARAMS="$(cd "${DATASET_DIR}" && python - <<'PY'
import json
from pathlib import Path
c = json.loads(Path("calibration.json").read_text())
print(f"{c['fx']},{c['fy']},{c['cx']},{c['cy']}")
PY
)"

echo "[INFO] DATASET_DIR=${DATASET_DIR}"
echo "[INFO] CAMERA_PARAMS=${CAMERA_PARAMS}"
echo "[INFO] COLMAP_IMAGE=${COLMAP_IMAGE}"

mkdir -p "${DATASET_DIR}/colmap"
rm -f "${DATASET_DIR}/colmap/database.db"

docker run --rm --gpus "${GPU_REQUEST}" \
  -e QT_QPA_PLATFORM=offscreen \
  -v "${EXPORTS_ROOT}:/data" \
  -w "/data/${SPECIMEN_ID}" \
  "${COLMAP_IMAGE}" colmap feature_extractor \
    --database_path colmap/database.db \
    --image_path images \
    --ImageReader.single_camera 1 \
    --ImageReader.camera_model PINHOLE \
    --ImageReader.camera_params "${CAMERA_PARAMS}"

docker run --rm --gpus "${GPU_REQUEST}" \
  -e QT_QPA_PLATFORM=offscreen \
  -v "${EXPORTS_ROOT}:/data" \
  -w "/data/${SPECIMEN_ID}" \
  "${COLMAP_IMAGE}" colmap exhaustive_matcher \
    --database_path colmap/database.db

python "${SCRIPT_DIR}/sync_colmap_image_ids.py" \
  --database "${DATASET_DIR}/colmap/database.db" \
  --images-txt "${DATASET_DIR}/colmap/sparse/0/images.txt"

mkdir -p "${DATASET_DIR}/colmap/sparse_triangulated/0"

docker run --rm --gpus "${GPU_REQUEST}" \
  -e QT_QPA_PLATFORM=offscreen \
  -v "${EXPORTS_ROOT}:/data" \
  -w "/data/${SPECIMEN_ID}" \
  "${COLMAP_IMAGE}" colmap point_triangulator \
    --database_path colmap/database.db \
    --image_path images \
    --input_path colmap/sparse/0 \
    --output_path colmap/sparse_triangulated/0

echo "[DONE] Triangulated COLMAP model: ${DATASET_DIR}/colmap/sparse_triangulated/0"
