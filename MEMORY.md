# terminal-list 长期记忆（MEMORY.md）

> 本文件只存跨任务长期有效的事实与约定，不记当前进度（进度看 STATUS.md）。
> 接手顺序：AGENTS.md → STATUS.md → MEMORY.md → 最近日记 → 按需读专题文件。

## 1. 项目定位

- 2026-09-09 老李确认产品北极星为 **Personal Terminal Companion**：用人话找到并安全使用终端命令。
- 2026-09-14 老Z 决策：用户面入口收敛为唯一 `ibox`，**覆盖 ADR-001 两条 Non-Goal**（详见 ADR-002）。
- `pycheat` + `cheatsheet.md` 是正式产品核心；OS / Shell 课程是解释层；`tk` 是 Beta（冻结扩域）；芯片架构与非终端放映是内容实验区。
- M0 不拆仓、不改仓库名、不扩 `tk` 域，先建立可信测试与文档基线。正式边界见 `docs/00-project/scope.md`。
- 公开仓库：`https://github.com/OGGIoao/terminal-list`
- 设计审美：**可复用、可迁移、单一数据源（Source of Truth）**；零散能力要收束成统一入口，不堆积互不相关的小脚本（用户长期规矩）。

## 2. 架构（单一数据源 + 适配器 + 融合排序）

- **单一数据源**：`~/.config/cheat/cheatsheet.md`（当前 **59 张卡**，按 7 个功能域分区）。改卡 = 改这一个文件，存盘即生效。
- ⚠️ **数据源有两份**：用户级 `~/.config/cheat/cheatsheet.md`（实际生效）与仓库版 `terminal-toolbox/cheatsheet.md`（出厂副本）。同步用 `ibox card sync`，**不要手工 cp**（曾两次导致漂移）。
- **适配器**：`load_cards()` 把 markdown 翻译成结构化卡片 dict（分类 / 课卷 / 别名 / 作用 / 用法 / 示例 / 踩坑）。换数据格式只改这一个函数。
- **排序双路（关注点分离，可替换）**：
  - 离线 `score_card()`：本地匹配（命名词 / 别名二元组 / 正文命中打分），零联网零依赖，永远可用。
  - ollama 语义：`fused_rank()` = 本地分占主导 + 语义相似度相对归一到 [0,1] × `SEMANTIC_W=15` 温和加成。**强本地命中永远压住语义；零本地分的近义卡才被语义抬出**。
  - ⚠️ **铁律**：不要改回纯语义替换。`nomic-embed-text` 是英文向，短中文区分度差（全挤 0.5–0.66），纯语义会把 `kill` 误排到 `type` 后。已踩过坑。
  - 已知精度缺陷（非故障、未修）：`score_card` 对「文件 / 进程」这类高频通用词区分度不足 —— 长句如「怎么把文件传到另一台机器」首位是 `stat` 而非 `scp`。
- **展示层**：开场屏（推荐 / 间隔复习 / 语义提示）/ 卡面四段彩色 / 复制 / 间隔复习。

## 3. 工具清单（用户面单入口）

| 工具 | 形态 | 用途 |
|------|------|------|
| **ibox**（短名 `c`） | Python CLI（`ibox`） | **唯一用户入口**：`how` 查命令 · `find` 搜自己数据 · `add`/`done` 记与完成 · `ask` 问本地模型 · `hi` 机器信息 · `sync` 一键 git 同步 · `learn` 学习模式 · `card` 卡库注册与体检 |
| `pycheat.py` | 引擎 | 命令卡检索 / 卡面渲染 / 交互浏览；被 `ibox how` 复用，旧名 `pycheat` 仍可用 |
| `tk` + `tkcore.py` | 引擎 | 数据域层 + 共享引擎（note / log / gitx / clip / todo / explain / sum）；被 `ibox find`/`add`/`ask` 复用 |
| `hi.sh` / `gup.sh` | bash（旧） | 已被 `ibox hi` / `ibox sync`（Python 版，Windows 亦可用）取代 |

- **ibox 是薄壳不造引擎**：`how` 转调 pycheat、`find`/`add`/`done`/`ask` 转调 tk（动态加载无后缀脚本）、`hi`/`sync` 为 Python 实现。旧名 `c`/`pycheat`/`tk`/`hi`/`gup` 全部保留为兼容壳。
- **tkcore.py** 是共享引擎（融合排序 + ollama 零依赖调用 + 模型感知缓存）；7 域只是「采集函数 + 存储」差异，引擎不动。
- 处理型域 `explain` / `sum` **需本机 chat 模型**（embedding 模型不能对话）。

## 4. 关键约定与硬伤

- **ollama 语义检索**：默认 `nomic-embed-text`；本机已装 **bge-m3** 并被 `resolve_embed_model()` 自动优先（中文区分度约 nomic 的 6–7 倍）。向量缓存按「内容 hash + 模型名」存 `~/.config/cheat/.pycheat_vectors.json`，换模型自动失效重建。
- **ollama 未运行时**语义增强会**静默降级**为纯离线（不报错，仅开场屏提示），近义 / 跨语言查询命中率下降 —— 排查检索异常时先确认 `:11434` 是否在跑（详见 P2）。
- **本机 ollama 形态**：`/Applications/Ollama.app`（CLI 在 `/usr/local/bin/ollama`），**无** brew service、**无** LaunchAgent → 用 `open -a Ollama` 启动，常驻菜单栏、不依赖任何会话。
- **零依赖**：只调标准库 `urllib` 调本机 `:11434`，不用 `requests` / `numpy`，避免污染环境（managed 隔离规矩）。
- **称呼约定**（用户指定，2026-08-27）：AI 助手名 = 小o，用户自称 = 老Z（仅该会话有效；接手人不必沿用）。
- **协作风格**（用户指定，2026-08-28）：先商量再动手——先给诊断 + 建议 + 带选项提问，让用户拍板关键分叉再实现。
- **用户背景**：从 Windows 转 macOS 的新手；讲解对照 Windows 概念、多用图示，不默认熟悉 unix 习惯。要深入底层、边讲边装、读一手资料。

## 5. 安装形态：软链直指仓库（2026-09-19 起）

- `~/bin/{ibox,tk,pycheat,gup,hi}` **直接指向本仓库** `terminal-toolbox/`。此前的 `~/terminal-toolbox/` 运行副本已退役为 `~/terminal-toolbox.retired-20260919`。**改仓库即改运行行为，不要再 cp 第二份**（运行副本模式曾三次导致漂移）。
- ⚠️ **脚本自身路径一律用 `os.path.realpath(__file__)`，禁用 `os.path.abspath(__file__)`**：软链调用时 `__file__` 保持软链路径不 realpath，`abspath` 会得到 `~/bin` —— 导致同目录 `tk` / `tkcore.py` / `cheatsheet.md` 定位失败、**新机器首次初始化静默失败**、并在 `~/bin` 写 `__pycache__`。三处已修（`ibox:32` / `pycheat.py:60` / `tk:29`）。
- **跨平台**：Windows 用 `pycheat.cmd` / `tk.cmd` / `ibox.cmd`，`install.ps1` 一键加 PATH + PowerShell 别名（幂等可重跑）；首次运行自动从同目录出厂副本初始化 cheatsheet。
- 剪贴板：darwin / win32 / WSL / X11 全分支已做。

## 6. 遗留与红线（接手人务必看）

- ⚠️ 仓库根的 `AGENTS.md` / `CLAUDE.md` 此前是 iCloud 软链（指向用户私有 Obsidian），**未纳入公开仓库**。现为自包含 `AGENTS.md` / `CLAUDE.md` / `STATUS.md` / `MEMORY.md`。**不要在公开仓库恢复 iCloud 软链**。
- 单一数据源纪律：`cheatsheet.md` 是知识真源，不复制内容进代码或文档再维护两份。
- 加卡走 `ibox card insert`（按「分类」自动归位），不要手工追加到文件末尾；改完跑 `ibox card check`。
- git 安全：只 add 本任务涉及文件；绝不 `git rm` / `reset`；个人目录走 `gup` 红线（ff-only，不 rm）。
- 自动化数据 `~/.workbuddy/workbuddy.db` 绝不用 `rm` / `sqlite3` / shell 删，只用自动化管理工具。
- **已知坑与已修 bug 不在本文件复述** —— 唯一归档地是 `docs/02-engineering/pitfalls.md`（`P1`…`P17`，每条固定「症状 / 根因 / 修法 / 防回归」）。改核心逻辑前先扫相关条目；修完新坑**当场**补一条，不要在本文件或 `daily/` 里再写一份。
