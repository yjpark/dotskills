---
name: ctx-plan
description: >
  Trigger after Claude Code's plan mode completes and the user approves the plan.
  Save the plan file from .claude/plans/ to clarified/ with provider: claude, type: plan.
  Use when the user says "save the plan", "ctx-plan", or similar after plan mode finishes.
---

# ctx-plan Skill

After Claude Code's built-in plan mode completes and the user approves the plan, this skill saves the plan into the `clarified/` pipeline with `provider: claude, type: plan`.

## Trigger conditions

Use this skill when:
- Plan mode has just completed and the user approved the plan
- A plan file exists in `.claude/plans/`
- The user says "save the plan", "ctx-plan", or similar

Do **not** use before coding. Plan mode already handles the planning step — this skill only saves the output.

### Guard: skip during clarify sessions

Before proceeding, check whether this conversation already produced a `clarified/` file (via `ctx-clarify` or similar). If a file in `clarified/` with today's date was written earlier in this session and its `type` is **not** `plan`, then this plan is a side effect of a clarify session. Do **not** save it — instead, tell the user:

> "Skipping plan save — this plan was a side effect of a clarify session."

Then stop. Do not proceed to the workflow steps.

## Workflow

### 1. Locate the plan file

Find the most recently modified file in `.claude/plans/`:

```bash
ls -t .claude/plans/ | head -1
```

Read its content.

### 2. Extract metadata

- **Title**: the text of the first `# heading` in the plan
- **Slug**: lowercase, hyphenated version of the title (e.g., `add-rate-limiting`)
- **Date**: today's date in `YYYY-MM-DD` format
- **Source**: if this plan was triggered by a beans task, set `source: beans://<bean-id>`. If unknown, omit or ask the user.

### 3. Write to clarified/

Save to `clarified/<YYYY-MM-DD>_<slug>.md` with this frontmatter:

```yaml
---
provider: claude
type: plan
title: "<plan title>"
date: YYYY-MM-DD
status: clarified
source: beans://<bean-id>  # optional, omit if not from a bean
---
```

Body = the full plan content (everything from the plan file, verbatim).

### 4. Auto-organize

Since the `claude` provider has `auto_organize: true`, automatically invoke `/ctx-organize` on the saved file immediately after writing it.

## Example

After plan mode produces `.claude/plans/auth-refactor.md`:

**User:** "save the plan, it's for beans://skills-abc1"

**Claude:**
1. Reads `.claude/plans/auth-refactor.md`
2. Extracts title: `Auth Refactor`
3. Writes `clarified/2026-03-15_auth-refactor.md`:

```markdown
---
provider: claude
type: plan
title: "Auth Refactor"
date: 2026-03-15
status: clarified
source: beans://skills-abc1
---

# Auth Refactor

## Goal
...

## Steps
...
```

4. Runs `/ctx-organize` on the saved file
