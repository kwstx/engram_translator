param(
    [int]$Pid = 0,
    [string]$ProcessName = "python",
    [int]$IntervalSec = 1,
    [int]$DurationSec = 300,
    [string]$OutFile = "perf_results\\resource_metrics.csv"
)

$ErrorActionPreference = "Stop"

if ($Pid -eq 0) {
    $proc = Get-Process -Name $ProcessName | Sort-Object CPU -Descending | Select-Object -First 1
    if (-not $proc) {
        throw "Process not found: $ProcessName"
    }
    $Pid = $proc.Id
}

if (-not (Test-Path (Split-Path $OutFile))) {
    New-Item -ItemType Directory -Path (Split-Path $OutFile) | Out-Null
}

$cpuCount = [Environment]::ProcessorCount
$start = Get-Date
$end = $start.AddSeconds($DurationSec)

$prev = Get-Process -Id $Pid
$prevCpu = $prev.CPU
$prevTime = Get-Date

"timestamp,cpu_percent,working_set_mb,private_bytes_mb,threads" | Out-File -FilePath $OutFile -Encoding ascii

while ((Get-Date) -lt $end) {
    Start-Sleep -Seconds $IntervalSec
    try {
        $proc = Get-Process -Id $Pid -ErrorAction Stop
    } catch {
        throw "Process $Pid exited."
    }

    $now = Get-Date
    $cpuDelta = $proc.CPU - $prevCpu
    $timeDelta = ($now - $prevTime).TotalSeconds
    $cpuPct = 0.0
    if ($timeDelta -gt 0) {
        $cpuPct = [Math]::Round(($cpuDelta / $timeDelta) * 100 / $cpuCount, 2)
    }
    $wsMb = [Math]::Round($proc.WorkingSet64 / 1MB, 2)
    $privMb = [Math]::Round($proc.PrivateMemorySize64 / 1MB, 2)
    $threads = $proc.Threads.Count

    $line = "{0},{1},{2},{3},{4}" -f $now.ToString("o"), $cpuPct, $wsMb, $privMb, $threads
    Add-Content -Path $OutFile -Value $line

    $prevCpu = $proc.CPU
    $prevTime = $now
}

Write-Host "Wrote metrics to $OutFile"
