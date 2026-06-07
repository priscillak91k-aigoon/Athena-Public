// turbo-all

---
description: Adversarial convergence audit — recursive zero-point review until mathematically clean
created: 2026-06-08
last_updated: 2026-06-08
---

// turbo-all

# /audit — Adversarial Convergence Audit

> **Bundles**: `/ultrathink` + `/think` + `/search` + `/research` + `/due-diligence`
> **Purpose**: Tear apart whatever you just built. Keep iterating until zero defects remain.
> **Philosophy**: Ship nothing that hasn't survived its own funeral.

---

## Core Principles

| Principle | Rule |
|-----------|------|
| **Anti-Spaghettification** | Every component must have exactly ONE job. If a function does two things, split it. If a file has mixed concerns, refactor it. |
| **Reliability** | Every failure mode must be handled explicitly. No silent swallows, no bare `except`, no "it'll probably be fine". |
| **Robustness** | The system must survive: bad input, missing dependencies, concurrent access, power loss, network drops, and user stupidity. |

---

// turbo-all

## Behaviour

When `/audit` is invoked, activate **recursive adversarial convergence mode**:

### Phase 1: Structural Integrity Scan

- [ ] **Read every file** touched in the current task
- [ ] **Dependency Audit**: Are all imports/packages real and pinned? Will they resolve on the target architecture (ARM64/x86)?
- [ ] **Separation of Concerns**: Does each file/function/class have exactly ONE responsibility?
- [ ] **Dead Code**: Is there anything that does nothing? Remove it.
- [ ] **Naming**: Are variable/function/file names self-documenting? Could a stranger read this cold?

### Phase 2: Failure Mode Enumeration

- [ ] **Input Validation**: What happens with null, empty, malformed, or adversarial input?
- [ ] **Concurrency**: Can two processes read/write the same resource simultaneously? (Race conditions, file locks, atomic writes)
- [ ] **Network**: What happens if the network drops mid-operation?
- [ ] **Disk**: What happens if the disk is full, the file is missing, or permissions are wrong?
- [ ] **Dependencies**: What happens if an external service (API, database, container) is down?
- [ ] **State Corruption**: What happens if the state file is manually edited, truncated, or deleted?

### Phase 3: Biological/Domain Accuracy (If Applicable)

- [ ] **Web Search**: Verify all domain-specific claims against current, authoritative sources
- [ ] **Cross-Reference**: Do at least 3 independent sources agree?
- [ ] **Recency**: Is the information current, or has it been superseded?

### Phase 4: Infrastructure & Deployment Audit

- [ ] **Docker**: Are all images real, tagged properly, and available for the target arch?
- [ ] **Volumes**: Are bind mounts correct? Will Docker auto-create directories as root and brick rootless containers?
- [ ] **Ports**: Any conflicts with existing services?
- [ ] **Permissions**: UID/GID alignment between host and container?
- [ ] **Persistence**: Does state survive container restart, host reboot, and drive disconnect?
- [ ] **Secrets**: Are credentials hardcoded where they shouldn't be? (Acceptable in air-gapped sovereign infra, flag otherwise)

### Phase 5: The Red Team Fork

- [ ] **Generate Scenario A** (Proponent): Argue that this implementation is correct and complete
- [ ] **Generate Scenario B** (Adversary): Argue that this implementation will fail, and explain exactly how
- [ ] **Adversarial Search**: Query `[component] failure modes`, `[library] known bugs`, `[pattern] anti-patterns`
- [ ] **Resolution**: For every adversarial finding, either fix it or document why it's acceptable

---

// turbo-all

## Convergence Protocol

> [!IMPORTANT]
> **This is the critical difference between `/audit` and running the sub-workflows manually.**
> `/audit` does NOT stop after one pass. It loops.

```
REPEAT:
    1. Run Phases 1-5
    2. Log all findings (fixes applied, issues found, issues dismissed with reasoning)
    3. Apply fixes
    4. Increment pass counter

    IF findings == 0:
        CONVERGE → Output final report
    ELIF pass_counter >= 5:
        HALT → Output report with remaining items flagged as ACCEPTED RISK
    ELSE:
        LOOP → Re-run Phases 1-5 on the modified code
```

### Convergence Output

After convergence, output a structured report:

```markdown
## /audit Convergence Report — Pass [N]

### Findings Fixed
| # | Severity | Description | Fix Applied |
|---|----------|-------------|-------------|

### Accepted Risks
| # | Severity | Description | Reasoning |
|---|----------|-------------|-----------|

### Verdict
[CONVERGED / HALTED AT MAX PASSES]
Confidence: [0-100]%
```

---

// turbo-all

## Stability Controls

| Trigger | Action |
|---------|--------|
| **Zero findings on a pass** | **CONVERGE**. Ship it. |
| **Pass counter ≥ 5** | **HALT**. Report remaining items as accepted risk. Combat Protocol activates — refuse further loops. |
| **Ruin-level finding on any pass** | **ESCALATE**. Stop everything. Report to user before continuing. |
| **User says "ship it"** | **OVERRIDE**. Log current state. Deploy. |

---

// turbo-all

## Anti-Spaghetti Checklist (Mandatory on Every Pass)

- [ ] No function exceeds 50 lines
- [ ] No file has mixed concerns (e.g., UI logic + data persistence)
- [ ] No magic numbers — all constants are named
- [ ] No duplicated logic — DRY or die
- [ ] No nested callbacks deeper than 2 levels
- [ ] No commented-out code left without an explicit `TODO` or `NOTE`
- [ ] Every error path produces a log entry or user-visible message

---

// turbo-all

## When NOT to Use /audit

- Quick one-line fixes (just fix it)
- Exploratory prototypes (use `/vibe` instead)
- Research-only tasks (use `/research`)

## When to Use /audit

- Before deploying ANYTHING to production
- After completing a multi-file feature
- When touching infrastructure (Docker, fstab, networking, permissions)
- When dealing with SOVEREIGN data (health, genetics, finances)
- When Cilla says "make sure this is bulletproof"

---

// turbo-all

## Tagging

#workflow #audit #adversarial #convergence #quality
