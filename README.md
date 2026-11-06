# Charybdis ZMK — keymap-editor2

This is an editable ZMK **source configuration**, based on [Tolian82/keymap-editor](https://github.com/Tolian82/keymap-editor), itself derived from [Vzhao-L/zmk-for-charybdis](https://github.com/Vzhao-L/zmk-for-charybdis/tree/main-20250226).

**Important:** The seller's two functioning `.uf2` files are compiled binaries, not source archives. Their exact source cannot be reliably recovered. This repository is a *best available source baseline*, **not a verified binary-equivalent reconstruction**. Do not overwrite working firmware until a test build is checked on the keyboard.

## Expected behavior and latest owner clarification

| Active layer | Left EC11 encoder | Right PMW3610 trackball | Right EC11 encoder |
| --- | --- | --- | --- |
| 0 | Vertical scrolling | Mouse cursor | Vertical scrolling (existing binding) |
| 1 | **Vertical scrolling remains enabled** | Scrolling (`scroll-layers = <1>`) | Horizontal scrolling |
| 2 | Vertical scrolling | Mouse cursor, unless another layer activates scrolling | Horizontal scrolling |
| Other layers | Inherits a lower active layer's vertical-scroll binding unless explicitly configured | Mouse unless layer 1 is the highest active layer | Existing ZMK fallback behavior |

The owner's latest instruction is **to keep the left encoder scrolling on ALL layers**. No attempt has been made to disable it on layer 1. The existing `sensor-bindings` are preserved verbatim in `config/charybdis.keymap`.

## Why encoder/sensor metadata is needed

The seller's ZMK board definition declares two rotary encoders in `charybdis.dtsi`, with one enabled by each half's overlay. Earlier `config/charybdis.json` incorrectly contained `"sensors": []`, so the web editor had no matching sensor layout metadata. This file now explicitly describes both encoders, in ZMK sensor order:

1. `left_encoder_1` (left EC11, vertical scrolling)
2. `right_encoder` (right EC11, vertical on layer 0 and horizontal on layers 1/2)

**Do not confuse the right rotary encoder with the right PMW3610 trackball.** The trackball is managed by its own driver in `charybdis_right.overlay`, switching to scroll on layer 1, and is **not** listed as a keymap encoder.

The `BEHAVIORS` tab exposes the definitions for the two encoder rotate behaviors and the `&msc` acceleration settings. These already match the source and do not need manual changes. When saving the keymap, the editor is expected to preserve the `sensor-bindings` assignments; GitHub Actions will reject a modified keymap if it doesn't.

**This fix has not yet been validated against a real editor save-and-flash cycle.** Keep the vendor UF2 files as rollback copies until confirmed physically.

## Editing with the web keymap editor

1. Open https://nickcoutsos.github.io/keymap-editor/.
2. Log in with GitHub and choose repository **`Tolian82/keymap-editor2`**, not `keymap-editor`.
3. Change only the desired key bindings or macros, save, and open [Actions](https://github.com/Tolian82/keymap-editor2/actions).
4. Ensure **`verify-pointing`** succeeds before using artifacts from the **`build`** job.
5. Flash both halves only after a working build has been verified. Keep the vendor's two working UF2 files safe as rollback images.

The guard intentionally rejects changes to hardware overlays, ZMK manifests, build settings, and the core scroll sensor bindings. This is a fail-closed safety check, not an auto-repair mechanism. If editor rewrites the protected sensor bindings, CI fails instead of silently generating a potentially broken firmware. Changes to hardware files must be deliberately reviewed and guard hashes updated.

**Hardware verification is still required:** source and build consistency tests cannot prove that the output behaves identically to the seller's known-good UF2 binaries.

See [Firmware reference](docs/firmware-reference.md).
