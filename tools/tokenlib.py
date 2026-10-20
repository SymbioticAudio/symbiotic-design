"""Design token file: validation and WCAG contrast (spec section 2)."""
import itertools
import json
import math
import re
import unicodedata

KINDS = {"color", "points", "font"}
APPEARANCES = {"light", "dark"}
USES = {"body": 4.5, "large": 3.0, "icon": 3.0}
WEIGHTS = ["ultraLight", "thin", "light", "regular", "medium", "semibold", "bold", "heavy", "black"]
# Always used with fullmatch: `$` would also accept a trailing newline.
NAME = re.compile(r"[a-z][A-Za-z0-9]*")
THEME_ID = re.compile(r"[a-z][a-z0-9]*(-[a-z0-9]+)*")
HEX = re.compile(r"#[0-9A-Fa-f]{6}([0-9A-Fa-f]{2})?")

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


def _one_line(text):
    """Non-blank text with no line breaks, tabs or other control characters.

    Descriptions and notes end up in generated Swift comments and string
    literals, where a newline would turn the rest of the text into code.
    """
    return (isinstance(text, str) and bool(text.strip())
            and not any(unicodedata.category(ch) in ("Cc", "Zl", "Zp") for ch in text))


def _is_number(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _check_value(kind, value):
    """Return None if value is valid for kind, else a short reason."""
    if kind == "color":
        if isinstance(value, str):
            return None if HEX.fullmatch(value) else f"not #RRGGBB or #RRGGBBAA: {value!r}"
        if isinstance(value, dict):
            if set(value) != {"system", "fallback"}:
                return "a system colour needs exactly 'system' and 'fallback'"
            if value["system"] not in SYSTEM_COLORS:
                return f"unknown macOS system colour {value['system']!r}"
            if not isinstance(value["fallback"], str) or not HEX.fullmatch(value["fallback"]):
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
    constant = set()  # groups whose values must be the same in every theme
    for group, spec in groups.items():
        if not NAME.fullmatch(group):
            problems.append(f"token group name {group!r} must be lowerCamelCase")
        if not isinstance(spec, dict) or not {"kind", "items"} <= set(spec) <= {"kind", "items", "constant"}:
            problems.append(f"token group {group!r} needs 'kind' and 'items' (and optionally 'constant')")
            continue
        if not isinstance(spec.get("constant", False), bool):
            problems.append(f"token group {group!r}: constant must be true or false")
        elif spec.get("constant"):
            constant.add(group)
        if spec["kind"] not in KINDS:
            problems.append(f"token group {group!r}: kind {spec['kind']!r} not one of color, points, font")
        if not isinstance(spec["items"], dict) or not spec["items"]:
            problems.append(f"token group {group!r}: 'items' must be a non-empty object")
            continue
        for name, desc in spec["items"].items():
            if not NAME.fullmatch(name):
                problems.append(f"token {group}.{name}: name must be lowerCamelCase")
            if not _one_line(desc):
                problems.append(f"token {group}.{name}: needs a one-line description")
            kinds[f"{group}.{name}"] = spec["kind"]
    themes = data.get("themes")
    if not isinstance(themes, list) or not themes:
        raise TokenError(problems + ["'themes' must be a non-empty list"])
    seen = set()
    first_constants = {}  # token -> (theme id, value) from the first theme that defines it
    for i, theme in enumerate(themes):
        if not isinstance(theme, dict):
            problems.append(f"themes[{i}] must be an object")
            continue
        tid = theme.get("id", f"themes[{i}]")
        for key in sorted(set(theme) - {"id", "appearance", "placeholder", "note", "values"}):
            problems.append(f"theme {tid}: unknown key {key!r}")
        if not isinstance(tid, str) or not THEME_ID.fullmatch(tid):
            problems.append(f"theme id {tid!r} must be lower-case words joined by hyphens")
        elif tid in seen:
            problems.append(f"theme id {tid!r} is used twice")
        seen.add(tid)
        if theme.get("appearance") not in APPEARANCES:
            problems.append(f"theme {tid}: appearance must be light or dark")
        if not isinstance(theme.get("placeholder", False), bool):
            problems.append(f"theme {tid}: placeholder must be true or false")
        if "note" in theme and not _one_line(theme["note"]):
            problems.append(f"theme {tid}: note must be one line of text")
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
                continue
            group = token.split(".", 1)[0]
            if group in constant:
                if token not in first_constants:
                    first_constants[token] = (tid, value)
                elif value != first_constants[token][1]:
                    origin, expected = first_constants[token]
                    problems.append(f"theme {tid}, {token}: {group} is constant, so it must equal theme "
                                    f"{origin}'s value {expected!r}")
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
