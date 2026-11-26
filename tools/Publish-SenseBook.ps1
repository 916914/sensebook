<#
Publish SenseBook to the founder's own GitHub (private repo) and Vercel (locked hub site).
Follows the project's security rules (see CLAUDE.md):
- tokens are typed at a hidden prompt, live only in this PowerShell process, and are cleared at the end;
- no `vercel login`, no `gh auth login`, no Git Credential Manager, nothing saved to disk;
- the Vercel project is locked to your login before the first upload; only the clean site/ folder is deployed;
- GitHub is never connected to Vercel.

Before running:
- GitHub: create an EMPTY PRIVATE repo yourself at https://github.com/new (for example "sensebook"), then make a
  fine-grained token (Settings > Developer settings > Fine-grained tokens) for ONLY that repo with
  "Contents: Read and write", expiring in 1 day.
- Vercel: make a token at https://vercel.com/account/tokens on your personal account, expiring in 1 day.
After running: delete both tokens on those pages.

Run from PowerShell in D:\Sensebook:
  powershell -ExecutionPolicy Bypass -File tools\Publish-SenseBook.ps1            # both
  powershell -ExecutionPolicy Bypass -File tools\Publish-SenseBook.ps1 -Only vercel
  powershell -ExecutionPolicy Bypass -File tools\Publish-SenseBook.ps1 -Only github
#>
param([ValidateSet('both', 'vercel', 'github')][string]$Only = 'both')
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

function Read-Secret([string]$Prompt) {
    $s = Read-Host $Prompt -AsSecureString
    return (New-Object System.Management.Automation.PSCredential 'x', $s).GetNetworkCredential().Password
}

if ($Only -in 'both', 'vercel') {
    Write-Host "`n== Vercel: building the hub site ==" -ForegroundColor Cyan
    python -I tools\build_site.py
    $env:VERCEL_TOKEN = Read-Secret 'Vercel token (hidden)'
    try { python -I tools\publish_vercel.py }
    finally { Remove-Item Env:VERCEL_TOKEN -ErrorAction SilentlyContinue }
}

if ($Only -in 'both', 'github') {
    Write-Host "`n== GitHub: pushing to your private repo ==" -ForegroundColor Cyan
    $repo = Read-Host 'Private repo HTTPS URL (e.g. https://github.com/<you>/sensebook.git)'
    if ($repo -notmatch '^https://github\.com/[^/]+/[^/]+?(\.git)?$') { throw 'That does not look like a GitHub HTTPS repo URL.' }
    if (-not (Test-Path .git)) {
        git init -b main | Out-Null
        git config user.name  'SenseBook founders'
        git config user.email 'founders@users.noreply.github.com'
    }
    git add -A
    $pending = git status --porcelain
    if ($pending) {
        git commit -q -m "SenseBook: venture plan, product spec, financial model, tri-grip design and prototype" `
                      -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
    }
    $tok = Read-Secret 'GitHub fine-grained token (hidden)'
    $b64 = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("x-access-token:$tok"))
    # Pass auth as per-process git config through environment variables: not in arguments, not saved anywhere.
    $env:GIT_CONFIG_COUNT = '2'
    $env:GIT_CONFIG_KEY_0 = 'http.https://github.com/.extraheader'; $env:GIT_CONFIG_VALUE_0 = "AUTHORIZATION: basic $b64"
    $env:GIT_CONFIG_KEY_1 = 'credential.helper';                     $env:GIT_CONFIG_VALUE_1 = ''
    try { git push $repo main }
    finally {
        'GIT_CONFIG_COUNT', 'GIT_CONFIG_KEY_0', 'GIT_CONFIG_VALUE_0', 'GIT_CONFIG_KEY_1', 'GIT_CONFIG_VALUE_1' |
            ForEach-Object { Remove-Item "Env:$_" -ErrorAction SilentlyContinue }
        $tok = $null; $b64 = $null
    }
    Write-Host "Pushed to $repo (the token was not saved)."
}

Write-Host "`nDone. Now delete the tokens you used:" -ForegroundColor Yellow
Write-Host "  https://vercel.com/account/tokens"
Write-Host "  https://github.com/settings/personal-access-tokens"
