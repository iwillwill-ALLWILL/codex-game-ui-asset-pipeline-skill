param(
    [switch]$Force
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$source = Join-Path $repoRoot "skills\game-ui-asset-pipeline"
if (-not (Test-Path -LiteralPath $source)) {
    throw "Skill source not found: $source"
}

$codexHome = $env:CODEX_HOME
if ([string]::IsNullOrWhiteSpace($codexHome)) {
    $codexHome = Join-Path $HOME ".codex"
}

$destParent = Join-Path $codexHome "skills"
$dest = Join-Path $destParent "game-ui-asset-pipeline"
New-Item -ItemType Directory -Path $destParent -Force | Out-Null

if (Test-Path -LiteralPath $dest) {
    if (-not $Force) {
        throw "Destination already exists: $dest. Re-run with -Force to replace it."
    }
    Remove-Item -LiteralPath $dest -Recurse -Force
}

Copy-Item -LiteralPath $source -Destination $dest -Recurse
Write-Host "Installed game-ui-asset-pipeline to $dest"
Write-Host "Restart Codex to pick up the skill."
