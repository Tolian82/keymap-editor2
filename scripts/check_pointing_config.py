#!/usr/bin/env python3
"""Protect the vendor-confirmed Charybdis pointing/split sensor mapping.

Golden baseline: branch baseline/vendor-bitexact-20261106, build 42240434217.
The source of that historical build reproduced both owner-supplied vendor UF2 files
byte for byte. THIS check guards source config only; it cannot prove that a newly
modified firmware with user macros behaves correctly on physical hardware.
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
    "build.yaml": "2479e24a08f8bce8979b5b73e5182290aa85646c",
    "config/west.yml": "eeb5ee4705b1e16c85204a9f978772c3d6728036",
    "config/charybdis.conf": "f58dcd9e855b7d81a6121e67fb6cc92e71423412",
    "config/charybdis.json": "22445125a1335eefb701437aa477ea748a334774",
    "config/boards/shields/charybdis/Kconfig.defconfig": "851ad1e92d01d87610509949e16fbb640ef7a812",
    "config/boards/shields/charybdis/Kconfig.shield": "16a7b54e6400a40ad199c64c29e8bfd6933db762",
    "config/boards/shields/charybdis/charybdis.conf": "e69de29bb2d1d6434b8b29ae775ad8c2e48c5391",
    "config/boards/shields/charybdis/charybdis.dtsi": "3159ed2d6507d4b3ae2f8e82c414826f51648f4b",
    "config/boards/shields/charybdis/charybdis.zmk.yml": "3c0e29bc341925ea10aae4a58ab79fae04fe0573",
    "config/boards/shields/charybdis/charybdis_left.conf": "e397e04fda6f28a70960ebf7824c0603746160f2",
    "config/boards/shields/charybdis/charybdis_left.overlay": "86c856b49f35254248892e747122e40a7d0ae294",
    "config/boards/shields/charybdis/charybdis_right.conf": "c36ca9da1b6524cb4eb3fd9c7d3922f28113eb43",
    "config/boards/shields/charybdis/charybdis_right.overlay": "279a6394d049f69bed839de4bbccb1a8863f990e"
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
        ("left_encoder_2", "alps,ec11", True),
    ]
    if actual_sensors != expected_sensors:
        fail(
            "editor sensor metadata must match TWO LEFT sensor channels in "
            f"the ZMK sensor order: {actual_sensors}"
        )

    # Working v1: TWO left sensor channels, no right rotary, and v1 board profile.
    board_text = (ROOT / "build.yaml").read_text()
    boards = re.findall(r"(?m)^  - board: (\S+)\s*$", board_text)
    if boards != ["nice_nano"] * 3:
        fail(f"v1 board target mismatch: {boards}")
    dtsi = uncomment((ROOT / "config/boards/shields/charybdis/charybdis.dtsi").read_text())
    if not re.search(r"sensors\s*=\s*<&left_encoder_1\s+&left_encoder_2>\s*;", dtsi):
        fail("v1 hardware must keep two LEFT encoder sensor slots")
    if "right_encoder:" in dtsi or "encoder_right" in dtsi:
        fail("v1 hardware must not create a RIGHT rotary encoder")
    left_overlay = uncomment((ROOT / "config/boards/shields/charybdis/charybdis_left.overlay").read_text())
    for sensor in ("left_encoder_1", "left_encoder_2"):
        if not re.search(rf"&{sensor}\s*\{{\s*status\s*=\s*\"okay\"\s*;", left_overlay):
            fail(f"left wheel sensor {sensor} not enabled")
    right_overlay = uncomment((ROOT / "config/boards/shields/charybdis/charybdis_right.overlay").read_text())
    if "right_encoder" in right_overlay:
        fail("right encoder must not be enabled on PMW3610 half")
    if not re.search(r"scroll-layers\s*=\s*<1>\s*;", right_overlay):
        fail("right PMW3610 scroll layer changed (must be layer_1)")

    text = uncomment((ROOT / "config/charybdis.keymap").read_text())
    if "#define ZMK_POINTING_DEFAULT_SCRL_VAL 12" not in text:
        fail("v1 scroll value changed")
    for listener,processor in (("mmv_input_listener","zip_xy_scaler"),("msc_input_listener","zip_scroll_scaler")):
        if not re.search(rf"&{listener}\s*\{{\s*input-processors\s*=\s*<&{processor}\s+2\s+1>\s*;\s*\}};", text):
            fail(f"v1 input scaler changed: {processor}")

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
            "time-to-max-speed-ms": "<100>",
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
        if not match or not re.search(r"tap-ms\s*=\s*<100>\s*;", match.group(1)):
            fail(f"{name} tap-ms changed (expected 100)")
    print("POINTING GUARD PASS: proven-v1 LEFT wheel sensor topology and PMW3610 scroll protection intact")

if __name__ == "__main__":
    main()
