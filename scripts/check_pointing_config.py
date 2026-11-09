#!/usr/bin/env python3
"""Guard critical Charybdis ZMK behavior while allowing keymap-editor key changes.

This checks repository consistency only; it is NOT proof of equivalence to vendor UF2.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# SHA-1 values are Git *blob* object IDs (integrity regression guard, not a
# cryptographic authenticity check). Update deliberately for hardware upgrades.
LOCKED_GIT_BLOBS = {
    "build.yaml": "a86c206d5118f8dd2d631ce83491f14c10fb6d58",
    "config/west.yml": "eeb5ee4705b1e16c85204a9f978772c3d6728036",
    "config/charybdis.conf": "f58dcd9e855b7d81a6121e67fb6cc92e71423412",
    "config/charybdis.json": "ac273223cc4212a7c52fc62c12c60d7bc01728cb",
    "config/boards/shields/charybdis/Kconfig.defconfig": "851ad1e92d01d87610509949e16fbb640ef7a812",
    "config/boards/shields/charybdis/Kconfig.shield": "16a7b54e6400a40ad199c64c29e8bfd6933db762",
    "config/boards/shields/charybdis/charybdis.conf": "e69de29bb2d1d6434b8b29ae775ad8c2e48c5391",
    "config/boards/shields/charybdis/charybdis.dtsi": "32ac7e2c0d72209ed9041aefeb305c4cbfbf56ee",
    "config/boards/shields/charybdis/charybdis.zmk.yml": "3c0e29bc341925ea10aae4a58ab79fae04fe0573",
    "config/boards/shields/charybdis/charybdis_left.conf": "82303644c9059058ef8d5aaccc3e62a6ffad9093",
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

    metadata = json.loads((ROOT / "config/charybdis.json").read_text())
    actual_sensors = [
        (item.get("ref"), item.get("compatible"), item.get("enabled"))
        for item in metadata.get("sensors", [])
    ]
    expected_sensors = [
        ("left_encoder_1", "alps,ec11", True),
        ("right_encoder", "alps,ec11", True),
    ]
    if actual_sensors != expected_sensors:
        fail(
            "editor sensor metadata must list LEFT and RIGHT encoders in "
            f"the ZMK sensor order: {actual_sensors}"
        )

    text = uncomment((ROOT / "config/charybdis.keymap").read_text())
    layers = dict(re.findall(r"(?ms)^\s*layer_(\d+)\s*\{(.*?)^\s*\};", text))
    if not {"0", "1", "2"}.issubset(layers):
        fail("missing or reordered core layers 0/1/2")
    expected = {
        "0": ["&scroll_vertical_encoder", "&scroll_horizontal_encoder"],
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
    # Reconfigurations in BEHAVIORS are also part of scrolling semantics.
    # These are the settings shown in the user's editor screenshots.
    for ref, expected_values in {
        "msc": {
            "delay-ms": "<0>",
            "time-to-max-speed-ms": "<30>",
            "acceleration-exponent": "<0>",
        },
        "lt": {
            "tapping-term-ms": "<200>",
            "quick-tap-ms": "<150>",
            "flavor": '"balanced"',
        },
    }.items():
        match = re.search(rf"&{ref}\s*\{{(.*?)\}};", text, re.S)
        if not match:
            fail(f"missing behavior reconfiguration: &{ref}")
        actual_values = dict(
            re.findall(r"([A-Za-z][\w-]*)\s*=\s*([^;]+);", match.group(1))
        )
        for field, expected_value in expected_values.items():
            if re.sub(r"\s+", "", actual_values.get(field, "")) != expected_value:
                fail(f"&{ref} {field} changed, expected {expected_value}")
    for name in ("scroll_vertical_encoder", "scroll_horizontal_encoder"):
        match = re.search(rf"{name}\s*:\s*{name}\s*\{{(.*?)\}};", text, re.S)
        if not match or not re.search(r"tap-ms\s*=\s*<64>\s*;", match.group(1)):
            fail(f"{name} tap-ms changed (expected 64)")
    print("POINTING GUARD PASS: uploaded working v2 layer-0 sensor mapping and guarded hardware/behaviors")

if __name__ == "__main__":
    main()
