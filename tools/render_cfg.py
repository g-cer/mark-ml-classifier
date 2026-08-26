"""Render the white-box Control Flow Graphs to vector PDF and raster PNG.

The CFGs under ``test/white_box_paths`` were produced by an AST-based script
during the white-box test design (see the Master Test Plan). Only a few of them
were ever rendered, and the documentation embedded low-resolution screenshots.

This script re-renders every ``.dot`` source with Graphviz so the documents can
embed sharp vector figures instead.

Usage:
    python tools/render_cfg.py [--outdir docs/latex/figures/cfg]
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

SOURCE_DIR = Path("test/white_box_paths")
DEFAULT_OUTDIR = Path("docs/latex/figures/cfg")
FORMATS = ("pdf", "png")


def render(dot_file: Path, outdir: Path) -> list[Path]:
    """Render a single .dot file to every configured output format."""
    stem = f"{dot_file.parent.name}-{dot_file.stem}".replace("_", "-").lstrip("-")
    produced = []

    for fmt in FORMATS:
        target = outdir / f"{stem}.{fmt}"
        cmd = ["dot", f"-T{fmt}", str(dot_file), "-o", str(target)]
        if fmt == "png":
            cmd.insert(1, "-Gdpi=200")
        subprocess.run(cmd, check=True)
        produced.append(target)

    return produced


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outdir", type=Path, default=DEFAULT_OUTDIR)
    parser.add_argument("--source", type=Path, default=SOURCE_DIR)
    args = parser.parse_args()

    if shutil.which("dot") is None:
        print("Graphviz 'dot' not found on PATH. Install it from graphviz.org.",
              file=sys.stderr)
        return 1

    dot_files = sorted(args.source.rglob("*.dot"))
    if not dot_files:
        print(f"No .dot files found under {args.source}", file=sys.stderr)
        return 1

    args.outdir.mkdir(parents=True, exist_ok=True)

    for dot_file in dot_files:
        for target in render(dot_file, args.outdir):
            print(f"{dot_file.as_posix()} -> {target.as_posix()}")

    print(f"\n{len(dot_files)} CFG(s) rendered into {args.outdir.as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
