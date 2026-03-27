---
name: milestone-review
description: Review a milestone or stage outcome at a higher level than a single code diff, focusing on completion status, remaining gaps, validation strength, contract adherence, and handoff readiness.
---

# milestone-review

## Purpose

Use this skill when a stage or milestone is believed to be complete, partially complete, or ready for handoff.

This skill is higher-level than PR review.
It evaluates whether the milestone outcome is strong enough to:
- close
- close with limitations
- remain open
- stop pending more evidence

---

## When to use

Use this skill when:
- a milestone closeout is being prepared
- several issues are already finished and someone wants a stage-level verdict
- the code may be “done enough” but the project meaning is still uncertain
- handoff quality matters

Do not use this skill as a substitute for code review on a specific diff.

---

## Inputs

Prefer these inputs:

1. `docs/plan/plan_stageX.md`
2. `docs/plan/issue_stageX.md`
3. `docs/contracts/contract_freeze*.md`
4. `docs/handoff/milestone_closeout*.md`
5. issue reports / PR summaries
6. relevant validation evidence
7. `docs/review/code_review.md` if available

---

## Required behavior

You must assess:

1. milestone goal completion
2. deliverable completeness
3. validation strength
4. remaining gaps
5. contract adherence
6. risk visibility
7. next-stage entry readiness

You must not:
- confuse “lots of activity” with “milestone complete”
- assume that passing local checks proves milestone success
- ignore unresolved semantic uncertainty
- mark handoff-ready if the next person would still need to rediscover the real state manually

---

## Output structure

Your review should include:

### 1. Overall verdict
- close
- close with limitations
- keep open
- stop / not reliable yet

### 2. Completion status
- what is truly done
- what is still missing

### 3. Validation assessment
- what current validation proves
- what it does not prove
- whether evidence is adequate for stage closure

### 4. Contract assessment
- whether execution stayed within the frozen boundary
- whether any freeze-level issue appeared

### 5. Risk summary
- blocking risks
- serious but non-blocking risks
- lower-priority risks

### 6. Handoff readiness
- can the next stage start cleanly?
- what should be read first?
- what must be decided before more coding?

### 7. Recommended next action
- close now
- close after one last targeted validation
- keep open until a gap is fixed
- revise milestone framing before continuing

---

## Suggested workflow

1. read the stage plan
2. read issue breakdown
3. read contract freeze
4. read milestone closeout draft if present
5. compare actual outputs against planned deliverables
6. assess validation honestly
7. judge whether the milestone is truly handoff-ready
8. produce a structured verdict

---

## Quality bar

A good milestone review should:
- save future humans from rediscovering milestone reality
- separate completed work from assumed completion
- expose hidden risk before the next stage begins
- help decide whether to close, continue, or freeze again

A weak milestone review will usually:
- summarize activity instead of judging completion
- treat code existence as proof of milestone success
- ignore handoff quality
- hide ambiguity behind optimistic language
