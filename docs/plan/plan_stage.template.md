# plan_stageX

## Stage Title

- Stage ID:
- Stage name:
- Suggested branch family:
- Status:
  - [ ] draft
  - [ ] active
  - [ ] frozen
  - [ ] complete

---

## 1. Background

Describe why this stage exists.

Answer:
- what happened before this stage
- what gap remains
- why now is the right time to do this stage

Keep this section short but concrete.

---

## 2. Goal

State the single core goal of this stage.

Good examples:
- establish the minimum runnable pipeline
- align implementation with a frozen contract
- add evaluation closure for an existing baseline
- prepare handoff-quality artifacts for next milestone

Avoid multi-goal stages unless absolutely necessary.

---

## 3. In Scope

List only what this stage is supposed to include.

- [ ] item 1
- [ ] item 2
- [ ] item 3

Use concrete deliverables, not vague ambitions.

---

## 4. Out of Scope

List what this stage must not absorb.

- [ ] item 1
- [ ] item 2
- [ ] item 3

This section is mandatory.
It protects the stage from uncontrolled expansion.

---

## 5. Inputs and Dependencies

Required upstream inputs:

- docs:
- configs:
- code modules:
- datasets / assets:
- previous milestone outputs:

Blocking dependencies:
- dependency 1
- dependency 2

---

## 6. Proposed Issue Breakdown

### Issue X.1
- Title:
- Goal:
- Main files / directories:
- Expected output:

### Issue X.2
- Title:
- Goal:
- Main files / directories:
- Expected output:

### Issue X.3
- Title:
- Goal:
- Main files / directories:
- Expected output:

Add or remove issues as needed, but keep them independently reviewable.

---

## 7. Deliverables

At the end of this stage, the repository should contain:

- [ ] deliverable 1
- [ ] deliverable 2
- [ ] deliverable 3

Possible deliverables:
- runnable code
- config file
- test / validation script
- benchmark report
- doc update
- closeout note

---

## 8. Acceptance Criteria

This stage is accepted only if:

- [ ] acceptance check 1
- [ ] acceptance check 2
- [ ] acceptance check 3

Each acceptance criterion should be externally checkable.

Bad:
- “looks good”
- “more complete”

Good:
- “script X runs successfully”
- “doc Y matches current behavior”
- “metric Z is reported with command and source”

---

## 9. Validation Plan

Minimum validation for this stage:

- local checks:
- focused tests:
- manual sanity checks:
- optional full-suite checks:

For each deliverable, specify what evidence will count as validation.

---

## 10. Risks

Main risks in this stage:

- Risk 1:
- Risk 2:
- Risk 3:

For each risk, optionally note:
- trigger
- likely impact
- mitigation

---

## 11. Stop Conditions

If any of these happen, stop and report:

- stop condition 1
- stop condition 2
- stop condition 3

Examples:
- required dependency is missing
- implementation would violate frozen interface
- validation evidence conflicts with intended semantics
- scope expansion becomes unavoidable

---

## 12. Handoff Note

At stage close, produce or update:

- closeout summary:
- key changed files:
- open problems:
- suggested next stage entry point:
