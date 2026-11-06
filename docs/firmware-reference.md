# Manufacturer binary baseline and comparison

## Exact reproducibility established 2026-11-06

The previously uploaded functioning manufacturer's UF2 pair is now reproduced
bit-for-bit from public source and a GitHub Actions build:

- Historical source: [Vzhao-L/zmk-for-charybdis @ 6c32880](https://github.com/Vzhao-L/zmk-for-charybdis/commit/6c32880db0a7a61efa826c3b624ba6cb0884f769).
- Frozen source branch: [baseline/vendor-bitexact-20261106](https://github.com/Tolian82/keymap-editor2/tree/baseline/vendor-bitexact-20261106).
- Archived reference build: [GitHub Actions 42240434217](https://github.com/Tolian82/keymap-editor2/actions/runs/42240434217).

| Source of images | LEFT SHA-256 | RIGHT SHA-256 |
| --- | --- | --- |
| Owner's original known-good manufacturer UF2s | `9eef19d7138cfe3c7acff26d1a562ca7a55d6463599c0a4c1bd12e86b383b6a0` | `42ad17a02ff98e46799ce09651cb5cca5d4bb2fe0fea19f8951a9a765dc85672` |
| Build 42240434217 | **SAME** | **SAME** |

Original sizes: left 363008 bytes; right 528384 bytes. Both exact matches
were verified against the original uploaded file bytes, not inferred from CI.

## Source forensics

The earlier imported `keymap-editor2` build 42201763467 matched the LEFT
image byte-for-byte but differed from the manufacturer RIGHT image in 59
payload bytes (9 blocks). With the untouched latest upstream
`main-20250226` keymap it differed by only 19 payload bytes (4 blocks).
Restoring the historical `layer_0` second sensor binding from
`&scroll_vertical_encoder` to `&scroll_horizontal_encoder` eliminated
ALL differences and recovered the original RIGHT SHA-256 exactly.

This establishes source correspondence **for the unchanged reference
firmware**. It does NOT prove the later customized firmware behaves identically:
adding macros changes binary code/data layout and the owner observed a left
scroll wheel regression after flashing customized run 42206973808.

## Owner-confirmed actual hardware

- LEFT: physical EC11 rotary scroll wheel, vertical scrolling.
- RIGHT: physical PMW3610 trackball, mouse on `layer_0`, scroll on `layer_1`.
- There is **NO physical right EC11 encoder**.
- Legacy `right_encoder` DT node and second `sensor-bindings` slot are part
  of the *exactly reproduced vendor build*. A draft experimental PR #2
  proposed disabling the phantom hardware node, but this diverges from the
  manufacturer reference and has not been hardware validated.
- Left wheel events traverse a separate ZMK split BLE sensor notification
  channel. Normal keyboard key presses from both halves are insufficient
  to prove that sensor notifications work.

## Safe changes to main

The owner's customized keymap and four Windows macros remain in `main`.
Only the `layer_0` second sensor binding and the guard/documentation were
updated to align with the manufacturer's source. The `charybdis.dtsi`,
overlay files, PMW3610 driver and ZMK revision are not changed.

In particular, `config/charybdis.json` exposes both **logical** sensor
positions to the web editor so the second `sensor-bindings` entry survives
round-trip saves. This must not be confused with two physical rotary wheels.

**Important:** no claim of a hardware fix is made solely from recompiling a
customized source. Do not run `settings_reset` without planning Bluetooth
re-pairing and without preserving the working vendor UF2 backups.
