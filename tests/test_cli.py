import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CliSmokeTests(unittest.TestCase):
    def run_cli(self, *args):
        with tempfile.TemporaryDirectory() as home:
            env = os.environ.copy()
            env["HOME"] = home
            env["USERPROFILE"] = home
            env["PYTHONDONTWRITEBYTECODE"] = "1"
            # 模拟 Windows runner 的非 UTF-8 默认代码页，防止中文输出回归。
            env["PYTHONIOENCODING"] = "cp1252"
            return subprocess.run(
                [sys.executable, *args],
                cwd=ROOT,
                env=env,
                text=True,
                encoding="utf-8",
                capture_output=True,
                timeout=15,
                check=False,
            )

    def test_pycheat_list(self):
        result = self.run_cli("terminal-toolbox/pycheat.py", "--no-llm", "--list")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("lsof", result.stdout)

    def test_tk_help(self):
        result = self.run_cli("terminal-toolbox/tk", "--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("note", result.stdout)
        self.assertIn("sum", result.stdout)


if __name__ == "__main__":
    unittest.main()
