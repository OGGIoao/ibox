"""运行环境：当前平台、配置目录、UTF-8 输出、剪贴板、按键读取。

所有「mac 和 Windows 不一样」的系统交互都收在这里，其余模块不判断 sys.platform。
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

PLATFORMS = ("mac", "win")
PLATFORM_LABEL = {"mac": "macOS", "win": "Windows"}


def current_platform():
    """卡片按 mac / win 两种实现组织；Linux 与 mac 同属 POSIX shell，暂用 mac 实现。"""
    return "win" if sys.platform == "win32" else "mac"


def config_dir():
    """用户数据目录：状态、向量缓存、自定义卡。IBOX_HOME 可覆盖（测试用）。"""
    return Path(os.environ.get("IBOX_HOME") or Path.home() / ".config" / "ibox")


def ensure_utf8_stdio():
    """Windows 旧代码页（cp936 / cp1252）或输出被重定向时，中文会乱码甚至崩溃。"""
    for stream in (sys.stdout, sys.stderr):
        encoding = (getattr(stream, "encoding", "") or "").lower().replace("-", "")
        if encoding != "utf8" and hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")


def copy_to_clipboard(text):
    """写剪贴板，成功返回粘贴快捷键提示，失败返回 None。"""
    if sys.platform == "darwin":
        args, hint = ["pbcopy"], "⌘V"
    elif sys.platform == "win32":
        args, hint = ["powershell", "-NoProfile", "-Command", "$input | Set-Clipboard"], "Ctrl+V"
    elif shutil.which("wl-copy"):
        args, hint = ["wl-copy"], "Ctrl+Shift+V"
    elif shutil.which("xclip"):
        args, hint = ["xclip", "-selection", "clipboard"], "Ctrl+Shift+V"
    else:
        return None
    try:
        subprocess.run(args, input=text, text=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        return None
    return hint


def _read_key_windows():
    import msvcrt

    ch = msvcrt.getch()
    if ch in (b"\x00", b"\xe0"):  # 方向键是双字节：前缀 + 键码
        return {b"H": "up", b"P": "down", b"K": "left", b"M": "right"}.get(msvcrt.getch(), "esc")
    if ch == b"\x03":
        raise KeyboardInterrupt
    if ch == b"\x1b":
        return "esc"
    return ch.decode("utf-8", "ignore") or None


def _read_key_posix():
    import termios
    import tty

    fd = sys.stdin.fileno()
    try:
        old = termios.tcgetattr(fd)
    except termios.error:
        return None
    try:
        tty.setraw(fd)
        c = sys.stdin.read(1)
        if c == "\x1b":
            if sys.stdin.read(1) == "[":
                return {"C": "right", "D": "left", "A": "up", "B": "down"}.get(sys.stdin.read(1), "esc")
            return "esc"
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
    if c == "\x03":
        raise KeyboardInterrupt
    return c


def read_key():
    """读一个按键（含方向键）；非交互终端返回 None，调用方据此退出交互循环。"""
    if not sys.stdin.isatty():
        return None
    return _read_key_windows() if sys.platform == "win32" else _read_key_posix()
