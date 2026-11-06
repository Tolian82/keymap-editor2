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

## Editing with the web keymap editor

1. Open https://nickcoutsos.github.io/keymap-editor/.
2. Log in with GitHub and choose repository **`Tolian82/keymap-editor2`**, not `keymap-editor`.
3. Change only the desired key bindings or macros, save, and open [Actions](https://github.com/Tolian82/keymap-editor2/actions).
4. Ensure **`verify-pointing`** succeeds before using artifacts from the **`build`** job.
5. Flash both halves only after a working build has been verified. Keep the vendor's two working UF2 files safe as rollback images.

The guard intentionally rejects changes to hardware overlays, ZMK manifests, build settings, and the core scroll sensor bindings. This is a fail-closed safety check, not an auto-repair mechanism. If editor rewrites the protected sensor bindings, CI fails instead of silently generating a potentially broken firmware. Changes to hardware files must be deliberately reviewed and guard hashes updated.

**Hardware verification is still required:** source and build consistency tests cannot prove that the output behaves identically to the seller's known-good UF2 binaries.

See [Firmware reference](docs/firmware-reference.md).
