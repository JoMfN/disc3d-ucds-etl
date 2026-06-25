from __future__ import annotations

import argparse
import sys

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

    p = sub.add_parser("validate")
    p.add_argument("--dataset", required=True)

    p = sub.add_parser("export-colmap")
    p.add_argument("--dataset", required=True)
    p.add_argument("--out", required=True)

    p = sub.add_parser("export-nerfstudio")
    p.add_argument("--dataset", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--no-copy-images", action="store_true")

    args = parser.parse_args(argv)

    if args.command == "build-ucds":
        path = build_ucds(args.images, args.campos, args.xml, args.out, args.dataset_id)
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

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
