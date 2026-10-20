# Symbiotic Design System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the symbiotic-design Swift package — design tokens for four themes, a role-based icon catalogue with in-house standard icons, and the owner's branded glyphs — all generated from JSON and SVG sources by a stdlib-only Python generator, with fidelity tests against headless-Chrome renders.

**Architecture:** `tools/generate.py` validates `tokens/tokens.json`, `icons/roles.json` and every SVG (through a strict SVG-subset reader that turns all geometry into absolute move/line/cubic/close operations), then writes committed Swift into `Sources/*/Generated/` plus two reports (`tokens/contrast.md`, `icons/coverage.md`). Three SwiftPM products split along the licence line: `SymbioticTokens` (MIT) ← `SymbioticIcons` (MIT) ← `SymbioticBrand` (all rights reserved). Hand-written Swift around the generated data provides the SwiftUI/AppKit API (`Theme`, `\.symbioticTheme`, `Icon`, `NSImage.icon`, `Icons.register`).

**Tech Stack:** Python 3 standard library (`unittest`, `xml.etree`, `json`); Swift 6 language mode, swift-tools 6.0, SwiftUI + AppKit + CoreGraphics, Swift Testing; headless Google Chrome for reference PNGs; GitHub Actions (macOS).

**Spec:** `docs/superpowers/specs/2026-10-20-design-system-design.md` (owner-approved; read it with this plan).

## Global Constraints

- Shell: every command block starts with `export DEVELOPER_DIR=/Library/Developer/CommandLineTools PYTHONDONTWRITEBYTECODE=1`. The Xcode licence is not accepted on the development Mac; `swift build`/`swift test` work through the Command Line Tools (Apple Swift 6.4). Never call `xcodebuild` or `xcrun`.
- All commands run from the repository root (`/Users/lattawb/workspace/symbiotic-design`, or the worktree you execute in).
- Swift builds and tests go through `scripts/swift.sh build|test` (Task 3), which adds `--build-system native` and the Swift Testing framework paths the Command Line Tools need.
- Python: Python 3 standard library only, no `pip install`, for `tools/` and `tools/tests/`. Tests run with `python3 -m unittest discover -s tools/tests`.
- Package floor: macOS 14, swift-tools 6.0, for all three products; the floor is the single constant `minimumMacOS` in `Package.swift`. macOS 14 APIs may be used.
- Products and licences: `SymbioticTokens` (MIT), `SymbioticIcons` (MIT), `SymbioticBrand` (all rights reserved; every Swift file in `Sources/SymbioticBrand/`, generated or hand-written, begins with the full `ASSETS-LICENSE` notice as `//` comments). `SymbioticBrand` depends on `SymbioticIcons`, never the reverse. MIT Swift files carry a `// MIT licence: see LICENSE.` line.
- Theme IDs are neutral: `classic-light`, `studio-dark`, `flat`, `console`. No vendor names in code or files.
- SF Symbols are never shipped as assets. No resource files ship in the package (it must work inside plugin bundles).
- Generated Swift is committed; apps never run the generator; no SwiftPM build plugins.
- Reference PNGs: headless Chrome, `"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new` (Task 8).
- Commits: stage by explicit path (never `git add -A` or `git add .`); never commit `.DS_Store` or `__pycache__`. Every commit message ends with exactly these two lines, naming the model you actually are in the first:
  `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`
  `Claude-Session: https://claude.ai/code/session_01F7df6grqTdqHgc2d2X359P`
- Never push, never tag (semantic version tags need the owner's approval). Do not edit the spec, `LICENSE` or `ASSETS-LICENSE`.
- No GUI or computer-use tools; everything is verified from the command line.
- Only the 12 glyphs whose `confidence` in `icons/glyphs.json` is `"confirmed by owner"` may be mapped to roles; all other glyphs stay unmapped.

## Review Focus

1. A user picks `classic-light` while macOS is in Dark Mode: system-colour tokens must still resolve to the light palette (pinned to the theme's appearance), not flip with the OS. Pinned by `lightThemeStaysLightInDarkMode` (Task 3).
2. A designer adds an SVG that uses something outside the subset (opacity, a colour, skew, `<text>`): the generator must fail naming the file and the feature, never draw it wrongly. Pinned by `Errors` in Task 1 and `test_unsupported_svg_fails` (Task 6).
3. Someone maps a guessed (unconfirmed) glyph to a role, or adds a role before its standard icon exists: the generator rejects the guess, and for a missing icon writes the coverage brief but leaves the Swift untouched. Pinned by `test_unconfirmed_glyph_is_rejected` (Task 4) and `test_missing_standard_icon_is_listed_and_no_swift_is_written` (Task 6).
4. Icons requested at sizes other than 16/24/32 (13 pt toolbar, 48 px tests): the image must be exactly the requested size and the stroke must follow the interpolation rule, not scale or vanish. Pinned by `iconStrokeIsExactAtTokenSizesAndScalesOutside` (Task 3) and `nsImageIsATemplateOfTheRequestedSize` with 13 (Task 6).
5. A contrast ratio just under the threshold (4.499:1) must not print as a passing-looking "4.50:1" next to a WARN. Pinned by `test_ratio_is_rounded_down` (Task 2).

## File Structure

```
Package.swift                                  products, targets, the minimumMacOS floor constant
scripts/swift.sh                               swift build/test with the flags the Command Line Tools need
.github/workflows/ci.yml                       regenerate-and-diff, Python tests, Swift build and tests
tokens/tokens.json                             token names, descriptions, contrast pairs, four themes
tokens/contrast.md                             generated WCAG report
icons/roles.json                               the role catalogue (120 roles)
icons/coverage.md                              generated designer brief
icons/standard/*.svg, icons/standard.json      106 standard icons (57 existing + 49 new) and their index
tools/svgsubset.py                             SVG subset reader: shapes, transforms, arcs -> cubics, bounds
tools/tokenlib.py                              token validation and WCAG contrast
tools/rolelib.py                               role validation and coverage report
tools/swiftgen_common.py                       Swift naming/number helpers shared by the generators
tools/swiftgen_tokens.py                       tokens -> Sources/SymbioticTokens/Generated/
tools/swiftgen_icons.py                        standard icons + roles -> Sources/SymbioticIcons/Generated/
tools/swiftgen_brand.py                        glyphs + role map -> Sources/SymbioticBrand/Generated/
tools/generate.py                              the command: validate everything, write everything
tools/references.py                            reference PNGs via headless Chrome
tools/contact_sheet.py                         existing; made location-independent
tools/tests/test_*.py                          unittest suites
Sources/SymbioticTokens/{ThemeColor,TypeStyle,Theme+Lookup}.swift + Generated/
Sources/SymbioticIcons/{IconDrawing,Icons,Icon,NSImage+Icon,IconBitmap}.swift + Generated/
Sources/SymbioticBrand/SymbioticBrand.swift + Generated/
Tests/SymbioticTokensTests/ThemeTests.swift
Tests/SymbioticIconsTests/{RoleTests,RenderTests,FidelityTests}.swift + References/*.png
Tests/SymbioticBrandTests/{BrandTests,BrandFidelityTests}.swift + References/*.png
```

## Rulings

Decisions the spec leaves open, made here so tasks do not re-decide them.

1. **Swift Testing, not XCTest**, run through `scripts/swift.sh`: with the Command Line Tools it adds `--build-system native` (the default Swift Build system fails to initialise there) and the framework search and rpath flags for `Testing`; when `DEVELOPER_DIR` is anything else (CI's Xcode) it runs plain `swift`.
2. **`tokens.json` shape:** `tokens.<group> = {kind: color|points|font, items: {name: description}}`; `contrast` is a list of `{text, on, use: body|large|icon}`; each theme has `id`, `appearance`, `placeholder`, `note`, `values.<group>.<name>`. A colour is `#RRGGBB`, `#RRGGBBAA`, or `{system, fallback}`; the fallback may carry alpha too (semi-transparent system colours such as `separatorColor`). System colour names are limited to an allow-list (`tokenlib.SYSTEM_COLORS`), which also generates the Swift `SystemColorName` enum.
3. **System colours are resolved in the theme's own appearance** (`NSColor(name:dynamicProvider:)` + `NSAppearance.performAsCurrentDrawingAppearance`), so `classic-light` stays light in Dark Mode and the four themes stay distinct.
4. **Generated type names carry the kind:** `Theme.TextColors`, `Theme.SpacingMetrics`, `Theme.TypeStyles` (avoids clashes with `SwiftUI.Text` and `Theme.Type`); property names are the spec's (`theme.meter.clip`, `theme.type.body`). Colours expose `.color` (SwiftUI) and `.nsColor` (AppKit); type styles expose `.font` and `.nsFont`.
5. **Icon stroke at any size:** exact token at 16, 24 and 32 pt; linear between them; proportional to `s16` below 16 and to `s32` above 32. Starter values 1.0 / 1.2 / 1.6 make 48 px exactly the SVG's own 2.4 px, which the fidelity tests rely on.
6. **Icons are generated data rendered by one shared renderer:** each icon is an `IconDrawing` literal of `IconShape`s holding `PathOp`s (`move`, `line`, `curve`, `close`). The Python reader converts arcs, quadratics, circles, ellipses and rounded rects to cubics and applies transforms, so Swift needs no SVG knowledge. Stroke weight is stored relative to the house stroke 1.2 (scaled by `sqrt|det|` of the transform); miter limit 4 (SVG's default) is set explicitly because CoreGraphics defaults to 10.
7. **SVG subset strictness:** `viewBox` must be `0 0 24 24`; `transform` only on `<g>` (spec wording); paints only `none`/`currentColor`; XML comments ignored; anything else raises `SvgError` naming the file.
8. **Confirmed glyph roles:** 05 → `editor.envelope`; 12 → `editor.notation-alternate`; 13 → `editor.notation`; 15 → `notation.fermata`; 23/24 → `monitor.phones-left`/`monitor.phones-right`; 29 → `routing.send`; 34 → `notation.repeat`; 35 → `notation.natural`; 38 → `editor.piano-roll`; 39 → `brand.logo`; 40 → `mode.loop`. The generator refuses any `brand` that is not owner-confirmed. `brand.logo` must not name a standard icon.
9. **49 new standard icons** are drawn in-house (Task 5) so every role has one; two categories are added (`editor`, `notation`). Several roles share an icon (`file.export`/`file.bounce`, `slot.fx`/`lane.input-fx`, `media.relink`/`routing.via`/`control.link`).
10. **Missing standard icon:** the generator still writes `icons/coverage.md` (it is the to-draw list) but exits 1 without touching any Swift.
11. **API additions beyond the spec's names:** `IconResolver` and `ResolvedIcon` (pure resolution, used by tests and previews), `Icons.unregister()`, `Icons.resolver`, `Icon(_:size:resolver:)`, `NSImage.icon(_:size:theme:resolver:)`, `Theme.named(_:)`, `Theme.standard(for:)`, `IconBitmap` (alpha masks for fidelity and app snapshot tests). The registry is lock-protected; only one test touches it, because Swift Testing runs suites of all test targets in parallel in one process.
12. **Wordmark:** `brand.logo` without a provider shows "SymbioticAudio" in the semibold system font at 0.75 x size; as an `NSImage` it is `size` high and as wide as the text.
13. **Fidelity:** 48 x 48 px, alpha channel only (black ink on transparent in both renders), mean absolute difference below 0.02. Measured while writing this plan: worst standard icon 0.008, worst glyph 0.008, and the closest *different* icon pair 0.07, so 0.02 separates both. References live in `Tests/<target>/References/`, are excluded from the targets and found through `#filePath` (no resources). Glyph references are all rights reserved.
14. **Legal texts are not edited.** `ASSETS-LICENSE` already covers "any PDF, PNG or other rendering generated from" the glyphs; the README states that `Sources/SymbioticBrand/` and `Tests/SymbioticBrandTests/References/` fall under it, and every brand Swift file carries the notice. The owner may add the paths to `ASSETS-LICENSE` later.
15. **`tools/contact_sheet.py`** had the repository's absolute path baked in; it now resolves `icons/` relative to itself (needed to run it in a worktree).
16. **CI** runs on `macos-15` with the runner's default Xcode toolchain, regenerates and fails on any change (`git status --porcelain` must be empty), then runs the Python and Swift tests. Reference PNGs are not regenerated in CI (Chrome versions vary).

---

### Task 1: SVG subset reader

Reads one icon SVG into absolute-coordinate shapes: every primitive becomes `M`/`L`/`C`/`Z` operations, arcs and quadratics become cubics, transforms are applied, and anything outside the spec §3.1 subset raises `SvgError`.

**Files:**
- Create: `tools/svgsubset.py`
- Test: `tools/tests/test_svgsubset.py`

**Interfaces:**
- Consumes: nothing.
- Produces (module `svgsubset`): `class SvgError(ValueError)`; `@dataclass Shape(ops: list, fill: bool, stroke: bool, weight: float = 1.0, cap: str = "butt", join: str = "miter")` where each op is `("M", x, y)`, `("L", x, y)`, `("C", x1, y1, x2, y2, x, y)` or `("Z",)`; `HOUSE_STROKE = 1.2`; `parse_svg_text(text: str, name: str = "icon") -> list[Shape]`; `parse_svg_file(path) -> list[Shape]`; `parse_path(d: str) -> list[tuple]`; `parse_transform(text: str) -> tuple` (6-tuple matrix); `arc_to_cubics(x1, y1, rx, ry, phi_deg, large, sweep, x2, y2) -> list[tuple]`; `bounds(shapes, samples=24) -> (x0, y0, x1, y1)` including half of each stroke.

- [ ] **Step 1: Write the failing test**

File: `tools/tests/test_svgsubset.py`

```python
import math
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import svgsubset as s  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[2]
HEAD = ('<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" '
        'fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="butt" stroke-linejoin="miter">')


def svg(body):
    return HEAD + body + "</svg>"


def close(test, got, want, places=6):
    test.assertEqual(len(got), len(want))
    for g, w in zip(got, want):
        test.assertAlmostEqual(g, w, places=places)


class Primitives(unittest.TestCase):
    def test_line_is_stroked_move_line(self):
        (shape,) = s.parse_svg_text(svg('<line x1="1" y1="2" x2="3" y2="4"/>'))
        self.assertEqual(shape.ops, [("M", 1, 2), ("L", 3, 4)])
        self.assertTrue(shape.stroke)
        self.assertFalse(shape.fill)
        self.assertAlmostEqual(shape.weight, 1.0)
        self.assertEqual((shape.cap, shape.join), ("butt", "miter"))

    def test_polygon_closes_and_polyline_does_not(self):
        poly, line = s.parse_svg_text(svg('<polygon points="1 1 5 1 5 5"/><polyline points="1,1 5,1"/>'))
        self.assertEqual(poly.ops[-1], ("Z",))
        self.assertEqual(line.ops, [("M", 1, 1), ("L", 5, 1)])

    def test_circle_is_four_cubics_through_the_extremes(self):
        (c,) = s.parse_svg_text(svg('<circle cx="12" cy="12" r="6" fill="currentColor" stroke="none"/>'))
        self.assertTrue(c.fill)
        self.assertFalse(c.stroke)
        self.assertEqual([op[0] for op in c.ops], ["M", "C", "C", "C", "C", "Z"])
        self.assertEqual(c.ops[0], ("M", 18, 12))
        close(self, c.ops[2][5:], (6, 12))

    def test_rect_with_rx_has_rounded_corners(self):
        (r,) = s.parse_svg_text(svg('<rect x="4" y="4" width="16" height="10" rx="2"/>'))
        self.assertEqual(r.ops[0], ("M", 6, 4))
        self.assertEqual(sum(1 for op in r.ops if op[0] == "C"), 4)

    def test_ellipse(self):
        (e,) = s.parse_svg_text(svg('<ellipse cx="12" cy="12" rx="6" ry="3"/>'))
        self.assertEqual(e.ops[0], ("M", 18, 12))
        close(self, e.ops[1][5:], (12, 15))

    def test_child_paint_overrides_root(self):
        (shape,) = s.parse_svg_text(svg('<line x1="0" y1="0" x2="1" y2="1" stroke-width="2.4" '
                                        'stroke-linecap="round" stroke-linejoin="bevel"/>'))
        self.assertAlmostEqual(shape.weight, 2.0)
        self.assertEqual((shape.cap, shape.join), ("round", "bevel"))

    def test_xml_comments_are_ignored(self):
        self.assertEqual(len(s.parse_svg_text(svg('<!-- note --><line x1="0" y1="0" x2="1" y2="1"/>'))), 1)


class Paths(unittest.TestCase):
    def ops(self, d):
        return s.parse_path(d)

    def test_absolute_and_relative_lines(self):
        self.assertEqual(self.ops("M1 1 L3 1 l0 2 H5 h1 V7 v-1 Z"),
                         [("M", 1, 1), ("L", 3, 1), ("L", 3, 3), ("L", 5, 3), ("L", 6, 3),
                          ("L", 6, 7), ("L", 6, 6), ("Z",)])

    def test_implicit_lineto_after_move(self):
        self.assertEqual(self.ops("m1 1 2 0 0 2"), [("M", 1, 1), ("L", 3, 1), ("L", 3, 3)])

    def test_compact_numbers(self):
        self.assertEqual(self.ops("M.5.5L-1-1"), [("M", 0.5, 0.5), ("L", -1, -1)])
        self.assertEqual(self.ops("M1e1,2E-1"), [("M", 10, 0.2)])

    def test_smooth_cubic_reflects_previous_control(self):
        ops = self.ops("M0 0 C0 1 1 2 2 2 S4 1 4 0")
        self.assertEqual(ops[2], ("C", 3, 2, 4, 1, 4, 0))

    def test_quadratic_becomes_cubic(self):
        ops = self.ops("M0 0 Q3 3 6 0")
        close(self, ops[1][1:], (2, 2, 4, 2, 6, 0))

    def test_smooth_quadratic_reflects(self):
        ops = self.ops("M0 0 Q3 3 6 0 T12 0")
        close(self, ops[2][1:], (8, -2, 10, -2, 12, 0))

    def test_close_returns_to_subpath_start_for_relative_moves(self):
        ops = self.ops("M2 2 l1 0 z m1 1 l1 0")
        self.assertEqual(ops[3], ("M", 3, 3))

    def test_packed_arc_flags(self):
        a = self.ops("M0 0 a1 1 0 011 1")
        b = self.ops("M0 0 a1 1 0 0 1 1 1")
        self.assertEqual(a, b)


class Arcs(unittest.TestCase):
    def point_on_circle(self, ops, cx, cy, r):
        for op in ops:
            if op[0] == "C":
                self.assertAlmostEqual(math.hypot(op[5] - cx, op[6] - cy), r, places=6)

    def test_half_circle_sweep_1_goes_through_the_top(self):
        # From (6,12) to (18,12) radius 6, sweep 1 (clockwise on screen): passes (12,6).
        ops = s.parse_path("M6 12 A6 6 0 0 1 18 12")
        self.assertEqual(len([o for o in ops if o[0] == "C"]), 2)
        close(self, ops[1][5:], (12, 6))
        close(self, ops[-1][5:], (18, 12))
        self.point_on_circle(ops, 12, 12, 6)

    def test_sweep_0_goes_through_the_bottom(self):
        ops = s.parse_path("M6 12 A6 6 0 0 0 18 12")
        close(self, ops[1][5:], (12, 18))

    def test_large_arc_takes_the_long_way(self):
        ops = s.parse_path("M12 6 A6 6 0 1 1 6 12")
        self.assertEqual(len([o for o in ops if o[0] == "C"]), 3)
        self.point_on_circle(ops, 12, 12, 6)

    def test_radius_too_small_is_scaled_up(self):
        ops = s.parse_path("M0 0 A1 1 0 0 1 10 0")
        close(self, ops[1][5:], (5, -5))

    def test_cubic_midpoint_is_on_the_circle(self):
        (c1x, c1y, c2x, c2y, x, y), = s.arc_to_cubics(18, 12, 6, 6, 0, 0, 1, 12, 18)
        mx = 0.125 * 18 + 0.375 * c1x + 0.375 * c2x + 0.125 * x
        my = 0.125 * 12 + 0.375 * c1y + 0.375 * c2y + 0.125 * y
        self.assertAlmostEqual(math.hypot(mx - 12, my - 12), 6, places=3)

    def test_rotated_ellipse_arc_ends_on_target(self):
        ops = s.parse_path("M4 12 A8 4 30 0 1 20 12")
        close(self, ops[-1][5:], (20, 12))

    def test_zero_radius_is_a_straight_line(self):
        ops = s.parse_path("M0 0 A0 5 0 0 1 4 4")
        close(self, ops[1][1:], (0, 0, 4, 4, 4, 4))


class Transforms(unittest.TestCase):
    def test_translate_scale_mirror(self):
        (shape,) = s.parse_svg_text(svg('<g transform="translate(24 0) scale(-1 1)"><line x1="2" y1="3" x2="5" y2="3"/></g>'))
        self.assertEqual(shape.ops, [("M", 22, 3), ("L", 19, 3)])
        self.assertAlmostEqual(shape.weight, 1.0)

    def test_rotate_about_centre(self):
        (shape,) = s.parse_svg_text(svg('<g transform="rotate(90 12 12)"><line x1="12" y1="6" x2="12" y2="12"/></g>'))
        close(self, shape.ops[0][1:], (18, 12))

    def test_matrix_and_nested_groups(self):
        (shape,) = s.parse_svg_text(svg('<g transform="matrix(2 0 0 2 0 0)"><g transform="translate(1,1)">'
                                        '<line x1="0" y1="0" x2="1" y2="0"/></g></g>'))
        self.assertEqual(shape.ops, [("M", 2, 2), ("L", 4, 2)])
        self.assertAlmostEqual(shape.weight, 2.0)

    def test_skew_is_rejected(self):
        with self.assertRaisesRegex(s.SvgError, "skewX"):
            s.parse_svg_text(svg('<g transform="skewX(10)"><line x1="0" y1="0" x2="1" y2="1"/></g>'))


class Errors(unittest.TestCase):
    def bad(self, body, pattern, whole=None):
        with self.assertRaisesRegex(s.SvgError, pattern):
            s.parse_svg_text(whole if whole is not None else svg(body))

    def test_unsupported_element(self):
        self.bad('<text>hi</text>', "unsupported element <text>")

    def test_unsupported_attribute(self):
        self.bad('<line x1="0" y1="0" x2="1" y2="1" opacity="0.5"/>', "'opacity'")

    def test_transform_outside_g(self):
        self.bad('<line x1="0" y1="0" x2="1" y2="1" transform="scale(2)"/>', "'transform'")

    def test_colour_other_than_current_color(self):
        self.bad('<line x1="0" y1="0" x2="1" y2="1" stroke="#f00"/>', "only none or currentColor")

    def test_bad_number(self):
        self.bad('<circle cx="12" cy="x" r="2"/>', "not a number")

    def test_bad_path_command(self):
        self.bad('<path d="M0 0 B1 1"/>', "unexpected 'B'")

    def test_path_missing_arguments(self):
        self.bad('<path d="M0 0 C1 1 2 2"/>', "C needs 6 numbers")

    def test_bad_arc_flag(self):
        self.bad('<path d="M0 0 A1 1 0 2 1 3 3"/>', "arc flag")

    def test_path_must_start_with_command(self):
        self.bad('<path d="1 1"/>', "must start with a command")

    def test_wrong_view_box(self):
        self.bad('', "viewBox", whole='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><line x1="0" y1="0" x2="1" y2="1"/></svg>')

    def test_not_xml(self):
        self.bad('', "well-formed", whole="<svg")

    def test_empty_icon(self):
        self.bad('', "draws nothing")

    def test_bad_linecap(self):
        self.bad('<line x1="0" y1="0" x2="1" y2="1" stroke-linecap="pointy"/>', "stroke-linecap")

    def test_foreign_namespace(self):
        self.bad('<x:foo xmlns:x="urn:x"/>', "foreign namespace")


class RepositoryIcons(unittest.TestCase):
    def test_every_icon_in_the_repository_parses(self):
        files = sorted((ROOT / "icons" / "standard").glob("*.svg")) + sorted((ROOT / "icons" / "svg").glob("*.svg"))
        self.assertGreaterEqual(len(files), 98)
        for f in files:
            with self.subTest(f.name):
                self.assertTrue(s.parse_svg_file(f))

    def test_bounds_of_a_stroked_square(self):
        shapes = s.parse_svg_text(svg('<polygon points="6 6 18 6 18 18 6 18"/>'))
        close(self, s.bounds(shapes), (5.4, 5.4, 18.6, 18.6))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run it to verify it fails**

Run:

```bash
export DEVELOPER_DIR=/Library/Developer/CommandLineTools PYTHONDONTWRITEBYTECODE=1
python3 -m unittest discover -s tools/tests 2>&1 | tail -3
```

Expected: an import error: `ModuleNotFoundError: No module named 'svgsubset'`, `FAILED (errors=1)`.

- [ ] **Step 3: Write the reader**

File: `tools/svgsubset.py`

```python
"""Reader for the house SVG subset (spec section 3.1).

Turns one icon SVG into a list of Shapes in absolute 24-unit grid
coordinates. Every curve becomes cubic Beziers, every transform is applied
to the points, and anything outside the subset raises SvgError.
"""
import math
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field

SVG_NS = "{http://www.w3.org/2000/svg}"
HOUSE_STROKE = 1.2          # grid units; Shape.weight is relative to this
KAPPA = 0.5522847498307936  # cubic approximation of a quarter circle

PAINT_ATTRS = {"fill", "stroke", "stroke-width", "stroke-linecap", "stroke-linejoin"}
ROOT_ATTRS = PAINT_ATTRS | {"width", "height", "viewBox", "xmlns"}
GEOMETRY = {
    "g": set(),
    "line": {"x1", "y1", "x2", "y2"},
    "circle": {"cx", "cy", "r"},
    "ellipse": {"cx", "cy", "rx", "ry"},
    "rect": {"x", "y", "width", "height", "rx", "ry"},
    "polyline": {"points"},
    "polygon": {"points"},
    "path": {"d"},
}
CAPS = {"butt", "round", "square"}
JOINS = {"miter", "round", "bevel"}
PAINTS = {"none", "currentColor"}


class SvgError(ValueError):
    """The file uses something outside the supported subset."""


@dataclass
class Shape:
    ops: list                 # ("M", x, y) | ("L", x, y) | ("C", x1, y1, x2, y2, x, y) | ("Z",)
    fill: bool
    stroke: bool
    weight: float = 1.0       # stroke width / HOUSE_STROKE, after transforms
    cap: str = "butt"
    join: str = "miter"


@dataclass
class Style:
    fill: str = "black"       # SVG initial values
    stroke: str = "none"
    width: float = 1.0
    cap: str = "butt"
    join: str = "miter"


# ---------------------------------------------------------------- numbers

NUMBER = re.compile(r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?")


def _num(text, what):
    text = text.strip()
    if not NUMBER.fullmatch(text):
        raise SvgError(f"{what}: not a number: {text!r}")
    return float(text)


def _numbers(text, what):
    rest = re.sub(r"[\s,]+", " ", text).strip()
    out = []
    pos = 0
    while pos < len(rest):
        if rest[pos] == " ":
            pos += 1
            continue
        m = NUMBER.match(rest, pos)
        if not m:
            raise SvgError(f"{what}: bad number list: {text!r}")
        out.append(float(m.group()))
        pos = m.end()
    return out


# ---------------------------------------------------------------- transforms

IDENTITY = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)


def multiply(m, n):
    """m then n applied as SVG does: result = m x n (n is applied first)."""
    a, b, c, d, e, f = m
    a2, b2, c2, d2, e2, f2 = n
    return (a * a2 + c * b2, b * a2 + d * b2,
            a * c2 + c * d2, b * c2 + d * d2,
            a * e2 + c * f2 + e, b * e2 + d * f2 + f)


def apply(m, x, y):
    a, b, c, d, e, f = m
    return (a * x + c * y + e, b * x + d * y + f)


TRANSFORM = re.compile(r"\s*(\w+)\s*\(([^)]*)\)\s*,?")


def parse_transform(text):
    m = IDENTITY
    pos = 0
    text = text.strip()
    while pos < len(text):
        t = TRANSFORM.match(text, pos)
        if not t:
            raise SvgError(f"transform: cannot read {text[pos:]!r}")
        name, args = t.group(1), _numbers(t.group(2), "transform")
        pos = t.end()
        if name == "translate" and len(args) in (1, 2):
            step = (1, 0, 0, 1, args[0], args[1] if len(args) == 2 else 0.0)
        elif name == "scale" and len(args) in (1, 2):
            sy = args[1] if len(args) == 2 else args[0]
            step = (args[0], 0, 0, sy, 0, 0)
        elif name == "rotate" and len(args) in (1, 3):
            r = math.radians(args[0])
            cos, sin = math.cos(r), math.sin(r)
            step = (cos, sin, -sin, cos, 0, 0)
            if len(args) == 3:
                cx, cy = args[1], args[2]
                step = multiply(multiply((1, 0, 0, 1, cx, cy), step), (1, 0, 0, 1, -cx, -cy))
        elif name == "matrix" and len(args) == 6:
            step = tuple(args)
        else:
            raise SvgError(f"transform: unsupported {name}({t.group(2).strip()})")
        m = multiply(m, step)
    return m


# ---------------------------------------------------------------- arcs

def arc_to_cubics(x1, y1, rx, ry, phi_deg, large, sweep, x2, y2):
    """SVG endpoint arc (spec F.6) as cubic segments [(c1x, c1y, c2x, c2y, x, y)]."""
    if (x1, y1) == (x2, y2):
        return []
    rx, ry = abs(rx), abs(ry)
    if rx == 0 or ry == 0:
        return [(x1, y1, x2, y2, x2, y2)]
    phi = math.radians(phi_deg % 360)
    cos, sin = math.cos(phi), math.sin(phi)
    dx, dy = (x1 - x2) / 2, (y1 - y2) / 2
    xp, yp = cos * dx + sin * dy, -sin * dx + cos * dy
    lam = (xp * xp) / (rx * rx) + (yp * yp) / (ry * ry)
    if lam > 1:
        s = math.sqrt(lam)
        rx, ry = rx * s, ry * s
    num = rx * rx * ry * ry - rx * rx * yp * yp - ry * ry * xp * xp
    den = rx * rx * yp * yp + ry * ry * xp * xp
    coef = math.sqrt(max(0.0, num / den))
    if large == sweep:
        coef = -coef
    cxp, cyp = coef * rx * yp / ry, -coef * ry * xp / rx
    cx = cos * cxp - sin * cyp + (x1 + x2) / 2
    cy = sin * cxp + cos * cyp + (y1 + y2) / 2

    def angle(ux, uy, vx, vy):
        a = math.atan2(ux * vy - uy * vx, ux * vx + uy * vy)
        return a

    t1 = angle(1, 0, (xp - cxp) / rx, (yp - cyp) / ry)
    dt = angle((xp - cxp) / rx, (yp - cyp) / ry, (-xp - cxp) / rx, (-yp - cyp) / ry)
    if not sweep and dt > 0:
        dt -= 2 * math.pi
    elif sweep and dt < 0:
        dt += 2 * math.pi
    n = max(1, math.ceil(abs(dt) / (math.pi / 2) - 1e-9))
    step = dt / n
    k = 4 / 3 * math.tan(step / 4)
    out = []
    t = t1
    for i in range(n):
        ta, tb = t, t + step
        ca, sa, cb, sb = math.cos(ta), math.sin(ta), math.cos(tb), math.sin(tb)
        p1 = (ca - k * sa, sa + k * ca)
        p2 = (cb + k * sb, sb - k * cb)
        p3 = (cb, sb)
        pts = []
        for ux, uy in (p1, p2, p3):
            ux, uy = ux * rx, uy * ry
            pts += [cos * ux - sin * uy + cx, sin * ux + cos * uy + cy]
        if i == n - 1:
            pts[4], pts[5] = x2, y2
        out.append(tuple(pts))
        t = tb
    return out


# ---------------------------------------------------------------- path data

ARGS = {"M": 2, "L": 2, "H": 1, "V": 1, "C": 6, "S": 4, "Q": 4, "T": 2, "A": 7, "Z": 0}


def parse_path(d):
    """Path data -> absolute ops with only M, L, C and Z."""
    tokens = _path_tokens(d)
    ops = []
    i = 0
    cmd = None
    cx = cy = 0.0          # current point
    sx = sy = 0.0          # subpath start
    last_c2 = None         # last cubic control point, for S
    last_q = None          # last quadratic control point, for T
    while i < len(tokens):
        tok = tokens[i]
        if isinstance(tok, str):
            cmd = tok
            i += 1
            if cmd in "Zz":
                ops.append(("Z",))
                cx, cy = sx, sy
                last_c2 = last_q = None
                continue
        elif cmd is None:
            raise SvgError(f"path: data must start with a command: {d!r}")
        elif cmd in "Zz":
            raise SvgError(f"path: numbers after Z in {d!r}")
        n = ARGS[cmd.upper()]
        args = tokens[i:i + n]
        if len(args) < n or any(isinstance(a, str) for a in args):
            raise SvgError(f"path: {cmd} needs {n} numbers in {d!r}")
        i += n
        rel = cmd.islower()
        up = cmd.upper()
        ox, oy = (cx, cy) if rel else (0.0, 0.0)
        if up == "M":
            cx, cy = args[0] + ox, args[1] + oy
            sx, sy = cx, cy
            ops.append(("M", cx, cy))
            cmd = "l" if rel else "L"   # further pairs are implicit lineto
            last_c2 = last_q = None
        elif up in "LHV":
            if up == "L":
                cx, cy = args[0] + ox, args[1] + oy
            elif up == "H":
                cx = args[0] + (cx if rel else 0.0)
            else:
                cy = args[0] + (cy if rel else 0.0)
            ops.append(("L", cx, cy))
            last_c2 = last_q = None
        elif up in "CS":
            if up == "C":
                x1, y1 = args[0] + ox, args[1] + oy
                rest = args[2:]
            else:
                x1, y1 = (2 * cx - last_c2[0], 2 * cy - last_c2[1]) if last_c2 else (cx, cy)
                rest = args
            x2, y2 = rest[0] + ox, rest[1] + oy
            x, y = rest[2] + ox, rest[3] + oy
            ops.append(("C", x1, y1, x2, y2, x, y))
            last_c2, last_q = (x2, y2), None
            cx, cy = x, y
        elif up in "QT":
            if up == "Q":
                qx, qy = args[0] + ox, args[1] + oy
                x, y = args[2] + ox, args[3] + oy
            else:
                qx, qy = (2 * cx - last_q[0], 2 * cy - last_q[1]) if last_q else (cx, cy)
                x, y = args[0] + ox, args[1] + oy
            ops.append(("C", cx + 2 / 3 * (qx - cx), cy + 2 / 3 * (qy - cy),
                        x + 2 / 3 * (qx - x), y + 2 / 3 * (qy - y), x, y))
            last_q, last_c2 = (qx, qy), None
            cx, cy = x, y
        else:  # A
            rx, ry, rot, large, sweep, x, y = args
            if large not in (0.0, 1.0) or sweep not in (0.0, 1.0):
                raise SvgError(f"path: arc flag must be 0 or 1 in {d!r}")
            x, y = x + ox, y + oy
            for seg in arc_to_cubics(cx, cy, rx, ry, rot, int(large), int(sweep), x, y):
                ops.append(("C",) + seg)
            cx, cy = x, y
            last_c2 = last_q = None
    return ops


def _path_tokens(d):
    """Numbers and command letters; arc flags may be packed ("a1 1 0 011 1")."""
    out = []
    pos = 0
    cmd = None
    index = 0
    while pos < len(d):
        ch = d[pos]
        if ch in " \t\r\n,":
            pos += 1
            continue
        if ch.isalpha():
            if ch not in "MmLlHhVvCcSsQqTtAaZz":
                raise SvgError(f"path: unexpected {ch!r} in {d!r}")
            cmd, index = ch, 0
            out.append(ch)
            pos += 1
            continue
        if cmd in ("A", "a") and index % 7 in (3, 4):
            if ch not in "01":
                raise SvgError(f"path: arc flag must be 0 or 1 in {d!r}")
            out.append(float(ch))
            pos += 1
            index += 1
            continue
        m = NUMBER.match(d, pos)
        if not m:
            raise SvgError(f"path: unexpected {ch!r} in {d!r}")
        out.append(float(m.group()))
        pos = m.end()
        index += 1
    return out


# ---------------------------------------------------------------- shapes

def _ellipse_ops(cx, cy, rx, ry):
    kx, ky = rx * KAPPA, ry * KAPPA
    return [("M", cx + rx, cy),
            ("C", cx + rx, cy + ky, cx + kx, cy + ry, cx, cy + ry),
            ("C", cx - kx, cy + ry, cx - rx, cy + ky, cx - rx, cy),
            ("C", cx - rx, cy - ky, cx - kx, cy - ry, cx, cy - ry),
            ("C", cx + kx, cy - ry, cx + rx, cy - ky, cx + rx, cy),
            ("Z",)]


def _rect_ops(x, y, w, h, rx, ry):
    if rx == 0 or ry == 0:
        return [("M", x, y), ("L", x + w, y), ("L", x + w, y + h), ("L", x, y + h), ("Z",)]
    kx, ky = rx * KAPPA, ry * KAPPA
    r, b = x + w, y + h
    return [("M", x + rx, y), ("L", r - rx, y),
            ("C", r - rx + kx, y, r, y + ry - ky, r, y + ry), ("L", r, b - ry),
            ("C", r, b - ry + ky, r - rx + kx, b, r - rx, b), ("L", x + rx, b),
            ("C", x + rx - kx, b, x, b - ry + ky, x, b - ry), ("L", x, y + ry),
            ("C", x, y + ry - ky, x + rx - kx, y, x + rx, y), ("Z",)]


def _attr_num(el, name, tag, default=None):
    if name not in el.attrib:
        if default is None:
            raise SvgError(f"<{tag}> needs {name}")
        return default
    return _num(el.attrib[name], f"<{tag}> {name}")


def _element_ops(el, tag):
    a = el.attrib
    if tag == "line":
        return [("M", _attr_num(el, "x1", tag, 0.0), _attr_num(el, "y1", tag, 0.0)),
                ("L", _attr_num(el, "x2", tag, 0.0), _attr_num(el, "y2", tag, 0.0))]
    if tag == "circle":
        r = _attr_num(el, "r", tag)
        return _ellipse_ops(_attr_num(el, "cx", tag, 0.0), _attr_num(el, "cy", tag, 0.0), r, r)
    if tag == "ellipse":
        return _ellipse_ops(_attr_num(el, "cx", tag, 0.0), _attr_num(el, "cy", tag, 0.0),
                            _attr_num(el, "rx", tag), _attr_num(el, "ry", tag))
    if tag == "rect":
        w, h = _attr_num(el, "width", tag), _attr_num(el, "height", tag)
        rx = a.get("rx")
        ry = a.get("ry")
        rxv = _num(rx, "<rect> rx") if rx is not None else None
        ryv = _num(ry, "<rect> ry") if ry is not None else None
        if rxv is None:
            rxv = ryv if ryv is not None else 0.0
        if ryv is None:
            ryv = rxv
        rxv, ryv = min(rxv, w / 2), min(ryv, h / 2)
        return _rect_ops(_attr_num(el, "x", tag, 0.0), _attr_num(el, "y", tag, 0.0), w, h, rxv, ryv)
    if tag in ("polyline", "polygon"):
        nums = _numbers(a.get("points", ""), f"<{tag}> points")
        if len(nums) < 4 or len(nums) % 2:
            raise SvgError(f"<{tag}> points needs an even count of at least 4 numbers")
        ops = [("M", nums[0], nums[1])] + [("L", nums[i], nums[i + 1]) for i in range(2, len(nums), 2)]
        return ops + [("Z",)] if tag == "polygon" else ops
    return parse_path(a.get("d", ""))


def _style(el, parent, tag):
    s = Style(parent.fill, parent.stroke, parent.width, parent.cap, parent.join)
    a = el.attrib
    for key in ("fill", "stroke"):
        if key in a:
            if a[key] not in PAINTS:
                raise SvgError(f"<{tag}> {key}={a[key]!r}: only none or currentColor")
            setattr(s, key, a[key])
    if "stroke-width" in a:
        s.width = _num(a["stroke-width"], f"<{tag}> stroke-width")
        if s.width <= 0:
            raise SvgError(f"<{tag}> stroke-width must be positive")
    if "stroke-linecap" in a:
        if a["stroke-linecap"] not in CAPS:
            raise SvgError(f"<{tag}> stroke-linecap={a['stroke-linecap']!r}")
        s.cap = a["stroke-linecap"]
    if "stroke-linejoin" in a:
        if a["stroke-linejoin"] not in JOINS:
            raise SvgError(f"<{tag}> stroke-linejoin={a['stroke-linejoin']!r}")
        s.join = a["stroke-linejoin"]
    return s


def _tag(el):
    tag = el.tag
    if not isinstance(tag, str):
        raise SvgError("unsupported node")
    if tag.startswith(SVG_NS):
        tag = tag[len(SVG_NS):]
    elif tag.startswith("{"):
        raise SvgError(f"element in a foreign namespace: {tag}")
    return tag


def _transform_ops(ops, m):
    out = []
    for op in ops:
        if op[0] == "Z":
            out.append(op)
            continue
        pts = []
        for i in range(1, len(op), 2):
            pts += list(apply(m, op[i], op[i + 1]))
        out.append((op[0],) + tuple(pts))
    return out


def _walk(el, matrix, style, shapes):
    for child in el:
        tag = _tag(child)
        if tag not in GEOMETRY:
            raise SvgError(f"unsupported element <{tag}>")
        allowed = GEOMETRY[tag] | PAINT_ATTRS | ({"transform"} if tag == "g" else set())
        for key in child.attrib:
            if key not in allowed:
                raise SvgError(f"<{tag}> attribute {key!r} is not supported")
        if (child.text or "").strip():
            raise SvgError(f"<{tag}> must not contain text")
        s = _style(child, style, tag)
        if tag == "g":
            m = matrix
            if "transform" in child.attrib:
                m = multiply(matrix, parse_transform(child.attrib["transform"]))
            _walk(child, m, s, shapes)
            continue
        if len(child):
            raise SvgError(f"<{tag}> must not have child elements")
        ops = _element_ops(child, tag)
        fill = s.fill != "none" and tag != "line"
        stroke = s.stroke != "none"
        if not ops or not (fill or stroke):
            continue
        a, b, c, d, _, _ = matrix
        scale = math.sqrt(abs(a * d - b * c))
        shapes.append(Shape(_transform_ops(ops, matrix), fill, stroke,
                            s.width * scale / HOUSE_STROKE, s.cap, s.join))


def parse_svg_text(text, name="icon"):
    try:
        root = ET.fromstring(text)
    except ET.ParseError as e:
        raise SvgError(f"{name}: not well-formed XML: {e}") from None
    if _tag(root) != "svg":
        raise SvgError(f"{name}: root element must be <svg>")
    for key in root.attrib:
        if key not in ROOT_ATTRS:
            raise SvgError(f"{name}: <svg> attribute {key!r} is not supported")
    if root.attrib.get("viewBox", "").split() != ["0", "0", "24", "24"]:
        raise SvgError(f"{name}: viewBox must be \"0 0 24 24\"")
    try:
        shapes = []
        _walk(root, IDENTITY, _style(root, Style(), "svg"), shapes)
    except SvgError as e:
        raise SvgError(f"{name}: {e}") from None
    if not shapes:
        raise SvgError(f"{name}: draws nothing")
    return shapes


def parse_svg_file(path):
    with open(path, encoding="utf-8") as f:
        return parse_svg_text(f.read(), str(path))


def bounds(shapes, samples=24):
    """Ink bounding box (x0, y0, x1, y1) including half of each stroke."""
    xs, ys = [], []
    for s in shapes:
        pad = s.weight * HOUSE_STROKE / 2 if s.stroke else 0.0
        px = py = 0.0
        for op in s.ops:
            pts = []
            if op[0] in ("M", "L"):
                pts = [(op[1], op[2])]
            elif op[0] == "C":
                for k in range(1, samples + 1):
                    t = k / samples
                    u = 1 - t
                    pts.append((u**3 * px + 3 * u * u * t * op[1] + 3 * u * t * t * op[3] + t**3 * op[5],
                                u**3 * py + 3 * u * u * t * op[2] + 3 * u * t * t * op[4] + t**3 * op[6]))
            for x, y in pts:
                xs += [x - pad, x + pad]
                ys += [y - pad, y + pad]
            if pts:
                px, py = pts[-1]
    return (min(xs), min(ys), max(xs), max(ys))
```

- [ ] **Step 4: Run the tests to verify they pass**

Run:

```bash
export DEVELOPER_DIR=/Library/Developer/CommandLineTools PYTHONDONTWRITEBYTECODE=1
python3 -m unittest discover -s tools/tests 2>&1 | tail -3
```

Expected: `Ran 42 tests` and `OK` (the repository test parses all 98 existing SVGs).

- [ ] **Step 5: Commit**

Run:

```bash
export DEVELOPER_DIR=/Library/Developer/CommandLineTools PYTHONDONTWRITEBYTECODE=1
git add tools/svgsubset.py \
  tools/tests/test_svgsubset.py
git status --short
git commit -q -F - <<'MSG'
SVG subset reader: shapes, transforms and arcs as cubics

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01F7df6grqTdqHgc2d2X359P
MSG
git status --short
```

Expected: `git status --short` before the commit lists only the paths above (no `.DS_Store`, no `__pycache__`); after the commit it prints nothing.

### Task 2: Token file, validation and contrast

The token source with all four themes, the validator the generator relies on (completeness, unknown keys, malformed values) and the WCAG contrast maths.

**Files:**
- Create: `tokens/tokens.json`
- Create: `tools/tokenlib.py`
- Test: `tools/tests/test_tokenlib.py`

**Interfaces:**
- Consumes: nothing.
- Produces (module `tokenlib`): `class TokenError(ValueError)` with `.problems: list[str]`; `load(path) -> dict` (validated); `validate(data: dict) -> None` (raises `TokenError` listing every problem); `flat_values(theme: dict) -> dict[str, value]` keyed `"group.name"`; `SYSTEM_COLORS: list[str]`; `WEIGHTS: list[str]`; `USES = {"body": 4.5, "large": 3.0, "icon": 3.0}`; `rgba(value) -> (r, g, b, a)` floats; `over(top, bottom)`; `luminance(c)`; `contrast_ratio(fg, bg) -> float`; `contrast_rows(data) -> list[(theme_id, text, on, use, ratio, needed, ok)]`; `format_ratio(ratio) -> str` (rounded down, e.g. `"4.49:1"`); `contrast_markdown(rows) -> str`. The test module also exports `minimal()` (a tiny valid token file) that later generator tests import.

- [ ] **Step 1: Write the failing test**

File: `tools/tests/test_tokenlib.py`

```python
import copy
import json
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import tokenlib as t  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[2]


def minimal():
    return {
        "tokens": {
            "text": {"kind": "color", "items": {"primary": "Main text"}},
            "surface": {"kind": "color", "items": {"window": "Window"}},
            "spacing": {"kind": "points", "items": {"m": "Medium gap"}},
            "type": {"kind": "font", "items": {"body": "Body text"}},
        },
        "contrast": [{"text": "text.primary", "on": "surface.window", "use": "body"}],
        "themes": [{
            "id": "classic-light", "appearance": "light",
            "values": {
                "text": {"primary": "#000000"},
                "surface": {"window": {"system": "windowBackgroundColor", "fallback": "#FFFFFF"}},
                "spacing": {"m": 12},
                "type": {"body": {"size": 13, "weight": "regular"}},
            },
        }],
    }


class Validation(unittest.TestCase):
    def problems(self, data):
        with self.assertRaises(t.TokenError) as ctx:
            t.validate(data)
        return ctx.exception.problems

    def test_minimal_file_is_valid(self):
        t.validate(minimal())

    def test_missing_token(self):
        d = minimal()
        del d["themes"][0]["values"]["spacing"]["m"]
        self.assertIn("theme classic-light lacks spacing.m", self.problems(d))

    def test_unknown_token(self):
        d = minimal()
        d["themes"][0]["values"]["spacing"]["huge"] = 99
        self.assertIn("theme classic-light defines unknown token spacing.huge", self.problems(d))

    def test_unknown_group(self):
        d = minimal()
        d["themes"][0]["values"]["glow"] = {"x": "#FFFFFF"}
        self.assertIn("theme classic-light defines unknown token glow.x", self.problems(d))

    def test_every_problem_is_reported_at_once(self):
        d = minimal()
        d["themes"][0]["values"]["text"]["primary"] = "red"
        d["themes"][0]["values"]["spacing"]["m"] = -1
        self.assertEqual(len(self.problems(d)), 2)

    def test_malformed_colours(self):
        for bad in ("#FFF", "FFFFFF", "#GGGGGG", 12, {"system": "windowBackgroundColor"},
                    {"system": "notAColor", "fallback": "#FFFFFF"},
                    {"system": "labelColor", "fallback": "white"}):
            with self.subTest(bad=bad):
                d = minimal()
                d["themes"][0]["values"]["text"]["primary"] = bad
                self.assertTrue(any("text.primary" in p for p in self.problems(d)))

    def test_alpha_colour_is_accepted(self):
        d = minimal()
        d["themes"][0]["values"]["text"]["primary"] = "#000000D9"
        t.validate(d)

    def test_points_must_be_non_negative_numbers(self):
        for bad in (-1, "12", True, None):
            with self.subTest(bad=bad):
                d = minimal()
                d["themes"][0]["values"]["spacing"]["m"] = bad
                self.assertTrue(any("spacing.m" in p for p in self.problems(d)))

    def test_font_needs_size_and_known_weight(self):
        for bad in ({"size": 13}, {"size": 0, "weight": "bold"}, {"size": 13, "weight": "fat"}):
            with self.subTest(bad=bad):
                d = minimal()
                d["themes"][0]["values"]["type"]["body"] = bad
                self.assertTrue(any("type.body" in p for p in self.problems(d)))

    def test_appearance_and_duplicate_ids(self):
        d = minimal()
        d["themes"].append(copy.deepcopy(d["themes"][0]))
        d["themes"][1]["appearance"] = "dim"
        problems = self.problems(d)
        self.assertIn("theme id 'classic-light' is used twice", problems)
        self.assertIn("theme classic-light: appearance must be light or dark", problems)

    def test_theme_id_must_be_neutral_kebab_case(self):
        d = minimal()
        d["themes"][0]["id"] = "Cubase_Dark"
        self.assertTrue(any("must be lower-case words" in p for p in self.problems(d)))

    def test_contrast_pair_must_name_colour_tokens(self):
        d = minimal()
        d["contrast"] = [{"text": "spacing.m", "on": "surface.nope", "use": "loud"}]
        problems = self.problems(d)
        self.assertEqual(len(problems), 3)

    def test_unknown_top_level_key(self):
        d = minimal()
        d["colours"] = {}
        self.assertIn("unknown top-level key 'colours'", self.problems(d))

    def test_token_needs_description(self):
        d = minimal()
        d["tokens"]["spacing"]["items"]["m"] = ""
        self.assertIn("token spacing.m: needs a one-line description", self.problems(d))


class Contrast(unittest.TestCase):
    def test_black_on_white_is_21(self):
        self.assertAlmostEqual(t.contrast_ratio(t.rgba("#000000"), t.rgba("#FFFFFF")), 21.0, places=6)

    def test_same_colour_is_1(self):
        self.assertAlmostEqual(t.contrast_ratio(t.rgba("#777777"), t.rgba("#777777")), 1.0)

    def test_known_grey(self):
        # #767676 on white is the classic 4.54:1 AA grey.
        self.assertAlmostEqual(t.contrast_ratio(t.rgba("#767676"), t.rgba("#FFFFFF")), 4.54, places=2)

    def test_alpha_is_composited_over_the_background(self):
        r, g, b, a = t.over(t.rgba("#00000080"), (1.0, 1.0, 1.0, 1.0))
        self.assertAlmostEqual(r, 1 - 128 / 255)
        self.assertEqual((r, a), (b, 1.0))

    def test_ratio_is_rounded_down(self):
        self.assertEqual(t.format_ratio(4.4988), "4.49:1")
        self.assertEqual(t.format_ratio(21.0), "21.00:1")

    def test_system_colour_uses_fallback(self):
        self.assertEqual(t.rgba({"system": "labelColor", "fallback": "#FF0000"}), (1.0, 0.0, 0.0, 1.0))

    def test_rows_flag_failures_without_raising(self):
        d = minimal()
        d["themes"][0]["values"]["text"]["primary"] = "#EEEEEE"
        (row,) = t.contrast_rows(d)
        self.assertEqual(row[:4], ("classic-light", "text.primary", "surface.window", "body"))
        self.assertFalse(row[6])
        self.assertIn("| WARN |", t.contrast_markdown([row]))


class RepositoryTokens(unittest.TestCase):
    def test_tokens_json_is_valid_and_has_the_four_themes(self):
        data = t.load(ROOT / "tokens" / "tokens.json")
        self.assertEqual([th["id"] for th in data["themes"]], ["classic-light", "studio-dark", "flat", "console"])
        self.assertEqual([th["appearance"] for th in data["themes"]], ["light", "dark", "light", "dark"])
        self.assertEqual([th.get("placeholder") for th in data["themes"]], [False, False, True, True])

    def test_spec_groups_are_present(self):
        with open(ROOT / "tokens" / "tokens.json", encoding="utf-8") as f:
            groups = json.load(f)["tokens"]
        self.assertEqual(sorted(groups), sorted(["surface", "text", "accent", "state", "meter", "graph", "control",
                                                 "strip", "spacing", "radius", "iconStroke", "type"]))
        self.assertEqual(list(groups["iconStroke"]["items"]), ["s16", "s24", "s32"])
        self.assertEqual(list(groups["control"]["items"]),
                         ["gain", "eqLow", "eqLowMid", "eqHighMid", "eqHigh", "send", "pan", "dynamics", "filter"])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run it to verify it fails**

Run:

```bash
export DEVELOPER_DIR=/Library/Developer/CommandLineTools PYTHONDONTWRITEBYTECODE=1
python3 -m unittest tools/tests/test_tokenlib.py 2>&1 | tail -3
```

Expected: `ModuleNotFoundError: No module named 'tokenlib'`.

- [ ] **Step 3: Write the token file**

Starter values: `classic-light` and `studio-dark` track macOS system colours with fallbacks; `flat` and `console` are marked `"placeholder": true` with a PLACEHOLDER note.

File: `tokens/tokens.json`

```json
{
  "description": "SymbioticAudio design tokens (MIT). Every theme defines every token; tools/generate.py validates this file and writes the Swift code and tokens/contrast.md.",
  "tokens": {
    "surface": {"kind": "color", "items": {
      "window": "Window background behind everything",
      "panel": "Panels, sidebars and editor backgrounds",
      "raised": "Controls and cards raised above a panel",
      "inset": "Recessed areas: fields, meters' wells, editor canvases",
      "separator": "Hairlines between areas",
      "selection": "Background of selected rows, regions and events",
      "focusRing": "Keyboard focus ring"
    }},
    "text": {"kind": "color", "items": {
      "primary": "Main text and icons",
      "secondary": "Labels, captions and inactive icons",
      "disabled": "Text and icons of disabled controls",
      "inverse": "Text on selection or other strong backgrounds"
    }},
    "accent": {"kind": "color", "items": {
      "accent": "Primary accent: default buttons, active toggles",
      "onAccent": "Text and icons on the accent colour"
    }},
    "state": {"kind": "color", "items": {
      "record": "Record and record-arm",
      "play": "Play / running",
      "solo": "Solo",
      "mute": "Mute",
      "warning": "Warnings and caution banners",
      "error": "Errors and faults",
      "offline": "Offline media or disconnected devices"
    }},
    "meter": {"kind": "color", "items": {
      "background": "Meter well",
      "low": "Level below -18 dBFS",
      "mid": "Level from -18 to -6 dBFS",
      "high": "Level from -6 to 0 dBFS",
      "clip": "Clip / over indicator"
    }},
    "graph": {"kind": "color", "items": {
      "line": "Waveform, envelope, LFO and scope line",
      "fill": "Area under a graph line",
      "grid": "Graph grid lines",
      "handle": "Editable point or handle",
      "handleSelected": "Selected point or handle"
    }},
    "control": {"kind": "color", "items": {
      "gain": "Gain and level controls",
      "eqLow": "Low EQ band",
      "eqLowMid": "Low-mid EQ band",
      "eqHighMid": "High-mid EQ band",
      "eqHigh": "High EQ band",
      "send": "Send levels",
      "pan": "Pan and balance",
      "dynamics": "Compressor, gate and limiter",
      "filter": "Filter cutoff and resonance"
    }},
    "strip": {"kind": "color", "items": {
      "channel": "Audio or MIDI channel strip",
      "instrument": "Instrument strip",
      "auxReturn": "Aux return strip",
      "bus": "Bus / group strip",
      "master": "Master strip"
    }},
    "spacing": {"kind": "points", "items": {
      "xxs": "Hairline gaps inside a control",
      "xs": "Between a control and its label",
      "s": "Between related controls",
      "m": "Between groups in a panel",
      "l": "Panel padding",
      "xl": "Between panels"
    }},
    "radius": {"kind": "points", "items": {
      "none": "Square corners",
      "s": "Small controls and buttons",
      "m": "Cards and fields",
      "l": "Panels and sheets"
    }},
    "iconStroke": {"kind": "points", "items": {
      "s16": "Icon stroke width at 16 pt",
      "s24": "Icon stroke width at 24 pt",
      "s32": "Icon stroke width at 32 pt"
    }},
    "type": {"kind": "font", "items": {
      "caption": "Small captions and meter scales",
      "body": "Body text and list rows",
      "label": "Control labels",
      "title": "Panel and section titles",
      "display": "Large readouts such as the transport position"
    }}
  },
  "contrast": [
    {"text": "text.primary", "on": "surface.window", "use": "body"},
    {"text": "text.primary", "on": "surface.panel", "use": "body"},
    {"text": "text.primary", "on": "surface.raised", "use": "body"},
    {"text": "text.primary", "on": "surface.inset", "use": "body"},
    {"text": "text.secondary", "on": "surface.window", "use": "body"},
    {"text": "text.secondary", "on": "surface.panel", "use": "body"},
    {"text": "text.inverse", "on": "surface.selection", "use": "body"},
    {"text": "accent.onAccent", "on": "accent.accent", "use": "body"},
    {"text": "state.record", "on": "surface.panel", "use": "icon"},
    {"text": "state.warning", "on": "surface.window", "use": "icon"},
    {"text": "graph.line", "on": "surface.inset", "use": "icon"},
    {"text": "meter.clip", "on": "meter.background", "use": "icon"}
  ],
  "themes": [
    {
      "id": "classic-light", "appearance": "light", "placeholder": false,
      "note": "Starter values that track macOS system colours; final palette in VizDAW SP7.",
      "values": {
        "surface": {"window": {"system": "windowBackgroundColor", "fallback": "#ECECEC"}, "panel": {"system": "controlBackgroundColor", "fallback": "#FFFFFF"}, "raised": {"system": "controlColor", "fallback": "#FFFFFF"}, "inset": {"system": "underPageBackgroundColor", "fallback": "#E3E3E3"}, "separator": {"system": "separatorColor", "fallback": "#0000001A"}, "selection": {"system": "selectedContentBackgroundColor", "fallback": "#0063E1"}, "focusRing": {"system": "keyboardFocusIndicatorColor", "fallback": "#0067F43F"}},
        "text": {"primary": {"system": "labelColor", "fallback": "#000000D9"}, "secondary": {"system": "secondaryLabelColor", "fallback": "#00000080"}, "disabled": {"system": "tertiaryLabelColor", "fallback": "#00000042"}, "inverse": {"system": "alternateSelectedControlTextColor", "fallback": "#FFFFFF"}},
        "accent": {"accent": {"system": "controlAccentColor", "fallback": "#007AFF"}, "onAccent": {"system": "alternateSelectedControlTextColor", "fallback": "#FFFFFF"}},
        "state": {"record": {"system": "systemRed", "fallback": "#FF3B30"}, "play": {"system": "systemGreen", "fallback": "#28CD41"}, "solo": {"system": "systemYellow", "fallback": "#FFCC00"}, "mute": {"system": "systemBlue", "fallback": "#007AFF"}, "warning": {"system": "systemOrange", "fallback": "#FF9500"}, "error": {"system": "systemRed", "fallback": "#FF3B30"}, "offline": {"system": "systemGray", "fallback": "#8E8E93"}},
        "meter": {"background": "#2B2B2B", "low": "#34C759", "mid": "#FFCC00", "high": "#FF9500", "clip": "#FF3B30"},
        "graph": {"line": {"system": "controlAccentColor", "fallback": "#007AFF"}, "fill": "#007AFF33", "grid": "#00000014", "handle": "#3C3C43", "handleSelected": {"system": "controlAccentColor", "fallback": "#007AFF"}},
        "control": {"gain": "#8E8E93", "eqLow": "#E5534B", "eqLowMid": "#E3A21A", "eqHighMid": "#3FB950", "eqHigh": "#4C8DF6", "send": "#A371F7", "pan": "#39C5CF", "dynamics": "#F778BA", "filter": "#DB8B0B"},
        "strip": {"channel": "#6E7681", "instrument": "#3FB950", "auxReturn": "#A371F7", "bus": "#E3A21A", "master": "#E5534B"},
        "spacing": {"xxs": 2, "xs": 4, "s": 8, "m": 12, "l": 16, "xl": 24},
        "radius": {"none": 0, "s": 3, "m": 6, "l": 10},
        "iconStroke": {"s16": 1.0, "s24": 1.2, "s32": 1.6},
        "type": {"caption": {"size": 10, "weight": "regular"}, "body": {"size": 13, "weight": "regular"}, "label": {"size": 11, "weight": "medium"}, "title": {"size": 15, "weight": "semibold"}, "display": {"size": 24, "weight": "bold"}}
      }
    },
    {
      "id": "studio-dark", "appearance": "dark", "placeholder": false,
      "note": "Starter values that track macOS system colours; final palette in VizDAW SP7.",
      "values": {
        "surface": {"window": {"system": "windowBackgroundColor", "fallback": "#323232"}, "panel": {"system": "controlBackgroundColor", "fallback": "#1E1E1E"}, "raised": {"system": "controlColor", "fallback": "#3C3C3C"}, "inset": {"system": "underPageBackgroundColor", "fallback": "#282828"}, "separator": {"system": "separatorColor", "fallback": "#FFFFFF1A"}, "selection": {"system": "selectedContentBackgroundColor", "fallback": "#0058D0"}, "focusRing": {"system": "keyboardFocusIndicatorColor", "fallback": "#1AA9FF4C"}},
        "text": {"primary": {"system": "labelColor", "fallback": "#FFFFFFD9"}, "secondary": {"system": "secondaryLabelColor", "fallback": "#FFFFFF8C"}, "disabled": {"system": "tertiaryLabelColor", "fallback": "#FFFFFF40"}, "inverse": {"system": "alternateSelectedControlTextColor", "fallback": "#FFFFFF"}},
        "accent": {"accent": {"system": "controlAccentColor", "fallback": "#0A84FF"}, "onAccent": {"system": "alternateSelectedControlTextColor", "fallback": "#FFFFFF"}},
        "state": {"record": {"system": "systemRed", "fallback": "#FF453A"}, "play": {"system": "systemGreen", "fallback": "#32D74B"}, "solo": {"system": "systemYellow", "fallback": "#FFD60A"}, "mute": {"system": "systemBlue", "fallback": "#0A84FF"}, "warning": {"system": "systemOrange", "fallback": "#FF9F0A"}, "error": {"system": "systemRed", "fallback": "#FF453A"}, "offline": {"system": "systemGray", "fallback": "#98989D"}},
        "meter": {"background": "#141414", "low": "#30D158", "mid": "#FFD60A", "high": "#FF9F0A", "clip": "#FF453A"},
        "graph": {"line": {"system": "controlAccentColor", "fallback": "#0A84FF"}, "fill": "#0A84FF40", "grid": "#FFFFFF1A", "handle": "#E5E5E7", "handleSelected": {"system": "controlAccentColor", "fallback": "#0A84FF"}},
        "control": {"gain": "#8E8E93", "eqLow": "#E5534B", "eqLowMid": "#E3A21A", "eqHighMid": "#3FB950", "eqHigh": "#4C8DF6", "send": "#A371F7", "pan": "#39C5CF", "dynamics": "#F778BA", "filter": "#DB8B0B"},
        "strip": {"channel": "#6E7681", "instrument": "#3FB950", "auxReturn": "#A371F7", "bus": "#E3A21A", "master": "#E5534B"},
        "spacing": {"xxs": 2, "xs": 4, "s": 8, "m": 12, "l": 16, "xl": 24},
        "radius": {"none": 0, "s": 3, "m": 6, "l": 10},
        "iconStroke": {"s16": 1.0, "s24": 1.2, "s32": 1.6},
        "type": {"caption": {"size": 10, "weight": "regular"}, "body": {"size": 13, "weight": "regular"}, "label": {"size": 11, "weight": "medium"}, "title": {"size": 15, "weight": "semibold"}, "display": {"size": 24, "weight": "bold"}}
      }
    },
    {
      "id": "flat", "appearance": "light", "placeholder": true,
      "note": "PLACEHOLDER palette: rough values only, replaced in VizDAW SP7.",
      "values": {
        "surface": {"window": "#F2F2F2", "panel": "#FFFFFF", "raised": "#E6E6E6", "inset": "#D9D9D9", "separator": "#CCCCCC", "selection": "#0078D7", "focusRing": "#000000"},
        "text": {"primary": "#000000", "secondary": "#595959", "disabled": "#A6A6A6", "inverse": "#FFFFFF"},
        "accent": {"accent": "#0078D7", "onAccent": "#FFFFFF"},
        "state": {"record": "#E81123", "play": "#107C10", "solo": "#FFB900", "mute": "#0078D7", "warning": "#FF8C00", "error": "#E81123", "offline": "#767676"},
        "meter": {"background": "#1F1F1F", "low": "#107C10", "mid": "#FFB900", "high": "#FF8C00", "clip": "#E81123"},
        "graph": {"line": "#0078D7", "fill": "#0078D733", "grid": "#0000001A", "handle": "#000000", "handleSelected": "#0078D7"},
        "control": {"gain": "#767676", "eqLow": "#E81123", "eqLowMid": "#FF8C00", "eqHighMid": "#107C10", "eqHigh": "#0078D7", "send": "#881798", "pan": "#00B7C3", "dynamics": "#E3008C", "filter": "#CA5010"},
        "strip": {"channel": "#767676", "instrument": "#107C10", "auxReturn": "#881798", "bus": "#FF8C00", "master": "#E81123"},
        "spacing": {"xxs": 2, "xs": 4, "s": 8, "m": 12, "l": 16, "xl": 24},
        "radius": {"none": 0, "s": 0, "m": 0, "l": 0},
        "iconStroke": {"s16": 1.0, "s24": 1.2, "s32": 1.6},
        "type": {"caption": {"size": 10, "weight": "regular"}, "body": {"size": 13, "weight": "regular"}, "label": {"size": 11, "weight": "medium"}, "title": {"size": 15, "weight": "semibold"}, "display": {"size": 24, "weight": "bold"}}
      }
    },
    {
      "id": "console", "appearance": "dark", "placeholder": true,
      "note": "PLACEHOLDER palette: rough values only, replaced in VizDAW SP7.",
      "values": {
        "surface": {"window": "#1A1C1F", "panel": "#2A2D31", "raised": "#3A3E44", "inset": "#121315", "separator": "#00000080", "selection": "#C8A04066", "focusRing": "#E0B850"},
        "text": {"primary": "#E8E4DA", "secondary": "#A8A398", "disabled": "#5E5B55", "inverse": "#121315"},
        "accent": {"accent": "#E0B850", "onAccent": "#121315"},
        "state": {"record": "#FF3030", "play": "#40D060", "solo": "#FFD040", "mute": "#F08030", "warning": "#FFB020", "error": "#FF3030", "offline": "#707070"},
        "meter": {"background": "#0A0A0A", "low": "#30E060", "mid": "#F0E040", "high": "#FF9020", "clip": "#FF2020"},
        "graph": {"line": "#60D0FF", "fill": "#60D0FF33", "grid": "#FFFFFF14", "handle": "#E8E4DA", "handleSelected": "#E0B850"},
        "control": {"gain": "#B0B0B0", "eqLow": "#D04040", "eqLowMid": "#D09030", "eqHighMid": "#40A050", "eqHigh": "#4080D0", "send": "#9060C0", "pan": "#40B0B0", "dynamics": "#D060A0", "filter": "#C07030"},
        "strip": {"channel": "#808890", "instrument": "#40A050", "auxReturn": "#9060C0", "bus": "#D09030", "master": "#D04040"},
        "spacing": {"xxs": 2, "xs": 4, "s": 8, "m": 12, "l": 16, "xl": 24},
        "radius": {"none": 0, "s": 3, "m": 6, "l": 10},
        "iconStroke": {"s16": 1.0, "s24": 1.2, "s32": 1.6},
        "type": {"caption": {"size": 10, "weight": "regular"}, "body": {"size": 13, "weight": "regular"}, "label": {"size": 11, "weight": "medium"}, "title": {"size": 15, "weight": "semibold"}, "display": {"size": 24, "weight": "bold"}}
      }
    }
  ]
}
```

- [ ] **Step 4: Write the validator and contrast maths**

File: `tools/tokenlib.py`

```python
"""Design token file: validation and WCAG contrast (spec section 2)."""
import itertools
import json
import math
import re

KINDS = {"color", "points", "font"}
APPEARANCES = {"light", "dark"}
USES = {"body": 4.5, "large": 3.0, "icon": 3.0}
WEIGHTS = ["ultraLight", "thin", "light", "regular", "medium", "semibold", "bold", "heavy", "black"]
NAME = re.compile(r"^[a-z][A-Za-z0-9]*$")
THEME_ID = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")
HEX = re.compile(r"^#[0-9A-Fa-f]{6}([0-9A-Fa-f]{2})?$")

# macOS semantic colours a token may name (all available on macOS 13).
SYSTEM_COLORS = [
    "windowBackgroundColor", "underPageBackgroundColor", "controlBackgroundColor",
    "textBackgroundColor", "controlColor", "gridColor", "separatorColor",
    "selectedContentBackgroundColor", "unemphasizedSelectedContentBackgroundColor",
    "keyboardFocusIndicatorColor", "findHighlightColor",
    "labelColor", "secondaryLabelColor", "tertiaryLabelColor", "quaternaryLabelColor",
    "textColor", "disabledControlTextColor", "alternateSelectedControlTextColor",
    "selectedMenuItemTextColor", "controlAccentColor",
    "systemRed", "systemOrange", "systemYellow", "systemGreen", "systemMint", "systemTeal",
    "systemCyan", "systemBlue", "systemIndigo", "systemPurple", "systemPink", "systemBrown",
    "systemGray",
]


class TokenError(ValueError):
    """The token file is incomplete or malformed; .problems lists every issue."""

    def __init__(self, problems):
        super().__init__("\n".join(problems))
        self.problems = problems


def load(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    validate(data)
    return data


def _is_number(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _check_value(kind, value):
    """Return None if value is valid for kind, else a short reason."""
    if kind == "color":
        if isinstance(value, str):
            return None if HEX.match(value) else f"not #RRGGBB or #RRGGBBAA: {value!r}"
        if isinstance(value, dict):
            if set(value) != {"system", "fallback"}:
                return "a system colour needs exactly 'system' and 'fallback'"
            if value["system"] not in SYSTEM_COLORS:
                return f"unknown macOS system colour {value['system']!r}"
            if not isinstance(value["fallback"], str) or not HEX.match(value["fallback"]):
                return f"fallback not #RRGGBB or #RRGGBBAA: {value['fallback']!r}"
            return None
        return f"not a colour: {value!r}"
    if kind == "points":
        return None if _is_number(value) and value >= 0 else f"not a non-negative number: {value!r}"
    if not isinstance(value, dict) or set(value) != {"size", "weight"}:
        return f"a type style needs exactly 'size' and 'weight': {value!r}"
    if not _is_number(value["size"]) or value["size"] <= 0:
        return f"size not a positive number: {value['size']!r}"
    if value["weight"] not in WEIGHTS:
        return f"weight {value['weight']!r} not one of {', '.join(WEIGHTS)}"
    return None


def validate(data):
    problems = []
    if not isinstance(data, dict):
        raise TokenError(["the file must hold a JSON object"])
    for key in sorted(set(data) - {"description", "tokens", "contrast", "themes"}):
        problems.append(f"unknown top-level key {key!r}")
    groups = data.get("tokens")
    if not isinstance(groups, dict) or not groups:
        raise TokenError(problems + ["'tokens' must be a non-empty object"])
    kinds = {}
    for group, spec in groups.items():
        if not NAME.match(group):
            problems.append(f"token group name {group!r} must be lowerCamelCase")
        if not isinstance(spec, dict) or set(spec) != {"kind", "items"}:
            problems.append(f"token group {group!r} needs exactly 'kind' and 'items'")
            continue
        if spec["kind"] not in KINDS:
            problems.append(f"token group {group!r}: kind {spec['kind']!r} not one of color, points, font")
        if not isinstance(spec["items"], dict) or not spec["items"]:
            problems.append(f"token group {group!r}: 'items' must be a non-empty object")
            continue
        for name, desc in spec["items"].items():
            if not NAME.match(name):
                problems.append(f"token {group}.{name}: name must be lowerCamelCase")
            if not isinstance(desc, str) or not desc.strip():
                problems.append(f"token {group}.{name}: needs a one-line description")
            kinds[f"{group}.{name}"] = spec["kind"]
    themes = data.get("themes")
    if not isinstance(themes, list) or not themes:
        raise TokenError(problems + ["'themes' must be a non-empty list"])
    seen = set()
    for i, theme in enumerate(themes):
        if not isinstance(theme, dict):
            problems.append(f"themes[{i}] must be an object")
            continue
        tid = theme.get("id", f"themes[{i}]")
        for key in sorted(set(theme) - {"id", "appearance", "placeholder", "note", "values"}):
            problems.append(f"theme {tid}: unknown key {key!r}")
        if not isinstance(tid, str) or not THEME_ID.match(tid):
            problems.append(f"theme id {tid!r} must be lower-case words joined by hyphens")
        elif tid in seen:
            problems.append(f"theme id {tid!r} is used twice")
        seen.add(tid)
        if theme.get("appearance") not in APPEARANCES:
            problems.append(f"theme {tid}: appearance must be light or dark")
        if not isinstance(theme.get("placeholder", False), bool):
            problems.append(f"theme {tid}: placeholder must be true or false")
        values = theme.get("values")
        if not isinstance(values, dict):
            problems.append(f"theme {tid}: 'values' must be an object")
            continue
        flat = {}
        for group, items in values.items():
            if not isinstance(items, dict):
                problems.append(f"theme {tid} defines unknown token group {group}" if group not in groups
                                else f"theme {tid}: {group} must be an object")
                continue
            for name, value in items.items():
                flat[f"{group}.{name}"] = value
        for token in kinds:
            if token not in flat:
                problems.append(f"theme {tid} lacks {token}")
        for token, value in flat.items():
            if token not in kinds:
                problems.append(f"theme {tid} defines unknown token {token}")
                continue
            reason = _check_value(kinds[token], value)
            if reason:
                problems.append(f"theme {tid}, {token}: {reason}")
    pairs = data.get("contrast", [])
    if not isinstance(pairs, list):
        problems.append("'contrast' must be a list")
        pairs = []
    for i, pair in enumerate(pairs):
        if not isinstance(pair, dict) or set(pair) != {"text", "on", "use"}:
            problems.append(f"contrast[{i}] needs exactly 'text', 'on' and 'use'")
            continue
        for key in ("text", "on"):
            if kinds.get(pair[key]) != "color":
                problems.append(f"contrast[{i}]: {pair[key]!r} is not a colour token")
        if pair["use"] not in USES:
            problems.append(f"contrast[{i}]: use must be body, large or icon")
    if problems:
        raise TokenError(problems)


def flat_values(theme):
    return {f"{g}.{n}": v for g, items in theme["values"].items() for n, v in items.items()}


# ---------------------------------------------------------------- contrast

def rgba(value):
    """Colour token value -> (r, g, b, a) floats 0-1, using the fallback for system colours."""
    text = value["fallback"] if isinstance(value, dict) else value
    h = text[1:]
    parts = [int(h[i:i + 2], 16) / 255 for i in range(0, len(h), 2)]
    return tuple(parts) if len(parts) == 4 else tuple(parts) + (1.0,)


def over(top, bottom):
    """Composite top over an opaque bottom colour."""
    a = top[3]
    return tuple(top[i] * a + bottom[i] * (1 - a) for i in range(3)) + (1.0,)


def luminance(c):
    def lin(v):
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(v) for v in c[:3])
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(fg, bg):
    hi, lo = sorted((luminance(fg), luminance(bg)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def contrast_rows(data):
    """[(theme id, text token, on token, use, ratio, needed, ok)] for every theme and pair."""
    rows = []
    for theme in data["themes"]:
        values = flat_values(theme)
        base = (1.0, 1.0, 1.0, 1.0) if theme["appearance"] == "light" else (0.0, 0.0, 0.0, 1.0)
        for pair in data.get("contrast", []):
            bg = over(rgba(values[pair["on"]]), base)
            fg = over(rgba(values[pair["text"]]), bg)
            ratio = contrast_ratio(fg, bg)
            need = USES[pair["use"]]
            rows.append((theme["id"], pair["text"], pair["on"], pair["use"], ratio, need, ratio >= need))
    return rows


def format_ratio(ratio):
    """Two decimals, rounded down, so a failing 4.499 never prints as 4.50."""
    return f"{math.floor(ratio * 100) / 100:.2f}:1"


def contrast_markdown(rows):
    lines = ["# Contrast report", "",
             "Generated by `tools/generate.py` from `tokens/tokens.json`; do not edit.",
             "WCAG AA: 4.5:1 for body text, 3:1 for large text and icons. System colours are",
             "checked through their fallbacks. A WARN is reported, not fatal: the starter",
             "palettes are not final.", ""]
    for tid, group in itertools.groupby(rows, key=lambda r: r[0]):
        lines += [f"## {tid}", "", "| Text | On | Use | Ratio | Needs | Result |", "|---|---|---|---|---|---|"]
        for _, text, on, use, ratio, need, ok in group:
            lines.append(f"| `{text}` | `{on}` | {use} | {format_ratio(ratio)} | {need:g}:1 | {'pass' if ok else 'WARN'} |")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"
```

- [ ] **Step 5: Run the tests to verify they pass**

Run:

```bash
export DEVELOPER_DIR=/Library/Developer/CommandLineTools PYTHONDONTWRITEBYTECODE=1
python3 -m unittest discover -s tools/tests 2>&1 | tail -3
```

Expected: `Ran 65 tests`, `OK`.

- [ ] **Step 6: Commit**

Run:

```bash
export DEVELOPER_DIR=/Library/Developer/CommandLineTools PYTHONDONTWRITEBYTECODE=1
git add tokens/tokens.json \
  tools/tokenlib.py \
  tools/tests/test_tokenlib.py
git status --short
git commit -q -F - <<'MSG'
Tokens: four themes, validation and WCAG contrast

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01F7df6grqTdqHgc2d2X359P
MSG
git status --short
```

Expected: `git status --short` before the commit lists only the paths above (no `.DS_Store`, no `__pycache__`); after the commit it prints nothing.

### Task 3: Generator and the SymbioticTokens product

`tools/generate.py` (tokens only for now) writes the generated `Theme` and `tokens/contrast.md`; the package starts with the `SymbioticTokens` product, its hand-written colour/type/environment code and its tests.

**Files:**
- Create: `tools/swiftgen_common.py`, `tools/swiftgen_tokens.py`, `tools/generate.py`
- Create: `Package.swift`, `scripts/swift.sh`
- Modify: `.gitignore` (append two lines)
- Create: `Sources/SymbioticTokens/ThemeColor.swift`, `Sources/SymbioticTokens/TypeStyle.swift`, `Sources/SymbioticTokens/Theme+Lookup.swift`
- Generated (by Step 6): `Sources/SymbioticTokens/Generated/Theme+Generated.swift`, `Sources/SymbioticTokens/Generated/SystemColorName+Generated.swift`, `tokens/contrast.md`
- Test: `tools/tests/test_swiftgen_tokens.py`, `tools/tests/test_generate.py`, `Tests/SymbioticTokensTests/ThemeTests.swift`

**Interfaces:**
- Consumes: `tokenlib.load`, `tokenlib.contrast_rows`, `tokenlib.contrast_markdown`, `tokenlib.format_ratio`, `tokenlib.flat_values`, `tokenlib.SYSTEM_COLORS`, `tokenlib.TokenError` (Task 2); `test_tokenlib.minimal()`.
- Produces (Python): `swiftgen_common.MIT_HEADER`, `lower_camel(text)`, `upper_camel(text)`, `identifier(name)` (back-quotes Swift keywords), `number(value, places=4)`, `string_literal(text)`, `license_comment(text)`; `swiftgen_tokens.OUT = "Sources/SymbioticTokens/Generated"`, `swiftgen_tokens.generate(data) -> dict[path, text]`; `generate.py` functions `write_tree(files, owned_dirs)`, `tokens_step() -> (files, owned_dirs)`, `main() -> int`. Test helper class `test_generate.Scratch` (copies `tools`, `tokens`, `icons`, `Sources`, `ASSETS-LICENSE` to a temp dir; `run_generate()`, `snapshot()`, `edit_json(rel, change)`) that Tasks 4 and 6 extend.
- Produces (Swift, module `SymbioticTokens`): `struct Theme: Sendable, Hashable, Identifiable` with `id: String`, `appearance: ThemeAppearance`, `isPlaceholder: Bool` and groups `surface: SurfaceColors`, `text: TextColors`, `accent: AccentColors`, `state: StateColors`, `meter: MeterColors`, `graph: GraphColors`, `control: ControlColors`, `strip: StripColors`, `spacing: SpacingMetrics`, `radius: RadiusMetrics`, `iconStroke: IconStrokeMetrics` (`s16`, `s24`, `s32: CGFloat`), `type: TypeStyles`; `Theme.classicLight`, `.studioDark`, `.flat`, `.console`, `Theme.all`; `Theme.named(_ id: String) -> Theme?`; `Theme.standard(for: ColorScheme) -> Theme`; `Theme.IconStrokeMetrics.width(forSize: CGFloat) -> CGFloat`; `struct ThemeColor` (`.nsColor: NSColor`, `.color: Color`, `.fallbackComponents`); `enum ThemeAppearance { light, dark }`; `struct TypeStyle` (`size`, `weight: FontWeight`, `.font`, `.nsFont`); `enum SystemColorName`; `EnvironmentValues.symbioticTheme: Theme`.

- [ ] **Step 1: Write the failing Python tests**

File: `tools/tests/test_swiftgen_tokens.py`

```python
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import swiftgen_common as c  # noqa: E402
import swiftgen_tokens as g  # noqa: E402
from test_tokenlib import minimal  # noqa: E402


class Common(unittest.TestCase):
    def test_camel_case(self):
        self.assertEqual(c.lower_camel("transport.play"), "transportPlay")
        self.assertEqual(c.lower_camel("return-to-zero"), "returnToZero")
        self.assertEqual(c.lower_camel("glyph-05"), "glyph05")
        self.assertEqual(c.lower_camel("classic-light"), "classicLight")
        self.assertEqual(c.upper_camel("iconStroke"), "IconStroke")

    def test_keywords_are_back_quoted(self):
        self.assertEqual(c.identifier("import"), "`import`")
        self.assertEqual(c.identifier("play"), "play")
        with self.assertRaises(ValueError):
            c.identifier("9lives")

    def test_numbers_are_short_and_stable(self):
        self.assertEqual([c.number(v) for v in (1.0, 0.123456, -0.00001, 12.5, 2.0000001)],
                         ["1", "0.1235", "0", "12.5", "2"])

    def test_string_literal_escapes(self):
        self.assertEqual(c.string_literal('a "b" \\'), '"a \\"b\\" \\\\"')

    def test_license_comment(self):
        self.assertEqual(c.license_comment("A\n\nB\n"), "// A\n//\n// B\n")


class TokensSwift(unittest.TestCase):
    def setUp(self):
        self.files = g.generate(minimal())
        self.theme = self.files["Sources/SymbioticTokens/Generated/Theme+Generated.swift"]

    def test_file_set(self):
        self.assertEqual(sorted(self.files), ["Sources/SymbioticTokens/Generated/SystemColorName+Generated.swift",
                                              "Sources/SymbioticTokens/Generated/Theme+Generated.swift"])

    def test_header_and_groups(self):
        self.assertTrue(self.theme.startswith("// Generated by tools/generate.py"))
        self.assertIn("    public let text: TextColors", self.theme)
        self.assertIn("    public let type: TypeStyles", self.theme)
        self.assertIn("        /// Main text\n        public let primary: ThemeColor", self.theme)
        self.assertIn("    public struct SpacingMetrics: Sendable, Hashable {", self.theme)

    def test_values(self):
        self.assertIn("primary: ThemeColor(hex: 0x000000FF)", self.theme)
        self.assertIn("window: ThemeColor(system: .windowBackgroundColor, fallback: 0xFFFFFFFF, appearance: .light)",
                      self.theme)
        self.assertIn("m: 12", self.theme)
        self.assertIn("body: TypeStyle(size: 13, weight: .regular)", self.theme)
        self.assertIn("    public static let classicLight = Theme(", self.theme)
        self.assertIn("    public static let all: [Theme] = [.classicLight]", self.theme)

    def test_alpha_hex(self):
        self.assertEqual(g.hex_literal("#00000080"), "0x00000080")
        self.assertEqual(g.hex_literal("#abcdef"), "0xABCDEFFF")

    def test_system_colour_enum_lists_every_allowed_name(self):
        text = self.files["Sources/SymbioticTokens/Generated/SystemColorName+Generated.swift"]
        for name in ("windowBackgroundColor", "controlAccentColor", "systemRed"):
            self.assertIn(f"    case {name}\n", text)
            self.assertIn(f"        case .{name}: return .{name}\n", text)

    def test_output_is_deterministic(self):
        self.assertEqual(g.generate(minimal()), self.files)


if __name__ == "__main__":
    unittest.main()
```

File: `tools/tests/test_generate.py`

```python
"""Runs tools/generate.py on a scratch copy of the repository."""
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
COPY = ["tools", "tokens", "icons", "Sources", "ASSETS-LICENSE"]


class Scratch(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.tmp.name)
        for name in COPY:
            src = ROOT / name
            if src.is_dir():
                shutil.copytree(src, self.root / name, ignore=shutil.ignore_patterns("__pycache__"))
            elif src.exists():
                shutil.copy2(src, self.root / name)

    def tearDown(self):
        self.tmp.cleanup()

    def run_generate(self):
        return subprocess.run([sys.executable, str(self.root / "tools" / "generate.py")],
                              capture_output=True, text=True)

    def snapshot(self):
        return {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*")
                if p.is_file() and "__pycache__" not in p.parts}

    def edit_json(self, rel, change):
        path = self.root / rel
        data = json.loads(path.read_text(encoding="utf-8"))
        change(data)
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


class Tokens(Scratch):
    def test_committed_output_is_up_to_date(self):
        before = self.snapshot()
        result = self.run_generate()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.snapshot(), before, "run python3 tools/generate.py and commit the result")

    def test_contrast_warnings_are_printed_not_fatal(self):
        def lower_contrast(d):
            d["themes"][0]["values"]["text"]["primary"] = "#EEEEEE"
        self.edit_json("tokens/tokens.json", lower_contrast)
        result = self.run_generate()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("warning: classic-light: text.primary on surface.window", result.stdout)
        self.assertIn("| `text.primary` | `surface.window` | body |",
                      (self.root / "tokens" / "contrast.md").read_text(encoding="utf-8"))

    def test_missing_token_fails_and_writes_nothing(self):
        def drop(d):
            del d["themes"][2]["values"]["meter"]["clip"]
        self.edit_json("tokens/tokens.json", drop)
        before = self.snapshot()
        result = self.run_generate()
        self.assertEqual(result.returncode, 1)
        self.assertIn("error: tokens.json: theme flat lacks meter.clip", result.stderr)
        self.assertEqual(self.snapshot(), before)

    def test_stale_generated_files_are_removed(self):
        stale = self.root / "Sources" / "SymbioticTokens" / "Generated" / "Old.swift"
        stale.write_text("// old\n", encoding="utf-8")
        self.assertEqual(self.run_generate().returncode, 0)
        self.assertFalse(stale.exists())
```

- [ ] **Step 2: Run them to verify they fail**

Run:

```bash
export DEVELOPER_DIR=/Library/Developer/CommandLineTools PYTHONDONTWRITEBYTECODE=1
python3 -m unittest discover -s tools/tests 2>&1 | tail -3
```

Expected: `FAILED (failures=3, errors=2)`: `No module named 'swiftgen_common'`, and the generator tests fail because `tools/generate.py` does not exist yet.

- [ ] **Step 3: Write the Swift test**

File: `Tests/SymbioticTokensTests/ThemeTests.swift`

```swift
// MIT licence: see LICENSE.
import AppKit
import SwiftUI
import Testing
@testable import SymbioticTokens

@Suite struct ThemeTests {
    @Test func fourThemesInOrder() {
        #expect(Theme.all.map(\.id) == ["classic-light", "studio-dark", "flat", "console"])
        #expect(Theme.all.map(\.appearance) == [.light, .dark, .light, .dark])
        #expect(Theme.all.map(\.isPlaceholder) == [false, false, true, true])
    }

    @Test func typedGroupsReadAsInTheSpec() {
        let theme = Theme.classicLight
        #expect(theme.spacing.m == 12)
        #expect(theme.meter.clip.fallbackComponents.red == 1)
        #expect(theme.control.eqLow == Theme.classicLight.control.eqLow)
        #expect(theme.type.body.size == 13)
        #expect(theme.type.title.weight == .semibold)
    }

    @Test(arguments: Theme.all.map(\.id))
    func everyTokenResolves(id: String) throws {
        let theme = try #require(Theme.named(id))
        let colours: [ThemeColor] = [
            theme.surface.window, theme.surface.panel, theme.surface.raised, theme.surface.inset,
            theme.surface.separator, theme.surface.selection, theme.surface.focusRing,
            theme.text.primary, theme.text.secondary, theme.text.disabled, theme.text.inverse,
            theme.accent.accent, theme.accent.onAccent,
            theme.state.record, theme.state.play, theme.state.solo, theme.state.mute,
            theme.state.warning, theme.state.error, theme.state.offline,
            theme.meter.background, theme.meter.low, theme.meter.mid, theme.meter.high, theme.meter.clip,
            theme.graph.line, theme.graph.fill, theme.graph.grid, theme.graph.handle, theme.graph.handleSelected,
            theme.control.gain, theme.control.eqLow, theme.control.eqLowMid, theme.control.eqHighMid,
            theme.control.eqHigh, theme.control.send, theme.control.pan, theme.control.dynamics, theme.control.filter,
            theme.strip.channel, theme.strip.instrument, theme.strip.auxReturn, theme.strip.bus, theme.strip.master,
        ]
        for colour in colours {
            #expect(colour.nsColor.usingColorSpace(.sRGB) != nil)
            _ = colour.color
        }
        let metrics: [CGFloat] = [
            theme.spacing.xxs, theme.spacing.xs, theme.spacing.s, theme.spacing.m, theme.spacing.l, theme.spacing.xl,
            theme.radius.none, theme.radius.s, theme.radius.m, theme.radius.l,
            theme.iconStroke.s16, theme.iconStroke.s24, theme.iconStroke.s32,
        ]
        #expect(metrics.allSatisfy { $0 >= 0 })
        for style in [theme.type.caption, theme.type.body, theme.type.label, theme.type.title, theme.type.display] {
            #expect(style.nsFont.pointSize == style.size)
        }
    }

    @Test func hexColourIsExact() {
        let c = ThemeColor(hex: 0x336699CC).nsColor.usingColorSpace(.sRGB)!
        #expect(abs(c.redComponent - 0x33 / 255.0) < 0.0001)
        #expect(abs(c.alphaComponent - 0xCC / 255.0) < 0.0001)
    }

    @Test func lightThemeStaysLightInDarkMode() {
        var light = NSColor.black
        var dark = NSColor.white
        NSAppearance(named: .darkAqua)!.performAsCurrentDrawingAppearance {
            light = Theme.classicLight.surface.window.nsColor.usingColorSpace(.sRGB)!
        }
        NSAppearance(named: .aqua)!.performAsCurrentDrawingAppearance {
            dark = Theme.studioDark.surface.window.nsColor.usingColorSpace(.sRGB)!
        }
        #expect(light.brightnessComponent > 0.6)
        #expect(dark.brightnessComponent < 0.4)
    }

    @Test func environmentDefaultFollowsColorScheme() {
        var env = EnvironmentValues()
        env.colorScheme = .light
        #expect(env.symbioticTheme.id == "classic-light")
        env.colorScheme = .dark
        #expect(env.symbioticTheme.id == "studio-dark")
        env.symbioticTheme = .console
        env.colorScheme = .light
        #expect(env.symbioticTheme.id == "console")
    }

    @Test func lookupByID() {
        #expect(Theme.named("flat") == .flat)
        #expect(Theme.named("cubase-dark") == nil)
    }

    @Test func iconStrokeIsExactAtTokenSizesAndScalesOutside() {
        let s = Theme.classicLight.iconStroke
        #expect(s.width(forSize: 16) == s.s16)
        #expect(s.width(forSize: 24) == s.s24)
        #expect(s.width(forSize: 32) == s.s32)
        #expect(abs(s.width(forSize: 20) - (s.s16 + s.s24) / 2) < 0.0001)
        #expect(abs(s.width(forSize: 48) - s.s32 * 1.5) < 0.0001)
        #expect(abs(s.width(forSize: 8) - s.s16 / 2) < 0.0001)
    }
}
```

- [ ] **Step 4: Write the generator modules**

File: `tools/swiftgen_common.py`

```python
"""Helpers shared by the Swift code generators."""
import re

MIT_HEADER = ("// Generated by tools/generate.py. Do not edit; edit the JSON/SVG sources and regenerate.\n"
              "// MIT licence: see LICENSE.\n")

SWIFT_KEYWORDS = {
    "associatedtype", "class", "deinit", "enum", "extension", "fileprivate", "func", "import", "init",
    "inout", "internal", "let", "open", "operator", "private", "protocol", "public", "rethrows", "static",
    "struct", "subscript", "typealias", "var", "break", "case", "continue", "default", "defer", "do",
    "else", "fallthrough", "for", "guard", "if", "in", "repeat", "return", "switch", "where", "while",
    "as", "catch", "false", "is", "nil", "super", "self", "Self", "throw", "throws", "true", "try",
    "Any", "Type", "Protocol",
}


def words(text):
    return [w for w in re.split(r"[^A-Za-z0-9]+", text) if w]


def lower_camel(text):
    """'transport.play' -> 'transportPlay', 'return-to-zero' -> 'returnToZero', 'glyph-05' -> 'glyph05'."""
    parts = words(text)
    head, rest = parts[0], parts[1:]
    out = head[0].lower() + head[1:] + "".join(p[0].upper() + p[1:] for p in rest)
    return out


def upper_camel(text):
    c = lower_camel(text)
    return c[0].upper() + c[1:]


def identifier(name):
    """A Swift identifier, back-quoted when it is a keyword."""
    if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", name):
        raise ValueError(f"not a Swift identifier: {name!r}")
    return f"`{name}`" if name in SWIFT_KEYWORDS else name


def number(value, places=4):
    """Deterministic short decimal: 1.0 -> '1', 0.12345 -> '0.1235', -0.0 -> '0'."""
    text = f"{value:.{places}f}".rstrip("0").rstrip(".")
    return "0" if text in ("-0", "") else text


def string_literal(text):
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


def license_comment(text):
    """Turn a licence file into a Swift comment block."""
    return "".join(f"// {line}".rstrip() + "\n" for line in text.rstrip("\n").split("\n"))
```

File: `tools/swiftgen_tokens.py`

```python
"""tokens.json -> Swift source for the SymbioticTokens product (spec section 2.5)."""
from swiftgen_common import MIT_HEADER, identifier, lower_camel, number, string_literal, upper_camel
from tokenlib import SYSTEM_COLORS, flat_values

OUT = "Sources/SymbioticTokens/Generated"
SUFFIX = {"color": "Colors", "points": "Metrics", "font": "Styles"}
SWIFT_TYPE = {"color": "ThemeColor", "points": "CGFloat", "font": "TypeStyle"}


def struct_name(group, kind):
    return upper_camel(group) + SUFFIX[kind]


def hex_literal(text):
    h = text[1:].upper()
    if len(h) == 6:
        h += "FF"
    return f"0x{h}"


def value_literal(kind, value, appearance):
    if kind == "color":
        if isinstance(value, dict):
            return (f"ThemeColor(system: .{value['system']}, fallback: {hex_literal(value['fallback'])}, "
                    f"appearance: .{appearance})")
        return f"ThemeColor(hex: {hex_literal(value)})"
    if kind == "points":
        return number(value)
    return f"TypeStyle(size: {number(value['size'])}, weight: .{value['weight']})"


def theme_swift(data):
    groups = data["tokens"]
    lines = [MIT_HEADER, "import CoreGraphics", "", "/// One complete set of design tokens. Generated from tokens/tokens.json.",
             "public struct Theme: Sendable, Hashable, Identifiable {",
             "    /// Neutral theme ID, e.g. \"classic-light\".",
             "    public let id: String",
             "    public let appearance: ThemeAppearance",
             "    /// True while the theme still has rough placeholder values (replaced in VizDAW SP7).",
             "    public let isPlaceholder: Bool"]
    for group, spec in groups.items():
        lines.append(f"    public let {identifier(lower_camel(group))}: {struct_name(group, spec['kind'])}")
    lines.append("}")
    lines.append("")
    lines.append("extension Theme {")
    for group, spec in groups.items():
        kind = spec["kind"]
        lines.append(f"    public struct {struct_name(group, kind)}: Sendable, Hashable {{")
        for name, desc in spec["items"].items():
            lines.append(f"        /// {desc}")
            lines.append(f"        public let {identifier(name)}: {SWIFT_TYPE[kind]}")
        lines.append("    }")
        lines.append("")
    for theme in data["themes"]:
        values = flat_values(theme)
        prop = lower_camel(theme["id"])
        lines.append(f"    public static let {identifier(prop)} = Theme(")
        lines.append(f"        id: {string_literal(theme['id'])},")
        lines.append(f"        appearance: .{theme['appearance']},")
        lines.append(f"        isPlaceholder: {'true' if theme.get('placeholder', False) else 'false'},")
        group_lines = []
        for group, spec in groups.items():
            kind = spec["kind"]
            args = ",\n".join(
                f"            {name}: {value_literal(kind, values[f'{group}.{name}'], theme['appearance'])}"
                for name in spec["items"])
            group_lines.append(f"        {lower_camel(group)}: {struct_name(group, kind)}(\n{args}\n        )")
        lines.append(",\n".join(group_lines))
        lines.append("    )")
        lines.append("")
    all_themes = ", ".join(f".{identifier(lower_camel(t['id']))}" for t in data["themes"])
    lines.append("    /// Every theme, in tokens.json order.")
    lines.append(f"    public static let all: [Theme] = [{all_themes}]")
    lines.append("}")
    return "\n".join(lines) + "\n"


def system_colors_swift():
    lines = [MIT_HEADER, "import AppKit", "",
             "/// The macOS semantic colours a token may name (tools/tokenlib.py SYSTEM_COLORS).",
             "public enum SystemColorName: String, Sendable, Hashable, CaseIterable {"]
    lines += [f"    case {name}" for name in SYSTEM_COLORS]
    lines += ["", "    /// The dynamic AppKit colour; it follows the current drawing appearance.",
              "    public var nsColor: NSColor {", "        switch self {"]
    lines += [f"        case .{name}: return .{name}" for name in SYSTEM_COLORS]
    lines += ["        }", "    }", "}"]
    return "\n".join(lines) + "\n"


def generate(data):
    """{relative path: file text} for the SymbioticTokens generated sources."""
    return {
        f"{OUT}/Theme+Generated.swift": theme_swift(data),
        f"{OUT}/SystemColorName+Generated.swift": system_colors_swift(),
    }
```

File: `tools/generate.py`

```python
#!/usr/bin/env python3
"""Validate the design sources and write every generated file.

Usage: python3 tools/generate.py
Writes tokens/contrast.md and Sources/SymbioticTokens/Generated/.
Exit status 1 (and nothing written) if a source is invalid.
"""
import pathlib
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import swiftgen_tokens  # noqa: E402
import tokenlib  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]


def write_tree(files, owned_dirs):
    """Write {relative path: text}; delete stale files in the generated dirs."""
    for d in owned_dirs:
        folder = ROOT / d
        if folder.is_dir():
            for old in folder.glob("*.swift"):
                if str(old.relative_to(ROOT)) not in files:
                    old.unlink()
    for rel, text in sorted(files.items()):
        path = ROOT / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def tokens_step():
    data = tokenlib.load(ROOT / "tokens" / "tokens.json")
    rows = tokenlib.contrast_rows(data)
    for tid, text, on, use, ratio, need, ok in rows:
        if not ok:
            print(f"warning: {tid}: {text} on {on} is {tokenlib.format_ratio(ratio)}, {use} needs {need:g}:1")
    files = swiftgen_tokens.generate(data)
    files["tokens/contrast.md"] = tokenlib.contrast_markdown(rows)
    return files, [swiftgen_tokens.OUT]


def main():
    try:
        files, owned = tokens_step()
    except tokenlib.TokenError as e:
        for p in e.problems:
            print(f"error: tokens.json: {p}", file=sys.stderr)
        return 1
    write_tree(files, owned)
    print(f"wrote {len(files)} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 5: Write the package skeleton and the hand-written Swift**

File: `Package.swift`

```swift
// swift-tools-version: 6.0
// MIT licence: see LICENSE.
import PackageDescription

/// The one place the deployment floor is set (spec section 4).
let minimumMacOS: SupportedPlatform = .macOS(.v14)

let package = Package(
    name: "symbiotic-design",
    platforms: [minimumMacOS],
    products: [
        .library(name: "SymbioticTokens", targets: ["SymbioticTokens"]),
    ],
    targets: [
        .target(name: "SymbioticTokens"),
        .testTarget(name: "SymbioticTokensTests", dependencies: ["SymbioticTokens"]),
    ]
)
```

File: `scripts/swift.sh`

```bash
#!/usr/bin/env bash
# Runs SwiftPM on this package with the flags the toolchain needs.
# Usage: scripts/swift.sh <build|test> [swift args...]
# MIT licence: see LICENSE.
set -euo pipefail
if [[ $# -lt 1 ]]; then
    echo "usage: scripts/swift.sh <build|test> [args...]" >&2
    exit 2
fi
root="$(cd "$(dirname "$0")/.." && pwd)"
cmd="$1"
shift
clt="/Library/Developer/CommandLineTools"
if [[ "${DEVELOPER_DIR:-}" != "$clt" ]]; then
    # Full Xcode (CI runners): default build system, Swift Testing in place.
    exec swift "$cmd" --package-path "$root" "$@"
fi
# Command Line Tools only: the native build system, plus the paths of
# Swift Testing, which the CLT ship outside the default search paths.
fw="$clt/Library/Developer/Frameworks"
exec swift "$cmd" --package-path "$root" --build-system native \
    -Xswiftc "-F$fw" \
    -Xlinker "-F$fw" \
    -Xlinker -rpath -Xlinker "$fw" \
    -Xlinker -rpath -Xlinker "$clt/Library/Developer/usr/lib" \
    "$@"
```

Append to `.gitignore`:

```text
.build/
.swiftpm/
```

File: `Sources/SymbioticTokens/ThemeColor.swift`

```swift
// MIT licence: see LICENSE.
import AppKit
import SwiftUI

/// Light or dark: the appearance a theme is designed for.
public enum ThemeAppearance: String, Sendable, Hashable, CaseIterable {
    case light
    case dark

    public var colorScheme: ColorScheme { self == .dark ? .dark : .light }

    public var nsAppearanceName: NSAppearance.Name { self == .dark ? .darkAqua : .aqua }
}

/// A colour token value: an sRGB colour, or a macOS semantic colour with an sRGB fallback.
public struct ThemeColor: Sendable, Hashable {
    public enum Source: Sendable, Hashable {
        /// 0xRRGGBBAA in sRGB.
        case rgba(UInt32)
        /// A macOS semantic colour, resolved in the theme's appearance; the fallback serves other platforms.
        case system(SystemColorName, fallback: UInt32)
    }

    public let source: Source
    /// The appearance a system colour is resolved in, so a light theme stays light in Dark Mode.
    public let appearance: ThemeAppearance

    public init(hex: UInt32) {
        source = .rgba(hex)
        appearance = .light
    }

    public init(system: SystemColorName, fallback: UInt32, appearance: ThemeAppearance) {
        source = .system(system, fallback: fallback)
        self.appearance = appearance
    }

    /// The sRGB value written in tokens.json (the fallback for a system colour), as 0...1 components.
    public var fallbackComponents: (red: Double, green: Double, blue: Double, alpha: Double) {
        let v: UInt32
        switch source {
        case .rgba(let x): v = x
        case .system(_, let fallback): v = fallback
        }
        return (Double((v >> 24) & 0xFF) / 255, Double((v >> 16) & 0xFF) / 255,
                Double((v >> 8) & 0xFF) / 255, Double(v & 0xFF) / 255)
    }

    public var nsColor: NSColor {
        switch source {
        case .rgba:
            let c = fallbackComponents
            return NSColor(srgbRed: c.red, green: c.green, blue: c.blue, alpha: c.alpha)
        case .system(let name, _):
            let pinned = appearance.nsAppearanceName
            return NSColor(name: nil) { _ in
                var resolved = NSColor.black
                let appearance = NSAppearance(named: pinned) ?? NSAppearance.currentDrawing()
                appearance.performAsCurrentDrawingAppearance {
                    resolved = name.nsColor.usingColorSpace(.sRGB) ?? name.nsColor
                }
                return resolved
            }
        }
    }

    public var color: Color { Color(nsColor: nsColor) }
}
```

File: `Sources/SymbioticTokens/TypeStyle.swift`

```swift
// MIT licence: see LICENSE.
import AppKit
import SwiftUI

/// The weights a type token may use (tools/tokenlib.py WEIGHTS).
public enum FontWeight: String, Sendable, Hashable, CaseIterable {
    case ultraLight, thin, light, regular, medium, semibold, bold, heavy, black

    public var swiftUI: Font.Weight {
        switch self {
        case .ultraLight: return .ultraLight
        case .thin: return .thin
        case .light: return .light
        case .regular: return .regular
        case .medium: return .medium
        case .semibold: return .semibold
        case .bold: return .bold
        case .heavy: return .heavy
        case .black: return .black
        }
    }

    public var appKit: NSFont.Weight {
        switch self {
        case .ultraLight: return .ultraLight
        case .thin: return .thin
        case .light: return .light
        case .regular: return .regular
        case .medium: return .medium
        case .semibold: return .semibold
        case .bold: return .bold
        case .heavy: return .heavy
        case .black: return .black
        }
    }
}

/// A type token: the system font at a size and weight.
public struct TypeStyle: Sendable, Hashable {
    public let size: CGFloat
    public let weight: FontWeight

    public init(size: CGFloat, weight: FontWeight) {
        self.size = size
        self.weight = weight
    }

    public var font: Font { .system(size: size, weight: weight.swiftUI) }
    public var nsFont: NSFont { .systemFont(ofSize: size, weight: weight.appKit) }
}
```

File: `Sources/SymbioticTokens/Theme+Lookup.swift`

```swift
// MIT licence: see LICENSE.
import CoreGraphics
import SwiftUI

extension Theme {
    /// The theme with this ID, e.g. a choice saved in preferences.
    public static func named(_ id: String) -> Theme? {
        all.first { $0.id == id }
    }

    /// The default theme for a colour scheme: classic-light or studio-dark.
    public static func standard(for scheme: ColorScheme) -> Theme {
        scheme == .dark ? .studioDark : .classicLight
    }
}

extension Theme.IconStrokeMetrics {
    /// Icon stroke width in points for an icon drawn at `size` points.
    ///
    /// Exact at 16, 24 and 32; linear between them; proportional to the
    /// nearest token below 16 and above 32.
    public func width(forSize size: CGFloat) -> CGFloat {
        if size <= 16 { return s16 * size / 16 }
        if size <= 24 { return s16 + (s24 - s16) * (size - 16) / 8 }
        if size <= 32 { return s24 + (s32 - s24) * (size - 24) / 8 }
        return s32 * size / 32
    }
}

private struct SymbioticThemeKey: EnvironmentKey {
    static let defaultValue: Theme? = nil
}

extension EnvironmentValues {
    /// The current theme. Unless set, classic-light in light mode and studio-dark in dark mode.
    public var symbioticTheme: Theme {
        get { self[SymbioticThemeKey.self] ?? Theme.standard(for: colorScheme) }
        set { self[SymbioticThemeKey.self] = newValue }
    }
}
```

Run:

```bash
export DEVELOPER_DIR=/Library/Developer/CommandLineTools PYTHONDONTWRITEBYTECODE=1
chmod +x scripts/swift.sh
```

- [ ] **Step 6: Generate**

Run:

```bash
export DEVELOPER_DIR=/Library/Developer/CommandLineTools PYTHONDONTWRITEBYTECODE=1
python3 tools/generate.py
```

Expected: nine `warning:` lines (starter palettes below WCAG AA, e.g. `warning: classic-light: text.secondary on surface.window is 3.87:1, body needs 4.5:1`), then `wrote 3 files`. The two Swift files exist under `Sources/SymbioticTokens/Generated/` and `tokens/contrast.md` has one table per theme.

- [ ] **Step 7: Run all tests to verify they pass**

Run:

```bash
export DEVELOPER_DIR=/Library/Developer/CommandLineTools PYTHONDONTWRITEBYTECODE=1
python3 -m unittest discover -s tools/tests 2>&1 | tail -3
scripts/swift.sh build 2>&1 | grep -v deprecated | tail -1
scripts/swift.sh test 2>&1 | grep -E '✘|Test run with'
```

Expected: Python `Ran 80 tests` … `OK`; `Build complete!`; `✔ Test run with 8 tests in 1 suite passed`. No `✘` lines.

- [ ] **Step 8: Commit**

Run:

```bash
export DEVELOPER_DIR=/Library/Developer/CommandLineTools PYTHONDONTWRITEBYTECODE=1
git add .gitignore \
  Package.swift \
  scripts/swift.sh \
  tools/swiftgen_common.py \
  tools/swiftgen_tokens.py \
  tools/generate.py \
  tools/tests/test_swiftgen_tokens.py \
  tools/tests/test_generate.py \
  tokens/contrast.md \
  Sources/SymbioticTokens \
  Tests/SymbioticTokensTests
git status --short
git commit -q -F - <<'MSG'
SymbioticTokens: generated Theme, contrast report and swift.sh

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01F7df6grqTdqHgc2d2X359P
MSG
git status --short
```

Expected: `git status --short` before the commit lists only the paths above (no `.DS_Store`, no `__pycache__`); after the commit it prints nothing.

### Task 4: Role catalogue and coverage report

`icons/roles.json` lists every role VizDAW (current SF Symbol uses, SP5 recording/monitoring/takes/media, the editors) and EG13 (`HANDOFF.md` requests) need, maps the 12 owner-confirmed glyphs, and the generator writes `icons/coverage.md`. At this point 49 roles name standard icons that do not exist yet; the report lists them and Task 5 draws them.

Where the roles come from: VizDAW today uses `xmark` (edit.close), `plus` (edit.add), `plus/minus.magnifyingglass` (view.zoom-in/out), `exclamationmark.triangle` (status.warning), `exclamationmark.circle` (status.problem), `circle.fill` fault indicator (status.fault), `speaker.slash` rate-mismatch banner (status.audio-muted), `externaldrive.badge.exclamationmark` (status.disk-slow), `minus.circle` (edit.remove-item), and the two diagonal-arrow row-height buttons (view.taller-rows, view.shorter-rows). SP5 adds record arm, input monitoring, punch, count-in, pre-roll, takes, media pool, offline media and relink, normalize and fades, bounce, MIDI input effects; the editors add arrangement, piano roll, list, strip chart, drum grid, notation views, envelope, and the arrow/pencil/eraser/scissors tools and snap. EG13 asks for parts A/B, layer/split/multi, poly/mono/legato, mono/stereo, the five slot categories, tempo sync, MIDI learn, random, add/remove route, via, bypass/power, the preset actions, settings and about.

**Files:**
- Create: `icons/roles.json`, `tools/rolelib.py`
- Modify: `tools/generate.py` (full replacement below), `tools/tests/test_generate.py` (append a class)
- Generated (by Step 5): `icons/coverage.md`
- Test: `tools/tests/test_rolelib.py`

**Interfaces:**
- Consumes: `swiftgen_common.lower_camel` (Task 3); `generate.py`'s `write_tree`, `tokens_step`; `test_generate.Scratch`.
- Produces (module `rolelib`): `class RoleError(ValueError)` with `.problems`; `load_json(path)`; `validate(data: dict, glyphs: list[dict]) -> list[dict]` (the roles; raises `RoleError`); `missing_standard(roles, standard_names) -> list[(role_id, standard_name)]`; `coverage_markdown(roles, standard_names, glyphs) -> str` with the three sections "Brief for the designer: roles with no brand glyph", "To draw in-house: standard icons that do not exist yet", "Glyphs not assigned to any role"; constants `LOGO = "brand.logo"`, `CONFIRMED = "confirmed by owner"`. `generate.py` gains `coverage_step() -> (files, missing)`.

- [ ] **Step 1: Write the failing tests**

File: `tools/tests/test_rolelib.py`

```python
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import rolelib as r  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[2]
GLYPHS = [
    {"id": "glyph-05", "suggestedRole": "envelope", "confidence": "confirmed by owner"},
    {"id": "glyph-06", "suggestedRole": "antenna", "confidence": "medium"},
    {"id": "glyph-39", "suggestedRole": "brand logo", "confidence": "confirmed by owner"},
]


def catalogue(*extra):
    return {"roles": [
        {"id": "transport.play", "standard": "play", "label": "Play"},
        {"id": "editor.envelope", "standard": "envelope", "brand": "glyph-05", "label": "Envelope"},
        {"id": "brand.logo", "brand": "glyph-39", "label": "SymbioticAudio"},
        *extra,
    ]}


class Validation(unittest.TestCase):
    def problems(self, data):
        with self.assertRaises(r.RoleError) as ctx:
            r.validate(data, GLYPHS)
        return ctx.exception.problems

    def test_valid_catalogue(self):
        self.assertEqual(len(r.validate(catalogue(), GLYPHS)), 3)

    def test_standard_is_required(self):
        p = self.problems(catalogue({"id": "edit.undo", "label": "Undo"}))
        self.assertIn("edit.undo: needs a standard icon", p)

    def test_logo_must_not_have_a_standard_icon(self):
        data = catalogue()
        data["roles"][2]["standard"] = "play"
        self.assertTrue(any("wordmark" in p for p in self.problems(data)))

    def test_logo_is_required(self):
        data = catalogue()
        del data["roles"][2]
        self.assertIn("brand.logo is missing", self.problems(data))

    def test_unconfirmed_glyph_cannot_be_mapped(self):
        p = self.problems(catalogue({"id": "net.wireless", "standard": "play", "brand": "glyph-06", "label": "W"}))
        self.assertIn("net.wireless: brand glyph glyph-06 is not confirmed by the owner", p)

    def test_unknown_glyph(self):
        p = self.problems(catalogue({"id": "x.y", "standard": "play", "brand": "glyph-99", "label": "X"}))
        self.assertIn("x.y: brand glyph 'glyph-99' does not exist", p)

    def test_duplicate_and_bad_ids(self):
        p = self.problems(catalogue({"id": "transport.play", "standard": "play", "label": "Play"},
                                    {"id": "Transport", "standard": "play", "label": "T"}))
        self.assertIn("transport.play: listed twice", p)
        self.assertTrue(any("dotted lower-case" in x for x in p))

    def test_swift_name_clash(self):
        p = self.problems(catalogue({"id": "transport.pla-y", "standard": "play", "label": "A"},
                                    {"id": "transport.pla.y", "standard": "play", "label": "B"}))
        self.assertTrue(any("clashes" in x for x in p))

    def test_label_and_unknown_keys(self):
        p = self.problems(catalogue({"id": "a.b", "standard": "play", "label": " ", "colour": "red"}))
        self.assertIn("a.b: needs a label", p)
        self.assertIn("a.b: unknown key 'colour'", p)


class Coverage(unittest.TestCase):
    def test_sections(self):
        roles = r.validate(catalogue({"id": "notation.fermata", "standard": "fermata", "label": "Fermata"}), GLYPHS)
        md = r.coverage_markdown(roles, ["play", "envelope"], GLYPHS)
        brief = md.split("## To draw")[0]
        self.assertIn("| `transport.play` | Play | `play` |", brief)
        self.assertNotIn("editor.envelope", brief)
        self.assertNotIn("brand.logo", brief)
        self.assertIn("| `notation.fermata` | `fermata` |", md)
        unassigned = md.split("## Glyphs not assigned")[1]
        self.assertIn("`glyph-06`", unassigned)
        self.assertNotIn("`glyph-05`", unassigned)

    def test_nothing_missing(self):
        roles = r.validate(catalogue(), GLYPHS)
        self.assertEqual(r.missing_standard(roles, ["play", "envelope"]), [])
        self.assertIn("None: every role's standard icon exists", r.coverage_markdown(roles, ["play", "envelope"], GLYPHS))


class RepositoryRoles(unittest.TestCase):
    def setUp(self):
        self.glyphs = r.load_json(ROOT / "icons" / "glyphs.json")
        self.roles = r.validate(r.load_json(ROOT / "icons" / "roles.json"), self.glyphs)
        self.by_id = {x["id"]: x for x in self.roles}

    def test_every_confirmed_glyph_is_mapped(self):
        confirmed = {g["id"] for g in self.glyphs if g["confidence"] == "confirmed by owner"}
        self.assertEqual(len(confirmed), 12)
        self.assertEqual({x["brand"] for x in self.roles if "brand" in x}, confirmed)

    def test_owner_assignments(self):
        expect = {"editor.envelope": "glyph-05", "editor.notation-alternate": "glyph-12", "editor.notation": "glyph-13",
                  "notation.fermata": "glyph-15", "monitor.phones-left": "glyph-23", "monitor.phones-right": "glyph-24",
                  "routing.send": "glyph-29", "notation.repeat": "glyph-34", "notation.natural": "glyph-35",
                  "editor.piano-roll": "glyph-38", "brand.logo": "glyph-39", "mode.loop": "glyph-40"}
        self.assertEqual({k: self.by_id[k]["brand"] for k in expect}, expect)

    def test_vizdaw_and_eg13_needs_are_covered(self):
        for rid in ["transport.play", "transport.record", "edit.add", "edit.close", "view.zoom-in", "view.zoom-out",
                    "status.warning", "status.problem", "status.fault", "status.audio-muted", "status.disk-slow",
                    "media.offline", "edit.remove-item", "view.taller-rows", "view.shorter-rows",
                    "record.arm", "monitor.input", "transport.punch-in", "transport.punch-out", "record.takes",
                    "media.pool", "audio.normalize", "audio.fade-in", "audio.fade-out",
                    "part.a", "part.b", "part.layer", "part.split", "part.multi", "voice.poly", "voice.mono",
                    "voice.legato", "audio.mono", "audio.stereo", "slot.source", "slot.filter", "slot.shaper",
                    "slot.fx", "slot.modulation", "control.tempo-sync", "control.midi-learn", "edit.random",
                    "routing.add-route", "routing.remove-route", "routing.via", "mixer.bypass", "mixer.power",
                    "preset.save", "preset.browse", "preset.previous", "preset.next", "preset.init",
                    "app.settings", "app.about"]:
            self.assertIn(rid, self.by_id)


if __name__ == "__main__":
    unittest.main()
```

Append to `tools/tests/test_generate.py`:

```python


class Roles(Scratch):
    def test_coverage_report_is_written(self):
        (self.root / "icons" / "coverage.md").unlink()
        result = self.run_generate()
        self.assertEqual(result.returncode, 0, result.stderr)
        text = (self.root / "icons" / "coverage.md").read_text(encoding="utf-8")
        self.assertIn("## Brief for the designer", text)
        self.assertIn("## Glyphs not assigned to any role", text)

    def test_unconfirmed_glyph_is_rejected(self):
        def map_guess(d):
            d["roles"].append({"id": "net.wireless", "standard": "play", "brand": "glyph-06", "label": "Wireless"})
        self.edit_json("icons/roles.json", map_guess)
        result = self.run_generate()
        self.assertEqual(result.returncode, 1)
        self.assertIn("glyph-06 is not confirmed by the owner", result.stderr)
```

- [ ] **Step 2: Run them to verify they fail**

Run:

```bash
export DEVELOPER_DIR=/Library/Developer/CommandLineTools PYTHONDONTWRITEBYTECODE=1
python3 -m unittest discover -s tools/tests 2>&1 | tail -3
```

Expected: `FAILED (errors=3)`: `No module named 'rolelib'`, and both new `Roles` generator tests error because `icons/coverage.md` and `icons/roles.json` do not exist yet.

- [ ] **Step 3: Write the role catalogue**

File: `icons/roles.json`

```json
{
  "description": "Icon roles used by VizDAW and EG13 (MIT). Apps draw icons by role. 'standard' names an icon in icons/standard/ (required except brand.logo); 'brand' names an owner-confirmed glyph in icons/svg/; 'label' is the default accessibility label.",
  "roles": [
    {"id": "transport.play", "standard": "play", "label": "Play"},
    {"id": "transport.pause", "standard": "pause", "label": "Pause"},
    {"id": "transport.stop", "standard": "stop", "label": "Stop"},
    {"id": "transport.record", "standard": "record", "label": "Record"},
    {"id": "transport.return-to-zero", "standard": "return-to-zero", "label": "Return to zero"},
    {"id": "transport.go-to-end", "standard": "go-to-end", "label": "Go to end"},
    {"id": "transport.rewind", "standard": "rewind", "label": "Rewind"},
    {"id": "transport.fast-forward", "standard": "fast-forward", "label": "Fast forward"},
    {"id": "transport.previous-marker", "standard": "previous", "label": "Previous marker"},
    {"id": "transport.next-marker", "standard": "next", "label": "Next marker"},
    {"id": "transport.punch-in", "standard": "punch-in", "label": "Punch in"},
    {"id": "transport.punch-out", "standard": "punch-out", "label": "Punch out"},
    {"id": "transport.metronome", "standard": "metronome", "label": "Metronome"},
    {"id": "transport.count-in", "standard": "count-in", "label": "Count in"},
    {"id": "transport.pre-roll", "standard": "pre-roll", "label": "Pre-roll"},
    {"id": "mode.loop", "standard": "loop", "brand": "glyph-40", "label": "Loop"},
    {"id": "mode.snap", "standard": "snap", "label": "Snap to grid"},
    {"id": "record.arm", "standard": "record-outline", "label": "Record arm"},
    {"id": "record.takes", "standard": "takes", "label": "Takes"},
    {"id": "record.keep-take", "standard": "check", "label": "Keep take"},
    {"id": "record.discard-take", "standard": "delete", "label": "Discard take"},
    {"id": "monitor.input", "standard": "monitor", "label": "Input monitoring"},
    {"id": "monitor.headphones", "standard": "headphones", "label": "Headphones"},
    {"id": "monitor.phones-left", "standard": "headphones-left", "brand": "glyph-23", "label": "Headphones left"},
    {"id": "monitor.phones-right", "standard": "headphones-right", "brand": "glyph-24", "label": "Headphones right"},
    {"id": "input.audio", "standard": "microphone", "label": "Audio input"},
    {"id": "editor.arrangement", "standard": "arrangement", "label": "Arrangement"},
    {"id": "editor.piano-roll", "standard": "piano-roll", "brand": "glyph-38", "label": "Piano roll"},
    {"id": "editor.list", "standard": "list", "label": "List editor"},
    {"id": "editor.strip-chart", "standard": "strip-chart", "label": "Strip chart"},
    {"id": "editor.drum-grid", "standard": "drum-grid", "label": "Drum grid"},
    {"id": "editor.notation", "standard": "treble-clef", "brand": "glyph-13", "label": "Notation"},
    {"id": "editor.notation-alternate", "standard": "bass-clef", "brand": "glyph-12", "label": "Alternate notation view"},
    {"id": "editor.envelope", "standard": "envelope", "brand": "glyph-05", "label": "Envelope"},
    {"id": "tool.arrow", "standard": "pointer", "label": "Arrow tool"},
    {"id": "tool.pencil", "standard": "pencil", "label": "Pencil tool"},
    {"id": "tool.eraser", "standard": "eraser", "label": "Eraser tool"},
    {"id": "tool.scissors", "standard": "cut", "label": "Scissors tool"},
    {"id": "notation.fermata", "standard": "fermata", "brand": "glyph-15", "label": "Fermata"},
    {"id": "notation.natural", "standard": "natural", "brand": "glyph-35", "label": "Natural"},
    {"id": "notation.repeat", "standard": "repeat-sign", "brand": "glyph-34", "label": "Repeat"},
    {"id": "edit.undo", "standard": "undo", "label": "Undo"},
    {"id": "edit.redo", "standard": "redo", "label": "Redo"},
    {"id": "edit.cut", "standard": "cut", "label": "Cut"},
    {"id": "edit.copy", "standard": "copy", "label": "Copy"},
    {"id": "edit.paste", "standard": "paste", "label": "Paste"},
    {"id": "edit.delete", "standard": "delete", "label": "Delete"},
    {"id": "edit.add", "standard": "add", "label": "Add"},
    {"id": "edit.remove", "standard": "remove", "label": "Remove"},
    {"id": "edit.remove-item", "standard": "remove-circle", "label": "Remove item"},
    {"id": "edit.close", "standard": "close", "label": "Close"},
    {"id": "edit.confirm", "standard": "check", "label": "Confirm"},
    {"id": "edit.random", "standard": "random", "label": "Randomise"},
    {"id": "view.zoom-in", "standard": "zoom-in", "label": "Zoom in"},
    {"id": "view.zoom-out", "standard": "zoom-out", "label": "Zoom out"},
    {"id": "view.search", "standard": "search", "label": "Search"},
    {"id": "view.taller-rows", "standard": "expand", "label": "Taller rows"},
    {"id": "view.shorter-rows", "standard": "collapse", "label": "Shorter rows"},
    {"id": "view.visible", "standard": "visible", "label": "Show"},
    {"id": "view.hidden", "standard": "hidden", "label": "Hide"},
    {"id": "view.menu", "standard": "menu", "label": "Menu"},
    {"id": "view.more", "standard": "more", "label": "More"},
    {"id": "nav.up", "standard": "chevron-up", "label": "Up"},
    {"id": "nav.down", "standard": "chevron-down", "label": "Down"},
    {"id": "nav.back", "standard": "chevron-left", "label": "Back"},
    {"id": "nav.forward", "standard": "chevron-right", "label": "Forward"},
    {"id": "status.warning", "standard": "warning", "label": "Warning"},
    {"id": "status.problem", "standard": "alert-circle", "label": "Problem"},
    {"id": "status.fault", "standard": "status-dot", "label": "Faults"},
    {"id": "status.audio-muted", "standard": "speaker-off", "label": "Audio muted"},
    {"id": "status.disk-slow", "standard": "drive-warning", "label": "Disk too slow"},
    {"id": "media.offline", "standard": "file-missing", "label": "Media offline"},
    {"id": "media.relink", "standard": "link", "label": "Relink"},
    {"id": "media.pool", "standard": "media-pool", "label": "Media pool"},
    {"id": "audio.normalize", "standard": "normalize", "label": "Normalize"},
    {"id": "audio.fade-in", "standard": "fade-in", "label": "Fade in"},
    {"id": "audio.fade-out", "standard": "fade-out", "label": "Fade out"},
    {"id": "audio.mono", "standard": "mono", "label": "Mono"},
    {"id": "audio.stereo", "standard": "stereo", "label": "Stereo"},
    {"id": "file.open", "standard": "folder-open", "label": "Open"},
    {"id": "file.save", "standard": "save", "label": "Save"},
    {"id": "file.import", "standard": "import", "label": "Import"},
    {"id": "file.export", "standard": "export", "label": "Export"},
    {"id": "file.bounce", "standard": "export", "label": "Bounce"},
    {"id": "mixer.solo", "standard": "solo", "label": "Solo"},
    {"id": "mixer.mute", "standard": "mute", "label": "Mute"},
    {"id": "mixer.bypass", "standard": "bypass", "label": "Bypass"},
    {"id": "mixer.power", "standard": "power", "label": "Power"},
    {"id": "routing.send", "standard": "send", "brand": "glyph-29", "label": "Send"},
    {"id": "routing.add-route", "standard": "add", "label": "Add route"},
    {"id": "routing.remove-route", "standard": "remove", "label": "Remove route"},
    {"id": "routing.via", "standard": "link", "label": "Via"},
    {"id": "lane.input-fx", "standard": "effects", "label": "MIDI input effects"},
    {"id": "voice.poly", "standard": "voice-poly", "label": "Poly"},
    {"id": "voice.mono", "standard": "voice-mono", "label": "Mono"},
    {"id": "voice.legato", "standard": "voice-legato", "label": "Legato"},
    {"id": "slot.source", "standard": "oscillator", "label": "Source"},
    {"id": "slot.filter", "standard": "filter", "label": "Filter"},
    {"id": "slot.shaper", "standard": "shaper", "label": "Shaper"},
    {"id": "slot.fx", "standard": "effects", "label": "Effects"},
    {"id": "slot.modulation", "standard": "modulation", "label": "Modulation"},
    {"id": "control.tempo-sync", "standard": "tempo-sync", "label": "Tempo sync"},
    {"id": "control.midi-learn", "standard": "midi-learn", "label": "MIDI learn"},
    {"id": "control.lock", "standard": "lock", "label": "Lock"},
    {"id": "control.unlock", "standard": "unlock", "label": "Unlock"},
    {"id": "control.link", "standard": "link", "label": "Link"},
    {"id": "control.unlink", "standard": "unlink", "label": "Unlink"},
    {"id": "preset.save", "standard": "save", "label": "Save preset"},
    {"id": "preset.browse", "standard": "folder-open", "label": "Browse presets"},
    {"id": "preset.previous", "standard": "chevron-left", "label": "Previous preset"},
    {"id": "preset.next", "standard": "chevron-right", "label": "Next preset"},
    {"id": "preset.init", "standard": "reset", "label": "Initialise preset"},
    {"id": "part.a", "standard": "part-a", "label": "Part A"},
    {"id": "part.b", "standard": "part-b", "label": "Part B"},
    {"id": "part.layer", "standard": "layer", "label": "Layer"},
    {"id": "part.split", "standard": "split", "label": "Split"},
    {"id": "part.multi", "standard": "multi", "label": "Multi"},
    {"id": "app.settings", "standard": "settings", "label": "Settings"},
    {"id": "app.about", "standard": "info", "label": "About"},
    {"id": "brand.logo", "brand": "glyph-39", "label": "SymbioticAudio"}
  ]
}
```

- [ ] **Step 4: Write the role library and wire it into the generator**

File: `tools/rolelib.py`

```python
"""Icon role catalogue: validation and the coverage report (spec sections 3.2 and 3.3)."""
import json
import re

from swiftgen_common import lower_camel

ROLE_ID = re.compile(r"^[a-z][a-z0-9-]*(\.[a-z0-9]+(-[a-z0-9]+)*)+$")
LOGO = "brand.logo"
CONFIRMED = "confirmed by owner"


class RoleError(ValueError):
    """roles.json is malformed; .problems lists every issue."""

    def __init__(self, problems):
        super().__init__("\n".join(problems))
        self.problems = problems


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def validate(data, glyphs):
    """Check roles.json against glyphs.json. Returns the role list."""
    problems = []
    if not isinstance(data, dict) or not isinstance(data.get("roles"), list):
        raise RoleError(["roles.json must be an object with a 'roles' list"])
    for key in sorted(set(data) - {"description", "roles"}):
        problems.append(f"unknown top-level key {key!r}")
    confidence = {g["id"]: g.get("confidence", "") for g in glyphs}
    seen = {}
    swift_names = {}
    for i, role in enumerate(data["roles"]):
        rid = role.get("id") if isinstance(role, dict) else None
        where = rid or f"roles[{i}]"
        if not isinstance(role, dict):
            problems.append(f"{where}: must be an object")
            continue
        for key in sorted(set(role) - {"id", "standard", "brand", "label"}):
            problems.append(f"{where}: unknown key {key!r}")
        if not isinstance(rid, str) or not ROLE_ID.match(rid):
            problems.append(f"{where}: id must be dotted lower-case words, e.g. transport.play")
            continue
        if rid in seen:
            problems.append(f"{rid}: listed twice")
        seen[rid] = role
        swift = lower_camel(rid)
        if swift in swift_names and swift_names[swift] != rid:
            problems.append(f"{rid}: Swift name {swift} clashes with {swift_names[swift]}")
        swift_names[swift] = rid
        if not isinstance(role.get("label"), str) or not role["label"].strip():
            problems.append(f"{rid}: needs a label")
        if rid == LOGO:
            if "standard" in role:
                problems.append(f"{LOGO}: must not name a standard icon (it falls back to the wordmark)")
        elif not isinstance(role.get("standard"), str) or not role["standard"]:
            problems.append(f"{rid}: needs a standard icon")
        if "brand" in role:
            brand = role["brand"]
            if brand not in confidence:
                problems.append(f"{rid}: brand glyph {brand!r} does not exist")
            elif confidence[brand] != CONFIRMED:
                problems.append(f"{rid}: brand glyph {brand} is not confirmed by the owner")
    if LOGO not in seen:
        problems.append(f"{LOGO} is missing")
    if problems:
        raise RoleError(problems)
    return data["roles"]


def missing_standard(roles, standard_names):
    """[(role id, standard name)] for roles whose standard icon has no SVG yet."""
    have = set(standard_names)
    return [(r["id"], r["standard"]) for r in roles if "standard" in r and r["standard"] not in have]


def coverage_markdown(roles, standard_names, glyphs):
    lines = ["# Icon coverage", "",
             "Generated by `tools/generate.py` from `icons/roles.json`; do not edit.",
             f"{len(roles)} roles, {sum(1 for r in roles if 'brand' in r)} with a brand glyph.", ""]
    lines += ["## Brief for the designer: roles with no brand glyph", "",
              "Each of these draws its standard icon until a brand glyph is assigned.", "",
              "| Role | Label | Standard icon now |", "|---|---|---|"]
    for r in roles:
        if "brand" not in r:
            lines.append(f"| `{r['id']}` | {r['label']} | `{r['standard']}` |")
    missing = missing_standard(roles, standard_names)
    lines += ["", "## To draw in-house: standard icons that do not exist yet", ""]
    if missing:
        lines += ["| Role | Standard icon to draw |", "|---|---|"]
        lines += [f"| `{rid}` | `{name}` |" for rid, name in missing]
    else:
        lines.append("None: every role's standard icon exists in `icons/standard/`.")
    used = {r["brand"] for r in roles if "brand" in r}
    lines += ["", "## Glyphs not assigned to any role", "",
              "Suggested roles are guesses from the shapes; the owner assigns them.", "",
              "| Glyph | Suggested role | Confidence |", "|---|---|---|"]
    for g in glyphs:
        if g["id"] not in used:
            lines.append(f"| `{g['id']}` | {g.get('suggestedRole', '')} | {g.get('confidence', '')} |")
    return "\n".join(lines) + "\n"
```

File: `tools/generate.py`

```python
#!/usr/bin/env python3
"""Validate the design sources and write every generated file.

Usage: python3 tools/generate.py
Writes tokens/contrast.md, icons/coverage.md and Sources/SymbioticTokens/Generated/.
Exit status 1 (and nothing written) if a source is invalid.
"""
import pathlib
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import rolelib  # noqa: E402
import swiftgen_tokens  # noqa: E402
import tokenlib  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]


def write_tree(files, owned_dirs):
    """Write {relative path: text}; delete stale files in the generated dirs."""
    for d in owned_dirs:
        folder = ROOT / d
        if folder.is_dir():
            for old in folder.glob("*.swift"):
                if str(old.relative_to(ROOT)) not in files:
                    old.unlink()
    for rel, text in sorted(files.items()):
        path = ROOT / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def tokens_step():
    data = tokenlib.load(ROOT / "tokens" / "tokens.json")
    rows = tokenlib.contrast_rows(data)
    for tid, text, on, use, ratio, need, ok in rows:
        if not ok:
            print(f"warning: {tid}: {text} on {on} is {tokenlib.format_ratio(ratio)}, {use} needs {need:g}:1")
    files = swiftgen_tokens.generate(data)
    files["tokens/contrast.md"] = tokenlib.contrast_markdown(rows)
    return files, [swiftgen_tokens.OUT]


def coverage_step():
    """Returns (files, missing standard icons). Missing icons are listed, not fatal yet."""
    glyphs = rolelib.load_json(ROOT / "icons" / "glyphs.json")
    roles = rolelib.validate(rolelib.load_json(ROOT / "icons" / "roles.json"), glyphs)
    standard_names = [e["id"] for e in rolelib.load_json(ROOT / "icons" / "standard.json")]
    files = {"icons/coverage.md": rolelib.coverage_markdown(roles, standard_names, glyphs)}
    return files, rolelib.missing_standard(roles, standard_names)


def main():
    try:
        token_files, token_dirs = tokens_step()
        icon_files, missing = coverage_step()
    except tokenlib.TokenError as e:
        for p in e.problems:
            print(f"error: tokens.json: {p}", file=sys.stderr)
        return 1
    except rolelib.RoleError as e:
        for p in e.problems:
            print(f"error: roles.json: {p}", file=sys.stderr)
        return 1
    for rid, name in missing:
        print(f"note: role {rid} needs icons/standard/{name}.svg (listed in icons/coverage.md)")
    files = {**token_files, **icon_files}
    write_tree(files, token_dirs)
    print(f"wrote {len(files)} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 5: Generate**

Run:

```bash
export DEVELOPER_DIR=/Library/Developer/CommandLineTools PYTHONDONTWRITEBYTECODE=1
python3 tools/generate.py | tail -3
```

Expected: 49 `note: role … needs icons/standard/<name>.svg` lines (e.g. `note: role transport.pre-roll needs icons/standard/pre-roll.svg`), then `wrote 4 files`. `icons/coverage.md` lists the 108 roles without a brand glyph, the 49 icons to draw and the 29 unassigned glyphs.

- [ ] **Step 6: Run the tests to verify they pass**

Run:

```bash
export DEVELOPER_DIR=/Library/Developer/CommandLineTools PYTHONDONTWRITEBYTECODE=1
python3 -m unittest discover -s tools/tests 2>&1 | tail -3
```

Expected: `Ran 96 tests`, `OK`.

- [ ] **Step 7: Commit**

Run:

```bash
export DEVELOPER_DIR=/Library/Developer/CommandLineTools PYTHONDONTWRITEBYTECODE=1
git add icons/roles.json \
  icons/coverage.md \
  tools/rolelib.py \
  tools/generate.py \
  tools/tests/test_rolelib.py \
  tools/tests/test_generate.py
git status --short
git commit -q -F - <<'MSG'
Icon roles for VizDAW and EG13, owner-confirmed glyphs and coverage report

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01F7df6grqTdqHgc2d2X359P
MSG
git status --short
```

Expected: `git status --short` before the commit lists only the paths above (no `.DS_Store`, no `__pycache__`); after the commit it prints nothing.

### Task 5: The 49 missing standard icons

Every role must have a standard icon (spec §3.2). Draw the 49 icons that `icons/coverage.md` lists, in the house style of `icons/standard/README.md`: 24-unit grid, the exact root element, 1.2 stroke on the root only, butt caps, miter joins, solid marks only where the convention needs them, ink (with half the stroke) inside 1.5–22.5, ink bounding box centred on (12, 12), coordinates rounded to 0.01. Every shape is drawn fresh from the convention; none is derived from another icon library or from the branded glyphs. A new house-style test checks all 106 icons.

**Files:**
- Create: `icons/standard/<name>.svg` for the 49 names in the script below
- Modify: `icons/standard.json` (append 49 entries), `icons/standard/README.md` (count and categories), `tools/contact_sheet.py` (location-independent), `icons/contact-sheet.html` (rebuilt), `icons/coverage.md` (regenerated)
- Test: `tools/tests/test_standard_icons.py`

**Interfaces:**
- Consumes: `svgsubset.parse_svg_text`, `svgsubset.bounds` (Task 1); `icons/roles.json` (Task 4).
- Produces: icon names later tasks rely on (as `StandardIcon` cases): `pre-roll`, `snap`, `takes`, `headphones-left`, `headphones-right`, `arrangement`, `piano-roll`, `list`, `strip-chart`, `drum-grid`, `treble-clef`, `bass-clef`, `envelope`, `pointer`, `pencil`, `eraser`, `fermata`, `natural`, `repeat-sign`, `remove-circle`, `expand`, `collapse`, `alert-circle`, `status-dot`, `speaker-off`, `drive-warning`, `file-missing`, `media-pool`, `normalize`, `fade-in`, `fade-out`, `mono`, `stereo`, `power`, `send`, `effects`, `voice-poly`, `voice-mono`, `voice-legato`, `oscillator`, `filter`, `shaper`, `modulation`, `reset`, `part-a`, `part-b`, `layer`, `split`, `multi`.

- [ ] **Step 1: Write the failing house-style test**

File: `tools/tests/test_standard_icons.py`

```python
"""House-style checks for icons/standard/ (icons/standard/README.md)."""
import json
import pathlib
import re
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import svgsubset as s  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[2]
STANDARD = ROOT / "icons" / "standard"
ROOT_ELEMENT = ('<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" '
                'fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="butt" stroke-linejoin="miter">')


def index():
    with open(ROOT / "icons" / "standard.json", encoding="utf-8") as f:
        return json.load(f)


class StandardIcons(unittest.TestCase):
    def test_index_matches_files(self):
        names = [e["id"] for e in index()]
        self.assertEqual(len(names), len(set(names)))
        self.assertEqual(sorted(names), sorted(p.stem for p in STANDARD.glob("*.svg")))
        for e in index():
            self.assertEqual(set(e), {"id", "name", "category", "description"}, e["id"])

    def test_every_role_has_its_standard_icon(self):
        with open(ROOT / "icons" / "roles.json", encoding="utf-8") as f:
            roles = json.load(f)["roles"]
        have = {e["id"] for e in index()}
        missing = sorted({r["standard"] for r in roles if "standard" in r} - have)
        self.assertEqual(missing, [])

    def test_house_style(self):
        for path in sorted(STANDARD.glob("*.svg")):
            with self.subTest(path.stem):
                text = path.read_text(encoding="utf-8")
                self.assertEqual(text.split("\n")[0], ROOT_ELEMENT)
                body = text.split("\n", 1)[1]
                self.assertNotIn("stroke-width", body)
                for paint in re.findall(r'(?:fill|stroke)="([^"]*)"', body):
                    self.assertIn(paint, ("currentColor", "none"))
                for num in re.findall(r"-?\d+\.\d+", body):
                    self.assertLessEqual(len(num.split(".")[1]), 2, f"{num} not rounded to 0.01")
                x0, y0, x1, y1 = s.bounds(s.parse_svg_text(text, path.stem))
                self.assertGreaterEqual(min(x0, y0), 1.5 - 1e-6, "ink outside the live area")
                self.assertLessEqual(max(x1, y1), 22.5 + 1e-6, "ink outside the live area")
                self.assertLessEqual(abs((x0 + x1) / 2 - 12), 0.3, "not centred horizontally")
                self.assertLessEqual(abs((y0 + y1) / 2 - 12), 0.3, "not centred vertically")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run it to verify it fails**

Run:

```bash
export DEVELOPER_DIR=/Library/Developer/CommandLineTools PYTHONDONTWRITEBYTECODE=1
python3 -m unittest tools/tests/test_standard_icons.py 2>&1 | tail -3
```

Expected: `FAILED (failures=1)`: `test_every_role_has_its_standard_icon` lists the 49 missing names.

- [ ] **Step 3: Draw the icons and append them to the index**

Each entry is the icon's child elements; the script wraps them in the exact root element.

Run:

```bash
export DEVELOPER_DIR=/Library/Developer/CommandLineTools PYTHONDONTWRITEBYTECODE=1
python3 - <<'EOF'
import json
import pathlib

ROOT_ELEMENT = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="butt" stroke-linejoin="miter">'

# name: (category, display name, description, child elements)
ICONS = {
    "pre-roll": ("transport", "Pre-roll", "Three lead-in dashes into a play triangle", [
        '<line x1="4.6" y1="12" x2="6.2" y2="12"/>',
        '<line x1="7.4" y1="12" x2="9" y2="12"/>',
        '<line x1="10.2" y1="12" x2="11.8" y2="12"/>',
        '<polygon points="13.2 7.2 19.4 12 13.2 16.8"/>',
    ]),
    "snap": ("edit", "Snap", "Horseshoe magnet (snap to grid)", [
        '<path d="M6.4 5.7 V12.7 A5.6 5.6 0 0 0 17.6 12.7 V5.7"/>',
        '<path d="M9.6 5.7 V12.7 A2.4 2.4 0 0 0 14.4 12.7 V5.7"/>',
        '<line x1="6.4" y1="5.7" x2="9.6" y2="5.7"/>',
        '<line x1="14.4" y1="5.7" x2="17.6" y2="5.7"/>',
        '<line x1="6.4" y1="8.9" x2="9.6" y2="8.9"/>',
        '<line x1="14.4" y1="8.9" x2="17.6" y2="8.9"/>',
    ]),
    "takes": ("transport", "Takes", "Three staggered bars (take lanes)", [
        '<polygon points="4.6 5.8 14.6 5.8 14.6 8.6 4.6 8.6"/>',
        '<polygon points="7 10.6 17 10.6 17 13.4 7 13.4"/>',
        '<polygon points="9.4 15.4 19.4 15.4 19.4 18.2 9.4 18.2"/>',
    ]),
    "headphones-left": ("audio", "Headphones left", "Left ear cup with half the headband", [
        '<path d="M9.9 13 V11.4 A5.8 5.8 0 0 1 15.7 5.6"/>',
        '<polygon points="8.3 13 11.5 13 11.5 18.4 8.3 18.4"/>',
    ]),
    "headphones-right": ("audio", "Headphones right", "Right ear cup with half the headband", [
        '<path d="M14.1 13 V11.4 A5.8 5.8 0 0 0 8.3 5.6"/>',
        '<polygon points="12.5 13 15.7 13 15.7 18.4 12.5 18.4"/>',
    ]),
    "arrangement": ("editor", "Arrangement", "Blocks laid out on three lanes", [
        '<polygon points="4.6 5.4 11 5.4 11 8.6 4.6 8.6"/>',
        '<polygon points="13 5.4 19.4 5.4 19.4 8.6 13 8.6"/>',
        '<polygon points="7.4 10.4 16.6 10.4 16.6 13.6 7.4 13.6"/>',
        '<polygon points="4.6 15.4 9.8 15.4 9.8 18.6 4.6 18.6"/>',
        '<polygon points="12.2 15.4 17 15.4 17 18.6 12.2 18.6"/>',
    ]),
    "piano-roll": ("editor", "Piano roll", "Keyboard strip beside three note bars", [
        '<polygon points="4.6 4.6 8.6 4.6 8.6 19.4 4.6 19.4"/>',
        '<line x1="4.6" y1="8.3" x2="8.6" y2="8.3"/>',
        '<line x1="4.6" y1="12" x2="8.6" y2="12"/>',
        '<line x1="4.6" y1="15.7" x2="8.6" y2="15.7"/>',
        '<polygon points="10.6 6.2 15 6.2 15 8.4 10.6 8.4"/>',
        '<polygon points="13 10.9 19.4 10.9 19.4 13.1 13 13.1"/>',
        '<polygon points="11.4 15.6 16.6 15.6 16.6 17.8 11.4 17.8"/>',
    ]),
    "list": ("editor", "List", "Three bullet points with lines (event list)", [
        '<circle cx="5.6" cy="7" r="1.1" fill="currentColor" stroke="none"/>',
        '<circle cx="5.6" cy="12" r="1.1" fill="currentColor" stroke="none"/>',
        '<circle cx="5.6" cy="17" r="1.1" fill="currentColor" stroke="none"/>',
        '<line x1="8.8" y1="7" x2="18.9" y2="7"/>',
        '<line x1="8.8" y1="12" x2="18.9" y2="12"/>',
        '<line x1="8.8" y1="17" x2="18.9" y2="17"/>',
    ]),
    "strip-chart": ("editor", "Strip chart", "Controller bars of different heights on a baseline", [
        '<line x1="4.6" y1="18.3" x2="19.4" y2="18.3"/>',
        '<line x1="6.6" y1="18.3" x2="6.6" y2="10.7"/>',
        '<line x1="10.2" y1="18.3" x2="10.2" y2="5.7"/>',
        '<line x1="13.8" y1="18.3" x2="13.8" y2="8.7"/>',
        '<line x1="17.4" y1="18.3" x2="17.4" y2="13.1"/>',
    ]),
    "drum-grid": ("editor", "Drum grid", "Step grid of squares, some filled (hits)", [
        '<polygon points="4.1 4.1 8.7 4.1 8.7 8.7 4.1 8.7" fill="currentColor" stroke="none"/>',
        '<polygon points="10.3 4.7 13.7 4.7 13.7 8.1 10.3 8.1"/>',
        '<polygon points="15.3 4.1 19.9 4.1 19.9 8.7 15.3 8.7" fill="currentColor" stroke="none"/>',
        '<polygon points="4.7 10.3 8.1 10.3 8.1 13.7 4.7 13.7"/>',
        '<polygon points="9.7 9.7 14.3 9.7 14.3 14.3 9.7 14.3" fill="currentColor" stroke="none"/>',
        '<polygon points="15.9 10.3 19.3 10.3 19.3 13.7 15.9 13.7"/>',
        '<polygon points="4.1 15.3 8.7 15.3 8.7 19.9 4.1 19.9" fill="currentColor" stroke="none"/>',
        '<polygon points="9.7 15.3 14.3 15.3 14.3 19.9 9.7 19.9" fill="currentColor" stroke="none"/>',
        '<polygon points="15.9 15.9 19.3 15.9 19.3 19.3 15.9 19.3"/>',
    ]),
    "treble-clef": ("notation", "Treble clef", "G clef: stem with a top loop and a spiral round the G line", [
        '<path d="M11.2 19.2 C12.4 20 13.6 19 13.2 17.6 L11.6 6.4 C11.4 4.6 13.4 3.8 14 5.2 C14.8 7.2 12 9.4 10.2 11 C8.2 12.8 8.4 16.4 11.6 16.6 C14.6 16.8 15.6 13.6 14 12.4 C12.8 11.4 10.8 12 10.8 13.8"/>',
    ]),
    "bass-clef": ("notation", "Bass clef", "F clef: dotted hook curling down, with two dots", [
        '<circle cx="7.9" cy="9.4" r="1.3" fill="currentColor" stroke="none"/>',
        '<path d="M6.7 9.4 C6.7 6.8 8.5 5.6 10.5 5.6 C13.3 5.6 14.7 7.6 14.7 10 C14.7 14 11.1 17 6.7 18.6"/>',
        '<circle cx="17.1" cy="8" r="0.9" fill="currentColor" stroke="none"/>',
        '<circle cx="17.1" cy="12" r="0.9" fill="currentColor" stroke="none"/>',
    ]),
    "envelope": ("editor", "Envelope", "Attack, decay, sustain, release line", [
        '<polyline points="4.6 18 8 6 11.6 11.4 16 11.4 19.4 18"/>',
    ]),
    "pointer": ("edit", "Pointer", "Arrow pointer (select tool)", [
        '<polygon points="7.2 4.6 7.2 17.6 10.4 14.6 12.8 19.4 14.8 18.4 12.4 13.8 16.8 13.4"/>',
    ]),
    "pencil": ("edit", "Pencil", "Pencil on the diagonal (draw tool)", [
        '<g transform="translate(-0.71 0.71) rotate(45 12 12)"><polygon points="10 4.8 14 4.8 14 14.8 10 14.8"/><polyline points="10 14.8 12 19.2 14 14.8"/><line x1="10" y1="7.2" x2="14" y2="7.2"/></g>',
    ]),
    "eraser": ("edit", "Eraser", "Eraser block on the diagonal (erase tool)", [
        '<g transform="rotate(45 12 12)"><polygon points="9 6 15 6 15 18 9 18"/><line x1="9" y1="13.4" x2="15" y2="13.4"/></g>',
    ]),
    "fermata": ("notation", "Fermata", "Arc over a dot (hold)", [
        '<path d="M5.4 15.4 A6.6 6.6 0 0 1 18.6 15.4"/>',
        '<circle cx="12" cy="13.6" r="1.2" fill="currentColor" stroke="none"/>',
    ]),
    "natural": ("notation", "Natural", "Natural sign: two offset stems joined by two slanted bars", [
        '<line x1="9.6" y1="4.6" x2="9.6" y2="16.4"/>',
        '<line x1="14.4" y1="7.6" x2="14.4" y2="19.4"/>',
        '<line x1="9.6" y1="10" x2="14.4" y2="8.6"/>',
        '<line x1="9.6" y1="15.4" x2="14.4" y2="14"/>',
    ]),
    "repeat-sign": ("notation", "Repeat", "End-repeat barline: two dots, a thin and a thick bar", [
        '<circle cx="8.2" cy="9.6" r="1.2" fill="currentColor" stroke="none"/>',
        '<circle cx="8.2" cy="14.4" r="1.2" fill="currentColor" stroke="none"/>',
        '<line x1="11.4" y1="5" x2="11.4" y2="19"/>',
        '<polygon points="14.4 4.4 17 4.4 17 19.6 14.4 19.6" fill="currentColor" stroke="none"/>',
    ]),
    "remove-circle": ("edit", "Remove (circled)", "Minus sign in a circle", [
        '<circle cx="12" cy="12" r="7.8"/>',
        '<line x1="8" y1="12" x2="16" y2="12"/>',
    ]),
    "expand": ("app", "Expand", "Two arrows pointing out to opposite corners", [
        '<polyline points="5.6 10.4 5.6 5.6 10.4 5.6"/>',
        '<line x1="5.6" y1="5.6" x2="10.6" y2="10.6"/>',
        '<polyline points="13.6 18.4 18.4 18.4 18.4 13.6"/>',
        '<line x1="18.4" y1="18.4" x2="13.4" y2="13.4"/>',
    ]),
    "collapse": ("app", "Collapse", "Two arrows pointing in from opposite corners", [
        '<polyline points="6.4 10.6 10.6 10.6 10.6 6.4"/>',
        '<line x1="5" y1="5" x2="10.6" y2="10.6"/>',
        '<polyline points="17.6 13.4 13.4 13.4 13.4 17.6"/>',
        '<line x1="19" y1="19" x2="13.4" y2="13.4"/>',
    ]),
    "alert-circle": ("app", "Alert", "Exclamation mark in a circle", [
        '<circle cx="12" cy="12" r="7.8"/>',
        '<line x1="12" y1="7.6" x2="12" y2="13.4"/>',
        '<circle cx="12" cy="16.2" r="0.85" fill="currentColor" stroke="none"/>',
    ]),
    "status-dot": ("app", "Status dot", "Small solid dot (status indicator)", [
        '<circle cx="12" cy="12" r="4.5" fill="currentColor" stroke="none"/>',
    ]),
    "speaker-off": ("audio", "Speaker off", "Loudspeaker with a cross (audio muted)", [
        '<polygon points="4.6 9.6 7.8 9.6 12 5.6 12 18.4 7.8 14.4 4.6 14.4"/>',
        '<line x1="14.6" y1="9.6" x2="19.4" y2="14.4"/>',
        '<line x1="19.4" y1="9.6" x2="14.6" y2="14.4"/>',
    ]),
    "drive-warning": ("app", "Drive warning", "Exclamation mark over a disk drive (disk too slow)", [
        '<polygon points="4.6 12 19.4 12 19.4 19 4.6 19"/>',
        '<circle cx="16.6" cy="15.5" r="0.85" fill="currentColor" stroke="none"/>',
        '<line x1="12" y1="4.8" x2="12" y2="7.8"/>',
        '<circle cx="12" cy="9.9" r="0.85" fill="currentColor" stroke="none"/>',
    ]),
    "file-missing": ("app", "File missing", "Page with a folded corner, struck through (media offline)", [
        '<polygon points="6.4 4.6 13.6 4.6 17.6 8.6 17.6 19.4 6.4 19.4"/>',
        '<polyline points="13.6 4.6 13.6 8.6 17.6 8.6"/>',
        '<line x1="5" y1="19" x2="19" y2="5"/>',
    ]),
    "media-pool": ("app", "Media pool", "Box holding a waveform, a sheet behind it", [
        '<polygon points="4.6 7.8 19.4 7.8 19.4 18.6 4.6 18.6"/>',
        '<line x1="6.2" y1="5.4" x2="17.8" y2="5.4"/>',
        '<polyline points="7 13.2 8.6 13.2 9.8 10.4 11.2 16 12.6 11 13.8 14.8 15 12.2 16.2 13.2 17 13.2"/>',
    ]),
    "normalize": ("audio", "Normalize", "Waveform reaching a ceiling and a floor line", [
        '<line x1="4.6" y1="5.6" x2="19.4" y2="5.6"/>',
        '<line x1="4.6" y1="18.4" x2="19.4" y2="18.4"/>',
        '<polyline points="4.6 12 6.6 12 8 8.4 9.4 15.6 10.8 6.6 12.2 17.4 13.6 8.6 15 15.4 16.4 10 17.6 12 19.4 12"/>',
    ]),
    "fade-in": ("audio", "Fade in", "Area under a curve rising from left to right", [
        '<path d="M4.6 18.4 C11.2 17.8 15.4 11.6 19.4 5.6 V18.4 Z"/>',
    ]),
    "fade-out": ("audio", "Fade out", "Area under a curve falling from left to right", [
        '<path d="M19.4 18.4 C12.8 17.8 8.6 11.6 4.6 5.6 V18.4 Z"/>',
    ]),
    "mono": ("audio", "Mono", "One ring (one channel)", [
        '<circle cx="12" cy="12" r="4.8"/>',
    ]),
    "stereo": ("audio", "Stereo", "Two overlapping rings (two channels)", [
        '<circle cx="9.2" cy="12" r="4.8"/>',
        '<circle cx="14.8" cy="12" r="4.8"/>',
    ]),
    "power": ("audio", "Power", "Ring open at the top with a bar through the gap", [
        '<path d="M8.4 7.2 A6.8 6.8 0 1 0 15.6 7.2"/>',
        '<line x1="12" y1="4.2" x2="12" y2="11.4"/>',
    ]),
    "send": ("audio", "Send", "Knob ring with an arrow leaving it (send)", [
        '<circle cx="7.8" cy="12" r="3.2"/>',
        '<line x1="11" y1="12" x2="19.4" y2="12"/>',
        '<polyline points="16.6 9.2 19.4 12 16.6 14.8"/>',
    ]),
    "effects": ("audio", "Effects", "Four-pointed star (effects)", [
        '<polygon points="12 4.6 13.8 10.2 19.4 12 13.8 13.8 12 19.4 10.2 13.8 4.6 12 10.2 10.2"/>',
    ]),
    "voice-poly": ("audio", "Poly", "Three stacked note heads on one stem (polyphonic)", [
        '<circle cx="12" cy="8.2" r="2"/>',
        '<circle cx="12" cy="12.6" r="2"/>',
        '<circle cx="12" cy="17" r="2"/>',
        '<line x1="14" y1="17" x2="14" y2="5"/>',
    ]),
    "voice-mono": ("audio", "Mono voice", "One note head on a stem (monophonic)", [
        '<circle cx="12" cy="16.4" r="2.4"/>',
        '<line x1="14.4" y1="16.4" x2="14.4" y2="5.2"/>',
    ]),
    "voice-legato": ("audio", "Legato", "Two note heads joined by a slur", [
        '<circle cx="8" cy="14.5" r="2"/>',
        '<circle cx="16" cy="14.5" r="2"/>',
        '<path d="M5.6 10.7 C8.2 6.5 15.8 6.5 18.4 10.7"/>',
    ]),
    "oscillator": ("audio", "Oscillator", "One cycle of a sine wave (sound source)", [
        '<path d="M4.6 12 C6.4 6.4 9.6 6.4 12 12 C14.4 17.6 17.6 17.6 19.4 12"/>',
    ]),
    "filter": ("audio", "Filter", "Low-pass response: flat, then rolling off", [
        '<path d="M5 7.4 H12.4 C15 7.4 16.2 9 17.2 11.8 L19 16.6"/>',
    ]),
    "shaper": ("audio", "Shaper", "S-shaped transfer curve in a frame (waveshaper)", [
        '<polygon points="4.6 4.6 19.4 4.6 19.4 19.4 4.6 19.4"/>',
        '<path d="M4.6 19.4 C10.6 19.4 13.4 4.6 19.4 4.6"/>',
    ]),
    "modulation": ("audio", "Modulation", "One cycle of a triangle wave (LFO)", [
        '<polyline points="4.6 12 8.3 6.6 15.7 17.4 19.4 12"/>',
    ]),
    "reset": ("app", "Reset", "Anticlockwise arrow round a circle (initialise)", [
        '<path d="M9.4 4.86 A7.6 7.6 0 1 0 16.89 6.18"/>',
        '<polyline points="19.48 5.95 16.89 6.18 17.11 8.77"/>',
    ]),
    "part-a": ("audio", "Part A", "Letter A in a square frame", [
        '<polygon points="4.8 4.8 19.2 4.8 19.2 19.2 4.8 19.2"/>',
        '<polyline points="8.6 16.6 12 7.4 15.4 16.6"/>',
        '<line x1="9.78" y1="13.4" x2="14.22" y2="13.4"/>',
    ]),
    "part-b": ("audio", "Part B", "Letter B in a square frame", [
        '<polygon points="4.8 4.8 19.2 4.8 19.2 19.2 4.8 19.2"/>',
        '<path d="M9.2 7.6 V16.4 H12.8 C16.2 16.4 16.2 11.8 12.8 11.8 H9.2 M9.2 7.6 H12.4 C15.2 7.6 15.2 11.8 12.4 11.8"/>',
    ]),
    "layer": ("audio", "Layer", "Two stacked layers: a diamond over a chevron", [
        '<polygon points="12 6.1 19.4 10.1 12 14.1 4.6 10.1"/>',
        '<polyline points="4.6 13.9 12 17.9 19.4 13.9"/>',
    ]),
    "split": ("audio", "Split", "Two boxes side by side (keyboard split)", [
        '<polygon points="4.6 7.4 10.8 7.4 10.8 16.6 4.6 16.6"/>',
        '<polygon points="13.2 7.4 19.4 7.4 19.4 16.6 13.2 16.6"/>',
    ]),
    "multi": ("audio", "Multi", "Four boxes in a 2 by 2 grid (multitimbral)", [
        '<polygon points="4.6 4.6 10.8 4.6 10.8 10.8 4.6 10.8"/>',
        '<polygon points="13.2 4.6 19.4 4.6 19.4 10.8 13.2 10.8"/>',
        '<polygon points="4.6 13.2 10.8 13.2 10.8 19.4 4.6 19.4"/>',
        '<polygon points="13.2 13.2 19.4 13.2 19.4 19.4 13.2 19.4"/>',
    ]),
}

folder = pathlib.Path('icons/standard')
index_path = pathlib.Path('icons/standard.json')
index = json.loads(index_path.read_text(encoding='utf-8'))
have = {e['id'] for e in index}
for name, (category, title, description, body) in ICONS.items():
    assert name not in have, name
    text = ROOT_ELEMENT + '\n' + ''.join(f'  {element}\n' for element in body) + '</svg>\n'
    (folder / f'{name}.svg').write_text(text, encoding='utf-8')
    index.append({'id': name, 'name': title, 'category': category, 'description': description})
index_path.write_text(json.dumps(index, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
print(f'{len(ICONS)} icons written; standard.json now lists {len(index)}')
EOF
```

Expected: `49 icons written; standard.json now lists 106`. The existing 57 entries are unchanged (`git diff icons/standard.json` shows only additions).

- [ ] **Step 4: Make the contact sheet script location-independent and update the icon count**

`tools/contact_sheet.py` had the repository's absolute path baked in; `icons/standard/README.md` states the count.

Run:

```bash
export DEVELOPER_DIR=/Library/Developer/CommandLineTools PYTHONDONTWRITEBYTECODE=1
python3 - <<'EOF'
import pathlib
sheet = pathlib.Path('tools/contact_sheet.py')
text = sheet.read_text(encoding='utf-8')
old = "import json, re, html\nD='/Users/lattawb/workspace/symbiotic-design/icons'\n"
new = "import json, re, html, pathlib\nD=str(pathlib.Path(__file__).resolve().parents[1]/'icons')\n"
assert old in text
sheet.write_text(text.replace(old, new), encoding='utf-8')
readme = pathlib.Path('icons/standard/README.md')
text = readme.read_text(encoding='utf-8')
old = "57 icons in four categories (`transport`, `edit`, `app`, `audio`), one file per icon:"
new = "106 icons in six categories (`transport`, `edit`, `app`, `audio`, `editor`, `notation`), one file per icon:"
assert old in text
readme.write_text(text.replace(old, new), encoding='utf-8')
EOF
head -2 tools/contact_sheet.py
```

Expected: the two new first lines of `contact_sheet.py`: `import json, re, html, pathlib` and `D=str(pathlib.Path(__file__).resolve().parents[1]/'icons')`.

- [ ] **Step 5: Rebuild the contact sheet and the coverage report**

Run:

```bash
export DEVELOPER_DIR=/Library/Developer/CommandLineTools PYTHONDONTWRITEBYTECODE=1
python3 tools/contact_sheet.py
python3 tools/generate.py | tail -1
grep -A2 'To draw in-house' icons/coverage.md
```

Expected: a byte count from the contact sheet, `wrote 4 files`, and `None: every role's standard icon exists in `icons/standard/`.` under the heading. Open `icons/contact-sheet.html` in a browser only if a human reviewer asks; agents check the numbers.

- [ ] **Step 6: Run the tests to verify they pass**

Run:

```bash
export DEVELOPER_DIR=/Library/Developer/CommandLineTools PYTHONDONTWRITEBYTECODE=1
python3 -m unittest discover -s tools/tests 2>&1 | tail -3
```

Expected: `Ran 99 tests`, `OK` (house style holds for all 106 icons; every role has its icon).

- [ ] **Step 7: Commit**

Run:

```bash
export DEVELOPER_DIR=/Library/Developer/CommandLineTools PYTHONDONTWRITEBYTECODE=1
git add icons/standard/*.svg \
  icons/standard.json \
  icons/standard/README.md \
  icons/contact-sheet.html \
  icons/coverage.md \
  tools/contact_sheet.py \
  tools/tests/test_standard_icons.py
git status --short
git commit -q -F - <<'MSG'
Standard icons: 49 more in the house style, one for every role

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01F7df6grqTdqHgc2d2X359P
MSG
git status --short
```

Expected: `git status --short` before the commit lists only the paths above (no `.DS_Store`, no `__pycache__`); after the commit it prints nothing.

### Task 6: The SymbioticIcons product

Generated `StandardIcon` and `IconRole`, and the hand-written API: the drawing model and renderer, the resolver and registry, the SwiftUI `Icon` view, `NSImage.icon` and the `IconBitmap` helpers. From here a role whose standard icon is missing stops the generator.

**Files:**
- Create: `tools/swiftgen_icons.py`
- Modify: `tools/generate.py` (full replacement), `Package.swift` (full replacement), `tools/tests/test_generate.py` (append a class)
- Create: `Sources/SymbioticIcons/IconDrawing.swift`, `Sources/SymbioticIcons/Icons.swift`, `Sources/SymbioticIcons/Icon.swift`, `Sources/SymbioticIcons/NSImage+Icon.swift`, `Sources/SymbioticIcons/IconBitmap.swift`
- Generated (by Step 6): `Sources/SymbioticIcons/Generated/StandardIcon+Generated.swift`, `Sources/SymbioticIcons/Generated/IconRole+Generated.swift`
- Test: `tools/tests/test_swiftgen_icons.py`, `Tests/SymbioticIconsTests/RoleTests.swift`, `Tests/SymbioticIconsTests/RenderTests.swift`

**Interfaces:**
- Consumes: `svgsubset.parse_svg_file`, `svgsubset.SvgError`; `rolelib.validate`, `rolelib.missing_standard`, `rolelib.coverage_markdown`; `swiftgen_common.*`; `Theme`, `Theme.IconStrokeMetrics.width(forSize:)`, `EnvironmentValues.symbioticTheme` (Task 3).
- Produces (Python): `swiftgen_icons.OUT = "Sources/SymbioticIcons/Generated"`; `op_literal(op)`, `paint(shape)`, `drawing_literal(shapes, indent)`, `drawings_enum(type_name, cases: list[(case, raw, shapes)], header, imports) -> str` (Task 7 reuses it), `roles_swift(roles)`, `generate(standard: list[(name, shapes)], roles) -> dict`. `generate.py` gains `parse_dir(folder, names)` and `icons_step() -> (files, owned_dirs, missing)`.
- Produces (Swift, module `SymbioticIcons`): `enum PathOp { move, line, curve, close }`; `struct IconShape(paint: Paint, weight: CGFloat, cap: Cap, join: Join, ops: [PathOp])` with `Paint { stroke, fill, fillAndStroke }`, `Cap`, `Join` (`.cgLineCap`, `.cgLineJoin`); `struct IconDrawing(shapes:)` with `gridSize = 24`, `miterLimit = 4`, `path(of:size:) -> CGPath`, `draw(in: CGContext, size: CGFloat, strokeWidth: CGFloat)`; generated `enum StandardIcon: String, CaseIterable` (`.drawing`) and `enum IconRole: String, CaseIterable` (`.label`, `.standard: StandardIcon?`); `protocol IconProvider: Sendable { func drawing(for: IconRole) -> IconDrawing? }`; `enum ResolvedIcon { drawing(IconDrawing), wordmark(String) }`; `struct IconResolver(provider:)` with `resolve(_:) -> ResolvedIcon`; `enum Icons` with `wordmark`, `register(_:)`, `unregister()`, `resolver`; `struct Icon: View` (`init(_ role:, size: = 16)`, `init(_:size:resolver:)`); `NSImage.icon(_:size:theme: = .classicLight, resolver: = Icons.resolver) -> NSImage`; `enum IconBitmap` with `alpha(of: IconDrawing, size: Int, strokeWidth:) -> [UInt8]`, `alpha(of: CGImage) -> [UInt8]`, `meanDifference(_:_:) -> Double`.

- [ ] **Step 1: Write the failing Python tests**

File: `tools/tests/test_swiftgen_icons.py`

```python
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import svgsubset as s  # noqa: E402
import swiftgen_icons as g  # noqa: E402

HEAD = ('<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" '
        'fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="butt" stroke-linejoin="miter">')
PLAY = s.parse_svg_text(HEAD + '<polygon points="7 5.5 17 12 7 18.5"/></svg>')
DOT = s.parse_svg_text(HEAD + '<circle cx="12" cy="12" r="6.6" fill="currentColor" stroke="none"/></svg>')
ROLES = [
    {"id": "transport.play", "standard": "play", "label": "Play"},
    {"id": "file.import", "standard": "import", "label": "Import \"file\""},
    {"id": "brand.logo", "brand": "glyph-39", "label": "SymbioticAudio"},
]


class IconsSwift(unittest.TestCase):
    def setUp(self):
        self.files = g.generate([("play", PLAY), ("import", DOT)], ROLES)
        self.icons = self.files["Sources/SymbioticIcons/Generated/StandardIcon+Generated.swift"]
        self.roles = self.files["Sources/SymbioticIcons/Generated/IconRole+Generated.swift"]

    def test_ops(self):
        self.assertEqual(g.op_literal(("M", 7.0, 5.5)), ".move(7, 5.5)")
        self.assertEqual(g.op_literal(("C", 1, 2, 3, 4, 5, 6.123456)), ".curve(1, 2, 3, 4, 5, 6.1235)")
        self.assertEqual(g.op_literal(("Z",)), ".close")

    def test_standard_icon_enum(self):
        self.assertIn('    case play = "play"', self.icons)
        self.assertIn('    case `import` = "import"', self.icons)
        self.assertIn("        case .`import`: return StandardIconDrawings.`import`", self.icons)
        self.assertIn("IconShape(paint: .stroke, weight: 1, cap: .butt, join: .miter, "
                      "ops: [.move(7, 5.5), .line(17, 12), .line(7, 18.5), .close])", self.icons)
        self.assertIn("IconShape(paint: .fill, weight: 1", self.icons)

    def test_roles(self):
        self.assertIn('    case transportPlay = "transport.play"', self.roles)
        self.assertIn('        case .fileImport: return "Import \\"file\\""', self.roles)
        self.assertIn("        case .fileImport: return .`import`", self.roles)
        self.assertIn("        case .brandLogo: return nil", self.roles)

    def test_mit_header(self):
        for text in self.files.values():
            self.assertTrue(text.startswith("// Generated by tools/generate.py"))
            self.assertIn("MIT licence", text.split("\n")[1])

    def test_deterministic(self):
        self.assertEqual(g.generate([("play", PLAY), ("import", DOT)], ROLES), self.files)


if __name__ == "__main__":
    unittest.main()
```

Append to `tools/tests/test_generate.py`:

```python


class Icons(Scratch):
    def test_missing_standard_icon_is_listed_and_no_swift_is_written(self):
        def add_role(d):
            d["roles"].append({"id": "tool.glue", "standard": "glue", "label": "Glue tool"})
        self.edit_json("icons/roles.json", add_role)
        swift = self.root / "Sources" / "SymbioticIcons" / "Generated" / "IconRole+Generated.swift"
        before = swift.read_bytes()
        result = self.run_generate()
        self.assertEqual(result.returncode, 1)
        self.assertIn("error: role tool.glue needs icons/standard/glue.svg", result.stderr)
        self.assertIn("| `tool.glue` | `glue` |", (self.root / "icons" / "coverage.md").read_text(encoding="utf-8"))
        self.assertEqual(swift.read_bytes(), before)

    def test_unsupported_svg_fails(self):
        path = self.root / "icons" / "standard" / "play.svg"
        path.write_text(path.read_text(encoding="utf-8").replace("<polygon", '<polygon opacity="0.5"'),
                        encoding="utf-8")
        result = self.run_generate()
        self.assertEqual(result.returncode, 1)
        self.assertIn("play.svg: <polygon> attribute 'opacity' is not supported", result.stderr)

    def test_index_and_files_must_agree(self):
        (self.root / "icons" / "standard" / "orphan.svg").write_text(
            (self.root / "icons" / "standard" / "play.svg").read_text(encoding="utf-8"), encoding="utf-8")
        result = self.run_generate()
        self.assertEqual(result.returncode, 1)
        self.assertIn("orphan", result.stderr)
```

- [ ] **Step 2: Run them to verify they fail**

Run:

```bash
export DEVELOPER_DIR=/Library/Developer/CommandLineTools PYTHONDONTWRITEBYTECODE=1
python3 -m unittest discover -s tools/tests 2>&1 | tail -3
```

Expected: `FAILED (failures=2, errors=2)`: `No module named 'swiftgen_icons'`, and the new `Icons` generator tests fail because the Task 4 generator neither stops on a missing icon nor reads the SVGs.

- [ ] **Step 3: Write the failing Swift tests**

File: `Tests/SymbioticIconsTests/RoleTests.swift`

```swift
// MIT licence: see LICENSE.
import Testing
@testable import SymbioticIcons

private struct OneRoleProvider: IconProvider {
    let role: IconRole
    let drawing: IconDrawing
    func drawing(for role: IconRole) -> IconDrawing? { role == self.role ? drawing : nil }
}

@Suite struct RoleTests {
    let plain = IconResolver(provider: nil)

    @Test func rolesAreTypedByTheirDottedID() {
        #expect(IconRole(rawValue: "transport.play") == .transportPlay)
        #expect(IconRole.modeLoop.rawValue == "mode.loop")
        #expect(IconRole.transportPlay.label == "Play")
        #expect(IconRole(rawValue: "transport.plya") == nil)
    }

    @Test(arguments: IconRole.allCases.filter { $0 != .brandLogo }.map(\.rawValue))
    func everyRoleDrawsItsStandardIconWithoutAProvider(id: String) throws {
        let role = try #require(IconRole(rawValue: id))
        let standard = try #require(role.standard)
        #expect(plain.resolve(role) == .drawing(standard.drawing))
        #expect(!role.label.isEmpty)
    }

    @Test func logoWithoutProviderIsTheWordmark() {
        #expect(IconRole.brandLogo.standard == nil)
        #expect(plain.resolve(.brandLogo) == .wordmark("SymbioticAudio"))
    }

    @Test func providerOverridesOnlyTheRolesItMaps() {
        let custom = IconDrawing(shapes: [IconShape(paint: .stroke, weight: 1, cap: .butt, join: .miter,
                                                    ops: [.move(2, 2), .line(22, 22)])])
        let resolver = IconResolver(provider: OneRoleProvider(role: .transportStop, drawing: custom))
        #expect(resolver.resolve(.transportStop) == .drawing(custom))
        #expect(resolver.resolve(.transportPlay) == .drawing(StandardIcon.play.drawing))
        #expect(resolver.resolve(.brandLogo) == .wordmark(Icons.wordmark))
    }

    @Test(arguments: StandardIcon.allCases.map(\.rawValue))
    func everyStandardIconHasInk(name: String) throws {
        let icon = try #require(StandardIcon(rawValue: name))
        #expect(!icon.drawing.shapes.isEmpty)
        let mask = IconBitmap.alpha(of: icon.drawing, size: 24, strokeWidth: 1.2)
        #expect(mask.contains { $0 > 128 })
    }
}
```

File: `Tests/SymbioticIconsTests/RenderTests.swift`

```swift
// MIT licence: see LICENSE.
import AppKit
import SwiftUI
import Testing
import SymbioticTokens
@testable import SymbioticIcons

@Suite struct RenderTests {
    let plain = IconResolver(provider: nil)

    @Test(arguments: [16.0, 24.0, 32.0, 13.0])
    func nsImageIsATemplateOfTheRequestedSize(size: Double) {
        let image = NSImage.icon(.transportPlay, size: size, resolver: plain)
        #expect(image.isTemplate)
        #expect(image.size == NSSize(width: size, height: size))
        #expect(image.accessibilityDescription == "Play")
        #expect(image.cgImage(forProposedRect: nil, context: nil, hints: nil) != nil)
    }

    @Test func wordmarkImageIsTheRequestedHeightAndWiderThanTall() {
        let image = NSImage.icon(.brandLogo, size: 24, resolver: plain)
        #expect(image.isTemplate)
        #expect(image.size.height == 24)
        #expect(image.size.width > 48)
    }

    @Test func strokeComesFromTheThemeNotFromScaling() {
        let drawing = StandardIcon.stop.drawing
        let thin = IconBitmap.alpha(of: drawing, size: 48, strokeWidth: 1)
        let thick = IconBitmap.alpha(of: drawing, size: 48, strokeWidth: 3)
        let ink = { (mask: [UInt8]) in mask.reduce(0) { $0 + Int($1) } }
        #expect(ink(thick) > ink(thin) * 2)
    }

    @Test func templateImageUsesTheThemeStroke() {
        let image = NSImage.icon(.transportStop, size: 32, theme: .classicLight, resolver: plain)
        let cg = image.cgImage(forProposedRect: nil, context: nil, hints: nil)!
        let fromImage = IconBitmap.alpha(of: cg)
        let expected = IconBitmap.alpha(of: StandardIcon.stop.drawing, size: cg.width,
                                        strokeWidth: Theme.classicLight.iconStroke.width(forSize: 32) * CGFloat(cg.width) / 32)
        #expect(IconBitmap.meanDifference(fromImage, expected) < 0.02)
    }

    @MainActor @Test func iconViewDrawsInTheForegroundStyle() throws {
        let renderer = ImageRenderer(content: Icon(.transportStop, size: 24, resolver: plain).foregroundStyle(Color.red))
        renderer.scale = 2
        let image = try #require(renderer.cgImage)
        #expect(image.width == 48)
        let rep = NSBitmapImageRep(cgImage: image)
        var inked = 0
        var red = 0
        for y in 0..<image.height {
            for x in 0..<image.width {
                if let c = rep.colorAt(x: x, y: y)?.usingColorSpace(.sRGB), c.alphaComponent > 0.9 {
                    inked += 1
                    if c.redComponent > 0.9 && c.greenComponent < 0.5 && c.blueComponent < 0.5 { red += 1 }
                }
            }
        }
        #expect(inked > 50)
        #expect(red == inked)
    }

    @MainActor @Test func wordmarkViewRendersText() throws {
        let renderer = ImageRenderer(content: Icon(.brandLogo, size: 20, resolver: plain))
        let image = try #require(renderer.cgImage)
        #expect(image.width > image.height * 2)
    }
}
```

- [ ] **Step 4: Write the icon generator and wire it in**

File: `tools/swiftgen_icons.py`

```python
"""Icon SVGs and roles.json -> Swift source (spec section 3.4)."""
from swiftgen_common import MIT_HEADER, identifier, lower_camel, number, string_literal

OUT = "Sources/SymbioticIcons/Generated"


def op_literal(op):
    if op[0] == "Z":
        return ".close"
    name = {"M": "move", "L": "line", "C": "curve"}[op[0]]
    return f".{name}(" + ", ".join(number(v) for v in op[1:]) + ")"


def paint(shape):
    if shape.fill and shape.stroke:
        return "fillAndStroke"
    return "fill" if shape.fill else "stroke"


def drawing_literal(shapes, indent="        "):
    """An IconDrawing(...) expression for parsed svgsubset shapes."""
    out = ["IconDrawing(shapes: ["]
    for s in shapes:
        ops = ", ".join(op_literal(op) for op in s.ops)
        out.append(f"{indent}    IconShape(paint: .{paint(s)}, weight: {number(s.weight)}, "
                   f"cap: .{s.cap}, join: .{s.join}, ops: [{ops}]),")
    out.append(f"{indent}])")
    return "\n".join(out)


def drawings_enum(type_name, cases, header, imports):
    """cases: [(swift case name, raw value, shapes)] -> enum with a `drawing` property."""
    lines = [header, *[f"import {m}" for m in imports], ""]
    lines.append(f"public enum {type_name}: String, Sendable, Hashable, CaseIterable {{")
    for case, raw, _ in cases:
        lines.append(f"    case {identifier(case)} = {string_literal(raw)}")
    lines += ["", "    /// The icon on its 24-unit grid.", "    public var drawing: IconDrawing {", "        switch self {"]
    for case, _, _ in cases:
        lines.append(f"        case .{identifier(case)}: return {type_name}Drawings.{identifier(case)}")
    lines += ["        }", "    }", "}", "", f"enum {type_name}Drawings {{"]
    for case, raw, shapes in cases:
        lines.append(f"    /// {raw}")
        lines.append(f"    static let {identifier(case)}: IconDrawing = {drawing_literal(shapes, '    ')}")
    lines.append("}")
    return "\n".join(lines) + "\n"


def roles_swift(roles):
    lines = [MIT_HEADER, "", "/// Every icon role the apps use (icons/roles.json). A misspelt role is a compile error.",
             "public enum IconRole: String, Sendable, Hashable, CaseIterable {"]
    for r in roles:
        lines.append(f"    case {identifier(lower_camel(r['id']))} = {string_literal(r['id'])}")
    lines += ["", "    /// The default accessibility label.", "    public var label: String {", "        switch self {"]
    for r in roles:
        lines.append(f"        case .{identifier(lower_camel(r['id']))}: return {string_literal(r['label'])}")
    lines += ["        }", "    }", "",
              "    /// The standard (MIT) icon for this role; nil only for brand.logo, which falls back to the wordmark.",
              "    public var standard: StandardIcon? {", "        switch self {"]
    for r in roles:
        value = f".{identifier(lower_camel(r['standard']))}" if "standard" in r else "nil"
        lines.append(f"        case .{identifier(lower_camel(r['id']))}: return {value}")
    lines += ["        }", "    }", "}"]
    return "\n".join(lines) + "\n"


def generate(standard, roles):
    """standard: [(name, shapes)] in a stable order -> {relative path: text}."""
    return {
        f"{OUT}/StandardIcon+Generated.swift": drawings_enum(
            "StandardIcon", [(lower_camel(n), n, s) for n, s in standard], MIT_HEADER, ["CoreGraphics"]),
        f"{OUT}/IconRole+Generated.swift": roles_swift(roles),
    }
```

File: `tools/generate.py`

```python
#!/usr/bin/env python3
"""Validate the design sources and write every generated file.

Usage: python3 tools/generate.py
Writes tokens/contrast.md, icons/coverage.md, Sources/SymbioticTokens/Generated/
and Sources/SymbioticIcons/Generated/.
Exit status 1 (and nothing written) if a source is invalid. If a role's
standard icon has no SVG yet, icons/coverage.md is still written (it lists
what to draw) but no Swift is.
"""
import pathlib
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import rolelib  # noqa: E402
import svgsubset  # noqa: E402
import swiftgen_icons  # noqa: E402
import swiftgen_tokens  # noqa: E402
import tokenlib  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]


def write_tree(files, owned_dirs):
    """Write {relative path: text}; delete stale files in the generated dirs."""
    for d in owned_dirs:
        folder = ROOT / d
        if folder.is_dir():
            for old in folder.glob("*.swift"):
                if str(old.relative_to(ROOT)) not in files:
                    old.unlink()
    for rel, text in sorted(files.items()):
        path = ROOT / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def tokens_step():
    data = tokenlib.load(ROOT / "tokens" / "tokens.json")
    rows = tokenlib.contrast_rows(data)
    for tid, text, on, use, ratio, need, ok in rows:
        if not ok:
            print(f"warning: {tid}: {text} on {on} is {tokenlib.format_ratio(ratio)}, {use} needs {need:g}:1")
    files = swiftgen_tokens.generate(data)
    files["tokens/contrast.md"] = tokenlib.contrast_markdown(rows)
    return files, [swiftgen_tokens.OUT]


def parse_dir(folder, names):
    return [(n, svgsubset.parse_svg_file(folder / f"{n}.svg")) for n in names]


def icons_step():
    """Returns (files, owned dirs, missing standard icons)."""
    glyphs = rolelib.load_json(ROOT / "icons" / "glyphs.json")
    roles = rolelib.validate(rolelib.load_json(ROOT / "icons" / "roles.json"), glyphs)
    standard_names = [e["id"] for e in rolelib.load_json(ROOT / "icons" / "standard.json")]
    on_disk = sorted(p.stem for p in (ROOT / "icons" / "standard").glob("*.svg"))
    if sorted(standard_names) != on_disk:
        raise svgsubset.SvgError("icons/standard.json and icons/standard/*.svg list different icons: "
                                 f"{sorted(set(standard_names) ^ set(on_disk))}")
    files = {"icons/coverage.md": rolelib.coverage_markdown(roles, standard_names, glyphs)}
    missing = rolelib.missing_standard(roles, standard_names)
    standard = parse_dir(ROOT / "icons" / "standard", standard_names)
    if not missing:
        files.update(swiftgen_icons.generate(standard, roles))
    return files, [swiftgen_icons.OUT], missing


def main():
    try:
        token_files, token_dirs = tokens_step()
        icon_files, icon_dirs, missing = icons_step()
    except tokenlib.TokenError as e:
        for p in e.problems:
            print(f"error: tokens.json: {p}", file=sys.stderr)
        return 1
    except rolelib.RoleError as e:
        for p in e.problems:
            print(f"error: roles.json: {p}", file=sys.stderr)
        return 1
    except svgsubset.SvgError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    if missing:
        write_tree({"icons/coverage.md": icon_files["icons/coverage.md"]}, [])
        for rid, name in missing:
            print(f"error: role {rid} needs icons/standard/{name}.svg (listed in icons/coverage.md)",
                  file=sys.stderr)
        return 1
    files = {**token_files, **icon_files}
    write_tree(files, token_dirs + icon_dirs)
    print(f"wrote {len(files)} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 5: Write the package manifest and the hand-written Swift**

File: `Package.swift`

```swift
// swift-tools-version: 6.0
// MIT licence: see LICENSE.
import PackageDescription

/// The one place the deployment floor is set (spec section 4).
let minimumMacOS: SupportedPlatform = .macOS(.v14)

let package = Package(
    name: "symbiotic-design",
    platforms: [minimumMacOS],
    products: [
        .library(name: "SymbioticTokens", targets: ["SymbioticTokens"]),
        .library(name: "SymbioticIcons", targets: ["SymbioticIcons"]),
    ],
    targets: [
        .target(name: "SymbioticTokens"),
        .target(name: "SymbioticIcons", dependencies: ["SymbioticTokens"]),
        .testTarget(name: "SymbioticTokensTests", dependencies: ["SymbioticTokens"]),
        .testTarget(name: "SymbioticIconsTests", dependencies: ["SymbioticIcons", "SymbioticTokens"]),
    ]
)
```

File: `Sources/SymbioticIcons/IconDrawing.swift`

```swift
// MIT licence: see LICENSE.
import CoreGraphics

/// One path command on the 24-unit icon grid (y down).
public enum PathOp: Sendable, Hashable {
    case move(CGFloat, CGFloat)
    case line(CGFloat, CGFloat)
    case curve(CGFloat, CGFloat, CGFloat, CGFloat, CGFloat, CGFloat)
    case close
}

/// One stroked and/or filled path of an icon.
public struct IconShape: Sendable, Hashable {
    public enum Paint: Sendable, Hashable { case stroke, fill, fillAndStroke }
    public enum Cap: Sendable, Hashable { case butt, round, square }
    public enum Join: Sendable, Hashable { case miter, round, bevel }

    public let paint: Paint
    /// Stroke width relative to the house stroke (1.2 grid units = 1).
    public let weight: CGFloat
    public let cap: Cap
    public let join: Join
    public let ops: [PathOp]

    public init(paint: Paint, weight: CGFloat, cap: Cap, join: Join, ops: [PathOp]) {
        self.paint = paint
        self.weight = weight
        self.cap = cap
        self.join = join
        self.ops = ops
    }
}

/// A complete icon as generated drawing code: shapes on a 24-unit grid.
public struct IconDrawing: Sendable, Hashable {
    public static let gridSize: CGFloat = 24
    /// SVG's default miter limit, which the source artwork assumes.
    public static let miterLimit: CGFloat = 4

    public let shapes: [IconShape]

    public init(shapes: [IconShape]) {
        self.shapes = shapes
    }

    /// The path of one shape scaled from the grid to a `size`-point square, y down.
    public func path(of shape: IconShape, size: CGFloat) -> CGPath {
        let k = size / Self.gridSize
        let path = CGMutablePath()
        for op in shape.ops {
            switch op {
            case let .move(x, y):
                path.move(to: CGPoint(x: x * k, y: y * k))
            case let .line(x, y):
                path.addLine(to: CGPoint(x: x * k, y: y * k))
            case let .curve(x1, y1, x2, y2, x, y):
                path.addCurve(to: CGPoint(x: x * k, y: y * k),
                              control1: CGPoint(x: x1 * k, y: y1 * k),
                              control2: CGPoint(x: x2 * k, y: y2 * k))
            case .close:
                path.closeSubpath()
            }
        }
        return path
    }

    /// Draws into a context whose y axis points down, with its current fill and
    /// stroke colours. `strokeWidth` is the theme's icon stroke for `size`; it is
    /// not scaled with the drawing.
    public func draw(in context: CGContext, size: CGFloat, strokeWidth: CGFloat) {
        for shape in shapes {
            let path = path(of: shape, size: size)
            if shape.paint != .stroke {
                context.addPath(path)
                context.fillPath(using: .winding)
            }
            if shape.paint != .fill {
                context.setLineWidth(strokeWidth * shape.weight)
                context.setLineCap(shape.cap.cgLineCap)
                context.setLineJoin(shape.join.cgLineJoin)
                context.setMiterLimit(Self.miterLimit)
                context.addPath(path)
                context.strokePath()
            }
        }
    }
}

extension IconShape.Cap {
    public var cgLineCap: CGLineCap {
        switch self {
        case .butt: return .butt
        case .round: return .round
        case .square: return .square
        }
    }
}

extension IconShape.Join {
    public var cgLineJoin: CGLineJoin {
        switch self {
        case .miter: return .miter
        case .round: return .round
        case .bevel: return .bevel
        }
    }
}
```

File: `Sources/SymbioticIcons/Icons.swift`

```swift
// MIT licence: see LICENSE.
import Foundation

/// Supplies drawings for roles, e.g. SymbioticBrand.provider. Return nil to
/// let a role fall back to its standard icon.
public protocol IconProvider: Sendable {
    func drawing(for role: IconRole) -> IconDrawing?
}

/// What a role draws as.
public enum ResolvedIcon: Sendable, Hashable {
    case drawing(IconDrawing)
    /// Text instead of a drawing: brand.logo with no brand provider.
    case wordmark(String)
}

/// Resolves roles: the provider's drawing if it maps the role, otherwise the
/// standard icon; brand.logo without a provider becomes the wordmark.
public struct IconResolver: Sendable {
    public let provider: (any IconProvider)?

    public init(provider: (any IconProvider)?) {
        self.provider = provider
    }

    public func resolve(_ role: IconRole) -> ResolvedIcon {
        if let drawing = provider?.drawing(for: role) {
            return .drawing(drawing)
        }
        if let standard = role.standard {
            return .drawing(standard.drawing)
        }
        return .wordmark(Icons.wordmark)
    }
}

/// The app-wide icon registry.
public enum Icons {
    /// What brand.logo shows when no brand provider is registered.
    public static let wordmark = "SymbioticAudio"

    /// Registers the provider used by `Icon` and `NSImage.icon` (one per app):
    /// `#if canImport(SymbioticBrand) Icons.register(SymbioticBrand.provider) #endif`
    public static func register(_ provider: any IconProvider) {
        registry.set(provider)
    }

    /// Removes the registered provider; every role draws its standard icon again.
    public static func unregister() {
        registry.set(nil)
    }

    /// A resolver for the currently registered provider.
    public static var resolver: IconResolver {
        IconResolver(provider: registry.get())
    }

    private static let registry = Registry()
}

private final class Registry: @unchecked Sendable {
    private let lock = NSLock()
    private var provider: (any IconProvider)?

    func set(_ value: (any IconProvider)?) {
        lock.lock()
        provider = value
        lock.unlock()
    }

    func get() -> (any IconProvider)? {
        lock.lock()
        defer { lock.unlock() }
        return provider
    }
}
```

File: `Sources/SymbioticIcons/Icon.swift`

```swift
// MIT licence: see LICENSE.
import SwiftUI
import SymbioticTokens

/// An icon drawn by role in the current foreground style, with the theme's
/// icon stroke for its size.
public struct Icon: View {
    private let role: IconRole
    private let size: CGFloat
    private let resolver: IconResolver?
    @Environment(\.symbioticTheme) private var theme

    public init(_ role: IconRole, size: CGFloat = 16) {
        self.init(role, size: size, resolver: nil)
    }

    /// Uses `resolver` instead of the registered provider (previews and tests).
    public init(_ role: IconRole, size: CGFloat = 16, resolver: IconResolver?) {
        self.role = role
        self.size = size
        self.resolver = resolver
    }

    public var body: some View {
        switch (resolver ?? Icons.resolver).resolve(role) {
        case .drawing(let drawing):
            let stroke = theme.iconStroke.width(forSize: size)
            Canvas { context, canvasSize in
                let side = min(canvasSize.width, canvasSize.height)
                for shape in drawing.shapes {
                    let path = Path(drawing.path(of: shape, size: side))
                    if shape.paint != .stroke {
                        context.fill(path, with: .foreground)
                    }
                    if shape.paint != .fill {
                        context.stroke(path, with: .foreground, style: StrokeStyle(
                            lineWidth: stroke * shape.weight,
                            lineCap: shape.cap.cgLineCap,
                            lineJoin: shape.join.cgLineJoin,
                            miterLimit: IconDrawing.miterLimit))
                    }
                }
            }
            .frame(width: size, height: size)
            .accessibilityElement()
            .accessibilityLabel(role.label)
            .accessibilityAddTraits(.isImage)
        case .wordmark(let text):
            Text(text)
                .font(.system(size: size * 0.75, weight: .semibold))
                .lineLimit(1)
                .fixedSize()
                .frame(height: size)
                .accessibilityLabel(role.label)
        }
    }
}
```

File: `Sources/SymbioticIcons/NSImage+Icon.swift`

```swift
// MIT licence: see LICENSE.
import AppKit
import SymbioticTokens

extension NSImage {
    /// A template image of the role at `size` points (tinted by AppKit like any
    /// template image). The stroke is the theme's icon stroke for that size.
    /// brand.logo without a brand provider becomes the wordmark: `size` high
    /// and as wide as the text.
    public static func icon(_ role: IconRole, size: CGFloat, theme: Theme = .classicLight,
                            resolver: IconResolver = Icons.resolver) -> NSImage {
        let image: NSImage
        switch resolver.resolve(role) {
        case .drawing(let drawing):
            let stroke = theme.iconStroke.width(forSize: size)
            image = NSImage(size: NSSize(width: size, height: size), flipped: true) { _ in
                guard let context = NSGraphicsContext.current?.cgContext else { return false }
                context.setFillColor(CGColor(gray: 0, alpha: 1))
                context.setStrokeColor(CGColor(gray: 0, alpha: 1))
                drawing.draw(in: context, size: size, strokeWidth: stroke)
                return true
            }
        case .wordmark(let text):
            let font = NSFont.systemFont(ofSize: size * 0.75, weight: .semibold)
            let attributed = NSAttributedString(string: text, attributes: [.font: font, .foregroundColor: NSColor.black])
            let width = ceil(attributed.size().width)
            image = NSImage(size: NSSize(width: width, height: size), flipped: false) { rect in
                let textHeight = attributed.size().height
                attributed.draw(at: NSPoint(x: 0, y: (rect.height - textHeight) / 2))
                return true
            }
        }
        image.isTemplate = true
        image.accessibilityDescription = role.label
        return image
    }
}
```

File: `Sources/SymbioticIcons/IconBitmap.swift`

```swift
// MIT licence: see LICENSE.
import CoreGraphics

/// Coverage masks for comparing icon renderings (fidelity tests, app snapshot tests).
public enum IconBitmap {
    /// Renders `drawing` at `size` x `size` pixels in black on transparent and
    /// returns the alpha channel, row by row from the top.
    public static func alpha(of drawing: IconDrawing, size: Int, strokeWidth: CGFloat) -> [UInt8] {
        render(width: size, height: size) { context in
            context.translateBy(x: 0, y: CGFloat(size))
            context.scaleBy(x: 1, y: -1)
            context.setFillColor(CGColor(gray: 0, alpha: 1))
            context.setStrokeColor(CGColor(gray: 0, alpha: 1))
            drawing.draw(in: context, size: CGFloat(size), strokeWidth: strokeWidth)
        }
    }

    /// The alpha channel of an image, row by row from the top.
    public static func alpha(of image: CGImage) -> [UInt8] {
        render(width: image.width, height: image.height) { context in
            context.draw(image, in: CGRect(x: 0, y: 0, width: image.width, height: image.height))
        }
    }

    /// Mean absolute difference of two equal-length masks, 0 (same) to 1.
    public static func meanDifference(_ a: [UInt8], _ b: [UInt8]) -> Double {
        precondition(a.count == b.count, "masks differ in size")
        guard !a.isEmpty else { return 0 }
        var total = 0
        for i in a.indices {
            total += abs(Int(a[i]) - Int(b[i]))
        }
        return Double(total) / Double(a.count) / 255
    }

    private static func render(width: Int, height: Int, _ body: (CGContext) -> Void) -> [UInt8] {
        var pixels = [UInt8](repeating: 0, count: width * height * 4)
        pixels.withUnsafeMutableBytes { buffer in
            guard let context = CGContext(
                data: buffer.baseAddress, width: width, height: height, bitsPerComponent: 8,
                bytesPerRow: width * 4, space: CGColorSpace(name: CGColorSpace.sRGB)!,
                bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue) else { return }
            body(context)
        }
        return stride(from: 3, to: pixels.count, by: 4).map { pixels[$0] }
    }
}
```

- [ ] **Step 6: Generate**

Run:

```bash
export DEVELOPER_DIR=/Library/Developer/CommandLineTools PYTHONDONTWRITEBYTECODE=1
python3 tools/generate.py | tail -1
```

Expected: `wrote 6 files`; `Sources/SymbioticIcons/Generated/` holds `StandardIcon+Generated.swift` (106 cases) and `IconRole+Generated.swift` (120 cases).

- [ ] **Step 7: Run all tests to verify they pass**

Run:

```bash
export DEVELOPER_DIR=/Library/Developer/CommandLineTools PYTHONDONTWRITEBYTECODE=1
python3 -m unittest discover -s tools/tests 2>&1 | tail -3
scripts/swift.sh build 2>&1 | grep -v deprecated | tail -1
scripts/swift.sh test 2>&1 | grep -E '✘|Test run with'
```

Expected: Python `Ran 107 tests`, `OK`; `Build complete!`; `✔ Test run with 19 tests in 3 suites passed`; no `✘`.

- [ ] **Step 8: Commit**

Run:

```bash
export DEVELOPER_DIR=/Library/Developer/CommandLineTools PYTHONDONTWRITEBYTECODE=1
git add Package.swift \
  tools/swiftgen_icons.py \
  tools/generate.py \
  tools/tests/test_swiftgen_icons.py \
  tools/tests/test_generate.py \
  Sources/SymbioticIcons \
  Tests/SymbioticIconsTests
git status --short
git commit -q -F - <<'MSG'
SymbioticIcons: generated roles and standard icons, Icon view, NSImage.icon, registry

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01F7df6grqTdqHgc2d2X359P
MSG
git status --short
```

Expected: `git status --short` before the commit lists only the paths above (no `.DS_Store`, no `__pycache__`); after the commit it prints nothing.

### Task 7: The SymbioticBrand product

The 41 glyphs as generated drawing code, the role-to-glyph map for the 12 confirmed glyphs, and `SymbioticBrand.provider`. Every Swift file in the product starts with the `ASSETS-LICENSE` notice.

**Files:**
- Create: `tools/swiftgen_brand.py`, `Sources/SymbioticBrand/SymbioticBrand.swift`
- Modify: `tools/generate.py` (full replacement), `Package.swift` (full replacement)
- Generated (by Step 6): `Sources/SymbioticBrand/Generated/BrandGlyph+Generated.swift`, `Sources/SymbioticBrand/Generated/BrandRoles+Generated.swift`
- Test: `tools/tests/test_swiftgen_brand.py`, `Tests/SymbioticBrandTests/BrandTests.swift`

**Interfaces:**
- Consumes: `swiftgen_icons.drawings_enum`, `swiftgen_common.license_comment`, `lower_camel`, `identifier` (Tasks 3, 6); `IconRole`, `IconDrawing`, `IconProvider`, `IconResolver`, `Icons` (Task 6).
- Produces (Python): `swiftgen_brand.OUT = "Sources/SymbioticBrand/Generated"`, `header(assets_license)`, `brand_roles_swift(roles, head)`, `generate(glyphs: list[(id, shapes)], roles, assets_license) -> dict`.
- Produces (Swift, module `SymbioticBrand`): `enum BrandGlyph: String, CaseIterable` (`.glyph01` … `.glyph41`, `.drawing`), `BrandGlyph.forRole(_: IconRole) -> BrandGlyph?`, `enum SymbioticBrand { static let provider: any IconProvider }`.

- [ ] **Step 1: Write the failing tests**

File: `tools/tests/test_swiftgen_brand.py`

```python
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import swiftgen_brand as g  # noqa: E402
from test_swiftgen_icons import PLAY, ROLES  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[2]


class BrandSwift(unittest.TestCase):
    def setUp(self):
        self.notice = (ROOT / "ASSETS-LICENSE").read_text(encoding="utf-8")
        self.files = g.generate([("glyph-39", PLAY)], ROLES, self.notice)

    def test_every_file_starts_with_the_assets_notice(self):
        first = "// " + self.notice.split("\n")[0]
        for path, text in self.files.items():
            self.assertTrue(path.startswith("Sources/SymbioticBrand/Generated/"))
            self.assertTrue(text.startswith(first), path)
            self.assertIn("// Contact: symbioticaudio@proton.me", text)
            self.assertNotIn("MIT", text.split("Generated by")[1])

    def test_glyph_enum_and_role_map(self):
        glyphs = self.files["Sources/SymbioticBrand/Generated/BrandGlyph+Generated.swift"]
        roles = self.files["Sources/SymbioticBrand/Generated/BrandRoles+Generated.swift"]
        self.assertIn('    case glyph39 = "glyph-39"', glyphs)
        self.assertIn("import SymbioticIcons", glyphs)
        self.assertIn("        case .brandLogo: return .glyph39", roles)
        self.assertNotIn("transportPlay", roles)

    def test_repository_sources_carry_the_notice(self):
        first = "// " + self.notice.split("\n")[0]
        for path in sorted((ROOT / "Sources" / "SymbioticBrand").rglob("*.swift")):
            with self.subTest(path.name):
                self.assertTrue(path.read_text(encoding="utf-8").startswith(first))


if __name__ == "__main__":
    unittest.main()
```

File: `Tests/SymbioticBrandTests/BrandTests.swift`

```swift
// SymbioticAudio branded artwork: see ASSETS-LICENSE. All rights reserved.
import Testing
import SymbioticIcons
@testable import SymbioticBrand

@Suite struct BrandTests {
    let branded = IconResolver(provider: SymbioticBrand.provider)

    @Test func mappedRolesDrawTheirGlyphs() {
        #expect(branded.resolve(.modeLoop) == .drawing(BrandGlyph.glyph40.drawing))
        #expect(branded.resolve(.editorEnvelope) == .drawing(BrandGlyph.glyph05.drawing))
        #expect(branded.resolve(.brandLogo) == .drawing(BrandGlyph.glyph39.drawing))
        #expect(branded.resolve(.transportPlay) == .drawing(StandardIcon.play.drawing))
    }

    @Test func exactlyTheTwelveConfirmedGlyphsAreMapped() {
        let mapped = Set(IconRole.allCases.compactMap { BrandGlyph.forRole($0) })
        #expect(mapped.count == 12)
        #expect(!mapped.contains(.glyph27))
        #expect(BrandGlyph.allCases.count == 41)
    }

    /// The only test that touches the app-wide registry, so parallel tests never see it change.
    @Test func registeringTheProviderSwitchesTheAppWideResolver() {
        Icons.unregister()
        #expect(Icons.resolver.resolve(.modeLoop) == .drawing(StandardIcon.loop.drawing))
        #expect(Icons.resolver.resolve(.brandLogo) == .wordmark("SymbioticAudio"))
        Icons.register(SymbioticBrand.provider)
        #expect(Icons.resolver.resolve(.modeLoop) == .drawing(BrandGlyph.glyph40.drawing))
        Icons.unregister()
        #expect(Icons.resolver.resolve(.modeLoop) == .drawing(StandardIcon.loop.drawing))
    }
}
```

- [ ] **Step 2: Run them to verify they fail**

Run:

```bash
export DEVELOPER_DIR=/Library/Developer/CommandLineTools PYTHONDONTWRITEBYTECODE=1
python3 -m unittest tools/tests/test_swiftgen_brand.py 2>&1 | tail -3
```

Expected: `ModuleNotFoundError: No module named 'swiftgen_brand'`.

- [ ] **Step 3: Write the brand generator**

File: `tools/swiftgen_brand.py`

```python
"""Brand glyphs and their role mapping -> Swift source for SymbioticBrand (spec section 3.4).

Every file written here starts with the ASSETS-LICENSE notice: the output is
a rendering of the owner's artwork and is all rights reserved.
"""
from swiftgen_common import identifier, license_comment, lower_camel
from swiftgen_icons import drawings_enum

OUT = "Sources/SymbioticBrand/Generated"


def header(assets_license):
    return license_comment(assets_license) + "//\n// Generated by tools/generate.py. Do not edit.\n"


def brand_roles_swift(roles, head):
    lines = [head, "import SymbioticIcons", "", "extension BrandGlyph {",
             "    /// The brand glyph the owner assigned to a role, if any (icons/roles.json).",
             "    public static func forRole(_ role: IconRole) -> BrandGlyph? {", "        switch role {"]
    for r in roles:
        if "brand" in r:
            lines.append(f"        case .{identifier(lower_camel(r['id']))}: return .{identifier(lower_camel(r['brand']))}")
    lines += ["        default: return nil", "        }", "    }", "}"]
    return "\n".join(lines) + "\n"


def generate(glyphs, roles, assets_license):
    """glyphs: [(id, shapes)] in a stable order -> {relative path: text}."""
    head = header(assets_license)
    return {
        f"{OUT}/BrandGlyph+Generated.swift": drawings_enum(
            "BrandGlyph", [(lower_camel(n), n, s) for n, s in glyphs], head, ["CoreGraphics", "SymbioticIcons"]),
        f"{OUT}/BrandRoles+Generated.swift": brand_roles_swift(roles, head),
    }
```

File: `tools/generate.py`

```python
#!/usr/bin/env python3
"""Validate the design sources and write every generated file.

Usage: python3 tools/generate.py
Writes tokens/contrast.md, icons/coverage.md and Sources/*/Generated/.
Exit status 1 (and nothing written) if a source is invalid. If a role's
standard icon has no SVG yet, icons/coverage.md is still written (it lists
what to draw) but no Swift is.
"""
import pathlib
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import rolelib  # noqa: E402
import svgsubset  # noqa: E402
import swiftgen_brand  # noqa: E402
import swiftgen_icons  # noqa: E402
import swiftgen_tokens  # noqa: E402
import tokenlib  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]


def write_tree(files, owned_dirs):
    """Write {relative path: text}; delete stale files in the generated dirs."""
    for d in owned_dirs:
        folder = ROOT / d
        if folder.is_dir():
            for old in folder.glob("*.swift"):
                if str(old.relative_to(ROOT)) not in files:
                    old.unlink()
    for rel, text in sorted(files.items()):
        path = ROOT / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def tokens_step():
    data = tokenlib.load(ROOT / "tokens" / "tokens.json")
    rows = tokenlib.contrast_rows(data)
    for tid, text, on, use, ratio, need, ok in rows:
        if not ok:
            print(f"warning: {tid}: {text} on {on} is {tokenlib.format_ratio(ratio)}, {use} needs {need:g}:1")
    files = swiftgen_tokens.generate(data)
    files["tokens/contrast.md"] = tokenlib.contrast_markdown(rows)
    return files, [swiftgen_tokens.OUT]


def parse_dir(folder, names):
    return [(n, svgsubset.parse_svg_file(folder / f"{n}.svg")) for n in names]


def icons_step():
    """Returns (files, owned dirs, missing standard icons)."""
    glyphs = rolelib.load_json(ROOT / "icons" / "glyphs.json")
    roles = rolelib.validate(rolelib.load_json(ROOT / "icons" / "roles.json"), glyphs)
    standard_names = [e["id"] for e in rolelib.load_json(ROOT / "icons" / "standard.json")]
    on_disk = sorted(p.stem for p in (ROOT / "icons" / "standard").glob("*.svg"))
    if sorted(standard_names) != on_disk:
        raise svgsubset.SvgError("icons/standard.json and icons/standard/*.svg list different icons: "
                                 f"{sorted(set(standard_names) ^ set(on_disk))}")
    files = {"icons/coverage.md": rolelib.coverage_markdown(roles, standard_names, glyphs)}
    missing = rolelib.missing_standard(roles, standard_names)
    standard = parse_dir(ROOT / "icons" / "standard", standard_names)
    brand = parse_dir(ROOT / "icons" / "svg", [g["id"] for g in glyphs])
    if not missing:
        files.update(swiftgen_icons.generate(standard, roles))
        assets_license = (ROOT / "ASSETS-LICENSE").read_text(encoding="utf-8")
        files.update(swiftgen_brand.generate(brand, roles, assets_license))
    return files, [swiftgen_icons.OUT, swiftgen_brand.OUT], missing


def main():
    try:
        token_files, token_dirs = tokens_step()
        icon_files, icon_dirs, missing = icons_step()
    except tokenlib.TokenError as e:
        for p in e.problems:
            print(f"error: tokens.json: {p}", file=sys.stderr)
        return 1
    except rolelib.RoleError as e:
        for p in e.problems:
            print(f"error: roles.json: {p}", file=sys.stderr)
        return 1
    except svgsubset.SvgError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    if missing:
        write_tree({"icons/coverage.md": icon_files["icons/coverage.md"]}, [])
        for rid, name in missing:
            print(f"error: role {rid} needs icons/standard/{name}.svg (listed in icons/coverage.md)",
                  file=sys.stderr)
        return 1
    files = {**token_files, **icon_files}
    write_tree(files, token_dirs + icon_dirs)
    print(f"wrote {len(files)} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Write the provider**

The file starts with the full `ASSETS-LICENSE` text as comments.

File: `Sources/SymbioticBrand/SymbioticBrand.swift`

```swift
// SymbioticAudio branded artwork
// Copyright (c) 2006-2026 Westlee Latta. All rights reserved.
//
// The following files are proprietary artwork and brand identity of
// SymbioticAudio. They are NOT licensed under the MIT licence in LICENSE, nor
// under any open-source licence of an application that uses them (including
// VizDAW and EG13, which are GPL-3.0):
//
//   - source-art/          (master artwork, Photoshop files)
//   - icons/svg/glyph-*    (glyph icons redrawn from the master artwork)
//   - icons/contact-sheet.html (embeds the glyph artwork; its glyph section
//     remains all rights reserved)
//   - logo/                (SymbioticAudio logo, when added)
//   - any PDF, PNG or other rendering generated from the files above
//
// Not covered by this file: the standard icon set in icons/standard/ (and
// icons/standard.json), which is MIT-licensed under LICENSE. The contact sheet
// also shows those standard icons; that section is MIT, the glyph section is not.
//
// No permission is granted to copy, modify, distribute or use this artwork,
// in whole or in part, except in official SymbioticAudio releases or with the
// copyright holder's prior written permission. Forks and redistributions of
// SymbioticAudio's open-source applications must remove this artwork and use
// their own or the applications' fallback icons.
//
// Contact: symbioticaudio@proton.me

import SymbioticIcons

/// The owner's brand glyphs as an icon provider. Register it once at launch:
///
///     #if canImport(SymbioticBrand)
///     Icons.register(SymbioticBrand.provider)
///     #endif
///
/// A fork removes the SymbioticBrand dependency and gets the standard icons.
public enum SymbioticBrand {
    public static let provider: any IconProvider = BrandProvider()
}

struct BrandProvider: IconProvider {
    func drawing(for role: IconRole) -> IconDrawing? {
        BrandGlyph.forRole(role)?.drawing
    }
}
```

- [ ] **Step 5: Add the product to the manifest**

File: `Package.swift`

```swift
// swift-tools-version: 6.0
// MIT licence: see LICENSE.
import PackageDescription

/// The one place the deployment floor is set (spec section 4).
let minimumMacOS: SupportedPlatform = .macOS(.v14)

let package = Package(
    name: "symbiotic-design",
    platforms: [minimumMacOS],
    products: [
        .library(name: "SymbioticTokens", targets: ["SymbioticTokens"]),
        .library(name: "SymbioticIcons", targets: ["SymbioticIcons"]),
        .library(name: "SymbioticBrand", targets: ["SymbioticBrand"]),
    ],
    targets: [
        .target(name: "SymbioticTokens"),
        .target(name: "SymbioticIcons", dependencies: ["SymbioticTokens"]),
        .target(name: "SymbioticBrand", dependencies: ["SymbioticIcons"]),
        .testTarget(name: "SymbioticTokensTests", dependencies: ["SymbioticTokens"]),
        .testTarget(name: "SymbioticIconsTests", dependencies: ["SymbioticIcons", "SymbioticTokens"]),
        .testTarget(name: "SymbioticBrandTests", dependencies: ["SymbioticBrand", "SymbioticTokens"]),
    ]
)
```

- [ ] **Step 6: Generate**

Run:

```bash
export DEVELOPER_DIR=/Library/Developer/CommandLineTools PYTHONDONTWRITEBYTECODE=1
python3 tools/generate.py | tail -1
head -2 Sources/SymbioticBrand/Generated/BrandGlyph+Generated.swift
```

Expected: `wrote 8 files`, then `// SymbioticAudio branded artwork` and `// Copyright (c) 2006-2026 Westlee Latta. All rights reserved.`

- [ ] **Step 7: Run all tests to verify they pass**

Run:

```bash
export DEVELOPER_DIR=/Library/Developer/CommandLineTools PYTHONDONTWRITEBYTECODE=1
python3 -m unittest discover -s tools/tests 2>&1 | tail -3
scripts/swift.sh build 2>&1 | grep -v deprecated | tail -1
scripts/swift.sh test 2>&1 | grep -E '✘|Test run with'
```

Expected: Python `Ran 110 tests`, `OK`; `Build complete!`; `✔ Test run with 22 tests in 4 suites passed`; no `✘`.

- [ ] **Step 8: Commit**

Run:

```bash
export DEVELOPER_DIR=/Library/Developer/CommandLineTools PYTHONDONTWRITEBYTECODE=1
git add Package.swift \
  tools/swiftgen_brand.py \
  tools/generate.py \
  tools/tests/test_swiftgen_brand.py \
  Sources/SymbioticBrand \
  Tests/SymbioticBrandTests
git status --short
git commit -q -F - <<'MSG'
SymbioticBrand: glyphs and logo as drawing code, brand provider (all rights reserved)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01F7df6grqTdqHgc2d2X359P
MSG
git status --short
```

Expected: `git status --short` before the commit lists only the paths above (no `.DS_Store`, no `__pycache__`); after the commit it prints nothing.

### Task 8: Reference PNGs and fidelity tests

`tools/references.py` renders every SVG at 48 x 48 px with headless Chrome (black on transparent); Swift tests render the same icons through the generated code and compare alpha (Ruling 13). Rendering all 147 references takes about two minutes.

**Files:**
- Create: `tools/references.py`
- Modify: `Package.swift` (full replacement: test targets exclude `References`)
- Create (by Step 5): `Tests/SymbioticIconsTests/References/*.png` (106), `Tests/SymbioticBrandTests/References/*.png` (41, all rights reserved)
- Test: `tools/tests/test_references.py`, `Tests/SymbioticIconsTests/FidelityTests.swift`, `Tests/SymbioticBrandTests/BrandFidelityTests.swift`

**Interfaces:**
- Consumes: `IconBitmap.alpha(of:size:strokeWidth:)`, `IconBitmap.alpha(of: CGImage)`, `IconBitmap.meanDifference` (Task 6); `StandardIcon`, `BrandGlyph` (Tasks 6, 7); `Theme.classicLight.iconStroke.width(forSize: 48)` = 2.4.
- Produces: `references.page_for(svg_text) -> str`, `references.render(svg_path, png_path, work)`, `references.SETS`, `references.main(names: set) -> int`; CLI `python3 tools/references.py [name ...]`.

- [ ] **Step 1: Write the failing tests**

File: `tools/tests/test_references.py`

```python
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import references as r  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[2]


class Page(unittest.TestCase):
    def test_page_draws_the_svg_at_48_px_in_black_on_transparent(self):
        svg = (ROOT / "icons" / "standard" / "play.svg").read_text(encoding="utf-8")
        page = r.page_for(svg)
        self.assertIn('width="48" height="48"', page)
        self.assertIn("background:transparent", page)
        self.assertIn("color:#000", page)

    def test_root_without_24_px_size_is_rejected(self):
        with self.assertRaises(ValueError):
            r.page_for('<svg viewBox="0 0 24 24"><line x1="0" y1="0" x2="1" y2="1"/></svg>')


class References(unittest.TestCase):
    def test_every_icon_has_a_48_px_reference(self):
        for src, dst in r.SETS:
            for svg in sorted(src.glob("*.svg")):
                with self.subTest(svg.name):
                    data = (dst / f"{svg.stem}.png").read_bytes()
                    self.assertEqual(data[:8], b"\x89PNG\r\n\x1a\n")
                    self.assertEqual((int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big")), (48, 48))


if __name__ == "__main__":
    unittest.main()
```

File: `Tests/SymbioticIconsTests/FidelityTests.swift`

```swift
// MIT licence: see LICENSE.
import CoreGraphics
import Foundation
import ImageIO
import Testing
import SymbioticTokens
@testable import SymbioticIcons

/// Every standard icon drawn by the generated code at 48 px matches the
/// headless-Chrome render of its SVG (tools/references.py).
@Suite struct FidelityTests {
    static let size = 48
    /// Mean per-pixel alpha difference allowed (0...1). See the plan's ruling on the tolerance.
    static let tolerance = 0.02

    static func reference(_ name: String) throws -> [UInt8] {
        let url = URL(fileURLWithPath: #filePath).deletingLastPathComponent()
            .appendingPathComponent("References/\(name).png")
        let source = try #require(CGImageSourceCreateWithURL(url as CFURL, nil), "missing \(url.path)")
        let image = try #require(CGImageSourceCreateImageAtIndex(source, 0, nil))
        #expect(image.width == size && image.height == size)
        return IconBitmap.alpha(of: image)
    }

    @Test(arguments: StandardIcon.allCases.map(\.rawValue))
    func matchesReference(name: String) throws {
        let icon = try #require(StandardIcon(rawValue: name))
        let stroke = Theme.classicLight.iconStroke.width(forSize: CGFloat(Self.size))
        let ours = IconBitmap.alpha(of: icon.drawing, size: Self.size, strokeWidth: stroke)
        let diff = IconBitmap.meanDifference(ours, try Self.reference(name))
        #expect(diff < Self.tolerance, "\(name): mean difference \(diff)")
    }

    @Test func aDifferentIconDoesNotMatch() throws {
        let stroke = Theme.classicLight.iconStroke.width(forSize: CGFloat(Self.size))
        let ours = IconBitmap.alpha(of: StandardIcon.play.drawing, size: Self.size, strokeWidth: stroke)
        #expect(IconBitmap.meanDifference(ours, try Self.reference("stop")) > Self.tolerance)
    }
}
```

File: `Tests/SymbioticBrandTests/BrandFidelityTests.swift`

```swift
// SymbioticAudio branded artwork: see ASSETS-LICENSE. All rights reserved.
import CoreGraphics
import Foundation
import ImageIO
import Testing
import SymbioticIcons
import SymbioticTokens
@testable import SymbioticBrand

/// Every brand glyph drawn by the generated code at 48 px matches the
/// headless-Chrome render of its SVG (tools/references.py).
@Suite struct BrandFidelityTests {
    /// Same tolerance as the standard icons (FidelityTests.tolerance).
    static let tolerance = 0.02

    @Test(arguments: BrandGlyph.allCases.map(\.rawValue))
    func glyphMatchesReference(id: String) throws {
        let glyph = try #require(BrandGlyph(rawValue: id))
        let url = URL(fileURLWithPath: #filePath).deletingLastPathComponent()
            .appendingPathComponent("References/\(id).png")
        let source = try #require(CGImageSourceCreateWithURL(url as CFURL, nil), "missing \(url.path)")
        let image = try #require(CGImageSourceCreateImageAtIndex(source, 0, nil))
        let stroke = Theme.classicLight.iconStroke.width(forSize: 48)
        let ours = IconBitmap.alpha(of: glyph.drawing, size: 48, strokeWidth: stroke)
        let diff = IconBitmap.meanDifference(ours, IconBitmap.alpha(of: image))
        #expect(diff < Self.tolerance, "\(id): mean difference \(diff)")
    }
}
```

- [ ] **Step 2: Run them to verify they fail**

Run:

```bash
export DEVELOPER_DIR=/Library/Developer/CommandLineTools PYTHONDONTWRITEBYTECODE=1
python3 -m unittest tools/tests/test_references.py 2>&1 | tail -3
```

Expected: `ModuleNotFoundError: No module named 'references'`.

- [ ] **Step 3: Write the renderer**

File: `tools/references.py`

```python
#!/usr/bin/env python3
"""Render reference PNGs of every icon SVG with headless Chrome.

Usage: python3 tools/references.py [name ...]
Writes Tests/SymbioticIconsTests/References/<name>.png for icons/standard/
and Tests/SymbioticBrandTests/References/<glyph>.png for icons/svg/ (those
renderings are all rights reserved, see ASSETS-LICENSE). Each PNG is 48x48,
black ink on a transparent background; the fidelity tests compare its alpha
with the generated Swift drawing code. With names, renders only those icons.
Set CHROME to use another Chrome binary.
"""
import concurrent.futures
import os
import pathlib
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
CHROME = os.environ.get("CHROME", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
SIZE = 48
SETS = [
    (ROOT / "icons" / "standard", ROOT / "Tests" / "SymbioticIconsTests" / "References"),
    (ROOT / "icons" / "svg", ROOT / "Tests" / "SymbioticBrandTests" / "References"),
]
PAGE = ("<!doctype html><html><head><meta charset=\"utf-8\"><style>"
        "html,body{{margin:0;padding:0;background:transparent}}svg{{display:block;color:#000}}"
        "</style></head><body>{svg}</body></html>")


def page_for(svg_text):
    svg = svg_text.replace('width="24" height="24"', f'width="{SIZE}" height="{SIZE}"', 1)
    if f'width="{SIZE}"' not in svg:
        raise ValueError("root <svg> must carry width=\"24\" height=\"24\"")
    return PAGE.format(svg=svg)


def render(svg_path, png_path, work):
    html = pathlib.Path(work) / f"{svg_path.stem}.html"
    html.write_text(page_for(svg_path.read_text(encoding="utf-8")), encoding="utf-8")
    png_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                    "--force-device-scale-factor=1", "--default-background-color=00000000",
                    f"--window-size={SIZE},{SIZE}", f"--user-data-dir={work}/profile-{svg_path.stem}",
                    f"--screenshot={png_path}", html.as_uri()],
                   check=True, capture_output=True, timeout=60)
    if not png_path.exists():
        raise RuntimeError(f"Chrome wrote no PNG for {svg_path.name}")
    return png_path


def main(names):
    jobs = []
    for src, dst in SETS:
        wanted = sorted(p for p in src.glob("*.svg") if not names or p.stem in names)
        if not names:
            for old in dst.glob("*.png"):
                if not (src / f"{old.stem}.svg").exists():
                    old.unlink()
        jobs += [(p, dst / f"{p.stem}.png") for p in wanted]
    with tempfile.TemporaryDirectory() as work:
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            for done in pool.map(lambda job: render(job[0], job[1], work), jobs):
                print(done.relative_to(ROOT))
    print(f"rendered {len(jobs)} references")
    return 0


if __name__ == "__main__":
    sys.exit(main(set(sys.argv[1:])))
```

- [ ] **Step 4: Exclude the reference folders from the test targets**

File: `Package.swift`

```swift
// swift-tools-version: 6.0
// MIT licence: see LICENSE.
import PackageDescription

/// The one place the deployment floor is set (spec section 4).
let minimumMacOS: SupportedPlatform = .macOS(.v14)

let package = Package(
    name: "symbiotic-design",
    platforms: [minimumMacOS],
    products: [
        .library(name: "SymbioticTokens", targets: ["SymbioticTokens"]),
        .library(name: "SymbioticIcons", targets: ["SymbioticIcons"]),
        .library(name: "SymbioticBrand", targets: ["SymbioticBrand"]),
    ],
    targets: [
        .target(name: "SymbioticTokens"),
        .target(name: "SymbioticIcons", dependencies: ["SymbioticTokens"]),
        .target(name: "SymbioticBrand", dependencies: ["SymbioticIcons"]),
        .testTarget(name: "SymbioticTokensTests", dependencies: ["SymbioticTokens"]),
        .testTarget(name: "SymbioticIconsTests", dependencies: ["SymbioticIcons", "SymbioticTokens"], exclude: ["References"]),
        .testTarget(name: "SymbioticBrandTests", dependencies: ["SymbioticBrand", "SymbioticTokens"], exclude: ["References"]),
    ]
)
```

- [ ] **Step 5: Render the references**

Run:

```bash
export DEVELOPER_DIR=/Library/Developer/CommandLineTools PYTHONDONTWRITEBYTECODE=1
python3 tools/references.py | tail -1
ls Tests/SymbioticIconsTests/References | wc -l
ls Tests/SymbioticBrandTests/References | wc -l
```

Expected: `rendered 147 references`, then `106` and `41`. (Chrome may print `CVDisplayLinkCreateWithCGDisplay failed` to stderr; it is harmless and captured.)

- [ ] **Step 6: Run all tests to verify they pass**

Run:

```bash
export DEVELOPER_DIR=/Library/Developer/CommandLineTools PYTHONDONTWRITEBYTECODE=1
python3 -m unittest discover -s tools/tests 2>&1 | tail -3
scripts/swift.sh test 2>&1 | grep -E '✘|Test run with'
```

Expected: Python `Ran 113 tests`, `OK`; `✔ Test run with 25 tests in 6 suites passed`; no `✘`. If an icon fails, its message prints the mean difference: compare `icons/standard/<name>.svg` with the generated literal before touching the tolerance.

- [ ] **Step 7: Commit**

Run:

```bash
export DEVELOPER_DIR=/Library/Developer/CommandLineTools PYTHONDONTWRITEBYTECODE=1
git add Package.swift \
  tools/references.py \
  tools/tests/test_references.py \
  Tests/SymbioticIconsTests/FidelityTests.swift \
  Tests/SymbioticIconsTests/References \
  Tests/SymbioticBrandTests/BrandFidelityTests.swift \
  Tests/SymbioticBrandTests/References
git status --short
git commit -q -F - <<'MSG'
Fidelity: headless-Chrome references and 48 px comparison tests

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01F7df6grqTdqHgc2d2X359P
MSG
git status --short
```

Expected: `git status --short` before the commit lists only the paths above (no `.DS_Store`, no `__pycache__`); after the commit it prints nothing.

### Task 9: CI workflow, README and handoff

CI regenerates and fails on any difference, then runs the Python and Swift tests on a macOS runner. The README documents the products, the licence split, the API and the regeneration workflow; `HANDOFF.md` tells EG13 which roles answer its requests.

**Files:**
- Create: `.github/workflows/ci.yml`
- Modify: `README.md` (full replacement), `HANDOFF.md` (append a section)

**Interfaces:**
- Consumes: `tools/generate.py`, `scripts/swift.sh`, the test suites (Tasks 1–8).
- Produces: nothing code depends on.

- [ ] **Step 1: Write the workflow**

File: `.github/workflows/ci.yml`

```yaml
# MIT licence: see LICENSE.
name: CI

on:
  push:
  pull_request:

jobs:
  check:
    runs-on: macos-15
    steps:
      - uses: actions/checkout@v4

      - name: Generated files match the sources
        run: |
          python3 tools/generate.py
          git status --porcelain
          test -z "$(git status --porcelain)"

      - name: Python tests
        run: python3 -m unittest discover -s tools/tests -v

      - name: Swift build and tests
        run: |
          scripts/swift.sh build
          scripts/swift.sh test
```

- [ ] **Step 2: Rewrite the README**

File: `README.md`

````markdown
# symbiotic-design

A design library for SymbioticAudio apps — the shared design language of
VizDAW and EG13: design tokens, icons and a Swift package that draws them.

## Licences (two of them)

- **Code, design tokens and the standard icon set** (`icons/standard/`):
  MIT — see `LICENSE`.
- **Branded artwork** (`source-art/`, `icons/svg/glyph-*`, the logo and
  anything rendered from them): **all rights reserved** — see
  `ASSETS-LICENSE`. Public visibility grants no rights to reuse it. This
  includes the `SymbioticBrand` product (`Sources/SymbioticBrand/`, every file
  of which starts with the `ASSETS-LICENSE` notice) and the glyph reference
  renders in `Tests/SymbioticBrandTests/References/`.

## Swift package

Add `https://github.com/SymbioticAudio/symbiotic-design` (pin a version tag),
macOS 14 or later. Three products:

| Product | Licence | What it gives you |
|---|---|---|
| `SymbioticTokens` | MIT | `Theme` with typed groups (`theme.meter.clip.color`, `theme.spacing.m`, `theme.type.body.font`), `Theme.classicLight`, `.studioDark`, `.flat`, `.console`, `Theme.all`, and the SwiftUI environment value `\.symbioticTheme` |
| `SymbioticIcons` | MIT | the standard icons as drawing code, `IconRole`, `Icon(_:size:)` (SwiftUI), `NSImage.icon(_:size:)` (template image), `Icons.register(_:)` |
| `SymbioticBrand` | all rights reserved | the owner's glyphs and logo as drawing code, and `SymbioticBrand.provider` |

```swift
import SymbioticIcons
#if canImport(SymbioticBrand)
import SymbioticBrand
#endif

// once, at launch
#if canImport(SymbioticBrand)
Icons.register(SymbioticBrand.provider)
#endif

// anywhere
Icon(.transportPlay, size: 16)                 // SwiftUI, current foreground style
NSImage.icon(.modeLoop, size: 16)              // AppKit template image
```

A role draws its brand glyph when the brand provider is registered and maps
that role, otherwise its standard icon. `brand.logo` without the provider is
the text wordmark "SymbioticAudio". A fork removes only the `SymbioticBrand`
dependency and still has a complete icon set. The package ships no resource
files, so it works inside plugin bundles.

Icons are drawn on their 24-unit grid scaled to the requested size; the
stroke width comes from the theme's `iconStroke` token for that size
(`s16`, `s24`, `s32`, interpolated between them and proportional outside).

## Sources and generated files

| Source | Generated from it |
|---|---|
| `tokens/tokens.json` | `Sources/SymbioticTokens/Generated/`, `tokens/contrast.md` |
| `icons/standard/*.svg`, `icons/standard.json` | `Sources/SymbioticIcons/Generated/StandardIcon+Generated.swift` |
| `icons/roles.json` | `Sources/SymbioticIcons/Generated/IconRole+Generated.swift`, `icons/coverage.md` |
| `icons/svg/glyph-*.svg`, `icons/glyphs.json` | `Sources/SymbioticBrand/Generated/` |

After changing a source:

```bash
python3 tools/generate.py              # validate and regenerate (stdlib Python 3 only)
python3 tools/references.py            # only if an SVG changed: reference PNGs (headless Chrome)
python3 -m unittest discover -s tools/tests
scripts/swift.sh test                  # Command Line Tools: export DEVELOPER_DIR=/Library/Developer/CommandLineTools first
```

Generated Swift is committed; apps never run the generator. CI regenerates
and fails on any difference.

- `tokens/contrast.md` lists each text/surface pair declared in
  `tokens.json` against WCAG AA per theme; warnings do not fail the build.
- `icons/coverage.md` is the designer's brief: roles with no brand glyph,
  standard icons still to draw, and glyphs not yet assigned to a role.
- The SVG subset the generator accepts is listed in
  `docs/superpowers/specs/2026-10-20-design-system-design.md` §3.1; anything
  else is an error.

## Contents

- `source-art/` — the master glyph artwork (Photoshop).
- `icons/` — the glyphs as 24-unit monoline SVGs, their roles
  (`glyphs.json`), the role catalogue (`roles.json`) and a contact sheet.
- `icons/standard/` — 106 standard icons (transport, edit, app, audio,
  editor, notation) drawn in the same house style, MIT-licensed; index in
  `icons/standard.json`.
- `tokens/` — design tokens for the four themes (`classic-light`,
  `studio-dark`, and the placeholder palettes `flat` and `console`).
- `tools/` — the generator, the reference renderer and
  `contact_sheet.py` (rebuilds `icons/contact-sheet.html`).
- `HANDOFF.md` — status and requests between the app projects.

## Special thanks

Special thanks to **Clayton Hibbert** for the original glyph designs.
````

- [ ] **Step 3: Append the status to HANDOFF.md**

Append to `HANDOFF.md`:

```markdown

## Status: Swift package (2026-10-20)
The package is in this repo: products `SymbioticTokens`, `SymbioticIcons` and `SymbioticBrand` (macOS 14+, swift-tools 6.0); see README.md. EG13's icon requests above are roles in `icons/roles.json` (`part.a`, `part.b`, `part.layer`, `part.split`, `part.multi`, `voice.poly`, `voice.mono`, `voice.legato`, `audio.mono`, `audio.stereo`, `slot.source`, `slot.filter`, `slot.shaper`, `slot.fx`, `slot.modulation`, `control.tempo-sync`, `control.midi-learn`, `edit.random`, `routing.add-route`, `routing.remove-route`, `routing.via`, `mixer.bypass`, `mixer.power`, `preset.save`, `preset.browse`, `preset.previous`, `preset.next`, `preset.init`, `app.settings`, `app.about`), each with a standard icon. The control styling requests (knob, slider, XY pad, meters…) are covered by tokens (`control`, `meter`, `graph`, `strip`, `spacing`, `radius`); the short visual guide is still to come. Request new roles here; `icons/coverage.md` is the designer's brief.
```

- [ ] **Step 4: Commit**

Run:

```bash
export DEVELOPER_DIR=/Library/Developer/CommandLineTools PYTHONDONTWRITEBYTECODE=1
git add .github/workflows/ci.yml \
  README.md \
  HANDOFF.md
git status --short
git commit -q -F - <<'MSG'
CI, README and handoff for the Swift package

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01F7df6grqTdqHgc2d2X359P
MSG
git status --short
```

Expected: `git status --short` before the commit lists only the paths above (no `.DS_Store`, no `__pycache__`); after the commit it prints nothing.

- [ ] **Step 5: Rehearse the CI job locally**

Run:

```bash
export DEVELOPER_DIR=/Library/Developer/CommandLineTools PYTHONDONTWRITEBYTECODE=1
python3 tools/generate.py > /dev/null && test -z "$(git status --porcelain)" && echo clean
python3 -m unittest discover -s tools/tests 2>&1 | tail -1
scripts/swift.sh build 2>&1 | grep -v deprecated | tail -1
scripts/swift.sh test 2>&1 | grep -E '✘|Test run with'
git log --oneline -10
```

Expected: `clean`, `OK`, `Build complete!`, `✔ Test run with 25 tests in 6 suites passed`, and the nine task commits on top of the plan commit. Do not push or tag.

## Self-Review

**Spec coverage.**
- §2.1 token source, refusal on missing/unknown tokens → Tasks 2–3 (`validate`, `test_missing_token_fails_and_writes_nothing`).
- §2.2 neutral theme IDs → Task 2 (`THEME_ID`, repository test).
- §2.3 all twelve groups with the listed names → Task 2 (`test_spec_groups_are_present`), Task 3 (`everyTokenResolves`).
- §2.4 hex and `{system, fallback}` values, starter/placeholder palettes → Task 2; Ruling 2.
- §2.5 typed `Theme`, `Color` + `NSColor`, statics, `Theme.all`, `\.symbioticTheme` default by appearance → Task 3.
- §2.6 completeness, unknown keys, malformed values, contrast warnings in output and `tokens/contrast.md` → Tasks 2–3.
- §3.1 SVG subset incl. arcs, all path commands, transforms, error on anything else → Task 1.
- §3.2 `roles.json` (`id`, `standard` required except `brand.logo`, `brand`, `label`), VizDAW current + SP5–SP7 + EG13 roles, the 12 confirmed glyphs, logo → wordmark → Tasks 4, 6.
- §3.3 coverage report sections → Task 4; in-house drawing of missing icons → Task 5.
- §3.4 `IconRole` compile-time roles, `Icon(_:size:)` with theme stroke and foreground colour, `NSImage.icon` template, `Icons.register`, brand product with notice, dependency direction, resolution order, guarded registration, stroke not scaled, no resources → Tasks 6–7.
- §4 layout, generator, `references.py`, committed generated code, Command Line Tools, macOS 14 floor → Tasks 3–8.
- §5 Python tests, fidelity at 48 px with a stated tolerance, behaviour tests, CI → Tasks 1–9.
- §6 versioning: no tags or pushes (Global Constraints); tagging `0.1.0` is the owner's call after review.

**Placeholder scan.** Every code step carries the full file; the only scripted content (Task 5's icon script) carries every coordinate. No "TBD", "similar to", or unshown helpers.

**Type consistency.** Checked across tasks: `IconDrawing.draw(in:size:strokeWidth:)`, `IconBitmap.alpha(of:size:strokeWidth:)`, `IconResolver.resolve(_:)`, `Theme.IconStrokeMetrics.width(forSize:)`, `drawings_enum(type_name, cases, header, imports)`, `rolelib.validate(data, glyphs)`, `swiftgen_*.OUT` constants and `generate.py` step functions match their producers.

**Review Focus.** Each of the five items has its test in the owning task (named in the section).

**Verification of this plan.** Replayed task by task on a scratch worktree of the commit before this plan, extracting every file and command from this document: all Python suites, `scripts/swift.sh build`, `scripts/swift.sh test` and the generator pass at the end of each task, and the final regenerate-and-diff is clean.
