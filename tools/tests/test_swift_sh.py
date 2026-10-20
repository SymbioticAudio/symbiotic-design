"""scripts/swift.sh picks the Command Line Tools branch robustly (review M2)."""
import os
import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "swift.sh"
CLT = "/Library/Developer/CommandLineTools"


class SwiftScript(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.bin = pathlib.Path(self.tmp.name)
        # Stand-ins: `swift` prints its arguments; `xcode-select -p` prints $FAKE_XCODE_SELECT.
        self.stub("swift", 'echo "swift $*"')
        self.stub("xcode-select", '[ "$1" = "-p" ] && echo "$FAKE_XCODE_SELECT"')

    def tearDown(self):
        self.tmp.cleanup()

    def stub(self, name, body):
        path = self.bin / name
        path.write_text(f"#!/bin/sh\n{body}\n", encoding="utf-8")
        path.chmod(0o755)

    def run_script(self, developer_dir=None, xcode_select=""):
        env = {"PATH": f"{self.bin}:/usr/bin:/bin", "FAKE_XCODE_SELECT": xcode_select}
        if developer_dir is not None:
            env["DEVELOPER_DIR"] = developer_dir
        return subprocess.run(["/bin/bash", str(SCRIPT), "build"], capture_output=True, text=True, env=env)

    def assert_clt(self, result):
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--build-system native", result.stdout)
        self.assertIn("swift.sh: Command Line Tools", result.stderr)

    def assert_xcode(self, result):
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("--build-system native", result.stdout)
        self.assertIn("swift.sh: Xcode", result.stderr)

    def test_exact_clt_path(self):
        self.assert_clt(self.run_script(CLT))

    def test_trailing_slash_is_ignored(self):
        self.assert_clt(self.run_script(CLT + "/"))
        self.assert_clt(self.run_script(CLT + "//"))

    def test_unset_developer_dir_asks_xcode_select(self):
        self.assert_clt(self.run_script(None, CLT))
        self.assert_xcode(self.run_script(None, "/Applications/Xcode.app/Contents/Developer"))

    def test_empty_developer_dir_counts_as_unset(self):
        self.assert_clt(self.run_script("", CLT + "/"))

    def test_xcode(self):
        self.assert_xcode(self.run_script("/Applications/Xcode.app/Contents/Developer", CLT))


if __name__ == "__main__":
    unittest.main()
