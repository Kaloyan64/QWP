# QW+ (Quixotic Whitespace Plus)

An esoteric scripting language where identifiers are invisible, memory rotates under your feet, and every instruction rewrites the source code that remains.

## Quick Start

```bash
pip install -e .
qwp examples/hello.qwp
      or
cd examples
qwp hellp.qwp
```

Force a non-Tuesday run (recommended for first success):

```bash
qwp examples/hello.qwp --day monday
      or
cd examples
qwp hello.qwp --day monday
```

## Core Concepts

- **Veil-glyphs** (`U+200B`, `U+200C`, `U+200D`, `U+FEFF`) — invisible identifiers and phase offsets
- **Relic-glyphs** (`⸮`, `⸸`, `⸹`, `⸺`, `⸻`, `⸼`, `⸽`, `⸾`, `⸿`) — operators whose meaning depends on `line_number mod 7`
- **Leaky Loom** — circular byte tape; every command rotates left and evaporates the leftmost byte into Tuesday
- **Butterfly Engine** — each executed line mutates all remaining lines in the source
- **Gaslight Trilogy** — silent reversal, cross-file accusations, calendrical math

## Spec Reference

See the language design document in the repository wiki, or run:

```bash
qwp --spec
```

## Warning

Running the same program twice without edits may reverse your previous output. This is intentional. Exit code will still be 0.
