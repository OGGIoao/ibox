"""运行环境：当前平台、配置目录、UTF-8 输出、系统查询、剪贴板、按键读取。

所有「mac 和 Windows 不一样」的系统交互都收在这里，其余模块不判断 sys.platform。
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from tempfile import NamedTemporaryFile

PLATFORMS = ("mac", "win")
PLATFORM_LABEL = {"mac": "macOS", "win": "Windows"}
_BUNDLED_SCRIPTS = {
    "file-spirit": "file-spirit/src/Inspect-File.ps1",
    "root-probe": "root-probe/src/Probe.ps1",
    "root-snapshots": "root-probe/src/Snapshot.ps1",
}

_RUN_TOOL_SCRIPT = r"""
$ErrorActionPreference = 'Stop'
$env:PSModulePath = Join-Path $PSHOME 'Modules'
$arguments = @{}
$values = ConvertFrom-Json -InputObject $env:IBOX_TOOL_ARGUMENTS
foreach ($property in $values.PSObject.Properties) {
    $arguments[$property.Name] = $property.Value
}
& $env:IBOX_TOOL_SCRIPT @arguments
"""

_TCP_LISTENERS_SCRIPT = r"""
[Console]::OutputEncoding = [Text.UTF8Encoding]::new($false)
$ErrorActionPreference = 'Stop'
$port = [uint16]$env:IBOX_QUERY_TCP_PORT
try {
    $listeners = @(Get-NetTCPConnection -LocalPort $port -State Listen)
} catch {
    if ($_.FullyQualifiedErrorId -ne 'CmdletizationQuery_NotFound,Get-NetTCPConnection') {
        throw
    }
    $listeners = @()
}

$results = @(
    foreach ($listener in $listeners) {
        $name = $null
        $path = $null
        try {
            $process = Get-Process -Id $listener.OwningProcess
            $name = $process.ProcessName
            $path = $process.Path
        } catch {
            # Keep the listener and any process fields already read.
        }
        [pscustomobject]@{
            address = $listener.LocalAddress
            pid = $listener.OwningProcess
            name = $name
            path = $path
        }
    }
)
ConvertTo-Json -InputObject $results -Compress
"""


def current_platform():
    """卡片按 mac / win 两种实现组织；Linux 与 mac 同属 POSIX shell，暂用 mac 实现。"""
    return "win" if sys.platform == "win32" else "mac"


def _windows_powershell():
    system_root = Path(os.environ.get("SystemRoot", r"C:\Windows"))
    return str(system_root / "System32/WindowsPowerShell/v1.0/powershell.exe")


def run_bundled_tool(tool, **arguments):
    """运行随 iBox 分发的脚本，输入作为参数传入固定脚本。"""
    if current_platform() != "win":
        raise RuntimeError("这件工具目前在 Windows 上使用。")
    script = Path(__file__).resolve().parent / "data" / "tools" / _BUNDLED_SCRIPTS[tool]
    if not script.is_file():
        raise RuntimeError("安装包里缺少这件工具的文件，请重新安装 iBox。")
    try:
        subprocess.run(
            [_windows_powershell(), "-NoProfile", "-STA", "-ExecutionPolicy", "RemoteSigned", "-Command", _RUN_TOOL_SCRIPT],
            env=dict(os.environ, IBOX_TOOL_SCRIPT=str(script), IBOX_TOOL_ARGUMENTS=json.dumps(arguments)),
            check=True,
        )
    except OSError as exc:
        raise RuntimeError("无法启动 Windows PowerShell。") from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError("工具未完成。可以查看上面的提示后再试。") from exc


def query_tcp_listeners(port):
    """读取 Windows 本机指定端口的 TCP 监听记录和可用的进程详情。"""
    if current_platform() != "win":
        raise RuntimeError("本机端口查询目前仅支持 Windows。")
    try:
        result = subprocess.run(
            [_windows_powershell(), "-NoProfile", "-NonInteractive", "-Command", _TCP_LISTENERS_SCRIPT],
            env=dict(os.environ, IBOX_QUERY_TCP_PORT=str(port)),
            stdin=subprocess.DEVNULL, capture_output=True, encoding="utf-8", errors="replace",
            timeout=15, check=True,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("Windows 查询超时，请稍后重试。") from exc
    except OSError as exc:
        raise RuntimeError("无法启动 Windows PowerShell。") from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError("Windows 无法读取 TCP 监听信息。") from exc
    try:
        listeners = json.loads(result.stdout)
    except ValueError as exc:
        raise RuntimeError("无法读取 Windows 返回的查询结果。") from exc
    if not isinstance(listeners, list):
        raise RuntimeError("Windows 返回的查询结果格式有误。")
    return listeners


def config_dir():
    """用户数据目录：状态、向量缓存、自定义卡。IBOX_HOME 可覆盖（测试用）。"""
    return Path(os.environ.get("IBOX_HOME") or Path.home() / ".config" / "ibox")


def root_records_dir():
    home = (config_dir() / "tools" / "root-probe").resolve()
    try:
        selected = (home / "records-location.txt").read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        selected = ""
    return Path(selected) if Path(selected).is_absolute() else home / "records"


def set_root_records_dir(folder):
    home = (config_dir() / "tools" / "root-probe").resolve()
    home.mkdir(parents=True, exist_ok=True)
    selected = folder / "iBox-根系记录" if folder else home / "records"
    with NamedTemporaryFile(mode="w", encoding="utf-8", dir=home, delete=False) as file:
        temporary = Path(file.name)
        file.write(str(selected))
    try:
        temporary.replace(home / "records-location.txt")
    finally:
        temporary.unlink(missing_ok=True)
    return selected


def open_output_dir(folder):
    """在资源管理器中打开产物目录，由用户选择要保留或删除的文件。"""
    os.startfile(str(folder))


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
