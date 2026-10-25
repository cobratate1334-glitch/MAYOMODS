# Mayo Mods - BlueStacks 5 crash log collector (Windows PowerShell 5.1+)
# Collects locally through Android Debug Bridge (ADB). No upload or administrator rights.
$ErrorActionPreference = 'Stop'
$Package = 'com.candywriter.bitlife'
$Base = Split-Path -Parent $MyInvocation.MyCommand.Path
$ReportRoot = Join-Path $Base 'Reports'
New-Item -ItemType Directory -Force -Path $ReportRoot | Out-Null
$Tag = Get-Date -Format 'yyyyMMdd-HHmmss'
$ReportDir = Join-Path $ReportRoot "MayoMods_BlueStacks_$Tag"
New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null
$LogFile = Join-Path $ReportDir 'android_full_logcat_PRIVATE.txt'
$ErrorFile = Join-Path $ReportDir 'adb_recording_errors.txt'
$SummaryFile = Join-Path $ReportDir 'crash_summary.txt'
$InfoFile = Join-Path $ReportDir 'device_and_app_info.txt'
$RecentFile = Join-Path $ReportDir 'recent_logcat_before_recording.txt'
$FilteredFile = Join-Path $ReportDir 'relevant_game_crash_lines.txt'

function Find-Adb {
    $candidates = @(
        (Join-Path ${env:ProgramFiles} 'BlueStacks_nxt\HD-Adb.exe'),
        (Join-Path ${env:ProgramFiles} 'BlueStacks_nxt\adb.exe'),
        (Join-Path ${env:ProgramFiles(x86)} 'BlueStacks_nxt\HD-Adb.exe'),
        (Join-Path ${env:ProgramFiles(x86)} 'BlueStacks_nxt\adb.exe'),
        (Join-Path $env:LOCALAPPDATA 'Android\Sdk\platform-tools\adb.exe')
    )
    foreach ($candidate in $candidates) {
        if ($candidate -and (Test-Path -LiteralPath $candidate -PathType Leaf)) { return $candidate }
    }
    $pathCmd = Get-Command adb.exe -ErrorAction SilentlyContinue
    if ($pathCmd) { return $pathCmd.Source }
    return $null
}

function Lines($header, $lines) {
    Add-Content -LiteralPath $InfoFile -Encoding UTF8 -Value "`r`n--- $header ---"
    if ($null -eq $lines) { return }
    foreach ($line in @($lines)) { Add-Content -LiteralPath $InfoFile -Encoding UTF8 -Value "$line" }
}

function Safe-Adb($adbPath, $device, [string[]]$argv) {
    try { return (& $adbPath -s $device @argv 2>&1 | Out-String).Trim() }
    catch { return "Unavailable: $($_.Exception.Message)" }
}

Write-Host ''
Write-Host 'MAYO MODS - BLUESTACKS CRASH LOGGER' -ForegroundColor Cyan
Write-Host 'Runs on your PC. No files are sent anywhere.'
Write-Host 'First: BlueStacks 5 > Settings > Advanced > Android Debug Bridge > ON.'
Write-Host ''

$adb = Find-Adb
if (-not $adb) {
    Write-Host 'Could not find Android ADB (HD-Adb.exe or adb.exe).' -ForegroundColor Red
    Write-Host 'Install BlueStacks 5 or Android SDK Platform-Tools, then run again.'
    exit 1
}
Write-Host "Using ADB: $adb"
$port = Read-Host 'ADB port shown in BlueStacks Advanced settings (Enter = 5555)'
if ([string]::IsNullOrWhiteSpace($port)) { $port = '5555' }
$number = 0
if (-not [int]::TryParse($port, [ref]$number) -or $number -lt 1 -or $number -gt 65535) {
    Write-Host 'Invalid port. Use the number shown by BlueStacks.' -ForegroundColor Red
    exit 1
}
$serial = "127.0.0.1:$number"
Write-Host "Connecting to $serial ..."
$connect = (& $adb connect $serial 2>&1 | Out-String).Trim()
Write-Host $connect
$state = (Safe-Adb $adb $serial @('get-state'))
if ($state -ne 'device') {
    Write-Host 'Could not connect. Confirm the right BlueStacks instance is running, ADB is enabled, and the port matches.' -ForegroundColor Red
    & $adb devices
    exit 1
}

Set-Content -LiteralPath $InfoFile -Encoding UTF8 -Value "MayoMods / BlueStacks PC crash diagnostics`r`nCaptured: $(Get-Date -Format o)`r`nADB serial: $serial`r`nPackage: $Package`r`nADB executable: $adb"
Lines 'Android version' (Safe-Adb $adb $serial @('shell','getprop','ro.build.version.release'))
Lines 'Android API' (Safe-Adb $adb $serial @('shell','getprop','ro.build.version.sdk'))
Lines 'Product model' (Safe-Adb $adb $serial @('shell','getprop','ro.product.model'))
Lines 'Manufacturer' (Safe-Adb $adb $serial @('shell','getprop','ro.product.manufacturer'))
Lines 'CPU ABIs supported by emulator' (Safe-Adb $adb $serial @('shell','getprop','ro.product.cpu.abilist'))
Lines 'Native bridge (if provided)' (Safe-Adb $adb $serial @('shell','getprop','ro.dalvik.vm.native.bridge'))
Lines 'OpenGL version' (Safe-Adb $adb $serial @('shell','getprop','ro.opengles.version'))
Lines 'App path' (Safe-Adb $adb $serial @('shell','pm','path',$Package))
$details = Safe-Adb $adb $serial @('shell','dumpsys','package',$Package)
$appVersionLines = $details -split "`n" | Where-Object { $_ -match 'versionCode=|versionName=|primaryCpuAbi=|secondaryCpuAbi=|targetSdk=' } | Select-Object -First 12
Lines 'App version / ABIs' $appVersionLines

Write-Host ''
Write-Host 'Collecting a snapshot of recent Android logs...'
try { & $adb -s $serial logcat -d -v threadtime -b main -b system -b crash 2>&1 | Out-File -LiteralPath $RecentFile -Encoding utf8 -Width 600 }
catch { "Could not collect snapshot: $($_.Exception.Message)" | Out-File -LiteralPath $RecentFile -Encoding utf8 }

Write-Host 'LIVE RECORDING STARTED' -ForegroundColor Green
Write-Host 'Now open Mayo Mods on BlueStacks and reproduce the crash.'
Write-Host 'Once the game crashes (or fails to load), come back here and press ENTER.'
$process = $null
try {
    $arguments = @('-s', $serial, 'logcat', '-v', 'threadtime', '-b', 'main', '-b', 'system', '-b', 'crash')
    $process = Start-Process -FilePath $adb -ArgumentList $arguments -PassThru -WindowStyle Hidden -RedirectStandardOutput $LogFile -RedirectStandardError $ErrorFile
    [void](Read-Host 'Press ENTER to stop and package the crash report')
} finally {
    if ($process -and -not $process.HasExited) {
        try { Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue } catch { }
    }
}
Start-Sleep -Milliseconds 350

$pattern = '(?i)com\.candywriter\.bitlife|MayoMods|RocketGames|libil2cpp|libunity|UnsatisfiedLinkError|dlopen failed|Fatal signal|SIGSEGV|SIGABRT|backtrace:|tombstone|AndroidRuntime|FATAL EXCEPTION|EGL_BAD_MATCH|libEGL|EGL_emulation|Unity|crash_dump|linker|ActivityManager.*bitlife|ActivityTaskManager.*bitlife'
$interesting = New-Object System.Collections.Generic.List[string]
foreach ($file in @($RecentFile, $LogFile)) {
    if (-not (Test-Path $file)) { continue }
    try {
        $fileLines = Get-Content -LiteralPath $file -ErrorAction Stop
        for ($i=0; $i -lt $fileLines.Count; $i++) {
            if ($fileLines[$i] -match $pattern) {
                # Keep two lines before and six lines after each match for stack-trace context.
                $lo = [Math]::Max(0, $i - 2)
                $hi = [Math]::Min($fileLines.Count - 1, $i + 6)
                for ($j=$lo; $j -le $hi; $j++) {
                    if ($interesting.Count -ge 6000) { break }
                    $interesting.Add($fileLines[$j])
                }
                if ($interesting.Count -ge 6000) { break }
                $i = $hi
            }
        }
    } catch {
        $interesting.Add("Unable to read ${file}: $($_.Exception.Message)")
    }
}
if ($interesting.Count -eq 0) { $interesting.Add('No matching log lines. Full local logs may still contain clues.') }
$interesting | Set-Content -LiteralPath $FilteredFile -Encoding UTF8
$summary = @(
 'MAYO MODS - BLUESTACKS CRASH REPORT',
 "Captured: $(Get-Date -Format o)",
 "ADB instance: $serial",
 "Game package: $Package",
 '',
 'Helpful clues (not a verified diagnosis):'
)
$scan = ($interesting -join "`n")
foreach ($item in @(
 @('ARM / native loader issue', '(?i)UnsatisfiedLinkError|dlopen failed|wrong ELF class|cannot locate symbol'),
 @('Native game crash', '(?i)Fatal signal|SIGSEGV|SIGABRT|crash_dump'),
 @('Java / Android exception', '(?i)FATAL EXCEPTION|AndroidRuntime'),
 @('Graphics or GPU related error', '(?i)EGL_BAD_MATCH|libEGL|OpenGL ES API')
)) {
    if ($scan -match $item[1]) { $summary += "- POSSIBLE: $($item[0])" }
}
if ($summary.Count -eq 6) { $summary += '- No automatic error category matched.' }
$summary += @(
 '',
 'Shareable ZIP contains:',
 '  device_and_app_info.txt, relevant_game_crash_lines.txt, crash_summary.txt',
 '',
 'The FULL Android logs stay in the Reports folder and are NOT included in the ZIP.',
 'Before sharing any file, check it for account names, messages or other personal data.',
 'This tool does not change the APK or solve emulator compatibility by itself.'
)
$summary | Set-Content -LiteralPath $SummaryFile -Encoding UTF8
$zip = Join-Path $ReportRoot "MayoMods_BlueStacks_Report_$Tag.zip"
Compress-Archive -LiteralPath $SummaryFile,$InfoFile,$FilteredFile -DestinationPath $zip -Force
Write-Host ''
Write-Host "Finished. Shareable report: $zip" -ForegroundColor Green
Write-Host "Full local logs: $ReportDir"
Write-Host 'Share the ZIP with the Mayo Mods developer after reviewing it for personal info.'
Write-Host 'The report is NOT uploaded automatically.'
