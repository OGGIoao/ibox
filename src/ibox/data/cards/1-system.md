# 硬件与系统信息

## 查看 CPU 架构（Intel 还是 ARM）
- id: arch
- 别名: 看架构,芯片架构,系统架构,arch
- 作用: 查看内核与硬件架构信息（跨平台通用）

### mac
- 命令: uname
- 用法: uname [选项]
- 示例: `uname -m` → arm64（架构）; `uname -a` → 内核名+主机+版本+架构全信息
- 踩坑: 只报"架构代号"不报具体型号；要型号用 `sysctl`/`system_profiler`

### win
- 用法: `$env:PROCESSOR_ARCHITECTURE`
- 示例: `$env:PROCESSOR_ARCHITECTURE` → AMD64 或 ARM64
- 踩坑: 在 32 位 PowerShell 里会显示 x86，即使系统本身是 64 位

## 查看 CPU 型号
- id: cpu-model
- 别名: 看cpu型号,cpu信息,cpu model
- 作用: 查出这台电脑的 CPU 具体型号

### mac
- 命令: sysctl
- 用法: sysctl [-n] 键名
- 示例: `sysctl -n machdep.cpu.brand_string` → Apple M5 Pro; `sysctl hw.memsize` → 内存字节数
- 踩坑: 仅 macOS/BSD；Linux 读 `/proc`，Windows 用 `wmic cpu get`

### win
- 命令: Get-CimInstance
- 用法: `Get-CimInstance Win32_Processor | Select-Object Name`
- 示例: `Get-CimInstance Win32_Processor | Select-Object Name` → Intel(R) Core(TM) i7-…
- 踩坑: 老教程里的 `wmic cpu get name` 在新版 Windows 11 上已被移除，优先用 Get-CimInstance

## 查看整机硬件配置
- id: hw-overview
- 别名: 硬件信息,系统报告,看配置,硬件详情,机器配置
- 作用: 一次看全型号、系统、内存等整机配置（「关于本机」的命令行版）

### mac
- 命令: system_profiler
- 用法: system_profiler <数据类型>
- 示例: `system_profiler SPHardwareDataType` → 芯片/内存/序列号; `system_profiler SPSoftwareDataType` → 系统版本
- 踩坑: 不加参数会输出极长（所有数据类型）；指定类型才实用

### win
- 命令: Get-ComputerInfo
- 用法: `Get-ComputerInfo`
- 示例: `Get-ComputerInfo | Select-Object CsModel, OsName, CsTotalPhysicalMemory`
- 踩坑: 不加筛选输出很长，首次运行要等几秒；图形版是 `msinfo32`

## 看内存够不够用
- id: memory
- 别名: 看内存,内存占用,内存不够,内存压力,neicun,memory
- 作用: 看内存还剩多少、是不是不够用了
- 常用: 是

### mac
- 命令: vm_stat
- 用法: vm_stat [间隔秒]
- 示例: `vm_stat 2` → 每 2 秒刷新；关注 free/speculative 与 pageout 计数
- 踩坑: 单位是"页(4096字节)"不是 MB，要换算；高 pageout 说明内存吃紧

### win
- 命令: Get-CimInstance
- 用法: `Get-CimInstance Win32_OperatingSystem | Select-Object FreePhysicalMemory, TotalVisibleMemorySize`
- 示例: `Get-CimInstance Win32_OperatingSystem | Select-Object FreePhysicalMemory, TotalVisibleMemorySize`
- 踩坑: 单位是 KB 不是 MB；想直观看曲线用任务管理器「性能 → 内存」

## 看 CPU 功耗与温度
- id: power
- 别名: 功耗,耗电,电源监控,看功耗,性能功耗
- 作用: 看 CPU 的功耗、温度和各核心负载

### mac
- 命令: powermetrics
- 用法: sudo powermetrics [--samplers 项] [-n 次数]
- 示例: `sudo powermetrics` → 滚屏输出（Ctrl+C 退出）; 看 CPU 各性能核/能效核占用
- 踩坑: 要 sudo 密码；输出持续刷新，用 `-n 1` 只看一次

### win
- 用法: Windows 没有原生命令，用 HWiNFO、LibreHardwareMonitor 等工具查看
- 踩坑: 网上的「一行命令查温度」大多依赖主板厂商支持，很多电脑上读不到

## 看磁盘读写速度
- id: disk-io
- 别名: 磁盘io,磁盘读写,disk io
- 作用: 磁盘 IO 吞吐监控

### mac
- 命令: iostat
- 用法: iostat [间隔] [次数]
- 示例: `iostat 2` → 每 2 秒看磁盘读写；看 disk0 的 KB/s 与响应时间
- 踩坑: 首次采样是"开机至今均值"，看第二次起才是实时

### win
- 命令: Get-Counter
- 用法: `Get-Counter '\PhysicalDisk(_Total)\Disk Bytes/sec'`
- 示例: `Get-Counter '\PhysicalDisk(_Total)\Disk Bytes/sec' -SampleInterval 2 -MaxSamples 5`
- 踩坑: 计数器名随系统语言本地化，中文系统上英文名可能报错；图形化看「资源监视器 → 磁盘」

## 查看系统版本
- id: os-version
- 别名: 看系统版本,系统版本,version
- 作用: 查看当前操作系统的名称和版本号

### mac
- 命令: sw_vers
- 用法: sw_vers
- 示例: `sw_vers` → ProductName/Version/Build 三行
- 踩坑: 仅 macOS；Linux 用 `/etc/os-release`，Windows 用 `ver`/`winver`

### win
- 命令: Get-ComputerInfo
- 用法: `Get-ComputerInfo -Property OsName, OsVersion`
- 示例: `Get-ComputerInfo -Property OsName, OsVersion` → Windows 11 Home / 10.0.26200
- 踩坑: `winver` 会弹出窗口，而不是在终端里输出

## 看电脑开机多久了
- id: uptime
- 别名: 开机多久,已运行多久,运行时间,在线时长
- 作用: 看系统运行时长与平均负载（load average）

### mac
- 命令: uptime
- 用法: uptime
- 示例: `uptime` → 运行天数 + 3 个负载数（1/5/15 分钟）；M 系列看核心数换算
- 踩坑: 负载≠CPU%，是"就绪队列长度"；多核下负载=核数才算满载

### win
- 命令: Get-CimInstance
- 用法: `(Get-Date) - (Get-CimInstance Win32_OperatingSystem).LastBootUpTime`
- 示例: `(Get-Date) - (Get-CimInstance Win32_OperatingSystem).LastBootUpTime`
- 踩坑: 开启「快速启动」时，关机再开机不算重启，开机时长会比你以为的长很多
