#!/usr/bin/env python3
"""Regression tests for editing ordinary keys without losing pointing settings.

This is not the web editor itself: it checks its expected save semantics.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KEYMAP = "config/charybdis.keymap"
CHECK = "scripts/check_pointing_config.py"


def test_case(name: str, mutate, should_pass: bool) -> None:
    with tempfile.TemporaryDirectory(prefix="charybdis-guard-") as directory:
        root = Path(directory)
        shutil.copytree(ROOT / "config", root / "config")
        (root / "scripts").mkdir()
        shutil.copy2(ROOT / CHECK, root / CHECK)
        shutil.copy2(ROOT / "build.yaml", root / "build.yaml")
        mutate(root)
        run = subprocess.run(
            [sys.executable, str(root / CHECK)],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
        passed = run.returncode == 0
        if passed != should_pass:
            raise SystemExit(
                f"EDITOR GUARD TEST FAIL: {name}, expected pass={should_pass}; "
                f"stdout={run.stdout!r}, stderr={run.stderr!r}"
            )
        print(f"EDITOR GUARD TEST PASS: {name} "
              f"({'accepted' if passed else 'correctly rejected'})")


def change(path: Path, old: str, new: str) -> None:
    content = path.read_text()
    if old not in content:
        raise RuntimeError(f"Missing expected pattern in {path}: {old}")
    path.write_text(content.replace(old, new, 1))


def main() -> None:
    test_case("untouched configuration", lambda root: None, True)
    test_case(
        "ordinary key assignment changed by editor",
        lambda root: change(root / KEYMAP, "&kp ESC", "&kp F1"),
        True,
    )
    test_case(
        "left wheel binding changed",
        lambda root: change(
            root / KEYMAP,
            "sensor-bindings = <&scroll_vertical_encoder &scroll_vertical_encoder>;",
            "sensor-bindings = <&scroll_horizontal_encoder &scroll_vertical_encoder>;",
        ),
        False,
    )
    test_case(
        "mouse scrolling behavior changed",
        lambda root: change(
            root / KEYMAP,
            "time-to-max-speed-ms = <30>",
            "time-to-max-speed-ms = <200>",
        ),
        False,
    )
    test_case(
        "hardware overlay changed",
        lambda root: (root / "config/boards/shields/charybdis/charybdis_right.overlay")
            .write_text(
                (root / "config/boards/shields/charybdis/charybdis_right.overlay")
                .read_text() + "\n// unexpected change\n"
            ),
        False,
    )


if __name__ == "__main__":
    main()
