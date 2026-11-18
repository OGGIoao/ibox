"""以子进程跑真实 CLI：覆盖入口路由与 Windows 非 UTF-8 代码页下的中文输出。"""
import io
import os
import socket
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from ibox.cli import main

SRC = Path(__file__).resolve().parents[1] / "src"


def run(*args):
    with tempfile.TemporaryDirectory() as home:
        env = dict(os.environ, IBOX_HOME=home, PYTHONPATH=str(SRC), PYTHONIOENCODING="cp1252",
                   PYTHONDONTWRITEBYTECODE="1")
        return subprocess.run(
            [sys.executable, "-m", "ibox", *args], env=env, text=True, encoding="utf-8",
            capture_output=True, stdin=subprocess.DEVNULL, timeout=30, check=False,
        )


class CliTests(unittest.TestCase):
    def test_windows_home_guides_first_query_and_explains_evidence(self):
        row = {"address": "127.0.0.1", "pid": 8420, "name": "node", "path": r"C:\Example\node.exe"}
        with (
            patch("ibox.cli.current_platform", return_value="win"),
            patch("sys.stdin.isatty", return_value=True),
            redirect_stdout(io.StringIO()) as output,
            patch.object(output, "isatty", return_value=True),
            patch("builtins.input", side_effect=["1", "oops", "http://localhost:3000/", "3", "2", "1", "3001", "0", "0"]),
            patch("ibox.cli.query_tcp_listeners", side_effect=[RuntimeError("查询超时"), [row], []]) as query,
        ):
            main([])
        text = output.getvalue()
        self.assertIn("< _>", text)
        world = text.index("屏幕底下藏着一个叫「灯下」的世界。")
        purpose = text.index("查看这台电脑上的程序、软件记录和文件。")
        self.assertLess(world, purpose)
        self.assertLess(purpose, text.index("/tools 查看工具"))
        startup = text.split("浏览器地址栏", 1)[0]
        self.assertNotIn("可用工具", startup)
        self.assertNotIn("文件精灵", startup)
        self.assertIn("可用工具", text)
        self.assertEqual(text.count("· 灯下"), 1)
        self.assertIn("浏览器地址栏", text)
        self.assertIn("程序启动窗口", text)
        self.assertIn("报错或软件设置", text)
        self.assertIn("请输入 1 到 65535", text)
        self.assertIn("这次查询没有成功。请再试一次", text)
        self.assertIn("正在使用端口 3000 的程序\n  node", text)
        self.assertIn("进程编号（PID）", text)
        self.assertIn("Get-NetTCPConnection", text)
        self.assertIn(row["path"], text)
        self.assertIn("当前没查到在端口 3001 等待 TCP 连接的程序", text)
        self.assertEqual([call.args for call in query.call_args_list], [(3000,), (3000,), (3001,)])

    def test_home_accepts_port_questions_and_asks_when_number_is_unclear(self):
        inputs = [
            "谁在用 3000？", "3", "0", "",
            "我的电脑 16G，内存占用高",
            "端口 3000 和 3001 谁在用", "3001", "0",
            "1", "3002", "0",
            "3003 有程序在用吗？", "0",
            "/port http://localhost:3004/", "0",
            "/map", "/", "/tools", "/exit",
        ]
        with (
            patch("ibox.cli.current_platform", return_value="win"),
            patch("sys.stdin.isatty", return_value=True),
            redirect_stdout(io.StringIO()) as output,
            patch.object(output, "isatty", return_value=True),
            patch("builtins.input", side_effect=inputs),
            patch("ibox.cli.query_tcp_listeners", return_value=[]) as query,
        ):
            main([])
        text = output.getvalue()
        self.assertIn("按回车或输入 /tools 找工具", text)
        self.assertIn("请指定一个要查的端口号", text)
        layer_map = text.split("灯下 · 四层地图", 1)[1].split("可用工具", 1)[0]
        self.assertNotIn("故事里", layer_map)
        self.assertNotIn("电脑里", layer_map)
        self.assertIn("[3] 文件精灵", layer_map.split("地层", 1)[0])
        active_layer = layer_map.split("地层", 1)[1].split("深层", 1)[0]
        self.assertIn("[2] 根系探测器", active_layer)
        self.assertIn("[1] 查端口", active_layer)
        self.assertIn("[3] 文件精灵", layer_map.split("深层", 1)[1].split("核心", 1)[0])
        self.assertIn("处理器（CPU）", layer_map.split("核心", 1)[1])
        self.assertIn("[1] 查端口", text)
        self.assertIn("找占用端口的程序  /port", text)
        self.assertEqual([call.args[0] for call in query.call_args_list], [3000, 3000, 3001, 3002, 3003, 3004])

    def test_map_numbered_tools_return_to_map(self):
        inputs = ["/map", "8", "1", "3000", "0", "2", "0", "3", "", "/exit"]
        with (
            patch("ibox.cli.current_platform", return_value="win"),
            patch("sys.stdin.isatty", return_value=True),
            redirect_stdout(io.StringIO()) as output,
            patch.object(output, "isatty", return_value=True),
            patch("builtins.input", side_effect=inputs),
            patch("ibox.cli.query_tcp_listeners", return_value=[]) as query,
            patch("ibox.cli.root_records_dir", return_value=Path("records")),
            patch("ibox.cli.run_bundled_tool") as launch,
        ):
            main([])
        maps = output.getvalue().split("灯下 · 四层地图")
        self.assertEqual(len(maps), 6)
        self.assertIn("请输入地图上显示的工具编号", maps[1])
        self.assertIn("端口 3000", maps[2])
        self.assertIn("[1] 查软件", maps[3])
        self.assertIn("在打开的窗口选择一个文件", maps[4])
        self.assertNotIn("可用工具", output.getvalue())
        query.assert_called_once_with(3000)
        launch.assert_called_once()
        self.assertEqual(launch.call_args.args, ("file-spirit",))

    def test_tool_picker_returns_to_current_filter_after_running_tools(self):
        inputs = ["", "指纹", "3", "/tools 卸载", "2", "0", "", "/exit"]
        with (
            patch("ibox.cli.current_platform", return_value="win"),
            patch("sys.stdin.isatty", return_value=True),
            redirect_stdout(io.StringIO()) as output,
            patch.object(output, "isatty", return_value=True),
            patch("builtins.input", side_effect=inputs),
            patch("ibox.cli.run_bundled_tool") as launch,
        ):
            main([])
        text = output.getvalue()
        self.assertEqual(text.count("可用工具 · 指纹"), 2)
        self.assertEqual(text.count("可用工具 · 卸载"), 2)
        file_search = text.split("可用工具 · 指纹", 1)[1].split("输编号打开", 1)[0]
        self.assertIn("[3] 文件精灵", file_search)
        self.assertNotIn("根系探测器", file_search)
        self.assertIn("[1] 查软件", text)
        launch.assert_called_once()
        self.assertEqual(launch.call_args.args, ("file-spirit",))

    def test_toolbox_routes_existing_tools_to_separate_user_outputs(self):
        with tempfile.TemporaryDirectory() as home:
            root = Path(home).resolve()
            inputs = ["/roots", "1", "微软 Python", "/roots", "2", "/file", "0"]
            records = root / "tools" / "root-probe" / "records"
            with (
                patch("ibox.cli.current_platform", return_value="win"),
                patch("sys.stdin.isatty", return_value=True),
                redirect_stdout(io.StringIO()) as output,
                patch.object(output, "isatty", return_value=True),
                patch("builtins.input", side_effect=inputs),
                patch("ibox.cli.config_dir", return_value=root),
                patch("ibox.cli.root_records_dir", return_value=records),
                patch("ibox.cli.run_bundled_tool") as launch,
            ):
                main([])
            cards = str(root / "tools" / "file-spirit" / "cards")
            probe, snapshot, spirit = launch.call_args_list
            self.assertEqual((probe.args, probe.kwargs), (("root-probe",), {"Keyword": "微软 Python", "RecordsDir": str(records)}))
            self.assertEqual((snapshot.args, snapshot.kwargs), (("root-snapshots",), {"RecordsDir": str(records)}))
            self.assertEqual((spirit.args, spirit.kwargs), (("file-spirit",), {"LegacyCards": cards}))

    def test_root_probe_remembers_custom_output_and_opens_only_that_folder(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary).resolve()
            chosen = base / "另一个 位置"
            records = chosen / "iBox-根系记录"
            records.mkdir(parents=True)
            old_file = records / "旧报告.html"
            old_file.write_text("keep", encoding="utf8")
            inputs = ["2", "3", str(chosen), "0", "2", "4", "1", "Python", "0"]
            with (
                patch("ibox.cli.current_platform", return_value="win"),
                patch("sys.stdin.isatty", return_value=True),
                redirect_stdout(io.StringIO()) as output,
                patch.object(output, "isatty", return_value=True),
                patch("builtins.input", side_effect=inputs),
                patch("ibox.env.config_dir", return_value=base / "config"),
                patch("ibox.cli.open_output_dir") as open_folder,
                patch("ibox.cli.run_bundled_tool") as launch,
            ):
                main([])
            open_folder.assert_called_once_with(records)
            launch.assert_called_once_with("root-probe", Keyword="Python", RecordsDir=str(records))
            self.assertEqual(old_file.read_text(encoding="utf8"), "keep")

    def test_redirected_bare_command_still_prints_usage(self):
        result = run()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("ibox port 3000", result.stdout)
        self.assertNotIn("/map 四层说明", result.stdout)

    @unittest.skipUnless(sys.platform == "win32", "需要 Windows TCP 查询")
    def test_port_reports_real_listener_and_empty_result(self):
        with socket.socket() as listener:
            listener.bind(("127.0.0.1", 0))
            port = str(listener.getsockname()[1])

            empty = run("port", port)
            self.assertEqual(empty.returncode, 0, empty.stderr)
            self.assertIn("当前没有监听记录", empty.stdout)

            listener.listen()
            result = run("port", port)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(f"127.0.0.1  ·  PID {os.getpid()}  ·", result.stdout)
            self.assertIn("程序路径  ", result.stdout)

    def test_port_rejects_invalid_number(self):
        for port in ("0", "65536", "abc"):
            with self.subTest(port=port):
                result = run("port", port)
                self.assertEqual(result.returncode, 2)
                self.assertIn("端口号须为 1 到 65535 的整数", result.stderr)

    def test_port_keeps_listener_if_process_details_are_missing(self):
        rows = [
            {"address": "::", "pid": 123, "name": "worker", "path": None},
            {"address": "127.0.0.1", "pid": 456, "name": None, "path": None},
        ]
        with patch("ibox.cli.query_tcp_listeners", return_value=rows), redirect_stdout(io.StringIO()) as output:
            with self.assertRaises(SystemExit) as exit_info:
                main(["port", "3000"])
        self.assertEqual(exit_info.exception.code, 0)
        self.assertIn("::  ·  PID 123  ·  worker", output.getvalue())
        self.assertIn("程序路径不可读", output.getvalue())
        self.assertIn("127.0.0.1  ·  PID 456  ·  进程详情不可用", output.getvalue())

    def test_port_failure_is_not_reported_as_empty(self):
        failure = subprocess.CalledProcessError(1, "powershell")
        with patch("ibox.env.current_platform", return_value="win"), patch("ibox.env.subprocess.run", side_effect=failure):
            with redirect_stdout(io.StringIO()) as output, redirect_stderr(io.StringIO()) as errors:
                with self.assertRaises(SystemExit) as exit_info:
                    main(["port", "3000"])
        self.assertEqual(exit_info.exception.code, 1)
        self.assertEqual(output.getvalue(), "")
        self.assertIn("查询失败", errors.getvalue())

    def test_bare_query_routes_to_how(self):
        r = run("--no-ai", "--platform", "win", "端口被谁占用")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Get-NetTCPConnection", r.stdout)
        self.assertIn("在 macOS 上", r.stdout)

    def test_platform_switch(self):
        r = run("how", "--no-ai", "端口被谁占用", "--platform", "mac")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("lsof", r.stdout)
        self.assertIn("在 Windows 上", r.stdout)

    def test_no_match_exits_nonzero(self):
        r = run("--no-ai", "zzqqxx")
        self.assertEqual(r.returncode, 1)
        self.assertIn("没找到", r.stdout)

    def test_list(self):
        r = run("how", "-l")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("网络与远程", r.stdout)

    def test_card_check(self):
        r = run("card", "check")
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("全部合规", r.stdout)

    def test_learn_overview(self):
        r = run("learn")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("硬件与系统信息", r.stdout)

    def test_user_card_overrides_builtin(self):
        with tempfile.TemporaryDirectory() as home:
            (Path(home) / "cards").mkdir()
            (Path(home) / "cards" / "mine.md").write_text(
                "# 我的\n\n## 我的磁盘空间\n- id: disk-free\n- 别名: 看空间\n- 作用: 自定义\n\n"
                "### win\n- 用法: `my-df`\n", encoding="utf-8")
            env = dict(os.environ, IBOX_HOME=home, PYTHONPATH=str(SRC))
            r = subprocess.run([sys.executable, "-m", "ibox", "--no-ai", "--platform", "win", "看空间"],
                               env=env, text=True, encoding="utf-8", capture_output=True,
                               stdin=subprocess.DEVNULL, timeout=30)
        self.assertIn("my-df", r.stdout)


if __name__ == "__main__":
    unittest.main()
