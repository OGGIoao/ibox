import unittest

from ibox import cards, search

# 说法 -> 期望排第一的卡。改排序逻辑或卡片别名后必须全部通过。
GOLDEN = {
    "查端口占用": "port-owner",
    "哪个文件夹最大": "folder-size",
    "查看磁盘空间": "disk-free",
    "哪个进程吃内存": "top-procs",
    "看系统版本": "os-version",
    "查进程": "list-procs",
    "提交代码": "git-commit",
    "启动ollama": "ollama-serve",
    "强制结束没响应的程序": "kill-proc",
    "怎么把文件传到另一台机器": "scp",
    "让别人ssh连进我电脑": "ssh-server",
    "装个新软件": "install-app",
    "看CPU型号": "cpu-model",
}

# 输入另一平台的命令名，也要找到同一件事——这是「两个版本共用一个意图库」的意义
CROSS_PLATFORM = {
    "lsof": "port-owner",
    "Stop-Process": "kill-proc",
    "winget": "install-app",
}


class GoldenQueryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cards = cards.load_all()

    def test_golden_queries_on_both_platforms(self):
        for platform in ("mac", "win"):
            for query, expected in GOLDEN.items():
                with self.subTest(platform=platform, query=query):
                    ranked = search.rank(self.cards, query, platform)
                    self.assertTrue(ranked, "没有结果")
                    self.assertEqual(ranked[0].id, expected)

    def test_command_names_from_either_platform(self):
        for platform in ("mac", "win"):
            for query, expected in CROSS_PLATFORM.items():
                with self.subTest(platform=platform, query=query):
                    self.assertEqual(search.rank(self.cards, query, platform)[0].id, expected)

    def test_learned_phrase_wins(self):
        learned = {"那个看空间的": {"disk-free": 1}}
        self.assertEqual(search.rank(self.cards, "那个看空间的", "win", learned)[0].id, "disk-free")

    def test_suggest_on_typo(self):
        self.assertIn("port-owner", [c.id for c in search.suggest(self.cards, "lsoff")])


if __name__ == "__main__":
    unittest.main()
