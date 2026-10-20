"""Runs tools/generate.py on a scratch copy of the repository."""
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import swiftgen_common as c  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[2]
COPY = ["tools", "tokens", "icons", "Sources", "ASSETS-LICENSE"]


class Scratch(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.tmp.name)
        for name in COPY:
            src = ROOT / name
            if src.is_dir():
                shutil.copytree(src, self.root / name, ignore=shutil.ignore_patterns("__pycache__"))
            elif src.exists():
                shutil.copy2(src, self.root / name)

    def tearDown(self):
        self.tmp.cleanup()

    def run_generate(self):
        return subprocess.run([sys.executable, str(self.root / "tools" / "generate.py")],
                              capture_output=True, text=True)

    def snapshot(self):
        return {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*")
                if p.is_file() and "__pycache__" not in p.parts}

    def edit_json(self, rel, change):
        path = self.root / rel
        data = json.loads(path.read_text(encoding="utf-8"))
        change(data)
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


class Tokens(Scratch):
    def test_committed_output_is_up_to_date(self):
        before = self.snapshot()
        result = self.run_generate()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.snapshot(), before, "run python3 tools/generate.py and commit the result")

    def test_contrast_warnings_are_printed_not_fatal(self):
        def lower_contrast(d):
            d["themes"][0]["values"]["text"]["primary"] = "#EEEEEE"
        self.edit_json("tokens/tokens.json", lower_contrast)
        result = self.run_generate()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("warning: classic-light: text.primary on surface.window", result.stdout)
        self.assertIn("| `text.primary` | `surface.window` | body |",
                      (self.root / "tokens" / "contrast.md").read_text(encoding="utf-8"))

    def test_missing_token_fails_and_writes_nothing(self):
        def drop(d):
            del d["themes"][2]["values"]["meter"]["clip"]
        self.edit_json("tokens/tokens.json", drop)
        before = self.snapshot()
        result = self.run_generate()
        self.assertEqual(result.returncode, 1)
        self.assertIn("error: tokens.json: theme flat lacks meter.clip", result.stderr)
        self.assertEqual(self.snapshot(), before)

    def test_stale_generated_files_are_removed(self):
        stale = self.root / "Sources" / "SymbioticTokens" / "Generated" / "Old.swift"
        stale.write_text("// old\n", encoding="utf-8")
        self.assertEqual(self.run_generate().returncode, 0)
        self.assertFalse(stale.exists())

    def test_theme_all_follows_the_theme_list(self):
        """No theme count is built in: a theme added to tokens.json appears in Theme.all."""
        def add_theme(d):
            extra = json.loads(json.dumps(d["themes"][0]))
            extra["id"] = "extra-test"
            d["themes"].append(extra)
            ids.extend(t["id"] for t in d["themes"])
        ids = []
        self.edit_json("tokens/tokens.json", add_theme)
        self.assertEqual(self.run_generate().returncode, 0)
        text = (self.root / "Sources" / "SymbioticTokens" / "Generated" / "Theme+Generated.swift").read_text(
            encoding="utf-8")
        listed = ", ".join(f".{c.lower_camel(i)}" for i in ids)
        self.assertIn(f"    public static let all: [Theme] = [{listed}]\n", text)
        self.assertIn("## extra-test", (self.root / "tokens" / "contrast.md").read_text(encoding="utf-8"))

    def test_constant_system_colour_fails_and_writes_nothing(self):
        def system_gold(d):
            for theme in d["themes"]:
                theme["values"]["brand"]["gold"] = {"system": "systemYellow", "fallback": "#EFC031"}
        self.edit_json("tokens/tokens.json", system_gold)
        before = self.snapshot()
        result = self.run_generate()
        self.assertEqual(result.returncode, 1)
        self.assertIn("error: tokens.json: brand.gold: brand is constant", result.stderr)
        self.assertEqual(self.snapshot(), before)


class Roles(Scratch):
    def test_coverage_report_is_written(self):
        (self.root / "icons" / "coverage.md").unlink()
        result = self.run_generate()
        self.assertEqual(result.returncode, 0, result.stderr)
        text = (self.root / "icons" / "coverage.md").read_text(encoding="utf-8")
        self.assertIn("## Brief for the designer", text)
        self.assertIn("## Glyphs not assigned to any role", text)

    def test_unconfirmed_glyph_is_rejected(self):
        def map_guess(d):
            d["roles"].append({"id": "net.wireless", "standard": "play", "brand": "glyph-06", "label": "Wireless"})
        self.edit_json("icons/roles.json", map_guess)
        result = self.run_generate()
        self.assertEqual(result.returncode, 1)
        self.assertIn("glyph-06 is not confirmed by the owner", result.stderr)

    def test_designer_name_error_names_glyphs_json(self):
        def bad(d):
            d[0]["designerName"] = "a\nb"
        self.edit_json("icons/glyphs.json", bad)
        result = self.run_generate()
        self.assertEqual(result.returncode, 1)
        self.assertIn("error: glyphs.json: glyph-01: designerName", result.stderr)
        self.assertNotIn("roles.json: glyphs.json", result.stderr)
