"""命令行入口。

  ibox                      开场屏（交互终端）/ 使用说明（非交互）
  ibox <想做的事>           等同 ibox how <想做的事>
  ibox how <想做的事>       查命令  [-c 复制最佳命令] [-l 列出全部] [--no-ai]
  ibox learn [分类] [--due] 按分类学习 / 复习
  ibox card check|list|dir  卡库体检 / 列表 / 自定义卡目录
  全局：--platform mac|win  查看另一个平台的做法
"""
import argparse
import sys

from ibox import __version__, cards as cardlib, search, state, ui
from ibox.env import PLATFORMS, PLATFORM_LABEL, current_platform, ensure_utf8_stdio

SUBCOMMANDS = ("how", "learn", "card")

GUIDE = """ibox %s · 说人话找终端命令（当前：%s 版）

  ibox 端口被谁占用           查命令（等同 ibox how …）
  ibox how 磁盘还剩多少 -c     把最佳命令复制到剪贴板
  ibox how -l                 列出全部卡片
  ibox learn                  按分类学习（目录 + 进度）
  ibox learn 网络              过某一类（可只写关键词）
  ibox learn --due            只看该复习的
  ibox card check             卡库体检
  ibox card dir               自定义卡放哪

  --platform mac|win          看另一个平台的做法
  浏览卡片时：n 下一张 · p 上一张 · c 复制 · t 切换平台 · / 重新搜索 · q 退出
"""


def _context(platform, use_semantic=True):
    cards = cardlib.load_all()
    return {"cards": cards, "platform": platform, "semantic": use_semantic,
            "learned": state.load()["learned"]}


def cmd_how(args, platform):
    ctx = _context(platform, not args.no_ai)
    cards = ctx["cards"]
    if args.list:
        ui.list_cards(cards)
        return 0
    q = " ".join(args.query).strip()
    if not q:
        if sys.stdin.isatty():
            ui.opening(ctx)
        else:
            print(GUIDE % (__version__, PLATFORM_LABEL[platform]))
        return 0
    found = search.search(cards, q, platform, ctx["learned"], ctx["semantic"])
    if not found:
        sug = search.suggest(cards, q)
        print("没找到和「%s」相关的卡片。" % q)
        if sug:
            print("你是不是想找：" + " / ".join(c.title for c in sug))
        return 1
    state.record_learn(q, found[0].id, search.known_words(cards))
    if args.copy:
        ui.copy_example(found[0], platform)
        return 0
    ui.browse(found, 0, ctx)
    return 0


def _match_category(want, cats):
    if want in cats:
        return want
    hits = [c for c in cats if want.lower() in c.lower()]
    return hits[0] if len(hits) == 1 else None


def cmd_learn(args, platform):
    ctx = _context(platform)
    cards = ctx["cards"]
    cats = cardlib.categories(cards)
    st = state.load()
    if args.due:
        due = set(state.due_for_review(st))
        order = [c for c in cards if c.id in due]
        if not order:
            print("✅ 暂时没有该复习的卡片。")
            return 0
        ui.browse(order, 0, ctx)
        return 0
    if not args.category:
        seen_total = 0
        print("按分类学习（共 %d 张）\n" % len(cards))
        for i, cat in enumerate(cats, 1):
            ids = [c.id for c in cards if c.category == cat]
            seen = sum(1 for x in ids if st["views"].get(x, {}).get("count"))
            seen_total += seen
            print("  %d. %s %s  %d/%d" % (i, ui.pad(cat, 16), "█" * seen + "·" * (len(ids) - seen), seen, len(ids)))
        print("\n  总进度 %d/%d · 看某一类：ibox learn <分类关键词>" % (seen_total, len(cards)))
        return 0
    cat = _match_category(args.category, cats)
    if not cat:
        print("未知分类「%s」；可选：%s" % (args.category, " / ".join(cats)))
        return 1
    ui.browse([c for c in cards if c.category == cat], 0, ctx)
    return 0


def cmd_card(args, platform):
    if args.action == "dir":
        print(cardlib.user_dir())
        print("在这里放 .md 卡片文件即可生效（格式同内置卡；同 id 会覆盖内置卡）。")
        return 0
    cards = cardlib.load_all(merge=args.action == "list")
    if args.action == "list":
        for cat in cardlib.categories(cards):
            print("\n# " + cat)
            for c in cards:
                if c.category == cat:
                    plats = "/".join(p for p in PLATFORMS if c.impl(p))
                    print("  %s %s %s" % (ui.pad(c.id, 16), ui.pad(plats, 8), c.title))
        return 0
    problems = cardlib.validate(cards)
    if problems:
        print("⚠️ 发现 %d 个问题：" % len(problems))
        for p in problems:
            print("  - " + p)
        return 1
    missing = {p: sum(1 for c in cards if not c.impl(p)) for p in PLATFORMS}
    print("✅ %d 张卡全部合规" % len(cards))
    print("   缺 mac 做法 %d 张 · 缺 win 做法 %d 张" % (missing["mac"], missing["win"]))
    return 0


def build_parser():
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--platform", choices=PLATFORMS, help="按哪个平台展示（默认当前系统）")

    p = argparse.ArgumentParser(prog="ibox", parents=[common], description="说人话找终端命令")
    p.add_argument("--version", action="version", version="ibox " + __version__)
    sub = p.add_subparsers(dest="cmd")

    how = sub.add_parser("how", parents=[common], help="查命令")
    how.add_argument("query", nargs="*")
    how.add_argument("-c", "--copy", action="store_true", help="复制最佳命令")
    how.add_argument("-l", "--list", action="store_true", help="列出全部卡片")
    how.add_argument("--no-ai", action="store_true", help="只用离线检索")

    learn = sub.add_parser("learn", parents=[common], help="按分类学习")
    learn.add_argument("category", nargs="?")
    learn.add_argument("--due", action="store_true", help="只看该复习的")

    card = sub.add_parser("card", parents=[common], help="卡库维护")
    card.add_argument("action", choices=("check", "list", "dir"))
    return p


def main(argv=None):
    ensure_utf8_stdio()
    argv = list(sys.argv[1:] if argv is None else argv)
    # 先摘出 --platform（它的值不是查询词），再判断：没写子命令 → 整句当作 how 的查询，
    # 于是 `ibox 端口被谁占用`、`ibox -c 磁盘空间` 都能直接用
    rest, plat = [], []
    it = iter(argv)
    for a in it:
        if a == "--platform":
            plat = ["--platform", next(it, "")]
        elif a.startswith("--platform="):
            plat = [a]
        else:
            rest.append(a)
    if not rest or rest[0] not in SUBCOMMANDS + ("-h", "--help", "--version"):
        rest.insert(0, "how")
    args = build_parser().parse_args(rest + plat)
    platform = args.platform or current_platform()
    handler = {"how": cmd_how, "learn": cmd_learn, "card": cmd_card}[args.cmd]
    try:
        sys.exit(handler(args, platform))
    except KeyboardInterrupt:
        print()
        sys.exit(130)
