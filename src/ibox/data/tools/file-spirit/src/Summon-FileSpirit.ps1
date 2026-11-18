<#
  文件精灵｜召唤程序
  由右键菜单调用：Windows 把被右键的那个文件的路径填进命令里的 "%1"，作为 -Path 传进来。
  只读取文件信息和 SHA-256 指纹，绝不修改原文件；生成的卡片写到临时目录。
#>
[CmdletBinding()]
param(
  [Parameter(Mandatory = $true, Position = 0)]
  [string]$Path,
  [string]$OutDir = (Join-Path $env:TEMP 'DigitalCivilization-FileSpirit'),
  [switch]$NoOpen,
  [switch]$InfoOnly
)

$ErrorActionPreference = 'Stop'

try {
  $item = Get-Item -LiteralPath $Path -Force
  if ($item.PSIsContainer) {
    throw '请对文件使用“召唤文件精灵”，文件夹里没有精灵。'
  }

  $hash = (Get-FileHash -LiteralPath $item.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
  # 只放文件名，不放完整路径：路径里可能有用户名，卡片会被截图分享
  $info = [ordered]@{
    name = $item.Name
    ext = $item.Extension.TrimStart('.').ToLowerInvariant()
    size = $item.Length
    created = $item.CreationTime.ToString('yyyy-MM-ddTHH:mm:ss.fffzzz')
    modified = $item.LastWriteTime.ToString('yyyy-MM-ddTHH:mm:ss.fffzzz')
    sha256 = $hash
  }
  if ($InfoOnly) { return [pscustomobject]$info }
  $json = $info | ConvertTo-Json -Compress

  $template = [IO.File]::ReadAllText((Join-Path $PSScriptRoot 'card-template.html'), [Text.Encoding]::UTF8)
  $spiritJs = [IO.File]::ReadAllText((Join-Path $PSScriptRoot 'spirit.js'), [Text.Encoding]::UTF8)
  $html = $template.Replace('/*SPIRIT_JS*/', $spiritJs).Replace('/*SPIRIT_DATA*/', $json)

  New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
  $out = Join-Path $OutDir ('spirit-{0}.html' -f $hash.Substring(0, 12))
  [IO.File]::WriteAllText($out, $html, (New-Object System.Text.UTF8Encoding $false))

  if (-not $NoOpen) { Start-Process -FilePath $out }
  Write-Output $out
}
catch {
  if ($NoOpen -or $InfoOnly) { throw }
  Add-Type -AssemblyName PresentationFramework
  [System.Windows.MessageBox]::Show($_.Exception.Message, '文件精灵', 'OK', 'Warning') | Out-Null
  exit 1
}
