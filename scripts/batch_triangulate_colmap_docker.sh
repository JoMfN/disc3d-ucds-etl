#!/usr/bin/env bash
set -euo pipefail

EXPORTS_ROOT="${1:?Usage: batch_triangulate_colmap_docker.sh EXPORTS_ROOT [LIMIT]}"
LIMIT="${2:-0}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

n=0
for DATASET_DIR in "${EXPORTS_ROOT}"/*; do
  [[ -d "${DATASET_DIR}" ]] || continue
  [[ -f "${DATASET_DIR}/dataset.json" ]] || continue

  if [[ "${LIMIT}" != "0" && "${n}" -ge "${LIMIT}" ]]; then
    break
  fi

  echo "[BATCH] $(basename "${DATASET_DIR}")"
  bash "${SCRIPT_DIR}/triangulate_colmap_docker.sh" "${DATASET_DIR}" all
  n=$((n + 1))
done
