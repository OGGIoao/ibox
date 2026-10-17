# 版本控制

## 看我改了哪些文件（git）
- id: git-status
- 别名: 看改动,当前状态,改了啥,git状态
- 作用: 看仓库当前状态——哪些文件改了、哪些是新增未跟踪（动手前先跑它，知道"我改了啥"）
- 常用: 是

### mac
- 命令: git
- 用法: git status ; git status -s
- 示例: `git status` → 列出已修改(M)/未跟踪(??); `git status -s` → 紧凑两列，左边暂存态右边工作区
- 踩坑: 改完先 `status` 再提交，避免漏改；`status -s` 更省眼；中文文件名显示成 `\345\...` 时加 `git config --global core.quotepath false`

### win
- 命令: git
- 用法: git status ; git status -s
- 示例: `git status` → 列出已修改(M)/未跟踪(??); `git status -s` → 紧凑两列，左边暂存态右边工作区
- 踩坑: 改完先 `status` 再提交，避免漏改；`status -s` 更省眼；中文文件名显示成 `\345\...` 时加 `git config --global core.quotepath false`

## 看提交历史
- id: git-log
- 别名: 看提交历史,提交记录,历史日志,查看log
- 作用: 看提交历史（快照时间线），确认"发生过什么、谁改的"

### mac
- 命令: git
- 用法: git log ; git log --oneline ; git log -p <文件>
- 示例: `git log --oneline -10` → 最近 10 条一行版; `git log -p README.md` → 某文件逐次改动; `git log --stat` → 每次改了哪些文件
- 踩坑: 默认满屏，用 `--oneline` 先看梗概；翻页用 空格，退出按 q；`git log --graph --oneline` 看分支拓扑

### win
- 命令: git
- 用法: git log ; git log --oneline ; git log -p <文件>
- 示例: `git log --oneline -10` → 最近 10 条一行版; `git log -p README.md` → 某文件逐次改动; `git log --stat` → 每次改了哪些文件
- 踩坑: 默认满屏，用 `--oneline` 先看梗概；翻页用 空格，退出按 q；`git log --graph --oneline` 看分支拓扑

## 保存一次改动（提交）
- id: git-commit
- 别名: 提交,保存改动,commit代码,交代码
- 作用: 把改动「暂存」再「提交」成一次历史记录（commit 才是真保存，只改不提交等于没存）

### mac
- 命令: git
- 用法: git add <文件> ; git commit -m "说明"
- 示例: `git add .` 暂存全部改动; `git commit -m "fix: 修复导出空指针"` 提交; `git commit -am "x"` 已跟踪文件一步提交
- 踩坑: `add .` 会连敏感文件/大文件一起提交，先 `status` 确认范围；commit 忘了 `-m` 会进编辑器卡住；改了但没 add 的内容不会进提交

### win
- 命令: git
- 用法: git add <文件> ; git commit -m "说明"
- 示例: `git add .` 暂存全部改动; `git commit -m "fix: 修复导出空指针"` 提交; `git commit -am "x"` 已跟踪文件一步提交
- 踩坑: `add .` 会连敏感文件/大文件一起提交，先 `status` 确认范围；commit 忘了 `-m` 会进编辑器卡住；改了但没 add 的内容不会进提交

## 新建 / 切换分支
- id: git-branch
- 别名: 建分支,切换分支,branch
- 作用: 看/建/切换分支（并行改东西互相不干扰，主线与实验分开）

### mac
- 命令: git
- 用法: git branch ; git switch -c <新分支> ; git switch <分支>
- 示例: `git branch` 列出分支(* 当前); `git switch -c feat-x` 新建并切换; `git switch main` 回主线
- 踩坑: 切换前先 commit 或 stash，否则未提交改动会被带过去; 删分支 `git branch -d` 需已合并; 远程分支用 `git switch -c 本地名 origin/远程名`

### win
- 命令: git
- 用法: git branch ; git switch -c <新分支> ; git switch <分支>
- 示例: `git branch` 列出分支(* 当前); `git switch -c feat-x` 新建并切换; `git switch main` 回主线
- 踩坑: 切换前先 commit 或 stash，否则未提交改动会被带过去; 删分支 `git branch -d` 需已合并; 远程分支用 `git switch -c 本地名 origin/远程名`

## 和远程仓库同步（拉取 / 推送）
- id: git-sync
- 别名: 同步,推送到远程,拉取代码,push,pull
- 作用: 与远程仓库同步——拉更新（pull）或推提交（push）

### mac
- 命令: git
- 用法: git fetch ; git pull ; git push
- 示例: `git push` 推当前分支; `  git pull` 拉并合并; `git fetch` 只看远程有啥不自动合；`git push -u origin 分支` 首次推新分支建立跟踪
- 踩坑: push 前先 pull 防冲突; pull 冲突要手动解决再 commit; 冲突时别慌，git 会标 `<<<<<<<` 让你手动取舍

### win
- 命令: git
- 用法: git fetch ; git pull ; git push
- 示例: `git push` 推当前分支; `  git pull` 拉并合并; `git fetch` 只看远程有啥不自动合；`git push -u origin 分支` 首次推新分支建立跟踪
- 踩坑: push 前先 pull 防冲突; pull 冲突要手动解决再 commit; 冲突时别慌，git 会标 `<<<<<<<` 让你手动取舍

## 临时收起没提交的改动
- id: git-stash
- 别名: 暂存改动,暂存,stash
- 作用: 把当前未提交改动「暂存」到一边，腾空工作区（紧急切分支/拉代码时救场）

### mac
- 命令: git
- 用法: git stash ; git stash pop ; git stash list
- 示例: `git stash` 收起改动; `git stash pop` 恢复; `git stash list` 看所有暂存; `git stash -u` 连未跟踪文件一起收
- 踩坑: 默认不收未跟踪文件（要 `-u`）；pop 冲突需手动解决；长期暂存用 `git stash save "备注"` 方便辨认

### win
- 命令: git
- 用法: git stash ; git stash pop ; git stash list
- 示例: `git stash` 收起改动; `git stash pop` 恢复; `git stash list` 看所有暂存; `git stash -u` 连未跟踪文件一起收
- 踩坑: 默认不收未跟踪文件（要 `-u`）；pop 冲突需手动解决；长期暂存用 `git stash save "备注"` 方便辨认

## 看具体改了什么
- id: git-diff
- 别名: 看差异,对比改动,diff
- 作用: 看具体改了什么（diff = 差异，比读日志直观得多）

### mac
- 命令: git
- 用法: git diff ; git diff --staged ; git diff <版本1> <版本2>
- 示例: `git diff` 看未暂存改动; `git diff --cached` 看已暂存待提交; `git diff HEAD~1` 与上一版对比
- 踩坑: diff 默认不显示已 `add` 的，要看已暂存用 `--staged`；大文件刷屏用 `--stat` 只看增删行数

### win
- 命令: git
- 用法: git diff ; git diff --staged ; git diff <版本1> <版本2>
- 示例: `git diff` 看未暂存改动; `git diff --cached` 看已暂存待提交; `git diff HEAD~1` 与上一版对比
- 踩坑: diff 默认不显示已 `add` 的，要看已暂存用 `--staged`；大文件刷屏用 `--stat` 只看增删行数

## 把仓库下载到本地
- id: git-clone
- 别名: 远程仓库,克隆仓库,拉仓库,clone
- 作用: 远程仓库地址管理 / 首次把整库拉到本地

### mac
- 命令: git
- 用法: git remote -v ; git clone <url>
- 示例: `git remote -v` 看当前远程地址; `git clone https://github.com/x/y.git` 克隆; `git remote set-url origin <新url>` 改地址
- 踩坑: clone 默认建子目录；改远程用 `set-url` 别改 `.git/config` 手滑; SSH 需配密钥，HTTPS 每次输账号（可用 credential 缓存）

### win
- 命令: git
- 用法: git remote -v ; git clone <url>
- 示例: `git remote -v` 看当前远程地址; `git clone https://github.com/x/y.git` 克隆; `git remote set-url origin <新url>` 改地址
- 踩坑: clone 默认建子目录；改远程用 `set-url` 别改 `.git/config` 手滑; SSH 需配密钥，HTTPS 每次输账号（可用 credential 缓存）
