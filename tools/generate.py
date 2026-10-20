#!/usr/bin/env python3
"""Validate the design sources and write every generated file.

Usage: python3 tools/generate.py
Writes tokens/contrast.md, icons/coverage.md and Sources/*/Generated/, and
restamps the ASSETS-LICENSE notice at the top of hand-written Swift under
Sources/SymbioticBrand/ and Tests/SymbioticBrandTests/ (any depth).
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
        for path in swiftgen_brand.stamped_sources(ROOT):
            rel = path.relative_to(ROOT).as_posix()
            if rel.startswith(swiftgen_brand.OUT + "/"):
                continue
            try:
                files[rel] = swiftgen_brand.restamp(path.read_text(encoding="utf-8"), assets_license)
            except ValueError as e:
                raise svgsubset.SvgError(f"{rel}: {e}") from None
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
            source = "" if p.startswith("glyphs.json:") else "roles.json: "
            print(f"error: {source}{p}", file=sys.stderr)
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
