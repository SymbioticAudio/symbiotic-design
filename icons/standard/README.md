# Standard icons

Standard icons — MIT (see ../../LICENSE). Generic conventional symbols drawn for SymbioticAudio in the house style.

107 icons in six categories (`transport`, `edit`, `app`, `audio`, `editor`, `notation`), one file per icon:
`<name>.svg`. The index with names, categories and descriptions is `../standard.json`.
Every shape was drawn fresh from the convention; none is copied or derived from
another icon library or from the branded glyphs in `../svg/` (which are all rights
reserved and are not part of this set).

## Style rules (same as the glyphs)

| Rule | Value |
|---|---|
| Canvas | `viewBox="0 0 24 24"`, `width`/`height` 24 |
| Stroke | `stroke="currentColor"`, `fill="none"`, `stroke-width="1.2"` on the root only |
| Caps / joins | `stroke-linecap="butt"`, `stroke-linejoin="miter"` (default miter limit 4) |
| Primitives | `line`, `polyline`, `polygon`, `circle`, `path` (with `A` arcs or `C` curves). Strokes, not outlined fills. |
| Solid marks | Only where the convention needs a filled mark: `fill="currentColor" stroke="none"` (record dot, pips, info/warning dots, the dots in `more`, `count-in` and the punch icons, MIDI pins). `record-outline` is the unfilled alternative to `record`. |
| Live area | Ink, including half the stroke, inside 1.5 to 22.5 |
| Optical size | Main ink about 12 to 17 units across, matching the glyphs (most are 14 to 17). |
| Alignment | Ink bounding box centred on (12, 12) |
| Coordinates | Rounded to 0.01 |

Root element, copied exactly into every file:

```
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2" stroke-linecap="butt" stroke-linejoin="miter">
```

Check new icons at 16, 24 and 32 px on light and dark backgrounds in `../contact-sheet.html`
(rebuild it with `python3 tools/contact_sheet.py`).
