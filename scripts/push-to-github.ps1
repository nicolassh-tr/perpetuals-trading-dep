# Usage (after creating an empty repo on GitHub):
#   .\scripts\push-to-github.ps1 https://github.com/YOUR_USER/perpetuals-trading-dep.git
param(
    [Parameter(Mandatory = $true)]
    [string] $RemoteUrl
)
Set-Location $PSScriptRoot\..
if (-not (git remote get-url origin 2>$null)) {
    git remote add origin $RemoteUrl
} else {
    git remote set-url origin $RemoteUrl
}
git push -u origin main
