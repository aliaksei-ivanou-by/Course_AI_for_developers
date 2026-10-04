# Phase 1 (supplement): run Catch2's full all-tests suite on the unmodified
# v3.16.0 baseline, following the snippet in Catch2 docs/contributing.md.
#
# Run from the Implementation directory, after phase1-baseline.ps1:
#   powershell -ExecutionPolicy Bypass -File .\scripts\phase1-all-tests.ps1
#
# Steps:
#   1. Verify the pinned clone (origin, commit, tag, branch, clean tree).
#   2. python tools/scripts/generateAmalgamatedFiles.py, then check that the only
#      change is the "Generated:" timestamp line in extras/catch_amalgamated.*.
#   3. Configure with the all-tests preset into C:\build\Course_AI\catch2\debug-build.
#   4. Build (Debug) and run CTest with -j 4.
#
# Step 2 leaves extras/catch_amalgamated.hpp and .cpp modified. The script does
# not undo that; the summary prints the restore command for the human to run
# after reviewing the diff. The script never deletes files and never runs
# destructive Git commands.

$ErrorActionPreference = 'Continue'
$expectedTag = 'v3.16.0'
$expectedSha = '317ac1ed4c0bb6e6b91eafc817e05c488feffcb3'
$expectedRemote = 'https://github.com/catchorg/Catch2.git'
$branch = 'task/retry-failed'
$buildRoot = 'C:\build\Course_AI\catch2'
$buildDir = Join-Path $buildRoot 'debug-build'
$amalgamated = @('extras/catch_amalgamated.hpp', 'extras/catch_amalgamated.cpp')

$implDir = (Get-Location).Path
$repo = Join-Path $implDir 'workspace\Catch2'
$baselines = Join-Path $repo 'tests\SelfTest\Baselines'
# Evidence folders are numbered run-01, run-02, ... in the order of execution,
# shared with phase1-baseline.ps1; this script adds the suffix -all-tests.
$evidence = Join-Path $implDir 'evidence\raw\phase1'
New-Item -ItemType Directory -Force -Path $evidence | Out-Null
$last = Get-ChildItem -Path $evidence -Directory |
    ForEach-Object { if ($_.Name -match '^run-(\d+)') { [int]$Matches[1] } } |
    Measure-Object -Maximum
$runName = 'run-{0:D2}-all-tests' -f $(if ($last.Count -gt 0) { [int]$last.Maximum + 1 } else { 1 })
$raw = Join-Path $evidence $runName
New-Item -ItemType Directory -Path $raw | Out-Null
$summary = Join-Path $raw 'summary.txt'
$test = $null

function Add-Summary([string]$text) { Add-Content -Path $summary -Value $text -Encoding UTF8 }

function Convert-Line($line) {
    if ($line -is [System.Management.Automation.ErrorRecord]) { return $line.Exception.Message }
    return "$line"
}

function Invoke-Step([string]$name, [string]$command) {
    $log = Join-Path $raw ("{0}.log" -f $name)
    Add-Summary ""
    Add-Summary "== $name"
    Add-Summary "cwd: $((Get-Location).Path)"
    Add-Summary "> $command"
    $timer = [Diagnostics.Stopwatch]::StartNew()
    $writer = New-Object System.IO.StreamWriter($log, $false, (New-Object System.Text.UTF8Encoding($false)))
    try {
        $global:LASTEXITCODE = 0
        Invoke-Expression "$command 2>&1" | ForEach-Object {
            $text = Convert-Line $_
            $writer.WriteLine($text)
            $text
        } | Out-Host
        $code = $LASTEXITCODE
    }
    finally { $writer.Close() }
    Add-Summary ("exit: {0}   seconds: {1}   log: {2}" -f $code, [int]$timer.Elapsed.TotalSeconds, $log)
    return $code
}

function Get-Output([string]$command) {
    $global:LASTEXITCODE = 0
    # Keep leading spaces: they are significant in `git status --short` output.
    return (((Invoke-Expression "$command 2>&1" | ForEach-Object { Convert-Line $_ }) -join "`n") -replace '^[\r\n]+', '').TrimEnd()
}

function Get-Unapproved {
    if (-not (Test-Path $baselines)) { return @() }
    return @(Get-ChildItem -Path $baselines -Filter '*.unapproved.txt' -File | ForEach-Object { $_.Name })
}

function Stop-Run([string]$reason) {
    if ((Get-Location).Path -ne $implDir) { Set-Location $implDir }
    Add-Summary ""
    Add-Summary "STOPPED: $reason"
    Write-Host "STOPPED: $reason" -ForegroundColor Red
    Write-Host "Summary: $summary"
    exit 1
}

Set-Content -Path $summary -Value "Phase 1 all-tests baseline, $runName" -Encoding UTF8

if (-not (Test-Path (Join-Path $implDir 'artifacts\00-task-contract.md'))) {
    Stop-Run "Run this script from the Implementation directory."
}
if (-not (Test-Path $repo)) { Stop-Run "workspace\Catch2 does not exist; run phase1-baseline.ps1 first." }

# --- Environment -------------------------------------------------------------
Add-Summary ""
Add-Summary "== environment"
Add-Summary ("os: {0} ({1})" -f (Get-CimInstance Win32_OperatingSystem).Caption, [Environment]::OSVersion.VersionString)
Add-Summary ("powershell: {0}" -f $PSVersionTable.PSVersion)
foreach ($tool in @('git --version', 'cmake --version', 'ctest --version', 'python --version')) {
    Add-Summary ("{0}: {1}" -f $tool, ((Get-Output $tool) -split "`n")[0])
}
Add-Summary ("build dir: {0} ({1} chars)" -f $buildDir, $buildDir.Length)

# --- Repository state --------------------------------------------------------
Add-Summary ""
Add-Summary "== repository state"
$remote = Get-Output 'git -C workspace/Catch2 remote get-url origin'
$sha = Get-Output 'git -C workspace/Catch2 rev-parse HEAD'
$tag = Get-Output 'git -C workspace/Catch2 describe --exact-match --tags HEAD'
$current = Get-Output 'git -C workspace/Catch2 branch --show-current'
$status = Get-Output 'git -C workspace/Catch2 status --short'
Add-Summary "remote: $remote"
Add-Summary "commit: $sha"
Add-Summary "tag: $tag"
Add-Summary "branch: $current"
Add-Summary ("status --short: {0}" -f $(if ($status) { $status } else { '<clean>' }))
if ($remote -ne $expectedRemote) { Stop-Run "origin is '$remote', expected $expectedRemote" }
if ($sha -ne $expectedSha) { Stop-Run "HEAD is $sha, expected $expectedSha ($expectedTag)" }
if ($tag -ne $expectedTag) { Stop-Run "HEAD is not exactly $expectedTag" }
if ($current -ne $branch) { Stop-Run "current branch is '$current', expected '$branch'" }
if ($status) {
    Stop-Run ("the working tree is not clean. If only the amalgamated files changed (for example from an " +
              "earlier run of this script), review and restore them: git -C workspace/Catch2 restore " + ($amalgamated -join ' '))
}

if (Test-Path $buildDir) {
    Stop-Run ("$buildDir already exists. It contains only build output. " +
              "Remove it manually and rerun: Remove-Item -Recurse -Force '$buildDir'")
}
$stale = Get-Unapproved
if ($stale.Count -gt 0) {
    Stop-Run ("stale approval output in tests\SelfTest\Baselines ($($stale -join ', ')). " +
              "Remove it manually and rerun: Get-ChildItem '$baselines' -Filter *.unapproved.txt | Remove-Item")
}
New-Item -ItemType Directory -Force -Path $buildRoot | Out-Null

Set-Location $repo
try {
    # --- 1. Regenerate the amalgamated distribution ---------------------------
    $gen = Invoke-Step 'amalgamate' 'python tools/scripts/generateAmalgamatedFiles.py'
    if ($gen -ne 0) { Stop-Run "generateAmalgamatedFiles.py failed" }

    $changed = Get-Output 'git status --short'
    $numstat = Get-Output 'git diff --numstat'
    Add-Summary ""
    Add-Summary "== amalgamation check"
    Add-Summary "status --short:"
    Add-Summary $(if ($changed) { $changed } else { '<clean>' })
    Add-Summary "diff --numstat:"
    Add-Summary $(if ($numstat) { $numstat } else { '<none>' })
    # Changed lines other than the generation timestamp.
    $diffLines = (Get-Output 'git diff -U0 --no-color') -split "`n" |
        Where-Object { $_ -match '^[+-]' -and $_ -notmatch '^(\+\+\+|---) ' }
    $unexpected = @($diffLines | Where-Object { $_ -notmatch '^[+-]//  Generated: ' })
    # Git may print "warning: ... LF will be replaced by CRLF" on stderr; skip it.
    $changedFiles = @((Get-Output 'git diff --name-only') -split "`n" | Where-Object { $_ -and $_ -notmatch '^warning: ' })
    $otherFiles = @($changedFiles | Where-Object { $amalgamated -notcontains $_ })
    Add-Summary ("changed lines other than 'Generated:': {0}" -f $unexpected.Count)
    $unexpected | Select-Object -First 20 | ForEach-Object { Add-Summary "  $_" }
    Add-Summary ("changed files other than the amalgamated pair: {0}" -f $(if ($otherFiles.Count) { $otherFiles -join ', ' } else { '<none>' }))
    if ($unexpected.Count -gt 0 -or $otherFiles.Count -gt 0) {
        Write-Host "WARNING: regeneration changed more than the timestamp; record it as a baseline finding." -ForegroundColor Yellow
    }

    # --- 2-4. Configure, build, test -----------------------------------------
    # Commands from the docs/contributing.md all-tests snippet, with a different
    # -B path, plus --config Debug (multi-config generator) and --parallel.
    $configure = Invoke-Step 'configure' "cmake -B '$buildDir' -S . -DCMAKE_BUILD_TYPE=Debug --preset all-tests"
    Add-Summary ""
    Add-Summary "== toolchain (from configure log)"
    Select-String -Path (Join-Path $raw 'configure.log') -Pattern 'compiler identification', 'Building for', 'Windows SDK', 'Found Python3' |
        ForEach-Object { Add-Summary $_.Line.Trim() }
    if ($configure -ne 0) { Stop-Run "configure failed (record it as a baseline issue; do not fix it)" }

    $build = Invoke-Step 'build' "cmake --build '$buildDir' --config Debug --parallel"
    if ($build -ne 0) {
        Add-Summary ""
        Add-Summary "== build errors (first 40)"
        Select-String -Path (Join-Path $raw 'build.log') -Pattern ' error ', 'FTK1011', ': fatal error' |
            Select-Object -First 40 | ForEach-Object { Add-Summary $_.Line.Trim() }
        Stop-Run "build failed (record it as a baseline issue; do not fix it)"
    }
    Add-Summary ("build warnings: {0}" -f @(Select-String -Path (Join-Path $raw 'build.log') -Pattern 'warning').Count)

    $test = Invoke-Step 'ctest' "ctest -j 4 --output-on-failure -C Debug --test-dir '$buildDir'"
    Add-Summary ""
    Add-Summary "== ctest totals"
    Select-String -Path (Join-Path $raw 'ctest.log') -Pattern '^\d+% tests passed', '^Total Test time', '^The following tests', '^\s+\d+ - .+\(.+\)\s*$' |
        ForEach-Object { Add-Summary $_.Line.Trim() }
    Add-Summary "label summary:"
    $inLabels = $false
    Get-Content (Join-Path $raw 'ctest.log') | ForEach-Object {
        if ($_ -match '^Label Time Summary') { $inLabels = $true; return }
        if ($inLabels) { if ($_ -match '^\s*$') { $inLabels = $false } else { Add-Summary "  $($_.Trim())" } }
    }

    $unapproved = Get-Unapproved
    Add-Summary ""
    Add-Summary "== approval differences (tests\SelfTest\Baselines\*.unapproved.txt)"
    Add-Summary ("result: {0}" -f $(if ($unapproved.Count -gt 0) { $unapproved -join ', ' } else { '<none>' }))

    $after = Get-Output 'git status --short'
    Add-Summary ""
    Add-Summary "== status --short after build (expected: only the amalgamated pair)"
    Add-Summary ("result: {0}" -f $(if ($after) { $after } else { '<clean>' }))
}
finally {
    Set-Location $implDir
}

Add-Summary ""
Add-Summary ("FINISHED: ctest exit {0}" -f $test)
Add-Summary ("Next, after reviewing the amalgamation check: git -C workspace/Catch2 restore {0}" -f ($amalgamated -join ' '))
Write-Host "`nDone. Summary: $summary" -ForegroundColor Green
if ($test -ne 0) { exit 1 }
