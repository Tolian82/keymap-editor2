# Charybdis ZMK — keymap-editor2

Customizable ZMK firmware source for the owner's wireless split Charybdis, editable with
[ZMK Keymap Editor](https://nickcoutsos.github.io/keymap-editor/).

## Important: restored and verified manufacturer baseline

On 2026-11-06, the manufacturer's previously working uploaded LEFT and RIGHT UF2
images were reproduced **byte for byte** by building the historical
`Vzhao-L/zmk-for-charybdis` `config/charybdis.keymap` revision
`6c32880db0a7a61efa826c3b624ba6cb0884f769` together with the matching
shield/ZMK build sources:

- **Frozen reference Git tag:** [vendor-bitexact-20261106](https://github.com/Tolian82/keymap-editor2/tree/vendor-bitexact-20261106)
- **Successful exact-match reference build:** [42240434217](https://github.com/Tolian82/keymap-editor2/actions/runs/42240434217)
- LEFT SHA-256: `9eef19d7138cfe3c7acff26d1a562ca7a55d6463599c0a4c1bd12e86b383b6a0`
- RIGHT SHA-256: `42ad17a02ff98e46799ce09651cb5cca5d4bb2fe0fea19f8951a9a765dc85672`

Do **not** move the reference tag. Its source is intentionally kept free of the owner's
later custom key assignments and Windows macros so the original two UF2 images
can always be regenerated and compared.

The working `main` branch is **customized**, preserving the owner's
`To1_macro`, `To0_macro`, and `Win_Left`, `WIn_Right`, `Ru_En`,
`Ctrl_Alt_Del` additions. It now restores the *vendor's sensor bindings*
while keeping these user customizations. As a result **the customized RIGHT UF2
cannot be byte-identical to the vendor image**.

## Actual hardware and intended behavior

| ZMK layer | LEFT physical rotary scroll wheel (EC11) | RIGHT physical trackball (PMW3610) |
| --- | --- | --- |
| `layer_0` (first layer) | Vertical scrolling | Mouse cursor |
| `layer_1` (second layer) | Vertical scrolling | Scrolling |
| Other layers | Wheel remains vertical via explicit mapping or inherited layer behavior | Cursor unless the active layer selects scrolling |

**There is no physical right rotary wheel.** The upstream hardware sources
nonetheless define an enabled `right_encoder` node and reserve a SECOND
logical `sensor-bindings` slot on the right controller. **Do not remove or
renumber that logical slot**: doing so without reworking ZMK split BLE sensor
index handling may stop the LEFT encoder from functioning.

Critically, the vendor's tested `layer_0` mapping is:

```dts
sensor-bindings = <&scroll_vertical_encoder &scroll_horizontal_encoder>;
```

An earlier version of this repository incorrectly duplicated
`&scroll_vertical_encoder` in BOTH slots. This was NOT identical to the
manufacturer's firmware. The exact vendor mapping is restored on `main`.
The second slot does not imply a physical right rotary wheel.

The right trackball's separate PMW3610 `scroll-layers = <1>;` setting is
protected in `charybdis_right.overlay`.

The Keymap Editor `config/charybdis.json` lists two logical sensors so it
round-trips the `sensor-bindings` array without silently dropping the second
entry. The second UI sensor is **only a placeholder**, not additional hardware.

## Editing procedure

1. Open the [ZMK Keymap Editor](https://nickcoutsos.github.io/keymap-editor/) and load `Tolian82/keymap-editor2`, branch `main`.
2. Edit only ordinary key assignments or desired macros; **do not change the sensor bindings, pointing behaviors, or right trackball settings**.
3. Save the keymap. The `verify-pointing` CI job must pass; it rejects
   changes to the manufacturer-confirmed scroll mapping and locked shield files.
4. Confirm all build jobs pass before downloading the `firmware` artifact.
5. Keep both original manufacturer UF2 images for rollback. Test the modified
   firmware on the physical keyboard before relying on it.

**Limits of CI:** a GREEN build only confirms compilation and that *known
source-level invariants* were preserved. It cannot certify split-BLE transport,
persistent settings, or the runtime behavior of a newly relinked firmware.
The owner observed a scrolling regression after an earlier customized flash;
that regression is not considered fixed until the owner verifies it.

See [Firmware reference and forensic comparison](docs/firmware-reference.md).
