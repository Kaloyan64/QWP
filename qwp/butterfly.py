"""Butterfly Engine — mutates remaining source after each executed line."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

from qwp.glyphs import VEIL_GLYPHS
from qwp.lexer import Line

if TYPE_CHECKING:
    pass

VEIL_CHARS = list(VEIL_GLYPHS.keys())


def _bit_rot(line: Line, rng: random.Random) -> None:
    if not line.raw:
        return
    pos = rng.randrange(len(line.raw))
    veil = rng.choice(VEIL_CHARS)
    line.raw = line.raw[:pos] + veil + line.raw[pos:]
    line.veils.append(veil)


def _semantic_inversion(line: Line, rng: random.Random) -> None:
    relic_positions = [i for i, ch in enumerate(line.raw) if ch in "⸮⸸⸹⸺⸻⸼⸽⸾⸿"]
    if len(relic_positions) < 2:
        return
    a, b = rng.sample(relic_positions, 2)
    chars = list(line.raw)
    chars[a], chars[b] = chars[b], chars[a]
    line.raw = "".join(chars)
    line.relics = [ch for ch in line.raw if ch in "⸮⸸⸹⸺⸻⸼⸽⸾⸿"]


def _temporal_smear(line: Line, prior: str | None) -> None:
    if prior is not None:
        line.raw = prior


def mutate_remaining(
    lines: list[Line],
    executed_index: int,
    prior_lines: list[str] | None,
    rng: random.Random,
) -> None:
    """Apply butterfly mutations to all lines after executed_index."""
    for i in range(executed_index + 1, len(lines)):
        choice = rng.random()
        prior = prior_lines[i] if prior_lines and i < len(prior_lines) else None
        if choice < 0.34:
            _bit_rot(lines[i], rng)
        elif choice < 0.67:
            _semantic_inversion(lines[i], rng)
        else:
            _temporal_smear(lines[i], prior)
        lines[i].relics = [ch for ch in lines[i].raw if ch in "⸮⸸⸹⸺⸻⸼⸽⸾⸿"]
        lines[i].veils = [ch for ch in lines[i].raw if ch in VEIL_GLYPHS]


def refresh_line_from_raw(line: Line) -> None:
    from qwp.lexer import _parse_string_body

    line.relics = [ch for ch in line.raw if ch in "⸮⸸⸹⸺⸻⸼⸽⸾⸿"]
    line.veils = [ch for ch in line.raw if ch in VEIL_GLYPHS]
    line.prime_punct = [ch for ch in line.raw if ch in ".,:;!?~"]
    if line.raw.count("⸺") >= 2:
        first = line.raw.index("⸺")
        last = line.raw.rindex("⸺")
        if first < last:
            line.string_payload = _parse_string_body(line.raw[first + 1 : last])
        else:
            line.string_payload = None
    else:
        line.string_payload = None
