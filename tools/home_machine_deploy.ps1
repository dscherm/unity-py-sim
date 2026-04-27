<#
.SYNOPSIS
  Run a generated Unity project's CoPlay scene setup in batchmode.

.DESCRIPTION
  Wraps Unity.exe with -batchmode -nographics -executeMethod so the
  GitHub Actions workflow on the home machine can deploy a scene
  without manual menu clicks. Returns Unity's own exit code.

  Two-pass usage in CI: this script for setup, then the same Unity
  invocation pattern with -executeMethod HomeMachinePlaytest.Run for
  Play mode validation.

.PARAMETER ProjectPath
  Path to the Unity project (e.g. data/generated/breakout_project).

.PARAMETER UnityPath
  Full path to Unity.exe. Defaults to the highest 6000.x in
  C:\Program Files\Unity\Hub\Editor\.

.PARAMETER Method
  Static method to invoke. Defaults to GeneratedSceneSetup.Execute,
  the standard CoPlay-emitted entry point.

.PARAMETER LogFile
  Where Unity writes its Editor log. Defaults to a temp file; the
  contents are echoed to stdout on completion.

.EXAMPLE
  pwsh tools/home_machine_deploy.ps1 -ProjectPath data/generated/breakout_project
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectPath,

    [string]$UnityPath = "",

    [string]$Method = "GeneratedSceneSetup.Execute",

    [string]$LogFile = "",

    # Set when the executed method drives its own lifetime (e.g. enters Play
    # mode). Unity's `-quit` flag forces an immediate exit after the static
    # method returns, which kills async work like Play mode coroutines
    # before they tick. The method must call EditorApplication.Exit() itself.
    [switch]$NoQuit,

    # Enable Unity's render context. By default we pass `-nographics` for
    # the deploy/setup case (no rendering needed). Play mode validation
    # needs a render target so ScreenCapture produces non-empty PNGs and
    # MonoBehaviour Update ticks at frame cadence — pass -WithGraphics.
    [switch]$WithGraphics
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

if (-not $LogFile) {
    $LogFile = Join-Path $env:TEMP ("unity_deploy_{0}.log" -f ([Guid]::NewGuid().ToString('N')))
}

$absProject = (Resolve-Path $ProjectPath).Path

Write-Host "[deploy] Unity: $UnityPath"
Write-Host "[deploy] Project: $absProject"
Write-Host "[deploy] Method: $Method"
Write-Host "[deploy] Log: $LogFile"

$unityArgs = @("-batchmode")
if (-not $WithGraphics) {
    $unityArgs += "-nographics"
}
$unityArgs += @(
    "-projectPath", $absProject
    "-executeMethod", $Method
    # Skip Unity's API Updater. It migrates assembly references between
    # Unity versions; our generated projects already target the runner's
    # exact Editor version (6000.4.0f1), so the updater is dead weight
    # — and on the home-machine runner it was timing out at 30s right
    # before the cold-start shader compiler OOM
    # (`Crash_2026-04-26_153847992`, run 24960280211).  Removing the
    # updater frees both the wallclock and the working set it holds
    # while shaders compile in parallel.
    "-disable-assembly-updater"
    # `-logFile -` makes Unity stream the log to stdout, so we tee it
    # into both the console (visible in CI) and a file artifact.
    "-logFile", "-"
)
if (-not $NoQuit) {
    $unityArgs += "-quit"
}

Write-Host "----- Unity log -----"
# Don't use 2>&1: PowerShell 5.1 wraps native stderr in ErrorRecord and,
# combined with ErrorActionPreference=Stop, aborts the script even on a
# zero-exit Unity run. With `-logFile -` Unity writes everything we care
# about to stdout; stderr only has cosmetic shutdown warnings.
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

Write-Host "[deploy] exit code: $exit"
Write-Host "[deploy] log saved: $LogFile"
exit $exit
