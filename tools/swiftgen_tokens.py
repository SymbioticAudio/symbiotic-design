"""tokens.json -> Swift source for the SymbioticTokens product (spec section 2.5)."""
from swiftgen_common import MIT_HEADER, identifier, lower_camel, number, string_literal, upper_camel
from tokenlib import SYSTEM_COLORS, TokenError, flat_values

OUT = "Sources/SymbioticTokens/Generated"
SUFFIX = {"color": "Colors", "points": "Metrics", "font": "Styles"}
SWIFT_TYPE = {"color": "ThemeColor", "points": "CGFloat", "font": "TypeStyle"}


def struct_name(group, kind):
    return upper_camel(group) + SUFFIX[kind]


def namespace_name(group):
    """The Theme-independent namespace of a constant group: brand -> Brand."""
    return upper_camel(group)


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


def initialiser(fields, indent, pinned=()):
    """A public memberwise init over [(name, type, default or None)].

    Fields named in `pinned` are colour groups, stored with their system colours
    resolved in the init's `appearance` parameter (review M3).
    """
    pad = " " * indent
    params = ",\n".join(f"{pad}    {identifier(n)}: {t}" + (f" = {d}" if d is not None else "")
                        for n, t, d in fields)
    body = "".join(f"{pad}    self.{identifier(n)} = {identifier(n)}"
                   + (".pinned(to: appearance)" if n in pinned else "") + "\n" for n, _, _ in fields)
    return [f"{pad}public init(\n{params}\n{pad}) {{\n{body}{pad}}}"]


def pinned_method(group, spec):
    """`func pinned(to:)` for a colour group: the same colours, system ones resolved in `appearance`."""
    name = struct_name(group, spec["kind"])
    args = ",\n".join(f"                {identifier(n)}: self.{identifier(n)}.pinned(to: appearance)"
                      for n in spec["items"])
    return ["        /// The same colours, with every system colour resolved in `appearance`.",
            f"        public func pinned(to appearance: ThemeAppearance) -> {name} {{",
            f"            {name}(\n{args}\n            )",
            "        }"]


# Top-level names a constant group's namespace must not take: this module's own types,
# the modules of this package and the ones it imports, and common SwiftUI/AppKit/Swift types.
RESERVED_TOP_LEVEL = {
    "Theme", "ThemeColor", "ThemeAppearance", "TypeStyle", "FontWeight", "SystemColorName",
    "SymbioticTokens", "SymbioticIcons", "SymbioticBrand", "SwiftUI", "AppKit", "CoreGraphics", "Foundation",
    "Swift", "Color", "Font", "View", "Text", "Image", "Shape", "Path", "Animation", "Environment",
    "EnvironmentValues", "ColorScheme", "NSColor", "NSFont", "NSImage", "NSAppearance", "NSView",
    "String", "Bool", "Int", "Double", "Float", "CGFloat", "Array", "Dictionary", "Set", "Optional",
}
# Theme members besides the groups and the theme statics.
THEME_MEMBERS = {"id", "appearance", "isPlaceholder", "all", "named", "standard", "init"}


def check_names(data):
    """Generated Swift names must not clash with each other or with existing ones (review M4)."""
    problems = []
    groups = data["tokens"]
    group_props = {lower_camel(g) for g in groups}
    for group, spec in groups.items():
        if lower_camel(group) in THEME_MEMBERS:
            problems.append(f"{group}: the group name clashes with Theme.{group}; rename the group")
        if spec.get("constant") and namespace_name(group) in RESERVED_TOP_LEVEL:
            problems.append(f"{group}: a constant group becomes the top-level Swift name "
                            f"{namespace_name(group)}, which is already used; rename the group")
    seen = set()
    for theme in data["themes"]:
        prop = lower_camel(theme["id"])
        if prop in THEME_MEMBERS or prop in group_props or prop in seen:
            problems.append(f"theme {theme['id']}: its Swift name Theme.{prop} clashes with another Theme "
                            "member; rename the theme")
        seen.add(prop)
    if problems:
        raise TokenError(problems)


def check_constants(data):
    """A constant group is also a Theme-independent namespace, so it cannot hold appearance-dependent values."""
    problems = []
    first = data["themes"][0]["values"]
    for group, spec in data["tokens"].items():
        if not spec.get("constant"):
            continue
        for name in spec["items"]:
            if isinstance(first[group][name], dict):
                problems.append(f"{group}.{name}: {group} is constant, so it needs a fixed colour, "
                                "not a system colour")
    if problems:
        raise TokenError(problems)


def theme_swift(data):
    groups = data["tokens"]
    fields = [(lower_camel(group), struct_name(group, spec["kind"]), None) for group, spec in groups.items()]
    lines = [MIT_HEADER, "import CoreGraphics", "", "/// One complete set of design tokens. Generated from tokens/tokens.json.",
             "///",
             "/// The built-in themes are the statics below; an app with its own visual identity",
             "/// can build its own value with the public initialisers.",
             "public struct Theme: Sendable, Hashable, Identifiable {",
             "    /// Neutral theme ID, e.g. \"classic-light\".",
             "    public let id: String",
             "    public let appearance: ThemeAppearance",
             "    /// True while the theme still has rough placeholder values (replaced in VizDAW SP7).",
             "    public let isPlaceholder: Bool"]
    for name, type_name, _ in fields:
        lines.append(f"    public let {identifier(name)}: {type_name}")
    lines.append("")
    colour_groups = {lower_camel(g) for g, spec in groups.items() if spec["kind"] == "color"}
    lines.append("    /// System colours in the colour groups are re-pinned to `appearance`, so the theme,")
    lines.append("    /// not where a colour was copied from, decides whether they resolve light or dark.")
    lines += initialiser([("id", "String", None), ("appearance", "ThemeAppearance", None),
                          ("isPlaceholder", "Bool", "false")] + fields, 4, pinned=colour_groups)
    lines.append("}")
    lines.append("")
    lines.append("extension Theme {")
    for group, spec in groups.items():
        kind = spec["kind"]
        lines.append(f"    public struct {struct_name(group, kind)}: Sendable, Hashable {{")
        for name, desc in spec["items"].items():
            lines.append(f"        /// {desc}")
            lines.append(f"        public let {identifier(name)}: {SWIFT_TYPE[kind]}")
        lines.append("")
        lines += initialiser([(name, SWIFT_TYPE[kind], None) for name in spec["items"]], 8)
        if kind == "color":
            lines.append("")
            lines += pinned_method(group, spec)
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
            if spec.get("constant"):
                ns = namespace_name(group)
                args = ",\n".join(f"            {identifier(name)}: {ns}.{identifier(name)}" for name in spec["items"])
            else:
                args = ",\n".join(
                    f"            {identifier(name)}: {value_literal(kind, values[f'{group}.{name}'], theme['appearance'])}"
                    for name in spec["items"])
            group_lines.append(f"        {identifier(lower_camel(group))}: {struct_name(group, kind)}(\n{args}\n        )")
        lines.append(",\n".join(group_lines))
        lines.append("    )")
        lines.append("")
    all_themes = ", ".join(f".{identifier(lower_camel(t['id']))}" for t in data["themes"])
    lines.append("    /// Every theme, in tokens.json order.")
    lines.append(f"    public static let all: [Theme] = [{all_themes}]")
    lines.append("}")
    first = flat_values(data["themes"][0])
    for group, spec in groups.items():
        if not spec.get("constant"):
            continue
        kind = spec["kind"]
        lines.append("")
        lines.append(f"/// Theme-independent tokens: the same in every theme (tokens.json group `{group}`).")
        lines.append(f"public enum {namespace_name(group)} {{")
        for name, desc in spec["items"].items():
            lines.append(f"    /// {desc}")
            lines.append(f"    public static let {identifier(name)}: {SWIFT_TYPE[kind]} = "
                         f"{value_literal(kind, first[f'{group}.{name}'], 'light')}")
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
    check_names(data)
    check_constants(data)
    return {
        f"{OUT}/Theme+Generated.swift": theme_swift(data),
        f"{OUT}/SystemColorName+Generated.swift": system_colors_swift(),
    }
