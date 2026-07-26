# Report Templates — Phases 1, 2 and 3

Use these exact formats. Fill placeholders `<...>` with real values.

---

## Phase 1 — Analysis summary (print to console)

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <language>
Framework:     <framework + version>
Dependencies:  <key deps>
Domain:        <business domain + main entities>
Architecture:  <monolithic | partially separated | organized MVC — one line why>
Source files:  <N> files analyzed
DB tables:     <table1, table2, ...>
================================
```

---

## Phase 2 — Architecture Audit Report (save to reports/audit-project-N.md)

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: <project name>
Stack:   <language + framework>
Files:   <N> analyzed | ~<L> lines of code

Summary
CRITICAL: <c> | HIGH: <h> | MEDIUM: <m> | LOW: <l>

Findings
```

Then one block per finding, ordered CRITICAL → HIGH → MEDIUM → LOW:

```
[<SEVERITY>] <Finding title>
File: <file>:<line or line-range>
Description: <what is wrong, concretely>
Impact: <why it matters>
Recommendation: <the fix, actionable>
```

Close with:

```
================================
Total: <total> findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

**Rules:** every finding cites `file:line`. At least 5 findings, at least one
CRITICAL or HIGH. The deprecated-API check must appear if any is found. STOP after
printing and wait for `y`.

---

## Phase 3 — Refactoring complete (print to console)

```
================================
PHASE 3: REFACTORING COMPLETE
================================
New Project Structure:
<tree of the new src/ layout>

Validation
  ✓ Application boots without errors        (<how it was checked>)
  ✓ All endpoints respond correctly         (<which endpoints, how>)
  ✓ Zero catalog anti-patterns remaining
================================
```

If a check fails, mark it `✗` with the reason instead of claiming success.
