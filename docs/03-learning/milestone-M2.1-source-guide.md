# M2.1 源码拆解｜端口查询的新手首页

## Architecture Map

[`cli.py`](../../src/ibox/cli.py) 根据参数和终端环境选择入口，并处理输入、查询和返回。[`ui.py`](../../src/ibox/ui.py) 显示结果和依据。[`env.py`](../../src/ibox/env.py) 复用 M2 的 Windows 查询，见 [M2 源码拆解](milestone-M2-source-guide.md)。

## Execution Flow

```text
Windows 终端运行 ibox
  → _diagnostics_home 调用 show_home 展示四层地图，接受问题或编号
  → _port_from_question 从明确的端口问题中识别一个数字
  → _guided_port 查询这个端口，必要时先引导补填端口号
  → query_tcp_listeners 返回系统查询结果
  → show_port_result 先显示程序，再显示关联
  → 选择「看怎么查到的」后调用 show_port_evidence
```

空结果和查询失败会给出各自的提示，随后可以重查同一个端口、换一个端口或返回。首页用本地规则识别常见表达，问题含有多个候选端口时会请用户只填一个。直接运行 `ibox port 3000` 走原来的输出入口。

## Key Files

- `cli.py` 中的 `main`、`_diagnostics_home` 和 `_guided_port`。
- `ui.py` 中的 `show_home`、`show_port_result` 和 `show_port_evidence`。
- [`test_cli.py`](../../tests/test_cli.py) 中的首页引导与重定向测试。

## Why

在用户需要输入或读结果时解释术语。首条结果的连线依次显示，程序名在动效开始前已给出。`IBOX_NO_MOTION=1` 可以关闭动效，仍能读完整关系。两段动画的等待时间合计约 240 毫秒。

## Alternatives

全屏界面可以做方向键选择和逐字段展开，需要更多终端状态管理。当前使用输入编号加回车，实现成本较小，适合先验证新手能否独立完成查询。

## Recommended Reading Order

1. 用 5 分钟运行 `ibox`，从首页查一次并打开依据。
2. 用 10 分钟读 `cli.py` 的首页与查询循环。
3. 用 8 分钟读 `ui.py` 的结果与依据函数。
4. 用 7 分钟对照测试与 [M2 查询链路](milestone-M2-source-guide.md)。
