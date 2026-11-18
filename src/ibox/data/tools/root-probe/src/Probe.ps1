<#
  根系探测器｜勘探
  输入一个软件名或厂商名，画出它在电脑里扎下的全部根系。
  只读：不改、不删任何东西，不需要管理员权限，不联网。
  报告写在本工具目录下的 records\reports 里，删掉整个工具目录就什么都不剩。
#>
[CmdletBinding()]
param(
  [string]$Keyword,
  [switch]$NoOpen,
  [string]$RecordsDir
)

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'Collect-Footprints.ps1')
. (Join-Path $PSScriptRoot 'Render-Report.ps1') -OutputDirectory $RecordsDir

Write-Host ''
Write-Host '  根系探测器 · 数字文明' -ForegroundColor Yellow
Write-Host '  只读勘探：不改、不删、不上传任何东西。' -ForegroundColor DarkGray
Write-Host ''

if (-not $Keyword) {
  Write-Echo '要找谁的根？输入软件名或厂商名，英文效果最好。'
  Write-Echo '可以输入好几个词，用空格隔开，比如：360 qihoo'
  $Keyword = Read-Host '  >'
}
$Keyword = $Keyword.Trim()
if ($Keyword.Length -lt 2) {
  Write-Echo '关键词至少要两个字，太短会把不相干的东西也认成一家。'
  exit 1
}

Write-Host ''
Write-Echo "好，往下挖。大约需要半分钟。"
$sw = [Diagnostics.Stopwatch]::StartNew()
$records = Get-RootProbeRecords -Progress { param($m) Write-Host ('    {0,5:n0}s  {1}' -f $sw.Elapsed.TotalSeconds, $m) -ForegroundColor DarkGray }
$data = [ordered]@{
  mode = 'probe'
  keyword = $Keyword
  generatedAt = (Get-Date).ToString('yyyy-MM-ddTHH:mm:ss')
  global = Get-GlobalChecks
  records = $records
}
$out = Write-RootProbeReport (ConvertTo-SafeJson $data) $Keyword -NoOpen:$NoOpen
Write-Host ''
Write-Echo ("挖完了：翻了 {0} 处可能扎根的地方。报告已生成。" -f $records.Count)
Write-Host "    $out" -ForegroundColor DarkGray
Write-Output $out
