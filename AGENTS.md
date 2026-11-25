# AGENTS.md

给接手开发的人或 AI Agent。产品说明看 [README.md](README.md)。

## 产品定位

产品定位以 [README.md](README.md) 为准。先做 Windows，按用户任务组织命令查阅与本机工具，帮助减少命令和参数的记忆负担。阶段边界以 [NOW.md](NOW.md) 链接的当前 Milestone 为准。

工具目录和交互入口分别在 `ui.py` 与 `cli.py`，Windows 查询及随包工具的脚本调用集中在 `env.py`。卡片维护沿用下面的规则。

本仓库承接数字文明的公开工具产出。恢复工作先读根目录 [README](README.md)、[NOW](NOW.md) 和 [当前阶段](CURRENT_MILESTONE.md)。使用者的操作说明在 [docs/guide.md](docs/guide.md)，工程入口在 [docs/development.md](docs/development.md)，仓库关系在 [docs/repository-roles.md](docs/repository-roles.md)。

## 面向新手的界面规则

- 假设用户第一次排查电脑问题。每个功能从用户能认出的现象出发，例如「报错说端口被占用」或「一登录就有程序自己打开」。
- 首页用一两句话说明 iBox 能帮用户查什么，以及查询只读取本机信息。首页只列可用的入口，并明确告诉用户怎么选、下一步填什么和怎么返回。
- 第一次出现必要术语时，就地用一句话解释。例如「端口号是程序等连接时用的编号，通常能在报错里找到」和「进程编号（PID）是 Windows 给这次运行分配的编号」。需要用户输入时，给一个示例并告诉用户去哪里找真实值。
- 结果先回答用户的问题，再按需展开字段含义、查询依据和命令。解释查到的结果、没查到和读不到分别意味着什么，并给出对应的下一步。动画只提示查询或结果的变化，关掉动画也能看懂界面。
- 验收时让一个从未用过 iBox 的人从首页完成一次查询。观察对方能否自己选到入口、填对输入，并说出结果里最重要的一条信息。

## 结构

```
src/ibox/
├── cli.py        命令行入口与子命令（port / how / learn / card）
├── cards.py      意图卡格式、解析、加载（内置 + 用户目录）、校验
├── search.py     离线打分 + 可选语义融合
├── semantic.py   ollama embeddings（可选，只用标准库）
├── state.py      最近查看 / 复习 / 学到的说法（一个 JSON）
├── ui.py         卡面渲染、交互浏览、开场屏
├── env.py        平台判断、本机查询、配置目录、UTF-8、剪贴板、按键
└── data/
    ├── cards/   内置卡，一个文件一个分类
    └── tools/   随安装包交付的 PowerShell、JS 和模板
```

## 规则

- **零第三方依赖**，只用标准库：将来要打包成单文件，依赖越少越稳。
- **离线检索永远可用**；ollama 只做加成。语义分被归一到 `[0, SEMANTIC_W]`，清晰的本地命中必须压住语义——不要改成纯语义排序（短中文在嵌入空间区分度很差，曾把「kill」排到「type」后面）。
- 改检索逻辑或卡片别名后，`tests/test_search.py` 的 golden queries 必须在 mac / win 两个平台都通过；发现新的「搜不准」就加一条进去。
- 卡片格式见 `cards.py` 顶部说明。每张内置卡都要有 `### mac` 与 `### win` 两段（测试强制）；某个平台确实没有做法时，在「用法」里写清楚替代方案。
- 系统差异只写在 `env.py`，其他模块不判断 `sys.platform`。
- 所有输出前调用 `ensure_utf8_stdio()`：Windows 默认代码页（cp936 / cp1252）下中文会崩。`tests/test_cli.py` 用 `PYTHONIOENCODING=cp1252` 守着它。
- 用户数据在 `~/.config/ibox/`（`IBOX_HOME` 可覆盖，测试用它隔离）。内置卡只读、随包发布，不再往用户目录复制一份。
- 私人系统学习文章在数字文明的本机 `learn/` 中维护。随工具公开的文档以用法、必要原理和当前源码为内容。

## 开发

```bash
python -m pip install -e .
python -m unittest discover -s tests
ibox card check
```

## 协作

用具体的系统现象讲解。重大改动先给诊断和选项，由老李确认后实施。
