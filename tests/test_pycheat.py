import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "terminal-toolbox" / "pycheat.py"
SHEET_PATH = ROOT / "terminal-toolbox" / "cheatsheet.md"

spec = importlib.util.spec_from_file_location("pycheat", MODULE_PATH)
pycheat = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pycheat)


class CheatSheetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cards = pycheat.load_cards(SHEET_PATH)

    def test_card_names_are_unique(self):
        names = [card["name"] for card in self.cards]
        self.assertEqual(len(names), len(set(names)))

    def test_required_fields_are_present(self):
        required = ("作用", "用法", "示例", "踩坑", "Windows对照", "来源卷")
        for card in self.cards:
            with self.subTest(card=card["name"]):
                for field in required:
                    self.assertTrue(card.get(field), f"缺少字段：{field}")

    def test_offline_golden_queries(self):
        cases = {
            "查端口占用": "lsof",
            "哪个文件夹最大": "du",
            "查看磁盘空间": "df",
            "哪个进程吃内存": "top / htop",
            "看系统版本": "sw_vers",
            "查进程": "ps",
            "提交代码": "git add / commit",
            "启动ollama": "ollama serve",
        }
        for query, expected in cases.items():
            with self.subTest(query=query):
                ranked = pycheat.rank(self.cards, query)
                self.assertTrue(ranked, "没有返回结果")
                self.assertEqual(ranked[0]["name"], expected)


if __name__ == "__main__":
    unittest.main()
