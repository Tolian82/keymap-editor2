#!/usr/bin/env python3
"""Guard critical Charybdis ZMK behavior while allowing keymap-editor key changes.

This checks repository consistency only; it is NOT proof of equivalence to vendor UF2.
"""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# SHA-1 values are Git *blob* object IDs (integrity regression guard, not a
# cryptographic authenticity check). Update deliberately for hardware upgrades.
LOCKED_GIT_BLOBS = {
    "build.yaml": "1b86acfe7d93a3f6726d1ca7cb88d52898682748",
    "config/west.yml": "631514f256504442bbdb3f761d522f53b64300a6",
    "config/charybdis.conf": "f58dcd9e855b7d81a6121e67fb6cc92e71423412",
    "config/charybdis.json": "d31b2966b4481cc7c20bfcbd83308efa77e5ae30",
    "config/boards/shields/charybdis/Kconfig.defconfig": "851ad1e92d01d87610509949e16fbb640ef7a812",
    "config/boards/shields/charybdis/Kconfig.shield": "16a7b54e6400a40ad199c64c29e8bfd6933db762",
    "config/boards/shields/charybdis/charybdis.conf": "e69de29bb2d1d6434b8b29ae775ad8c2e48c5391",
    "config/boards/shields/charybdis/charybdis.dtsi": "32ac7e2c0d72209ed9041aefeb305c4cbfbf56ee",
    "config/boards/shields/charybdis/charybdis.zmk.yml": "3c0e29bc341925ea10aae4a58ab79fae04fe0573",
    "config/boards/shields/charybdis/charybdis_left.conf": "e397e04fda6f28a70960ebf7824c0603746160f2",
    "config/boards/shields/charybdis/charybdis_left.overlay": "2f011d99e263e7d8986cede0377334270c6a0aa0",
    "config/boards/shields/charybdis/charybdis_right.conf": "c36ca9da1b6524cb4eb3fd9c7d3922f28113eb43",
    "config/boards/shields/charybdis/charybdis_right.overlay": "b5a1e8f6327d0f3e4cecac94d778c5aef3cdcfc2"
}

def git_blob_id(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()

def uncomment(content: str) -> str:
    return re.sub(r"/\*.*?\*/|//[^\n]*", "", content, flags=re.S)

def fail(reason: str) -> None:
    print(f"POINTING GUARD FAIL: {reason}", file=sys.stderr)
    raise SystemExit(1)

def main() -> None:
    for path, expected in LOCKED_GIT_BLOBS.items():
        file = ROOT / path
        if not file.is_file():
            fail(f"missing protected file: {path}")
        got = git_blob_id(file.read_bytes())
        if got != expected:
            fail(f"protected configuration modified: {path} (expected {expected}, got {got}); restore or review the intentional hardware change")

    text = uncomment((ROOT / "config/charybdis.keymap").read_text())
    layers = dict(re.findall(r"(?ms)^\s*layer_(\d+)\s*\{(.*?)^\s*\};", text))
    if not {"0", "1", "2"}.issubset(layers):
        fail("missing or reordered core layers 0/1/2")
    expected = {
        "0": ["&scroll_vertical_encoder", "&scroll_vertical_encoder"],
        "1": ["&scroll_vertical_encoder", "&scroll_horizontal_encoder"],
        "2": ["&scroll_vertical_encoder", "&scroll_horizontal_encoder"],
    }
    for layer, body in layers.items():
        bindings = re.findall(r"sensor-bindings\s*=\s*(.*?);", body, re.S)
        if layer in expected and len(bindings) != 1:
            fail(f"layer {layer} must have exactly one sensor-bindings property")
        if not bindings:
            continue  # ZMK falls back to bindings on lower active layers.
        if len(bindings) != 1:
            fail(f"layer {layer} has duplicate sensor-bindings")
        behaviors = re.findall(r"&[A-Za-z_][A-Za-z0-9_]*", bindings[0])
        if layer in expected:
            if behaviors != expected[layer]:
                fail(f"layer {layer}: sensor bindings changed: {behaviors}")
        elif not behaviors or behaviors[0] != "&scroll_vertical_encoder":
            fail(f"layer {layer}: left encoder must remain vertical")
    for name, first, second in [
        ("scroll_vertical_encoder", "SCRL_DOWN", "SCRL_UP"),
        ("scroll_horizontal_encoder", "SCRL_LEFT", "SCRL_RIGHT"),
    ]:
        match = re.search(
            rf"{name}\s*:\s*{name}\s*\{{(.*?)\}};", text, re.S
        )
        if not match:
            fail(f"missing sensor behavior: {name}")
        normalized = re.sub(r"\s+", " ", match.group(1))
        if f"<&msc {first}>, <&msc {second}>" not in normalized:
            fail(f"sensor behavior changed: {name}")
    print("POINTING GUARD PASS: left encoder retained; right trackball overlay locked; core layer sensor bindings intact")

if __name__ == "__main__":
    main()
