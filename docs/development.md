# 开发与源码入口

先阅读 [AGENTS.md](../AGENTS.md) 和 [NOW.md](../NOW.md)，确认当前阶段、产品边界和验证状态。

## 结构

| 位置 | 职责 |
| --- | --- |
| [cli.py](../src/ibox/cli.py) | 命令分发、工具列表与地图的返回位置、端口输入、根系菜单 |
| [ui.py](../src/ibox/ui.py) | 首页形象、地图、列表和结果文案 |
| [env.py](../src/ibox/env.py) | Windows 查询、固定脚本调用、用户路径与环境差异 |
| [data/tools](../src/ibox/data/tools) | 两件工具的 PowerShell、JS 和模板，随安装包分发 |
| [cards.py](../src/ibox/cards.py)、[search.py](../src/ibox/search.py) | 命令卡解析和检索 |
| [tests](../tests) | 命令分发、真实回环监听、筛选返回、保存路径和卡片回归 |

首页可以用一句话提问。工具列表和地图都能按编号打开工具，执行后由 `_diagnostics_home` 恢复来源视图。各工具的输入处理函数最终调用 `env.py` 中的系统查询或 `run_bundled_tool`。

## 验证

Python 运行依赖使用标准库，安装构建使用 setuptools。

```powershell
python -m pip install -e .
python -m unittest discover -s tests -v
python -m ibox card check
```

Windows 的真实端口回归会创建一次本机回环监听。Linux 和 macOS 的 CI 执行可运行的命令卡与路由测试。Windows 工具依赖 Windows PowerShell 5.1，文件检查窗使用系统 WinForms。

## 构建

```powershell
python -m pip wheel --no-deps --wheel-dir dist .
python -m pip install --user --force-reinstall dist/ibox-0.3.7-py3-none-any.whl
```

换版本后应同步 `pyproject.toml` 和 `src/ibox/__init__.py`。构建物在 `dist/`，由 Git 忽略。

PowerShell 文件采用 UTF-8 BOM。运行文件相对位置写在 `env.py` 的固定入口表中，包内资源由 `pyproject.toml` 的 `package-data` 收录。用户输入通过子进程环境中的 JSON 传给固定脚本，再转为 PowerShell 参数。

## 现有工具的维护

根系探测器和早期像素文件精灵起源于数字文明，当前源码以本仓库 `src/ibox/data/tools/` 为唯一维护位置，`Inspect-File.ps1` 提供原生文件检查窗。历史来源见 [NOTICE](../NOTICE.md)。

修复公共脚本时，核对旧工具的调用方式。例如根系脚本的 `RecordsDir` 在 iBox 里指向用户选择的位置，单独运行时仍有原来的默认值；`Summon-FileSpirit.ps1 -InfoOnly` 供原生窗取得指纹，原有 HTML 卡片入口仍在脚本中。

旧工具已归档，跨仓职责见[仓库分工](repository-roles.md)。
