# Personal Terminal Companion

> 👋 **接手本项目？** 按顺序读：[`AGENTS.md`](AGENTS.md) → [`STATUS.md`](STATUS.md) → [`MEMORY.md`](MEMORY.md) → 最近日记 [`daily/`](daily/)。已知坑与已修 bug 见 [`docs/02-engineering/pitfalls.md`](docs/02-engineering/pitfalls.md)。

> **你不用记命令名，只要会说"想做的事"。** 工具帮你找到一张可信、可复制、带风险提示和平台差异的命令卡。

---

## 这是什么

一个"边学边造"的 terminal 工具箱，也是**正式产品 Personal Terminal Companion** 的载体：正式产品核心由 `pycheat` 和命令卡真源 `terminal-toolbox/cheatsheet.md` 组成；离线搜索永远可用，Ollama 只提供可选语义增强。

用户面入口自 **2026-09-14** 起收敛为**唯一入口 `ibox`**（`how` / `find` / `add` / `done` / `ask` / `hi` / `sync` / `learn` / `card`），旧名全部保留为兼容壳。完整产品边界见 [`scope.md`](docs/00-project/scope.md)，当前进度只看 [`STATUS.md`](STATUS.md)。

仓库中的配套内容：
- [`个人终端工具箱.md`](个人终端工具箱.md) — 活文档：成长路线 + 历史工具卡（#1–#4）
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

更完整的字段说明与卡面示例，见 [`ibox-使用说明.md`](terminal-toolbox/ibox-使用说明.md)。

---

## 目录结构

```
terminal-list/
├── README.md                        # 你在这里（人类蓝图）
├── AGENTS.md                        # 接手入口：Agent / 人先读这份
├── STATUS.md                        # 当前态：主线 / 下一动作 / 阻塞
├── MEMORY.md                        # 跨任务长期事实与约定
├── CLAUDE.md → AGENTS.md            # 软链（同源，避免两份漂移）
├── docs/
│   ├── 00-project/scope.md          # 产品边界（Goal / Non-Goal）
│   ├── 01-design/decisions/         # ADR 决策记录（ADR-001 边界、ADR-002 入口收敛）
│   └── 02-engineering/pitfalls.md   # 踩坑库（P1…P17，已知坑的唯一归档地）
├── specs/m0-acceptance.md           # M0 验收规格 + 8 条 golden queries
├── daily/                           # 中立工作日记（append-only）
├── terminal-toolbox/                # ← 真正可运行的工具
│   ├── ibox             # 统一入口（用户面唯一命令）
│   ├── pycheat.py       # 命令卡引擎（被 ibox how 复用）
│   ├── tk + tkcore.py   # 数据域层 + 共享引擎（被 ibox find / add / ask 复用）
│   ├── *.cmd + install.ps1   # Windows 入口与一键安装
│   └── cheatsheet.md    # 数据源出厂副本（59 张卡，7 个功能域）
├── tests/ · scripts/                # 测试与 CI 辅助（HTML 链接检查等）
├── 个人终端工具箱.md                 # 活文档：成长路线 + 历史工具卡
├── 操作系统底层与终端精通课程.md      # OS / Shell 主线课程
├── 芯片架构横向博览知识系统.md        # 内容实验区（横向产业）
├── 芯片架构内功/                     # 内容实验区（纵向深潜 + 交互动画）
├── 可视化放映/                       # 课程配套幻灯片（零依赖 HTML）
└── 阶段总结-2026-08-12.md
```

---

## 安装（macOS）

> 下面用 `~/bin` 做用户级命令目录（无需 `sudo`）。若该目录不在 `PATH`，先在 `~/.zshrc` 加一行：
> `export PATH="$HOME/bin:$PATH"`

```bash
# 1) 克隆（或下载）本仓库
git clone https://github.com/OGGIoao/terminal-list.git
cd terminal-list

# 2) 把入口软链成全局命令（软链直指仓库 —— 改仓库即生效，无须再 cp）
chmod +x terminal-toolbox/ibox terminal-toolbox/tk terminal-toolbox/pycheat.py
ln -s "$PWD/terminal-toolbox/ibox"        ~/bin/ibox
ln -s "$PWD/terminal-toolbox/tk"          ~/bin/tk
ln -s "$PWD/terminal-toolbox/pycheat.py"  ~/bin/pycheat

# 3) 桥接层：短名 c + 敲错命令时的提示钩子
cat > ~/.cheat.zsh <<'EOF'
# 个人终端工具箱 · 桥接层（c = ibox + 敲错提示）
alias c='ibox'
command_not_found_handler() {
  local tried="$1"
  [[ ${#tried} -lt 2 ]] && return 1        # 太短的尝试不触发（省一次 python 启动）
  [[ "$tried" == */* ]] && return 1        # 像路径的（含 /）不是命令拼写，跳过
  local sug
  sug=$(command ibox how --suggest "$tried" 2>/dev/null)
  if [[ -n "$sug" ]]; then
    echo "没找到命令 '$tried'，但 ibox 里有相关的：" >&2
    echo "$sug" | tr '\n' ' ' >&2; echo "" >&2
  fi
  return 1
}
EOF
echo '[ -s "$HOME/.cheat.zsh" ] && \. "$HOME/.cheat.zsh"' >> ~/.zshrc
source ~/.zshrc

# 4) 数据源无需手动准备 —— 首次运行会自动把出厂副本初始化到
#    ~/.config/cheat/cheatsheet.md（零配置，且不污染仓库）
ibox hi
```

**Windows / Linux 说明**
- **Windows**：在 PowerShell 里跑 `.\terminal-toolbox\install.ps1` —— 一键把工具目录加入 PATH，并写好 `c` / `ibox` / `tk` / `pycheat` 别名（幂等，可重复运行）。入口脚本为 `ibox.cmd` / `pycheat.cmd` / `tk.cmd`。详见 [`跨平台使用指南.md`](terminal-toolbox/跨平台使用指南.md)。
- `hi` / `gup` 已由 `ibox hi` / `ibox sync`（Python 实现）取代，**Windows 同样可用**；旧的 `hi.sh` / `gup.sh` 保留仅为历史留档。

**数据源与兜底**：`ibox` 优先读 `~/.config/cheat/cheatsheet.md`；若该文件不存在，会自动从**脚本同目录**的出厂副本复制过去并提示（所以第 4 步不需要手动操作）。用户加卡落在用户级目录、可跨机同步，仓库内置副本保持不变。

---

## 快速上手

```bash
# 直接敲 ibox —— 会打印完整使用指南（不用记子命令）
ibox

# 查命令怎么用（说人话就行）
ibox how 端口占用           # → 命中 lsof 卡，进入彩色卡面浏览
ibox 端口占用               # 省略子命令等价于 how（兼容 c 的肌肉记忆）

# 搜你自己的数据（note / todo / clip / git / log）
ibox find 备份              # 默认搜快记（note）
ibox find --in todo         # 搜任务盒
ibox find "连接被拒绝" --in log   # 在日志里跨语言捞针

# 记一条 / 标记完成（列表会显示可引用的短 id）
ibox add "改 ssh 端口前先备份"
ibox add "周五交报告" --in todo
ibox done a3f21c

# 学习模式
ibox learn                  # 分类目录 + 进度条
ibox learn 网络              # 依次过某一类（可只写关键词）
ibox learn --卷 2            # 按 OS 课卷筛
ibox learn --due            # 只过「该复习的」

# 维护卡库
ibox card check             # 体检：分类 / 课卷 / 字段 / 卡名唯一
ibox card insert 新卡.md     # 按卡里的「分类」自动插进对应分区
ibox card sync              # 对齐用户级与仓库版两份数据源

# 机器信息 / 一键 git 同步 / 问本地模型
ibox hi                     # 我是谁 / 在哪 / 什么系统
ibox hi -v                  # 附芯片与内存信息
ibox sync                   # 当前仓库：ff-only pull → 提交 → push
ibox ask tar -xzf           # 问本地模型（需本机有 chat 模型）
```

浏览卡面时底部菜单：
`n/→/j` 下一张 · `p/←/k` 上一张 · `b` 回退 · `f` 前进 · `c` 复制示例 · `/` 重新搜索 · `q` 退出

**旧名全部仍可用**：`c`（= `ibox` 短名）· `pycheat` · `tk` · `hi` · `gup` —— 入口改名不破坏已有习惯。

---

## 数据源与自定义

所有卡片在 `terminal-toolbox/cheatsheet.md`（**出厂副本**；实际生效的是 `~/.config/cheat/cheatsheet.md`），按 **7 个功能域**分区。每张卡长这样：

```markdown
## df
- 分类: 文件与磁盘              # 受控词表（7 个功能域之一），机器据此归位
- 课卷: 2                      # OS 课卷号；`-` 表示工具箱自带，跨卷写 `2,7`
- 别名: 磁盘空间,哪个盘满了,disk free
- 作用: 看磁盘各分区还剩多少空间
- 用法: `df -h`
- 示例: `df -h`
- 踩坑: 默认按块显示不直观，务必加 -h 看人类可读单位
- Windows对照: Windows 用 `wsl df -h` 或资源管理器属性
- 来源卷: 第二卷 文件系统        # 自由文本，供人追溯（安全视角 / 实战标记放这里）
```

- **加卡请用 `ibox card insert 新卡.md`** —— 它按卡里的「分类」自动插进对应分区并刷新分区卡数；分类非法 / 字段缺失 / 卡名重复会被直接拒绝，不会静默乱放。**手工往文件末尾追加会破坏分区结构。**
- 加完跑 `ibox card check` 体检，再跑 `ibox card sync` 对齐两份数据源。
- `别名:` 是「人话命中」的关键（中文二元组重叠 + 拼音 + 英文都能匹配）。
- `常用: 是` 标记的卡会出现在开场屏的「★ 你可能关心的指令」。

---

## 成长路线

工具按"循序渐进"的方式沉淀，逐步从易到难：

```
alias 别名  →  zsh 函数  →  .sh 脚本  →  软链到 ~/bin（用户级）
                                       →  oh-my-zsh 插件（团队化）
                                       →  Python CLI + 本地 ollama 向量语义查询（阶段2·已落地）
                                       →  统一入口 ibox（阶段3·2026-09-14 已落地）
```

`ibox`（引擎为 `pycheat`）是当前路线图的「阶段 2 + 3」：**离线、零依赖、即查即用**为基础，叠加**自学习别名**（越用越懂你）、**间隔复习**（开场屏提醒巩固）与**本地 ollama 语义检索**（同义 / 近义也能命中）。语义检索零额外依赖（仅 `urllib` 调本机 `11434`），自动探测 ollama —— 在跑就用语义、否则退回离线；`--llm` 强制、`--no-llm` 强制离线。

> 排序策略是**本地匹配为主、语义为温和加成**的融合排序（fusion）：本地命中分占主导，语义相似度只做相对温和加成，**绝不让语义覆盖一个清晰的本地命中**；零本地分的近义卡也能被语义抬出。嵌入模型默认 `nomic-embed-text`，若本机已拉取中文更强的 `bge-m3` 会自动优先（无需改代码）。
>
> 排序的已知精度缺陷（如长句查询里 `stat` 压过 `scp`）记录在 [`pitfalls.md` P15](docs/02-engineering/pitfalls.md)，未修。

---

## 安全红线（务必遵守）

- `ibox sync`（原 `gup`）只在**当前仓库内**操作；**绝不 `rm` / `reset --hard` / `force push`**；先 ff-only pull 再提交，无改动直接退出。
- 自动化数据 `~/.workbuddy/workbuddy.db` **绝不用 `rm`/`sqlite3`/shell 删除**，只走自动化管理工具。
- 个人目录只提交明确要同步的文件，不盲目把无关改动一并提交。
- 开发协作红线（单一数据源、软链约定、加卡方式等）见 [`AGENTS.md` §6](AGENTS.md)。

---

## License

见 [`LICENSE`](LICENSE)（MIT）。
