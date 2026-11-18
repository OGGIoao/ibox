"""命令行入口。

  ibox                      开场屏（交互终端）/ 使用说明（非交互）
  ibox <想做的事>           等同 ibox how <想做的事>
  ibox how <想做的事>       查命令  [-c 复制最佳命令] [-l 列出全部] [--no-ai]
  ibox learn [分类] [--due] 按分类学习 / 复习
  ibox card check|list|dir  卡库体检 / 列表 / 自定义卡目录
  ibox port <端口号>        查 Windows 本机的 TCP 监听进程
  --platform mac|win       切换命令卡的展示平台
"""
import argparse
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

from ibox import __version__, cards as cardlib, search, state, ui
from ibox.env import (
    PLATFORMS, PLATFORM_LABEL, config_dir, current_platform, ensure_utf8_stdio, open_output_dir,
    query_tcp_listeners, root_records_dir, run_bundled_tool, set_root_records_dir,
)

SUBCOMMANDS = ("how", "learn", "card", "port")

GUIDE = """ibox %s · 本机排障与命令卡（当前命令卡平台为 %s）

  ibox port 3000              查 Windows 本机的 TCP 监听进程
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
        if sys.stdin.isatty() and sys.stdout.isatty():
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


def _parse_port(value):
    try:
        port = int(value)
    except ValueError:
        port = 0
    if not 1 <= port <= 65535:
        raise argparse.ArgumentTypeError("端口号须为 1 到 65535 的整数")
    return port


def cmd_port(args, _platform):
    try:
        listeners = query_tcp_listeners(args.port)
    except RuntimeError as exc:
        print(f"查询失败。{exc}", file=sys.stderr)
        return 1

    if not listeners:
        print(f"本机 TCP 端口 {args.port} 当前没有监听记录。")
    else:
        print(f"本机 TCP 端口 {args.port} · {len(listeners)} 条监听记录")
        for row in listeners:
            name = row["name"] or "进程详情不可用"
            print(f"  {row['address']}  ·  PID {row['pid']}  ·  {name}")
            if row["path"]:
                print(f"    程序路径  {row['path']}")
            elif row["name"]:
                print("    程序路径不可读")
    print("来源  Windows Get-NetTCPConnection（监听） / Get-Process（进程）")
    return 0


def _port_from_question(question):
    """只从明确的端口问题里取一个编号，避免把其他数字当成端口。"""
    match = re.fullmatch(
        r"(?:谁(?:正在|在)?用\s*)?(\d+)(?:\s*(?:被谁占用|被占用了吗|谁在用|有程序在用吗|还在用吗|空了吗))?",
        question.rstrip("？?。！!").strip(),
    )
    if match:
        return match[1]
    if "端口" in question:
        numbers = re.findall(r"(?<![\d.+-])\d+(?![\d.])", question)
        if len(numbers) == 1:
            return numbers[0]
    return ""


def _parse_guided_port(value):
    if value.isdecimal():
        return _parse_port(value)
    try:
        address = urlsplit(value if "://" in value else "//" + value)
        if address.hostname in {"localhost", "127.0.0.1", "::1", "0.0.0.0"} and address.port:
            return address.port
    except ValueError:
        pass
    raise argparse.ArgumentTypeError("请输入 1 到 65535 之间的端口号，或粘贴带端口的本机地址。")


def _guided_port(value=""):
    if not value:
        ui.show_port_help()
    while True:
        if not value:
            value = input("\n端口 > ").strip()
            if not value:
                return
        try:
            port = _parse_guided_port(value)
        except argparse.ArgumentTypeError:
            print("请输入 1 到 65535 之间的端口号，例如 3000，或粘贴 http://localhost:3000。")
            value = ""
            continue

        value = ""
        print(f"正在查本机端口 {port}…", flush=True)
        try:
            listeners = query_tcp_listeners(port)
        except RuntimeError as exc:
            listeners = None
            print("这次查询没有成功。请再试一次。")
            print(f"系统提示  {exc}")
        else:
            if listeners:
                ui.show_port_result(port, listeners)
            else:
                print(f"当前没查到在端口 {port} 等待 TCP 连接的程序。")
                print("可核对端口号，或在程序启动后重查。")

        options = "[1] 换端口"
        if listeners:
            options += "  [2] 详情"
        options += "  [3] 重查  [0] 返回"
        while True:
            choice = input(f"\n{options} > ").strip()
            if choice in ("", "0"):
                return
            if choice == "1":
                break
            if choice == "3":
                value = str(port)
                break
            if choice == "2" and listeners:
                ui.show_port_evidence(listeners)
            else:
                print("请输入上方显示的选项编号。")


def _guided_root_probe():
    print(f"\n{ui.ACCENT}根系探测器{ui.R}")
    print("查看安装记录、自启项目等本机信息。")
    records = root_records_dir()
    while True:
        print(f"\n当前保存位置  {records}")
        print("  [1] 查软件    [2] 保存或对比快照")
        print("  [3] 换目录    [4] 管理保存的结果   [0] 返回")
        choice = input("根系探测器 > ").strip()
        if choice in ("", "0"):
            return
        if choice == "1":
            keyword = input("输入软件名或厂商名，例如 Python（直接回车返回）> ").strip()
            if not keyword:
                return
            if len(keyword) < 2:
                print("请至少输入两个字，再选 1 重试。")
                continue
            run_bundled_tool("root-probe", Keyword=keyword, RecordsDir=str(records))
            return
        if choice == "2":
            print("快照会记下当时有哪些软件记录，方便与另一次对比。")
            run_bundled_tool("root-snapshots", RecordsDir=str(records))
            return
        if choice == "3":
            print("例如 D:\\iBox。新报告和快照会放到你选的位置下的 iBox-根系记录 文件夹。")
            value = input("粘贴现有文件夹的位置，或输入「默认」恢复（回车取消）> ").strip().strip('"')
            if not value:
                continue
            if value == "默认":
                records = set_root_records_dir(None)
                continue
            folder = Path(value).expanduser()
            if not folder.is_absolute() or not folder.is_dir():
                print("请使用一个已经存在的完整文件夹位置。")
                continue
            records = set_root_records_dir(folder.resolve())
            print("下次打开会沿用这个位置。原有报告仍在原来的目录。")
            continue
        if choice == "4":
            if records.is_dir():
                print("在打开的文件夹里选中不用的报告或快照，按 Delete 即可删除。")
                open_output_dir(records)
            else:
                print("这个位置还没有报告或快照。")
            continue
        print("请输入上面显示的选项编号。")


def _guided_file_spirit():
    print(f"\n{ui.ACCENT}文件精灵{ui.R}  在打开的窗口选择一个文件。")
    cards = (config_dir() / "tools" / "file-spirit" / "cards").resolve()
    run_bundled_tool("file-spirit", LegacyCards=str(cards))


def _matching_tools(tools, query):
    words = query.casefold().split()
    for command, (number, name, purpose, keywords, _) in tools.items():
        searchable = f"{command} {name} {purpose} {keywords}".casefold()
        if all(word in searchable for word in words):
            yield number, command, name, purpose


def _diagnostics_home():
    tools = {
        "/port": ("1", "查端口", "找占用端口的程序", "网络 连接 监听 TCP", _guided_port),
        "/roots": ("2", "根系探测器", "看软件留下的记录", "卸载 自启 安装 快照 残留", _guided_root_probe),
        "/file": ("3", "文件精灵", "看指纹、对比文件", "备份 副本 内容 校验 SHA256", _guided_file_spirit),
    }
    shortcuts = {number: command for command, (number, _, _, _, _) in tools.items()}
    map_labels = {command: f"[{number}] {name}" for command, (number, name, _, _, _) in tools.items()}
    view = "input"
    tool_query = ""
    ui.show_home(__version__)
    while True:
        prompt = ">"
        if view == "map":
            ui.show_layer_map(map_labels)
            prompt = "地图 >"
        elif view == "tools":
            ui.show_tools(list(_matching_tools(tools, tool_query)), tool_query)
            prompt = "工具 >"
        choice = input(f"\n{ui.ACCENT}{prompt}{ui.R} ").strip()
        if choice in ("0", "/exit"):
            return
        if not choice:
            view = "tools" if view == "input" else "input"
            tool_query = ""
            continue
        command, _, argument = choice.partition(" ")
        if command in ("/", "/tools"):
            view = "tools"
            tool_query = argument.strip()
            continue
        if choice == "/map":
            view = "map"
            tool_query = ""
            continue
        command = shortcuts.get(choice, command)
        return_view = "tools" if view == "input" else view
        if command in tools:
            _, _, _, _, use_tool = tools[command]
            if command != "/port" and argument:
                print(f"输入 {command} 后按回车，就能看到该工具的指引。")
                continue
            try:
                if command == "/port":
                    use_tool(argument.strip())
                else:
                    use_tool()
            except (OSError, RuntimeError) as exc:
                print(f"无法完成这次操作。{exc}")
            view = return_view
            continue
        if view == "map" and choice.isdecimal():
            print("请输入地图上显示的工具编号。")
            continue
        port = _port_from_question(choice)
        if port:
            _guided_port(port)
            view = return_view
        elif view == "tools":
            tool_query = choice
        elif "端口" in choice:
            print("\n请指定一个要查的端口号。")
            _guided_port()
            view = return_view
        elif view == "map":
            print("请输入地图上的编号，或直接回车返回。")
        elif next(_matching_tools(tools, choice), None):
            view = "tools"
            tool_query = choice
        else:
            print("按回车或输入 /tools 找工具，也可以问「谁在用 3000？」。")


def build_parser():
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--platform", choices=PLATFORMS, help="命令卡展示平台（默认当前系统）")

    p = argparse.ArgumentParser(prog="ibox", parents=[common], description="Windows 本机排障与命令卡")
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

    port = sub.add_parser("port", help="查 Windows 本机的 TCP 监听进程")
    port.add_argument("port", metavar="端口号", type=_parse_port)
    return p


def main(argv=None):
    ensure_utf8_stdio()
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv and current_platform() == "win" and sys.stdin.isatty() and sys.stdout.isatty():
        try:
            _diagnostics_home()
        except EOFError:
            print()
        except KeyboardInterrupt:
            print()
            sys.exit(130)
        return
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
    handler = {"how": cmd_how, "learn": cmd_learn, "card": cmd_card, "port": cmd_port}[args.cmd]
    try:
        sys.exit(handler(args, platform))
    except KeyboardInterrupt:
        print()
        sys.exit(130)
