# M2｜从端口找到进程

- 当前为 `Done`。老李于 2026-11-12 确认产品收束到本机只读排障，并授权实现第一条查询路径。
- M1 已交付意图卡、Windows/macOS 双平台命令展示与检索。
- 此前 M2 计划做通用 Shell 命令解释，随后考虑免安装发行及 Claude Code hook。新路线的第二条排障路径是「进程 → 自启记录」，在 M2 验证后单独定边界。

## 阶段边界

| 项 | 内容 |
| --- | --- |
| Goal | 用户输入一个本地 TCP 端口，得到可核对的监听进程信息。 |
| Non-Goal | 通用命令检索与解释的扩展、Agent 集成、独立资源监控或电脑信息页、远程查询、修改系统状态、macOS 实时查询。 |
| Deliverables | 一个可从 iBox 调用的 Windows 只读入口，返回监听地址、PID、进程名与可读取的可执行文件路径，附结果来源。 |
| Technical Boundary | 用当前用户权限查询本机 TCP 监听与进程。监听记录和进程详情是两次观察，按权限及进程当前状态标注可用字段。 |
| Exit Criteria | 用真实本机监听核对地址和 PID；区分空结果与查询失败；遇到进程已退出或路径无法读取时保留可核对的监听信息；跑完现有回归测试。 |

## 交付

- 从 `ibox port <端口号>` 进入 Windows 本机查询。端口范围为 1–65535。空结果与有记录的结果均返回 0，查询失败返回 1，参数错误返回 2。
- 进程详情读取失败时保留监听地址和 PID，能读取进程名时同时展示。
- 当前没有已知外部阻塞。

## 验证证据

- 2026-11-12 在本机 Windows PowerShell 5.1.26100.9711、普通用户权限下验证 `Get-NetTCPConnection` → `Get-Process`。监听 PID 与测试进程一致，且进程路径可读。关闭监听后，系统返回 `CmdletizationQuery_NotFound`。
- 在 Python 3.13.9 下运行 `python -m unittest discover -s tests`，21 项全部通过。新增回归覆盖真实监听、空结果、非法端口、查询失败和进程详情缺失。 `python -m ibox card check` 的 56 张卡全部通过校验。
- 在临时目录构建并安装 wheel，调用生成的 `ibox.exe` 查同一端口的 IPv4 和 IPv6 监听。两个地址、PID 和路径均正确，临时用户配置目录未创建。
- 用本机 Python 3.13 将当前工作区版本安装到 Windows 当前用户。从仓库外通过 PATH 运行 `ibox --version` 与 `ibox port <测试端口>`，版本与监听 PID 均正确。隔离环境也验证了安装、强制重装和卸载。
- 使用 PowerShell 测试替身返回一个已无法打开的 PID，验证查询脚本保留地址和 PID，并将进程详情留空。
- 查询依据见 [Get-NetTCPConnection](https://learn.microsoft.com/en-us/powershell/module/nettcpip/get-nettcpconnection) 和 [Get-Process](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/get-process)。后者的路径等详情按实际可读性展示。

## 源码理解与 Review

- [M2 源码拆解](../03-learning/milestone-M2-source-guide.md) 已完成。
- Review 通过本阶段四项验收。真实系统测试覆盖本机 Windows PowerShell 5.1 与 Python 3.13，其他 Windows/Python 组合尚未实测。
- 进程详情与监听记录来自两次系统读取。进程可能在两次读取之间退出，下一阶段继续区分现场记录和自启证据。
