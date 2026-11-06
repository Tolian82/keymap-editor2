# Known-good seller firmware reference (provided by owner, 2026-11-06)

These are **binary** reference images, *not decompiled source files*. The SHA-256 values below identify exactly the two uploaded files. Keep the original copies separately in case a rebuilt firmware is unsuccessful.

| Image | Size (bytes) | SHA-256 |
| --- | ---: | --- |
| `charybdis_left-nice_nano_v2-zmk.uf2` | 363008 | `9eef19d7138cfe3c7acff26d1a562ca7a55d6463599c0a4c1bd12e86b383b6a0` |
| `charybdis_right-nice_nano_v2-zmk.uf2` | 528384 | `42ad17a02ff98e46799ce09651cb5cca5d4bb2fe0fea19f8951a9a765dc85672` |

Both uploads contain valid UF2 blocks (payload size 256, family ID `0xada52840`) and recognizable `ZMK`, `Zephyr OS v3.5.0`, `XI-MK1_2` strings. The right contains `trackball@0` and `encoder_right`; left contains `encoder_left_1`. These confirm hardware family and construction, **not exact source equivalence**.

Source configuration retained from `Tolian82/keymap-editor`:
- Trackball node: `config/boards/shields/charybdis/charybdis_right.overlay` with `scroll-layers = <1>;`.
- Encoder hardware: `charybdis.dtsi`, left/right overlays and per-half `.conf` files.
- Per-layer encoder bindings in `config/charybdis.keymap`.
- Exact checks before build: `scripts/check_pointing_config.py`.

The editor itself is not a UF2-to-ZMK decompiler. Repeated firmware builds can differ due to toolchain revision, driver dependencies, build flags and source differences.

## Keymap Editor metadata correction (2026-11-06)

The original source config had `config/charybdis.json: "sensors": []` despite declaring `left_encoder_1` and `right_encoder` in its ZMK shield. The metadata has been updated to expose both rotary encoders in the same order as `charybdis.dtsi`. This changes **editor metadata only**; it does not modify hardware overlays, PMW3610 source, keymap bindings, or the flashing reference binaries.

Verification: CI verifies the sensor list, locked ZMK hardware configuration, rotate behaviors, `&msc` scroll parameters, and per-layer sensor bindings. This does not replace a physical regression test after the editor saves a change.
