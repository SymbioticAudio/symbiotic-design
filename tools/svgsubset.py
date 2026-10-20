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
        elif name in ("skewX", "skewY"):
            raise SvgError("transform: only translate, rotate, uniform scale and mirror "
                           "are supported (no skew or non-uniform scale)")
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
        if not ops and cmd not in ("M", "m"):
            raise SvgError(f"path: data must start with a moveto (M or m): {d!r}")
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
    return _reopen_after_close(ops)


def _reopen_after_close(ops):
    """SVG: a drawing command after Z starts a new subpath at the closed one's start."""
    out = []
    start = None
    closed = False
    for op in ops:
        if op[0] == "M":
            start, closed = (op[1], op[2]), False
        elif op[0] == "Z":
            closed = True
        elif closed and start is not None:
            out.append(("M",) + start)
            closed = False
        out.append(op)
    return out


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


def _attr_num(el, name, tag, default=None, non_negative=False):
    if name not in el.attrib:
        if default is None:
            raise SvgError(f"<{tag}> needs {name}")
        return default
    v = _num(el.attrib[name], f"<{tag}> {name}")
    if non_negative and v < 0:
        raise SvgError(f"<{tag}> {name} must not be negative")
    return v


def _element_ops(el, tag):
    a = el.attrib
    if tag == "line":
        return [("M", _attr_num(el, "x1", tag, 0.0), _attr_num(el, "y1", tag, 0.0)),
                ("L", _attr_num(el, "x2", tag, 0.0), _attr_num(el, "y2", tag, 0.0))]
    if tag == "circle":
        r = _attr_num(el, "r", tag, non_negative=True)
        if r == 0:
            return []
        return _ellipse_ops(_attr_num(el, "cx", tag, 0.0), _attr_num(el, "cy", tag, 0.0), r, r)
    if tag == "ellipse":
        erx, ery = _attr_num(el, "rx", tag, non_negative=True), _attr_num(el, "ry", tag, non_negative=True)
        if erx == 0 or ery == 0:
            return []
        return _ellipse_ops(_attr_num(el, "cx", tag, 0.0), _attr_num(el, "cy", tag, 0.0), erx, ery)
    if tag == "rect":
        w = _attr_num(el, "width", tag, non_negative=True)
        h = _attr_num(el, "height", tag, non_negative=True)
        if w == 0 or h == 0:
            return []
        rx = a.get("rx")
        ry = a.get("ry")
        rxv = _attr_num(el, "rx", tag, non_negative=True) if rx is not None else None
        ryv = _attr_num(el, "ry", tag, non_negative=True) if ry is not None else None
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
        if (child.tail or "").strip():
            raise SvgError(f"text after <{tag}> is not supported")
        s = _style(child, style, tag)
        if tag == "g":
            m = matrix
            if "transform" in child.attrib:
                m = multiply(matrix, parse_transform(child.attrib["transform"]))
                a, b, c, d = m[:4]
                if abs(a * a + b * b - (c * c + d * d)) >= 1e-9 or abs(a * c + b * d) >= 1e-9:
                    raise SvgError("transform: only translate, rotate, uniform scale and mirror "
                                   "are supported (no skew or non-uniform scale)")
                if abs(a * d - b * c) < 1e-12:
                    raise SvgError("transform: degenerate (zero scale collapses the drawing)")
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
