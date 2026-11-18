# M2 源码拆解｜从端口找到进程

运行 `ibox port 3000`，iBox 会读取 Windows 此刻的 TCP 监听记录，并按 PID 补上当前可读取的进程名和程序路径。

## Architecture Map

- [`cli.py`](../../src/ibox/cli.py) 负责参数校验、结果输出和退出码。
- [`env.py`](../../src/ibox/env.py) 负责启动系统自带的 Windows PowerShell、运行固定查询并读取 JSON。
- [`test_cli.py`](../../tests/test_cli.py) 用真实回环监听和替身数据覆盖成功、空结果及失败路径。

## Execution Flow

```text
ibox port <端口号>
  → cli.main / build_parser / _parse_port
  → cli.cmd_port
  → env.query_tcp_listeners
  → Get-NetTCPConnection -State Listen（地址、PID）
  → Get-Process -Id（进程名、可读路径）
  → JSON
  → CLI 输出
```

端口号通过子进程环境传给固定脚本。结果从标准输出回到 Python，本次查询没有持久状态。PowerShell 的特定「未找到」结果转换成空数组。其他监听查询错误交回 CLI 报告。进程查询是补充步骤，失败时保留已经获得的地址和 PID。

## Key Files

| 文件 | 先看什么 |
| --- | --- |
| [`cli.py`](../../src/ibox/cli.py) | `_parse_port` 限制端口范围，`cmd_port` 展示查询结果和字段缺失。 |
| [`env.py`](../../src/ibox/env.py) | `query_tcp_listeners` 建立子进程边界，`_TCP_LISTENERS_SCRIPT` 说明地址和 PID 从哪来。 |
| [`test_cli.py`](../../tests/test_cli.py) | `test_port_reports_real_listener_and_empty_result` 用同一个绑定端口对照调用 `listen()` 前后。 |

## Why

系统 cmdlet 能提供结构化的 TCP 记录，Python 从 JSON 读取字段。这条路径可以复用仓库现有的标准库与系统适配层。代价是每次查询要启动 Windows PowerShell，进程名和路径的可读性取决于当前账号权限和进程状态。

## Alternatives

- 解析 `netstat` 文本同样能取得监听地址和 PID，进程路径仍要再查，文本解析也需要兼顾输出差异。
- 直接绑定 Windows 原生网络 API 能省去启动 PowerShell 的开销，但需要维护结构体布局和错误处理。本阶段的验收只需查询单个端口。

## Recommended Reading Order

1. 花 5 分钟跑一次 `ibox port <端口号>`，对照输出和返回状态。
2. 花 8 分钟读 `cli.py` 的参数校验和 `cmd_port`。
3. 花 12 分钟在 `env.py` 里跟踪监听记录、PID、进程详情和 JSON。
4. 花 5 分钟读真实监听测试，看看测试为何先绑定端口、再进入监听状态。
