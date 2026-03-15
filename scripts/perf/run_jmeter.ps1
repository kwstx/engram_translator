param(
    [string]$TargetHost = "localhost",
    [int]$Port = 8000,
    [int]$Threads = 50,
    [int]$RampUp = 30,
    [int]$Duration = 180,
    [string]$Jwt = "",
    [string]$Payloads = "scripts\\perf\\jmeter\\payloads.csv",
    [string]$JmxPath = "scripts\\perf\\jmeter\\translator_load_test.jmx",
    [string]$ResultsDir = "perf_results"
)

$ErrorActionPreference = "Stop"

if (-not (Get-Command jmeter -ErrorAction SilentlyContinue)) {
    throw "JMeter not found on PATH. Install JMeter and ensure 'jmeter' is available."
}

if (-not (Test-Path $JmxPath)) {
    throw "JMX file not found: $JmxPath"
}

if (-not (Test-Path $Payloads)) {
    throw "Payloads file not found: $Payloads"
}

if (-not (Test-Path $ResultsDir)) {
    New-Item -ItemType Directory -Path $ResultsDir | Out-Null
}

$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$jtlPath = Join-Path $ResultsDir "results_$stamp.jtl"
$reportDir = Join-Path $ResultsDir "report_$stamp"

$args = @(
    "-n",
    "-t", $JmxPath,
    "-l", $jtlPath,
    "-e",
    "-o", $reportDir,
    "-Jhost=$TargetHost",
    "-Jport=$Port",
    "-Jthreads=$Threads",
    "-Jramp_up=$RampUp",
    "-Jduration=$Duration",
    "-Jpayloads=$Payloads"
)

if ($Jwt -ne "") {
    $args += "-Jjwt=$Jwt"
}

Write-Host "Running JMeter with:"
Write-Host ($args -join " ")

jmeter @args

Write-Host "JTL: $jtlPath"
Write-Host "Report: $reportDir\\index.html"
