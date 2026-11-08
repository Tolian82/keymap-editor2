# Working v1 Charybdis firmware: diagnostic evidence and reconstruction

## Uploaded evidence, 2026-11-08

The owner's physical test overrides all prior assumptions: the **v1** pair works, the **v2** pair does not reliably scroll using the LEFT wheel.

| File | Size | SHA-256 |
| --- | ---: | --- |
| charybdis_left-nice_nano_v1-zmk.uf2 | 363520 | `17a4eb8a79721f77ac97078491a2b4720f3de9a4d5e5e07d45bc45168a3f3e04` |
| charybdis_right-nice_nano_v1-zmk.uf2 | 527360 | `2678989c4b0e40b247b66d3bc51d82f0a31a6854ccad17449fa5375e2d969cac` |
| charybdis_left-nice_nano_v2-zmk.uf2 | 363008 | `9eef19d7138cfe3c7acff26d1a562ca7a55d6463599c0a4c1bd12e86b383b6a0` |
| charybdis_right-nice_nano_v2-zmk.uf2 | 528384 | `42ad17a02ff98e46799ce09651cb5cca5d4bb2fe0fea19f8951a9a765dc85672` |

The firmware images are valid nRF52840 UF2 files, start address `0x26000`, payload 256 bytes per UF2 block, Zephyr OS v3.5.0. These SHA-256 hashes refer to user-uploaded files, NOT a model inference.

### Extracted compiled-device fingerprints

| Feature | Working v1 LEFT | Working v1 RIGHT | Problematic v2 LEFT | Problematic v2 RIGHT |
| --- | --- | --- | --- | --- |
| encoder_left_1 | yes | no | yes | no |
| encoder_left_2 | **yes** | no | **no** | no |
| encoder_right | no | no | no | **yes** |
| PMW3610 trackball@0 | no | yes | no | yes |
| zip_xy_scaler | **yes** | **yes** | **no** | **no** |
| zip_scroll_scaler | **yes** | **yes** | **no** | **no** |

This is strong binary evidence of a change in hardware topology and pointing-processing. Compiled string presence does not independently prove the device caused a particular malfunction.

### Git history corroboration

- Historic [charybdis left overlay](https://github.com/Vzhao-L/zmk-for-charybdis/commit/5b8f89ceda5d25e9ca9ce1b850066f22aabeb11b) explicitly disabled the second LEFT encoder.
- Historic [right overlay](https://github.com/Vzhao-L/zmk-for-charybdis/commit/56e3edabe5484ec79fdd213ccf7426c02cea6448) explicitly enabled the phantom RIGHT encoder.
- Historical [DTSI](https://github.com/Vzhao-L/zmk-for-charybdis/blob/23603824f3263c31b7d09756ce2f325a7c5c9e16/config/boards/shields/charybdis/charybdis.dtsi) contained a pair of mirrored left sensor channels.
- Historical [keymap](https://github.com/Vzhao-L/zmk-for-charybdis/blob/23603824f3263c31b7d09756ce2f325a7c5c9e16/config/charybdis.keymap) used pointing scalers and a different EC11 scroll configuration.
- ZMK v0.3 defines the first-generation nice!nano target as `nice_nano`, while `nice_nano_v2` differs in external power polarity, initialization delay and battery measurement. Merely changing target is not guaranteed to fix an actual v2 controller; this is a compatibility hypothesis from the filenames.

## Reconstruction and guard rationale

The code intentionally restores BOTH left EC11 channels, removes the ghost right encoder, uses v1-style scroll scalers/parameters and preserves the latest owner keymap/macro assignments. A static source guard blocks accidental regressions from Keymap Editor saves, and a post-build UF2 check verifies device fingerprints on both halves.

The right trackball still uses `scroll-layers = <1>` (zero-based `layer_1`). The left wheel must remain vertical when the layer changes.

**Unresolved:** no complete exact source for the user's working v1 pair has been established. No SHA equality is claimed for new builds. ZMK's USB/BLE persistent settings may also affect split sensor events; do not run `settings_reset` as a routine test. The repair is not considered accepted until the user verifies on the physical keyboard.
