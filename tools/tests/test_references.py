import pathlib
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

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


class Retry(unittest.TestCase):
    PNG = b"\x89PNG\r\n\x1a\n" + b"body" + b"IEND\xaeB`\x82"

    def _fake_chrome(self, failures, exc):
        calls = []

        def run(cmd, **kwargs):
            calls.append(cmd)
            if len(calls) <= failures:
                raise exc(cmd)
            shot = next(a for a in cmd if a.startswith("--screenshot="))
            pathlib.Path(shot.split("=", 1)[1]).write_bytes(self.PNG)
            return subprocess.CompletedProcess(cmd, 0)
        return run, calls

    def _render(self, failures, exc, attempts=3):
        run, calls = self._fake_chrome(failures, exc)
        with tempfile.TemporaryDirectory() as work, mock.patch.object(r.subprocess, "run", run):
            png = pathlib.Path(work) / "out" / "play.png"
            r.render(ROOT / "icons" / "standard" / "play.svg", png, work, attempts=attempts)
            return png.read_bytes(), len(calls)

    def test_a_non_zero_chrome_exit_is_retried(self):
        data, calls = self._render(1, lambda cmd: subprocess.CalledProcessError(1, cmd))
        self.assertEqual(data, self.PNG)
        self.assertEqual(calls, 2)

    def test_a_timeout_is_retried(self):
        data, calls = self._render(2, lambda cmd: subprocess.TimeoutExpired(cmd, 60))
        self.assertEqual(data, self.PNG)
        self.assertEqual(calls, 3)

    def test_gives_up_after_the_attempts(self):
        with self.assertRaises(RuntimeError):
            self._render(3, lambda cmd: subprocess.CalledProcessError(1, cmd))


if __name__ == "__main__":
    unittest.main()
