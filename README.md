# ibox

> 不用记命令名，说出想做的事就行。

`ibox` 是给**不写代码的人**用的终端小帮手：

- **我想做件事，但不知道命令** → `ibox 端口被谁占用`，给你一张可信的命令卡：怎么敲、示例、容易踩的坑。
- **AI 在我的终端里跑了条命令，我想看懂** → `ibox explain`（开发中，见路线图）。

同一套「意图卡」分别写了 **macOS** 和 **Windows** 的做法：在哪个系统上用，就看到哪个系统的命令；按 `t` 可以看另一个系统怎么做。

## 安装

暂时需要 Python 3.9+（之后会提供免安装的单文件版本）：

```bash
git clone https://github.com/OGGIoao/ibox.git
cd ibox
python -m pip install -e .
```

## 用法

```bash
ibox                        # 开场屏：直接输入想做的事
ibox 哪个程序最占内存        # 查命令
ibox how 磁盘还剩多少 -c     # 把最佳命令复制到剪贴板
ibox how -l                 # 列出全部卡片
ibox learn                  # 按分类学习（目录 + 进度）
ibox learn 网络              # 过某一类
ibox learn --due            # 只看该复习的
ibox --platform mac 看CPU型号   # 看另一个系统的做法
```

浏览卡片时：`n` 下一张 · `p` 上一张 · `c` 复制命令 · `t` 切换平台 · `/` 重新搜索 · `q` 退出。

装了 [Ollama](https://ollama.com) 并拉取嵌入模型（推荐 `ollama pull bge-m3`）时，会自动启用语义检索，近义说法也能命中；没装也完全可用。加 `--no-ai` 可强制只用离线检索。

## 自己加卡

`ibox card dir` 显示自定义卡目录。在那里放 `.md` 文件，格式与 [`src/ibox/data/cards/`](src/ibox/data/cards/) 里的内置卡相同；同 `id` 会覆盖内置卡。写完跑 `ibox card check` 检查格式。

```markdown
# 我的分类

## 查看端口被谁占用
- id: port-owner
- 别名: 端口占用,查端口,谁占了端口
- 作用: 查看哪个程序占用了某个网络端口

### mac
- 命令: lsof
- 用法: `lsof -i :<端口>`
- 示例: `lsof -i :3000`
- 踩坑: 查不到时可能需要 sudo

### win
- 命令: Get-NetTCPConnection
- 用法: `Get-NetTCPConnection -LocalPort <端口>`
```

## 路线图

| 阶段 | 内容 | 状态 |
|---|---|---|
| M1 | 新包结构、意图卡 + mac / win 双实现、统一检索引擎 | ✅ |
| M2 | `ibox explain`：拆解 bash / PowerShell 命令，逐段说明并标注风险 | 计划中 |
| M3 | macOS / Windows 免安装单文件版；接入 Claude Code hook，Agent 跑命令前自动解释 | 计划中 |

## License

MIT
