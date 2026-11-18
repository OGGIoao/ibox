<#
  根系探测器｜收集器
  把电脑上"软件可能留下足迹"的位置全部读一遍，整理成统一格式的记录。
  全程只读：注册表一律以只读方式打开，不改、不删任何文件，不需要管理员权限。
  每条记录：kind（种类）、name（名字）、location（登记在哪）、target（指向的文件）、
            exists（目标还在不在）、signer（签名者）、sig（签名状态）、extra（附加信息）
#>

$script:SigCache = @{}
$script:UserName = $env:USERNAME
$script:UserProfile = $env:USERPROFILE
$script:WinDir = ($env:SystemRoot + '\').ToLowerInvariant()

# —— 隐私：报告会被截图分享 ——
function Hide-Private([string]$text) {
  if (-not $text) { return $text }
  $t = $text
  if ($script:UserProfile) { $t = $t -ireplace [regex]::Escape($script:UserProfile), '%USERPROFILE%' }
  if ($script:UserName -and $script:UserName.Length -ge 3) { $t = $t -ireplace [regex]::Escape($script:UserName), '<用户>' }
  $t = $t -replace 'S-1-5-21-[\d-]+', 'S-1-5-21-…'
  return $t
}

# —— 注册表：直接用 .NET 只读打开，比 PowerShell 的注册表驱动器快得多 ——
$script:Hives = @{
  'HKCU' = [Microsoft.Win32.Registry]::CurrentUser
  'HKLM' = [Microsoft.Win32.Registry]::LocalMachine
  'HKCR' = [Microsoft.Win32.Registry]::ClassesRoot
}

function Open-RegKey([string]$path) {
  # 路径写成 "HKCU\Software\..."；OpenSubKey 的第二个参数 $false 表示只读
  $parts = $path -split '\\', 2
  $root = $script:Hives[$parts[0]]
  if (-not $root -or $parts.Count -lt 2) { return $null }
  try { return $root.OpenSubKey($parts[1], $false) } catch { return $null }
}

function Get-SubKeyNames([string]$path) {
  $k = Open-RegKey $path
  if (-not $k) { return @() }
  try { return $k.GetSubKeyNames() } catch { return @() } finally { $k.Close() }
}

function Get-RegValue([string]$path, [string]$name = '') {
  $k = Open-RegKey $path
  if (-not $k) { return $null }
  try { return $k.GetValue($name) } catch { return $null } finally { $k.Close() }
}

function Get-RegValues([string]$path) {
  $map = [ordered]@{}
  $k = Open-RegKey $path
  if (-not $k) { return $map }
  try { foreach ($n in $k.GetValueNames()) { $map[$n] = $k.GetValue($n) } } catch { } finally { $k.Close() }
  return $map
}

# —— 从一行命令里取出它真正指向的文件 ——
function Resolve-TargetPath([string]$command) {
  if (-not $command) { return $null }
  $c = [Environment]::ExpandEnvironmentVariables($command.Trim())
  if ($c -match '^"([^"]+)"') { $p = $Matches[1] }
  elseif ($c -match '^(.+?\.(exe|dll|sys|cmd|bat|ps1|vbs|js|com|scr|cpl|ocx))(\s|,|$)') { $p = $Matches[1] }
  else { $p = ($c -split '\s+')[0] }
  $p = $p.Trim() -replace '^\\\?\?\\', ''
  $p = $p -ireplace '^\\SystemRoot\\', ($env:SystemRoot + '\')
  if ($p -imatch '^system32\\') { $p = Join-Path $env:SystemRoot $p }
  if ($p -and -not [IO.Path]::IsPathRooted($p)) {
    $guess = Join-Path (Join-Path $env:SystemRoot 'System32') $p
    if (Test-Path -LiteralPath $guess) { $p = $guess }
  }
  return $p
}

# —— 验明正身：目标还在不在，签名是谁 ——
function Get-SignerInfo([string]$path) {
  $none = @{ signer = $null; sig = $null; exists = $null }
  if (-not $path) { return $none }
  try { if (-not [IO.Path]::IsPathRooted($path)) { return $none } } catch { return $none }
  $key = $path.ToLowerInvariant()
  if ($script:SigCache.ContainsKey($key)) { return $script:SigCache[$key] }
  $info = @{ signer = $null; sig = $null; exists = (Test-Path -LiteralPath $path) }
  if ($info.exists -and (Test-Path -LiteralPath $path -PathType Leaf)) {
    $company = $null
    if ($key.StartsWith($script:WinDir)) {
      # Windows 目录里绝大多数是系统文件，逐个验签名很慢（要查签名目录）。
      # 版本信息写着微软的，先标成"系统文件"跳过验签；其余照常验签名。
      try { $company = [Diagnostics.FileVersionInfo]::GetVersionInfo($path).CompanyName } catch { }
    }
    if ($company -match '^Microsoft') {
      $info.signer = 'Microsoft Corporation'
      $info.sig = 'System'
    } else {
      try {
        $subj = $null
        if ((Get-Item -LiteralPath $path).Length -gt 50MB) {
          # 大文件完整校验要把整个文件算一遍哈希，太慢；只读出签名证书，标成"已签名（未逐字节校验）"
          try {
            $subj = [Security.Cryptography.X509Certificates.X509Certificate]::CreateFromSignedFile($path).Subject
            $info.sig = 'SignedLarge'
          } catch { $info.sig = 'NotSigned' }
        } else {
          $s = Get-AuthenticodeSignature -LiteralPath $path -ErrorAction Stop
          $info.sig = [string]$s.Status
          if ($s.SignerCertificate) { $subj = $s.SignerCertificate.Subject }
        }
        if ($subj -match '(?:^|,\s*)O="?([^",]+)') { $info.signer = $Matches[1].Trim() }
        elseif ($subj -match '(?:^|,\s*)CN="?([^",]+)') { $info.signer = $Matches[1].Trim() }
        if ($subj -match 'Hardware Compatibility Publisher|Hardware Driver Publisher' -and $info.sig -eq 'Valid') {
          # 内核驱动由微软"驱动认证"代签，签名者显示成微软；改用文件自报的厂商名来认亲
          $vendor = $null
          try { $vendor = [Diagnostics.FileVersionInfo]::GetVersionInfo($path).CompanyName } catch { }
          if ($vendor -and $vendor -notmatch '^Microsoft') { $info.signer = $vendor.Trim(); $info.sig = 'WHQL' }
        }
      } catch { $info.sig = 'Unknown' }
    }
  }
  $script:SigCache[$key] = $info
  return $info
}

function New-Record($kind, $name, $location, $command, $extra) {
  $target = Resolve-TargetPath $command
  $si = Get-SignerInfo $target
  [pscustomobject][ordered]@{
    kind = $kind
    name = Hide-Private ([string]$name)
    location = Hide-Private ([string]$location)
    target = Hide-Private $target
    exists = $si.exists
    signer = $si.signer
    sig = $si.sig
    extra = $extra
  }
}

function Get-RootProbeRecords {
  param([scriptblock]$Progress = { param($m) })
  $records = New-Object System.Collections.ArrayList
  $add = { param($r) [void]$records.Add($r) }

  # —— 地层：户口（卸载登记）——
  & $Progress '查户口：卸载登记'
  foreach ($root in 'HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall',
                    'HKLM\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall',
                    'HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall') {
    foreach ($sub in Get-SubKeyNames $root) {
      $p = Get-RegValues "$root\$sub"
      if (-not $p['DisplayName']) { continue }
      $cmd = if ($p['UninstallString']) { $p['UninstallString'] } else { $p['DisplayIcon'] }
      $extra = [ordered]@{ publisher = $p['Publisher']; installLocation = (Hide-Private $p['InstallLocation']); version = $p['DisplayVersion'] }
      & $add (New-Record 'uninstall' $p['DisplayName'] "$root\$sub" $cmd $extra)
    }
  }

  # —— 地层：注册表里的厂商键 ——
  & $Progress '翻账本：注册表里的厂商键'
  foreach ($root in 'HKCU\Software', 'HKLM\SOFTWARE', 'HKLM\SOFTWARE\WOW6432Node') {
    foreach ($sub in Get-SubKeyNames $root) {
      if ($sub -in 'Classes', 'Microsoft', 'Policies', 'WOW6432Node', 'RegisteredApplications', 'Clients') { continue }
      & $add (New-Record 'regkey' $sub "$root\$sub" $null $null)
    }
  }

  # —— 地层：开机自启（Run 键 + 启动文件夹）——
  & $Progress '查开机自启'
  foreach ($root in 'HKCU\Software\Microsoft\Windows\CurrentVersion\Run',
                    'HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run',
                    'HKLM\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Run') {
    $vals = Get-RegValues $root
    foreach ($v in $vals.Keys) {
      if (-not $v) { continue }
      & $add (New-Record 'run' $v $root ([string]$vals[$v]) $null)
    }
  }
  $shell = New-Object -ComObject WScript.Shell
  foreach ($dir in [Environment]::GetFolderPath('Startup'), [Environment]::GetFolderPath('CommonStartup')) {
    if (-not $dir -or -not (Test-Path -LiteralPath $dir)) { continue }
    foreach ($f in Get-ChildItem -LiteralPath $dir -File -ErrorAction SilentlyContinue) {
      if ($f.Name -ieq 'desktop.ini') { continue }
      $t = $f.FullName
      # CreateShortcut 只是读取快捷方式，不调用 Save 就不会写入任何东西
      if ($f.Extension -ieq '.lnk') { try { $t = $shell.CreateShortcut($f.FullName).TargetPath } catch { } }
      & $add (New-Record 'startup' $f.BaseName $dir "`"$t`"" $null)
    }
  }

  # —— 地层：服务；核心：驱动 ——
  & $Progress '查服务和驱动'
  foreach ($s in Get-CimInstance Win32_Service -ErrorAction SilentlyContinue) {
    $cmd = $s.PathName
    if ($cmd -imatch 'svchost\.exe') {
      $dll = Get-RegValue "HKLM\SYSTEM\CurrentControlSet\Services\$($s.Name)\Parameters" 'ServiceDll'
      if ($dll) { $cmd = "`"$dll`"" }
    }
    $extra = [ordered]@{ display = $s.DisplayName; state = $s.State; startMode = $s.StartMode }
    & $add (New-Record 'service' $s.Name 'HKLM\SYSTEM\CurrentControlSet\Services' $cmd $extra)
  }
  foreach ($d in Get-CimInstance Win32_SystemDriver -ErrorAction SilentlyContinue) {
    $extra = [ordered]@{ display = $d.DisplayName; state = $d.State; startMode = $d.StartMode }
    & $add (New-Record 'driver' $d.Name 'HKLM\SYSTEM\CurrentControlSet\Services' $d.PathName $extra)
  }

  # —— 地层：计划任务 ——
  & $Progress '查计划任务'
  foreach ($t in Get-ScheduledTask -ErrorAction SilentlyContinue) {
    $exec = $null
    foreach ($a in $t.Actions) { if ($a.Execute) { $exec = $a.Execute; break } }
    if (-not $exec) { continue }
    if ($exec -notmatch '^"') { $exec = "`"$exec`"" }
    $extra = [ordered]@{ state = [string]$t.State; author = (Hide-Private $t.Author) }
    & $add (New-Record 'task' $t.TaskName ('任务计划程序' + $t.TaskPath) $exec $extra)
  }

  # —— 地表：右键菜单 ——
  & $Progress '查右键菜单'
  foreach ($cls in '*', 'Directory', 'Directory\Background', 'Folder', 'AllFilesystemObjects', 'Drive') {
    foreach ($hive in 'HKCU\Software\Classes', 'HKLM\SOFTWARE\Classes') {
      $base = "$hive\$cls"
      foreach ($verb in Get-SubKeyNames "$base\shell") {
        $cmd = Get-RegValue "$base\shell\$verb\command"
        $label = Get-RegValue "$base\shell\$verb"
        if (-not $label) { $label = Get-RegValue "$base\shell\$verb" 'MUIVerb' }
        $name = if ($label -and $label -notmatch '^@') { "$label（$verb）" } else { $verb }
        & $add (New-Record 'contextmenu' $name "$base\shell\$verb" $cmd $null)
      }
      foreach ($h in Get-SubKeyNames "$base\shellex\ContextMenuHandlers") {
        $clsid = Get-RegValue "$base\shellex\ContextMenuHandlers\$h"
        if (-not $clsid -and $h -match '^\{') { $clsid = $h }
        $dll = if ($clsid) { Get-RegValue "HKCR\CLSID\$clsid\InprocServer32" }
        & $add (New-Record 'contextmenu' $h "$base\shellex\ContextMenuHandlers\$h" $(if ($dll) { "`"$dll`"" }) $null)
      }
    }
  }

  # —— 地表：文件关联（你本人选过的默认打开方式）——
  & $Progress '查文件关联'
  $fileExts = 'HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\FileExts'
  foreach ($ext in Get-SubKeyNames $fileExts) {
    $prog = $null
    foreach ($uc in 'UserChoice', 'UserChoiceLatest') {
      $prog = Get-RegValue "$fileExts\$ext\$uc" 'ProgId'
      if ($prog) { break }
    }
    if (-not $prog) { continue }
    $cmd = Get-RegValue "HKCR\$prog\shell\open\command"
    $extra = [ordered]@{ ext = $ext; progId = $prog }
    & $add (New-Record 'association' "$ext → $prog" "$fileExts\$ext" $cmd $extra)
  }

  # —— 地表：开始菜单和桌面的快捷方式 ——
  & $Progress '查快捷方式'
  foreach ($dir in [Environment]::GetFolderPath('Programs'), [Environment]::GetFolderPath('CommonPrograms'),
                   [Environment]::GetFolderPath('Desktop'), [Environment]::GetFolderPath('CommonDesktopDirectory')) {
    if (-not $dir -or -not (Test-Path -LiteralPath $dir)) { continue }
    foreach ($f in Get-ChildItem -LiteralPath $dir -Filter *.lnk -Recurse -Depth 1 -File -ErrorAction SilentlyContinue) {
      $t = $null
      try { $t = $shell.CreateShortcut($f.FullName).TargetPath } catch { }
      & $add (New-Record 'shortcut' $f.BaseName $f.DirectoryName $(if ($t) { "`"$t`"" }) $null)
    }
  }

  # —— 深层：程序目录和数据目录里的文件夹 ——
  & $Progress '查文件夹'
  $folderRoots = @($env:ProgramFiles, ${env:ProgramFiles(x86)}, $env:ProgramData, $env:APPDATA, $env:LOCALAPPDATA,
    (Join-Path $env:LOCALAPPDATA 'Programs'), (Join-Path (Split-Path $env:LOCALAPPDATA) 'LocalLow')) | Select-Object -Unique
  foreach ($root in $folderRoots) {
    if (-not $root -or -not (Test-Path -LiteralPath $root)) { continue }
    foreach ($d in Get-ChildItem -LiteralPath $root -Directory -Force -ErrorAction SilentlyContinue) {
      if ($d.Attributes -band [IO.FileAttributes]::ReparsePoint) { continue }
      & $add (New-Record 'folder' $d.Name $root $null $null)
    }
  }

  # —— 横切：hosts 文件 ——
  & $Progress '查 hosts'
  $hosts = Join-Path $env:SystemRoot 'System32\drivers\etc\hosts'
  foreach ($line in Get-Content -LiteralPath $hosts -ErrorAction SilentlyContinue) {
    $l = ($line -replace '#.*$', '').Trim()
    if (-not $l) { continue }
    $parts = $l -split '\s+'
    for ($i = 1; $i -lt $parts.Count; $i++) {
      & $add (New-Record 'hosts' $parts[$i] $hosts $null ([ordered]@{ address = $parts[0] }))
    }
  }

  return , $records
}

function Get-GlobalChecks {
  # 和具体软件无关、但每次都值得看一眼的全局状态
  $proxy = Get-RegValues 'HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings'
  $hosts = Join-Path $env:SystemRoot 'System32\drivers\etc\hosts'
  $hostLines = @(Get-Content -LiteralPath $hosts -ErrorAction SilentlyContinue | Where-Object { ($_ -replace '#.*$', '').Trim() })
  [ordered]@{
    hostsEntries = $hostLines.Count
    proxyEnabled = [bool]($proxy['ProxyEnable'] -eq 1)
    proxyServer = if ($proxy['ProxyEnable'] -eq 1) { [string]$proxy['ProxyServer'] } else { $null }
    os = (Get-CimInstance Win32_OperatingSystem -ErrorAction SilentlyContinue).Caption
  }
}
