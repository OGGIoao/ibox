# STATUS.md — Personal Terminal Companion 当前状态

> 唯一当前态。更新进度、下一动作、阻塞时只改本文件。
> 更新日期：2026-09-09

## 当前主线

**M0 — 可信基线**。

2026-09-09 老李确认路线 A：正式产品收敛为 Personal Terminal Companion，核心任务是“用人话找到并安全使用终端命令”。边界见 `docs/00-project/scope.md`，决策见 `docs/01-design/decisions/ADR-001-product-boundary.md`。

## 产品状态

- `pycheat` + `cheatsheet.md`：核心产品；离线搜索可用，Ollama 为可选增强。
- `tk`：Beta；七个现有域暂时保留，冻结扩域，等待真实使用验证。
- `hi` / `gup`：POSIX 辅助工具，不属于 Windows 核心承诺。
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

## 下一动作

1. 在真实 Windows PowerShell 环境验证 `install.ps1`、`c` 与 `tk` 入口；CI 不替代真人安装验收。
2. 验收通过后生成 `docs/03-learning/milestone-0-source-guide.md`，带老李完成 M0 Review。
3. Review 后再决定 M1 的单一体验问题；候选优先从真实使用摩擦中产生。

## 阻塞 / 风险

- 当前无代码硬阻塞。
- Windows PowerShell 安装尚无本轮真实设备验收。
- `pycheat.py` 与 `tkcore.py` 仍各自维护一份近似排序逻辑；已有测试护栏，是否统一留到 M1 评估，不在 M0 提前重构。

## M0 Exit Criteria

- 8 条 golden queries 全部通过：本地已满足。
- 命令卡名称唯一、必需字段完整：本地已满足。
- HTML 本地链接无失效目标：本地已满足。
- macOS / Windows / Linux CI 通过：已满足（run `34424799213`）。
- README / STATUS 与实际能力一致：本轮已校正，待 Review。
- Windows PowerShell 真人安装验收：待完成。
