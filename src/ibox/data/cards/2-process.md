# 进程与资源

## 看哪个程序最占 CPU / 内存
- id: top-procs
- 别名: 看进程,哪个程序最占cpu,最占内存的进程,进程监控,实时进程,process
- 作用: 找出最占 CPU 或内存的程序
- 常用: 是

### mac
- 命令: top, htop
- 用法: top -o cpu ; htop
- 示例: `top -o cpu` 按 CPU 排序; htop 里 F9 发信号、F4 过滤、F5 树状
- 踩坑: top 默认交互；htop 不在系统自带，要 `brew install htop`；F9 杀进程前确认 PID

### win
- 命令: Get-Process
- 用法: `Get-Process | Sort-Object CPU -Descending | Select-Object -First 10`
- 示例: `Get-Process | Sort-Object WorkingSet -Descending | Select-Object -First 10 Name, Id, WorkingSet`
- 踩坑: 只是一次快照、不会实时刷新；CPU 列是累计秒数不是百分比。实时看用任务管理器（Ctrl+Shift+Esc）

## 列出正在运行的程序
- id: list-procs
- 别名: 查进程,进程列表,看pid,进程快照,pid
- 作用: 列出进程快照（非实时），看 PID/父PID/命令

### mac
- 命令: ps
- 用法: ps aux ; ps -o pid,ppid,comm -p <PID>
- 示例: `ps aux | head` 看全部; `ps -p 1 -o comm=` → launchd（确认 PID 1 是谁）
- 踩坑: macOS 的 `ps aux` BSD 风格，与 Linux 略有差异；`ps -ef` 也通用

### win
- 命令: Get-Process
- 用法: `Get-Process [名字]`
- 示例: `Get-Process chrome`
- 踩坑: 名字不带 .exe；找不到时会报红字，加 `-ErrorAction SilentlyContinue` 可静默

## 结束卡死的程序
- id: kill-proc
- 别名: 杀进程,关掉程序,kill process
- 作用: 结束一个卡住或不想要的程序（按进程号或名字）

### mac
- 命令: kill
- 用法: kill <PID> ; kill -9 <PID> ; kill -TERM <PID>
- 示例: `kill 1234` 优雅退出; `kill -9 1234` 强杀（SIGKILL，进程来不及清理）
- 踩坑: `-9` 是最后手段，会跳过清理导致数据丢失/僵尸；先试默认再 `-9`

### win
- 命令: Stop-Process
- 用法: `Stop-Process -Id <PID>` 或 `Stop-Process -Name <名字>`
- 示例: `Stop-Process -Name notepad`
- 踩坑: Stop-Process 直接强制结束，没有「先温和请求退出」这一步，未保存的内容会丢；结束别的用户的进程需要管理员

## 管理后台服务（开机自启）
- id: services
- 别名: 管后台服务,开机启动,服务管理
- 作用: 查看、启动、停止在后台运行的系统服务

### mac
- 命令: launchctl
- 用法: launchctl list ; launchctl load/unload <plist> ; launchctl setenv KEY val
- 示例: `launchctl list | grep -i agent` 看用户级服务; `launchctl getenv PATH` 看 GUI 的 PATH
- 踩坑: 改了 launchd 的环境变量要注销重登才生效；这是 GUI 应用 PATH 的来源（不读 .zshrc）

### win
- 命令: Get-Service, Start-Service, Stop-Service
- 用法: `Get-Service` / `Start-Service <名>` / `Stop-Service <名>`
- 示例: `Get-Service | Where-Object Status -eq Running`
- 踩坑: 启停服务需要「以管理员身份运行」PowerShell；服务名（Name）和显示名（DisplayName）不一样
