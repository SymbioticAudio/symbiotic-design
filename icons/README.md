**Artwork © 2006–2026 Westlee Latta. All rights reserved — see ../ASSETS-LICENSE. Not covered by any open-source licence of the apps that use it.**

# Glyph icon set

41 monoline glyphs, redrawn as stroked vector SVGs from the designer's master sheet
(`Symbols_Large.psd`, 720×576, black on white; `Symbols 2 white.psd` is the same set
white on blue). Numbering runs row by row, left to right, starting at `glyph-01`
(rows hold 8, 7, 9, 7 and 10 glyphs).

```
svg/glyph-NN.svg     one file per glyph
glyphs.json          id, row, col, neutral description, suggested role, confidence
contact-sheet.html   every glyph at 96 px plus 16/24/32 px strips, in light and dark
```

## Drawing rules

| Rule | Value |
|---|---|
| Canvas | `viewBox="0 0 24 24"` (`width`/`height` 24) |
| Stroke | `stroke="currentColor"`, `fill="none"`, **`stroke-width="1.2"`** for every glyph |
| Caps / joins | `stroke-linecap="butt"`, `stroke-linejoin="miter"` (default miter limit 4), as in the source |
| Primitives | `circle`, `line`, `polyline`, `polygon`, and `path` with `A` arcs or `C` curves. Strokes only, no outlined fills. A filled dot would use `fill="currentColor" stroke="none"`; none of the current glyphs need one. |
| Live area | 1.5 units of padding on every side: ink, including half the stroke, stays inside 1.5 to 22.5 |
| Alignment | Each glyph's ink bounding box is centred on (12, 12) |
| Coordinates | Rounded to 0.01 |

### Scale and stroke width

In the source, the stroke is 4 px. The glyphs are typically 45 to 65 px across, and the
largest is about 80 px. All glyphs share one scale, **0.3 units per source px**, which turns
the 4 px stroke into **1.2 units**. That keeps the stroke-to-size ratio and the relative
sizes of the glyphs the same as on the master sheet.

Eight glyphs would overflow the 21-unit live area at that scale: 01, 03, 09, 14, 30, 38,
39 and 41. Each is scaled down just enough to fit (0.25 to 0.30 units/px). They keep the
same 1.2 stroke, so they read up to about 18 % heavier than the rest. This was chosen over
using a different stroke width per glyph.

### Fidelity

Each glyph was fitted to the master artwork by maximising the overlap between a raster
of the drawn primitives and the source pixels. It was then rendered and checked by eye
against the source. These are redraws of the original geometry, not reinterpretations.
Where the source is slightly asymmetric, the asymmetry was kept.

Two glyphs differ between the masters. In the white-on-blue file, the ring in glyph-23
and the half-disc in glyph-24 are filled solid. The SVGs follow the black master, where
both are outlines.

## Adding a glyph

1. Draw it on the same 24×24 grid, using only stroked primitives with `stroke-width 1.2`,
   butt caps and miter joins. Keep the ink inside 1.5 to 22.5 and centre its bounding box
   on (12, 12).
2. If it comes from source artwork, use the same 0.3 units/px scale, so that a 4 px source
   stroke becomes 1.2. Scale it down only if it would overflow the live area.
3. Copy the root element exactly from an existing file:
   `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="butt" stroke-linejoin="miter">`.
   Put no colours or stroke widths on child elements.
4. Save it as `svg/glyph-NN.svg` using the next free number, and add a matching entry to
   `glyphs.json`.
5. Add a card for it to `contact-sheet.html`, and check it at 16, 24 and 32 px on light
   and dark backgrounds.
