# Техническая база прошивки и защита редактора

## Привязка к сборке пользователя

Источник: GitHub Actions
[42204233271](https://github.com/Tolian82/keymap-editor2/actions/runs/42204233271),
commit `545c53e3f94310eb013c377b495f4378a114641f`.

При восстановлении исходников дерево Git было возвращено в точности
к этому коммиту. Все последующие изменения в `main` касаются только
проверочных сценариев, документации и конфигурации CI.

В этой исходной базе:
- сборка ZMK `v0.3` для `nice_nano_v2`;
- закреплён PMW3610 драйвер `1d9c2c68ca76012e1b1e5f6ef02fa5eadc4ca399`;
- физический левый энкодер `left_encoder_1`, логический слот `right_encoder`
  в списке ZMK сенсоров, и правый PMW3610 трекбол;
- поведение `scroll_vertical_encoder` и `scroll_horizontal_encoder`
  с `tap-ms = <64>`;
- `&msc` со значениями `time-to-max-speed-ms = <30>`,
  `acceleration-exponent = <0>`, `delay-ms = <0>`;
- `sensor-bindings` на `layer_0`: два вертикальных назначения;
  на `layer_1` и `layer_2`: первое вертикальное, второе горизонтальное;
- `scroll-layers = <1>` для правого PMW3610.

`right_encoder` не означает установленное физически правое колесо;
на правой стороне у пользователя находится только трекбол. Программный
слот сохранён для точного воспроизведения выбранной сборки.

## Защита после Keymap Editor

`scripts/check_pointing_config.py` проверяет Git blob ID аппаратных файлов
и свойства keymap, позволяя изменить обычные клавиши и макросы.

`scripts/test_keymap_editor_guard.py` проверяет, что:
- редактирование обычной клавиши не блокирует сборку;
- изменение сенсорных привязок, параметров `&msc` и защищённого
  аппаратного файла вызывает отказ.

`scripts/check_compiled_pointing.py` проверяет структуру итоговых UF2
и характерные скомпилированные имена устройств левой и правой половин.
Этот тест не требует идентичного SHA для пользовательских изменений,
поскольку они меняют сам бинарник.

Реальное действие колеса, BLE-канала сенсоров и взаимодействие с трекболом
может подтвердить только проверка на клавиатуре. В частности, если при
неизменной конфигурации колесо работает через раз, автоматическая проверка
структуры UF2 не доказывает исправность прошивки.

## Исторические данные

В другом эксперименте была исследована пара `nice_nano_v1`, но
сформированный по ней пользовательский вариант не запустился.
Ветка `main` больше не содержит ни этих опытных изменений, ни
проверок бинарников, основанных на v1.

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
