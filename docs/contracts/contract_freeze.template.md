# contract_freeze

## Contract Title

- Contract ID:
- Related stage / milestone:
- Status:
  - [ ] proposed
  - [ ] frozen
  - [ ] revised
  - [ ] retired
- Owner:
- Last updated:

## 1. Purpose

This contract freeze exists to lock the current working boundary for this stage.

Its purpose is to prevent:
- silent scope drift
- accidental interface changes
- semantic changes hidden inside “small implementation tweaks”
- repeated redesign during an execution phase

This document is not a full design spec.
It is a boundary document.

---

## 2. What This Contract Covers

List the area that is frozen in this stage.

Examples:
- module interfaces
- file responsibilities
- data flow
- config semantics
- evaluation meaning
- experiment assumptions
- input/output definitions
- milestone deliverable boundaries

Current contract scope:
- item 1:
- item 2:
- item 3:

---

## 3. Frozen Objectives

The following goals are fixed for this stage:

- Objective 1:
- Objective 2:
- Objective 3:

These objectives must not be reinterpreted during normal implementation work.

If execution reveals they are no longer valid, stop and report instead of redefining them silently.

---

## 4. Frozen Inputs / Outputs

Define the stable meaning of inputs and outputs in this stage.

### Inputs
- Input A:
  - source:
  - expected form:
  - meaning:
- Input B:
  - source:
  - expected form:
  - meaning:

### Outputs
- Output A:
  - location / API / artifact:
  - expected form:
  - meaning:
- Output B:
  - location / API / artifact:
  - expected form:
  - meaning:

If an implementation needs to change any of the above, it must trigger a freeze review.

---

## 5. Frozen Interfaces

List interfaces that must remain stable during this stage.

Examples:
- function signatures
- config keys
- file layout
- schema fields
- command-line behavior
- evaluation output columns

Frozen interfaces:
- Interface 1:
- Interface 2:
- Interface 3:

Allowed tolerance:
- minor internal refactor that preserves interface meaning
- doc clarification without semantic change
- non-breaking validation additions

Not allowed:
- renaming without approval
- silent semantic drift
- hidden behavior changes behind the same interface

---

## 6. Allowed Change Window

The following changes are allowed within this frozen stage:

- implementation detail improvements that do not change semantics
- focused bug fixes that restore intended behavior
- additional tests / validation
- documentation sync
- narrow refactors that preserve interfaces and outputs

Project-specific allowed changes:
- Allowed change 1:
- Allowed change 2:

This section is important:
it tells agents where they still have execution freedom.

---

## 7. Explicitly Forbidden Changes

The following changes must not be made during this stage without explicit approval:

- Forbidden change 1:
- Forbidden change 2:
- Forbidden change 3:

Common examples:
- redesigning architecture mid-stage
- changing output meaning
- changing evaluation criteria
- changing stable config semantics
- moving major directories
- adding major dependencies
- reinterpreting milestone goals

---

## 8. Validation Contract

The following validation expectations are frozen for this stage:

- required local checks:
- required focused tests:
- required manual sanity checks:
- optional broader checks:

A task cannot be called complete if it violates these minimum validation expectations.

---

## 9. Stop Conditions

If any of the following happen, stop and report:

- the implementation cannot proceed without changing a frozen interface
- validation evidence contradicts the frozen objective
- the requested task implies scope expansion beyond this contract
- missing upstream dependency makes the contract impossible to honor
- semantic correctness becomes uncertain in a way that tests do not catch

Project-specific stop conditions:
- Stop condition 1:
- Stop condition 2:

---

## 10. Change Control

If someone believes this contract must change, do not silently edit code first.

Use this process:

1. identify the exact frozen item that is no longer viable
2. explain why it blocks execution or correctness
3. propose the smallest necessary revision
4. obtain human approval
5. update this contract explicitly before continuing

Normal implementation work must not bypass this process.

---

## 11. Linked Documents

Relevant docs:
- `docs/ai/PROJECT_CONTEXT.md`
- `docs/plan/...`
- `docs/review/code_review.md`

Project-specific links:
- `...`
- `...`

---

## 12. Freeze Review Notes

Use this section to track boundary decisions over time.

### Review entry
- date:
- requested by:
- issue:
- proposed change:
- decision:
- rationale:

Add one entry per boundary-level change request.
