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
    See docs/types/meme-edit.md for -Type meme-edit (base video + inserts +
    meme text + TTS voice lines); -Brand is required for it, since a meme
    can be made for either identity and the anonymity rules depend on it.
    -VideoType (saint-capybara only) picks one of the three Saint Capybara
    video types: short (default, 9:16, 60-180s), long-instagram (9:16, up
    to 20 min) or long-youtube (16:9, no length cap). Use a long type ONLY
    when the user explicitly asked for it (docs/saint-capybara/
    script-format.md "Video types").
    Safe to re-run — existing folders/files are left alone.

.EXAMPLE
    .\new_project.ps1 -Slug sacrament-2026
.EXAMPLE
    .\new_project.ps1 -Slug adam-god-claim -Type saint-capybara
.EXAMPLE
    .\new_project.ps1 -Slug tribune-oped-response -Type saint-capybara -SourceKind article
.EXAMPLE
    .\new_project.ps1 -Slug book-of-abraham-deep-dive -Type saint-capybara -VideoType long-instagram
.EXAMPLE
    .\new_project.ps1 -Slug kinderhook-plates-explained -Type saint-capybara -VideoType long-youtube
.EXAMPLE
    .\new_project.ps1 -Slug potluck-desserts -Type meme-edit -Brand standard
#>
param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[a-z0-9]+(-[a-z0-9]+)*$')]
    [string]$Slug,

    [ValidateSet('standard', 'saint-capybara', 'meme-edit')]
    [string]$Type = 'standard',

    # saint-capybara only: 'video' (a clip is reacted to) or 'article' (a
    # text source; the beats template uses `excerpt` beats instead of clips
    # and the source is ingested with capy_ingest.py --article-file).
    [ValidateSet('video', 'article')]
    [string]$SourceKind = 'video',

    # saint-capybara only: 'short' (9:16, 60-180s, the default),
    # 'long-instagram' (9:16, 180-1200s) or 'long-youtube' (16:9, 180s+,
    # no length cap). Long types only when the user explicitly asks.
    [ValidateSet('short', 'long-instagram', 'long-youtube')]
    [string]$VideoType = 'short',

    # meme-edit only (required there): which identity the meme is for.
    [ValidateSet('standard', 'saint-capybara')]
    [string]$Brand,

    [string]$Root = "D:\Videos"
)

$projectPath = Join-Path $Root $Slug

if ($Type -eq 'meme-edit' -and -not $Brand) {
    throw "-Type meme-edit needs -Brand standard|saint-capybara (see docs/types/meme-edit.md 'Brand')"
}
if ($VideoType -ne 'short' -and $Type -ne 'saint-capybara') {
    throw "-VideoType $VideoType is only for -Type saint-capybara"
}

if ($Type -eq 'saint-capybara') {
    $subfolders = @('source', 'transcripts', 'research', 'images', 'script', 'audio', 'captions', 'frames', 'exports')
} elseif ($Type -eq 'meme-edit') {
    $subfolders = @('source', 'transcripts', 'inserts', 'overlays', 'audio', 'script', 'exports')
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

    # research/briefs/ holds the multi-angle research subagents' output
    # (docs/saint-capybara/research-protocol.md sec 15, /capy-research skill).
    New-Item -ItemType Directory -Force -Path (Join-Path $projectPath 'research\briefs') | Out-Null

    $beatsTemplate = if ($SourceKind -eq 'article') { 'beats.article.yaml' } else { 'beats.yaml' }
    $scriptBeatsDest = Join-Path $projectPath 'script\beats.yaml'
    if (-not (Test-Path $scriptBeatsDest)) {
        $beatsContent = Get-Content (Join-Path $templatesDir $beatsTemplate) -Raw
        $beatsContent = $beatsContent.Replace('REPLACE-WITH-SLUG', $Slug)
        if ($VideoType -ne 'short') {
            # long-youtube: no max_seconds -- no length cap (capy.beats.VIDEO_TYPES).
            $size = if ($VideoType -eq 'long-youtube') { 'width: 1920, height: 1080' } else { 'width: 1080, height: 1920' }
            $maxPart = if ($VideoType -eq 'long-youtube') { '' } else { ', max_seconds: 1200' }
            # Two single-line replaces (not one spanning a newline) so a CRLF
            # checkout of the template still matches.
            $beatsContent = $beatsContent.Replace(
                'video_type: short',
                "video_type: $VideoType`nlong_form_requested: `"REPLACE: date + the user's own words asking for long form`"")
            $beatsContent = $beatsContent.Replace(
                'format: { width: 1080, height: 1920, fps: 30, min_seconds: 60, max_seconds: 180 }',
                "format: { $size, fps: 30, min_seconds: 180$maxPart }")
        }
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
    if ($VideoType -ne 'short') {
        Write-Host "VIDEO TYPE: $VideoType. Fill in long_form_requested:"
        Write-Host "in script\beats.yaml with the user's own request -- the lint errors without it."
        Write-Host ""
    }
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
} elseif ($Type -eq 'meme-edit') {
    $repoRoot = Split-Path -Parent $PSScriptRoot
    $planDest = Join-Path $projectPath 'script\edit-plan.md'
    if (-not (Test-Path $planDest)) {
        $plan = Get-Content (Join-Path $repoRoot 'assets\meme-edit\edit-plan.md') -Raw
        $plan = $plan.Replace('REPLACE-WITH-SLUG', $Slug).Replace('REPLACE-WITH-BRAND', $Brand)
        Set-Content -Path $planDest -Value $plan -NoNewline -Encoding utf8
    }
    Write-Host ""
    Write-Host "Meme/edit project (brand: $Brand). script\edit-plan.md copied. Next:"
    Write-Host "  1. Base video into source\ (capy_ingest.py URL, or copy a local file), transcribe."
    Write-Host "  2. Fill in script\edit-plan.md, push it to reviews\$Slug\, wait for approval."
    Write-Host "  3. meme_text.py -> overlays\, capy_tts.py --sample -> audio\, inserts\, then Resolve."
    if ($Brand -eq 'saint-capybara') {
        Write-Host "  Saint Capybara brand: brand.md sec 9-10 anonymity rules apply; finish with the"
        Write-Host "  metadata-strip remux + capy_check_brand.py."
    } else {
        Write-Host "  Standard brand: no Saint Capybara assets (sprites, pixel fonts, am_michael voice)."
    }
} else {
    Write-Host "Next: copy source files into '$projectPath\source', then create a"
    Write-Host "Resolve project named '$Slug' via the davinci-resolve MCP."
}

Write-Host ""
Write-Host "Project folder ready: $projectPath"
Get-ChildItem $projectPath | Select-Object Name | Format-Table -AutoSize
