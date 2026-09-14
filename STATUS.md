# STATUS.md — Personal Terminal Companion 当前状态

> 唯一当前态。更新进度、下一动作、阻塞时只改本文件。
> 更新日期：2026-09-14

## 当前主线

**M0 — 可信基线**（主体已完成）；其上并行完成了一次**用户面入口收敛**。

2026-09-09 老李确认路线 A：正式产品收敛为 Personal Terminal Companion，核心任务是「用人话找到并安全使用终端命令」。边界见 `docs/00-project/scope.md`，决策见 `docs/01-design/decisions/ADR-001-product-boundary.md`。

2026-09-14 老Z 决策：**用户面入口从 5 个顶层命令（`c` / `pycheat` / `tk` / `hi` / `gup`）收敛为唯一入口 `ibox`**（`how` / `find` / `add` / `done` / `ask` / `hi` / `sync` + 开场使用指南），旧名全部保留为兼容壳。该决策**覆盖 ADR-001 的两条 Non-Goal**（「不重写 `hi` / `gup`」「不新增大型交互功能」），依据见 `docs/01-design/decisions/ADR-002-ibox-single-entry.md`。

## 产品状态

- **用户面入口**：`ibox`（短名 `c`）——唯一入口；旧名 `pycheat` / `tk` / `hi` / `gup` 为兼容壳，全部仍可用。
- `pycheat` + `cheatsheet.md`：正式产品核心（命令卡引擎 + 知识真源）；离线搜索永远可用，Ollama 为可选增强。
- `tk`：Beta；七个现有域保留，**冻结扩域**（ADR-001），等待真实使用验证；其域函数现被 `ibox` 复用。
- `hi` / `gup`：已由 bash 重写为 Python（`ibox hi` / `ibox sync`），**Windows 现在也能用** —— ADR-001 中「POSIX 辅助、非 Windows 承诺」的表述据此更新。
- OS / Shell 课程：解释层。
- 芯片架构与非终端放映：内容实验区；M0 不扩写、不删除、不拆仓。

## M0 已完成

- 产品边界 Scope 与 ADR-001 已落稿。
- 建立 M0 验收规格与 8 条离线 golden queries。
- 新增 `lsof` 卡，修复 `c 查端口占用` 错误命中 `du`。
- 建立 6 项自动测试：卡名唯一、字段完整、golden queries、`pycheat` / `tk` / HTML checker smoke test。
- 建立 HTML 本地链接检查；修复逻辑电路放映的目录路径及未完成页跳转。
- 本地验证：6 tests passed；Python 编译通过；HTML 本地链接检查通过。
- 三平台 GitHub Actions 已通过：macOS / Windows / Linux 均完成编译、测试和链接检查；Windows 额外通过 `.cmd` 入口执行与 `install.ps1` 语法解析（run `34424799213`）。
- 修复 Windows `cp1252` 默认代码页导致中文 CLI 输出崩溃的问题，并加入模拟非 UTF-8 环境的回归测试。
- 中枢已改用仓库内 `daily/`，不再依赖 clone 后不存在的私有 `.workbuddy/memory/`。

## 本批（2026-09-14）：`ibox` 入口收敛 + 3 处交互硬伤

- 新增统一入口 `terminal-toolbox/ibox`：**薄壳，不造新引擎** —— `how` 转调 `pycheat`，`find` / `add` / `done` / `ask` 转调 `tk`（动态加载无后缀脚本，不复制代码），`hi` / `sync` 为 Python 实现；无子命令时打印**完整使用指南**。
- 修 3 处硬伤：
  1. **Windows 浏览失效** —— `read_key()` 只实现 termios 分支，`import tty, termios` 在 Windows 失败即返回 `None` → 只显示第一张卡；已增加 `msvcrt` 分支。
  2. **浏览中按 `/` 重搜范围错** —— `search_rank(order, q2)` 只搜当前结果集，已改为全量 `cards`。
  3. **`todo` 列表不显示 id** 而完成命令要求传 id —— note / todo / clip 列表统一显示短 id（如 `[a3f21c]`）。
- 顺手：`add` / `record` / `done` 不再打 ollama 噪音提示（仅检索类动作提示）。
- 跨平台集成：新增 `ibox.cmd`；`install.ps1` 别名块改为首尾标记包裹（幂等、可原地升级）。
- 文档与数据源同步：`pycheat-使用说明.md` → `ibox-使用说明.md`（重写）；`cheatsheet.md`、`跨平台使用指南.md`、`tk-技术解读.md`、`AGENTS.md`、`README.md`、`个人终端工具箱.md` 同步更新。
- 本地验证：隔离 HOME 下逐子命令实测通过（含 `done <短id>` 端到端）；语法编译通过。

## 下一动作

1. **与老李的 M0 Review 对齐**：ibox 覆盖了 ADR-001 两条 Non-Goal，需确认 ADR-002 与 `scope.md` 同步，否则 M0 Exit Criteria 中「README / STATUS 与实际能力一致」会对不上。
2. 在真实 Windows PowerShell 环境验证 `install.ps1`、`ibox`（含翻页修复）与 `c` —— CI 不替代真人安装验收。
3. 可选：拉 chat 模型 `ollama pull qwen2.5:0.5b`，让 `ibox ask` 立即可用。
4. 可选：`ibox find` 目前一次只搜一个域（默认 note）；跨域聚合排序**未做**（成本不均：log 扫盘、git 读仓库）。
5. 可选：给 `ibox` 加 zsh tab 补全与 ↑ 调历史（当前开场屏用裸 `input()`）。
6. 可选：`ibox sync` 沿用原 `gup.sh` 的 `git add -A`（无差别暂存），与本仓库「只 add 明确涉及文件」的纪律不同 —— **风险已识别，行为未改**。

## 阻塞 / 风险

- 当前无代码硬阻塞。
- **流程风险（新增）**：ibox 收敛与 ADR-001 边界存在显式冲突，已由老Z 决策覆盖；若不落稿 ADR-002 并同步 `scope.md`，后续接手人会在「边界文档」与「代码现状」之间反复困惑。
- Windows PowerShell 安装尚无本轮真实设备验收。
- `pycheat.py` 与 `tkcore.py` 仍各自维护一份近似排序逻辑；已有测试护栏，是否统一留到 M1 评估，不在 M0 提前重构。

## M0 Exit Criteria

- 8 条 golden queries 全部通过：本地已满足。
- 命令卡名称唯一、必需字段完整：本地已满足。
- HTML 本地链接无失效目标：本地已满足。
- macOS / Windows / Linux CI 通过：已满足（run `34424799213`）。
- README / STATUS 与实际能力一致：本轮已校正，**但需在 ADR-002 落稿后重新确认**（用户面入口已改变）。
- Windows PowerShell 真人安装验收：待完成（且需覆盖 `ibox` 与 Windows 翻页修复）。
