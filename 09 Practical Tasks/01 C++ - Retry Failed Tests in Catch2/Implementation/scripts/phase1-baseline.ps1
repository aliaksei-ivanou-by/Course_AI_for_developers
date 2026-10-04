# Phase 1: establish the pinned Catch2 v3.16.0 baseline.
#
# Run from the Implementation directory:
#   powershell -ExecutionPolicy Bypass -File .\scripts\phase1-baseline.ps1
#
# First run: clones Catch2 into workspace\Catch2, verifies the tag and a clean
# tree, and creates the task/retry-failed branch.
# Later runs: reuse the existing clone after verifying the pinned commit, the
# branch, and a clean tree.
#
# The source stays in workspace\Catch2. The build directory is created at the
# short path C:\build\Course_AI\catch2\basic-test-build (allowed by the contract's
# permission boundary): with the build tree inside the long checkout path,
# MSBuild's FileTracker hits the Windows MAX_PATH limit (260). A subst drive
# mapping was tried and rejected because Catch2's approvalTests.py resolves the
# real source path and the mapped drive letter then breaks every baseline.
#
# Logs go to evidence\raw\phase1\run-<NN>\ (next free number; UTF-8, ignored by Git);
# summary.txt in that folder is the short record used for artifacts\01-baseline.md.
# The script never deletes files and never runs destructive Git commands.

$ErrorActionPreference = 'Continue'
$expectedTag = 'v3.16.0'
$expectedSha = '317ac1ed4c0bb6e6b91eafc817e05c488feffcb3'
$branch = 'task/retry-failed'
$buildRoot = 'C:\build\Course_AI\catch2'
$buildDir = Join-Path $buildRoot 'basic-test-build'

$implDir = (Get-Location).Path
$repo = Join-Path $implDir 'workspace\Catch2'
$baselines = Join-Path $repo 'tests\SelfTest\Baselines'
# Evidence folders are numbered run-01, run-02, ... in the order of execution.
$evidence = Join-Path $implDir 'evidence\raw\phase1'
New-Item -ItemType Directory -Force -Path $evidence | Out-Null
$last = Get-ChildItem -Path $evidence -Directory |
    ForEach-Object { if ($_.Name -match '^run-(\d+)') { [int]$Matches[1] } } |
    Measure-Object -Maximum
$runName = 'run-{0:D2}' -f $(if ($last.Count -gt 0) { [int]$last.Maximum + 1 } else { 1 })
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

Set-Content -Path $summary -Value "Phase 1 basic-tests baseline, $runName" -Encoding UTF8

if (-not (Test-Path (Join-Path $implDir 'artifacts\00-task-contract.md'))) {
    Stop-Run "Run this script from the Implementation directory."
}

# --- Environment -------------------------------------------------------------
Add-Summary ""
Add-Summary "== environment"
Add-Summary ("os: {0} ({1})" -f (Get-CimInstance Win32_OperatingSystem).Caption, [Environment]::OSVersion.VersionString)
Add-Summary ("powershell: {0}" -f $PSVersionTable.PSVersion)
foreach ($tool in @('git --version', 'cmake --version', 'ctest --version', 'python --version')) {
    Add-Summary ("{0}: {1}" -f $tool, ((Get-Output $tool) -split "`n")[0])
}
Add-Summary ("implementation dir: {0} ({1} chars)" -f $implDir, $implDir.Length)
Add-Summary ("checkout: {0} ({1} chars)" -f $repo, $repo.Length)
Add-Summary ("build dir: {0} ({1} chars)" -f $buildDir, $buildDir.Length)
$cmakeVersionLine = ((Get-Output 'cmake --version') -split "`n")[0]
if ($cmakeVersionLine -match '(\d+)\.(\d+)') {
    if ([int]$Matches[1] -lt 3 -or ([int]$Matches[1] -eq 3 -and [int]$Matches[2] -lt 21)) {
        Stop-Run "CMake 3.21 or newer is required for CMakePresets.json version 3."
    }
} else {
    Stop-Run "CMake was not found on PATH."
}
# --- Checkout (first run) or verification (later runs) ----------------------
if (-not (Test-Path $repo)) {
    Add-Summary ""
    Add-Summary "== mode: fresh clone"
    if ((Invoke-Step 'clone' 'git clone https://github.com/catchorg/Catch2.git workspace/Catch2') -ne 0) { Stop-Run "clone failed" }
    if ((Invoke-Step 'checkout' "git -C workspace/Catch2 checkout $expectedTag") -ne 0) { Stop-Run "checkout of $expectedTag failed" }

    $tag = Get-Output 'git -C workspace/Catch2 describe --exact-match --tags HEAD'
    Add-Summary ""
    Add-Summary "== gate: describe --exact-match --tags HEAD"
    Add-Summary "result: $tag"
    if ($tag -ne $expectedTag) { Stop-Run "HEAD is not exactly $expectedTag" }

    $status = Get-Output 'git -C workspace/Catch2 status --short'
    Add-Summary "== gate: status --short (before branch)"
    Add-Summary ("result: {0}" -f $(if ($status) { $status } else { '<clean>' }))
    if ($status) { Stop-Run "the checkout is not clean" }

    if ((Invoke-Step 'branch' "git -C workspace/Catch2 switch -c $branch") -ne 0) { Stop-Run "could not create $branch" }
} else {
    Add-Summary ""
    Add-Summary "== mode: reuse existing clone"
}

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
if ($remote -ne 'https://github.com/catchorg/Catch2.git') { Stop-Run "origin is '$remote', expected the official Catch2 repository" }
if ($sha -ne $expectedSha) { Stop-Run "HEAD is $sha, expected $expectedSha ($expectedTag)" }
if ($tag -ne $expectedTag) { Stop-Run "HEAD is not exactly $expectedTag" }
if ($current -ne $branch) { Stop-Run "current branch is '$current', expected '$branch'" }
if ($status) { Stop-Run "the working tree is not clean" }

# --- Preconditions for a fresh, honest baseline ------------------------------
if (Test-Path $buildDir) {
    Stop-Run ("$buildDir already exists. It contains only build output. " +
              "Remove it manually and rerun: Remove-Item -Recurse -Force '$buildDir'")
}
$stale = Get-Unapproved
if ($stale.Count -gt 0) {
    # These are ignored by Git, but approve.py would accept them as baselines.
    Stop-Run ("stale approval output in tests\SelfTest\Baselines ($($stale -join ', ')). " +
              "Remove it manually and rerun: Get-ChildItem '$baselines' -Filter *.unapproved.txt | Remove-Item")
}
New-Item -ItemType Directory -Force -Path $buildRoot | Out-Null

# --- Configure, build, test ---------------------------------------------------
# Configure: the basic-tests command from Catch2 docs/contributing.md with a
# different -B path. Build and test follow the documented all-tests pattern,
# plus --config Debug (multi-config generator) and --parallel (speed only).
Set-Location $repo
try {
    $configure = Invoke-Step 'configure' "cmake -B '$buildDir' -S . -DCMAKE_BUILD_TYPE=Debug --preset basic-tests"

    Add-Summary ""
    Add-Summary "== toolchain (from configure log and CMakeCache.txt)"
    Select-String -Path (Join-Path $raw 'configure.log') -Pattern 'compiler identification', 'Building for', 'Windows SDK' |
        ForEach-Object { Add-Summary $_.Line.Trim() }
    $cache = Join-Path $buildDir 'CMakeCache.txt'
    if (Test-Path $cache) {
        Select-String -Path $cache -Pattern '^CMAKE_GENERATOR:', '^CMAKE_GENERATOR_PLATFORM:', '^CMAKE_CXX_COMPILER:', '^CMAKE_HOME_DIRECTORY:' |
            ForEach-Object { Add-Summary $_.Line.Trim() }
    }
    if ($configure -ne 0) { Stop-Run "configure failed" }

    $build = Invoke-Step 'build' "cmake --build '$buildDir' --config Debug --parallel"
    if ($build -ne 0) { Stop-Run "build failed (record it as a baseline issue; do not fix it)" }

    $test = Invoke-Step 'ctest' "ctest --test-dir '$buildDir' -C Debug --output-on-failure"
    Add-Summary ""
    Add-Summary "== ctest totals"
    Select-String -Path (Join-Path $raw 'ctest.log') -Pattern '^\d+% tests passed', '^Total Test time', '^The following tests FAILED', '^\s+\d+ - .+\(.+\)\s*$' |
        ForEach-Object { Add-Summary $_.Line.Trim() }
    # The recorded baseline registers 82 tests; a different count means the
    # test set changed and must be explained before comparing results.
    $totalLine = Select-String -Path (Join-Path $raw 'ctest.log') -Pattern 'tests failed out of (\d+)' | Select-Object -Last 1
    $total = if ($totalLine) { [int]$totalLine.Matches[0].Groups[1].Value } else { 0 }
    Add-Summary ("tests registered: {0} (Phase 1 baseline: 82)" -f $total)
    if ($total -ne 82) { Write-Host "WARNING: $total tests registered, the Phase 1 baseline has 82." -ForegroundColor Yellow }

    $unapproved = Get-Unapproved
    Add-Summary ""
    Add-Summary "== approval differences (tests\SelfTest\Baselines\*.unapproved.txt)"
    Add-Summary ("result: {0}" -f $(if ($unapproved.Count -gt 0) { $unapproved -join ', ' } else { '<none>' }))

    $after = Get-Output 'git status --short'
    Add-Summary ""
    Add-Summary "== status --short after build"
    Add-Summary ("result: {0}" -f $(if ($after) { $after } else { '<clean>' }))
}
finally {
    Set-Location $implDir
}

# --- Course repository must ignore the workspace ----------------------------
foreach ($path in @('workspace/Catch2', 'evidence/raw/phase1')) {
    $ignored = Get-Output "git check-ignore -v $path"
    Add-Summary ""
    Add-Summary "== course repo: git check-ignore -v $path"
    Add-Summary ("result: {0}" -f $(if ($ignored) { $ignored } else { '<NOT IGNORED>' }))
}

Add-Summary ""
Add-Summary ("FINISHED: ctest exit {0}" -f $test)
Write-Host "`nDone. Summary: $summary" -ForegroundColor Green
if ($test -ne 0) { exit 1 }
