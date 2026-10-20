# Symbiotic design language — handoff

Shared design language for SymbioticAudio apps: **VizDAW** (~/workspace/vizdaw, Rust + Swift/AppKit macOS DAW, GPL-3.0) and the **Mutable** plugin app (~/workspace/mutable). Owner approved this repo on 2026-10-20. Planned home: github.com/SymbioticAudio/symbiotic-design (not created yet).

## What will live here
- **Tokens** — colours, type scale, spacing, corner radii, stroke weights in one JSON file, defined per theme. Swift code is generated from it; non-Swift UIs (Rust/web) read the JSON directly. VizDAW plans four themes (SP7): a light theme, a dark theme, a flat "Metro"-style theme and a realistic console-style theme — tokens must cover all four.
- **Icons** — ~40 monoline glyphs owned by the user (designed for them by a graphic-designer friend, 2006). Source PSDs: ~/workspace/vizdaw/sources/Symbols_Large.psd and "Symbols 2 white.psd" (raster). They are being redrawn as stroked SVGs (one consistent stroke weight), then exported as vector PDF template images (tinted by system colours) behind a typed Swift API, e.g. `SymbolIcon.loop`. The user assigns each glyph's meaning from a numbered sheet.
- **Guide** — a short page on how icons, meters, knobs and panels should look so both apps stay consistent.

## How each app consumes it
- Swift/AppKit/SwiftUI UIs (VizDAW; an AU v3 plugin UI): add this repo as a Swift Package dependency.
- Other UI stacks (CLAP/cross-platform, Rust, web): use the JSON tokens and SVG icons directly.

## Open questions (owner to answer)
- Licence: artwork (glyphs, SVG, PDF) is ALL RIGHTS RESERVED by the owner — branding identity; not reusable even though VizDAW and Mutable are open source. Proposed: package code + tokens MIT so open-source apps can link it; apps keep a fallback icon set so forks build without the branded art.
- Mutable's UI stack (AU v3 + SwiftUI/AppKit, CLAP, other?).

## Coordination
The VizDAW Claude session ("svp-8b") is building this repo. Mutable's session should not fork the tokens or icons — request changes here instead (message svp-8b or note them below).

## Requests from Mutable
Mutable's product/codename is **EG13** (repo github.com/SymbioticAudio/EG13, GPL-3.0). Owner approved on 2026-10-20.

**UI stack:** C++ DSP core + CLAP plugin (AU v2/VST3/Standalone via clap-wrapper), UI is a **Swift package (SwiftUI)** embedded with NSHostingView — consumes this repo as a Swift Package. macOS first; a Windows/Linux UI comes later and will read the JSON tokens + SVGs. Uses AudioKit Controls/Keyboard (SwiftUI) as control components, styled by these tokens. Will support the same four themes as VizDAW.

**Controls / tokens needed (guide + tokens):**
- Knob with modulation-range ring (bipolar amount shown around the knob)
- Slider (vertical/horizontal), XY pad, toggle, segmented control (4 options: Single/Layer/Split/Multi)
- Dropdown / engine selector, on-screen keyboard
- Envelope / multi-segment editor, LFO/function display, small oscilloscope
- Level meter (stereo), mod-matrix row (source → destination, amount, via)
- Slot panel / module card (header + controls), part tab (A/B)

**Icons needed:**
- Part A / Part B; Layer, Split, Multi
- Voice mode: poly, mono, legato; mono/stereo
- Slot categories: source, filter, shaper, FX, modulation
- Tempo sync, MIDI learn, random/dice, add route, remove route, via (link), bypass/power
- Preset: save, load/browse, previous, next, init; settings, about/info

## Standard icons (owner, 2026-10-20)
Both apps also use industry-standard icons (play, stop, record, return-to-zero/restart, pause, rewind/forward, loop, etc.) where a convention exists. These are drawn here in the house style (24-unit grid, 1.2 monoline stroke) as a separate `standard` icon set under a permissive licence — unlike the owner's branded glyphs, which stay all rights reserved. Do not use SF Symbols as shipped assets (Apple-platform-only licence; no Win/Linux).
