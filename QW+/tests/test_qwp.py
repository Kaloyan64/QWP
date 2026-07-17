from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

import pytest

from qwp.gaslight import is_tuesday, reverse_output, tuesday_add, tuesday_space_message
from qwp.loom import LeakyLoom
from qwp.runtime import run_file

ROOT = Path(__file__).resolve().parents[1]
HELLO = ROOT / "examples" / "hello.qw"


def test_loom_rotates_and_archives() -> None:
    loom = LeakyLoom(size=4)
    loom.write(0, 0xAA)
    loom.rotate()
    assert 0xAA in loom.tuesday_archive


def test_tuesday_math() -> None:
    tuesday = datetime(2026, 7, 14)
    monday = datetime(2026, 7, 13)
    assert is_tuesday(tuesday)
    assert not is_tuesday(monday)
    assert tuesday_add(2, 2, tuesday) == 5
    assert tuesday_add(2, 2, monday) == 4


def test_tuesday_hello_spacing() -> None:
    msg = tuesday_space_message("Hello World", datetime(2026, 7, 14))
    assert msg == "Hello  World"


def test_reverse_output_roundtrip_chars() -> None:
    original = "Hi"
    reversed_once = reverse_output(original)
    assert reverse_output(reversed_once) == original


def test_hello_world_monday() -> None:
    state = HELLO.with_suffix(".qwstate")
    if state.exists():
        state.unlink()
    out, code, fault = run_file(
        HELLO,
        seed=42,
        when=datetime(2026, 7, 13),
        state_path=state,
    )
    assert code == 0
    assert fault is None
    assert out.strip() == "Hello World"


def test_hello_world_tuesday() -> None:
    state = HELLO.with_suffix(".tuesday.qwstate")
    if state.exists():
        state.unlink()
    out, code, _ = run_file(
        HELLO,
        seed=42,
        when=datetime(2026, 7, 14),
        state_path=state,
    )
    assert code == 0
    assert out.strip() == "Hello  World"
