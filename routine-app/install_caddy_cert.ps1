<#
.SYNOPSIS
    Trust the Caddy local root CA so browsers stop warning about the sovereign
    LifeHub HTTPS certificate.

.DESCRIPTION
    Caddy is configured with `local_certs` and signs its own HTTPS certificates
    from a private root CA (CN=Caddy Local Authority ... Root). Windows does not
    trust that root by default, which is why the browser shows
    "Connection is not private". Installing this root into Cert:\CurrentUser\Root
    fixes it for THIS user only -- no admin rights, no machine-wide trust.

.PARAMETER CertPath
    Path to the Caddy root certificate (.crt). Defaults to the copy synced under
    infrastructure/sj_atom, resolved relative to this script.

.NOTES
    Scope : CurrentUser (HKCU) -- does NOT require an elevated/admin shell.
    Safe  : Idempotent. If the cert is already trusted it does nothing.
            Refuses to install anything that is not the self-signed Caddy root.
#>

[CmdletBinding()]
param(
    [string]$CertPath = (Join-Path $PSScriptRoot '..\infrastructure\sj_atom\caddy_root.crt'),
    [string]$StoreLocation = 'Cert:\CurrentUser\Root'
)

$ErrorActionPreference = 'Stop'

# Guard: we only ever trust a root whose subject matches this.
$ExpectedSubjectPattern = 'Caddy Local Authority'

function Fail($msg) { Write-Host "[FAIL] $msg" -ForegroundColor Red; exit 1 }

# 1. Resolve & validate the cert file ----------------------------------------
if (-not (Test-Path -LiteralPath $CertPath)) {
    Fail "Certificate not found at: $CertPath`n       Pass -CertPath '<path-to-caddy_root.crt>' explicitly."
}
$CertPath = (Resolve-Path -LiteralPath $CertPath).Path
Write-Host "[*] Certificate file : $CertPath"

# 2. Load & inspect BEFORE trusting ------------------------------------------
try {
    $cert = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2 $CertPath
} catch {
    Fail "File is not a valid X.509 certificate: $($_.Exception.Message)"
}

Write-Host "[*] Subject          : $($cert.Subject)"
Write-Host "[*] Issuer           : $($cert.Issuer)"
Write-Host "[*] Valid            : $($cert.NotBefore) -> $($cert.NotAfter)"
Write-Host "[*] Thumbprint       : $($cert.Thumbprint)"

# Refuse to trust anything that is not a self-signed CA matching the expectation.
if ($cert.Subject -ne $cert.Issuer) {
    Fail "Refusing to install: certificate is NOT self-signed (not a root)."
}
if ($cert.Subject -notmatch $ExpectedSubjectPattern) {
    Fail "Refusing to install: subject does not match '$ExpectedSubjectPattern'. This is not the Caddy root."
}
if ($cert.NotAfter -lt (Get-Date)) {
    Fail "Refusing to install: certificate expired on $($cert.NotAfter)."
}

# 3. Idempotency: already trusted? -------------------------------------------
$existing = Get-ChildItem -Path $StoreLocation | Where-Object { $_.Thumbprint -eq $cert.Thumbprint }
if ($existing) {
    Write-Host "`n[OK] Already trusted in $StoreLocation (thumbprint $($cert.Thumbprint)). Nothing to do." -ForegroundColor Green
    exit 0
}

# 4. Install ------------------------------------------------------------------
# Adding to the CurrentUser Root store raises a one-time Windows consent dialog
# ("You are about to install a certificate from a certification authority...").
# Click YES to trust the Caddy root. This prompt is a deliberate Windows
# security control for root-store changes -- approving it is the whole point.
Write-Host "`n[*] Installing into $StoreLocation ..."
Write-Host "[*] Windows will show a consent dialog -- click YES to trust the Caddy root." -ForegroundColor Cyan
try {
    $null = Import-Certificate -FilePath $CertPath -CertStoreLocation $StoreLocation -ErrorAction Stop
} catch {
    if ($_.Exception.Message -match 'UI is not allowed') {
        Fail "This shell is non-interactive, so the trust-consent dialog cannot be shown.`n       Run this script from a normal (interactive) PowerShell window and click YES on the prompt."
    }
    Fail "Install failed: $($_.Exception.Message)"
}

# 5. Verify -------------------------------------------------------------------
$verify = Get-ChildItem -Path $StoreLocation | Where-Object { $_.Thumbprint -eq $cert.Thumbprint }
if ($verify) {
    Write-Host "[OK] Caddy root CA is now trusted for the current user." -ForegroundColor Green
    Write-Host "     Thumbprint: $($cert.Thumbprint)"
    Write-Host "     Fully restart your browser, then reload the LifeHub site -- the warning should be gone."
} else {
    Fail "Post-install verification could not find the certificate in the store."
}
