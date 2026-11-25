# iBox · 灯下工具箱

iBox 是面向普通用户的终端伴侣，帮你少背命令、看懂参数，并用本机工具核对结果。当前先做 Windows。

## 我们在做什么

- **查命令**：用「想做什么」找做法，按文件、程序与资源、网络与端口等任务组织。
- **用命令**：看用途、示例和需要替换的参数，再复制到终端使用；统一参数引导仍在设计中。
- **看懂执行**：回看 Agent 做过什么、命令怎样工作、结果有哪些依据。这部分处于原型验证，尚未进入正式菜单。

本机工具放在相应任务下。查端口属于「网络与端口」，查看进程属于「程序与资源」。

## 当前能用什么

当前版本为 **0.3.7**，提供 56 张命令卡与三项 Windows 本机工具。

| 你想做什么 | 当前入口 |
| --- | --- |
| 看内存、找占资源的程序 | 按白话查命令，例如 `ibox how --no-ai 哪个程序最占内存` |
| 查网络或端口 | 查命令；直接查本机 TCP 监听可用 `ibox port 3000` |
| 看磁盘、文件信息或比较文件 | 查命令；在交互界面用 `/file` 打开文件检查窗 |
| 看软件留下的记录、对比快照 | 在交互界面用 `/roots` 打开根系探测器 |

查命令会显示做法；本机查询入口会读取当前电脑的实际信息。0.3.7 的查卡与工具菜单仍使用两组入口，统一任务导航待实现。

## 第一次安装

需要 Windows、Python 3.9+ 和系统自带的 Windows PowerShell 5.1。

1. [下载源码 ZIP](https://github.com/OGGIoao/ibox/archive/refs/heads/main.zip) 并解压。
2. 在包含 `pyproject.toml` 的目录打开 PowerShell。
3. 安装后，先试一次离线命令查阅。

```powershell
python -m pip install --user .
python -m ibox how --no-ai 磁盘还剩多少
```

要使用本机工具，运行 `python -m ibox`，按回车查看列表。安装成功后也可直接输入 `ibox`。详细操作与返回方式见[使用说明](docs/guide.md)。

## 继续了解

- [命令查阅](docs/command-cards.md)：搜索、复制示例和自定义卡片。
- [使用说明](docs/guide.md)：本机查询、文件对比和结果保存。
- [开发指南](docs/development.md)：源码、测试与构建。
- [当前进度](NOW.md)：已完成的验证与后续工作。

游戏、世界观与视频由私有的数字文明项目维护，个人学习资料私有保存，职责见[仓库分工](docs/repository-roles.md)。

问题反馈见 [Issues](https://github.com/OGGIoao/ibox/issues)。代码采用 [MIT](LICENSE)，来源与形象说明见 [NOTICE](NOTICE.md)。
