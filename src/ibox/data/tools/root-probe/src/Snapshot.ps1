<#
  根系探测器｜快照对比
  装软件之前拍一张，装完拍一张，卸载后再拍一张。三张一比，它装了什么、卸载后留下了什么，一目了然。
  只读：快照只记录"哪里有什么"，存在本工具目录下的 records\snapshots 里。
#>
[CmdletBinding()]
param(
  [ValidateSet('', 'Take', 'Compare')]
  [string]$Action = '',
  [string]$Label,
  [string[]]$Files,
  [switch]$NoOpen,
  [string]$RecordsDir
)

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'Collect-Footprints.ps1')
. (Join-Path $PSScriptRoot 'Render-Report.ps1') -OutputDirectory $RecordsDir
$snapDir = Join-Path $script:RecordsDir 'snapshots'

function Save-Snapshot([string]$label) {
  Write-Echo '拍快照：把所有可能扎根的地方记一遍。大约需要半分钟。'
  $sw = [Diagnostics.Stopwatch]::StartNew()
  $records = Get-RootProbeRecords -Progress { param($m) Write-Host ('    {0,5:n0}s  {1}' -f $sw.Elapsed.TotalSeconds, $m) -ForegroundColor DarkGray }
  $snap = [ordered]@{ label = $label; takenAt = (Get-Date).ToString('yyyy-MM-ddTHH:mm:ss'); records = $records }
  New-Item -ItemType Directory -Force -Path $snapDir | Out-Null
  $safe = ($label -replace '[\\/:*?"<>|\s]+', '_')
  $path = Join-Path $snapDir ('{0}-{1}.json' -f (Get-Date -Format 'yyyyMMdd-HHmmss'), $safe)
  [IO.File]::WriteAllText($path, (ConvertTo-SafeJson $snap), (New-Object System.Text.UTF8Encoding $false))
  Write-Echo ("快照「{0}」已保存，记下了 {1} 处。" -f $label, $records.Count)
  return $path
}

function Compare-Snapshots([string[]]$paths) {
  # 直接拼接快照的 JSON 原文，不做二次转换，保证前后记录一字不差
  $texts = $paths | ForEach-Object { [IO.File]::ReadAllText($_, [Text.Encoding]::UTF8) }
  $head = [ordered]@{ mode = 'compare'; generatedAt = (Get-Date).ToString('yyyy-MM-ddTHH:mm:ss'); global = Get-GlobalChecks }
  $headJson = ConvertTo-SafeJson $head
  $json = $headJson.Substring(0, $headJson.Length - 1) + ',"snapshots":[' + ($texts -join ',') + ']}'
  $labels = ($paths | ForEach-Object { [IO.Path]::GetFileNameWithoutExtension($_).Substring(16) }) -join '-'
  $out = Write-RootProbeReport $json ('对比-' + $labels) -NoOpen:$NoOpen
  Write-Echo '对比报告已生成。'
  return $out
}

function Get-Snapshots { @(Get-ChildItem -LiteralPath $snapDir -Filter *.json -ErrorAction SilentlyContinue | Sort-Object Name) }

Write-Host ''
Write-Host '  根系探测器 · 快照对比 · 数字文明' -ForegroundColor Yellow
Write-Host '  只读：快照只记录"哪里有什么"，不改、不删任何东西。' -ForegroundColor DarkGray
Write-Host ''

if ($Action -eq 'Take') { Save-Snapshot $(if ($Label) { $Label } else { '快照' }); return }
if ($Action -eq 'Compare') { Compare-Snapshots $Files; return }

Write-Echo '用法：装软件前拍一张（比如叫"装之前"），装完拍一张（"装之后"），卸载后再拍一张（"卸载后"）。'
Write-Echo '然后选"对比"，按顺序选这三张。'
Write-Host ''
$snaps = Get-Snapshots
Write-Host '  1  拍一张新快照'
if ($snaps.Count -ge 2) { Write-Host '  2  对比已有的快照' }
Write-Host '  0  返回'
$choice = (Read-Host '  >').Trim()
if ($choice -eq '' -or $choice -eq '0') { return }

if ($choice -eq '1') {
  Write-Echo '给这张快照起个名字，比如：装之前、装之后、卸载后'
  $name = (Read-Host '  >').Trim()
  if (-not $name) { $name = '快照' }
  Save-Snapshot $name | Out-Null
} elseif ($choice -eq '2' -and $snaps.Count -ge 2) {
  Write-Host ''
  for ($i = 0; $i -lt $snaps.Count; $i++) {
    Write-Host ('  {0,2}  {1}' -f ($i + 1), $snaps[$i].BaseName)
  }
  Write-Echo '按时间顺序输入两张或三张的编号，用空格隔开，比如：1 2 3'
  Write-Echo '两张：看这段时间多了什么；三张：看卸载后还剩什么。'
  $nums = (Read-Host '  >') -split '\s+' | Where-Object { $_ -match '^\d+$' } | ForEach-Object { [int]$_ }
  $picked = @($nums | Where-Object { $_ -ge 1 -and $_ -le $snaps.Count } | ForEach-Object { $snaps[$_ - 1].FullName })
  if ($picked.Count -lt 2 -or $picked.Count -gt 3) { Write-Echo '需要两张或三张。'; exit 1 }
  Compare-Snapshots $picked | Out-Null
} else {
  Write-Echo '没有这个选项。'
}
