# 文件与磁盘

## 列出文件夹里的文件
- id: list-files
- 别名: 列文件,看目录内容,list
- 作用: 列出目录内容

### mac
- 命令: ls
- 用法: ls -la <路径> ; ls -l
- 示例: `ls -la /` 看根目录(含隐藏文件 `.`开头); `ls -la ~` 看家目录隐藏项
- 踩坑: 默认不显示隐藏文件(`.`开头)，必须 `-a`；macOS 的 `@` 表示有扩展属性

### win
- 命令: Get-ChildItem
- 用法: `Get-ChildItem [路径]`
- 示例: `Get-ChildItem -Force`
- 踩坑: PowerShell 里 `ls` 是 Get-ChildItem 的别名，不认 `-la` 这类 mac 参数；看隐藏文件用 `-Force`

## 查看有哪些磁盘 / 分区
- id: volumes
- 别名: 挂载,看挂载点,磁盘挂载,挂载信息
- 作用: 查看已挂载的文件系统及其类型/选项

### mac
- 命令: mount
- 用法: mount ; mount | grep apfs
- 示例: `mount | head` → 看 `/` 是 apfs, sealed, read-only（系统盘密封只读=SIP 体现）
- 踩坑: macOS `/` 是只读密封的；可写数据在 `/System/Volumes/Data`

### win
- 命令: Get-Volume
- 用法: `Get-Volume`
- 示例: `Get-Volume`
- 踩坑: Get-PSDrive 也能列「驱动器」，但会混进注册表等非磁盘项

## 查看文件详细信息（大小、修改时间）
- id: file-info
- 别名: 文件详情,文件属性,文件元信息,看inode
- 作用: 查看文件大小、创建和修改时间、权限等详细信息

### mac
- 命令: stat
- 用法: stat -f "格式串" <文件> (macOS BSD 风格)
- 示例: `stat -f "%N inode=%i size=%z links=%l" ~/.zshrc`
- 踩坑: macOS 用 `-f` + 格式串（BSD），Linux 用 `-c`（GNU），参数不通用

### win
- 命令: Get-Item
- 用法: `Get-Item <文件> | Format-List *`
- 示例: `Get-Item .\report.docx | Select-Object Length, CreationTime, LastWriteTime`
- 踩坑: Length 的单位是字节

## 创建链接（让一个文件出现在两个地方）
- id: link
- 别名: 建软链,软链接,symlink
- 作用: 创建链接——硬链接(默认) 或 软链接(`-s`)，把命令"放"进 PATH

### mac
- 命令: ln
- 用法: ln 源 目标(硬) ; ln -s 源 目标(软) ; ln -sf 源 目标(强制覆盖)
- 示例: `sudo ln -sf ~/.nvm/.../bin/node /usr/local/bin/` 让 GUI 找到 node
- 踩坑: 软链指向被删→断裂(红色)；硬链接共享 inode，删原文件数据还在；跨文件系统只能用软链

### win
- 命令: New-Item
- 用法: `New-Item -ItemType SymbolicLink -Path <链接> -Target <目标>`
- 示例: `New-Item -ItemType SymbolicLink -Path .\notes -Target D:\Dropbox\notes`
- 踩坑: 需要管理员或开启「开发者模式」；桌面上的 .lnk 快捷方式不是真正的链接

## 看磁盘还剩多少空间
- id: disk-free
- 别名: 看磁盘,磁盘空间,磁盘占用,剩多少空间,disk,cipan
- 作用: 查看每个磁盘已用多少、还剩多少
- 常用: 是

### mac
- 命令: df
- 用法: df -h
- 示例: `df -h` → 人类可读(GB)；看 `/System/Volumes/Data` 才是你真正能写的盘
- 踩坑: 要看"剩余可用"而非"已用"；APFS 有"可清除空间"概念

### win
- 命令: Get-PSDrive
- 用法: `Get-PSDrive -PSProvider FileSystem`
- 示例: `Get-PSDrive -PSProvider FileSystem`
- 踩坑: Used / Free 两列单位是 GB；网络盘可能显示为空

## 找出哪个文件夹最占空间
- id: folder-size
- 别名: 文件夹大小,看目录占用,大文件,folder size
- 作用: 统计目录/文件占用大小（排查谁占空间）

### mac
- 命令: du
- 用法: du -sh <路径> ; du -sh ~/.* 2>/dev/null | sort -h
- 示例: `du -sh ~/.*` → 看哪个隐藏目录异常大（安全巡检：藏匿/日志逃避）
- 踩坑: 不带 `-s` 会递归列出每个子项刷屏；`/` 根目录要 sudo 才全看得到

### win
- 命令: Get-ChildItem, Measure-Object
- 用法: `(Get-ChildItem <文件夹> -Recurse -File | Measure-Object Length -Sum).Sum / 1MB`
- 示例: `(Get-ChildItem .\Downloads -Recurse -File -ErrorAction SilentlyContinue | Measure-Object Length -Sum).Sum / 1MB`
- 踩坑: 大文件夹会很慢；没权限的子目录会报红字。想一眼看全盘用 WinDirStat 这类图形工具

## 按名字找文件
- id: find-files
- 别名: 找文件,搜索文件,按名找,find file
- 作用: 按名称/类型/时间递归查找文件
- 常用: 是

### mac
- 命令: find
- 用法: find <起点> -name "模式" ; find . -type f -mtime -1
- 示例: `find ~ -name "*.log" 2>/dev/null` 找所有日志; 安全巡检可疑隐藏脚本
- 踩坑: 默认递归很深，慢；配合 `2>/dev/null` 屏蔽无权限报错

### win
- 命令: Get-ChildItem
- 用法: `Get-ChildItem -Path <起点> -Recurse -Filter <模式>`
- 示例: `Get-ChildItem -Path $HOME -Recurse -Filter *.pdf -ErrorAction SilentlyContinue`
- 踩坑: `-Filter` 比 `-Include` 快得多；从 C:\ 根开始搜会非常慢

## 查看 / 清除下载文件的「来自网络」标记
- id: download-mark
- 别名: 扩展属性,自定义属性,macOS属性,文件扩展属性
- 作用: 查看或清除系统给网上下载的文件打的「来源」标记（打不开下载的程序时常用）

### mac
- 命令: xattr
- 用法: xattr -l <文件> ; xattr -d com.apple.quarantine <文件>
- 示例: `xattr -l ~/Downloads/foo.dmg` 看下载隔离标记（Gatekeeper 依据）
- 踩坑: 从网上下载的文件带 quarantine，首次打开弹"未知开发者"；删标记可绕过（谨慎）

### win
- 命令: Unblock-File, Get-Item
- 用法: 查看：`Get-Item <文件> -Stream Zone.Identifier`；清除：`Unblock-File <文件>`
- 示例: `Unblock-File .\setup.ps1`
- 踩坑: 只对确认可信的文件解除——这个标记正是系统在提醒你「文件来自网络」
