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
        """Root element, paint, rounding, live area and centring for every icon.

        Advisory limit (pre-flight M6): svgsubset.bounds pads each point by half
        the stroke only, so the live-area check ignores miter tips at sharp
        joins and square caps. Those are checked by eye on the contact sheet.
        """
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
