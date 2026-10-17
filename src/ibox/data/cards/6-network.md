# 网络与远程

## 查看端口被谁占用
- id: port-owner
- 别名: 查端口占用,端口被谁占用,谁占了端口,监听端口,port,端口进程
- 作用: 查看哪些进程打开了文件或占用了网络端口

### mac
- 命令: lsof
- 用法: lsof -i :<端口> ; lsof -iTCP -sTCP:LISTEN -n -P
- 示例: `lsof -i :3000` → 找出占用 3000 端口的进程；`lsof -iTCP -sTCP:LISTEN -n -P` → 列出 TCP 监听端口
- 踩坑: 查不到时可能需要 `sudo`；结束进程前先确认 PID 和程序身份，不要见端口就强杀

### win
- 命令: Get-NetTCPConnection, Get-Process
- 用法: `Get-NetTCPConnection -LocalPort <端口>`
- 示例: `Get-Process -Id (Get-NetTCPConnection -LocalPort 3000).OwningProcess`
- 踩坑: 端口没人占用时会报错（这不是坏事）；老办法 `netstat -ano | findstr :3000`

## 远程登录另一台电脑
- id: ssh
- 别名: 远程登录,连服务器,登录服务器,ssh连接,远程执行命令
- 作用: 登录远程主机并执行命令（全程加密）；也是所有远程操作的地基

### mac
- 命令: ssh
- 用法: `ssh [选项] 用户@主机` ；只跑一条命令用 `ssh 用户@主机 "命令"`
- 示例: `ssh user@192.168.1.10` → 登录；`ssh lab "df -h"` → 只执行一条命令并返回；`ssh -p 2222 user@host` → 指定端口
- 踩坑: 首次连接要确认主机指纹（输 yes）；连不上按三步查——主机通不通（ping）、22 端口开没开（nc -vz host 22）、认证对不对

### win
- 命令: ssh
- 用法: `ssh [选项] 用户@主机` ；只跑一条命令用 `ssh 用户@主机 "命令"`
- 示例: `ssh user@192.168.1.10` → 登录；`ssh lab "df -h"` → 只执行一条命令并返回；`ssh -p 2222 user@host` → 指定端口
- 踩坑: 首次连接要确认主机指纹（输 yes）；连不上按三步查——主机通不通（ping）、22 端口开没开（nc -vz host 22）、认证对不对

## 生成 SSH 密钥
- id: ssh-keygen
- 别名: 生成密钥,免密登录,密钥对,ssh密钥
- 作用: 生成 SSH 密钥对（公钥 + 私钥），免密登录的起点

### mac
- 命令: ssh-keygen
- 用法: `ssh-keygen -t ed25519 -C "备注"`
- 示例: `ssh-keygen -t ed25519 -C "macbook"` → 生成 ~/.ssh/id_ed25519（私钥）与 id_ed25519.pub（公钥）
- 踩坑: 私钥（无 .pub 后缀那个）永不外传；推荐 ed25519，别再用 rsa 2048；想要空密码直接回车，但私钥文件泄露即等于失守

### win
- 命令: ssh-keygen
- 用法: `ssh-keygen -t ed25519 -C "备注"`
- 示例: `ssh-keygen -t ed25519 -C "macbook"` → 生成 ~/.ssh/id_ed25519（私钥）与 id_ed25519.pub（公钥）
- 踩坑: 私钥（无 .pub 后缀那个）永不外传；推荐 ed25519，别再用 rsa 2048；想要空密码直接回车，但私钥文件泄露即等于失守

## 设置 SSH 免密登录
- id: ssh-copy-id
- 别名: 装公钥,配置免密,免密登录,拷贝公钥
- 作用: 把本地公钥追加到远端 ~/.ssh/authorized_keys，实现免密登录

### mac
- 命令: ssh-copy-id
- 用法: `ssh-copy-id [-i 公钥] [-p 端口] 用户@主机`
- 示例: `ssh-copy-id user@server` → 输最后一次密码，之后 `ssh user@server` 就不问密码了
- 踩坑: macOS 可能没有此命令（`brew install ssh-copy-id`），可手动：`cat ~/.ssh/id_ed25519.pub | ssh user@host "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"`；远端 ~/.ssh 权限必须 700、authorized_keys 必须 600，否则免密静默失效

### win
- 命令: ssh
- 用法: `type $env:USERPROFILE\.ssh\id_ed25519.pub | ssh 用户@主机 "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"`
- 示例: `type $env:USERPROFILE\.ssh\id_ed25519.pub | ssh me@192.168.1.10 "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"`
- 踩坑: Windows 没有 ssh-copy-id；若目标也是 Windows 且是管理员账户，公钥要放 `C:\ProgramData\ssh\administrators_authorized_keys`

## 给常用服务器起短名
- id: ssh-config
- 别名: 主机别名,ssh配置,简化ssh,跳板机配置
- 作用: 给常用主机起短名，省去每次敲 IP/端口/用户名；也是跳板机、隧道、密钥指定的统一落点

### mac
- 命令: ssh
- 用法: 编辑 `~/.ssh/config`，一台主机写一个 `Host` 块
- 示例: 写 `Host lab` / `HostName 100.64.0.5` / `User zhangsan` / `Port 2222` / `IdentityFile ~/.ssh/id_ed25519` → 以后 `ssh lab` 即可
- 踩坑: 配置文件权限必须 600（`chmod 600 ~/.ssh/config`），否则 ssh 直接拒读；`Host` 短名别和真实域名冲突

### win
- 用法: 编辑 `$env:USERPROFILE\.ssh\config`，格式与 mac 完全相同
- 示例: `notepad $env:USERPROFILE\.ssh\config`
- 踩坑: 用记事本保存时注意不要被加上 .txt 后缀

## 交互式上传 / 下载文件（SFTP）
- id: sftp
- 别名: 传文件,上传下载,远程文件,交互传输
- 作用: 基于 SSH 的交互式文件传输，可浏览、上传、下载

### mac
- 命令: sftp
- 用法: `sftp 用户@主机` → 进入 `sftp>` 提示符
- 示例: `sftp user@host` 后：`ls` 看远端、`cd` 切远端目录、`get 远程文件` 下载、`put 本地文件` 上传、`bye` 退出
- 踩坑: 传大量文件或要增量/断点续传时，用 `rsync -avz --progress` 比 sftp 高效得多；`put -r` 递归上传并非所有实现都支持

### win
- 命令: sftp
- 用法: `sftp 用户@主机` → 进入 `sftp>` 提示符
- 示例: `sftp user@host` 后：`ls` 看远端、`cd` 切远端目录、`get 远程文件` 下载、`put 本地文件` 上传、`bye` 退出
- 踩坑: 传大量文件或要增量/断点续传时，用 `rsync -avz --progress` 比 sftp 高效得多；`put -r` 递归上传并非所有实现都支持

## 在两台电脑之间拷文件
- id: scp
- 别名: 拷贝文件,跨机复制,复制到服务器,传输文件,传文件,传到另一台电脑,传到另一台机器,发文件到服务器
- 作用: 一条命令在两台机器之间拷贝文件

### mac
- 命令: scp
- 用法: `scp [选项] 源 目标`（远端写作 `用户@主机:路径`）
- 示例: `scp app.log user@host:/tmp/` → 上传；`scp user@host:/var/log/app.log .` → 下载到当前目录；`scp -r 目录 user@host:/tmp/` → 递归拷贝目录
- 踩坑: 新版 OpenSSH 的 scp 底层已换成 SFTP 协议；**大量文件、断点续传、增量同步别用 scp**，改用 `rsync -avz --progress`；路径含空格要转义

### win
- 命令: scp
- 用法: `scp [选项] 源 目标`（远端写作 `用户@主机:路径`）
- 示例: `scp app.log user@host:/tmp/` → 上传；`scp user@host:/var/log/app.log .` → 下载到当前目录；`scp -r 目录 user@host:/tmp/` → 递归拷贝目录
- 踩坑: 新版 OpenSSH 的 scp 底层已换成 SFTP 协议；**大量文件、断点续传、增量同步别用 scp**，改用 `rsync -avz --progress`；路径含空格要转义

## 记住 SSH 密钥密码，不用每次输
- id: ssh-agent
- 别名: 密钥代理,免重复输密码,记住密钥,钥匙串
- 作用: 在内存中缓存已解密的私钥，避免每次 ssh 都输 passphrase

### mac
- 命令: ssh-agent, ssh-add
- 用法: `eval "$(ssh-agent -s)"` 启动，然后 `ssh-add ~/.ssh/id_ed25519` 加载
- 示例: macOS 更省事：`ssh-add --apple-use-keychain ~/.ssh/id_ed25519` → 存进钥匙串，重启后仍生效
- 踩坑: agent 默认只在当前会话有效；macOS 想持久要在 `~/.ssh/config` 加 `AddKeysToAgent yes` 与 `UseKeychain yes`；`ssh-add -l` 查看已加载密钥，`ssh-add -D` 全部清空

### win
- 命令: Start-Service, ssh-add
- 用法: `Start-Service ssh-agent; ssh-add`
- 示例: `Start-Service ssh-agent; ssh-add $env:USERPROFILE\.ssh\id_ed25519`
- 踩坑: ssh-agent 服务默认是禁用的，需先在管理员 PowerShell 执行 `Get-Service ssh-agent | Set-Service -StartupType Automatic`

## 把几台电脑连成一个内网
- id: tailscale
- 别名: 内网穿透,虚拟内网,异地组网,免公网IP,跨机互控,组网
- 作用: 把多台设备组进一个虚拟内网（每台分到 100.x 地址），互相直连——免公网 IP、免端口映射

### mac
- 命令: tailscale
- 用法: 各设备都装 tailscale 并登同一账号，再用 `tailscale status` 看在线设备与地址
- 示例: `tailscale status` → 列出已组网设备及其 100.x 地址；`tailscale ip -4` → 只看本机虚拟 IP；`ping 100.x.y.z` → 验证直连是否通
- 踩坑: 免费版个人够用；**组网只负责「路通」，不负责「开门」**——连上后仍要目标机自己开了 SSH/RDP 服务才行；企业网络可能拦 UDP，会退回 DERP 中继（变慢）

### win
- 命令: tailscale
- 用法: 各设备都装 tailscale 并登同一账号，再用 `tailscale status` 看在线设备与地址
- 示例: `tailscale status` → 列出已组网设备及其 100.x 地址；`tailscale ip -4` → 只看本机虚拟 IP；`ping 100.x.y.z` → 验证直连是否通
- 踩坑: 免费版个人够用；**组网只负责「路通」，不负责「开门」**——连上后仍要目标机自己开了 SSH/RDP 服务才行；企业网络可能拦 UDP，会退回 DERP 中继（变慢）

## 让别的电脑能 SSH 连进来
- id: ssh-server
- 别名: 开启SSH,远程登录,被连mac,mac当服务器,开sshd,openssh server,windows被远程,装sshd
- 作用: 让别的电脑能 SSH 连进这台电脑（mac 自带服务端，打开即可；Windows 需先加装）

### mac
- 命令: systemsetup
- 用法: 系统设置 → 通用 → 共享 → 打开「远程登录」；命令行等价 `sudo systemsetup -setremotelogin on`
- 示例: `sudo systemsetup -setremotelogin on` → 开启；`sudo systemsetup -getremotelogin` → 查状态；对方 `ssh 你的用户名@这台机器的地址`
- 踩坑: 新版 macOS 上 `systemsetup` 可能要求在「系统设置 → 隐私与安全性 → 完全磁盘访问」里给终端授权，否则报错；**只在可信网络开启**（或配合 tailscale 限定来源）；关闭用 `-setremotelogin off`

### win
- 命令: Add-WindowsCapability, Start-Service
- 用法: 设置 → 应用 → 可选功能 → 添加功能 → 勾选「OpenSSH 服务器」；再用管理员 PowerShell 启动服务并设为自启
- 示例: 管理员 PowerShell：`Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0` 安装；`Start-Service sshd` 启动；`Set-Service -Name sshd -StartupType Automatic` 设为自启；`Get-Service sshd` 查状态
- 踩坑: **这是 macOS↔Windows 互控最容易卡住的一步**（Windows 天生没有 sshd，而 macOS 自带）；默认登录 shell 是 cmd，想用 PowerShell 得改注册表 `DefaultShell`；防火墙需放行 22 端口
