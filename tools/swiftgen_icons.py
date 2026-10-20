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
