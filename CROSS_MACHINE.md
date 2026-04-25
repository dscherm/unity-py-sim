# CROSS_MACHINE.md — home-machine GitHub Actions runner

This doc covers everything needed to bring the home Windows machine
online as a self-hosted GitHub Actions runner so the Unity playtest
workflow (`.github/workflows/home_machine.yml`) runs automatically on
every push to `main`. M-7 of `SUCCESS.md` lives here.

## Prerequisites

On the home machine:

- Windows 10/11 with admin access.
- Unity 6 (`6000.x`) installed via Unity Hub. Verify by running
  `& "C:\Program Files\Unity\Hub\Editor\6000.x.x\Editor\Unity.exe" -version`.
- Unity license activated for batchmode use (see "License activation"
  below — a Personal license works).
- CoPlay package available in the Unity project's `Packages/` (already
  vendored under `data/generated/<game>_project/Packages/Coplay/`).
- PowerShell 7+ (`pwsh`). Windows PowerShell 5.1 also works but the
  workflow uses `pwsh` shell tags.
- Git, Python 3.11+, `gh` CLI, and `dotnet` SDK 8+.
- Local clone of `unity-py-sim` (the runner work-folder is separate;
  the runner clones automatically per job).

## License activation (one-time)

Unity refuses to launch in `-batchmode` without an activated license.
For a Personal license:

```powershell
$ULF = "$HOME\Unity_lic.ulf"  # downloaded from id.unity.com after manual activation
& "C:\Program Files\Unity\Hub\Editor\6000.x.x\Editor\Unity.exe" `
  -batchmode -nographics -manualLicenseFile $ULF -logFile - -quit
```

Pro/Plus floating licenses use `-serial`, `-username`, `-password`.
Store those as repo secrets (`UNITY_SERIAL`, `UNITY_USERNAME`,
`UNITY_PASSWORD`) and add an `Activate Unity` step to the workflow if
your account requires per-machine reactivation; the current workflow
assumes the license is already activated and persists between runs.

## Runner registration

1. In GitHub: **Settings → Actions → Runners → New self-hosted runner**.
   Choose **Windows**, **x64**.
2. GitHub shows a one-time `--token` value. Note it.
3. On the home machine, in PowerShell **as a regular user** (not admin):
   ```powershell
   $runnerRoot = "C:\actions-runner"
   New-Item -ItemType Directory -Force $runnerRoot | Out-Null
   Set-Location $runnerRoot
   # Use the download URL GitHub printed (version may have moved)
   Invoke-WebRequest -Uri https://github.com/actions/runner/releases/download/v2.319.1/actions-runner-win-x64-2.319.1.zip `
     -OutFile actions-runner.zip
   Expand-Archive -Path actions-runner.zip -DestinationPath . -Force
   .\config.cmd `
     --url https://github.com/dscherm/unity-py-sim `
     --token <PASTE_TOKEN> `
     --name home-unity `
     --labels self-hosted,Windows,unity `
     --work _work
   ```
4. Install as a Windows service so the runner survives reboots:
   ```powershell
   .\svc.cmd install
   .\svc.cmd start
   ```
5. Verify the runner appears as **Idle** under **Settings → Actions →
   Runners** in the repo.

## Smoke test

Trigger the workflow manually before relying on push triggers:

```powershell
gh workflow run home_machine.yml --ref main
gh run watch
```

Expected: `breakout` and `flappy_bird` jobs each take ~10–15 min.
Artifacts (`<game>-playtest-<run_id>.zip`) contain `frame_*.png`
screenshots + `summary.json`. Check **Actions** in the repo UI.

## Failure modes and fixes

| Symptom | Likely cause | Fix |
|---|---|---|
| `Unity.exe not found at ...` | Hub install path differs | Pass `-UnityPath` to `home_machine_deploy.ps1`; or symlink to the expected path |
| `LICENSE SYSTEM` errors in Editor.log | License inactive or expired | Re-run manual activation; check the runner user has access to `%LocalAppData%\Unity\Unity_lic.ulf` |
| Workflow hangs at "Play mode validation" | Unity entered Play mode but never exited | Inspect `Editor.log` artifact; usually a NullRef in a MonoBehaviour Awake — check the game's generated scripts |
| `summary.json not produced` | Play mode never entered (compile errors) | Look at the deploy step's log — most likely a C# syntax error from the translator |
| Runner shows as Offline after reboot | Service didn't auto-start | `cd C:\actions-runner; .\svc.cmd status` then `.\svc.cmd start` |

## Verifying the failure path

Before declaring M-7 done, prove a deliberate regression turns the
home-machine check red:

1. On a feature branch, hand-edit a generated `.cs` file to introduce
   a NullRef (e.g., `transform = null;` in `Awake()`).
2. Push, open a PR.
3. Confirm the **Home Machine** check fails with the exception in the
   uploaded log.
4. Revert the diff and confirm green.

## Secrets and security notes

- The runner clones the public repo; no secrets needed for that.
- Unity license info, if managed via secrets, must be marked as
  repository secrets — never commit `Unity_lic.ulf`.
- The runner runs jobs as the user it was registered under; do **not**
  run it as `Administrator` unless a specific job requires it.
- Pause the runner before manual machine maintenance:
  `cd C:\actions-runner; .\svc.cmd stop`.

## Capacity

The runner serves only this repository. For a parallel matrix the
runner becomes the bottleneck — the current workflow runs games
sequentially per push (matrix entries serialize on a single runner).
Adding a second runner with the same labels gives parallelism without
config changes.
