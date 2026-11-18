#!/usr/bin/env python3
"""Publish this repository's front page where the bounty's judge reads it.

The page is a committed asset, `entry.png`, sitting beside this program. The
program checks it against the bounty's limits and copies it to /output/entry.png.
It reads nothing else and touches no network, so two runs write identical bytes.
"""

from __future__ import annotations

import hashlib
import os
import shutil
import struct
import sys
from pathlib import Path

ASSET = "entry.png"
OUTPUT_ENV = "ENTRY_OUTPUT_DIR"
DEFAULT_OUTPUT = "/output"
BYTE_CAP = 1_048_576
SIDE_CAP = 1024
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
IHDR = b"IHDR"


class GateError(RuntimeError):
    """The asset would be refused by the scorer's gate."""


def png_extent(data: bytes) -> tuple[int, int]:
    """Width and height from the IHDR chunk that follows the signature."""
    if not data.startswith(PNG_SIGNATURE):
        raise GateError("entry.png is not a PNG by its first bytes")
    if data[12:16] != IHDR:
        raise GateError("the PNG's first chunk is not IHDR")
    width, height = struct.unpack(">II", data[16:24])
    return width, height


def gate(path: Path) -> tuple[int, int, str]:
    """Refuse what the gate refuses, and report size and digest for the log."""
    if not path.is_file():
        raise GateError(f"{path} is missing")
    data = path.read_bytes()
    if len(data) > BYTE_CAP:
        raise GateError(f"{len(data)} bytes is over the {BYTE_CAP}-byte cap")
    if len(data) < 33:
        raise GateError("the file is shorter than a PNG header")
    width, height = png_extent(data)
    if width > SIDE_CAP or height > SIDE_CAP:
        raise GateError(f"{width}x{height} is over the {SIDE_CAP}px cap")
    return width, height, hashlib.sha256(data).hexdigest()


def publish(asset: Path, out_dir: Path) -> Path:
    """Copy the asset to the output path and prove the bytes arrived intact."""
    out_dir.mkdir(parents=True, exist_ok=True)
    dest = out_dir / ASSET
    shutil.copyfile(asset, dest)
    if hashlib.sha256(dest.read_bytes()).digest() != hashlib.sha256(asset.read_bytes()).digest():
        raise IOError(f"{dest} does not match the committed asset")
    return dest


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    here = Path(__file__).resolve().parent
    asset = here / ASSET
    out_dir = Path(argv[0]) if argv else Path(os.environ.get(OUTPUT_ENV, DEFAULT_OUTPUT))
    width, height, digest = gate(asset)
    dest = publish(asset, out_dir)
    print(f"{dest}: {width}x{height}, {asset.stat().st_size} bytes, sha256 {digest[:16]}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except GateError as exc:
        print(f"refused: {exc}", file=sys.stderr)
        raise SystemExit(2)