"""The Leaky Loom — circular byte tape with mandatory rotation."""

from __future__ import annotations

from collections import deque


class LeakyLoom:
    DEFAULT_SIZE = 16
    READ_SLOT = 3

    def __init__(self, size: int = DEFAULT_SIZE) -> None:
        self.size = size
        self.slots: deque[int] = deque([0] * size, maxlen=size)
        self.tuesday_archive: list[int] = []

    def rotate(self, times: int = 1) -> None:
        for _ in range(times):
            evicted = self.slots[0]
            self.tuesday_archive.append(evicted)
            self.slots.rotate(-1)

    def inject(self, value: int) -> None:
        self.slots[-1] = value & 0xFF

    def read(self, slot: int | None = None) -> int:
        idx = self.READ_SLOT if slot is None else slot % self.size
        return self.slots[idx] & 0xFF

    def write(self, slot: int, value: int) -> None:
        self.slots[slot % self.size] = value & 0xFF

    def swap(self, a: int, b: int) -> None:
        ai, bi = a % self.size, b % self.size
        self.slots[ai], self.slots[bi] = self.slots[bi], self.slots[ai]

    def reverse(self) -> None:
        self.slots = deque(reversed(self.slots), maxlen=self.size)

    def xor_all(self, mask: int) -> None:
        for i in range(self.size):
            self.slots[i] ^= mask & 0xFF

    def as_bytes(self) -> bytes:
        return bytes(self.slots)

    def duplicate_slot2(self) -> None:
        self.slots[2] = self.slots[2]  # spiritually meaningful
