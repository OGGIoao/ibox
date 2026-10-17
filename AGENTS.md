# AGENTS.md

给接手开发的人或 AI Agent。产品说明看 [README.md](README.md)。

## 产品定位

即插即用的终端小帮手，用户是**不写代码的人**。两个场景：

1. **意图 → 命令**（`ibox how`）：说想做的事，给出可信的命令卡。
2. **命令 → 解释**（`ibox explain`，M2）：看懂 AI Agent 在终端里跑的命令，逐段说明并标注风险。

两个发行版：macOS 与 Windows，**同一套代码、同一个意图卡库**，只是展示不同平台的实现。

## 结构

```
src/ibox/
├── cli.py        命令行入口与子命令（how / learn / card）
├── cards.py      意图卡格式、解析、加载（内置 + 用户目录）、校验
├── search.py     离线打分 + 可选语义融合
├── semantic.py   ollama embeddings（可选，只用标准库）
├── state.py      最近查看 / 复习 / 学到的说法（一个 JSON）
├── ui.py         卡面渲染、交互浏览、开场屏
├── env.py        平台判断、配置目录、UTF-8、剪贴板、按键——所有系统差异只在这里
└── data/cards/   内置卡，一个文件一个分类，文件名数字前缀决定分类顺序
```

## 规则

- **零第三方依赖**，只用标准库：将来要打包成单文件，依赖越少越稳。
- **离线检索永远可用**；ollama 只做加成。语义分被归一到 `[0, SEMANTIC_W]`，清晰的本地命中必须压住语义——不要改成纯语义排序（短中文在嵌入空间区分度很差，曾把「kill」排到「type」后面）。
- 改检索逻辑或卡片别名后，`tests/test_search.py` 的 golden queries 必须在 mac / win 两个平台都通过；发现新的「搜不准」就加一条进去。
- 卡片格式见 `cards.py` 顶部说明。每张内置卡都要有 `### mac` 与 `### win` 两段（测试强制）；某个平台确实没有做法时，在「用法」里写清楚替代方案。
- 系统差异只写在 `env.py`，其他模块不判断 `sys.platform`。
- 所有输出前调用 `ensure_utf8_stdio()`：Windows 默认代码页（cp936 / cp1252）下中文会崩。`tests/test_cli.py` 用 `PYTHONIOENCODING=cp1252` 守着它。
- 用户数据在 `~/.config/ibox/`（`IBOX_HOME` 可覆盖，测试用它隔离）。内置卡只读、随包发布，不再往用户目录复制一份。

## 开发

```bash
python -m pip install -e .
python -m unittest discover -s tests
ibox card check
```

## 协作

用户是从 Windows 转 macOS 的新手：讲解时对照 Windows 概念，重大改动先给诊断和选项，让用户拍板再实现。
