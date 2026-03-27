# code_review

## Purpose

This document defines the project-level review expectations.

It is not only about style.
Its primary purpose is to catch:

- scope drift
- contract violations
- missing validation
- doc/config mismatch
- misleading “looks correct but semantically wrong” changes

---

## 1. Scope Review

Check whether the change stays within the intended scope.

Questions:
- Does the diff solve the requested issue or stage objective?
- Did it introduce unrelated cleanup or opportunistic refactors?
- Did it touch files or modules that were not justified?
- Did it silently expand the milestone scope?

Mark:
- [ ] in scope
- [ ] partly out of scope
- [ ] clearly out of scope

---

## 2. Contract / Interface Review

Check whether the change violates any frozen boundary.

Questions:
- Did it change public entrypoints?
- Did it change config semantics?
- Did it alter stable data flow or expected outputs?
- Did it break compatibility with documented behavior?
- Did it violate anything listed in `docs/contracts/`?

Mark:
- [ ] no contract issue found
- [ ] possible contract issue
- [ ] clear contract violation

---

## 3. Validation Review

Check whether the reported validation is adequate.

Questions:
- Were the most relevant checks actually run?
- Was validation proportional to the change impact?
- Were results reported honestly and specifically?
- Is there any unsupported claim like “works” without evidence?

Mark:
- [ ] validation adequate
- [ ] validation incomplete but acceptable
- [ ] validation insufficient

---

## 4. Documentation Sync Review

Check whether repository docs remain aligned with behavior.

Questions:
- Should `README.md` have changed?
- Should any file under `docs/` have changed?
- Did config comments / examples become stale?
- Did usage snippets, scripts, or instructions diverge from reality?

Mark:
- [ ] docs in sync
- [ ] minor doc sync missing
- [ ] significant doc sync missing

---

## 5. Dependency / Configuration Review

Check for hidden repo-wide impact.

Questions:
- Were new dependencies added?
- Were lockfiles changed?
- Were build/test/dev scripts changed?
- Were project-wide configs updated?
- If yes, was the change justified and scoped?

Mark:
- [ ] no concerning repo-wide impact
- [ ] moderate repo-wide impact
- [ ] high repo-wide impact

---

## 6. Semantic Correctness Review

This is the most important section for research / workflow-heavy repos.

Questions:
- Could this change pass tests but still be semantically wrong?
- Did it optimize the wrong target?
- Did it hide a deeper issue by making outputs merely “look better”?
- Does the implementation still reflect the intended meaning of the task?
- Is there any mismatch between metric improvement and actual goal satisfaction?

Mark:
- [ ] semantics look aligned
- [ ] semantics uncertain
- [ ] likely semantic mismatch

---

## 7. Risk Summary

Classify review findings:

### P0
Must stop. Merge should not proceed.

Examples:
- false validation claim
- clear contract violation
- dangerous infra / secret change
- result meaning is broken

### P1
Serious issue. Fix before merge.

Examples:
- missing validation
- significant doc mismatch
- out-of-scope architectural change
- risky dependency introduction

### P2
Improvement recommended but not blocking.

Examples:
- report clarity
- missing narrow tests
- over-complex implementation where simpler would suffice

---

## 8. Review Output Format

Review reports should follow this structure:

1. Overall verdict
   - approve / revise / stop
2. Scope status
3. Contract status
4. Validation status
5. Documentation sync status
6. Semantic risk summary
7. Issue list by severity
8. Recommended next action

Keep the review concise and evidence-based.

---

## 9. Merge Guidance

Approve only if all of the following are true:

- the change is in scope
- no P0 / P1 issue remains
- validation is adequate for impact level
- docs/config are not misleading
- semantic intent still matches project goal

If unsure, prefer:
- “revise” over “approve”
- “stop and report” over silent acceptance
