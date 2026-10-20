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
            source = "" if p.startswith("glyphs.json:") else "roles.json: "
            print(f"error: {source}{p}", file=sys.stderr)
        return 1
    for rid, name in missing:
        print(f"note: role {rid} needs icons/standard/{name}.svg (listed in icons/coverage.md)")
    files = {**token_files, **icon_files}
    write_tree(files, token_dirs)
    print(f"wrote {len(files)} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
