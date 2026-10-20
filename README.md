# symbiotic-design

A design library for SymbioticAudio apps — the shared design language of
VizDAW and EG13: design tokens, icons and a short visual guide.

## Licences (two of them)

- **Code, design tokens and the standard icon set** (`icons/standard/`):
  MIT — see `LICENSE`.
- **Branded artwork** (`source-art/`, `icons/svg/glyph-*`, the logo and
  anything rendered from them): **all rights reserved** — see
  `ASSETS-LICENSE`. Public visibility grants no rights to reuse it.

## Contents

- `source-art/` — the master glyph artwork (Photoshop).
- `icons/` — the glyphs as 24-unit monoline SVGs, their roles
  (`glyphs.json`) and a contact sheet.
- `icons/standard/` — 57 standard icons (transport, edit, app, audio:
  play, stop, record, undo, settings, solo, mute…) drawn in the same house
  style, MIT-licensed; index in `icons/standard.json`.
- `tools/contact_sheet.py` — rebuilds `icons/contact-sheet.html`.
- `HANDOFF.md` — status and requests between the app projects.

Coming next: per-theme tokens (JSON → Swift), vector PDF exports and a
Swift package.

## Special thanks

Special thanks to **Clayton Hibbert** for the original glyph designs.
