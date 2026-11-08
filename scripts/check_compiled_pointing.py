#!/usr/bin/env python3
"""Check UF2 device topology against the selected Actions 42204233271 baseline.

This does not claim runtime equivalence: modified keymaps produce new binary
layouts. It detects compiled device loss or an accidental board-family switch.
"""
from __future__ import annotations

import hashlib
import struct
import sys
from pathlib import Path

MAGIC_START = (0x0A324655, 0x9E5D5157)
MAGIC_END = 0x0AB16F30
NRF52840_FAMILY = 0xADA52840
EXPECTED = {
    "left": {
        "required": (b"encoder_left_1", b"ZMK"),
        "absent": (b"encoder_left_2", b"encoder_right", b"trackball@0"),
    },
    "right": {
        "required": (b"encoder_right", b"trackball@0", b"ZMK"),
        "absent": (b"encoder_left_1", b"encoder_left_2"),
    },
}


def fail(why: str) -> None:
    raise SystemExit(f"COMPILED POINTING FAIL: {why}")


def payload_from_uf2(path: Path) -> bytes:
    data = path.read_bytes()
    if not data or len(data) % 512:
        fail(f"{path.name}: invalid UF2 length")
    parts = {}
    count = len(data) // 512
    for i in range(count):
        block = data[i * 512 : (i + 1) * 512]
        a, b, flags, address, size, number, total, family = struct.unpack_from(
            "<8I", block
        )
        end = struct.unpack_from("<I", block, 508)[0]
        if (a, b) != MAGIC_START or end != MAGIC_END:
            fail(f"{path.name}: invalid UF2 signature in block {i}")
        if family != NRF52840_FAMILY or size != 256 or number != i or total != count:
            fail(f"{path.name}: unexpected MCU, payload, or block ordering")
        if address in parts:
            fail(f"{path.name}: duplicate address {address:#x}")
        parts[address] = block[32 : 32 + size]
    return b"".join(parts[k] for k in sorted(parts))


def main() -> None:
    directory = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("firmware")
    for side, rules in EXPECTED.items():
        found = list(directory.rglob(f"charybdis_{side}-nice_nano_v2-zmk.uf2"))
        if len(found) != 1:
            fail(f"{side}: expected one nice_nano_v2 UF2, found {len(found)}")
        file = found[0]
        data = payload_from_uf2(file)
        for value in rules["required"]:
            if value not in data:
                fail(f"{side}: missing baseline device signature {value!r}")
        for value in rules["absent"]:
            if value in data:
                fail(f"{side}: unexpected device signature {value!r}")
        sha = hashlib.sha256(file.read_bytes()).hexdigest()
        print(f"COMPILED POINTING PASS: {file.name} SHA256={sha}")
    print("COMPILED POINTING PASS: both halves match baseline device topology")


if __name__ == "__main__":
    main()
