@echo off
setlocal
rem terminal-toolbox — Windows 入口（统一工具箱 ibox）
rem 用法：把本目录加入 PATH 后，直接敲 ibox（c 是它的短别名）。
rem ibox 在仓库内无 .py 后缀（供 macOS 软链），Windows 用 runpy 执行无后缀脚本，
rem 这样 macOS 与 Windows 共用同一份 ibox 源码，不漂移。
if not defined PYTHON (set "PYTHON=python")
where %PYTHON% >nul 2>nul
if errorlevel 1 set "PYTHON=py"
%PYTHON% -c "import runpy; runpy.run_path(r'%~dp0ibox', run_name='__main__')" %*
endlocal
