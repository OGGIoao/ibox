# Personal Terminal Companion

> 👋 **接手本项目？** 按顺序读：[`AGENTS.md`](AGENTS.md) → [`STATUS.md`](STATUS.md) → [`MEMORY.md`](MEMORY.md) → 最近日记 [`daily/`](daily/)（中立日记；`.workbuddy/memory/` 是本机 Agent 私有记忆，clone 后没有属正常）。

> **你不用记命令名，只要会说“想做的事”。** 工具帮你找到一张可信、可复制、带风险提示和平台差异的命令卡。

---

## 这是什么

一个"边学边造"的 terminal 工具箱，也是**正式产品 Personal Terminal Companion** 的载体：正式产品核心由 `pycheat` 和命令卡真源 `terminal-toolbox/cheatsheet.md` 组成；离线搜索永远可用，Ollama 只提供可选语义增强。
用户面入口自 **2026-09-14** 起收敛为**唯一入口 `ibox`**（`how` / `find` / `add` / `done` / `ask` / `hi` / `sync`），旧名全部保留为兼容壳。完整产品边界见 [`scope.md`](docs/00-project/scope.md)，当前进度只看 [`STATUS.md`](STATUS.md)。

仓库中的配套内容：
- [`个人终端工具箱.md`](个人终端工具箱.md) — 本工具箱的说明书与成长路线图（工具卡 #1–#4 在此）
- [`操作系统底层与终端精通课程.md`](操作系统底层与终端精通课程.md) — OS / Shell 解释层
- [`芯片架构横向博览知识系统.md`](芯片架构横向博览知识系统.md) 与 [`芯片架构内功/`](芯片架构内功/) — 内容实验区，不属于当前核心产品承诺

---

## 工具清单

| # | 工具 | 形态 | 一句话 |
|---|------|------|--------|
| ★ | **`ibox`** | Python CLI（`terminal-toolbox/ibox`，软链 `~/bin/ibox`；短名 `c`） | **统一入口**（2026-09-14 起）：`how` 查命令 · `find` 搜自己的数据 · `add` / `done` 记与完成任务 · `ask` 问本地模型 · `hi` 机器信息 · `sync` 一键 git 同步 · `learn` 按功能域学习 · `card` 卡库注册与体检。直接敲 `ibox` 会打印完整使用指南 |
| — | `pycheat`（`pycheat.py`） | Python CLI | 命令卡引擎（正式产品核心），现被 `ibox how` 复用；旧名 `pycheat` / `c` 仍可用 |
| β | `tk`（`tk` + `tkcore.py`） | Python CLI | **Beta**：note / log / gitx / clip / todo / explain / sum，被 `ibox find` / `add` / `ask` 复用；旧名 `tk` 仍可用（ADR-001 要求冻结扩域，等待真实使用验证） |
| — | `hi`（`hi.sh`） | shell 脚本 | 已被 `ibox hi` 取代（Python 版，Windows 也能用） |
| — | `gup`（`gup.sh`） | shell 脚本 | 已被 `ibox sync` 取代（Python 版，Windows 也能用） |
| — | `cheat`（✗ 已废弃） | zsh 函数 | 已被取代（历史留档，见 `个人终端工具箱.md`） |

更完整的字段说明、截图式卡面示例，见 [`个人终端工具箱.md`](个人终端工具箱.md)。

---

## 目录结构

```
terminal-list/
├── README.md
├── 个人终端工具箱.md                 # 活文档（工具卡 + 路线图）
├── 操作系统底层与终端精通课程.md      # 主线课程
├── 芯片架构横向博览知识系统.md        # 横向行业追踪
├── 阶段总结-2026-08-12.md
├── LICENSE
├── .gitignore
├── terminal-toolbox/                # ← 真正可运行的工具
│   ├── pycheat.py        # 工具#4：命令速查 CLI（仅标准库；可选接本机 ollama 做语义检索，零额外依赖）
│   ├── tk + tkcore.py     # Beta：跨域工具入口 + 共享检索引擎
│   ├── hi.sh             # 工具#2：系统/身份速览
│   ├── gup.sh            # 工具#3：安全一键 git 同步
│   ├── seed_aliases.py   # 给 cheatsheet 批量补「别名:」字段的辅助脚本
│   └── cheatsheet.md     # 数据源（49 张卡，含 8 张 ollama 指令卡）；pycheat 读它
└── 可视化放映/                      # 课程配套幻灯片（HTML）
```

---

## 安装（macOS）

> 下面用 `~/bin` 做用户级命令目录（无需 `sudo`）。若该目录不在 `PATH`，先在 `~/.zshrc` 加一行：
> `export PATH="$HOME/bin:$PATH"`

```bash
# 1) 克隆（或下载）本仓库
git clone https://github.com/OGGIoao/terminal-list.git
cd terminal-list

# 2) 把脚本软链成全局命令（注意保持可执行）
chmod +x terminal-toolbox/*.sh terminal-toolbox/pycheat.py
ln -s "$PWD/terminal-toolbox/hi.sh"        ~/bin/hi
ln -s "$PWD/terminal-toolbox/gup.sh"       ~/bin/gup
ln -s "$PWD/terminal-toolbox/pycheat.py"   ~/bin/pycheat
ln -s "$PWD/terminal-toolbox/tk"           ~/bin/tk

# 3) 桥接层：c 别名 + 敲错提示钩子（旧版 cheat.zsh 已废弃，这里重建精简版）
cat > ~/.cheat.zsh <<'EOF'
# 个人终端工具箱 · 桥接层（c=pycheat + 敲错提示）
alias c='pycheat'
command_not_found_handler() {
  local q="$1"
  [ "${#q}" -lt 2 ] && return 127
  local hits
  hits=$(pycheat --suggest "$q" 2>/dev/null)
  [ -n "$hits" ] && echo "💡 你是不是想用这些命令？"$'\n'"$hits"
  return 127
}
EOF
echo '[ -s "$HOME/.cheat.zsh" ] && \. "$HOME/.cheat.zsh"' >> ~/.zshrc
source ~/.zshrc

# 4) 放好数据源 cheatsheet（推荐；不放也能跑，见下方"兜底"）
mkdir -p ~/.config/cheat
cp terminal-toolbox/cheatsheet.md ~/.config/cheat/cheatsheet.md
```

**Windows / Linux 说明**
- `pycheat` / `tk` 提供纯 Python 主路径和 Windows `.cmd` 入口；安装见 [`跨平台使用指南.md`](terminal-toolbox/跨平台使用指南.md)。Windows CI 覆盖 Python 路径，PowerShell 安装流程仍需真实设备验收。
- `hi.sh` / `gup.sh` 是 POSIX shell 辅助工具，不属于 Windows 核心承诺；Windows 需 WSL 或 Git Bash。

**cheatsheet 兜底**：`pycheat` 优先读 `~/.config/cheat/cheatsheet.md`；若该路径不存在，会自动改用**脚本同目录的 `cheatsheet.md`**。所以即便跳过第 4 步，clone 下来直接 `python3 terminal-toolbox/pycheat.py` 也能用。

---

## 快速上手

```bash
# pycheat：说人话就能搜
pycheat                       # 开场屏：置顶常用 + 最近查看 + ↻该复习的，输入"想做的事"回车即搜
pycheat 看哪个程序最占内存     # 直接意图搜索 → 进入彩色卡面浏览（命中后该说法被记住，下次直命中）
pycheat -c 看哪个文件夹最大    # 把最佳匹配的「示例」复制到剪贴板，⌘V 直接跑
pycheat -l                    # 列出全部 49 张卡（编号 + 一句话用途）
pycheat --learn show          # 查看你「教给它的」人话说法与命中次数
pycheat --forget 看哪个程序最占内存   # 忘掉某个自学习说法
pycheat --llm 哪个进程吃 RAM       # 强制本地 ollama 语义检索（同义也能命中；无 ollama 则报错退出）
pycheat --no-llm 看哪个程序最占内存  # 强制离线匹配（即便 ollama 在跑）

# c（= pycheat 的短名，已接好别名与敲错提示钩子）
c                             # 进开场屏：置顶常用 + 最近查看，输入"想做的事"回车即搜
c df                          # 直接搜某条

# hi：我是谁 / 在哪 / 什么芯片
hi
hi -v                         # 附带芯片架构信息

# gup：安全一键同步当前仓库
gup                           # 在当前 git 仓库里：ff-only pull → 时间戳提交 → push
```

浏览卡面时底部菜单：
`n/→/j` 下一张 · `p/←/k` 上一张 · `b` 回退 · `f` 前进 · `c` 复制示例 · `/` 重新搜索 · `q` 退出

---

## 数据源与自定义

所有卡片都在 `terminal-toolbox/cheatsheet.md`，格式极简——`## 标题` 起一张卡，下面用 `- 字段: 值` 写字段：

```markdown
## df
- 作用: 看磁盘各分区还剩多少空间
- 用法: df -h
- 示例: `df -h`
- 别名: 磁盘空间、哪个盘满了、disk free
- 踩坑: 默认按块显示不直观，务必加 -h 看人类可读单位
- Windows对照: macOS/Linux 用 df -h；Windows 用 `wsl df -h` 或资源管理器属性
- 来源卷: 终端工具箱·磁盘
```

- 想加自己的命令？直接往 `cheatsheet.md` 追加 `## 新命令` + 字段即可，`pycheat` / `c` 立刻能搜到。
- `别名:` 字段是"人话命中"的关键（中文二元组重叠 + 拼音 + 英文都能匹配）；`seed_aliases.py` 可批量给已有卡片补别名。
- `常用: 是` 标记的卡会出现在 pycheat 开场屏的"★ 你可能关心的指令"。

---

## 成长路线

工具按"循序渐进"的方式沉淀，逐步从易到难：

```
alias 别名  →  zsh 函数  →  .sh 脚本  →  软链到 ~/bin（用户级）
                                       →  oh-my-zsh 插件（团队化）
                                       →  Python CLI + 本地 ollama 向量语义查询（阶段2·已落地）
```

`pycheat` 是当前路线图的"阶段 2"：**离线、零依赖、即查即用**为基础，叠加**自学习别名**（越用越懂你）、**间隔复习**（开场屏提醒巩固）与**本地 ollama 语义检索**（同义/近义也能命中）。语义检索零额外依赖（仅 `urllib` 调本机 `11434`），自动探测 ollama——在跑就用语义、否则退回离线；`--llm` 强制、`--no-llm` 强制离线。

> 排序策略是**本地匹配为主、语义为温和加成**的融合排序（fusion）：本地命中分占主导，语义相似度只做相对温和加成，**绝不让语义覆盖一个清晰的本地命中**；零本地分的近义卡也能被语义抬出。嵌入模型默认 `nomic-embed-text`，若本机已拉取中文更强的 `bge-m3` 会自动优先（无需改代码）。

---

## 安全红线（务必遵守）

- `gup` 只在**当前仓库内**操作；**绝不 `rm` / `reset --hard` / `force push`**；先 ff-only pull 再提交，无改动直接退出。
- 自动化数据 `~/.workbuddy/workbuddy.db` **绝不用 `rm`/`sqlite3`/shell 删除**，只走自动化管理工具。
- 个人目录只提交明确要同步的文件，不盲目把无关改动一并提交。

---

## License

见 [`LICENSE`](LICENSE)（MIT）。
