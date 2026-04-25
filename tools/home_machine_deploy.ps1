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

    [string]$LogFile = ""
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

$unityArgs = @(
    "-batchmode"
    "-nographics"
    "-projectPath", $absProject
    "-executeMethod", $Method
    # `-logFile -` makes Unity stream the log to stdout, so we tee it
    # into both the console (visible in CI) and a file artifact.
    "-logFile", "-"
    "-quit"
)

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
