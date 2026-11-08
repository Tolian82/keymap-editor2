#!/usr/bin/env python3
"""Fail-closed UF2 binary check for the user's proven-working v1 wheel topology.

This verifies compiled hardware-device and pointing-processor fingerprints.
It CANNOT prove runtime behavior or physical keyboard compatibility.
"""
from __future__ import annotations

import hashlib
import struct
import sys
from pathlib import Path

START0 = 0x0A324655
START1 = 0x9E5D5157
END = 0x0AB16F30
FAMILY_NRF52840 = 0xADA52840


def fail(message: str) -> None:
    raise SystemExit(f"V1 UF2 TOPOLOGY FAIL: {message}")


def parse(path: Path) -> bytes:
    data = path.read_bytes()
    if len(data) % 512:
        fail(f"{path.name}: not a multiple of 512 bytes")
    blocks: dict[int, bytes] = {}
    count = len(data) // 512
    for i in range(count):
        block = data[i * 512 : (i + 1) * 512]
        magic0, magic1, flags, addr, size, number, total, family = struct.unpack_from("<8I", block)
        tail = struct.unpack_from("<I", block, 508)[0]
        if (magic0, magic1, tail) != (START0, START1, END):
            fail(f"{path.name}: invalid UF2 magic in block {i}")
        if size != 256 or number != i or total != count:
            fail(f"{path.name}: malformed UF2 block {i}")
        if family != FAMILY_NRF52840:
            fail(f"{path.name}: wrong MCU family 0x{family:08X}")
        if addr in blocks:
            fail(f"{path.name}: duplicate UF2 address 0x{addr:X}")
        blocks[addr] = block[32:32 + size]
    return b"".join(blocks[addr] for addr in sorted(blocks))


def main() -> None:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("firmware")
    halves = {}
    for side in ("left", "right"):
        paths = list(root.rglob(f"charybdis_{side}*.uf2"))
        if len(paths) != 1:
            fail(f"expected exactly one {side} UF2 under {root}, got {len(paths)}")
        halves[side] = (paths[0], parse(paths[0]))
    for side in ("left", "right"):
        path, payload = halves[side]
        required = (
            (b"encoder_left_1", b"encoder_left_2", b"zip_xy_scaler", b"zip_scroll_scaler")
            if side == "left" else
            (b"trackball@0", b"scroll_vertical_encoder", b"scroll_horizontal_encoder",
             b"zip_xy_scaler", b"zip_scroll_scaler")
        )
        absent = (
            (b"encoder_right", b"trackball@0")
            if side == "left" else
            (b"encoder_right", b"encoder_left_1", b"encoder_left_2")
        )
        for anchor in required:
            if anchor not in payload:
                fail(f"{path.name}: missing {anchor.decode()} found in working v1")
        for anchor in absent:
            if anchor in payload:
                fail(f"{path.name}: unexpected device {anchor.decode()} absent from working v1")
        print(f"V1 UF2 TOPOLOGY PASS: {path.name}, size={path.stat().st_size}, "
              f"SHA256={hashlib.sha256(path.read_bytes()).hexdigest()}")
    print("V1 UF2 fingerprint PASS: both wheel channels on LEFT; PMW3610 only on RIGHT; pointing scalers present")


if __name__ == "__main__":
    main()
