# M2.3 源码拆解｜本机 DIY 反馈

## Architecture Map

[`cli.py`](../../src/ibox/cli.py) 处理输入和工具菜单。[`ui.py`](../../src/ibox/ui.py) 显示端口入口提示和分色结果。[`env.py`](../../src/ibox/env.py) 负责输出目录设置和调用 Windows PowerShell。[`Inspect-File.ps1`](../../src/ibox/data/tools/file-spirit/src/Inspect-File.ps1) 负责原生窗与导出。

## Execution Flow

- 交互终端启动一次 `show_home`，显示 ASCII 小向导并进入单个输入提示。`/tools` 或 `/` 列出 `/port`、`/roots` 和 `/file`。`/map` 展开四层，`/exit` 退出。
- `_diagnostics_home` 在会话内保留工具列表的筛选词。回车在输入区和工具列表之间切换，`_matching_tools` 按名称、用途或关键词筛选。每件工具返回后重新显示当前筛选结果。
- `show_layer_map` 按灯下世界观将故事场景、系统机制和可体验的工具放在一起。地图与列表使用同一份工具编号。文件精灵从地表可见的文件连到深层的内容对比。根系探测器与端口查询从地层观察系统记录和正在运行的程序。从地图打开工具后，返回时恢复地图。
- 查端口调用 `show_port_help` 展示三个实际位置。输入中的本机 URL 由 `_parse_guided_port` 提取端口，再走现有 TCP 监听查询。
- 根系探测器从 `root_records_dir` 读取当前位置。更改后用 `set_root_records_dir` 保存路径设置，并把路径交给原有的报告或快照入口。清理通过资源管理器选文件。
- 文件精灵用系统对话框选文件，调用 `Summon-FileSpirit.ps1 -InfoOnly` 获得文件信息和指纹。窗体字段为只读，另存按钮调用 `Export-Inspection` 生成文本。打开和对比没有输出文件。

## Key Files

- `cli.py` 的 `_parse_guided_port`、`_guided_root_probe` 和 `_guided_file_spirit`。
- `env.py` 的 `set_root_records_dir` 和 `run_bundled_tool`。
- `Inspect-File.ps1` 的 `Get-Inspection`、`Compare-Inspection` 和 `Export-Inspection`。

## Why

先告诉用户可以去哪里找端口号，再接受现成的本机地址。暖色用于标题和输入提示，术语解释在详情里。根系记录单独保存一个可更改的位置，旧报告继续留在原路径。原生文件窗直接查看结果，减少每查一次就自动生成的文件。

## Alternatives

可以继续在浏览器显示文件信息，模板与独立玩具更容易共用，用户仍要切换窗口。原生窗复用指纹计算，标题、复制、对比、另存功能直接在同一窗口完成。自动按期限删文件需要定义何时仍在使用，现阶段在目录中由使用者决定。

## Recommended Reading Order

1. 花 5 分钟在查端口里试一次本机地址，展开结果依据。
2. 花 8 分钟从 `_guided_root_probe` 顺到保存路径设置和原探测器。
3. 花 12 分钟读文件精灵的窗体、对比和导出调用。
4. 花 5 分钟对照 [输入与目录测试](../../tests/test_cli.py)。
