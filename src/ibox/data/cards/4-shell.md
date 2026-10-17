# Shell 与环境

## 查看 PATH（终端去哪些地方找命令）
- id: show-path
- 别名: 看PATH,环境变量,路径变量,PATH在哪
- 作用: 查看终端会去哪些文件夹里找命令（排在前面的优先）

### mac
- 命令: echo
- 用法: echo $PATH | tr ':' '\n'  （分行更易读）
- 示例: 排错"command not found"先看 PATH 含不含命令所在目录
- 踩坑: 改了 ~/.zshrc 的 PATH 必须重开终端或 `source` 才生效

### win
- 用法: `$env:PATH -split ';'`
- 示例: `$env:PATH -split ';'`
- 踩坑: Windows 用分号分隔，mac 用冒号；CMD 里写法是 `echo %PATH%`

## 设置环境变量
- id: env-var
- 别名: 设置环境变量,导出变量,临时变量,加环境变量
- 作用: 把变量"导出"为环境变量（子进程可见）；仅写 `VAR=val` 不会传给子进程

### mac
- 命令: export
- 用法: export VAR=值 ; export PATH="$PATH:/新目录"
- 示例: `export PATH="$HOME/bin:$PATH"` 把自定义目录插到最前（最高优先）
- 踩坑: 直接 `PATH=val` 会清空原有 PATH；追加必须 `="$PATH:..."`

### win
- 用法: 当前窗口：`$env:NAME = "值"`；永久：`[Environment]::SetEnvironmentVariable("NAME", "值", "User")`
- 示例: `$env:OLLAMA_HOST = "0.0.0.0"`
- 踩坑: 永久设置后要重开终端才生效；别用 `setx` 改 PATH，超过 1024 字符会被截断

## 给命令起短名
- id: alias
- 别名: 起别名,命令别名,自定义短名,设别名
- 作用: 给常用命令起一个短名字，少敲几个字

### mac
- 命令: alias
- 用法: alias ll='ls -la' ; alias  (列出全部)
- 示例: `alias gs='git status'` 省敲键盘
- 踩坑: 别名可被恶意覆盖冒充真命令（PATH 劫持同理）；`type 命令` 看它到底是别名/函数/文件

### win
- 命令: Set-Alias
- 用法: `Set-Alias <短名> <命令>`
- 示例: `Set-Alias np notepad`
- 踩坑: 只在当前窗口有效，永久要写进 `$PROFILE`；Set-Alias 不能带参数，带参数要写 function

## 查一个命令到底是什么
- id: what-is-cmd
- 别名: 命令类型,看命令是什么,命令来源,命令在哪
- 作用: 揭示一个"命令名"到底是什么（别名/函数/内建/文件路径）

### mac
- 命令: type
- 用法: type <名称> ; type -a <名称>
- 示例: `type ls` 看是否被 alias; `type claude` 看真实路径 → 排错利器
- 踩坑: 同名时优先级：alias > function > 内建 > PATH 文件；用它识破伪装

### win
- 命令: Get-Command
- 用法: `Get-Command <命令>`
- 示例: `Get-Command ls` → Alias  ls -> Get-ChildItem
- 踩坑: CommandType 一列告诉你它是别名、cmdlet 还是外部程序

## 查命令装在哪
- id: cmd-path
- 别名: 找命令位置,命令路径,程序在哪,查命令路径
- 作用: 显示命令在 PATH 中的绝对路径（自检三连之一）

### mac
- 命令: which
- 用法: which <命令> ; which -a <命令>
- 示例: `which node` → ~/.nvm/.../bin/node；"command not found"先跑它
- 踩坑: 不识别 alias/function（用 `type` 补）；只报 PATH 内能找到的

### win
- 命令: Get-Command, where.exe
- 用法: `(Get-Command <命令>).Source` 或 `where.exe <命令>`
- 示例: `where.exe python`
- 踩坑: PowerShell 里单写 `where` 是 Where-Object 的别名，必须写 `where.exe`

## 让改过的终端配置立刻生效
- id: reload-profile
- 别名: 重载配置,生效配置,加载脚本,应用配置
- 作用: 改完终端配置文件后，不用重开窗口就让它生效

### mac
- 命令: source
- 用法: source ~/.zshrc ; . ~/.zshrc
- 示例: 改完配置后 `source ~/.zshrc` 即可刷新，不必重开
- 踩坑: 如果文件有语法错，source 会报错且可能中断当前环境；先 `zsh -n` 检查

### win
- 用法: `. $PROFILE`
- 示例: `. $PROFILE`
- 踩坑: 开头是「点 + 空格」；若提示「禁止运行脚本」，是执行策略拦截，不是文件写错

## 检查终端配置文件有没有写错
- id: syntax-check
- 别名: 检查语法,zsh语法,配置语法检查,脚本语法
- 作用: 只检查终端配置文件的语法、不执行，改完后先跑一遍防止改坏

### mac
- 命令: zsh
- 用法: zsh -n ~/.zshrc
- 示例: 编辑前后各跑一次，无输出=语法 OK（你曾因引号写错整文件失效）
- 踩坑: 只查语法不查逻辑；配合 `cp ~/.zshrc ~/.zshrc.bak` 双保险

### win
- 用法: `[System.Management.Automation.Language.Parser]::ParseFile($PROFILE, [ref]$null, [ref]$errs) | Out-Null; $errs`
- 示例: `[System.Management.Automation.Language.Parser]::ParseFile($PROFILE, [ref]$null, [ref]$errs) | Out-Null; $errs`
- 踩坑: 没有任何输出就是没有语法错误

## 查看终端配置文件
- id: view-profile
- 别名: 看配置,查看zsh配置,打开配置文件,看shell配置
- 作用: 查看 shell 配置文件内容（自检三连之一，定位配置写坏）

### mac
- 命令: cat
- 用法: cat ~/.zshrc
- 示例: "command not found"时看 nvm/PATH 段是否还在、有无乱码/缺引号
- 踩坑: 大文件用 `less` 翻页；改前先备份

### win
- 命令: Get-Content
- 用法: `Get-Content $PROFILE`
- 示例: `Get-Content $PROFILE`
- 踩坑: 文件可能还不存在：先 `Test-Path $PROFILE`，不存在时用 `notepad $PROFILE` 新建

## 用命令安装软件
- id: install-app
- 别名: 装软件,包管理,安装软件,install
- 作用: 用命令搜索、安装、升级软件（命令行版的「应用商店」）
- 常用: 是

### mac
- 命令: brew
- 用法: brew install <包> ; brew list ; brew --prefix
- 示例: `brew install htop fzf ripgrep` 批量装工具；`brew list` 看已装
- 踩坑: 装的是命令行工具不是 .app；GUI 程序用 `brew install --cask`

### win
- 命令: winget
- 用法: `winget search <关键词>` 查 ID，再 `winget install <ID>`
- 示例: `winget install Git.Git`
- 踩坑: 用 ID 安装更准确，按名字装可能装到同名的其他软件

## 安装 Node 命令行工具（如 claude）
- id: npm-global
- 别名: 全局装包,安装npm包,装CLI工具,全局安装
- 作用: Node 包管理；`npm install -g` 装全局命令（claude/codex 等）

### mac
- 命令: npm
- 用法: npm install -g <包> ; npm ls -g --depth=0 ; npm config get prefix
- 示例: 全局命令装在 nvm 的 node 版本目录里，需 nvm 加载才进 PATH
- 踩坑: install-scripts 策略可能拦截 postinstall（claude 原生二进制曾因此没装上）；切换 node 版本后全局命令需重装

### win
- 命令: npm
- 用法: `npm install -g <包>`
- 示例: `npm install -g @anthropic-ai/claude-code`
- 踩坑: 若提示「禁止运行脚本」，是 npm.ps1 被执行策略拦了，可改用 `npm.cmd install -g <包>`
