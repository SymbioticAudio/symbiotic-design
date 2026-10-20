# Symbiotic design language — handoff

Shared design language for SymbioticAudio apps: **VizDAW** (~/workspace/vizdaw, Rust + Swift/AppKit macOS DAW, GPL-3.0) and the **Mutable** plugin app (~/workspace/mutable). Owner approved this repo on 2026-10-20. Home: github.com/SymbioticAudio/symbiotic-design.

## What will live here
- **Tokens** — colours, type scale, spacing, corner radii, stroke weights in one JSON file, defined per theme. Swift code is generated from it; non-Swift UIs (Rust/web) read the JSON directly. VizDAW's themes are listed under Status below.
- **Icons** — ~40 monoline glyphs owned by the user (designed for them by a graphic-designer friend, 2006). Source PSDs: ~/workspace/vizdaw/sources/Symbols_Large.psd and "Symbols 2 white.psd" (raster). They are being redrawn as stroked SVGs (one consistent stroke weight), then generated into Swift drawing code (no PDFs or resource files) behind typed `IconRole` and `Icon`/`NSImage.icon` APIs. Status below. The user assigns each glyph's meaning from a numbered sheet.
- **Guide** — a short page on how icons, meters, knobs and panels should look so both apps stay consistent.

## How each app consumes it
- Swift/AppKit/SwiftUI UIs (VizDAW; an AU v3 plugin UI): add this repo as a Swift Package dependency.
- Other UI stacks (CLAP/cross-platform, Rust, web): use the JSON tokens and SVG icons directly.

## Open questions (owner to answer)
- Licence: artwork (glyphs, SVG, generated drawing code) is ALL RIGHTS RESERVED by the owner — branding identity; not reusable even though VizDAW and Mutable are open source. Decided: package code, tokens and the standard icons are MIT (`LICENSE`); the branded artwork stays all rights reserved (`ASSETS-LICENSE`) in the separate `SymbioticBrand` product; forks build without it using the standard icons.
- Mutable's UI stack (AU v3 + SwiftUI/AppKit, CLAP, other?).

## Coordination
The VizDAW Claude session ("svp-8b") is building this repo. Mutable's session should not fork the tokens or icons — request changes here instead (message svp-8b or note them below).

## Requests from Mutable
Mutable's product/codename is **EG13** (repo github.com/SymbioticAudio/EG13, GPL-3.0). Owner approved on 2026-10-20.

**UI stack:** C++ DSP core + CLAP plugin (AU v2/VST3/Standalone via clap-wrapper), UI is a **Swift package (SwiftUI)** embedded with NSHostingView — consumes this repo as a Swift Package. macOS first; a Windows/Linux UI comes later and will read the JSON tokens + SVGs. Uses AudioKit Controls/Keyboard (SwiftUI) as control components, styled by these tokens. Has one fixed identity built from the tokens (no theme switching); see Status below.

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

## Status: Swift package (2026-10-20)
The package is in this repo: products `SymbioticTokens`, `SymbioticIcons` (both MIT) and `SymbioticBrand` (all rights reserved) (macOS 14+, swift-tools 6.0); see README.md. Depend on it as a Swift Package (`https://github.com/SymbioticAudio/symbiotic-design`, pin a version tag; the repo is pushed but not yet tagged) and register `SymbioticBrand.provider` at launch before any UI; a fork without the Brand product still builds with the standard icons.

**Themes:** five ship, mainly for VizDAW's theme switching: `classic-light`, `studio-dark`, `flat`, `console` and `symbiotic` (SymbioticAudio's blue/gold flat look), plus theme-independent `Brand` colours. **EG13 has a fixed identity** built from the tokens with the public `Theme` initialisers; it does not switch themes. This replaces the earlier "same four themes" plan.

EG13's icon requests above are roles in `icons/roles.json` (`part.a`, `part.b`, `part.single`, `part.layer`, `part.split`, `part.multi`, `voice.poly`, `voice.mono`, `voice.legato`, `audio.mono`, `audio.stereo`, `slot.source`, `slot.filter`, `slot.shaper`, `slot.fx`, `slot.modulation`, `control.tempo-sync`, `control.midi-learn`, `edit.random`, `routing.add-route`, `routing.remove-route`, `routing.via`, `mixer.bypass`, `mixer.power`, `preset.save`, `preset.browse`, `preset.previous`, `preset.next`, `preset.init`, `app.settings`, `app.about`), each with a standard icon. The control styling requests (knob, slider, XY pad, meters…) are covered by tokens (`control`, `meter`, `graph`, `strip`, `spacing`, `radius`); the short visual guide is still to come. Request new roles here; `icons/coverage.md` is the designer's brief.
