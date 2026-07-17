"""Tokenize QW+ source into lines and glyph streams."""

from __future__ import annotations

from dataclasses import dataclass, field

from qwp.glyphs import PRIME_PUNCT, RELIC_GLYPHS, VEIL_GLYPHS


@dataclass
class StringSegment:
    char: str
    delay: int = 0


@dataclass
class Line:
    number: int
    raw: str
    relics: list[str] = field(default_factory=list)
    veils: list[str] = field(default_factory=list)
    string_payload: list[StringSegment] | None = None
    prime_punct: list[str] = field(default_factory=list)


def _parse_string_body(body: str) -> list[StringSegment]:
    segments: list[StringSegment] = []
    delay = 0
    for ch in body:
        if ch in VEIL_GLYPHS:
            delay += 1
            continue
        if ch in RELIC_GLYPHS or ch in PRIME_PUNCT:
            continue
        segments.append(StringSegment(char=ch, delay=delay))
        delay = 0
    return segments


def parse_source(source: str) -> list[Line]:
    lines: list[Line] = []
    for idx, raw in enumerate(source.splitlines(), start=1):
        relics: list[str] = []
        veils: list[str] = []
        prime_punct: list[str] = []
        string_payload: list[StringSegment] | None = None

        if raw.count("⸺") >= 2:
            first = raw.index("⸺")
            last = raw.rindex("⸺")
            if first < last:
                string_payload = _parse_string_body(raw[first + 1 : last])

        for ch in raw:
            if ch in RELIC_GLYPHS:
                relics.append(ch)
            elif ch in VEIL_GLYPHS:
                veils.append(ch)
            elif ch in PRIME_PUNCT:
                prime_punct.append(ch)

        lines.append(
            Line(
                number=idx,
                raw=raw,
                relics=relics,
                veils=veils,
                string_payload=string_payload,
                prime_punct=prime_punct,
            )
        )
    return lines


def visible_repr(raw: str) -> str:
    out: list[str] = []
    for ch in raw:
        if ch in VEIL_GLYPHS:
            out.append(f"<{VEIL_GLYPHS[ch]}>")
        else:
            out.append(ch)
    return "".join(out)
