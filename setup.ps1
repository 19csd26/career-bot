# setup.ps1 — Windows setup for Career Bot
# Registers both the Telegram bot and LeetCode auto-committer in Task Scheduler.
# Run in PowerShell (Admin): powershell -ExecutionPolicy Bypass -File setup.ps1

$RepoDir  = Split-Path -Parent $MyInvocation.MyCommand.Path
$Python   = "$RepoDir\.venv\Scripts\python.exe"
$LogDir   = "$env:USERPROFILE\.career-bot"

if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir | Out-Null
}

# ── Sanity checks ──────────────────────────────────────────────────────────────

if (-not (Test-Path "$RepoDir\.env")) {
    Write-Host "ERROR: .env file not found."
    Write-Host "Copy .env.example to .env and fill in your keys."
    exit 1
}

if (-not (Test-Path $Python)) {
    Write-Host "Virtual environment not found. Creating it..."
    python -m venv "$RepoDir\.venv"
    & "$RepoDir\.venv\Scripts\pip" install -q -r "$RepoDir\requirements.txt"
    Write-Host "Dependencies installed."
}

# ── Task Scheduler helper ─────────────────────────────────────────────────────

function Register-BotTask {
    param(
        [string]$Name,
        [string]$Script
    )

    $action   = New-ScheduledTaskAction `
                    -Execute $Python `
                    -Argument "`"$Script`"" `
                    -WorkingDirectory $RepoDir

    $trigger  = New-ScheduledTaskTrigger -AtLogon -User $env:USERNAME

    $settings = New-ScheduledTaskSettingsSet `
                    -ExecutionTimeLimit 0 `
                    -RestartOnIdle `
                    -MultipleInstances IgnoreNew

    Unregister-ScheduledTask -TaskName $Name -Confirm:$false -ErrorAction SilentlyContinue

    Register-ScheduledTask `
        -TaskName $Name `
        -Action   $action `
        -Trigger  $trigger `
        -Settings $settings `
        -RunLevel Highest | Out-Null

    Start-ScheduledTask -TaskName $Name
    Write-Host "  OK  $Name (Task Scheduler)"
}

# ── Register tasks ────────────────────────────────────────────────────────────

Write-Host "Platform: Windows"
Register-BotTask -Name "CareerBot-TelegramBot" -Script "$RepoDir\telegram_bot.py"
Register-BotTask -Name "CareerBot-LCWatcher"   -Script "$RepoDir\lc_watcher.py"

Write-Host ""
Write-Host "Both services are running and will auto-start on every login."
Write-Host ""
Write-Host "Logs:"
Write-Host "  Get-Content $LogDir\telegram_bot_error.log -Wait"
Write-Host "  Get-Content $LogDir\lc_watcher_error.log -Wait"
Write-Host ""
Write-Host "Manage tasks: open taskschd.msc"
Write-Host ""
Write-Host "Next step: open Telegram and send /start to your bot (first time only)."
