param(
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$resourcesRoot = Join-Path $repoRoot "Resources"
$lv0RawRoot = Join-Path $repoRoot "LinguisticDataCore-LV0\\data\\raw"

function Write-Step([string]$message) {
    Write-Host "[setup_raw_links] $message"
}

function Ensure-Dir([string]$path) {
    if (-not (Test-Path -LiteralPath $path)) {
        if ($DryRun) {
            Write-Step "Would create directory: $path"
        } else {
            New-Item -ItemType Directory -Path $path | Out-Null
            Write-Step "Created directory: $path"
        }
    }
}

function Ensure-Junction([string]$linkPath, [string]$targetPath) {
    Ensure-Dir (Split-Path -Parent $linkPath)
    if (Test-Path -LiteralPath $linkPath) {
        $item = Get-Item -LiteralPath $linkPath -Force
        if ($item.LinkType -and ($item.Target -contains $targetPath)) {
            Write-Step "OK junction: $linkPath -> $targetPath"
            return
        }
        Write-Step "SKIP (exists, not target): $linkPath"
        return
    }

    if (-not (Test-Path -LiteralPath $targetPath)) {
        Write-Step "SKIP (missing target): $targetPath"
        return
    }

    if ($DryRun) {
        Write-Step "Would create junction: $linkPath -> $targetPath"
    } else {
        New-Item -ItemType Junction -Path $linkPath -Target $targetPath | Out-Null
        Write-Step "Created junction: $linkPath -> $targetPath"
    }
}

function Ensure-HardLink([string]$linkPath, [string]$targetPath) {
    Ensure-Dir (Split-Path -Parent $linkPath)
    if (Test-Path -LiteralPath $linkPath) {
        $item = Get-Item -LiteralPath $linkPath -Force
        if ($item.LinkType -eq "HardLink") {
            Write-Step "OK hardlink: $linkPath"
            return
        }
        Write-Step "SKIP (exists, not hardlink): $linkPath"
        return
    }

    if (-not (Test-Path -LiteralPath $targetPath)) {
        Write-Step "SKIP (missing target): $targetPath"
        return
    }

    if ($DryRun) {
        Write-Step "Would create hardlink: $linkPath -> $targetPath"
    } else {
        New-Item -ItemType HardLink -Path $linkPath -Target $targetPath | Out-Null
        Write-Step "Created hardlink: $linkPath -> $targetPath"
    }
}

Write-Step "Repo root: $repoRoot"
Write-Step "Resources: $resourcesRoot"
Write-Step "LV0 raw:  $lv0RawRoot"

# Arabic sources
Ensure-Junction (Join-Path $lv0RawRoot "arabic\\quran-morphology") (Join-Path $resourcesRoot "qac_morphology")
Ensure-HardLink (Join-Path $lv0RawRoot "arabic\\word_root_map.csv") (Join-Path $resourcesRoot "word_root_map.csv")
Ensure-Junction (Join-Path $lv0RawRoot "arabic\\arabic_roots_hf") (Join-Path $resourcesRoot "arabic_roots_hf")

# English (cmudict)
Ensure-Junction (Join-Path $lv0RawRoot "english\\cmudict") (Join-Path $resourcesRoot "english_modern")

Write-Step "Done."
