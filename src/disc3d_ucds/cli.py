from __future__ import annotations

import argparse
import json
import sys

from .batch_prepare import prepare_exports
from .build import build_ucds
from .exporters.colmap import export_colmap
from .exporters.nerfstudio import export_nerfstudio
from .validate import validate_dataset


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="disc3d-ucds")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("build-ucds")
    p.add_argument("--images", required=True)
    p.add_argument("--campos", required=True)
    p.add_argument("--xml", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--dataset-id", default=None)
    p.add_argument(
        "--image-mode",
        choices=["copy", "hardlink", "symlink", "reflink", "auto"],
        default="copy",
        help="How images are materialized in the export folder.",
    )

    p = sub.add_parser("validate")
    p.add_argument("--dataset", required=True)

    p = sub.add_parser("export-colmap")
    p.add_argument("--dataset", required=True)
    p.add_argument("--out", required=True)

    p = sub.add_parser("export-nerfstudio")
    p.add_argument("--dataset", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--no-copy-images", action="store_true")

    p = sub.add_parser("prepare-exports")
    p.add_argument("--source-root", required=True)
    p.add_argument("--export-root", required=True)
    p.add_argument("--workers", type=int, default=4)
    p.add_argument(
        "--image-mode",
        choices=["copy", "hardlink", "symlink", "reflink", "auto"],
        default="hardlink",
        help="Default is hardlink for speed and low storage use on Linux.",
    )
    p.add_argument("--overwrite", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--no-validate", action="store_true")
    p.add_argument("--limit", type=int, default=None)
    p.add_argument("--manifest", default=None, help="Optional discovered_scans.jsonl to reuse discovery results.")

    args = parser.parse_args(argv)

    if args.command == "build-ucds":
        path = build_ucds(args.images, args.campos, args.xml, args.out, args.dataset_id, image_mode=args.image_mode)
        print(path)
        return 0

    if args.command == "validate":
        errors = validate_dataset(args.dataset)
        if errors:
            for e in errors:
                print(f"ERROR: {e}", file=sys.stderr)
            return 1
        print("Dataset validation passed.")
        return 0

    if args.command == "export-colmap":
        print(export_colmap(args.dataset, args.out))
        return 0

    if args.command == "export-nerfstudio":
        print(export_nerfstudio(args.dataset, args.out, copy_images=not args.no_copy_images))
        return 0

    if args.command == "prepare-exports":
        summary = prepare_exports(
            source_root=args.source_root,
            export_root=args.export_root,
            workers=args.workers,
            image_mode=args.image_mode,
            overwrite=args.overwrite,
            dry_run=args.dry_run,
            validate=not args.no_validate,
            limit=args.limit,
            manifest_path=args.manifest,
        )
        print(json.dumps(summary, indent=2))
        return 0 if summary.get("failed", 0) == 0 else 1

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
