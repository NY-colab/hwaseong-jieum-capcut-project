param(
    [string]$Repository = 'NY-colab/hwaseong-jieum-capcut-project',
    [string]$Tag = 'latest',
    [string]$DownloadDirectory = (Join-Path $PSScriptRoot 'downloads'),
    [string]$DraftRoot,
    [switch]$DownloadOnly
)
$ErrorActionPreference = 'Stop'
if (Get-Process -Name CapCut -ErrorAction SilentlyContinue) { throw 'CapCut을 저장하고 완전히 종료한 뒤 다시 실행하세요.' }
if ($Repository -notmatch '^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$') { throw 'Invalid repository.' }
if ($Tag -eq 'latest') { $api = "https://api.github.com/repos/$Repository/releases/latest" }
else { $encodedTag = [uri]::EscapeDataString($Tag); $api = "https://api.github.com/repos/$Repository/releases/tags/$encodedTag" }
$release = Invoke-RestMethod -Uri $api -Headers @{ 'User-Agent'='Jieum-CapCut-Installer' }
$target = Join-Path $DownloadDirectory ([guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $target -Force | Out-Null
$names = @('SHA256SUMS.txt','hwaseong-jieum-capcut.zip')
$assets = @($release.assets | Where-Object { $_.name -in $names -or $_.name -match '^hwaseong-jieum-capcut\.zip\.part[0-9]+$' })
if (-not ($assets | Where-Object name -eq 'SHA256SUMS.txt')) { throw 'Release checksum file missing.' }
foreach ($asset in $assets) {
    if ($asset.browser_download_url -notlike 'https://github.com/*') { throw 'Unexpected download host.' }
    Invoke-WebRequest -Uri $asset.browser_download_url -OutFile (Join-Path $target $asset.name)
}
$checksumFile = Join-Path $target 'SHA256SUMS.txt'
$verifiedNames = @()
foreach ($line in Get-Content -LiteralPath $checksumFile) {
    if ($line -notmatch '^([a-fA-F0-9]{64})  (hwaseong-jieum-capcut\.zip(?:\.part[0-9]+)?)$') { throw 'Invalid checksum record.' }
    $expected = $Matches[1]; $assetName = $Matches[2]; $file = Join-Path $target $assetName
    if (-not (Test-Path -LiteralPath $file)) { throw "Missing release asset: $file" }
    if ((Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash -ne $expected) { throw "Checksum mismatch: $file" }
    if ($assetName -in $verifiedNames) { throw 'Duplicate checksum record.' }
    $verifiedNames += $assetName
}
if ($verifiedNames.Count -eq 0) { throw 'Checksum list is empty.' }
foreach ($asset in $assets | Where-Object name -ne 'SHA256SUMS.txt') {
    if ($asset.name -notin $verifiedNames) { throw 'Downloaded asset is not listed in SHA256SUMS.txt.' }
}
$zip = Join-Path $target 'hwaseong-jieum-capcut.zip'
if (-not (Test-Path -LiteralPath $zip)) {
    $parts = @(Get-ChildItem -LiteralPath $target -Filter '*.part*' | Sort-Object Name)
    if ($parts.Count -eq 0) { throw 'Release ZIP missing.' }
    for ($i = 0; $i -lt $parts.Count; $i++) {
        $expectedPart = 'hwaseong-jieum-capcut.zip.part{0:000}' -f ($i + 1)
        if ($parts[$i].Name -ne $expectedPart) { throw 'Missing or out-of-order ZIP part.' }
    }
    $stream = [IO.File]::Create($zip)
    try { foreach ($part in $parts) { $inputStream = [IO.File]::OpenRead($part.FullName); try { $inputStream.CopyTo($stream) } finally { $inputStream.Dispose() } } }
    finally { $stream.Dispose() }
}
if ($DownloadOnly) { Write-Output $zip; exit 0 }
$unpacked = Join-Path $target 'package'
# Python checks every ZIP member for traversal and symlinks before extraction.
$extract = @'
import pathlib,sys,zipfile
dest=pathlib.Path(sys.argv[2]).resolve()
with zipfile.ZipFile(sys.argv[1]) as z:
 for m in z.infolist():
  p=pathlib.Path(m.filename)
  if p.is_absolute() or '..' in p.parts or ':' in m.filename or '\\' in m.filename or (m.external_attr>>16)&0o170000==0o120000:raise SystemExit('Unsafe ZIP entry')
 z.extractall(dest)
'@
$python = Get-Command python -ErrorAction Stop
& $python.Source -c $extract $zip $unpacked
if ($LASTEXITCODE -ne 0) { throw 'Extraction failed.' }
$installer = Join-Path $unpacked 'install_project.py'
$arguments = @($installer, '--package', $unpacked)
if ($DraftRoot) { $arguments += @('--draft-root', $DraftRoot) }
& $python.Source @arguments
if ($LASTEXITCODE -ne 0) { throw 'Project installation failed.' }
