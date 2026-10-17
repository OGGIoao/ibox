"""终端界面：卡面渲染、交互浏览、开场屏。"""
import os
import sys
import unicodedata

from ibox import search, semantic, state
from ibox.cards import first_snippet
from ibox.env import PLATFORM_LABEL, copy_to_clipboard, read_key

_COLOR = sys.stdout.isatty() and not os.environ.get("NO_COLOR")


def _c(code):
    return "\033[%sm" % code if _COLOR else ""


R, BOLD, DIM, BORD = _c(0), _c("1"), _c("2"), _c("90")
CYAN, GREEN, YELLOW, MAG, RED, BLUE = (_c(x) for x in ("1;36", "1;32", "1;33", "1;35", "1;31", "1;34"))
W = 58


def pad(text, width):
    """按显示宽度补空格（中文占两格），让中英混排的列对齐。"""
    shown = sum(2 if unicodedata.east_asian_width(ch) in "WF" else 1 for ch in text)
    return text + " " * max(0, width - shown)


def _bold_code(text, base):
    """把 `命令` 里的命令加粗，一眼看到该敲什么。"""
    parts = text.split("`")
    return "".join(BOLD + p + R + base if i % 2 else p for i, p in enumerate(parts))


def _row(label="", value="", color=""):
    if not label:
        print(BORD + "│" + R)
    else:
        print(BORD + "│ " + R + color + label.ljust(4, "　") + R + "  " + value)


def render(card, platform):
    other = "mac" if platform == "win" else "win"
    print(BORD + "╭─ " + R + BOLD + card.title + R + BORD + " " + "─" * max(6, W - 2 * len(card.title)) + R)
    _row()
    _row("用途", card.purpose, CYAN)
    _row()
    impl = card.impl(platform)
    print(BORD + "│ " + R + BLUE + "▌在 %s 上" % PLATFORM_LABEL[platform] + R)
    if impl:
        if impl.get("命令"):
            _row("命令", impl["命令"], GREEN)
        _row("用法", _bold_code(impl.get("用法", ""), ""), GREEN)
        if impl.get("示例"):
            _row("示例", _bold_code(impl["示例"], YELLOW), YELLOW)
        if impl.get("踩坑"):
            _row("踩坑", RED + _bold_code(impl["踩坑"], RED) + R, RED)
    else:
        _row("", "")
        print(BORD + "│   " + R + DIM + "这件事在 %s 上没有对应做法" % PLATFORM_LABEL[platform] + R)
    other_impl = card.impl(other)
    if other_impl:
        _row()
        print(BORD + "│ " + R + DIM + "在 %s 上：%s" % (
            PLATFORM_LABEL[other], _bold_code(other_impl.get("用法", ""), DIM)) + R)
    if card.aliases:
        _row()
        _row("说法", MAG + "、".join(card.aliases) + R, MAG)
    print(BORD + "└" + "─" * W + R)


def copy_example(card, platform):
    impl = card.impl(platform) or {}
    cmd = first_snippet(impl.get("示例") or impl.get("用法", ""))
    if not cmd:
        print("（这张卡在 %s 上没有可复制的命令）" % PLATFORM_LABEL[platform])
        return
    hint = copy_to_clipboard(cmd)
    if hint:
        print("✅ 已复制，%s 粘贴运行：\n   %s" % (hint, cmd))
    else:
        print("（剪贴板不可用，请手动复制）\n   %s" % cmd)


def list_cards(cards):
    cur = None
    for i, c in enumerate(cards, 1):
        if c.category != cur:
            cur = c.category
            print("\n" + BOLD + cur + R)
        print("  %2d. %s" % (i, c.title))


def _menu():
    print(DIM + " n/→ 下一张  p/← 上一张  b 回退  f 前进  c 复制命令  t 切换平台  / 重新搜索  q 退出" + R)


def _pause():
    try:
        input(DIM + "（回车继续）" + R)
    except (EOFError, KeyboardInterrupt):
        pass


def browse(order, start, ctx):
    """交互浏览：翻页、回退、复制、切平台、重新搜索（在全部卡片里搜）。"""
    if not order:
        return
    idx, hist, future = start, [], []
    platform = ctx["platform"]
    while True:
        if sys.stdout.isatty():
            sys.stdout.write("\033[2J\033[H")
        card = order[idx]
        print(DIM + "〔 %d / %d 〕" % (idx + 1, len(order)) + R)
        state.record_view(card.id)
        render(card, platform)
        if sys.stdout.isatty():
            _menu()
        k = read_key() if sys.stdout.isatty() else None
        if k is None:
            return  # 非交互（管道、脚本）：只展示最佳一张
        if k in ("q", "Q", "esc"):
            return
        if k in ("n", "j", "right", "down") and idx < len(order) - 1:
            hist.append(idx)
            future.clear()
            idx += 1
        elif k in ("p", "k", "left", "up") and idx > 0:
            hist.append(idx)
            future.clear()
            idx -= 1
        elif k == "b" and hist:
            future.append(idx)
            idx = hist.pop()
        elif k == "f" and future:
            hist.append(idx)
            idx = future.pop()
        elif k == "c":
            copy_example(card, platform)
            _pause()
        elif k == "t":
            platform = "mac" if platform == "win" else "win"
        elif k == "/":
            try:
                q = input("\n重新搜索（说想做的事）：").strip()
            except (EOFError, KeyboardInterrupt):
                return
            if q:
                found = search.search(ctx["cards"], q, platform, ctx["learned"], ctx["semantic"])
                if found:
                    order, idx, hist, future = found, 0, [], []
                else:
                    print("没找到「%s」，保持当前" % q)
                    _pause()


def opening(ctx):
    """无参数进入：开场屏 + 小型 REPL。"""
    cards = ctx["cards"]
    by_id = {c.id: c for c in cards}
    pinned = [c for c in cards if c.pinned][:6]
    while True:
        st = state.load()
        recent = [by_id[i].title for i in st["recent"][:5] if i in by_id]
        due = [by_id[i].title for i in state.due_for_review(st) if i in by_id]
        print(BORD + "╭─ " + R + BOLD + "ibox · 说人话找终端命令" + R + DIM +
              "  （%s 版）" % PLATFORM_LABEL[ctx["platform"]] + R)
        _row()
        print(BORD + "│ " + R + CYAN + "直接说想做的事：" + R + GREEN +
              "哪个程序最占内存 · 端口被谁占用 · 磁盘还剩多少" + R)
        _row()
        if pinned:
            print(BORD + "│ " + R + MAG + "★ 常用" + R)
            for i, c in enumerate(pinned, 1):
                print(BORD + "│   " + R + DIM + str(i) + R + "  " + c.title)
        if recent:
            _row()
            print(BORD + "│ " + R + YELLOW + "↺ 最近：" + R + DIM + " · ".join(recent) + R)
        if due:
            print(BORD + "│ " + R + YELLOW + "↻ 该复习：" + R + DIM + " · ".join(due) + R)
        if ctx["semantic"] and semantic.available():
            print(BORD + "│ " + R + DIM + "🧠 语义检索已启用（ollama · %s）" % semantic.model() + R)
        print(BORD + "└" + "─" * W + R)
        print(DIM + "输入想做的事回车搜 · 数字选常用 · 直接回车看全部 · q 退出" + R)
        try:
            line = input(BOLD + "ibox> " + R).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if line in ("q", "quit", "exit"):
            return
        if not line:
            list_cards(cards)
            try:
                s = input("\n选序号（回车返回）：").strip()
            except (EOFError, KeyboardInterrupt):
                continue
            if s.isdigit() and 0 < int(s) <= len(cards):
                browse(cards, int(s) - 1, ctx)
            continue
        if line.isdigit():
            n = int(line)
            if 0 < n <= len(pinned):
                browse(pinned, n - 1, ctx)
            continue
        found = search.search(cards, line, ctx["platform"], ctx["learned"], ctx["semantic"])
        if found:
            state.record_learn(line, found[0].id, search.known_words(cards))
            browse(found, 0, ctx)
        else:
            sug = search.suggest(cards, line)
            print("没找到「%s」。" % line + ("你是不是想找：" + " / ".join(c.title for c in sug) if sug else ""))
            _pause()
