<#
.SYNOPSIS
    Create the standard D:\Videos\<slug>\ folder layout for a new video project.

.DESCRIPTION
    See docs/pipeline.md section 0 for -Type standard (response / interview /
    solo-history — all use the same folder set and a Resolve project).
    See docs/types/saint-capybara.md and docs/saint-capybara/*.md for
    -Type saint-capybara, which uses a different folder set (no cards\,
    adds research\/audio\/captions\/frames\). Its Resolve project is
    created later, at build time (see
    docs/saint-capybara/hybrid-resolve-pipeline.md), not by this script.
    Safe to re-run — existing folders/files are left alone.

.EXAMPLE
    .\new_project.ps1 -Slug sacrament-2026
.EXAMPLE
    .\new_project.ps1 -Slug adam-god-claim -Type saint-capybara
.EXAMPLE
    .\new_project.ps1 -Slug tribune-oped-response -Type saint-capybara -SourceKind article
#>
param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[a-z0-9]+(-[a-z0-9]+)*$')]
    [string]$Slug,

    [ValidateSet('standard', 'saint-capybara')]
    [string]$Type = 'standard',

    # saint-capybara only: 'video' (a clip is reacted to) or 'article' (a
    # text source; the beats template uses `excerpt` beats instead of clips
    # and the source is ingested with capy_ingest.py --article-file).
    [ValidateSet('video', 'article')]
    [string]$SourceKind = 'video',

    [string]$Root = "D:\Videos"
)

$projectPath = Join-Path $Root $Slug

if ($Type -eq 'saint-capybara') {
    $subfolders = @('source', 'transcripts', 'research', 'images', 'script', 'audio', 'captions', 'frames', 'exports')
} else {
    $subfolders = @('source', 'images', 'transcripts', 'script', 'cards', 'exports')
}

if (-not (Test-Path $Root)) {
    New-Item -ItemType Directory -Force -Path $Root | Out-Null
}

New-Item -ItemType Directory -Force -Path $projectPath | Out-Null

foreach ($sub in $subfolders) {
    $subPath = Join-Path $projectPath $sub
    New-Item -ItemType Directory -Force -Path $subPath | Out-Null
}

if ($Type -eq 'saint-capybara') {
    $repoRoot = Split-Path -Parent $PSScriptRoot
    $templatesDir = Join-Path $repoRoot 'assets\saint-capybara\templates'

    $beatsTemplate = if ($SourceKind -eq 'article') { 'beats.article.yaml' } else { 'beats.yaml' }
    $scriptBeatsDest = Join-Path $projectPath 'script\beats.yaml'
    if (-not (Test-Path $scriptBeatsDest)) {
        $beatsContent = Get-Content (Join-Path $templatesDir $beatsTemplate) -Raw
        $beatsContent = $beatsContent.Replace('REPLACE-WITH-SLUG', $Slug)
        Set-Content -Path $scriptBeatsDest -Value $beatsContent -NoNewline -Encoding utf8
    }

    $claimsDest = Join-Path $projectPath 'research\claims.md'
    if (-not (Test-Path $claimsDest)) {
        $claimsContent = (Get-Content (Join-Path $templatesDir 'claims.md') -Raw).Replace('REPLACE-WITH-SLUG', $Slug)
        Set-Content -Path $claimsDest -Value $claimsContent -NoNewline -Encoding utf8
    }

    $sourcesDest = Join-Path $projectPath 'research\sources.yaml'
    if (-not (Test-Path $sourcesDest)) {
        Copy-Item (Join-Path $templatesDir 'sources.yaml') $sourcesDest
    }

    $pronDest = Join-Path $projectPath 'script\pronunciations.yaml'
    if (-not (Test-Path $pronDest)) {
        Copy-Item (Join-Path $templatesDir 'pronunciations.yaml') $pronDest
    }

    Write-Host ""
    Write-Host "Saint Capybara templates copied: script\beats.yaml (from $beatsTemplate --"
    Write-Host "remember the closing beat must end on '...God bless.', see"
    Write-Host "docs/saint-capybara/script-format.md), research\claims.md,"
    Write-Host "research\sources.yaml, script\pronunciations.yaml."
    Write-Host ""
    if ($SourceKind -eq 'article') {
        Write-Host "Source kind: ARTICLE (text). Next:"
        Write-Host "  1. Fetch the article with the agent's WebFetch (or have the user paste it"
        Write-Host "     for paywalled pieces) into a cleaned .md, blank-line separated paragraphs."
        Write-Host "  2. python tools\capy_ingest.py --article-file cleaned.md --article-url URL"
        Write-Host "       --publication ... --byline ... --date YYYY-MM-DD [--paywalled]"
        Write-Host "       [--archive auto|fresh|skip | --archive-url ...] --project $projectPath"
        Write-Host "     -> source\source.md (numbered paragraphs) + source\source_info.json (kind: article, sha256 pin)."
        Write-Host "  3. research\claims.md with paragraph anchors; research\sources.yaml with the"
        Write-Host "     article as the type: critic / source_kind: article entry (see the template)."
        Write-Host "  4. script\beats.yaml: excerpt beats (kind: excerpt, para: N) precede each response."
        Write-Host "  5. capy_check_sources.py -> capy_check_brand.py -> capy_storyboard.py -> Gate A."
    } else {
        Write-Host "Source kind: VIDEO. Next: tools\capy_ingest.py (URL and/or local file) ->"
        Write-Host "transcribe -> research (docs\saint-capybara\research-protocol.md) -> fill in"
        Write-Host "script\beats.yaml -> capy_check_sources.py -> capy_check_brand.py ->"
        Write-Host "capy_storyboard.py -> Gate A."
    }
} else {
    Write-Host "Next: copy source files into '$projectPath\source', then create a"
    Write-Host "Resolve project named '$Slug' via the davinci-resolve MCP."
}

Write-Host ""
Write-Host "Project folder ready: $projectPath"
Get-ChildItem $projectPath | Select-Object Name | Format-Table -AutoSize
