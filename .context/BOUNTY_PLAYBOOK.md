# 🎯 Bug Bounty Master Playbook
> Compiled from 10 research streams. This is the operational bible.

---

## Phase 1: RECONNAISSANCE (The Foundation)

### 1.1 Subdomain Enumeration
```bash
# Passive enumeration (fast, stealthy)
subfinder -d target.com -o subs.txt
assetfinder --subs-only target.com >> subs.txt
amass enum -passive -d target.com >> subs.txt

# Brute-force with permutations
puredns bruteforce wordlist.txt target.com -o brute_subs.txt
dnsgen subs.txt | puredns resolve > permuted_subs.txt
altdns -i subs.txt -o altered_subs.txt -w words.txt

# Resolve all
sort -u subs.txt brute_subs.txt permuted_subs.txt > all_subs.txt
massdns -r resolvers.txt all_subs.txt -o S > resolved.txt
```

### 1.2 Live Host Discovery
```bash
# Probe for live HTTP services
cat all_subs.txt | httpx -silent -status-code -title -tech-detect -o live_hosts.txt

# Extract technology stack
cat all_subs.txt | httpx -silent -tech-detect -json -o tech_stack.json
```

### 1.3 ASN & IP Range Discovery
```bash
# Find all IP ranges owned by the target
# Check: bgp.he.net, asnlookup
# This reveals dev servers, acquired infrastructure, forgotten assets
whois -h whois.radb.net -- '-i origin AS12345' | grep -Eo "([0-9.]+){4}/[0-9]+"
```

### 1.4 Content & Endpoint Discovery
```bash
# JavaScript file extraction (GOLD MINE for API keys/endpoints)
cat live_hosts.txt | katana -js-crawl -d 3 -o crawled_urls.txt
cat crawled_urls.txt | grep "\.js$" | httpx -sr -srd js_files/

# Extract endpoints from JS
cat js_files/* | linkfinder -i - -o endpoints.txt

# Wayback Machine mining
echo "target.com" | gau --threads 5 --o wayback_urls.txt
cat wayback_urls.txt | grep -E "\.(js|json|xml|config|env|bak|sql)$" > interesting_files.txt

# Parameter discovery
arjun -u https://target.com/api/endpoint -m GET POST
cat wayback_urls.txt | gf interestingparams > params.txt

# Directory fuzzing
ffuf -u https://target.com/FUZZ -w /path/to/SecLists/Discovery/Web-Content/raft-large-directories.txt -mc 200,301,302,403
```

### 1.5 Cloud & Infrastructure Recon
```bash
# S3 bucket enumeration
cloud_enum -k target -l results.txt

# Check for open S3 buckets
aws s3 ls s3://target-bucket --no-sign-request

# Check cloud metadata (if you have SSRF)
curl http://169.254.169.254/latest/meta-data/  # AWS
curl -H "Metadata:true" http://169.254.169.254/metadata/instance?api-version=2020-06-01  # Azure
curl -H "Metadata-Flavor: Google" http://metadata.google.internal/  # GCP
```

---

## Phase 2: VULNERABILITY SCANNING

### 2.1 Nuclei Scanning
```bash
# The big chain: subfinder → httpx → nuclei
subfinder -d target.com -silent | httpx -silent | nuclei -t ~/nuclei-templates/

# Targeted scans
nuclei -l live_hosts.txt -t cves/          # Known CVEs
nuclei -l live_hosts.txt -t exposures/     # Exposed files/configs
nuclei -l live_hosts.txt -t misconfiguration/  # Misconfigs
nuclei -l live_hosts.txt -t takeovers/     # Subdomain takeovers
nuclei -l live_hosts.txt -t technologies/  # Tech detection

# Custom template example (YAML)
# Save as my-check.yaml:
# id: custom-admin-panel
# info:
#   name: Admin Panel Detection
#   severity: info
# requests:
#   - method: GET
#     path:
#       - "{{BaseURL}}/admin"
#       - "{{BaseURL}}/administrator"
#     matchers:
#       - type: status
#         status: [200]
```

### 2.2 GitHub Dorking (Secret Hunting)
```
# Search operators for GitHub code search:
org:target "API_KEY"
org:target "AWS_SECRET_ACCESS_KEY"
org:target "password" filename:.env
org:target "BEGIN RSA PRIVATE KEY"
org:target filename:config.json "database"
org:target extension:pem private
org:target "jdbc:mysql://"
org:target "mongodb+srv://"
org:target "AKIA"  # AWS access key prefix
org:target filename:docker-compose.yml "password"
org:target filename:.npmrc "_authToken"

# Automated tools
trufflehog git https://github.com/target/repo --only-verified
gitleaks detect --source=/path/to/repo
```

**Key insight**: Even if devs delete secrets, they persist in git history. Always check commit history.
**Filter out false positives**: test dirs, example files, locale/l10n files, security rule test files.

---

## Phase 3: EXPLOITATION TECHNIQUES

### 3.1 Subdomain Takeover
**What**: DNS record points to a service (S3, Heroku, Azure, etc.) that's been deleted/unclaimed.
**Impact**: Phishing, cookie theft, malicious content under trusted domain.
**Bounty range**: $200-$2,000+

**How to find**:
1. Enumerate all subdomains
2. Check for CNAME records pointing to third-party services
3. Verify the service is unclaimed (404, default page, etc.)
4. Attempt to claim the service

**Common vulnerable services**: GitHub Pages, Heroku, AWS S3, Azure, Shopify, Fastly, Pantheon, Tumblr, WordPress.com, Zendesk, Unbounce, Surge.sh

**Tools**: `subjack`, `can-i-take-over-xyz`, nuclei takeover templates

### 3.2 SSRF (Server-Side Request Forgery)
**What**: Force server to make requests to internal/unintended resources.
**Impact**: Cloud metadata theft, internal network scan, RCE.
**Bounty range**: $500-$25,000+ (HackerOne paid $25K for SSRF exposing AWS creds)

**Where to look**:
- URL parameters: `url=`, `link=`, `src=`, `redirect=`, `uri=`, `path=`, `dest=`
- File upload (SVG, XML, PDF generation)
- Webhook URLs
- Import/export features
- PDF generators (inject `<iframe>`)

**Payloads**:
```
# AWS metadata
http://169.254.169.254/latest/meta-data/iam/security-credentials/
http://169.254.169.254/latest/user-data

# Bypass filters
http://0177.0.0.1/       # Octal
http://2130706433/        # Decimal
http://0x7f000001/        # Hex
http://[::1]/             # IPv6
http://127.1/             # Shortened
http://127.0.0.1.nip.io/  # DNS rebinding
```

### 3.3 IDOR (Insecure Direct Object Reference)
**What**: Access other users' data by manipulating IDs.
**Impact**: Data breach, account takeover.
**Bounty range**: $500-$10,000+

**Where to look**:
- Any endpoint with user IDs, order IDs, file IDs
- API endpoints: `/api/v1/users/123` → try `/api/v1/users/124`
- Download/export features
- Delete operations
- Password reset flows

**Advanced techniques**:
- Change HTTP methods (GET→POST→PUT→DELETE)
- Array parameters: `id[]=123&id[]=124`
- Replace "me" or "current" with numeric IDs
- Try older API versions: `/api/v1/` vs `/api/v2/`
- Check mobile API endpoints (less protected)
- Parameter pollution: `id=123&id=124`
- UUID leak: check profile pages, emails, sharing links for UUIDs
- JWT manipulation: decode JWT, change user_id claim
- GraphQL: query with different user's ID argument

### 3.4 XSS (Cross-Site Scripting)
**What**: Execute JavaScript in victim's browser.
**Impact**: Session hijacking, account takeover, phishing.
**Bounty range**: $150-$5,000+ (Blind XSS can pay $250K+)

**Types**:
- **Stored XSS**: Payload persists (comments, profiles) — highest value
- **Reflected XSS**: Payload in URL parameters
- **DOM XSS**: Client-side JS processes input unsafely
- **Blind XSS**: Fires in admin panels, internal tools

**WAF Bypass Payloads**:
```html
<img src=x onerror=alert(1)>
<svg/onload=alert(1)>
<math><mtext><table><mglyph><style><!--</style><img src onerror=alert(1)>
"><img src=x onerror=prompt(1)>
javascript:alert(1)// (in href attributes)
<details open ontoggle=alert(1)>
<body onload=alert(1)>
```

**WAF bypass techniques**:
- Case variation: `sCrIpT`
- URL encoding: `%3Cscript%3E`
- Double encoding: `%253Cscript%253E`
- Unicode: `\u003cscript\u003e`
- HTML entities: `&#60;script&#62;`
- Payload fragmentation across parameters

### 3.5 OAuth & Authentication Flaws
**What**: Misconfigured OAuth flows leading to account takeover.
**Impact**: Full account compromise.
**Bounty range**: $1,000-$15,000+

**What to test**:
- `redirect_uri` manipulation (open redirect → token theft)
- Missing `state` parameter (CSRF in OAuth)
- Token reuse across applications
- Pre-account takeover (register email before victim uses OAuth)
- Check `/.well-known/openid-configuration` for config leaks
- Consent phishing via malicious OAuth apps

### 3.6 API Security
**What**: Broken access control, excessive data exposure, rate limiting bypass.
**Impact**: Data breach, privilege escalation.

**What to test**:
- **BOLA/IDOR**: Change object IDs in API calls
- **Broken Authentication**: Missing auth on endpoints
- **Excessive Data Exposure**: API returns more data than UI shows
- **Rate Limiting**: Bypass with IP rotation, headers
- **Mass Assignment**: Add extra fields in POST/PUT requests
- **GraphQL Introspection**: Query `{__schema{types{name fields{name}}}}` in production
- **BFLA**: Access admin endpoints as regular user

---

## Phase 4: REPORT WRITING (Get Paid Faster)

### Template:
```
## Title
[Vuln Type] in [Component] - [Impact Summary]
e.g., "SSRF in PDF Generation Leading to AWS Metadata Exposure"

## Summary
One paragraph: what, where, impact.

## Steps to Reproduce
1. Navigate to https://...
2. Intercept request with Burp Suite
3. Modify parameter X to Y
4. Observe: [what happens]

## Proof of Concept
- Screenshots
- HTTP request/response
- Video walkthrough (highly recommended)

## Impact
- What can an attacker do?
- Business impact (data breach, financial, reputation)
- CVSS score justification

## Remediation
- Specific, actionable fix recommendations
```

### Pro Tips:
- **Video PoC** = faster triage, higher bounty
- **Clear impact** = justify severity, get higher payout
- **Business context** = "this leaks PII of all users" > "parameter can be changed"
- **One vuln per report** = unless they chain
- **Check program scope** before reporting
- **Professional tone** = builds relationship with team
- **Test with clean browser** = ensure repro steps work

---

## Phase 5: AUTOMATION PIPELINE

### The Ideal Chain:
```
subfinder → httpx → nuclei → Burp Suite (manual)
     ↓
  dnsgen/altdns (permutations)
     ↓
  ffuf (path fuzzing)
     ↓
  katana/gau (content discovery)
     ↓
  linkfinder (JS endpoint extraction)
     ↓
  trufflehog/gitleaks (secret scanning)
```

### Continuous Monitoring:
- Run recon weekly via cron
- Monitor for new subdomains
- Alert on changes to assets
- Scan new CVEs against known assets

---

## High-Value Target Selection

| Program | Platform | Max Bounty | Best Attack Surface |
|---------|----------|-----------|-------------------|
| Shopify | HackerOne | $50,000 | *.shopify.com — massive scope |
| HashiCorp | HackerOne | $25,000 | Cloud infrastructure tools |
| Automattic | HackerOne | $25,000 | WordPress ecosystem |
| GitLab | HackerOne | $20,000 | CI/CD, source code |
| Elastic | HackerOne | $10,000 | Search/analytics |
| Brave | HackerOne | $10,000 | Browser, crypto |
| Nextcloud | HackerOne | $10,000 | Self-hosted cloud |
| Mapbox | HackerOne | $10,000 | Maps/location APIs |
| Mattermost | HackerOne | $5,000 | Messaging platform |
| Sentry | HackerOne | $5,000 | Error tracking |
| Postman | HackerOne | $3,000 | API tooling |
| Discourse | HackerOne | $2,048 | Forum software (SUSPENDED until Apr 2026) |

### Strategy: Pick ONE program, go DEEP.
Don't spread thin across many programs. Master one target's architecture, API patterns, and technology stack.

---

## Quick Reference: Bounty-Worthy Findings by Severity

### Critical ($2,000-$50,000+)
- RCE (Remote Code Execution)
- SQL Injection with data exfiltration
- SSRF exposing cloud credentials
- Authentication bypass
- Account takeover chains

### High ($1,000-$10,000)
- Stored XSS in privileged contexts
- IDOR exposing sensitive data
- OAuth account takeover
- Privilege escalation
- API key leaks (verified active)

### Medium ($200-$2,000)
- Subdomain takeover
- Reflected XSS
- CSRF on sensitive actions
- Rate limiting bypass on auth endpoints
- Information disclosure

### Low ($50-$500)
- Open redirect
- Missing security headers
- Self-XSS
- Verbose error messages
- Minor information disclosure

---

## Tools to Install

### Essential:
- **Subfinder** — subdomain enumeration
- **httpx** — HTTP probing
- **Nuclei** — template-based scanning
- **ffuf** — web fuzzing
- **Burp Suite Community** — intercepting proxy
- **gau** — wayback URL extraction
- **katana** — web crawling
- **trufflehog** — secret scanning
- **gitleaks** — git secret scanning
- **LinkFinder** — JS endpoint extraction

### Nice to Have:
- **Amass** — comprehensive subdomain enum
- **Arjun** — parameter discovery
- **Dalfox** — XSS scanning
- **SQLMap** — SQL injection
- **cloud_enum** — cloud bucket/resource enum
- **subjack** — subdomain takeover checker
- **dirsearch** — directory brute-force
