"""意图卡：解析、加载、校验。

一张卡 = 一个「想做的事」，下面分别写它在 mac / win 上怎么做：

    # 网络与远程                      ← 文件的一级标题就是分类

    ## 查看端口被谁占用               ← 意图标题
    - id: port-owner                  ← 稳定标识（小写字母、数字、连字符）
    - 别名: 端口占用,查端口           ← 人话说法，检索命中的关键
    - 作用: 一句话说明
    - 常用: 是                        ← 可选，出现在开场屏

    ### mac
    - 命令: lsof                      ← 涉及的程序名（检索与将来的 explain 用）
    - 用法: …  （必填）
    - 示例: `…` → 解释               ← 第一个反引号片段就是「复制」的内容
    - 踩坑: …

    ### win
    - …

内置卡在包内 data/cards/；用户自定义卡放 <配置目录>/cards/*.md，同 id 覆盖内置卡。
"""
import re
from dataclasses import dataclass, field
from pathlib import Path

from ibox.env import PLATFORMS, config_dir

BUILTIN_DIR = Path(__file__).resolve().parent / "data" / "cards"
CARD_FIELDS = ("id", "别名", "作用", "常用")
IMPL_FIELDS = ("命令", "用法", "示例", "踩坑")
_ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
_FIELD_RE = re.compile(r"^-\s*([^:：]+)[:：]\s*(.*)$")


@dataclass
class Card:
    title: str
    category: str
    source: str
    fields: dict = field(default_factory=dict)
    impls: dict = field(default_factory=dict)  # 平台 -> {命令/用法/示例/踩坑}
    problems: list = field(default_factory=list)  # 解析时发现的格式问题

    @property
    def id(self):
        return self.fields.get("id", "")

    @property
    def purpose(self):
        return self.fields.get("作用", "")

    @property
    def aliases(self):
        return [a.strip().lower() for a in self.fields.get("别名", "").split(",") if a.strip()]

    @property
    def pinned(self):
        return self.fields.get("常用") == "是"

    def impl(self, platform):
        return self.impls.get(platform)

    def commands(self, platform=None):
        """涉及的程序名；不指定平台则返回所有平台的并集。"""
        plats = [platform] if platform else list(self.impls)
        out = []
        for p in plats:
            for c in self.impls.get(p, {}).get("命令", "").split(","):
                c = c.strip()
                if c and c not in out:
                    out.append(c)
        return out


def parse(text, source="<string>"):
    """把一个卡片文件解析成 Card 列表。"""
    category = ""
    cards = []
    card = None
    section = None  # None = 卡片公共字段；否则是平台名
    for lineno, raw in enumerate(text.splitlines(), 1):
        line = raw.rstrip()
        where = "%s:%d" % (source, lineno)
        if line.startswith("# "):
            category = line[2:].strip()
        elif line.startswith("## "):
            card = Card(title=line[3:].strip(), category=category, source=where)
            cards.append(card)
            section = None
        elif line.startswith("### "):
            if card is None:
                continue
            section = line[4:].strip()
            if section not in PLATFORMS:
                card.problems.append("未知平台段「%s」（只认 %s）" % (section, " / ".join(PLATFORMS)))
            card.impls.setdefault(section, {})
        elif card is not None:
            m = _FIELD_RE.match(line)
            if not m:
                continue
            key, val = m.group(1).strip(), m.group(2).strip()
            if section is None:
                if key not in CARD_FIELDS:
                    card.problems.append("未知字段「%s」" % key)
                card.fields[key] = val
            else:
                if key not in IMPL_FIELDS:
                    card.problems.append("%s 段未知字段「%s」" % (section, key))
                card.impls[section][key] = val
    return cards


def user_dir():
    return config_dir() / "cards"


def _card_files():
    files = sorted(BUILTIN_DIR.glob("*.md"))
    if user_dir().is_dir():
        files += sorted(user_dir().glob("*.md"))
    return files


def load_all(merge=True):
    """加载内置卡 + 用户卡。merge=True 时同 id 的用户卡覆盖内置卡（保持内置顺序）。"""
    cards = []
    for path in _card_files():
        cards += parse(path.read_text(encoding="utf-8"), source=path.name)
    if not merge:
        return cards
    by_id = {}
    for c in cards:
        by_id[c.id or c.title] = c
    seen, out = set(), []
    for c in cards:
        key = c.id or c.title
        if key not in seen:
            seen.add(key)
            out.append(by_id[key])
    return out


def categories(cards):
    out = []
    for c in cards:
        if c.category not in out:
            out.append(c.category)
    return out


def validate(cards):
    """返回问题列表（字符串）；空列表即全部合规。"""
    problems = []
    ids, titles = {}, {}
    for c in cards:
        tag = "[%s] %s" % (c.source, c.title)
        problems += ["%s：%s" % (tag, p) for p in c.problems]
        if not c.category:
            problems.append("%s：文件缺少「# 分类」一级标题" % tag)
        if not _ID_RE.match(c.id):
            problems.append("%s：id「%s」应为小写字母、数字、连字符" % (tag, c.id))
        elif c.id in ids:
            problems.append("%s：id「%s」与 %s 重复" % (tag, c.id, ids[c.id]))
        ids.setdefault(c.id, c.source)
        if c.title in titles:
            problems.append("%s：标题与 %s 重复" % (tag, titles[c.title]))
        titles.setdefault(c.title, c.source)
        for f in ("别名", "作用"):
            if not c.fields.get(f):
                problems.append("%s：缺「%s」" % (tag, f))
        if not any(p in c.impls for p in PLATFORMS):
            problems.append("%s：至少要有一个 ### mac 或 ### win 段" % tag)
        for p, impl in c.impls.items():
            if not impl.get("用法"):
                problems.append("%s：%s 段缺「用法」" % (tag, p))
    return problems


def first_snippet(text):
    """示例里第一个 `反引号` 片段——就是用户真正要敲的那条命令。"""
    m = re.search(r"`([^`]+)`", text or "")
    return m.group(1) if m else (text or "").strip()
