# AGENTS.md — terminal-list 接手入口

> 任何 AI Agent（WorkBuddy / Claude Code / Codex / Cursor 等）或人接手本项目前，先读此文件。
> 本文件是仓库里**唯一必须首先读取**的入口。保持纯 markdown，不嵌入任何 Agent 私有格式。

## 1. 这是什么

- **个人终端工具箱**：一套自研 Python CLI 小工具集合，命令行卡片「即查即用、意图式搜索」。用户侧只有 **一个入口 `ibox`**（2026-09-14 起从 `c`/`pycheat`/`tk`/`hi`/`gup` 收敛而来，旧名保留为兼容壳）。
- 公开仓库：`https://github.com/OGGIoao/terminal-list`
- **真源原则**：本仓库是项目唯一真源。知识只存在于 `cheatsheet.md` 一份，代码与文档读取它，不复制维护两份。

## 2. 目录地图

| 路径 | 内容 |
|------|------|
| `terminal-toolbox/ibox` | **统一入口**（2026-09-14 起）：`how` / `find` / `add` / `done` / `ask` / `hi` / `sync` + 开场使用指南 |
| `terminal-toolbox/pycheat.py` | 命令卡引擎（检索 / 卡面渲染 / 交互浏览），被 `ibox how` 复用 |
| `terminal-toolbox/tk` + `tkcore.py` | 数据域层 + 共享引擎（note / log / gitx / clip / todo / explain / sum），被 `ibox` 复用 |
| `terminal-toolbox/cheatsheet.md` | 数据源（知识真源），48 张卡（含 8 张 ollama 卡） |
| `terminal-toolbox/ibox.cmd` / `pycheat.cmd` / `tk.cmd` + `install.ps1` | Windows 入口与一键安装 |
| `terminal-toolbox/ibox-使用说明.md` · `跨平台使用指南.md` · `tk-技术解读.md` | 文档 |
| `README.md` | 人类蓝图 |
| `个人终端工具箱.md` | 活文档（工具卡 + 用法 + 路线图） |
| `STATUS.md` / `MEMORY.md` | 当前状态 / 长期事实（本中枢） |
| `.workbuddy/memory/YYYY-MM-DD.md` | 工作日记（最近优先） |
| `操作系统底层与终端精通课程.md` | OS 底层与终端精通课程纵向主线（环境变量分裂 / 进程环境等） |
| `芯片架构横向博览知识系统.md` | 芯片架构横向博览（产业编年史式，行业 / 系统接口层） |
| `芯片架构内功/` | 芯片架构纵向深潜（微架构 / SIMT / MESI 等，含 6 动画 + 2 md） |
| `可视化放映/` | 概念动画与放映页（逻辑电路 / 芯片架构等交互演示，零依赖 HTML） |
| `OS第四卷-环境变量分裂-设计.md` | OS 第四卷系统化设计稿（待老Z确认后写正文） |
| `阶段总结-*.md` | 阶段性总结 |

## 3. 接手流程（启动必做）

1. 读 `AGENTS.md`（本文件）
2. 读 `STATUS.md`，确认当前主线、下一动作、阻塞
3. 读 `MEMORY.md`，掌握架构、约定与硬伤
4. 读 `daily/` 最近 1–2 篇（本仓库日记在 `.workbuddy/memory/`，如 `2026-09-05.md`）
5. 按需读 `README.md` / `个人终端工具箱.md` / `terminal-toolbox/` 文档（用 grep 检索，别全量读大文档）
6. 干活
7. 收尾：按 §5 更新状态、向日记 append、commit 到本仓库

## 4. 核心架构（必懂，否则易改坏）

- **单一数据源** `cheatsheet.md` + **适配器** `load_cards()`（markdown → 卡片 dict：name / 别名 / 作用 / 用法 / 示例 / 踩坑）+ **排序双路** + **展示层**。
- **排序双路（关注点分离）**：
  - 离线 `score_card()`：本地匹配（命名词 / 别名二元组 / 正文），零联网零依赖，永远可用。
  - ollama 语义：本机 embeddings 向量化，`fused_rank()` 融合排序（本地分占主导 + 语义相似度相对归一到 [0,1] × `SEMANTIC_W=15` 温和加成）。
  - **铁律**：强本地命中永远压住语义；零本地分的近义卡才被语义抬出。**不要改成纯语义替换**——`nomic-embed-text` 是英文向模型，短中文区分度差（全挤 0.5–0.66），纯语义会把 `kill` 误排到 `type` 后面。这条坑已踩过，回归代价大。
- `tkcore.py` 是 `tk` 套件的共享引擎，移植自 `pycheat`；**加新域 = 加一个适配器（采集函数），引擎不动**。
- **入口分层（2026-09-14）**：用户面只有 `ibox` 一个入口，它是**薄壳不造新引擎**——
  `how` 转调 `pycheat`、`find`/`add`/`done`/`ask` 转调 `tk`（动态加载无后缀脚本）、`hi`/`sync` 由 Python 实现（原 `hi.sh`/`gup.sh` 逻辑照搬，已跨平台）。
  旧名 `c` / `pycheat` / `tk` / `hi` / `gup` 全部保留，内部转调 `ibox`；**改入口名不得破坏用户肌肉记忆**。

## 5. 记忆写入协议（所有 Agent 统一）

- 实质工作后：向 `.workbuddy/memory/YYYY-MM-DD.md` append 简记（做了什么 / 结论 / 待办 / 踩坑）。
- 当前态变化 → 更新 `STATUS.md`（唯一当前态，避免多处重复维护）。
- 长期约定 / 偏好变化 → 原地更新 `MEMORY.md`（整体 ≤ 4000 字，纯 markdown）。
- **禁止**写入 Agent 私有注入块（`<system-reminder>`、专用 YAML 指令块、`<!-- ... -->` 控制标记）。中枢文件必须纯 markdown，任何 Agent 与 Obsidian 都能无损读取。
- 提交：先 `git status --short` 与 `git diff --check`，**只 add 本任务明确涉及的文件**；禁止 `git add -A`。一句结论式 commit message，让演进有历史、跨机可同步。

## 6. 红线（务必遵守）

- ⚠️ **不在公开仓库恢复 / 新增指向 iCloud 或其他私有路径的软链**（如 `AGENTS.md` → `iCloud/...`）。此前那份软链已移为 `.icloud.bak` 且不提交；本仓库现用自包含 `AGENTS.md` / `CLAUDE.md` / `STATUS.md` / `MEMORY.md`，已纳入 git。
- 不复制 `cheatsheet.md` 内容进代码或文档做第二份维护（单一数据源纪律）。
- ✅ **保持单入口**：新增能力请做成 `ibox` 的子命令，**不要再起新的顶层命令名**。用户面已从 5 个名字收敛到 1 个（`c`/`pycheat`/`tk`/`hi`/`gup` 各自为政就是反面教材）；用户明说「不想越来越臃肿」。
- git 安全：只 add 明确涉及的文件；**绝不 `git rm` / `git reset --hard`**；个人目录操作走 `gup` 红线（ff-only，不 rm）。
- 自动化数据 `~/.workbuddy/workbuddy.db` 绝不用 `rm` / `sqlite3` / shell 删，只用自动化管理工具。
- 改排序 / 语义逻辑前，先读 `MEMORY.md` §2 与 `pycheat.py` 的 `fused_rank` 实现，避免回归纯语义翻车。

## 7. 协作风格（用户偏好，2026-08-27/28 指定）

- 用户从 Windows 转 macOS 的新手；讲解对照 Windows 概念、多用图示，不默认其熟悉 unix 习惯。
- **先商量再动手**：先给诊断 + 建议 + 带选项提问，让用户拍板关键分叉，再实现（重大改动尤其如此）。
- 用户自称「老Z」，称呼前助手为「小o」（仅该会话有效；接手人按实际对话对象调整称呼，不必沿用小o）。

## 8. 自举：在其他 Agent 项目接入本中枢

- 本仓库已是自包含中枢。若要在别处复用，把 `AGENTS.md` / `CLAUDE.md` 软链到目标项目根（内容同源）：
  `ln -s "<本仓库>/AGENTS.md" ./AGENTS.md` 与 `./CLAUDE.md`。
- 接手后 Agent 读 `AGENTS.md` → 按 §3 接手 → 按 §5 写记忆并 commit。
- 真源不变：所有 Agent 写回同一仓库，记忆不锁死在单一工具，换 Agent 不失忆。
