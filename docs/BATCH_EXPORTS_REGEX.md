# Batch export preparation with regex discovery

This module prepares one standardized training/export folder per DISC3D scan.
It is intended for large batches such as hundreds of museum specimens.

## Source naming convention

The discovery layer expects scan folders matching:

```text
YYYYMMDDTHHMMSS__OBJECTID__Taxon_name__DISC3D
```

Example:

```text
20250430T104842__06778f__Carabus_violaceus_meyeri__DISC3D
```

Inside each scan folder it searches only one level deep and uses compiled
regular expressions for:

```text
OBJECTID__edof/
YYYYMMDDTHHMMSS__OBJECTID__Taxon_name__CamPos.txt
models/*_Calibrated_Cameras_OBJECTID_YYYYMMDDTHHMMSS.xml
```

This is deliberately faster and more deterministic than recursive globbing.

## Target export layout

Each specimen becomes:

```text
exports/
└── YYYYMMDDTHHMMSS__OBJECTID__Taxon_name/
    ├── calibration.json
    ├── dataset.json
    ├── metadata.json
    ├── poses.json
    ├── transforms.json
    ├── images/
    ├── colmap/
    │   └── sparse/
    │       └── 0/
    │           ├── cameras.txt
    │           ├── images.txt
    │           └── points3D.txt
    └── nerfstudio/
        ├── transforms.json -> ../transforms.json
        └── images -> ../images
```

## Dry run

```bash
python -m disc3d_ucds.cli prepare-exports \
  --source-root ../MetashapeDisc3D \
  --export-root ../exports \
  --workers 4 \
  --image-mode hardlink \
  --dry-run
```

This writes:

```text
exports/_logs/discovered_scans.jsonl
exports/_logs/discovery_errors.jsonl
```

## Full run

```bash
python -m disc3d_ucds.cli prepare-exports \
  --source-root ../MetashapeDisc3D \
  --export-root ../exports \
  --workers 4 \
  --image-mode hardlink
```

## Image materialization modes

`--image-mode hardlink` is the recommended Linux default when the source and
export folders live on the same filesystem. It avoids copying 396 images per
specimen and can reduce preparation time and storage use drastically.

Available modes:

- `hardlink`: fastest portable-on-same-filesystem option.
- `symlink`: fastest overall, but depends on source folders remaining in place.
- `reflink`: copy-on-write clone on supported filesystems.
- `copy`: slow but self-contained.
- `auto`: hardlink, then reflink, then copy.

## Incremental processing

Existing exports are skipped when `dataset.json` already exists. Use
`--overwrite` only when rebuilding intentionally.

## Recommended scaling

For 961 scans, run export preparation with moderate parallelism. Most time is
filesystem I/O, not CPU computation.

```bash
python -m disc3d_ucds.cli prepare-exports \
  --source-root /data/MetashapeDisc3D \
  --export-root /data/disc3d_exports \
  --workers 8 \
  --image-mode hardlink
```

Start with `--workers 4` on shared storage and increase only if I/O remains
responsive.
