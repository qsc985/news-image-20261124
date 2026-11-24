#!/usr/bin/env python3
"""Verify and publish the news-image entry.

Checks that ``entry.png`` sitting next to this file is a genuine,
uncorrupted PNG of exactly 1024x1024 pixels and at most 1 MiB, then
copies it to ``$MAKEFUN_OUTPUT_DIR`` (default ``/output``) as
``entry.png``.

Exit status: 0 on success, 1 on any verification or copy failure.
"""

from __future__ import annotations

import hashlib
import os
import shutil
import struct
import sys
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
ENTRY_NAME = "entry.png"
EXPECTED_WIDTH = 1024
EXPECTED_HEIGHT = 1024
MAX_BYTES = 1024 * 1024  # 1 MiB
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def sha256_of(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def check_png(path: str) -> None:
    """Raise ValueError unless *path* is a valid 1024x1024 PNG."""
    with open(path, "rb") as handle:
        data = handle.read()

    if len(data) > MAX_BYTES:
        raise ValueError(
            f"{path} is {len(data)} bytes, over the {MAX_BYTES} byte limit")
    if not data.startswith(PNG_SIGNATURE):
        raise ValueError(f"{path} does not start with the PNG signature")

    offset = len(PNG_SIGNATURE)
    width = height = None
    idat = bytearray()
    while offset < len(data):
        if offset + 8 > len(data):
            raise ValueError(f"{path} ends mid-chunk header")
        length, chunk_type = struct.unpack(">I4s", data[offset:offset + 8])
        body_start = offset + 8
        body_end = body_start + length
        if body_end + 4 > len(data):
            raise ValueError(f"{path} ends mid-chunk {chunk_type!r}")
        body = data[body_start:body_end]
        stored_crc = struct.unpack(">I", data[body_end:body_end + 4])[0]
        actual_crc = zlib.crc32(chunk_type + body) & 0xFFFFFFFF
        if stored_crc != actual_crc:
            raise ValueError(
                f"{path} chunk {chunk_type!r} has a bad CRC")
        if chunk_type == b"IHDR":
            width, height = struct.unpack(">II", body[:8])
        elif chunk_type == b"IDAT":
            idat.extend(body)
        elif chunk_type == b"IEND":
            break
        offset = body_end + 4

    if width is None or height is None:
        raise ValueError(f"{path} has no IHDR chunk")
    if (width, height) != (EXPECTED_WIDTH, EXPECTED_HEIGHT):
        raise ValueError(
            f"{path} is {width}x{height}, expected "
            f"{EXPECTED_WIDTH}x{EXPECTED_HEIGHT}")
    # Decompressing the image data proves the pixel stream is intact.
    zlib.decompress(bytes(idat))


def main() -> int:
    source = os.path.join(HERE, ENTRY_NAME)
    output_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    target = os.path.join(output_dir, ENTRY_NAME)

    if not os.path.isfile(source):
        print(f"error: {source} not found", file=sys.stderr)
        return 1
    try:
        check_png(source)
    except (OSError, ValueError, zlib.error) as exc:
        print(f"error: {source} failed verification: {exc}", file=sys.stderr)
        return 1

    try:
        os.makedirs(output_dir, exist_ok=True)
        shutil.copyfile(source, target)
        if sha256_of(source) != sha256_of(target):
            print(f"error: copy to {target} does not match {source}",
                  file=sys.stderr)
            return 1
    except OSError as exc:
        print(f"error: could not copy to {target}: {exc}", file=sys.stderr)
        return 1

    size = os.path.getsize(target)
    print(f"ok: {target} ({size} bytes, "
          f"{EXPECTED_WIDTH}x{EXPECTED_HEIGHT})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
