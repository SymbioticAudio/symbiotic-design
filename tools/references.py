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


def _complete_png(path):
    data = path.read_bytes() if path.exists() else b""
    return data[:8] == b"\x89PNG\r\n\x1a\n" and data.endswith(b"IEND\xaeB`\x82")


def render(svg_path, png_path, work, attempts=3):
    html = pathlib.Path(work) / f"{svg_path.stem}.html"
    html.write_text(page_for(svg_path.read_text(encoding="utf-8")), encoding="utf-8")
    png_path.parent.mkdir(parents=True, exist_ok=True)
    for attempt in range(attempts):
        png_path.unlink(missing_ok=True)
        try:
            subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                            "--no-first-run", "--no-default-browser-check",
                            "--force-device-scale-factor=1", "--default-background-color=00000000",
                            f"--window-size={SIZE},{SIZE}",
                            f"--user-data-dir={work}/profile-{svg_path.stem}-{attempt}",
                            f"--screenshot={png_path}", html.as_uri()],
                           check=True, capture_output=True, timeout=60)
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
            # Chrome sometimes writes the screenshot and then fails to exit
            # (subprocess.run has killed it) or exits non-zero. Keep the PNG
            # if it is complete; otherwise try again.
            pass
        if _complete_png(png_path):
            return png_path
    raise RuntimeError(f"Chrome wrote no PNG for {svg_path.name} in {attempts} attempts")


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
