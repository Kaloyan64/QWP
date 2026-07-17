"""Relic-glyph semantics keyed by line_number mod 7."""

from __future__ import annotations

from enum import Enum, auto

RELIC_GLYPHS = frozenset("⸮⸸⸹⸺⸻⸼⸽⸾⸿")
VEIL_GLYPHS = {
    "\u200b": "ZWSP",
    "\u200c": "ZWNJ",
    "\u200d": "ZWJ",
    "\ufeff": "BOM",
}
PRIME_PUNCT = frozenset(".,:;!?~")


class Op(Enum):
    NOP = auto()
    LOOM_ROTATE2 = auto()
    EMIT_BYTE = auto()
    INGEST_STDIN = auto()
    XOR_LOOM = auto()
    JUMP_MOON = auto()
    HALT = auto()
    ADD = auto()
    SUB = auto()
    MUL = auto()
    DIV = auto()
    MOD = auto()
    NAND = auto()
    NOR = auto()
    COMPARE = auto()
    SWAP_13 = auto()
    REVERSE_LOOM = auto()
    DUP_SLOT2 = auto()
    DELETE_SELF = auto()
    REWRITE_NEIGHBOR = auto()
    PRAY = auto()
    OPEN_STRING = auto()
    CLOSE_STRING = auto()
    OPEN_REGRET = auto()
    CLOSE_REGRET = auto()
    COMMENT = auto()
    UNCOMMENT = auto()
    BOTH = auto()
    CALL = auto()
    RETURN_MAYBE = auto()
    TAIL_CALL = auto()
    YIELD_TUESDAY = auto()
    IMPORT_VOID = auto()
    EXPORT_SHAME = auto()
    RECURSE = auto()
    IF_GT = auto()
    IF_EQ = auto()
    IF_TUESDAY = auto()
    IF_LIE = auto()
    ELSE = auto()
    ELIF = auto()
    ENDIF = auto()
    PRINT_CHAR = auto()
    PRINT_LOOM = auto()
    PRINT_LIE = auto()
    PRINT_PREVIOUS = auto()
    PRINT_STDERR_SWAP = auto()
    PRINT_DEVNULL = auto()
    PRINT_SELF = auto()
    CONDENSE_CHAR = auto()
    PHASE_TICK = auto()


# line_mod -> glyph -> Op
TABLE: dict[str, list[Op]] = {
    "⸮": [
        Op.NOP,
        Op.LOOM_ROTATE2,
        Op.EMIT_BYTE,
        Op.INGEST_STDIN,
        Op.XOR_LOOM,
        Op.JUMP_MOON,
        Op.HALT,
    ],
    "⸸": [
        Op.ADD,
        Op.SUB,
        Op.MUL,
        Op.DIV,
        Op.MOD,
        Op.NAND,
        Op.NOR,
    ],
    "⸹": [
        Op.COMPARE,
        Op.SWAP_13,
        Op.REVERSE_LOOM,
        Op.DUP_SLOT2,
        Op.DELETE_SELF,
        Op.REWRITE_NEIGHBOR,
        Op.PRAY,
    ],
    "⸺": [
        Op.OPEN_STRING,
        Op.CLOSE_STRING,
        Op.OPEN_REGRET,
        Op.CLOSE_REGRET,
        Op.COMMENT,
        Op.UNCOMMENT,
        Op.BOTH,
    ],
    "⸻": [
        Op.CALL,
        Op.RETURN_MAYBE,
        Op.TAIL_CALL,
        Op.YIELD_TUESDAY,
        Op.IMPORT_VOID,
        Op.EXPORT_SHAME,
        Op.RECURSE,
    ],
    "⸼": [
        Op.IF_GT,
        Op.IF_EQ,
        Op.IF_TUESDAY,
        Op.IF_LIE,
        Op.ELSE,
        Op.ELIF,
        Op.ENDIF,
    ],
    "⸽": [
        Op.PRINT_CHAR,
        Op.PRINT_LIE,
        Op.PRINT_PREVIOUS,
        Op.PRINT_LOOM,
        Op.PRINT_STDERR_SWAP,
        Op.PRINT_DEVNULL,
        Op.PRINT_SELF,
    ],
    "⸾": [Op.PHASE_TICK] * 7,
    "⸿": [Op.CONDENSE_CHAR] * 7,
}


def resolve(glyph: str, line_number: int) -> Op:
    ops = TABLE.get(glyph)
    if ops is None:
        return Op.NOP
    return ops[(line_number - 1) % 7]


def is_prime_line(n: int) -> bool:
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True
