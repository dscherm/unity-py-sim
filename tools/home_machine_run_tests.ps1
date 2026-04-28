<#
.SYNOPSIS
  Run Unity Test Framework's PlayMode tests in batchmode and emit JUnit XML.

.DESCRIPTION
  Wraps Unity.exe with -runTests -testPlatform PlayMode so the home_machine
  GitHub Actions workflow can fail-red on Awake/Start/Update NullRefs that
  the deploy-only batchmode harness silently misses.

  Differs from home_machine_deploy.ps1 in two ways:
    - Drives via -runTests (Unity manages its own lifetime; no -quit).
    - Renders by default — PlayMode tests need a swapchain to tick frames.
      Pass -NoGraphics to override on tests that don't touch rendering.

  Returns Unity's own exit code (0 = all tests passed; non-zero = failure
  or test run abort). The test framework also writes a JUnit-style XML at
  -ResultsFile that the workflow uploads as an artifact.

.PARAMETER ProjectPath
  Path to the Unity project (e.g. data/generated/breakout_project).

.PARAMETER UnityPath
  Full path to Unity.exe. Defaults to the highest 6000.x in
  C:\Program Files\Unity\Hub\Editor\.

.PARAMETER ResultsFile
  Path where Unity writes the JUnit XML test results. Defaults to
  <ProjectPath>/test_results.xml.

.PARAMETER LogFile
  Where Unity writes its Editor log. Defaults to a temp file; the contents
  are tee'd to stdout on completion so CI log capture is preserved.

.PARAMETER NoGraphics
  Pass -nographics to Unity. Off by default — PlayMode test ticking is
  more reliable with a render target.

.EXAMPLE
  pwsh tools/home_machine_run_tests.ps1 -ProjectPath data/generated/breakout_project -ResultsFile breakout_tests.xml
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectPath,

    [string]$UnityPath = "",

    [string]$ResultsFile = "",

    [string]$LogFile = "",

    [switch]$NoGraphics
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $ProjectPath)) {
    Write-Error "ProjectPath '$ProjectPath' not found"
    exit 2
}

if (-not $UnityPath) {
    $hubRoot = "C:\Program Files\Unity\Hub\Editor"
    if (-not (Test-Path $hubRoot)) {
        Write-Error "UnityPath not provided and $hubRoot does not exist."
        exit 2
    }
    $candidate = Get-ChildItem $hubRoot -Directory |
        Where-Object { $_.Name -match '^6\d{3}\.' } |
        Sort-Object Name -Descending |
        Select-Object -First 1
    if (-not $candidate) {
        Write-Error "No Unity 6000.x install found under $hubRoot"
        exit 2
    }
    $UnityPath = Join-Path $candidate.FullName "Editor\Unity.exe"
}

if (-not (Test-Path $UnityPath)) {
    Write-Error "Unity.exe not found at '$UnityPath'"
    exit 2
}

$absProject = (Resolve-Path $ProjectPath).Path

if (-not $ResultsFile) {
    $ResultsFile = Join-Path $absProject "test_results.xml"
}
# Make ResultsFile absolute so Unity (cwd-agnostic) writes to the expected spot.
$resultsDir = Split-Path -Parent $ResultsFile
if ($resultsDir -and -not (Test-Path $resultsDir)) {
    New-Item -ItemType Directory -Force -Path $resultsDir | Out-Null
}

if (-not $LogFile) {
    $LogFile = Join-Path $env:TEMP ("unity_runtests_{0}.log" -f ([Guid]::NewGuid().ToString('N')))
}

Write-Host "[run-tests] Unity: $UnityPath"
Write-Host "[run-tests] Project: $absProject"
Write-Host "[run-tests] Platform: PlayMode"
Write-Host "[run-tests] Results: $ResultsFile"
Write-Host "[run-tests] Log: $LogFile"

$unityArgs = @("-batchmode")
if ($NoGraphics) {
    $unityArgs += "-nographics"
}
$unityArgs += @(
    "-projectPath", $absProject
    "-runTests"
    "-testPlatform", "PlayMode"
    "-testResults", $ResultsFile
    # Match home_machine_deploy.ps1: skip the API Updater.  Generated
    # projects already target the runner's exact Editor version, so it
    # has no migrations to run — and the timeout-then-shader-OOM chain
    # observed during deploy applies equally to the test invocation.
    "-disable-assembly-updater"
    "-logFile", "-"
)

Write-Host "----- Unity log -----"
# Same stderr-redirection caveat as home_machine_deploy.ps1 — don't use
# 2>&1 (PS5.1 wraps native stderr in ErrorRecord and trips Stop-on-error).
$prevPref = $ErrorActionPreference
$ErrorActionPreference = "Continue"
try {
    & $UnityPath @unityArgs | Tee-Object -FilePath $LogFile
} finally {
    $ErrorActionPreference = $prevPref
}
$exit = $LASTEXITCODE
if ($null -eq $exit) { $exit = 0 }
Write-Host "----- /Unity log -----"

Write-Host "[run-tests] exit code: $exit"
Write-Host "[run-tests] results: $ResultsFile"
Write-Host "[run-tests] log saved: $LogFile"
exit $exit
