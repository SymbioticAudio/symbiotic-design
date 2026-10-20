# symbiotic-design: tokens, icon roles and the Swift package

Status: approved in conversation 2026-10-20 (sections 1–3); this document awaits the owner's review.

## 1. Intent

One design language for SymbioticAudio's apps: **VizDAW** (Rust + Swift/AppKit DAW, GPL-3.0) and **EG13** (CLAP/AU synth plugin with a SwiftUI UI, GPL-3.0). Both apps consume this repository as a Swift package. EG13's later Windows/Linux UI reads the same JSON and SVG files directly.

Success means:
- both apps draw every icon and colour through this package, by role, not by file name;
- the owner's branded artwork stays all rights reserved, and an open-source fork that drops it still builds and shows a complete standard icon set;
- the five planned themes exist from the first release with starter values, and their final visual design (VizDAW SP7) changes values only, never the code that uses them.

Owner decisions this spec rests on:
- Scope **A**: token structure and all five themes now; starter values; real palettes later.
- Icons as **generated code** (approach 1), split into three products along the licence line.
- Branded artwork © Westlee Latta, all rights reserved (`ASSETS-LICENSE`); code, tokens and standard icons MIT (`LICENSE`). Credit: original glyph designs by Clayton Hibbert.
- Standard (industry-conventional) icons are drawn in-house in the house style; SF Symbols are never shipped as assets.

Out of scope: wiring the package into VizDAW (a later VizDAW plan) or EG13 (its own session), the final palettes of the five themes (VizDAW SP7 designs them; `symbiotic` is the owner's and already has real values), and new branded glyphs (the owner's designer draws those from `icons/coverage.md`).

## 2. Design tokens

### 2.1 Source
`tokens/tokens.json` holds:
- `tokens`: every token name, grouped by kind, each with a one-line description;
- `themes`: five themes, each with `id`, `appearance` (`light` | `dark`) and a value for **every** token.

The generator refuses to build if any theme lacks a token or defines an unknown one.

### 2.2 Theme IDs
Neutral IDs; no vendor names anywhere in code or files: `classic-light`, `studio-dark`, `flat`, `console`, `symbiotic`. User-facing names are chosen in SP7.

`symbiotic` is the owner's flat blue-and-gold look from symbioticaudio.org; it is offered as a theme, never the default.

### 2.3 Token groups
- **surface**: window, panel, raised, inset, separator, selection, focusRing
- **text**: primary, secondary, disabled, inverse
- **accent**: accent, onAccent
- **state**: record, play, solo, mute, warning, error, offline
- **meter**: background, low, mid, high, clip
- **graph**: line, fill, grid, handle, handleSelected (waveforms, envelopes, LFO, scope)
- **control** (colour by function, present in every theme): gain, eqLow, eqLowMid, eqHighMid, eqHigh, send, pan, dynamics, filter
- **strip** (colour by type): channel, instrument, auxReturn, bus, master
- **brand** (theme-independent: the same values in every theme; the symbioticaudio.org palette): gold, cyan, cyanInk, ink, paper, rule
- **spacing**: xxs, xs, s, m, l, xl (points)
- **radius**: none, s, m, l (points)
- **iconStroke**: s16, s24, s32 (stroke width in points at each icon size)
- **type**: caption, body, label, title, display (system font; size and weight)

### 2.4 Values
- Colours are `#RRGGBB` or `#RRGGBBAA` (sRGB).
- A colour may instead be `{ "system": "<macOS semantic colour name>", "fallback": "#RRGGBB" }`. Swift uses the system colour; other platforms use the fallback.
- Starter values: `classic-light` and `studio-dark` track macOS system colours with fallbacks; `flat` and `console` get rough placeholder palettes, clearly marked as placeholders in the file; `symbiotic` takes its values from the symbioticaudio.org palette.

### 2.5 Swift output (product SymbioticTokens, MIT)
- A generated `Theme` struct with typed groups: `theme.meter.clip`, `theme.control.eqLow`, `theme.spacing.m`.
- Colours expose both `SwiftUI.Color` and `NSColor`.
- `Theme.classicLight`, `.studioDark`, `.flat`, `.console`, `.symbiotic`, and `Theme.all`.
- A SwiftUI environment value `\.symbioticTheme` (default `.classicLight` or `.studioDark` by appearance).

### 2.6 Checks
- Completeness (every theme, every token), unknown keys, malformed values.
- Contrast: each text colour against each surface it is declared to sit on (pairs listed in `tokens.json`) is checked against WCAG AA (4.5:1 for body text, 3:1 for large text and icons). Pairs below the threshold are reported as warnings per theme in the generator output and in `tokens/contrast.md`; they do not fail the build (the starter palettes are not final).

## 3. Icons

### 3.1 Sources
- `icons/svg/glyph-NN.svg`: the owner's 41 glyphs (all rights reserved).
- `icons/standard/<name>.svg`: 57 standard icons (MIT); more are added as roles need them.
- Both sets: `viewBox="0 0 24 24"`, monoline stroke in `currentColor`, the shared house style.
- Supported SVG subset: `svg`, `g` (with `transform` of translate/scale/rotate/matrix), `line`, `circle`, `ellipse`, `rect`, `polyline`, `polygon`, `path` (all commands, absolute and relative, including arcs), attributes `fill`, `stroke`, `stroke-width`, `stroke-linecap`, `stroke-linejoin`. Anything else is an error, never a silent omission.

### 3.2 Role catalogue
`icons/roles.json` lists every role the apps use:
- `id` (dotted, e.g. `transport.play`, `mode.loop`, `editor.notation`, `routing.send`, `brand.logo`);
- `standard`: the standard icon name (**required**, except `brand.logo`);
- `brand`: the glyph ID, if one draws this role;
- `label`: the default accessibility label.

The first catalogue covers what VizDAW uses today (transport, editing, zoom, warnings, media offline), VizDAW's planned SP5–SP7 features (record, monitor, punch, takes, editor modes, notation marks, mixer), and EG13's request list in `HANDOFF.md`. The owner's 12 confirmed glyph roles map to their roles; unconfirmed glyphs are left unmapped until the owner assigns them.

`brand.logo` falls back to a text wordmark ("SymbioticAudio"), never to another drawing.

### 3.3 Coverage report
The generator writes `icons/coverage.md`:
- **Brief for the designer**: roles with no brand glyph.
- **To draw in-house**: roles whose standard icon does not exist yet (e.g. fermata, natural sign, clefs), drawn as plain conventional MIT symbols.
- Glyphs not yet assigned to any role.

### 3.4 Swift output
- **SymbioticIcons** (MIT): the standard icons as generated drawing code; the generated `IconRole` type (so a misspelt role is a compile error); `Icon(_ role:, size:)` as a SwiftUI view that uses the theme's `iconStroke` for its size and the current foreground colour; `NSImage.icon(_ role:, size:)` returning a template image; `Icons.register(_ provider:)`.
- **SymbioticBrand** (all rights reserved; every generated file starts with the `ASSETS-LICENSE` notice): the glyphs and the logo as generated drawing code, and `SymbioticBrand.provider`.
- Dependency direction: SymbioticBrand depends on SymbioticIcons, never the reverse.
- Resolution: a role draws its brand glyph when a brand provider is registered and maps that role, otherwise its standard icon.
- Apps register the brand provider with one guarded line (`#if canImport(SymbioticBrand)`). A fork removes only the SymbioticBrand dependency.
- Stroke scales with size: each icon is drawn on its 24-unit grid scaled to the requested size, with the stroke taken from `iconStroke` for that size rather than scaled.
- No resource files ship, so the package works inside plugin bundles hosted by other apps.

## 4. Repository layout and tooling

```
Package.swift                    swift-tools 6.0, macOS 14; products SymbioticTokens, SymbioticIcons, SymbioticBrand
tokens/tokens.json
tokens/contrast.md (generated)
icons/svg/, icons/standard/, icons/glyphs.json, icons/standard.json, icons/roles.json, icons/coverage.md
tools/generate.py                stdlib-only Python 3: validates, writes Sources/*/Generated/ and icons/coverage.md
tools/contact_sheet.py           existing
tools/references.py              renders reference PNGs of every SVG with headless Chrome
Sources/SymbioticTokens/{Generated/, *.swift}
Sources/SymbioticIcons/{Generated/, *.swift}
Sources/SymbioticBrand/{Generated/, *.swift}
Tests/...                        Swift tests; tools/tests/ Python tests
```

- Generated Swift is committed; apps never run the generator, and no SwiftPM build plugins are used.
- Swift builds and tests run with the Command Line Tools (`DEVELOPER_DIR=/Library/Developer/CommandLineTools`); the Xcode licence is not accepted on the development Mac.
- Floor macOS 14 for all three products: the owner moved EG13 to macOS 14 (2026-10-20) so both apps share one floor that CI can test.

## 5. Testing

- **Python** (`unittest`): the SVG subset reader and its error cases; arc-to-Bézier conversion against known points; transforms; token validation and contrast maths.
- **Fidelity** (Swift): every icon rendered at 48 px by the generated code is compared with its reference PNG (headless Chrome render of the source SVG); mean per-pixel difference below a stated tolerance. Reference PNGs are committed and regenerated by `tools/references.py`.
- **Behaviour** (Swift): every role resolves; with no brand provider every role draws its standard icon and `brand.logo` yields the wordmark; with the provider, mapped roles draw glyphs; every theme exposes every token; `NSImage.icon` returns a template image of the requested size.
- **CI** (GitHub Actions, macOS): run the generator and fail on any diff with the committed output; run the Python and Swift tests.

## 6. Versioning

Semantic version tags (`0.1.0` first). Apps pin a version. Tags and pushes are made only with the owner's approval.
