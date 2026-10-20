import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import references as r  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[2]


class Page(unittest.TestCase):
    def test_page_draws_the_svg_at_48_px_in_black_on_transparent(self):
        svg = (ROOT / "icons" / "standard" / "play.svg").read_text(encoding="utf-8")
        page = r.page_for(svg)
        self.assertIn('width="48" height="48"', page)
        self.assertIn("background:transparent", page)
        self.assertIn("color:#000", page)

    def test_root_without_24_px_size_is_rejected(self):
        with self.assertRaises(ValueError):
            r.page_for('<svg viewBox="0 0 24 24"><line x1="0" y1="0" x2="1" y2="1"/></svg>')


class References(unittest.TestCase):
    def test_every_icon_has_a_48_px_reference(self):
        for src, dst in r.SETS:
            for svg in sorted(src.glob("*.svg")):
                with self.subTest(svg.name):
                    data = (dst / f"{svg.stem}.png").read_bytes()
                    self.assertEqual(data[:8], b"\x89PNG\r\n\x1a\n")
                    self.assertEqual((int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big")), (48, 48))


if __name__ == "__main__":
    unittest.main()
