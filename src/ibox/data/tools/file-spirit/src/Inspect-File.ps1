param(
  [string]$Path,
  [string]$LegacyCards
)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
[System.Windows.Forms.Application]::EnableVisualStyles()

function Select-InspectionFile($owner, [string]$title) {
  $dialog = New-Object System.Windows.Forms.OpenFileDialog
  $dialog.Title = $title
  $dialog.CheckFileExists = $true
  try {
    $choice = if ($owner) { $dialog.ShowDialog($owner) } else { $dialog.ShowDialog() }
    if ($choice -eq 'OK') { return $dialog.FileName }
  }
  finally { $dialog.Dispose() }
}

function Get-Inspection([string]$file) {
  & (Join-Path $PSScriptRoot 'Summon-FileSpirit.ps1') -Path $file -InfoOnly
}

function Compare-Inspection($first, $second) {
  if ($first.sha256 -eq $second.sha256) { return '指纹相同，文件内容一致。' }
  return '指纹不同，文件内容不一致。'
}

function Export-Inspection([string]$destination, [string]$summary) {
  $stream = [IO.File]::Open($destination, [IO.FileMode]::CreateNew)
  try {
    $bytes = [Text.Encoding]::UTF8.GetBytes($summary)
    $stream.Write($bytes, 0, $bytes.Length)
  }
  finally { $stream.Dispose() }
}

if (-not $Path) { $Path = Select-InspectionFile $null '文件精灵 · 选择要检查的文件' }
if (-not $Path) { return }
$Path = (Get-Item -LiteralPath $Path).FullName
$info = Get-Inspection $Path
$size = '{0:N0} 字节' -f $info.size
$modified = ([DateTimeOffset]::Parse($info.modified)).ToString('yyyy-MM-dd HH:mm:ss')

$window = New-Object System.Windows.Forms.Form
$window.Text = '文件精灵 · 文件检查'
$window.StartPosition = 'CenterScreen'
$window.Font = New-Object System.Drawing.Font('Microsoft YaHei UI', 10)
$window.ClientSize = New-Object System.Drawing.Size(696, 376)
$window.MinimumSize = New-Object System.Drawing.Size(540, 410)
$window.AutoScaleMode = 'Font'

$layout = New-Object System.Windows.Forms.TableLayoutPanel
$layout.Dock = 'Fill'
$layout.Padding = New-Object System.Windows.Forms.Padding(16)
$layout.ColumnCount = 2
[void]$layout.ColumnStyles.Add((New-Object System.Windows.Forms.ColumnStyle('Absolute', 118)))
[void]$layout.ColumnStyles.Add((New-Object System.Windows.Forms.ColumnStyle('Percent', 100)))
$window.Controls.Add($layout)
$layout.RowCount = 9
foreach ($height in 36, 32, 32, 32, 32, 32, 33, 52) {
  [void]$layout.RowStyles.Add((New-Object System.Windows.Forms.RowStyle('Absolute', $height)))
}
[void]$layout.RowStyles.Add((New-Object System.Windows.Forms.RowStyle('Percent', 100)))

$title = New-Object System.Windows.Forms.Label
$title.Text = '检查这份文件'
$title.Font = New-Object System.Drawing.Font('Microsoft YaHei UI', 14, [System.Drawing.FontStyle]::Bold)
$title.Dock = 'Fill'
$layout.Controls.Add($title, 0, 0)
$layout.SetColumnSpan($title, 2)

$rows = [ordered]@{
  '文件名' = $info.name
  '文件位置' = $Path
  '文件大小' = $size
  '修改时间' = $modified
  '内容指纹' = $info.sha256
}
$row = 1
foreach ($entry in $rows.GetEnumerator()) {
  $label = New-Object System.Windows.Forms.Label
  $label.Text = $entry.Key
  $label.TextAlign = 'MiddleLeft'
  $label.Dock = 'Fill'
  $layout.Controls.Add($label, 0, $row)
  $field = New-Object System.Windows.Forms.TextBox
  $field.Text = $entry.Value
  $field.ReadOnly = $true
  $field.AccessibleName = $entry.Key
  if ($entry.Key -eq '内容指纹') { $field.Font = New-Object System.Drawing.Font('Consolas', 9) }
  $field.Dock = 'Fill'
  $layout.Controls.Add($field, 1, $row)
  $row++
}

$hint = New-Object System.Windows.Forms.Label
$hint.Text = '内容指纹（SHA-256）根据文件内容计算，可以用来核对副本。'
$hint.Dock = 'Fill'
$layout.Controls.Add($hint, 0, 6)
$layout.SetColumnSpan($hint, 2)
$status = New-Object System.Windows.Forms.Label
$status.Text = '可以对比另一份文件，例如下载前后的两份副本。'
$status.Dock = 'Fill'
$status.ForeColor = [System.Drawing.SystemColors]::HotTrack
$layout.Controls.Add($status, 0, 7)
$layout.SetColumnSpan($status, 2)

$actions = New-Object System.Windows.Forms.FlowLayoutPanel
$actions.Dock = 'Fill'
$layout.Controls.Add($actions, 0, 8)
$layout.SetColumnSpan($actions, 2)

function Add-InspectorButton([string]$text, [scriptblock]$onClick) {
  $button = New-Object System.Windows.Forms.Button
  $button.Text = $text
  $button.AutoSize = $true
  $button.Add_Click($onClick)
  $actions.Controls.Add($button)
}

Add-InspectorButton '对比另一个文件' {
  $other = Select-InspectionFile $window '选择另一份文件做对比'
  if ($other) {
    $window.UseWaitCursor = $true
    $status.Text = '正在计算另一份文件的指纹…'
    $status.Refresh()
    try {
      $second = Get-Inspection $other
      $status.Text = "与 $($second.name) 对比：$(Compare-Inspection $info $second)"
    }
    catch { $status.Text = "无法读取另一份文件。$($_.Exception.Message)" }
    finally { $window.UseWaitCursor = $false }
  }
}
Add-InspectorButton '复制指纹' {
  try {
    [System.Windows.Forms.Clipboard]::SetText($info.sha256)
    $status.Text = '已复制当前文件的内容指纹。'
  }
  catch { $status.Text = '剪贴板暂时不可用。可以选中指纹按 Ctrl+C。' }
}
Add-InspectorButton '另存检查结果' {
  $dialog = New-Object System.Windows.Forms.SaveFileDialog
  $dialog.Title = '选择检查结果的保存位置'
  $dialog.Filter = '文本文件 (*.txt)|*.txt'
  $dialog.FileName = $info.name + '.检查.txt'
  $dialog.OverwritePrompt = $false
  try {
    if ($dialog.ShowDialog($window) -eq 'OK') {
      $summary = ($rows.GetEnumerator() | ForEach-Object { "$($_.Key)  $($_.Value)" }) -join [Environment]::NewLine
      Export-Inspection $dialog.FileName $summary
      $status.Text = "已保存到 $($dialog.FileName)"
    }
  }
  catch { $status.Text = '这次没有保存成功。请试试另一个位置或文件名。' }
  finally { $dialog.Dispose() }
}
if ($LegacyCards -and (Test-Path -LiteralPath $LegacyCards -PathType Container)) {
  Add-InspectorButton '管理旧卡片' {
    try {
      Start-Process -FilePath $LegacyCards
      $status.Text = '可以在资源管理器里删除不需要的旧卡片。'
    }
    catch { $status.Text = '无法打开旧卡片目录。' }
  }
}

try { [void]$window.ShowDialog() }
finally { $window.Dispose() }
