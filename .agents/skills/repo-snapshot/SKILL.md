---
name: repo-snapshot
description: Scan a repository and produce a concise project snapshot covering structure, stack, entrypoints, tooling, validation signals, risk zones, and missing operating docs.
---

# repo-snapshot

## Purpose

Use this skill at project startup or when entering an unfamiliar repository.

The goal is to create a factual `project_snapshot.md` that helps later steps such as:

- drafting `AGENTS.md`
- drafting `PROJECT_CONTEXT.md`
- drafting stage / issue plans
- identifying risky directories
- identifying missing documentation or workflow gaps

This skill is for repository understanding, not implementation.

---

## When to use

Use this skill when:

- the repository is new to you
- there is no reliable `AGENTS.md` yet
- the existing docs look incomplete or stale
- you need to bootstrap project rules before coding
- a human asks for a repo scan / architecture summary / starter documentation pass

Do not use this skill as a substitute for task execution.

---

## Required behavior

You must prefer factual extraction over speculation.

If something cannot be confirmed from the repository:
- do not invent it
- either omit it
- or label it as unknown / needs confirmation

Your job is to summarize signals that are actually present.

---

## What to inspect

Inspect as many of the following as are relevant and present:

### Repository shape
- top-level directories
- monorepo vs single-package structure
- major code areas
- docs / configs / scripts / tests locations

### Project signals
- README.md
- existing AGENTS.md or similar files
- docs/*
- package managers and dependency files
- build / lint / test / format configs
- CI workflows
- Docker / devcontainer / infra files
- key entrypoints
- training / serving / evaluation / app startup scripts
- examples / notebooks / scripts

### Quality and risk signals
- protected or stable areas
- generated files
- lockfiles
- data / assets / checkpoints / migrations
- secrets / env templates
- directories that should not be casually modified

---

## Output target

Write the snapshot to:

- `docs/snapshots/project_snapshot.md`

If the path does not exist, create it.

If a project-specific template exists, follow it.
Otherwise use the structure below.

---

## Output structure

Use this structure:

# project_snapshot

## 1. Repository Overview
- repository type
- apparent purpose
- primary language(s)
- main framework(s)
- monorepo or not

## 2. Top-Level Structure
- key directories and what they appear to contain

## 3. Key Entry Points
- main runtime entrypoints
- main config entrypoints
- main training / inference / service / app entrypoints
- likely first files to read

## 4. Tooling Signals
- package/build system
- lint / format tools
- type-check tools
- test frameworks
- CI signals
- docker / environment signals

## 5. Validation Signals
- confirmed commands or scripts for:
  - install
  - run
  - test
  - lint
  - build
  - focused checks if discoverable

## 6. Risk Zones
- directories or files that appear sensitive
- generated artifacts
- infra / deploy / secret-related files
- public interfaces or schemas likely requiring caution

## 7. Documentation State
- docs that already exist
- likely stale or missing docs
- whether AGENTS.md exists and whether it looks usable

## 8. Missing Operating Documents
Recommend whether the repo likely needs:
- AGENTS.md
- PROJECT_CONTEXT.md
- stage plan
- issue plan
- review checklist
- contract freeze doc

## 9. Open Uncertainties
- facts that could not be confirmed from repository evidence

---

## Quality bar

A good snapshot should be:

- concise
- evidence-based
- immediately useful for later documentation generation
- free of invented facts
- focused on how an agent can work safely in the repo

Avoid:
- long prose summaries
- speculative architecture claims
- generic advice not grounded in the repo

---

## Suggested workflow

1. inspect top-level structure
2. inspect README and major docs
3. inspect dependency/config files
4. inspect scripts and test/build signals
5. identify entrypoints and risk zones
6. write the snapshot
7. clearly separate confirmed facts from uncertainties

---

## Final note

This skill does not decide project direction.
It only prepares an accurate operational picture of the repository.
