<#
  根系探测器｜报告生成
  把收集到的数据（JSON 文本）塞进报告模板，写成一个独立的 HTML 文件。
#>

param([string]$OutputDirectory)

$script:ToyRoot = Split-Path -Parent $PSScriptRoot
$script:RecordsDir = Join-Path $script:ToyRoot 'records'
if ($OutputDirectory) { $script:RecordsDir = $OutputDirectory }

function ConvertTo-SafeJson($obj) {
  # 内联进 <script> 时，"</" 会提前结束脚本标签，换成等价的 "<\/"
  ($obj | ConvertTo-Json -Depth 6 -Compress).Replace('</', '<\/')
}

function Write-RootProbeReport([string]$dataJson, [string]$fileStem, [switch]$NoOpen) {
  $template = [IO.File]::ReadAllText((Join-Path $PSScriptRoot 'report-template.html'), [Text.Encoding]::UTF8)
  $probeJs = [IO.File]::ReadAllText((Join-Path $PSScriptRoot 'probe.js'), [Text.Encoding]::UTF8)
  $html = $template.Replace('/*PROBE_JS*/', $probeJs).Replace('/*PROBE_DATA*/', $dataJson)
  $dir = Join-Path $script:RecordsDir 'reports'
  New-Item -ItemType Directory -Force -Path $dir | Out-Null
  $safeStem = ($fileStem -replace '[\\/:*?"<>|\s]+', '_')
  $out = Join-Path $dir ('{0}-{1}.html' -f (Get-Date -Format 'yyyyMMdd-HHmmss'), $safeStem)
  [IO.File]::WriteAllText($out, $html, (New-Object System.Text.UTF8Encoding $false))
  if (-not $NoOpen) { Start-Process -FilePath $out }
  return $out
}

function Write-Echo([string]$text) {
  Write-Host '  ▍ ' -ForegroundColor Cyan -NoNewline
  Write-Host $text
}
