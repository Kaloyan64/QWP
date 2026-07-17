"""QW+ command-line interface."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

from qwp.runtime import run_file

SPEC = """
QW+ Spec Sheet (abridged)
=========================
Veil-glyphs: U+200B U+200C U+200D U+FEFF (invisible identifiers)
Relic-glyphs: ⸮ ⸸ ⸹ ⸺ ⸻ ⸼ ⸽ ⸾ ⸿

Meaning = f(glyph, line_number mod 7)

⸮ : NOP | rotate×2 | emit | stdin | xor | jump | HALT
⸸ : add | sub | mul | div | mod | nand | nor
⸹ : cmp | swap 1↔3 | reverse | dup | delete-self | rewrite | pray
⸺ : open/close string | regret | comment modes
⸻ : call | return | tail | yield-tuesday | import | export | recurse
⸼ : if > | if == | if tuesday | if lie | else | elif | endif
⸽ : print char | print loom | print lie | print prev | swap streams | null | self

Every command rotates the Leaky Loom one byte left.
Tuesday: arithmetic lies, Hello World gains an extra space.
Second run after syntax fault: output may be reversed.
"""


def _parse_day(day: str | None) -> datetime | None:
    if not day:
        return None
    day = day.lower()
    mapping = {
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5,
        "sunday": 6,
    }
    if day not in mapping:
        raise SystemExit(f"unknown day: {day}")
    # Anchor to a known week: 2026-07-13 is Monday
    base = datetime(2026, 7, 13)
    from datetime import timedelta

    return base + timedelta(days=mapping[day])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="qwp", description="Run QW+ programs")
    parser.add_argument("file", nargs="?", type=Path, help="QW+ source file")
    parser.add_argument("--seed", type=int, default=42, help="RNG seed")
    parser.add_argument("--day", type=str, help="Override weekday (monday..sunday)")
    parser.add_argument("--spec", action="store_true", help="Print spec sheet")
    parser.add_argument("--visible", action="store_true", help="Show veil-glyphs in stderr")
    args = parser.parse_args(argv)

    if args.spec:
        print(SPEC)
        return 0

    if not args.file:
        parser.error("file is required unless --spec is passed")

    when = _parse_day(args.day)
    output, code, fault = run_file(args.file, seed=args.seed, when=when)

    if args.visible and args.file.exists():
        from qwp.lexer import parse_source, visible_repr

        for line in parse_source(args.file.read_text(encoding="utf-8")):
            print(f"{line.number:3}: {visible_repr(line.raw)}", file=sys.stderr)

    if fault:
        print(fault, file=sys.stderr)

    sys.stdout.write(output)
    if output and not output.endswith("\n"):
        sys.stdout.write("\n")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
