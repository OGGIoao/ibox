# M2.2 源码拆解｜灯下工具目录

## Architecture Map

[`ui.py`](../../src/ibox/ui.py) 显示四层地图和工具目录。[`cli.py`](../../src/ibox/cli.py) 根据编号进入各自的引导。[`env.py`](../../src/ibox/env.py) 启动 Windows 自带的 PowerShell，并调用 [包内运行文件](../../src/ibox/data/tools)。

## Execution Flow

- 查端口沿用 [M2 查询链路](milestone-M2-source-guide.md)。
- 根系探测器通过工具编号 2 进入勘探或快照。脚本复用 Windows 软件记录采集，报告和快照写到 iBox 用户目录。
- 文件精灵通过工具编号 3 接收文件位置。脚本计算 SHA-256，并把结果交给原有网页模板和像素精灵渲染。

## Key Files

- `cli.py` 的 `_diagnostics_home`、`_guided_root_probe` 和 `_guided_file_spirit`。
- `env.py` 的 `run_bundled_tool` 从固定表中选择脚本，把输入编成 JSON 后通过子进程环境传入，PowerShell 再用参数集合调用脚本。模块从 Windows PowerShell 自己的目录加载，避免从 PowerShell 7 启动时加载另一版本的模块。
- [`pyproject.toml`](../../pyproject.toml) 的 `package-data` 将两件工具的运行脚本、模板、JS 及许可证装进 wheel。

## Why

已有采集和绘图功能继续在数字文明的 `toys/` 下维护。iBox 随包提供运行副本，安装到另一台电脑也能找到脚本。代价是更新上游工具时要把对应的 `src` 运行文件同步到 `src/ibox/data/tools/`，保留 PowerShell 文件的 UTF-8 BOM，再重新构建。根系探测器的 `RecordsDir` 允许集成方指定工具自己的数据位置，单独运行时使用原来的 `records` 默认路径。

## Alternatives

直接从开发电脑的仓库路径启动，实现更短，但安装在没有仓库的电脑时无法运行。通用插件安装器能让工具独立发布，需要额外定义发现、更新和权限记录。首批工具可以通过现有 Python 安装包分发。

## Recommended Reading Order

1. 花 5 分钟从首页各打开一次三个工具，观察输入和产物。
2. 花 10 分钟读 `cli.py` 的分发、软件名和文件位置处理。
3. 花 8 分钟读 `env.py` 中的脚本路径与参数传递。
4. 花 7 分钟挑一个包内 PowerShell 入口，顺着它读到浏览器输出。
