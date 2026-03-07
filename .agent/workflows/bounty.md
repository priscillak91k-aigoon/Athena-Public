---
description: Boot bug bounty hunting mode — full recon-to-report pipeline
---

// turbo-all

# /bounty — Bug Bounty Hunt Mode

> **Purpose**: Structured bounty hunting with maximum efficiency.
> **Knowledge**: `.context/BOUNTY_PLAYBOOK.md` — technique bible (ALWAYS read first)
> **Operations**: `bounty_ops/` — scan data, scripts, findings (gitignored)

## Phase 1: Load Context

- [ ] Read `.context/BOUNTY_PLAYBOOK.md` — techniques, payloads, report templates
- [ ] Create `bounty_ops/` directory if not exists
- [ ] Check `bounty_ops/` for existing scan data and previous findings
- [ ] Check `bounty_ops/hunt_log.md` for past sessions and open leads

## Phase 2: Target Selection

// turbo

- [ ] Ask the user: **"Which target?"** Options:
  - A specific company/domain (e.g., `shopify.com`)
  - A specific bounty platform program (e.g., "Shopify on HackerOne")
  - "Continue" — resume from last session's leads
  - "Fresh scan" — run full recon on a new target from the target list

- [ ] If target selected, verify the bounty program is ACTIVE (not suspended/paused)
- [ ] Note the program's scope, max bounty, and any special rules

## Phase 3: Execute Attack Pipeline

The pipeline has 5 stages. Work through them in order:

### Stage 1: Recon (`/recon <target>`)
```
subfinder → httpx → content discovery → JS analysis → GitHub dorking
```
- [ ] Run subdomain enumeration
- [ ] Probe live hosts
- [ ] Extract JS endpoints
- [ ] Run GitHub dorks against target org
- [ ] Check Wayback Machine for old endpoints

### Stage 2: Scan
```
nuclei → custom checks → manual review
```
- [ ] Run nuclei templates against live hosts (if nuclei installed)
- [ ] Check for subdomain takeovers (dangling DNS)
- [ ] Check for exposed configs/files (.env, .git, admin panels)
- [ ] Check cloud resources (S3 buckets, etc.)

### Stage 3: Exploit
- [ ] Test top findings manually
- [ ] For SSRF: try cloud metadata endpoints
- [ ] For IDOR: swap user IDs, check access control
- [ ] For XSS: test input fields, URL parameters
- [ ] For OAuth: check redirect_uri handling

### Stage 4: Verify
- [ ] Confirm vulnerability is real (not false positive)
- [ ] Document reproduction steps
- [ ] Take screenshots/recordings as evidence
- [ ] Assess impact and CVSS score

### Stage 5: Report
- [ ] Draft report using template from BOUNTY_PLAYBOOK.md
- [ ] Include: title, summary, repro steps, PoC, impact, remediation
- [ ] Submit via HackerOne (or other platform)
- [ ] Save draft/confirmation screenshot

## Phase 4: Save State

- [ ] Save all findings to `bounty_ops/`
- [ ] Update `bounty_ops/hunt_log.md` with session summary and open leads
- [ ] Note any leads to follow up on next session

## Output:

```
🎯 BOUNTY HUNT MODE — ACTIVE
   Playbook: .context/BOUNTY_PLAYBOOK.md
   Ops Dir:  bounty_ops/
   Git: BLOCKED (gitignored)
   
   Pipeline: Recon → Scan → Exploit → Verify → Report
```

---

## Quick Reference: What Makes a Finding Worth Reporting

| Finding | Worth It? | Typical Bounty |
|---------|-----------|---------------|
| RCE | 🔥 ALWAYS | $5,000-$50,000+ |
| SSRF → cloud creds | 🔥 ALWAYS | $2,000-$25,000 |
| SQL injection | 🔥 ALWAYS | $2,000-$15,000 |
| Account takeover | 🔥 ALWAYS | $1,000-$10,000 |
| IDOR (sensitive data) | ✅ YES | $500-$5,000 |
| Stored XSS | ✅ YES | $200-$3,000 |
| Subdomain takeover | ✅ YES | $200-$2,000 |
| Reflected XSS | ⚠️ MAYBE | $100-$500 |
| Open redirect | ⚠️ Only if chainable | $50-$200 |
| Missing headers | ❌ Usually N/A | Not accepted |
| Self-XSS | ❌ NO | Not accepted |

---

# workflow #bounty #hunting #security
