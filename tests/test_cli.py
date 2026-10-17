"""以子进程跑真实 CLI：覆盖入口路由与 Windows 非 UTF-8 代码页下的中文输出。"""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"


def run(*args):
    with tempfile.TemporaryDirectory() as home:
        env = dict(os.environ, IBOX_HOME=home, PYTHONPATH=str(SRC), PYTHONIOENCODING="cp1252",
                   PYTHONDONTWRITEBYTECODE="1")
        return subprocess.run(
            [sys.executable, "-m", "ibox", *args], env=env, text=True, encoding="utf-8",
            capture_output=True, stdin=subprocess.DEVNULL, timeout=30, check=False,
        )


class CliTests(unittest.TestCase):
    def test_bare_query_routes_to_how(self):
        r = run("--no-ai", "--platform", "win", "端口被谁占用")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Get-NetTCPConnection", r.stdout)
        self.assertIn("在 macOS 上", r.stdout)

    def test_platform_switch(self):
        r = run("how", "--no-ai", "端口被谁占用", "--platform", "mac")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("lsof", r.stdout)
        self.assertIn("在 Windows 上", r.stdout)

    def test_no_match_exits_nonzero(self):
        r = run("--no-ai", "zzqqxx")
        self.assertEqual(r.returncode, 1)
        self.assertIn("没找到", r.stdout)

    def test_list(self):
        r = run("how", "-l")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("网络与远程", r.stdout)

    def test_card_check(self):
        r = run("card", "check")
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("全部合规", r.stdout)

    def test_learn_overview(self):
        r = run("learn")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("硬件与系统信息", r.stdout)

    def test_user_card_overrides_builtin(self):
        with tempfile.TemporaryDirectory() as home:
            (Path(home) / "cards").mkdir()
            (Path(home) / "cards" / "mine.md").write_text(
                "# 我的\n\n## 我的磁盘空间\n- id: disk-free\n- 别名: 看空间\n- 作用: 自定义\n\n"
                "### win\n- 用法: `my-df`\n", encoding="utf-8")
            env = dict(os.environ, IBOX_HOME=home, PYTHONPATH=str(SRC))
            r = subprocess.run([sys.executable, "-m", "ibox", "--no-ai", "--platform", "win", "看空间"],
                               env=env, text=True, encoding="utf-8", capture_output=True,
                               stdin=subprocess.DEVNULL, timeout=30)
        self.assertIn("my-df", r.stdout)


if __name__ == "__main__":
    unittest.main()
