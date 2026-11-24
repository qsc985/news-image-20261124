"""Run the news-image-20261124 entry (The World Today, 24 November 2026).

Reads the front-page image bundled with this repo (entry.png), checks
that it is a complete 1024x1024 PNG of at most 1 MiB, and writes an
identical copy into the directory named by MAKEFUN_OUTPUT_DIR (or
/output when unset).

Pure standard library: struct for the chunk walk, os/shutil/sys for
the file work. No network access, no image libraries, no third-party
code. The image itself is produced at build time by draw_news.py; this
script never draws anything, it only validates and copies.

Returns 0 when the copy is written, 1 when anything goes wrong.
"""

import os
import shutil
import struct
import sys
import zlib

IMAGE_NAME = "entry.png"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
MAX_IMAGE_BYTES = 1_048_576  # entry.png must be at most 1 MiB


def iter_chunks(blob):
    """Yield (type, data) for every chunk in a PNG byte string.

    Raises ValueError on a truncated header, a chunk that runs past
    the end of the data, or trailing bytes after the final chunk.
    """
    if blob[:8] != PNG_SIGNATURE:
        raise ValueError("missing PNG signature")
    offset = 8
    while offset < len(blob):
        if offset + 8 > len(blob):
            raise ValueError("truncated chunk header")
        (size,) = struct.unpack(">I", blob[offset:offset + 4])
        kind = blob[offset + 4:offset + 8]
        end = offset + 8 + size + 4  # header + payload + CRC
        if end > len(blob):
            raise ValueError(f"chunk {kind!r} runs past end of file")
        payload = blob[offset + 8:offset + 8 + size]
        (stored_crc,) = struct.unpack(">I", blob[offset + 8 + size:end])
        if stored_crc != zlib.crc32(kind + payload):
            raise ValueError(f"chunk {kind!r} fails its CRC check")
        yield kind, payload
        offset = end
    if offset != len(blob):
        raise ValueError("trailing bytes after last chunk")


def check_png(blob):
    """Return (True, '') for a complete 1024x1024 PNG of at most 1 MiB,
    else (False, reason).

    Requires the file to fit the size limit, IHDR first, IEND last, at
    least one IDAT chunk carrying image data, and an IHDR payload
    declaring the 1024x1024 front page this entry ships — not just any
    structurally valid PNG.
    """
    if len(blob) > MAX_IMAGE_BYTES:
        return False, (
            f"image is {len(blob)} bytes, over the {MAX_IMAGE_BYTES}-byte limit")
    try:
        chunks = list(iter_chunks(blob))
    except ValueError as err:
        return False, f"malformed PNG: {err}"
    if len(chunks) < 3:
        return False, "PNG has too few chunks to hold an image"
    if chunks[0][0] != b"IHDR":
        return False, "first chunk is not IHDR"
    if chunks[-1][0] != b"IEND":
        return False, "last chunk is not IEND"
    if not any(kind == b"IDAT" for kind, _ in chunks):
        return False, "PNG contains no IDAT image data"
    ihdr = chunks[0][1]
    if len(ihdr) < 13:
        return False, "IHDR payload is truncated"
    width, height = struct.unpack(">II", ihdr[:8])
    if (width, height) != (1024, 1024):
        return False, f"image is {width}x{height}, expected 1024x1024"
    bit_depth, color_type = ihdr[8], ihdr[9]
    if (bit_depth, color_type) not in ((8, 2), (8, 6)):
        return False, (
            f"unexpected IHDR bit depth {bit_depth} / colour type {color_type}, "
            "expected 8-bit RGB or RGBA")
    if ihdr[10] != 0:
        return False, f"unexpected IHDR compression method {ihdr[10]}, expected 0"
    if ihdr[11] != 0:
        return False, f"unexpected IHDR filter method {ihdr[11]}, expected 0"
    if ihdr[12] not in (0, 1):
        return False, f"unexpected IHDR interlace method {ihdr[12]}, expected 0 or 1"
    return True, ""


def run():
    base = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(base, IMAGE_NAME)
    try:
        with open(source, "rb") as handle:
            blob = handle.read()
    except OSError as err:
        print(f"error: cannot read {source}: {err}", file=sys.stderr)
        return 1
    if not blob:
        print(f"error: {source} is empty", file=sys.stderr)
        return 1
    ok, reason = check_png(blob)
    if not ok:
        print(f"error: entry.png is not a complete 1024x1024 PNG "
              f"of at most 1 MiB: {reason}",
              file=sys.stderr)
        return 1
    target_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    try:
        os.makedirs(target_dir, exist_ok=True)
        target = os.path.join(target_dir, IMAGE_NAME)
        shutil.copyfile(source, target)
        # Confirm the copy is byte-identical to the validated source.
        with open(target, "rb") as handle:
            copied = handle.read()
    except OSError as err:
        print(f"error: cannot write output: {err}", file=sys.stderr)
        return 1
    if copied != blob:
        print("error: output copy differs from entry.png", file=sys.stderr)
        return 1
    print(f"wrote {target} ({len(blob)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(run())
