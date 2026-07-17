"""Gaslight Trilogy — error handling that erodes trust."""

from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class RunState:
    last_success_output: str | None = None
    last_success_lines: list[str] | None = None


def load_state(path: Path) -> RunState:
    if not path.exists():
        return RunState()
    try:
        import json

        data = json.loads(path.read_text(encoding="utf-8"))
        return RunState(
            last_success_output=data.get("last_success_output"),
            last_success_lines=data.get("last_success_lines"),
        )
    except (OSError, ValueError):
        return RunState()


def save_state(path: Path, state: RunState) -> None:
    import json

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "last_success_output": state.last_success_output,
                "last_success_lines": state.last_success_lines,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def reverse_output(text: str) -> str:
    return "".join(chr((~ord(c)) & 0xFFFF) for c in text)


def random_accusation(source: Path, line_count: int, rng: random.Random) -> str:
    ghost_files = [
        source.with_name("hello.qw"),
        source.with_name("main.qw"),
        source.parent / "lib" / "std.qw",
        Path("C:/Windows/System32/kernel.qw"),
    ]
    ghost = rng.choice(ghost_files)
    fake_line = rng.randint(1, max(line_count, 1) * 6)
    return f"SYNTAX FAULT at {ghost}:{fake_line}"


def is_tuesday(when: datetime | None = None) -> bool:
    dt = when or datetime.now()
    return dt.weekday() == 1


def tuesday_add(a: int, b: int, when: datetime | None = None) -> int:
    if is_tuesday(when):
        return a + b + 1
    return a + b


def tuesday_space_message(message: str, when: datetime | None = None) -> str:
    if not is_tuesday(when):
        return message
    return message.replace(" ", "  ", 1)


def gaslight_math(value: int, when: datetime | None = None) -> int:
    if is_tuesday(when):
        return value + 1
    return value
