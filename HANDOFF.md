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

## Requests from EG13 (2026-10-27, M7: reusable design choices offered for review)
The owner offers EG13's reusable design choices "for review and inclusion if appropriate", so other SymbioticAudio plugins can reuse the cap and display styles under their own colours. These five requests follow on from (d), (g), (h), (j) and (k) above (the shared SymbioticControls product, colours injected) and do not repeat them. Nothing here is urgent and EG13 changes nothing in this repo. If you include a component, EG13 will switch to the library's version in a later change so the two never drift apart.

Sources are in the EG13 repo (github.com/SymbioticAudio/EG13, branch `m7-release` at the time of writing), under `ui/EG13UI/Sources/EG13UI/`, written below as `Style/EG13KnobStyle.swift:106` and so on. EG13 spacing, radii and type come from this repo's studioDark theme (spacing xxs 2, xs 4, s 8, m 12, l 16, xl 24; radius s 3, m 6; caption 10 pt, label 11 pt); "token" below means one of those. All geometry is in points at 100 %; the editor scales the whole view 75–200 % (vector, so 200 % is the same drawing twice the size). Screenshots (rendered by `swift run --package-path ui/EG13UI EG13UIPreview --snapshot-design-requests <dir>`) are in `docs/requests/eg13/`.

### 1. Knob: cap and skirt band, cap emphasis colours as slots
`docs/requests/eg13/knob-cap-100.png`, `knob-cap-200.png` (top block: EG13 colours; bottom block: the same knobs with another plugin's colours injected).

Fixed geometry (identical in every plugin):
- Three sizes, as skirt diameter: large 48, medium 38, small 28 (`Style/EG13Layout.swift:19-21`).
- Cap diameter as a part of the skirt: large 23/34 (0.676), medium and small 10.5/17 (0.618) (`Style/EG13KnobStyle.swift:106-108`). Layers outside in: skirt (black disc), track plus value arc inside the skirt band, cap, indicator (`:264-309`). Flat: no gradients, no assets.
- Value arc: sits in the skirt band, centred in it, stroke 0.7 of the band width, butt caps (`:274-277`); band = (skirt − cap)/2 (`:272`). Sweep 270°, from 7:30 to 4:30 (`:116-127`). A bipolar value fills from the centre (origin 0.5) (`:268-269`, `:289`).
- Indicator: a capsule, width max(2, 0.07 × d), height 0.42 × cap, its centre 0.25 × cap from the cap's centre, rotated with the value (`:305-309`).
- Focus ring 2 pt around the whole knob (`:310-312`); disabled draws at 0.45 opacity (`:315`).
- Optional layers, off in EG13: ticks (band 0.08 × d, 11 ticks large / 7 otherwise, `:99-113`, `:217-235`), outside arc (ring 0.07 × d) and cap-rim arc (`:61-69`, `:276-279`).
- Label: uppercase, bold caption, either plain or on a chip (corner radius 2, 3 pt horizontal padding), wraps at spaces to at most two lines, never shrinks or cuts (`:358-417`).

Palette slots (colours are injected; EG13's values in brackets, `Style/EG13Palette.swift`, `Style/EG13KnobStyle.swift:12-24`):
- `skirt` (black), `plainCap` (white), `darkCap` (black), `track` (white at 0.14, `:42`), `tick` (legend at 0.6), `indicator` (black, for white and accent caps), `indicatorOnDark` (white, for the black cap), `label`, `chipText` (white), `focus`.
- Per cap emphasis, three style slots: `accent` (the arc, and the accent cap's fill), `accentInk` (the chip fill, dark enough for white text at 4.5:1). EG13 sets them in `knobStyle(for:)` (`EG13Palette.swift:72-91`): white cap gets a grey arc (`whiteKnobArc`, the panel grey) and a plain label; accent caps (pink, teal) get the accent as the arc and fill, its ink as the chip, and a chip label; the black cap gets a mid-grey arc (`blackKnobArc` #A8A8A5) and a plain label.
- The set of emphasis kinds is open: plain, accent A, accent B, black. A plugin supplies two accents; EG13 uses pink and teal.

Behaviour: cap colour never changes with the value; the emphasis is chosen per parameter (data, not code: `Model/EG13PanelLayout.swift:1-40`). Interaction (drag, fine drag, scroll, double-click reset, keyboard) is separate from drawing (`Controls/EG13ControlInteraction.swift`).

### 2. Modulation wave mark on the cap
`docs/requests/eg13/mod-wave-mark-100.png`, `mod-wave-mark-200.png` (each cap colour, pointer up and down, large and medium).

A small static wave on the cap says "a modulation route targets this control". It is never animated, shows no amount and is never the source's own shape.

Fixed geometry (`Style/EG13KnobStyle.swift:145-198`):
- Width 0.45 × the cap's diameter (`:151`); height (peak to trough) 0.3 × its width (`:153`); 1.5 sine cycles (`:155`, drawn as 32 line segments, `:201-213`).
- Stroke: max(2, 0.12 × cap radius), round caps and joins (`:175`; 1.5 pt at 75 % zoom, `:158`).
- Position: its centre 0.55 × the cap radius from the cap's centre, on the vertical axis (`:157`, `:178-180`): the bottom third while the pointer is in the upper half of the cap (pointer angle from horizontal, horizontal counts as upper), the top third when it is in the lower half, so the mark and the pointer never cross (`:163-167`). It moves only when the value takes the pointer across horizontal.
- Click area 14 × 10 pt at the mark (`:161`, `:183-187`); the click opens the knob's route list. It is also hidden from VoiceOver as an image; the route list is the accessible path.

Palette slot: one, the mark's ink: contrasting ink on the cap, dark #333333 on the white cap and white on accent and black caps (`:194-197`). The library should derive this from the cap's own fill (or take it as one slot).

### 3. LCD-style readout and button, with the MOTION n pattern and its popover
`docs/requests/eg13/lcd-readout-100.png`, `lcd-readout-200.png` (readout wells, stepper, menu well, a card header with MOTION 2, and the popover list below it; a popover itself cannot be image-rendered, so it is drawn as its content).

Fixed geometry:
- Readout well (`EG13LCDText`, `Style/EG13KnobStyle.swift:328-356`): text uppercased, monospaced bold, size max(label 11, 12) = 12 pt (kept at 12 so the green on grey reads at 75 %), one line, shrinks to 0.7 at the most; horizontal padding xs (4); background corner radius s (3); focus ring 2 pt in the `focus` slot. The well's own size is the caller's (stepper well 64 × 26, wide 88 × 26: `Controls/EG13Stepped.swift:53-54`, `Style/EG13Layout.swift:38-40`; menu well 24 high, 118 wide or 190 for engine names: `Controls/EG13EnginePicker.swift:62`, `EG13Layout.swift:36`).
- Stepper: a minus icon, the well, a plus icon (10 pt icons, xxs 2 apart), label under the well (`Controls/EG13Stepped.swift:50-60`). Menu well: a closed state with up/down chevrons (8 pt), opens the system menu.
- Segment row (`Views/EG13ControlView.swift:112-137`): wells in one LCD strip, 2 pt padding, each segment 24 high, 11 pt monospaced bold, horizontal padding s; the selected segment is filled with the lit colour and its text in the LCD background colour; the others lit text on the dark strip.
- MOTION n button (`Views/EG13MotionMenu.swift:9-42`): an LCD well, 18 high (`EG13Layout.swift:37`), text `MOTION n` (n = the number of routes into the card), monospaced bold max(caption 10, 11) = 11 pt, horizontal padding s (8), corner radius s. It exists only when n ≥ 1, sits in the card header after the engine controls, and moves to a second header line if the header is too narrow (`Views/EG13ModuleCard.swift:107-122`).
- Popover list (`:44-98`): width 340, background `lcdBackground`, padding xs, rows 26 high (`:65`) with a one-line `Source → Destination` text (12 pt monospaced bold, left), the amount as a signed percent ("+45 %", `Model/EG13Motion.swift:42-45`), and a level bar 44 × 6 (`:66`, `:102-118`): a track at 0.2 of the lit colour and a fill from the left of width = the source's live level (0...1; a fixed source such as velocity shows the empty track). Clicking a row selects that route (EG13 opens it in the matrix editor). The list follows the source live at 15 Hz.

Palette slots: `lcdBackground` (#383838), `lcdText` / lit segment (#AFD22C), `focus`; the segment colours are the same two slots swapped. The level bar's track and fill derive from `lcdText`.

### 4. Mini trace display
`docs/requests/eg13/mini-trace-100.png`, `mini-trace-200.png` (a modulator card; the trace is at the right of the header).

A small LCD well showing the last two seconds of a modulation source, one min–max bar per display frame, so a fast LFO reads as a band and a slow envelope as a line.

Fixed geometry and behaviour (`Views/EG13ModTraceView.swift`, `Model/EG13ModTrace.swift`):
- Size 64 × 20, shrinking to 40 wide when the header is tight (`Views/EG13ModuleCard.swift:33-35`, `:94-95`); corner radius s (`:70`).
- 30 frames (2 s at 15 Hz, newest at the right) (`EG13ModTrace.swift:10-16`). Frame step = (width − 4)/29, 2 pt inset on every side (`EG13ModTraceView.swift:43-46`). Each frame is a vertical bar from its min to its max, at least 1 pt tall (`:59-62`), at 0.5 opacity of the ink and a line width of max(1, 0.8 × step) (`:67`); a line through the bars' middles, 1.2 pt, round joins, in full ink (`:68`). A frame with no data is a gap and breaks the line (`:57`).
- Scale: bottom-up 0...1 for a unipolar signal; centred −1...1 as soon as any frame in the window went negative, with a centre line at 0.25 opacity, 0.5 pt (`:8-20`, `:47-52`).
- Refresh: the model ticks at 30 Hz and pushes a trace frame every second tick, 15 Hz (`Model/EG13Synth.swift:236-247`). It goes quiet when idle: a window of gaps, or the same frame repeated for a full window, changes nothing, writes nothing and redraws nothing (`EG13ModTrace.swift:74-107`, notably `:89` and `:99`), so an idle plugin costs no UI work. The Canvas reads frames in place, no allocation per redraw (`:46-52`).
- The window also resets when the trace is hidden (Settings → modulation display off).

Palette slots: `lcdBackground` (well), `lcdText` (the ink; bars and line derive from it by opacity). The trace has no axes or labels of its own.

### 5. Card-column layout rules
`docs/requests/eg13/card-columns-100.png`, `card-columns-200.png` (the whole editor; the left column holds four module cards and the right column the four modulator cards, at one fixed window ratio).

These are layout rules for a plugin editor of module cards, not a component:
- Rules (`Views/EG13RootView.swift:64-104`, `Views/EG13ModuleCard.swift:173-201`, `Style/EG13Layout.swift:71-80`):
  1. Cards are as tall as their content (header strip 28, 6 padding, 4 row gap: `EG13Layout.swift:32-34`); the card width is fixed per column.
  2. Two columns end on one line: the strip is as tall as the taller column (up to the space between the header and the bottom bar).
  3. The shorter column spreads its gaps: free space is shared equally between its cards, never less than the minimum gap (8) (`spreadGap`); the cards keep their own heights.
  4. The bottom bar floats one gap (8) below the columns; spare window height collects at the bottom of the window, not between the strip and the bar.
  5. When the cards are taller than the space, the column scrolls and the bar sits at the bottom.
  6. Outer padding 12; the right column has a 28 high pane switch above it (a segment row, see 3).
- Dimensions at 100 %: window 1200 × 760; header 56; bottom bar 78; right column 470 wide (`EG13Layout.swift:10-16`, `:55`); knob cells 64 minimum (50 in the right column) and 96 at most, knob rows balanced (16 knobs that fit 10 per row go as two rows of 8: `gridShape`, `:82-90`).
- No colour slots beyond the panel surfaces (window, panel, raised header strip: EG13Theme maps them to the existing `surface.*` tokens, `Style/EG13Theme.swift:17-24`).
- Lower priority than 1–4: this is a design note for the guide; a layout helper (a spreading stack) is only worth adding if a second plugin needs the same behaviour. EG13's is `EG13SpreadStack` (`Views/EG13ModuleCard.swift:177-201`), about 25 lines of SwiftUI Layout.
