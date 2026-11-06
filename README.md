# Charybdis ZMK — keymap-editor2

This is an editable ZMK **source configuration**, based on [Tolian82/keymap-editor](https://github.com/Tolian82/keymap-editor), itself derived from [Vzhao-L/zmk-for-charybdis](https://github.com/Vzhao-L/zmk-for-charybdis/tree/main-20250226).

**Important:** The seller's two functioning `.uf2` files are compiled binaries, not source archives. Their exact source cannot be reliably recovered. This repository is a *best available source baseline*, **not a verified binary-equivalent reconstruction**. Do not overwrite working firmware until a test build is checked on the keyboard.

## Actual hardware (confirmed by owner)

| Active ZMK layer | Physical LEFT rotary scrolling wheel (EC11) | Physical RIGHT PMW3610 trackball |
| --- | --- | --- |
| `layer_0` — first layer | Vertical scrolling | Mouse cursor |
| `layer_1` — second layer | Vertical scrolling | Scrolling |
| `layer_2` and other layers | Left scrolling retained by explicit bindings or lower-layer fallback | Mouse cursor unless `layer_1` becomes the highest active layer |

**There is no right rotary encoder on the physical keyboard.** An earlier README incorrectly described one. The right half has **only the trackball**.

## Why a disabled right encoder *placeholder* still exists in Devicetree

The original source includes a two-entry ZMK `zmk,keymap-sensors` list:
`sensors = <&left_encoder_1 &right_encoder>;`.
The left wheel uses slot 0 in this array; the second slot is merely a logical
placeholder. This order must remain stable across the split BLE connection,
and central ZMK v0.3 requires a `zmk,keymap-sensors` node to receive left
sensor events.

The candidate change on this diagnostic branch explicitly **disables** the
nonexistent `right_encoder` in the right half's overlay. This avoids configuring
GPIO interrupts for a device that does not exist. The physical left encoder,
its logical index, `sensor-bindings`, the PMW3610 driver and
`scroll-layers = <1>` are unchanged.

`config/charybdis.json` still describes **two logical sensor positions** for
the Keymap Editor but marks the unwired right slot `enabled: false`.
That slot is not a physical control. If the editor rewrites `sensor-bindings`
during a save, the GitHub Actions guard must fail.

**IMPORTANT:** This is a proposed diagnostic change, not a proven fix.
The original uploaded seller UF2 files are the rollback reference. Compile
success alone is not proof of reliable left-wheel scrolling. Do not merge or
flash this candidate before a deliberate physical test plan.

## Editing with the web keymap editor

1. Open https://nickcoutsos.github.io/keymap-editor/.
2. Log in with GitHub and choose repository **`Tolian82/keymap-editor2`**, not `keymap-editor`.
3. Change only the desired key bindings or macros, save, and open [Actions](https://github.com/Tolian82/keymap-editor2/actions).
4. Ensure **`verify-pointing`** succeeds before using artifacts from the **`build`** job.
5. Flash both halves only after a working build has been verified. Keep the vendor's two working UF2 files safe as rollback images.

The guard intentionally rejects changes to hardware overlays, ZMK manifests, build settings, and the core scroll sensor bindings. This is a fail-closed safety check, not an auto-repair mechanism. If editor rewrites the protected sensor bindings, CI fails instead of silently generating a potentially broken firmware. Changes to hardware files must be deliberately reviewed and guard hashes updated.

**Hardware verification is still required:** source and build consistency tests cannot prove that the output behaves identically to the seller's known-good UF2 binaries.

See [Firmware reference](docs/firmware-reference.md).
