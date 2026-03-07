---
description: Run full reconnaissance on a target domain for bug bounty hunting
---

// turbo-all

# /recon — Target Reconnaissance Pipeline

> **Purpose**: Automated recon pipeline for a single target domain.
> **Usage**: `/recon shopify.com` or `/recon <target>`
> **Reference**: `.context/BOUNTY_PLAYBOOK.md` for techniques
> **Output**: `bounty_ops/recon_<target>_<timestamp>.json`

## Phase 1: Setup

// turbo

- [ ] Create `bounty_ops/` directory if not exists
- [ ] Read `.context/BOUNTY_PLAYBOOK.md` Phase 1 (Reconnaissance)
- [ ] Create a Python recon script in `bounty_ops/`

## Phase 2: Subdomain Enumeration

### DNS & Subdomain Discovery
```python
# Use multiple sources:
# 1. crt.sh (Certificate Transparency logs) — free, no API key
# 2. DNS brute-force against common subdomain wordlist
# 3. Web archive (Wayback Machine) for historical subdomains
# 4. Check for CNAME records pointing to third-party services
```

### Live Host Probing
```python
# For each discovered subdomain:
# 1. Resolve DNS (A, AAAA, CNAME records)
# 2. HTTP probe (check if it responds on 80/443)
# 3. Grab response headers, title, status code
# 4. Detect technology stack from headers
# 5. Flag interesting status codes: 200, 301, 403 (potential bypass), 500
```

### Content Discovery
```python
# For each live host:
# 1. Check common sensitive paths: /.env, /.git/config, /admin, /api,
#    /actuator/env, /swagger-ui.html, /graphql, /.well-known/
# 2. Check robots.txt and sitemap.xml for hidden paths
# 3. Check for directory listing
# 4. Look for API documentation endpoints
```

## Phase 3: GitHub Dorking

// turbo

- [ ] Search GitHub for the target organization:
  - `org:<target> "API_KEY"`
  - `org:<target> "password" filename:.env`
  - `org:<target> "AWS_SECRET" OR "AKIA"`
  - `org:<target> "BEGIN RSA PRIVATE KEY"`
  - `org:<target> filename:docker-compose.yml password`
  - `org:<target> "mongodb+srv://" OR "jdbc:mysql://"`

- [ ] Filter: skip test dirs, example files, locale files, security test rules
- [ ] Verify any potential secrets are actually live/valid before reporting

## Phase 4: Subdomain Takeover Check

// turbo

- [ ] For each CNAME record found:
  - Check if the target service still exists
  - Known vulnerable: GitHub Pages, Heroku, AWS S3, Azure, Shopify, Fastly, Surge.sh
  - Flag any returning 404, "NoSuchBucket", default parking pages, or SSL mismatch

## Phase 5: Cloud Asset Check

// turbo

- [ ] Check for publicly accessible cloud resources:
  - S3 buckets: `<target>`, `<target>-dev`, `<target>-staging`, `<target>-backup`
  - GCS buckets: same naming patterns
  - Azure blobs: `<target>.blob.core.windows.net`

## Phase 6: Output & Triage

// turbo

- [ ] Save results to `bounty_ops/recon_<target>_<timestamp>.json`
- [ ] Generate triage summary:
  - **Critical**: Live secrets, exposed credentials, open admin panels
  - **High**: Subdomain takeovers, interesting 403s, unauthed API endpoints
  - **Medium**: Exposed configs, verbose error pages, debug endpoints
  - **Low**: Information disclosure, missing headers
- [ ] Update `bounty_ops/hunt_log.md` with findings
- [ ] Suggest next steps → `/hunt` to exploit leads

```
📡 RECON COMPLETE — <target>
   Subdomains found: X
   Live hosts: Y
   Findings: Z (Critical: A, High: B, Medium: C, Low: D)
   
   Top leads:
   1. [CRITICAL] ...
   2. [HIGH] ...
   3. [MEDIUM] ...
   
   Next: /hunt to exploit these leads
```

---

# workflow #recon #enumeration #bounty
