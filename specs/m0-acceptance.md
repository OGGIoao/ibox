# M0 — 可信基线验收规格

## Goal

让仓库中“可用”的核心承诺可重复验证，为下一轮体验迭代建立稳定基线。

## Non-Goals

- 不新增 `tk` 域、模型依赖或大型交互功能。
- 不统一重构 `pycheat` 与 `tkcore` 的搜索实现。
- 不拆仓、不改仓库名、不扩写课程。

## Deliverables

- 核心命令卡结构校验与离线 golden queries。
- Python 编译、CLI smoke test、HTML 内链检查。
- macOS / Windows / Linux 的 CI 基线。
- README、STATUS、安装示例与实际行为对齐。
- 产品边界 ADR 与中立日记入口。

## Golden Queries

以下查询必须在 `--no-llm` 模式下把预期卡排在第一位：

| 查询 | 预期卡 |
|---|---|
| 查端口占用 | `lsof` |
| 哪个文件夹最大 | `du` |
| 查看磁盘空间 | `df` |
| 哪个进程吃内存 | `top / htop` |
| 看系统版本 | `sw_vers` |
| 查进程 | `ps` |
| 提交代码 | `git add / commit` |
| 启动 ollama | `ollama serve` |

## Exit Criteria

- 自动测试覆盖全部 golden queries，并在三个桌面系统的 CI 中通过。
- 所有命令卡名称唯一，必需字段完整。
- HTML 本地链接不存在失效目标；尚未制作的页面不提供可点击入口。
- README 与 STATUS 不再承诺未验证能力。
- macOS 本地验证通过；Windows CI 只证明 Python 代码路径，真实 PowerShell 安装仍须真人验收。
