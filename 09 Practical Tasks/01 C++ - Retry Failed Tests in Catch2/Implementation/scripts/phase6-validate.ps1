# Phase 6: build and test the Catch2 checkout for one task.
#
# Run from the Implementation directory:
#   powershell -ExecutionPolicy Bypass -File .\scripts\phase6-validate.ps1 -Task T01 -Preset basic
#   powershell -ExecutionPolicy Bypass -File .\scripts\phase6-validate.ps1 -Task T03 -Preset all -Filter 'RetryFailed'
#
# -Task    task ID from artifacts\06-tasks.md (used for the evidence folder)
# -Preset  basic -> basic-tests preset in <BuildRoot>\basic-test-build
#          all   -> all-tests preset in <BuildRoot>\debug-build (also builds the extra tests)
# -Filter  optional CTest -R regular expression; matching tests run first as the
#          focused set, then the full suite of the preset runs
#
# The checkout must be the task branch based on v3.16.0. Uncommitted changes are
# expected (the files of the task under test) and are recorded, not rejected.
# Build directories are reused for incremental builds. The amalgamated files are
# not regenerated (task T13 does that). Logs go to
# evidence\raw\phase6\<Task>-run-NN-<preset>\ (UTF-8, ignored by Git). The folder
# is kept flat so that it stays within the nesting depth the review tooling can read.
# The script never deletes files and never runs destructive Git commands.

param(
    [Parameter(Mandatory = $true)][ValidatePattern('^T\d{2}$')][string]$Task,
    [Parameter(Mandatory = $true)][ValidateSet('basic', 'all')][string]$Preset,
    [string]$Filter = '',
    [string]$BuildRoot = 'C:\build\Course_AI\catch2'
)

$ErrorActionPreference = 'Continue'
$baseSha = '317ac1ed4c0bb6e6b91eafc817e05c488feffcb3'
$expectedRemote = 'https://github.com/catchorg/Catch2.git'
$branch = 'task/retry-failed'
$presetName = if ($Preset -eq 'basic') { 'basic-tests' } else { 'all-tests' }
$buildDir = Join-Path $BuildRoot $(if ($Preset -eq 'basic') { 'basic-test-build' } else { 'debug-build' })

if ($Filter -match "'") {
    Write-Host "STOPPED: -Filter must not contain single quotes." -ForegroundColor Red
    exit 1
}

$implDir = (Get-Location).Path
$repo = Join-Path $implDir 'workspace\Catch2'
$baselines = Join-Path $repo 'tests\SelfTest\Baselines'

# Evidence folders are numbered <Task>-run-01, <Task>-run-02, ... per task.
$phaseDir = Join-Path $implDir 'evidence\raw\phase6'
New-Item -ItemType Directory -Force -Path $phaseDir | Out-Null
$last = Get-ChildItem -Path $phaseDir -Directory |
    ForEach-Object { if ($_.Name -match ('^' + $Task + '-run-(\d+)')) { [int]$Matches[1] } } |
    Measure-Object -Maximum
$runName = '{0}-run-{1:D2}-{2}' -f $Task, $(if ($last.Count -gt 0) { [int]$last.Maximum + 1 } else { 1 }), $Preset
$raw = Join-Path $phaseDir $runName
New-Item -ItemType Directory -Path $raw | Out-Null
$summary = Join-Path $raw 'summary.txt'

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

function Add-CtestSummary([string]$name) {
    $log = Join-Path $raw ("{0}.log" -f $name)
    Add-Summary ""
    Add-Summary "== $name totals"
    Select-String -Path $log -Pattern '^\d+% tests passed', '^Total Test time', '^The following tests', '^\s+\d+ - .+\(.+\)\s*$', '^No tests were found' |
        ForEach-Object { Add-Summary $_.Line.Trim() }
}

function Stop-Run([string]$reason) {
    if ((Get-Location).Path -ne $implDir) { Set-Location $implDir }
    Add-Summary ""
    Add-Summary "STOPPED: $reason"
    Write-Host "STOPPED: $reason" -ForegroundColor Red
    Write-Host "Summary: $summary"
    exit 1
}

Set-Content -Path $summary -Value ("Phase 6 validation: {0}, preset {1}" -f $runName, $presetName) -Encoding UTF8

if (-not (Test-Path (Join-Path $implDir 'artifacts\06-tasks.md'))) {
    Stop-Run "Run this script from the Implementation directory."
}
if (-not (Test-Path $repo)) { Stop-Run "workspace\Catch2 does not exist." }

# --- Environment -------------------------------------------------------------
Add-Summary ""
Add-Summary "== environment"
Add-Summary ("os: {0}" -f [Environment]::OSVersion.VersionString)
Add-Summary ("powershell: {0}" -f $PSVersionTable.PSVersion)
foreach ($tool in @('git --version', 'cmake --version', 'ctest --version', 'python --version')) {
    Add-Summary ("{0}: {1}" -f $tool, ((Get-Output $tool) -split "`n")[0])
}
Add-Summary ("build dir: {0}" -f $buildDir)
Add-Summary ("filter: {0}" -f $(if ($Filter) { $Filter } else { '<none>' }))

# --- Repository state --------------------------------------------------------
Add-Summary ""
Add-Summary "== repository state"
$remote = Get-Output 'git -C workspace/Catch2 remote get-url origin'
$head = Get-Output 'git -C workspace/Catch2 rev-parse HEAD'
$current = Get-Output 'git -C workspace/Catch2 branch --show-current'
$global:LASTEXITCODE = 0
git -C workspace/Catch2 merge-base --is-ancestor $baseSha HEAD 2>$null
$basedOnTag = ($LASTEXITCODE -eq 0)
$status = Get-Output 'git -C workspace/Catch2 status --short'
$diffStat = Get-Output 'git -C workspace/Catch2 diff --stat HEAD'
Add-Summary "remote: $remote"
Add-Summary "head: $head"
Add-Summary "branch: $current"
Add-Summary "based on v3.16.0 ($baseSha): $basedOnTag"
Add-Summary "status --short:"
Add-Summary $(if ($status) { $status } else { '<clean>' })
Add-Summary "diff --stat HEAD:"
Add-Summary $(if ($diffStat) { $diffStat } else { '<none>' })
if ($remote -ne $expectedRemote) { Stop-Run "origin is '$remote', expected $expectedRemote" }
if ($current -ne $branch) { Stop-Run "current branch is '$current', expected '$branch'" }
if (-not $basedOnTag) { Stop-Run "HEAD does not descend from v3.16.0 ($baseSha)" }

$stale = Get-Unapproved
if ($stale.Count -gt 0) {
    # These are ignored by Git, but approve.py would accept them as baselines.
    Stop-Run ("stale approval output in tests\SelfTest\Baselines ($($stale -join ', ')). " +
              "Inspect it, then remove it manually and rerun: Get-ChildItem '$baselines' -Filter *.unapproved.txt | Remove-Item")
}
New-Item -ItemType Directory -Force -Path $BuildRoot | Out-Null

# --- Configure, build, test --------------------------------------------------
$focusedCode = $null
$fullCode = $null
Set-Location $repo
try {
    $configure = Invoke-Step 'configure' "cmake -B '$buildDir' -S . -DCMAKE_BUILD_TYPE=Debug --preset $presetName"
    if ($configure -ne 0) { Stop-Run "configure failed" }

    $build = Invoke-Step 'build' "cmake --build '$buildDir' --config Debug --parallel"
    $buildLog = Join-Path $raw 'build.log'
    Add-Summary ("build warnings: {0}   build errors: {1}" -f
        @(Select-String -Path $buildLog -Pattern 'warning [A-Z]*\d+|warning:').Count,
        @(Select-String -Path $buildLog -Pattern 'error [A-Z]*\d+|error:').Count)
    if ($build -ne 0) {
        Add-Summary ""
        Add-Summary "== build errors (first 40)"
        Select-String -Path $buildLog -Pattern 'error [A-Z]*\d+|error:' |
            Select-Object -First 40 | ForEach-Object { Add-Summary $_.Line.Trim() }
        Stop-Run "build failed"
    }

    $jobs = if ($Preset -eq 'all') { ' -j 4' } else { '' }
    if ($Filter) {
        $focusedCode = Invoke-Step 'ctest-focused' "ctest --test-dir '$buildDir' -C Debug --output-on-failure -R '$Filter'"
        Add-CtestSummary 'ctest-focused'
    }
    $fullCode = Invoke-Step 'ctest-full' "ctest --test-dir '$buildDir' -C Debug --output-on-failure$jobs"
    Add-CtestSummary 'ctest-full'

    $unapproved = Get-Unapproved
    Add-Summary ""
    Add-Summary "== approval differences (tests\SelfTest\Baselines\*.unapproved.txt)"
    Add-Summary ("result: {0}" -f $(if ($unapproved.Count -gt 0) { $unapproved -join ', ' } else { '<none>' }))

    $after = Get-Output 'git status --short'
    Add-Summary ""
    Add-Summary "== status --short after the run (expected: only the task's files)"
    Add-Summary $(if ($after) { $after } else { '<clean>' })
}
finally {
    Set-Location $implDir
}

$ok = ($fullCode -eq 0) -and (($null -eq $focusedCode) -or ($focusedCode -eq 0))
$result = if ($ok) { 'PASSED' } else { 'FAILED' }
Add-Summary ""
Add-Summary ("FINISHED: {0} (focused exit {1}, full exit {2})" -f $result,
    $(if ($null -eq $focusedCode) { 'n/a' } else { $focusedCode }), $fullCode)
Write-Host ("`n{0}. Summary: {1}" -f $result, $summary) -ForegroundColor $(if ($ok) { 'Green' } else { 'Red' })
if (-not $ok) { exit 1 }
