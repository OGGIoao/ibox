# STATUS.md — terminal-list 当前状态

> 唯一当前态。更新进度 / 下一动作 / 阻塞时只改本文件，不在多处重复维护。
> 更新日期：2026-09-14

## 当前主线

个人终端工具箱已成型且全部推到 GitHub：主搜索 `pycheat`（离线 + ollama 融合语义）、跨域套件 `tk`（7 域）、跨平台（macOS / Windows）。最新提交 `9ab0cd4` 刚完成 Windows 支持。随后用户决定「换人接手」，故建立本仓库**自包含中枢**（`AGENTS.md` / `STATUS.md` / `MEMORY.md`，取代此前指向私人 iCloud 的软链），以便交接。2026-09-08 将工作区剩余未跟踪内容（OS 第四卷环境变量分裂设计稿、芯片架构内功深潜目录）全量提交推送，远程 `main` 现为 `e2b421c`，**工作区与 GitHub 完全对齐**——接手人 `git clone` 即获完整中枢，可直接接手。

2026-09-14 完成**入口收敛**：用户面从 5 个顶层命令（`c` / `pycheat` / `tk` / `hi` / `gup`）收敛为**唯一入口 `ibox`**（子命令 `how` / `find` / `add` / `done` / `ask` / `hi` / `sync`），旧名全部保留为兼容壳；同时修掉 3 处交互硬伤（Windows 翻页失效、浏览内重搜范围错、todo 不显示 id），`hi` / `gup` 用 Python 重写后 **Windows 也终于可用**。

## 已完成（按提交线）

1. init：三套核心文档（OS 课 / 芯片课 / 工具箱）
2. 仓库自包含化：去掉 Obsidian 软链，纳入脚本
3. 废弃旧版 `cheat`
4. 剪贴板跨平台化
5. 增量自学习别名 + 间隔复习
6. ollama 语义检索 → 融合排序（`bge-m3` 自动优先）
7. `bge-m3` 拉取成功 + 缓存模型感知修复 + 使用说明文档
8. ollama 卡实战示例 + `ollama show` 演示卡 + 速查小抄附录
9. `tk` 跨域套件（`tkcore` 引擎 + 7 域：note / log / gitx / clip / todo / explain / sum）
10. 跨平台支持（`.cmd` 入口 + `install.ps1` + 首次自动初始化 cheatsheet）
11. **本批：建立仓库自包含中枢（换人接手用）**
12. **本批：全量同步 GitHub**——提交 OS 第四卷环境变量分裂设计稿 + 芯片架构内功深潜目录（6 动画 + 2 md），远程 `main` 现为 `e2b421c`，工作区与 GitHub 完全对齐。
13. **本批：入口收敛为 `ibox` + 修 3 处交互硬伤**——新建统一入口 `ibox`（薄壳，复用 `pycheat` / `tkcore` / `tk`，不重写）；开场屏即使用指南；`hi` / `sync` Python 化（Windows 可用）；旧名 `c` / `pycheat` / `tk` / `hi` / `gup` 保留兼容；`cheatsheet.md` 与全部文档同步改名。

## 当前状态

- 最新提交：`<本次提交>`（2026-09-14 入口收敛为 ibox）
- 用户面入口：**`ibox`**（短名 `c`）；旧名 `pycheat` / `tk` / `hi` / `gup` 为兼容壳，全部仍可用。
- 工具箱功能：全可用（mac / win）。`ibox ask` 需本机有 **chat 模型**才可用（`bge-m3` / `nomic-embed-text` 不能对话）。
- 已实测验证：`note` / `todo` / `gitx` / `clip` / `log` 语义召回（含「连接被拒绝」→ 英文 `connection refused` 段 的**跨语言捞针**）；`explain` / `sum` 缺 chat 模型时友好降级。
- 中枢：本仓库现含 `AGENTS.md` / `STATUS.md` / `MEMORY.md`（自包含，已纳入 git）；旧的 iCloud 软链移为 `.icloud.bak` 且不提交。

## 下一动作（接手人可接）

1. 可选：拉 chat 模型 `ollama pull qwen2.5:0.5b`，让 `ibox ask` 立即可用。
2. 可选：`ibox find` 一次只搜一个域（默认 note）。若想「一句话一次搜全部域」，需加跨域聚合排序——**未做**（成本不均：log 要扫盘、git 要读仓库）。
3. 可选：给 `ibox` 加 zsh tab 补全与 ↑ 调历史（当前开场屏用裸 `input()`，没有历史）。
4. 可选：`ibox sync` 沿用 `gup.sh` 的 `git add -A`（无差别暂存），与本仓库「只 add 明确涉及文件」的纪律不同——**风险已识别，行为未改**（改了会影响日常同步习惯）。
5. 用户待决：iCloud 软链 `AGENTS.md` / `CLAUDE.md` 是否纳入公开仓库（**当前决定：不纳入**，已改为自包含）。
6. 已完成（原待办）：`tk` 软链 `~/bin/tk` ✅；`hi` / `gup` Python 跨平台化 ✅（收进 `ibox hi` / `ibox sync`）。

## 阻塞 / 风险

- 无硬阻塞。唯一风险是公开仓库误含 iCloud 私有路径软链——已在本次中枢化时排除（改为自包含文件）。
- ollama 偶发 502 / 服务不健康：`tk` 已在启动期探测并温和提示；**跨语言查询（中文查英文日志）强依赖 ollama 健康**。

## 接手人第一步

1. `git clone` 仓库（或拷贝 `terminal-toolbox/`）。
2. 读 `AGENTS.md` → 本文件 → `MEMORY.md` →（日记在 `.workbuddy/memory/`，属本机私有记忆，clone 后无日记属正常；接手以本文件 + MEMORY 为准）。
3. 装 Python（3.9+，勾 Add to PATH）。
4. （可选）装 ollama + `ollama pull bge-m3` 开语义检索。
5. **macOS**：把 `ibox` 软链到 `~/bin`（`ln -s ~/terminal-toolbox/ibox ~/bin/ibox`）；旧名软链可选保留。**Windows**：PowerShell 跑 `install.ps1` 后重开终端。
6. 试：`ibox`（开场指南）、`ibox how 查端口占用`、`ibox add "记一笔"`、`ibox find --in log "连接被拒绝" -p app.log`、`ibox hi`。
