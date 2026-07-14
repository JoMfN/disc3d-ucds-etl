#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import sqlite3
from pathlib import Path


def read_db_image_ids(database: Path) -> dict[str, int]:
    con = sqlite3.connect(database)
    try:
        rows = con.execute("SELECT image_id, name FROM images").fetchall()
    finally:
        con.close()
    return {name: int(image_id) for image_id, name in rows}


def sync_images_txt(images_txt: Path, database: Path) -> None:
    name_to_id = read_db_image_ids(database)

    backup = images_txt.with_suffix(images_txt.suffix + ".before_db_id_sync")
    if not backup.exists():
        shutil.copy2(images_txt, backup)

    out_lines: list[str] = []
    changed = 0
    missing = 0

    for line in images_txt.read_text(encoding="utf-8").splitlines(keepends=True):
        stripped = line.strip()

        if not stripped or stripped.startswith("#"):
            out_lines.append(line)
            continue

        parts = stripped.split()

        if len(parts) >= 10:
            name = parts[-1]
            if name in name_to_id:
                old_id = parts[0]
                new_id = str(name_to_id[name])
                if old_id != new_id:
                    changed += 1
                parts[0] = new_id
                out_lines.append(" ".join(parts) + "\n")
            else:
                missing += 1
                out_lines.append(line)
        else:
            out_lines.append(line)

    images_txt.write_text("".join(out_lines), encoding="utf-8")
    print(f"[SYNC] changed={changed}, missing_names={missing}, output={images_txt}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", required=True)
    parser.add_argument("--images-txt", required=True)
    args = parser.parse_args()

    sync_images_txt(Path(args.images_txt), Path(args.database))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
