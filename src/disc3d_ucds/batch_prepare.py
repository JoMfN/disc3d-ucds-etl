from __future__ import annotations

import csv
import json
import os
import shutil
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict
from pathlib import Path

from .build import build_ucds
from .discovery import Disc3DScan, discover_scans, scan_to_dict
from .exporters.colmap import export_colmap
from .exporters.nerfstudio import export_nerfstudio
from .validate import validate_dataset


def _safe_unlink(path: Path) -> None:
    if path.is_symlink() or path.exists():
        path.unlink()


def _relative_symlink(src: Path, dst: Path) -> None:
    _safe_unlink(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    rel = os.path.relpath(src, start=dst.parent)
    dst.symlink_to(rel)


def _prepare_one(payload: dict) -> dict:
    scan = Disc3DScan(**payload["scan"])
    export_root = Path(payload["export_root"])
    image_mode = payload["image_mode"]
    overwrite = payload["overwrite"]
    validate = payload["validate"]

    out_dir = export_root / scan.specimen_id
    started = time.time()

    if out_dir.exists() and overwrite:
        shutil.rmtree(out_dir)

    if (out_dir / "dataset.json").exists() and not overwrite:
        return {
            "specimen_id": scan.specimen_id,
            "status": "skipped",
            "out_dir": str(out_dir),
            "seconds": 0.0,
            "message": "dataset.json already exists",
        }

    out_dir.mkdir(parents=True, exist_ok=True)

    dataset_path = build_ucds(
        images=scan.images,
        campos=scan.campos,
        xml=scan.xml,
        out=out_dir,
        dataset_id=scan.specimen_id,
        image_mode=image_mode,
    )

    if validate:
        errors = validate_dataset(dataset_path)
        if errors:
            raise RuntimeError(f"Validation failed for {scan.specimen_id}: {errors}")

    export_colmap(dataset_path, out_dir / "colmap" / "sparse" / "0")
    export_nerfstudio(dataset_path, out_dir, copy_images=False)

    ns_dir = out_dir / "nerfstudio"
    ns_dir.mkdir(exist_ok=True)
    _relative_symlink(out_dir / "transforms.json", ns_dir / "transforms.json")
    _relative_symlink(out_dir / "images", ns_dir / "images")

    elapsed = time.time() - started
    return {
        "specimen_id": scan.specimen_id,
        "status": "ok",
        "out_dir": str(out_dir),
        "seconds": elapsed,
        "message": "",
    }


def write_manifest(scans: list[Disc3DScan], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for scan in scans:
            f.write(json.dumps(scan_to_dict(scan), ensure_ascii=False) + "\n")


def write_discovery_errors(errors: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for error in errors:
            f.write(json.dumps(error, ensure_ascii=False) + "\n")


def read_manifest(path: Path) -> list[Disc3DScan]:
    scans: list[Disc3DScan] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            scans.append(Disc3DScan(**json.loads(line)))
    return scans


def write_report(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["specimen_id", "status", "out_dir", "seconds", "message"]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def prepare_exports(
    source_root: str | Path,
    export_root: str | Path,
    workers: int = 4,
    image_mode: str = "hardlink",
    overwrite: bool = False,
    dry_run: bool = False,
    validate: bool = True,
    limit: int | None = None,
    manifest_path: str | Path | None = None,
) -> dict:
    source_root = Path(source_root)
    export_root = Path(export_root)
    logs = export_root / "_logs"
    logs.mkdir(parents=True, exist_ok=True)

    if manifest_path:
        scans = read_manifest(Path(manifest_path))
        errors = []
    else:
        scans, errors = discover_scans(source_root)
        write_manifest(scans, logs / "discovered_scans.jsonl")
        write_discovery_errors(errors, logs / "discovery_errors.jsonl")

    if limit is not None:
        scans = scans[:limit]

    if dry_run:
        return {
            "source_root": str(source_root),
            "export_root": str(export_root),
            "discovered": len(scans),
            "discovery_errors": len(errors),
            "workers": workers,
            "image_mode": image_mode,
            "dry_run": True,
            "manifest": str(logs / "discovered_scans.jsonl"),
            "errors": str(logs / "discovery_errors.jsonl"),
        }

    payloads = [
        {
            "scan": asdict(scan),
            "export_root": str(export_root),
            "image_mode": image_mode,
            "overwrite": overwrite,
            "validate": validate,
        }
        for scan in scans
    ]

    rows: list[dict] = []
    workers = max(1, int(workers))

    if workers == 1:
        for payload in payloads:
            try:
                rows.append(_prepare_one(payload))
            except Exception as exc:
                scan = payload["scan"]
                rows.append(
                    {
                        "specimen_id": scan["specimen_id"],
                        "status": "failed",
                        "out_dir": str(export_root / scan["specimen_id"]),
                        "seconds": 0.0,
                        "message": repr(exc),
                    }
                )
    else:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            futures = [pool.submit(_prepare_one, payload) for payload in payloads]
            for fut in as_completed(futures):
                try:
                    rows.append(fut.result())
                except Exception as exc:
                    rows.append(
                        {
                            "specimen_id": "UNKNOWN",
                            "status": "failed",
                            "out_dir": "",
                            "seconds": 0.0,
                            "message": repr(exc),
                        }
                    )

    rows.sort(key=lambda r: r.get("specimen_id", ""))
    report = logs / "prepare_exports_report.csv"
    write_report(rows, report)

    return {
        "source_root": str(source_root),
        "export_root": str(export_root),
        "discovered": len(scans),
        "discovery_errors": len(errors),
        "ok": sum(1 for r in rows if r["status"] == "ok"),
        "skipped": sum(1 for r in rows if r["status"] == "skipped"),
        "failed": sum(1 for r in rows if r["status"] == "failed"),
        "workers": workers,
        "image_mode": image_mode,
        "dry_run": False,
        "report": str(report),
        "manifest": str(logs / "discovered_scans.jsonl"),
        "errors": str(logs / "discovery_errors.jsonl"),
    }
