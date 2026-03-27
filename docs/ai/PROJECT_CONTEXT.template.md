# PROJECT_CONTEXT

## 1. Project Summary

- Project name:
- Project type:
  - [ ] research
  - [ ] product
  - [ ] coursework
  - [ ] prototype
  - [ ] infrastructure
- One-sentence description:
- Primary language / stack:

## 2. Current Phase

- Current milestone / stage:
- Why this stage exists:
- What this stage should prove or deliver:
- What is explicitly out of scope in this stage:

## 3. High-Level Goal

Describe the high-level goal in 3–8 lines.

Focus on:
- what success looks like
- what the system is supposed to achieve
- what matters more: correctness / speed / reproducibility / demoability / extensibility / research validity

## 4. Human-Owned Decisions

These areas are owned by the human and should not be changed by agents without approval:

- research / product direction:
- milestone boundaries:
- contract freeze:
- evaluation criteria:
- release / submission decisions:
- public API / external commitments:

## 5. Agent-Owned Execution Scope

Agents are expected to help with:

- code implementation
- refactor within approved scope
- tests / validation
- local documentation sync
- issue-level execution
- milestone-level closeout drafting

Agents are not expected to decide:

- whether the overall direction is correct
- whether a failed result invalidates the project hypothesis
- whether to expand scope
- whether to change the meaning of success

## 6. Project Constraints

List durable constraints here.

Examples:
- do not change stable file layout without approval
- prefer minimal viable implementation before optimization
- keep configs explicit and reproducible
- avoid adding dependencies unless justified
- prioritize readable diffs over clever rewrites

Project-specific constraints:
- Constraint 1:
- Constraint 2:
- Constraint 3:

## 7. Success Criteria for This Phase

A phase is considered successful when:

- [ ] Deliverable 1:
- [ ] Deliverable 2:
- [ ] Deliverable 3:

Optional quantitative gates:
- metric / threshold:
- runtime / cost budget:
- reproducibility requirement:

## 8. Stop Conditions

If any of these happen, the agent should stop and report instead of pushing forward:

- Stop condition 1:
- Stop condition 2:
- Stop condition 3:

Examples:
- validation results contradict task assumptions
- required files or configs are missing
- proposed change would violate contract freeze
- implementation requires unapproved dependency or architecture change

## 9. Important Files and Docs

Core files:
- `...`
- `...`

Planning docs:
- `...`
- `...`

Contracts / review docs:
- `...`
- `...`

## 10. Reporting Preference

When reporting progress, prefer this style:

- concise factual summary
- changed files first
- validation second
- open risks last
- do not overclaim certainty
