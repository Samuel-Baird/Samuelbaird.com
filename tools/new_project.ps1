<#
.SYNOPSIS
    Create the standard D:\Videos\<slug>\ folder layout for a new video project.

.DESCRIPTION
    See docs/pipeline.md section 0. Creates source/, images/, transcripts/,
    script/, cards/, and exports/ under D:\Videos\<slug>\. Safe to re-run —
    existing folders/files are left alone.

.EXAMPLE
    .\new_project.ps1 -Slug sacrament-2026
#>
param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[a-z0-9]+(-[a-z0-9]+)*$')]
    [string]$Slug,

    [string]$Root = "D:\Videos"
)

$projectPath = Join-Path $Root $Slug
$subfolders = @('source', 'images', 'transcripts', 'script', 'cards', 'exports')

if (-not (Test-Path $Root)) {
    New-Item -ItemType Directory -Force -Path $Root | Out-Null
}

New-Item -ItemType Directory -Force -Path $projectPath | Out-Null

foreach ($sub in $subfolders) {
    $subPath = Join-Path $projectPath $sub
    New-Item -ItemType Directory -Force -Path $subPath | Out-Null
}

Write-Host "Project folder ready: $projectPath"
Get-ChildItem $projectPath | Select-Object Name | Format-Table -AutoSize
Write-Host ""
Write-Host "Next: copy source files into '$projectPath\source', then create a"
Write-Host "Resolve project named '$Slug' via the davinci-resolve MCP."
