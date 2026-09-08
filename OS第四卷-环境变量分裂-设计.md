# OS 第四卷 · 环境变量分裂 —— 系统化设计稿（待老Z确认后写正文）

> 定位：OS 底层与终端精通课程纵向主线第四卷。
> 设计原则：**系统讲解「环境变量与进程环境」的全部机制**，WeSight 找不到 CLI 只是其中一个病例，不再是唯一靶子。
> 延续风格：边讲边装（亲手验证）+ 安全视角（从第二卷起缝进）+ Windows↔macOS 对照（老Z 从 Windows 来）。

---

## 一句话主线

环境变量不是「全局设置」，而是「每个进程出生时从父进程拷贝的一份键值表」；macOS 上终端和 GUI 应用由不同的祖先启动，拿到的环境天然分裂——WeSight 只是这条规律的一个具体伤口。

---

## 章节设计（8 节，逐层递进）

### §1 环境变量到底是什么（破除直觉误区）
- **知识点**：进程的环境块 = key=value 字符串数组，随进程诞生；`fork/exec` 时子进程**拷贝**父环境；改自己不影响父/兄弟（每进程独立）。
- **核心瞬间**：「全局变量」是错觉——你在终端 `export` 的东西，只对「这个进程及其后代」可见，关掉终端就没了。
- **边讲边装**：`env` / `printenv` / `echo $PATH` 看自己进程的环境；`cat /proc/...`(Linux) 类比。
- **Windows 对照**：`set`(会话级) / `setx`(持久) / 系统变量 vs 用户变量。

### §2 环境是怎么一层层设起来的（Shell 侧）
- **知识点**：Shell 启动文件链（login vs interactive）：`/etc/zprofile → ~/.zprofile → /etc/zshrc → ~/.zshrc`；`export` 把变量从 shell 局部提升进环境块。
- **核心瞬间**：为什么 `PATH=...`（不 export）对子进程无效——回扣第三卷 3.5。
- **边讲边装**：`export FOO=bar; bash -c 'echo $FOO'` 验证继承；去掉 export 子进程看不到。

### §3 macOS 上 GUI 与 Shell 的「两个世界」（本卷核心）
- **知识点**：终端祖先链 `launchd → 用户会话 → Terminal.app → zsh`（读 .zshrc，环境你组装）；GUI 应用祖先链 `launchd → 应用`（**不读 .zshrc**）。
- **核心瞬间**：launchd 给 GUI 设的环境从哪来——`/etc/paths`、`/etc/paths.d/*`、LaunchAgents 的 `EnvironmentVariables`（`/etc/launchd.conf` 已废弃）。
- **边讲边装**：对比 `launchctl getenv PATH` vs 终端 `echo $PATH`；`ps -o comm -p <pid>` 看父进程。
- **收口到 WeSight**：你那个坑 = launchd 给 GUI 的环境不含 .zshrc 加的 PATH。

### §4 PATH 与 Homebrew：命令到底「装哪儿了」
- **知识点**：Intel Mac `/usr/local/bin` vs Apple Silicon `/opt/homebrew/bin`（后者不在老 PATH 里，需 shell 加）。
- **核心瞬间**：为什么 `brew` 终端能用、GUI 里 not found——PATH 没传给 GUI 世界。
- **边讲边装**：`which brew` / `ls -l $(which brew)` 看清真实路径。

### §5 让 GUI 找到命令：几种正统解法（不止软链一条路）
- 解法 A：软链到系统级 PATH（如 `/usr/local/bin`，需 sudo）—— 你给 WeSight 做的就是这招。
- 解法 B：`launchctl setenv`（临时，重启失效）/ 写 LaunchAgent 持久设 launchd 环境。
- 解法 C：应用自身配置（VS Code `terminal.integrated.env`、IDE 的 PATH 设置）。
- 解法 D：`env` 包装脚本 / `.app` 的 `Info.plist` `LSEnvironment`。
- **对比维度**：持久性 / 作用范围 / 是否需 sudo / 是否影响所有用户。

### §6 安全视角（课程红线，延伸第二卷）
- **知识点**：环境变量泄露（API key/token 写在 `.zshrc` 的 export，被所有子进程继承，甚至误传公开仓库——回扣 terminal-list 软链教训）；环境注入（恶意 LaunchAgent 篡改 launchd 环境，诱导加载恶意 PATH / `DYLD_INSERT_LIBRARIES` 经典攻击）；PATH 劫持在 GUI 世界的安全差异（已在第三卷 3.5 讲过，本卷延伸）。
- **意识动作**：不在环境里长期放密钥；审查 `~/Library/LaunchAgents`。

### §7 跨平台对照（Windows ↔ macOS ↔ WSL）
- **知识点**：Windows 系统/用户变量由 `explorer.exe` 继承给所有 GUI——**Windows 下 GUI 反而能读到，因为同一祖先**；WSL 环境来自其 init，与 Windows 宿主可互通，但 Windows GUI 读不到 WSL 的 PATH（反向分裂）。
- **结论**：分裂不是 macOS 独有，但 launchd 模型让「终端 vs GUI」分裂特别明显。

### §8 收束 + 下一卷预告
- 回到 WeSight 坑给出完整归因与多种解法选型；预告第五卷（权限）：文件权限、sudo、SIP 如何决定谁能改这些环境/路径。

---

## 与既有课程的回扣
- 第三卷 3.5（`export` 机制 / 每进程独立）→ 本卷 §1–§2 展开。
- 第三卷 3.4（启动链 login/interactive）→ 本卷 §2–§3 升级到 launchd 全局启动链。
- 第二卷安全视角（PATH 劫持 / 软链接）→ 本卷 §6 延伸（GUI 世界的环境注入）。

## 待老Z拍板的设计分叉
1. **范围**：8 节全做，还是先聚焦 §1–§5（机制+解法）、§6–§7（安全+跨平台）作为进阶？
2. **实操深度**：边讲边装要不要带一次「写 LaunchAgent 持久设 PATH」的真操作（涉及 ~/Library/LaunchAgents，需谨慎）？
3. **WeSight 软链是否补做验证**：第四卷写好后是顺手把你那次 `/usr/local/bin` 软链验证一遍，还是只讲解法不碰系统？
4. **篇幅**：按前三卷风格一卷入课程文档（长文），还是也出一套「第四卷可视化放映」配套页？

## 关联提醒（非本卷）
- 逻辑电路卷大纲第 08 页「多位加法器·级联」在已发布序列（slide 07 全加器 → 08 MUX）中暂未单独成页，是否补做待定，与第四卷无关。
