# Charybdis ZMK firmware — keymap-editor2

## Important: the **v1** UF2 pair is the physically proven wheel reference

On 2026-11-08 the owner supplied four UF2 files and confirmed:
- `charybdis_left-nice_nano_v1-zmk.uf2` and `charybdis_right-nice_nano_v1-zmk.uf2`: **left scroll wheel works correctly**.
- `nice_nano_v2` pair and [edited v2 build 42492050194](https://github.com/Tolian82/keymap-editor2/actions/runs/42492050194): left wheel **does not work correctly**.
- The previous claim that the bit-exactly reproduced v2 image was a *working* hardware reference is superseded. The [vendor-bitexact-20261106](https://github.com/Tolian82/keymap-editor2/tree/vendor-bitexact-20261106) tag remains a historical v2 reconstruction, not a v1 wheel acceptance baseline.

The actual keyboard has **one physical wheel on LEFT**, **one PMW3610 trackball on RIGHT**, and no physical right encoder. The working v1 binary nonetheless contains **two left encoder device channels** with reversed A/B pin order, both from the same physical wheel.

## Wheel restoration candidate (2026-11-08)

The firmware source is based on the latest [user-edited v2 layout, commit 9702b20](https://github.com/Tolian82/keymap-editor2/commit/9702b20d8ac8c4db65aba1ef4cd9339126fe6abc). All of the user's new ordinary key bindings and macros remain intact.

The restored v1-style hardware/software features are:
- Both LEFT wheel channels `left_encoder_1` and `left_encoder_2` (reversed GPIO A/B) in the shield, and both explicitly enabled on LEFT.
- **No** `right_encoder` on RIGHT; the right controller retains PMW3610 with `scroll-layers = <1>;`.
- ZMK sensor order `<&left_encoder_1 &left_encoder_2>` in the DTSI, and matching two logical sensors exposed to Keymap Editor.
- Pointing processors `zip_xy_scaler 2 1` and `zip_scroll_scaler 2 1`, present in both proven working v1 UF2 binaries.
- Historical v1-style scrolling values and EC11 parameters.
- `nice_nano` target (the ZMK v0.3 target for first-generation nice!nano). The file label `nice_nano_v1` alone does not prove the user's physical controller revision; verify before flashing.

The right trackball remains a mouse on `layer_0`, and scrolls on `layer_1` (the second layer in the UI). The left physical wheel should scroll vertically on both, with the second channel's existing binding preserved.

**This is a candidate reconstruction based on verified binary features and historical source, NOT an exact binary reproduction of the supplied v1 UF2s.** A successful CI build is NOT proof of wheel operation. Only physical testing can confirm.

## Safely editing with [Nick Coutsos Keymap Editor](https://nickcoutsos.github.io/keymap-editor/)

1. Select `Tolian82/keymap-editor2` on `main` after the repaired candidate is accepted.
2. Edit ordinary keys or macros only. Do not edit the **Sensor bindings**, mouse behaviors, or `&msc`/`&mmv` reconfigurations.
3. Save. GitHub Actions runs **two safeguards**:
   - `verify-pointing`: fails if the editor changes protected hardware files or scroll behavior settings.
   - `verify-binary-scroll-topology`: inspects the generated LEFT and RIGHT UF2 files and rejects builds that lose either LEFT sensor channel, gain a phantom RIGHT encoder, or omit the known v1 pointing scalers.
4. Use the `firmware` artifact only if **all** Actions jobs pass. The guards fail closed: if the editor rewrites protected settings, the build is flagged rather than treated as safely deployable.
5. Keep both known-working v1 files unchanged as a physical rollback pair.

This does **not** guarantee that every new keymap behaves correctly at runtime. It prevents the documented regressions from silently passing CI and makes accidental wheel topology changes visible.

See [forensic notes](docs/firmware-reference.md).
