# symbiotic-design

A design library for SymbioticAudio apps — the shared design language of
VizDAW and EG13: design tokens, icons and a Swift package that draws them.

## Licences (two of them)

- **Code, design tokens and the standard icon set** (`icons/standard/`):
  MIT — see `LICENSE`. The standard icons and the standard section of the
  contact sheet are MIT.
- **Branded artwork** (the owner's glyphs and logo, and anything rendered
  from them): **all rights reserved** — see `ASSETS-LICENSE`, which lists
  the reserved paths (among them `source-art/`, `icons/svg/glyph-*`,
  `icons/glyphs.json`, `icons/coverage.md`, `Sources/SymbioticBrand/`, the
  brand tests and glyph reference renders). Public visibility grants no
  rights to reuse it. Every generated `SymbioticBrand` file starts with the
  `ASSETS-LICENSE` notice.

## Swift package

Add `https://github.com/SymbioticAudio/symbiotic-design` (pin a version tag),
macOS 14 or later. Three products:

| Product | Licence | What it gives you |
|---|---|---|
| `SymbioticTokens` | MIT | `Theme` with typed groups (`theme.meter.clip.color`, `theme.spacing.m`, `theme.type.body.font`), the themes below, `Theme.all`, the theme-independent `Brand` colours, and the SwiftUI environment value `\.symbioticTheme` |
| `SymbioticIcons` | MIT | the standard icons as drawing code, `IconRole`, `Icon(_:size:)` (SwiftUI), `NSImage.icon(_:size:theme:)` (template image), `Icons.register(_:)` |
| `SymbioticBrand` | all rights reserved | the owner's glyphs and logo as drawing code, and `SymbioticBrand.provider` |

```swift
import SymbioticIcons
#if canImport(SymbioticBrand)
import SymbioticBrand
#endif

// once, at launch, before any UI is created
#if canImport(SymbioticBrand)
Icons.register(SymbioticBrand.provider)
#endif

// anywhere
Icon(.transportPlay, size: 16)                 // SwiftUI, current foreground style
NSImage.icon(.modeLoop, size: 16, theme: .studioDark)   // AppKit template image
```

A role draws its brand glyph when the brand provider is registered and maps
that role, otherwise its standard icon. `brand.logo` without the provider is
the text wordmark "SymbioticAudio". A fork removes only the `SymbioticBrand`
dependency and still has a complete icon set. After removing the Brand
product, clean the build folder (a stale `SymbioticBrand` module in `.build`
or DerivedData can make `canImport` succeed and then fail at link time). The
package ships no resource files, so it works inside plugin bundles.

Icons are drawn on their 24-unit grid scaled to the requested size; the
stroke width comes from the theme's `iconStroke` token for that size
(`s16`, `s24`, `s32`, interpolated between them and proportional outside).

## Themes

Five themes ship: `classic-light`, `studio-dark`, `flat`, `console` and
`symbiotic` (SymbioticAudio's blue-and-gold flat look; it is not the default).
They are mainly for VizDAW, which lets the user switch. The six `Brand` colours
(gold, cyan, cyan ink, ink, paper and rule) are the same in every theme.

An app can build its own `Theme` with the public initialisers; EG13 does this
with one fixed custom palette made from the tokens and has no theme switching.

A theme re-pins macOS system colours to its own light or dark appearance, so
`classic-light` stays light when macOS is in Dark Mode.

### Applying a theme

For SwiftUI, `.symbioticTheme(_:)` sets both `\.symbioticTheme` and
`\.colorScheme`, so icons (which follow the foreground style) match the
theme even against the OS appearance:

```swift
ContentView().symbioticTheme(.classicLight)
```

For AppKit, set the window's `appearance` (or, in a plugin, the
`NSHostingView`'s) to `NSAppearance(named: theme.appearance.nsAppearanceName)`
and pass `theme:` to `NSImage.icon`. To honour Increase Contrast, use
`theme.appearance.nsAppearanceName(highContrast: NSWorkspace.shared.accessibilityDisplayShouldIncreaseContrast)`
instead.

## Sources and generated files

| Source | Generated from it |
|---|---|
| `tokens/tokens.json` | `Sources/SymbioticTokens/Generated/`, `tokens/contrast.md` |
| `icons/standard/*.svg`, `icons/standard.json` | `Sources/SymbioticIcons/Generated/StandardIcon+Generated.swift` |
| `icons/roles.json` | `Sources/SymbioticIcons/Generated/IconRole+Generated.swift`, `icons/coverage.md` |
| `icons/svg/glyph-*.svg`, `icons/glyphs.json` | `Sources/SymbioticBrand/Generated/` |
| the SVGs above | `icons/contact-sheet.html` (`tools/contact_sheet.py`) |

After changing a source:

```bash
python3 tools/generate.py              # validate and regenerate (stdlib Python 3 only)
python3 tools/contact_sheet.py         # rebuild the contact sheet
python3 tools/references.py            # only if an SVG changed: reference PNGs (headless Chrome)
python3 -m unittest discover -s tools/tests
scripts/swift.sh test                  # Command Line Tools: export DEVELOPER_DIR=/Library/Developer/CommandLineTools first
```

Generated Swift is committed; apps never run the generator. CI regenerates
(including the contact sheet) and fails on any difference, runs the Python
and Swift tests on Xcode pinned to a Swift 6.2 or later toolchain, and builds
the `SymbioticTokens` and `SymbioticIcons` targets (`swift build --target`,
not `--product`, which SwiftPM ignores for automatic library products and
then builds everything) in a clean scratch folder, failing if any
`SymbioticBrand` module or object appears, to prove that a fork without
`SymbioticBrand` builds.

- `tokens/contrast.md` lists each text/surface pair declared in
  `tokens.json` against WCAG AA per theme; warnings do not fail the build.
- `icons/coverage.md` is the designer's brief: roles with no brand glyph,
  standard icons still to draw, and glyphs not yet assigned to a role.
- The SVG subset the generator accepts is listed in
  `docs/superpowers/specs/2026-10-20-design-system-design.md` section 3.1;
  anything else is an error.

## Checking by eye (owner)

Automated tests cannot judge looks. Before tagging a release:

- Open `icons/contact-sheet.html` and confirm the glyphs and standard icons
  look right.
- In an app, switch through all five themes in both light and dark macOS.
  `classic-light` must stay light in Dark Mode, with dark icons.
- Turn on Increase Contrast (System Settings, Accessibility, Display) and
  confirm the `classic-light` and `studio-dark` system colours switch to
  their high-contrast variants.
- Read `tokens/contrast.md` for any warnings you do not accept.

## Contents

- `source-art/` — the master glyph artwork (Photoshop).
- `tokens/` — `tokens.json` (the single source of every theme) and the
  generated `contrast.md`.
- `tools/` — the stdlib-Python generator, `contact_sheet.py`,
  `references.py` and their tests.
- `icons/` — the glyphs as 24-unit monoline SVGs, their roles
  (`glyphs.json`), the role catalogue (`roles.json`) and a contact sheet.
- `icons/standard/` — 107 standard icons (transport, edit, app, audio,
  editor, notation) drawn in the same house style, MIT-licensed; index in
  `icons/standard.json`.
- `HANDOFF.md` — status and requests between the app projects.

## Special thanks

Special thanks to **Clayton Hibbert** for the original glyph designs.
