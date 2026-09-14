# ibox 使用详细说明

> 结构性更新：**2026-09-14** —— 统一入口从 `pycheat` / `tk` / `hi` / `gup` 收敛为 **`ibox`**（旧名全部保留可用）。
> 本说明讲「怎么用」；设计动机与路线图见 `个人终端工具箱.md`；Windows 安装见 `跨平台使用指南.md`。

## 0. 一句话定位

`ibox`（短名 `c`）是个人终端工具箱的**唯一入口**，说人话就能用、不必记命令名。它把原先分散的几件事收进一个名字：

- 查命令怎么用（原 `c` / `pycheat`）
- 在自己的笔记 / 日志 / git 提交 / 剪贴板 / 待办里搜（原 `tk` 的五个检索域）
- 让本地模型解释命令、摘要长文本（原 `tk explain` / `tk sum`）
- 看机器信息（原 `hi`）、一键 git 同步（原 `gup`）

**只需记三条**：`ibox how`（查命令）· `ibox find`（搜自己的）· `ibox add`（记一笔）。其余随时敲 `ibox` 看开场指南。

---

## 1. 全部子命令（一张表看全）

| 命令 | 作用 | 原对应 |
|---|---|---|
| `ibox` | 开场屏 = 完整使用指南 | — |
| `ibox how <说法>` | 查命令怎么用（人话搜索） | `c` / `pycheat` |
| `ibox how -c <说法>` | 复制最佳匹配的示例到剪贴板 | `pycheat -c` |
| `ibox how -l` | 列出全部命令卡（编号 + 用途） | `pycheat -l` |
| `ibox find <说法>` | 搜自己的数据（默认 note 域） | `tk note` |
| `ibox find --in todo` | 看未完成任务 | `tk todo` |
| `ibox find --in clip` | 搜剪贴板历史 | `tk clip` |
| `ibox find --in git "关键词"` | 搜 git 提交 | `tk gitx` |
| `ibox find --in log "报错" -p app.log` | 搜日志（`-p` 可给文件或目录） | `tk log` |
| `ibox add "文本"` | 记一条快记 | `tk note -a` |
| `ibox add "文本" --in todo` | 加一个任务 | `tk todo -a` |
| `ibox add --clip` | 把当前剪贴板记一条 | `tk clip -r` |
| `ibox done <id>` | 任务标记完成（id 见 `find` 输出里的 `[xxxxxx]`） | `tk todo -d` |
| `ibox ask <命令>` | 让本地模型解释命令 | `tk explain` |
| `ibox ask --sum -f 文件` | 摘要长文本（也可 `cat 文件 \| ibox ask --sum`） | `tk sum` |
| `ibox hi` / `ibox hi -v` | 我在哪台机器（`-v` 带芯片 / 内存） | `hi` |
| `ibox sync` | 一键 git 同步（当前仓库） | `gup` |

`--in` 可选值：`note`（默认）· `todo` · `clip` · `git` · `log`。省略 `--in` 就是搜快记。

---

## 2. 旧名还能用吗？能。

旧名都是薄壳，内部转调 `ibox`，行为一致——你的肌肉记忆不用改：

| 旧习惯 | 现在等价于 | 说明 |
|---|---|---|
| `c 端口占用` | `ibox how 端口占用`（或直接 `ibox 端口占用`） | `c` 就是 `ibox` 的别名 |
| `pycheat -c top` | `ibox how -c top` | 全部 flag 原样可用 |
| `tk note 记一笔` | `ibox add "记一笔"` | — |
| `tk todo` | `ibox find --in todo` | — |
| `hi` | `ibox hi` | — |
| `gup` | `ibox sync` | — |

> 之所以不删旧名：入口重命名的成本必须为 0，否则改名的收益会被「改习惯」的代价吃掉。

---

## 3. 安装与配置（本机现状）

整个工具**零额外 Python 依赖**（只用标准库 + 系统剪贴板命令）。链路如下：

| 环节 | 位置 | 作用 |
|---|---|---|
| 统一入口 | `~/terminal-toolbox/ibox` | 子命令分发 + 开场指南 + `hi`/`sync` |
| 命令卡引擎 | `~/terminal-toolbox/pycheat.py` | 检索、卡面渲染、交互浏览（被 ibox 复用） |
| 数据域层 | `~/terminal-toolbox/tk` + `tkcore.py` | 笔记/日志/提交/剪贴板/待办 的采集与语义引擎 |
| 全局命令 | `~/bin/ibox`（软链） | 任意目录敲 `ibox` 都行 |
| 短名别名 | `~/.cheat.zsh`（由 `~/.zshrc` source） | `alias c='ibox'` |
| 数据源 | `~/.config/cheat/cheatsheet.md` | 49 张命令卡（含 8 张 ollama），所见即所得 |
| 个人数据 | `~/.config/cheat/.tk_*.jsonl` | note / todo / clip 的记录 |
| 学习与缓存 | `~/.config/cheat/.pycheat_*.json` | 自学习说法库、复习曲线、卡片向量缓存 |

**重装 / 换机器：**
```bash
# macOS
ln -s ~/terminal-toolbox/ibox ~/bin/ibox
chmod +x ~/terminal-toolbox/ibox
echo 'source ~/.cheat.zsh' >> ~/.zshrc     # 已加则忽略
```
```powershell
# Windows（在工具箱目录）
.\install.ps1     # 加 PATH + 写别名 ibox / c / pycheat / tk，重开终端生效
```

---

## 4. 日常怎么用（4 个最常用动作）

### 动作 A：不知道敲什么 → 看开场指南
```bash
ibox        # 或 c
```
直接列出**全部子命令 + 最常见用法**。记不住命令时敲它就对了（它就是为「一下子记不住」准备的）。

### 动作 B：查某条命令怎么用
```bash
ibox how 哪个进程吃内存
ibox how 强制结束没响应的程序
ibox how git 提交改动
ibox 看系统是什么版本        # 省略 how 也行，等价
```
- 支持**中文描述**、**拼音**（`neicun`）、**命令名**（`top`）、**英文**混合
- 返回按「本地匹配分 + 语义温和加成（融合排序）」排序的彩色卡面
- 清晰命中永远压过语义噪声（实测：`强制结束没响应` → `kill` 顶到 #1）

### 动作 C：把示例复制走
```bash
ibox how -c 看内存      # 最佳匹配的「示例」直接进剪贴板，⌘V / Ctrl+V 就能跑
```

### 动作 D：搜自己的东西
```bash
ibox add "改 ssh 端口要先备份"      # 先记
ibox find 备份                      # 再搜（默认搜快记）
ibox find --in todo                 # 看还有哪些任务没做
```
搜到任务后，行首的 `[a3f21c]` 就是它的 id：
```bash
ibox done a3f21c                    # 标记完成
```

---

## 5. 卡面长什么样（分区彩色）

| 段 | 颜色 | 内容 |
|---|---|---|
| **作用** | 青 | 这条命令解决什么问题（人话） |
| **用法** | 绿 | 命令语法 `[选项]` |
| **示例** | 黄 | 可直接抄的实战命令（反引号内会加粗） |
| **通俗别名** | 品红 | 人话 / 拼音 / 英文说法，命中靠它 |
| **踩坑** | 红 | 新手最容易栽的地方 |
| **平台对照** | 蓝 | 同功能的 Windows 命令 |
| **来源** | 灰 | 出自 OS 课的哪一卷 |

浏览键位：`n`/`→` 下一张 · `p`/`←` 上一张 · `b` 回退 · `f` 前进 · `c` 复制示例 · `/` 重新搜索 · `q` 退出。

> 「`/` 重新搜索」搜的是**全量 49 张卡**，不是当前结果集——翻了几张再搜也不会被范围困住。

---

## 6. 语义检索（ollama，可选增强）

装了本地 ollama 后，`ibox` 会自动叠加向量语义匹配——**同义 / 近义也能命中**（如「哪个进程吃 RAM」↔ `top / htop`）。

**机制：**
- 零额外依赖，仅 `urllib` 调本机 `http://localhost:11434/api/embeddings`
- 排序 = **融合排序**：本地匹配分占主导，语义相似度只做温和加成，**绝不覆盖清晰本地命中**
- 嵌入模型默认 `nomic-embed-text`；本机若已拉 `bge-m3`（中文更强）会**自动优先**
- 卡片向量按「内容 hash + 模型名」缓存，换模型自动失效重建

**三个开关：**
```bash
ibox how 哪个进程吃 RAM      # 自动：ollama 在跑就增强，否则纯离线
ibox how --llm 看系统版本    # 强制语义检索（ollama 不可用则报错退出）
ibox how --no-llm git提交    # 强制离线（即便 ollama 在跑）
```

**把中文区分度拉满（可选）：**
```bash
ollama pull bge-m3      # 约 1.2GB，拉到即生效，代码已自动优先，无需改配置
ollama list             # 确认 bge-m3:latest 在位
```

---

## 7. 自学习别名 + 间隔复习（越用越懂你）

**自学习**：每次用「人话」搜并命中某卡，这条「说法 → 命令」会被固化，下次同类说法直接命中。
```bash
ibox how --learn            # 查看已学说法 + 命中次数
ibox how --learn clear      # 清空学习库
ibox how --forget 看内存    # 忘掉某条说法
```
> 只在「说法不是现成命令名 / 别名」时才学，避免污染。

**间隔复习**：每张卡记录查看次数与上次时间，`ibox how`（无参数进开场屏）会自动挑「快忘了的」提醒你巩固（看过 <3 次或 >7 天没看）。

---

## 8. 命令敲错主动提示

在交互 zsh 里敲了不存在的命令，`command_not_found_handler` 会调 `ibox how --suggest` 给相关卡提示：
```
💡 没找到命令 'gti'，但 ibox 里有相关的：git
   输入 c <名字> 看详情（直接 c 回车看使用指南）
```
（仅交互式 zsh 生效；太短或像路径的尝试不触发，避免误打扰。）

---

## 9. 自己加命令卡（最该掌握的进阶）

数据源是纯 markdown，**加一张卡 = 文末加一个 `## 命令名` 区块**，存盘即生效，无需改代码。

```markdown
## 你的新命令
- 别名: 人话说法1,人话说法2,拼音
- 作用: 一句话说明解决什么
- 用法: 命令 [选项] 参数
- 示例: `实际命令` → 输出说明
- 踩坑: 最容易错的点 / 平台差异
- Windows对照: 等效的 Windows 命令（没有写 无）
- 来源卷: 你从哪学来的
```

**三步加上：**
1. `open ~/.config/cheat/cheatsheet.md`
2. 滚到文件末尾，粘贴上面整段
3. ⌘S 存盘 → 敲 `ibox how 你的说法` 就能搜到

要点：
- **别名行是命中关键**——多写人话 / 拼音
- 示例用反引号包裹命令，卡面会高亮
- 想删卡：把整段 `## 名字 …` 删掉存盘即可

---

## 10. 常见问题排查

| 现象 | 原因 / 解决 |
|---|---|
| `ibox` 命令找不到 | `~/bin` 不在 PATH，或软链断了 → 重跑 §3 |
| `c` 没反应 | `~/.cheat.zsh` 未被 source → 确认 `~/.zshrc` 里有 `source ~/.cheat.zsh` |
| `add` 时提示 ollama 未运行 | 正常（记笔记不需要语义检索）；只有 `find` 类检索才会提示 |
| 语义检索没生效 | ollama 没起 → `ollama serve`；模型没拉 → `ollama pull nomic-embed-text` |
| 强制 `--llm` 报错退出 | 模型名对不上 / ollama 未起 → `ollama list` 核对，或改用 `--no-llm` |
| `ibox ask` 说没有 chat 模型 | 嵌入模型不能对话 → `ollama pull qwen2.5:0.5b` |
| `ibox sync` 报不是 git 仓库 | 先 `cd` 到仓库根目录再跑 |
| 卡面中文乱码 | 终端字体缺字，与工具无关 |
| Windows 上翻页没反应 | 已修（2026-09-14）：Windows 走 `msvcrt` 读键，升级后即可翻页 |

---

## 11. 命令速查表

| 想做的事 | 敲什么 |
|---|---|
| 看使用指南 | `ibox` 或 `c` |
| 人话查命令 | `ibox how 你想干的事`（或 `c 你想干的事`） |
| 复制示例 | `ibox how -c 关键词` |
| 列全部卡 | `ibox how -l` |
| 记一条快记 | `ibox add "内容"` |
| 加个任务 | `ibox add "内容" --in todo` |
| 搜自己的数据 | `ibox find 关键词` |
| 看未完成任务 | `ibox find --in todo` |
| 完成任务 | `ibox done <id>` |
| 强制语义检索 | `ibox how --llm 关键词` |
| 强制离线 | `ibox how --no-llm 关键词` |
| 看自学习库 | `ibox how --learn` |
| 问本地模型 | `ibox ask tar -xzf` |
| 摘要长文本 | `ibox ask --sum -f 文件` |
| 我在哪台机器 | `ibox hi`（`-v` 看芯片） |
| 一键 git 同步 | `ibox sync` |
| 加新卡 | 编辑 `~/.config/cheat/cheatsheet.md` 文末加区块 |

---

*本说明与 `个人终端工具箱.md`（设计 / 路线图）互补：那份讲「为什么这么造」，这份讲「怎么用」。*

---

## 附录 A：ollama 速查小抄（8 张卡一页看全）

> 一句话：**serve 起服务 → pull 拉模型 → run/list/ps 用模型 → rm 清理 → embeddings 给程序调 → show 看元信息**。
> `ibox` 的语义检索只依赖 `embeddings` 接口 + 一个嵌入模型（`nomic-embed-text` 默认，`bge-m3` 自动优先）。

| 命令 | 一句话定位 | 最常用示例 | 关键点 |
|---|---|---|---|
| **ollama serve** | 启动本地推理服务（11434） | `ollama serve &` | 语义检索的前提；后台常驻 |
| **ollama pull** | 下载模型到本机 | `ollama pull bge-m3` | 拉到即自动优先；断线可重试续传 |
| **ollama run** | 进入对话（没模型会先拉） | `ollama run qwen2.5:0.5b`（`/bye` 退出） | 嵌入模型不能对话，聊天用 qwen/llama |
| **ollama list** | 看已装模型 | `ollama list` | 出现 `bge-m3:latest` = 已自动优先 |
| **ollama ps** | 看正在跑的模型 | `ollama ps` | 占内存时查谁在吃资源 |
| **ollama rm** | 删模型 | `ollama rm <模型名>` | 别误删嵌入底座，检索靠它 |
| **ollama embeddings (REST)** | 程序调用向量化 | `curl .../api/embeddings -d '{"model":"bge-m3","prompt":"文本"}'` | `ibox --llm` 就是这么干的 |
| **ollama show** | 看模型元信息 | `ollama show bge-m3` | 查参数 / license / Modelfile |

**记忆口诀**：起（serve）→ 拉（pull）→ 用（run/list/ps）→ 删（rm）；嵌入另算（embeddings/show）。

**和 ibox 的关系**：`ibox how` 能直接搜上面任意一张——比如 `ibox 看模型详情` → `ollama show`、`ibox 拉模型` → `ollama pull`。
