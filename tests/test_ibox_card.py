"""ibox card / learn 子命令冒烟测试 —— 对应「卡库注册机制 + 学习模式」。

这些测试守护的是卡库的结构性约束：
  - 每张卡的分类必须在受控词表内、课卷值合法、必需字段完整、卡名唯一；
  - 学习模式的分类目录与按课卷筛必须可用；
  - 两份数据源（用户级 / 仓库版）的比对命令必须可用。

注意：pycheat 的 resolve_sheet() 优先使用用户级数据源，无则回退仓库版 ——
所以本测试在本地（有用户级）与 CI（无用户级）下都能跑。
"""
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IBOX = ROOT / "terminal-toolbox" / "ibox"

CATEGORIES = ("硬件与系统信息", "进程与资源", "文件与磁盘", "Shell 与环境",
              "版本控制", "网络与远程", "AI 工具")


def run_ibox(*args):
    return subprocess.run(
        [sys.executable, str(IBOX), *args],
        capture_output=True, text=True, encoding="utf-8",
        stdin=subprocess.DEVNULL, cwd=str(ROOT), timeout=60,
    )


class IboxCardTests(unittest.TestCase):
    def test_card_check_all_green(self):
        """卡库体检：分类合法 / 课卷合法 / 字段完整 / 卡名唯一。"""
        p = run_ibox("card", "check")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("全部合规", p.stdout)

    def test_card_list_shows_categories(self):
        p = run_ibox("card", "list")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("网络与远程", p.stdout)

    def test_learn_overview_lists_all_domains(self):
        p = run_ibox("learn")
        self.assertEqual(p.returncode, 0, p.stderr)
        for cat in CATEGORIES:
            self.assertIn(cat, p.stdout)

    def test_learn_by_volume(self):
        """按 OS 课卷筛：第二卷（文件系统）应能列出卡片。"""
        p = run_ibox("learn", "--卷", "2")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("第 2 卷", p.stdout)

    def test_card_sync_is_runnable(self):
        """比对命令可用即可：一致报一致，不一致报差异（两种都算通过）。"""
        p = run_ibox("card", "sync")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertTrue("完全一致" in p.stdout or "不一致" in p.stdout)


if __name__ == "__main__":
    unittest.main()
