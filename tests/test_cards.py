import unittest

from ibox import cards


class BuiltinCardTests(unittest.TestCase):
    def test_builtin_cards_are_valid(self):
        loaded = cards.load_all(merge=False)
        self.assertGreater(len(loaded), 50)
        self.assertEqual(cards.validate(loaded), [])

    def test_every_card_has_both_platforms(self):
        for c in cards.load_all():
            with self.subTest(card=c.id):
                self.assertIsNotNone(c.impl("mac"))
                self.assertIsNotNone(c.impl("win"))

    def test_categories_follow_file_order(self):
        cats = cards.categories(cards.load_all())
        self.assertEqual(cats[0], "硬件与系统信息")
        self.assertEqual(cats[-1], "AI 工具")


class ParseTests(unittest.TestCase):
    SAMPLE = """# 测试分类

## 做一件事
- id: do-thing
- 别名: 做事,干活
- 作用: 演示

### mac
- 命令: foo
- 用法: `foo -x`
- 示例: `foo -x 1` → 解释

### win
- 命令: Get-Foo, Set-Foo
- 用法: `Get-Foo`
"""

    def test_parse_sections(self):
        (c,) = cards.parse(self.SAMPLE)
        self.assertEqual(c.category, "测试分类")
        self.assertEqual(c.id, "do-thing")
        self.assertEqual(c.aliases, ["做事", "干活"])
        self.assertEqual(c.impl("mac")["用法"], "`foo -x`")
        self.assertEqual(c.commands("win"), ["Get-Foo", "Set-Foo"])
        self.assertEqual(c.commands(), ["foo", "Get-Foo", "Set-Foo"])
        self.assertEqual(cards.validate([c]), [])

    def test_validate_reports_problems(self):
        text = self.SAMPLE.replace("id: do-thing", "id: Bad_ID").replace("### win", "### linux")
        problems = cards.validate(cards.parse(text, source="x.md"))
        self.assertTrue(any("id" in p for p in problems))
        self.assertTrue(any("未知平台段" in p for p in problems))

    def test_first_snippet(self):
        self.assertEqual(cards.first_snippet("`df -h` → 看空间；`df -i`"), "df -h")
        self.assertEqual(cards.first_snippet("没有反引号"), "没有反引号")


if __name__ == "__main__":
    unittest.main()
