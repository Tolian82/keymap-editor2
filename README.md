# Charybdis: редактируемая прошивка ZMK

## Основа текущей ветки main

**Исходники восстановлены из успешной сборки GitHub Actions
[№42204233271](https://github.com/Tolian82/keymap-editor2/actions/runs/42204233271)
(коммит `545c53e3f94310eb013c377b495f4378a114641f`).**

Аппаратная и функциональная конфигурация этого коммита сохранена **без
изменений**. Дополнительно введены только проверки, документация и изменения
GitHub Actions, которые не меняют генерируемую прошивку.

- Плата сборки: `nice_nano_v2` на обеих половинах.
- В исходном DTSI объявлен `left_encoder_1`, а также логический
  `right_encoder`; справа физически находится **только трекбол PMW3610**,
  и наличие программного узла не означает наличие второго колеса.
- Левое физическое колесо: вертикальная прокрутка на `layer_0`, `layer_1`
  и `layer_2`, наследование нижних слоёв в остальных случаях.
- Правый трекбол: указатель мыши на `layer_0`, режим прокрутки на
  `layer_1`, через `scroll-layers = <1>;`.
- Приоритет этой ветки — восстановление **именно выбранного пользователем
  исходного варианта**, а не экспериментов с профилем v1.
- Более поздние пользовательские переназначения и дополнительные
  макросы после коммита `545c53e` не включены в исходную базу;
  их можно вновь добавить через редактор.

Контрольные SHA-256 артефактов **оригинальной сборки №42204233271**:

| Файл | SHA-256 |
| --- | --- |
| `charybdis_left-nice_nano_v2-zmk.uf2` | `9eef19d7138cfe3c7acff26d1a562ca7a55d6463599c0a4c1bd12e86b383b6a0` |
| `charybdis_right-nice_nano_v2-zmk.uf2` | `51c1d57bdd34a0ac83922b8daa9623275cd5735d7895f21863eb574d9a6d0f05` |

Эти SHA относятся к исходному архиву экшена, **а не** к новому
варианту после изменения клавиш. Эта конкретная сборка успешно компилировалась,
но отсутствие проблем с колёсиком на физическом устройстве не доказано.

## Редактирование через Keymap Editor

1. Откройте [ZMK Keymap Editor](https://nickcoutsos.github.io/keymap-editor/)
   и выберите `Tolian82/keymap-editor2`, ветка **main**.
2. Меняйте обычные клавиши и нужные макросы. Не меняйте
   `Sensor bindings` и вкладку `BEHAVIORS` для колесика/мыши.
3. Сохраните изменения. После этого откройте
   [GitHub Actions](https://github.com/Tolian82/keymap-editor2/actions).
4. Сборка должна успешно пройти **три этапа**:
   `verify-pointing`, `build` и `verify-compiled-pointing`.
5. Используйте артефакт `firmware` только после всех зелёных проверок.
   `settings_reset` не прошивайте для обычной смены клавиш.

Проверка исходников `scripts/check_pointing_config.py` жёстко фиксирует
плату, настройки сенсоров, трекбола, параметры скроллинга и их привязки к слоям.
Новые тесты имитируют обычную замену клавиши (должна проходить) и
изменение настройки скроллинга (должно блокироваться).
После компиляции `scripts/check_compiled_pointing.py` проверяет,
что в UF2 присутствуют устройства исходной сборки.

**Важно:** CI предотвращает известные изменения конфигурации, но не может
гарантировать работу энкодера при каждом новом варианте прошивки. Требуется
первоначально проверить восстановленную базу на клавиатуре и сохранить её как
аппаратно принятую. Не заменяйте резервные копии своих работавших UF2.

Технические детали: [docs/firmware-reference.md](docs/firmware-reference.md).

## 2026-11-08: verified *working* uploaded nice_nano_v2 pair (critical correction)

The user confirmed that the newly uploaded files
`charybdis_left-nice_nano_v2-zmk(3).uf2` and
`charybdis_right-nice_nano_v2-zmk(3).uf2` **actually work on the physical
keyboard**, including the LEFT scroll wheel.

| Half | SHA-256 of user-verified working UF2 |
| --- | --- |
| LEFT | `9eef19d7138cfe3c7acff26d1a562ca7a55d6463599c0a4c1bd12e86b383b6a0` |
| RIGHT | `42ad17a02ff98e46799ce09651cb5cca5d4bb2fe0fea19f8951a9a765dc85672` |

This pair matches **exactly** the archived historical
[Actions 42240434217](https://github.com/Tolian82/keymap-editor2/actions/runs/42240434217)
and preserved [vendor-bitexact-20261106](https://github.com/Tolian82/keymap-editor2/tree/vendor-bitexact-20261106)
Git tag. The previously selected baseline
[Actions 42204233271](https://github.com/Tolian82/keymap-editor2/actions/runs/42204233271)
had **the identical LEFT UF2**, but the RIGHT UF2 differed by **59 application
bytes across 9 UF2 blocks**, even though both files were 528384 bytes long.

The older baseline's `layer_0` sensor bindings were:
```dts
sensor-bindings = <&scroll_vertical_encoder &scroll_vertical_encoder>;
```
The user-verified working source has:
```dts
sensor-bindings = <&scroll_vertical_encoder &scroll_horizontal_encoder>;
```

The first sensor is the physical LEFT wheel and remains vertically scrolling.
The second DT sensor slot is present in the manufacturer's firmware, but the
physical RIGHT half has a PMW3610 trackball rather than a wheel. **Do not
disable or delete that slot as a shortcut:** the diagnostic attempt at
disabling the right encoder [Actions 42511405510](https://github.com/Tolian82/keymap-editor2/actions/runs/42511405510)
did **not** fix the user's wheel problem.

This candidate changes **only the second layer-0 sensor behavior** compared
with the user's most recent saved keymap `d176a4ae`. It preserves ALL
user-assigned keys, four new macro definitions, overlays, `nice_nano_v2`,
pinned PMW3610 driver, and other layer bindings. The source guard is corrected
to require the *observed working* mapping and the regression tests reject
accidental reversion to the dual-vertical mapping.

**Caution:** this is a controlled source correction based on the user's exact
working reference. The new RIGHT binary contains the owner's edited keys and
macros, so it will NOT be bit-identical to the original working firmware.
Source-level and binary-device tests cannot guarantee physical operation or
BLE sensor event delivery. Hardware acceptance remains pending.
