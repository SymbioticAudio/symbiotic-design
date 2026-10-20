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

## Requests from EG13 (2026-10-20, after 0.1.0)
EG13 depends on symbiotic-design exactly 0.1.0 (owner approved). EG13's identity changed: a fixed Mutable-Instruments-inspired look — mid-grey window, light aluminium module panels with dark legends, colour accents per module category; one palette, ignores macOS appearance; built with Theme's public initialisers.
- (a) Module-category colour tokens: source, filter, shaper, partFx, mod — legible as arcs and chips on light panels and on mid-grey. (Interim in EG13: control.eqHighMid / filter / dynamics / send / eqHigh.) → candidate for 0.2.0.
- (b) Part A / Part B colours: EG13 uses brand.cyan and brand.gold. Answer: acceptable — the brand group is constant across themes and is the owner's identity; dedicated part tokens only if a second app needs them.
- (c) Surfaces: "mid-grey window + light metal panel + dark legend" maps onto existing tokens — surface.window (mid-grey), surface.panel / surface.raised (aluminium), text.primary/secondary (dark legends on panels). EG13 sets those values in its own Theme; no new surface tokens needed for 0.1.0.
- (d) Hardware-style controls (shaded caps, skirt, ticks, indicator, value arc, mod ring) shared as a possible SymbioticControls product — awaiting the owner's decision. Until then EG13 builds them locally from tokens only, ready to upstream.
- (e) Seed values from EG13's mock for 0.2.0 (on aluminium #E4E4E0–#CACAC6 and mid-grey #8C8C89): category source #2E7D32, filter #B35900, shaper #C2185B, partFx #6A3FA0, mod #0077A8. Part ink on light panels: A = brand.cyanInk #0077A8; B = #9A7200 — proposed new constant `brand.goldInk` (gold's counterpart to cyanInk). EG13 surfaces for reference: header/keyboard bar #545452, window #8C8C89, placeholder panels #BDBDB9, LCD displays #1F2A22 / #1F2A2E.
- (f) Update (owner, 2026-10-20): EG13 owns its Mutable-Instruments-modelled palette (category + part colours) locally and is no longer bound by symbiotic-design for colours; it keeps using the library for icons, typography, spacing and control behaviour. So (a) category tokens and (e) brand.goldInk are no longer EG13 needs — keep only if VizDAW wants them. The owner prefers FLAT controls (layers: cap, skirt, ticks, indicator, value arc), not modelled 3D knobs — relevant if a shared SymbioticControls product goes ahead.
- (g) Owner's family rule (2026-10-20, via EG13): each SymbioticAudio plugin may have its own identity through COLOUR; icons, typography, layout conventions and knob/control design are SHARED across the family. So the library owns the shared control design (shape, layers, behaviour) and each app injects its colours — knob/slider colours via a style/palette parameter, not tied to theme tokens.
- (h) Owner likes the knobs in both references (AIR Flavor Pro: flat cap + indicator + thin coloured value arc; VCV/Mutable-style: black skirt, white or accent-filled cap, short indicator, colour label chips). Shared knob supports both as options: value arc on/off, cap plain or accent-filled, labels plain or chips; colours injected. Inspiration only — no third-party assets.
- (i) Owner also likes the subtle secondary ring inside the outer ring (Flavor Pro style): knob style gets an optional faint inner ring layer between the outer ring/value arc and the cap.
- (j) EG13 mock approved by the owner (2026-10-20, "looks good for now"). EG13's palette is its own (not a library concern). Knob revised by the owner: flat, no shading, NO ticks; the value arc sits INSIDE the black skirt band (fills min→value over a ~14% white track) — layers outside→in: skirt, track+arc in the skirt band, cap, indicator. Proportions: small skirt r17 / cap r10.5; hero skirt r34 / cap r23. Caps plain white, accent-filled or black; indicator black on white/accent caps, white on black caps; arc = accent (accent caps), part colour (plain caps), light grey (dark master knobs). Labels plain uppercase or accent chip with white text. Shared-knob options: value arc on/off + placement (skirt band | outside), inner ring on/off, ticks on/off, cap plain|accent|black, labels text|chips, colours injected. EG13 defaults: arc-in-skirt on, ticks off, inner ring off.
- (k) Owner decision: controls move into the library LATER — EG13 builds them locally first (drawing separate from behaviour, colours injected), then upstreams them as SymbioticControls.
