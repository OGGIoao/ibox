# 命令卡

命令卡承接按任务查做法的核心路径，提供命令、参数示例和常见问题。当前先围绕 Windows 使用，卡库同时保留已有的 macOS 做法。

在 PowerShell 输入以下命令进入卡片功能。

```powershell
ibox how
ibox how --no-ai 端口被谁占用
ibox how 磁盘还剩多少 -c
ibox how -l
ibox learn
ibox learn 网络
ibox learn --due
ibox --platform mac 看CPU型号
```

`-c` 复制最佳匹配的示例，`-l` 列出卡片。`learn` 按分类浏览卡片，`--due` 显示按查看历史推荐的复习项。

浏览卡片时按 `n` 下一张、`p` 上一张、`c` 复制、`t` 切换平台、`/` 搜索、`q` 退出。

若本机已有 Ollama 和嵌入模型，搜索可以使用本机服务补充语义匹配。模型选择及请求位置见 [semantic.py](../src/ibox/semantic.py)。`--no-ai` 使用离线文字检索。

## 自己加卡

`ibox card dir` 显示自定义卡目录。在那里放 Markdown 文件，同一个 `id` 可以覆盖内置卡。格式参照 [内置卡](../src/ibox/data/cards)，写完运行 `ibox card check` 校验内置卡格式，自定义卡可通过查阅结果确认。

```markdown
# 我的分类

## 查看端口被谁占用
- id: port-owner
- 别名: 端口占用,查端口,谁占了端口
- 作用: 查看哪个程序占用了某个网络端口

### mac
- 命令: lsof
- 用法: lsof -i :<端口>
- 示例: lsof -i :3000

### win
- 命令: Get-NetTCPConnection
- 用法: Get-NetTCPConnection -LocalPort <端口>
```
