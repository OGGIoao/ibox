# install.ps1 — terminal-toolbox Windows 一键安装
# 用法（任选其一）：
#   1) 资源管理器里右键本文件 →「使用 PowerShell 运行」
#   2) 在 PowerShell 中：cd 到本目录后执行  .\install.ps1
# 作用：
#   1) 检查 Python（语义检索可选检查 ollama）
#   2) 把工具箱目录加入「用户 PATH」（持久化，重启终端生效）
#   3) 在 PowerShell $PROFILE 写入别名块 ibox / c / pycheat / tk
#      （首尾标记包裹：可重复运行，重复运行会原地升级，不堆叠重复定义）
# 全程不修改系统盘以外的任何文件。

$ErrorActionPreference = "Stop"
$TB = $PSScriptRoot  # 本脚本所在目录，即工具箱根

Write-Host "== terminal-toolbox Windows 安装 ==" -ForegroundColor Cyan

# ---------- 1) 检查 Python ----------
$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) { $py = Get-Command py -ErrorAction SilentlyContinue }
if (-not $py) {
    Write-Host "❌ 未检测到 Python。" -ForegroundColor Red
    Write-Host "   请先安装 Python 3.9+，并务必勾选安装界面的 'Add python.exe to PATH'。" -ForegroundColor Yellow
    Write-Host "   下载：https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "   装好重新运行本脚本即可。" -ForegroundColor Yellow
    pause
    exit 1
}
Write-Host "✅ Python: $($py.Source)" -ForegroundColor Green

# ---------- 2) 可选检查 ollama（语义检索用）----------
$ol = Get-Command ollama -ErrorAction SilentlyContinue
if ($ol) {
    Write-Host "✅ ollama 已安装（语义检索可用；首次用会提示拉取 bge-m3/nomic-embed-text）" -ForegroundColor Green
} else {
    Write-Host "⚠️ 未检测到 ollama（可选）。装了才能用本地语义检索：" -ForegroundColor Yellow
    Write-Host "   下载：https://ollama.com/download" -ForegroundColor Yellow
}

# ---------- 3) 加入用户 PATH（持久化）----------
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($userPath -notlike "*$TB*") {
    if ([string]::IsNullOrEmpty($userPath)) { $newPath = $TB }
    else { $newPath = $userPath.TrimEnd(';') + ";" + $TB }
    [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
    Write-Host "✅ 已将工具箱目录加入用户 PATH：`n   $TB" -ForegroundColor Green
} else {
    Write-Host "✅ 工具箱目录已在用户 PATH 中" -ForegroundColor Green
}

# ---------- 4) 写 PowerShell 别名块（首尾标记 → 幂等且可原地升级）----------
$begin = "# >>> terminal-toolbox aliases >>>"
$end   = "# <<< terminal-toolbox aliases <<<"
$block = @"
$begin
function ibox { python "$TB\ibox" @args }
function c { python "$TB\ibox" @args }
function pycheat { python "$TB\pycheat.py" @args }
function tk { python -c "import runpy; runpy.run_path(r'$TB\tk', run_name='__main__')" @args }
$end
"@

if (-not (Test-Path $PROFILE)) {
    New-Item -ItemType File -Path $PROFILE -Force | Out-Null
}
$existing = Get-Content $PROFILE -Raw -ErrorAction SilentlyContinue
if ($null -eq $existing) { $existing = "" }
$pattern = "(?s)" + [regex]::Escape($begin) + ".*?" + [regex]::Escape($end)

if ($existing -match $pattern) {
    # 已有旧块 → 原地替换（保证重跑得到最新别名，不留残留定义）
    $stripped = [regex]::Replace($existing, $pattern, "").TrimEnd()
    if ([string]::IsNullOrEmpty($stripped)) { Set-Content -Path $PROFILE -Value $block }
    else { Set-Content -Path $PROFILE -Value ($stripped + "`r`n`r`n" + $block) }
    Write-Host "✅ 已更新 $PROFILE 中的别名块：ibox / c / pycheat / tk" -ForegroundColor Green
} else {
    Add-Content -Path $PROFILE -Value "`r`n$block"
    Write-Host "✅ 已在 $PROFILE 追加别名块：ibox / c / pycheat / tk" -ForegroundColor Green
}

Write-Host ""
Write-Host "🎉 安装完成！请「重新打开 PowerShell」使 PATH 与别名生效，然后试试：" -ForegroundColor Cyan
Write-Host "   ibox                 # 开场屏：使用指南全在里面" -ForegroundColor White
Write-Host "   ibox how 查端口占用    # 人话搜命令（也可直接 c 查端口占用）" -ForegroundColor White
Write-Host "   ibox find 部署报错     # 搜你自己的笔记 / 日志 / 提交" -ForegroundColor White
Write-Host "   ibox add `"改 ssh 端口`"    # 记一条快记" -ForegroundColor White
Write-Host "   ibox hi               # 我在哪台机器" -ForegroundColor White
Write-Host ""
Write-Host "c 是 ibox 的短别名；旧名 pycheat / tk 仍可用（内部转调 ibox）。" -ForegroundColor DarkGray
Write-Host "数据同步：把 C:\Users\你\.config\cheat\cheatsheet.md 放进 OneDrive/iCloud 并双向同步，" -ForegroundColor DarkGray
Write-Host "即可让 Windows 与 macOS 共享同一份命令卡（详见跨平台使用指南.md）。" -ForegroundColor DarkGray
pause
