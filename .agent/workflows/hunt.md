---
description: Active vulnerability hunting on a target — exploit and verify findings
---

// turbo-all

# /hunt — Active Vulnerability Hunting

> **Purpose**: Hands-on exploitation and verification of leads from recon.
> **Prerequisite**: Run `/recon` first or have existing findings in `bounty_ops/`.
> **Reference**: `.context/BOUNTY_PLAYBOOK.md` — techniques and payloads.

## Phase 1: Load Leads

// turbo

- [ ] Check `bounty_ops/` for recon results and previous findings
- [ ] Read `bounty_ops/hunt_log.md` for open leads
- [ ] List all leads sorted by severity: Critical → High → Medium
- [ ] Ask user which leads to pursue, or auto-pick highest severity

## Phase 2: Attack Execution

Work through leads in priority order. For each lead, apply the appropriate technique:

### If: 403 Forbidden Endpoints
```
Path manipulation: /path/, /path/., /path//, /path..;/, /path%00
Header bypass: X-Original-URL, X-Forwarded-For: 127.0.0.1, X-Real-IP: 127.0.0.1
Method switching: GET → POST → PUT → OPTIONS
Encoding: URL encode, double encode, Unicode
```
- [ ] Create and run `bounty_ops/bypass_403.py` against target endpoints

### If: Potential Subdomain Takeover
```
1. Verify CNAME record points to unclaimed service
2. Attempt to claim the service
3. Host proof-of-concept content
4. Take screenshots as evidence
```
- [ ] Verify DNS records
- [ ] Check if service is claimable
- [ ] Document with screenshots

### If: Exposed API/Endpoints
```
1. Test for authentication bypass (access without token)
2. Test for IDOR (swap user IDs, object IDs)
3. Test for SSRF (internal IP payloads, cloud metadata)
4. Test for injection (SQL, command, template)
5. Test for excessive data exposure (compare API response vs UI)
```
- [ ] Use requests library to probe endpoints
- [ ] Document all non-standard responses

### If: GitHub Secret Leak
```
1. Verify the secret is actually valid (carefully!)
2. Check if it has elevated permissions
3. Document the repository, file, and commit
4. Do NOT use the secret for anything beyond verification
```
- [ ] Verify secret validity
- [ ] Assess scope of access

### If: JavaScript Endpoint Discovery
```
1. Extract all API endpoints from JS files
2. Test each for: auth bypass, IDOR, SSRF, param injection
3. Check for hardcoded API keys or tokens
4. Test deprecated API versions (v1 vs v2)
```
- [ ] Run endpoint extraction
- [ ] Test each discovered endpoint

### If: GraphQL Endpoint
```
1. Try introspection: {__schema{types{name fields{name}}}}
2. If introspection enabled → map full schema
3. Test mutations for access control
4. Test for nested query DoS
5. Check batch operations for IDOR
```
- [ ] Test introspection query
- [ ] Map accessible queries/mutations

## Phase 3: Verify & Document

// turbo

For each confirmed finding:
- [ ] Reproduce from scratch in clean browser/session
- [ ] Take screenshots at each step
- [ ] Record exact HTTP requests/responses
- [ ] Calculate CVSS score
- [ ] Write impact statement

## Phase 4: Report or Escalate

- [ ] If confirmed → draft HackerOne report (use BOUNTY_PLAYBOOK.md template)
- [ ] If needs more work → save as lead in `bounty_ops/hunt_log.md`
- [ ] If false positive → document why and move to next lead

## Phase 5: Update Hunt Log

- [ ] Update `bounty_ops/hunt_log.md` with:
  - Leads investigated and outcomes
  - Reports submitted (with HackerOne IDs)
  - Open leads for next session

```
🔫 HUNT RESULTS
   Leads investigated: X
   Confirmed findings: Y
   Reports drafted: Z
   Leads for next session: W
```

---

# workflow #hunt #exploit #verify #bounty
