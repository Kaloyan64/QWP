"""QW+ runtime — non-linear execution with a rotating loom."""

from __future__ import annotations

import hashlib
import random
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TextIO

from qwp.butterfly import mutate_remaining, refresh_line_from_raw
from qwp.gaslight import (
    RunState,
    gaslight_math,
    is_tuesday,
    load_state,
    random_accusation,
    reverse_output,
    save_state,
    tuesday_add,
    tuesday_space_message,
)
from qwp.glyphs import Op, is_prime_line, resolve
from qwp.lexer import Line, parse_source
from qwp.loom import LeakyLoom


@dataclass
class CondensationItem:
    byte: int
    ticks: int


@dataclass
class Runtime:
    lines: list[Line]
    loom: LeakyLoom = field(default_factory=LeakyLoom)
    output: list[str] = field(default_factory=list)
    condensation: list[CondensationItem] = field(default_factory=list)
    stdin: TextIO = field(default_factory=lambda: sys.stdin)
    rng: random.Random = field(default_factory=random.Random)
    when: datetime | None = None
    syntax_fault: bool = False
    print_index: int = 0
    loaded_message: str = ""
    emit_armed: bool = False
    halted: bool = False
    prior_lines_snapshot: list[str] | None = None
    moon_phase: int = 3

    def tick_condensation(self) -> None:
        for item in self.condensation:
            if item.ticks > 0:
                item.ticks -= 1
            elif item.ticks == 0:
                self.loom.inject(item.byte ^ ((self.lines[0].number * self._weekday()) & 0xFF))
                item.ticks = -1

    def _weekday(self) -> int:
        if self.when:
            return self.when.weekday()
        return datetime.now().weekday()

    def rotate_and_tick(self, times: int = 1) -> None:
        for _ in range(times):
            self.tick_condensation()
            self.loom.rotate()

    def load_string_line(self, line: Line) -> None:
        if not line.string_payload:
            return
        self.condensation.clear()
        for seg in line.string_payload:
            self.condensation.append(CondensationItem(byte=ord(seg.char), ticks=seg.delay))
        self.loaded_message = "".join(seg.char for seg in line.string_payload)

    def execute_op(self, op: Op, line: Line, line_index: int) -> None:
        if op in {Op.NOP, Op.PRAY, Op.ENDIF, Op.ELIF, Op.COMMENT, Op.UNCOMMENT, Op.BOTH}:
            self.rotate_and_tick()
            return

        if op == Op.LOOM_ROTATE2:
            self.rotate_and_tick(2)
            return

        if op == Op.OPEN_STRING:
            self.load_string_line(line)
            self.rotate_and_tick()
            return

        if op == Op.CLOSE_STRING:
            self.rotate_and_tick()
            return

        if op == Op.SWAP_13:
            self.rotate_and_tick()
            self.loom.swap(1, 3)
            return

        if op == Op.REVERSE_LOOM:
            self.rotate_and_tick()
            self.loom.reverse()
            return

        if op == Op.DUP_SLOT2:
            self.rotate_and_tick()
            self.loom.duplicate_slot2()
            return

        if op == Op.XOR_LOOM:
            self.rotate_and_tick()
            self.loom.xor_all(line.number & 0xFF)
            return

        if op == Op.EMIT_BYTE:
            self.rotate_and_tick()
            self.emit_armed = True
            return

        if op == Op.PRINT_LOOM:
            self.rotate_and_tick()
            if not self.emit_armed and self.print_index == 0:
                return
            if self.print_index < len(self.loaded_message):
                self.output.append(self.loaded_message[self.print_index])
                self.print_index += 1
            else:
                value = self.loom.read()
                if value:
                    self.output.append(chr(value))
            return

        if op == Op.PRINT_CHAR:
            self.rotate_and_tick()
            self.output.append("⸽")
            return

        if op == Op.PRINT_LIE:
            self.rotate_and_tick()
            self.output.append("maybe")
            return

        if op == Op.PRINT_PREVIOUS:
            self.rotate_and_tick()
            return

        if op == Op.PRINT_SELF:
            self.rotate_and_tick()
            self.output.append("⸽")
            return

        if op == Op.INGEST_STDIN:
            self.rotate_and_tick()
            data = self.stdin.read(1)
            if data:
                self.loom.inject(ord(data[0]))
            return

        if op == Op.ADD:
            self.rotate_and_tick()
            a, b = self.loom.read(1), self.loom.read(2)
            self.loom.write(3, tuesday_add(a, b, self.when) & 0xFF)
            return

        if op == Op.SUB:
            self.rotate_and_tick()
            a, b = self.loom.read(1), self.loom.read(2)
            self.loom.write(3, gaslight_math(a - b, self.when) & 0xFF)
            return

        if op == Op.MUL:
            self.rotate_and_tick()
            a, b = self.loom.read(1), self.loom.read(2)
            self.loom.write(3, (a * b) & 0xFF)
            return

        if op == Op.DIV:
            self.rotate_and_tick()
            a, b = self.loom.read(1), max(self.loom.read(2), 1)
            self.loom.write(3, (a // b) & 0xFF)
            return

        if op == Op.MOD:
            self.rotate_and_tick()
            a, b = self.loom.read(1), max(self.loom.read(2), 1)
            self.loom.write(3, a % b)
            return

        if op == Op.HALT:
            self.halted = True
            return

        if op == Op.DELETE_SELF:
            line.raw = ""
            refresh_line_from_raw(line)
            return

        if op == Op.YIELD_TUESDAY:
            self.rotate_and_tick()
            if self.loom.tuesday_archive:
                self.loom.inject(self.loom.tuesday_archive[-1])
            return

        if op == Op.PHASE_TICK:
            self.rotate_and_tick()
            return

        if op == Op.CONDENSE_CHAR:
            self.rotate_and_tick()
            if self.condensation:
                item = self.condensation.pop(0)
                self.loom.inject(item.byte)
            return

        self.rotate_and_tick()

    def execute_line(self, line_index: int) -> None:
        line = self.lines[line_index]
        if is_prime_line(line.number):
            for ch in line.prime_punct:
                if ch == ";":
                    self.tick_condensation()

        if line.string_payload:
            self.load_string_line(line)

        for glyph in line.relics:
            if self.halted:
                return
            op = resolve(glyph, line.number)
            self.execute_op(op, line, line_index)
            if self.halted:
                return

        mutate_remaining(
            self.lines,
            line_index,
            self.prior_lines_snapshot,
            self.rng,
        )

    def choose_next_line(self, current: int) -> int | None:
        if self.halted:
            return None
        if current + 1 < len(self.lines):
            if len(self.lines) > 8 and self.rng.random() < 0.08:
                digest = hashlib.sha1(self.loom.as_bytes()).hexdigest()
                jump = int(digest[:2], 16) % len(self.lines)
                return jump
            return current + 1
        return None

    def run(self) -> str:
        if not self.lines:
            return ""

        idx = 0
        safety = 0
        while idx is not None and safety < 10_000:
            self.execute_line(idx)
            if self.halted:
                break
            idx = self.choose_next_line(idx)
            safety += 1

        text = "".join(self.output)
        return tuesday_space_message(text, self.when)


def _validate_source(source: str, path: Path, rng: random.Random) -> bool:
    scrubbed = source
    for block in re.findall(r"⸺([^⸺]*)⸺", source):
        scrubbed = scrubbed.replace(block, "")
    if any(ch.isalnum() for ch in scrubbed):
        return False
    if source.count("⸺") % 2 != 0:
        return False
    return True


def run_file(
    path: Path,
    *,
    seed: int | None = None,
    when: datetime | None = None,
    state_path: Path | None = None,
    gaslight_accuse: bool = True,
) -> tuple[str, int, str | None]:
    source = path.read_text(encoding="utf-8")
    rng = random.Random(seed)
    state_file = state_path or path.with_suffix(".qwstate")
    state = load_state(state_file)
    prior_snapshot = [ln.raw for ln in parse_source(source)]

    if not _validate_source(source, path, rng):
        if gaslight_accuse and rng.random() < 0.5:
            msg = random_accusation(path, len(source.splitlines()), rng)
            if state.last_success_output is not None:
                return reverse_output(state.last_success_output), 0, msg
            return "", 0, msg
        if state.last_success_output is not None:
            return reverse_output(state.last_success_output), 0, None
        return "", 0, None

    lines = parse_source(source)
    runtime = Runtime(
        lines=lines,
        rng=rng,
        when=when,
        prior_lines_snapshot=state.last_success_lines,
    )
    output = runtime.run()

    if is_tuesday(when) and output == "Hello World":
        output = tuesday_space_message(output, when)

    state.last_success_output = output
    state.last_success_lines = [ln.raw for ln in lines]
    save_state(state_file, state)
    return output, 0, None
