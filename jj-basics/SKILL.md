# Jujutsu Basics

Manage code changes with Jujutsu (jj) using a linear stash workflow that produces clean, reviewable history.

## Trigger

When the user asks to work on a task in a repository that uses Jujutsu (has a `.jj/` directory), and the work involves creating or managing revisions.

## Scope

**In scope:** Linear chain of revisions, bookmarks, squash workflow, interactive planning.

**Out of scope:** `jj split`, `jj edit`, `jj rebase`, `jj git push`, remote sync, branching change graphs, conflict resolution, issue tracker integration.

## Commands

Only use these jj commands:

- `jj new` / `jj new -m "..."` — create a new revision
- `jj describe -m "..."` — set or update a revision's description
- `jj bookmark create -r @ <name>` — create a bookmark at the current revision
- `jj bookmark set -r @ <name>` — move a bookmark to the current revision
- `jj squash` — move changes from the current (staging) revision into its parent
- `jj log` — review the change graph
- `jj status` — check the current state

## Bookmark Naming

Use kebab-case slug: `<short-description>` (e.g., `add-auth-middleware`, `fix-parser-bug`).

## Revision Description Format

```
One-line summary

- Refs: <task context or user request>
- What: <planned changes>
- Checks: <conditions that must pass to consider this revision complete>
```

The first line is always a concise one-line summary. Subsequent lines use Markdown list format.

## Workflow

### Phase 1: Planning (interactive, blocking)

1. Receive the task from the user.
2. Plan the revisions needed to complete the task:
   - Each revision should be coherent (one concern, one area of the codebase).
   - Order revisions by implementation dependency.
   - Define clear completion checks for each revision.
3. Present the plan to the user.
   - If anything is unclear, ask for clarification.
   - If there is a better approach than what the user suggested, explain it.
4. **Do NOT proceed to Phase 2 until the user explicitly approves the plan.**

For simple tasks, a single revision is perfectly fine. Do not over-plan.

### Phase 2: Execution

For each planned revision:

#### 2a. Create the revision

Run `jj new -m "<description>"` with the description in the format specified above.

If this is the **first revision** and there are **multiple planned revisions**, append the full plan to the description after a `---` separator line:

```
One-line summary

- Refs: <task context>
- What: <planned changes>
- Checks: <completion conditions>

---

Plan:
1. <revision 1 summary>
2. <revision 2 summary>
...
```

#### 2b. Manage the bookmark

- First revision: `jj bookmark create -r @ <slug>`
- Subsequent revisions: `jj bookmark set -r @ <slug>`

**Notify the user** after each bookmark operation (e.g., "Bookmark `add-auth-middleware` created at revision xyz" or "Bookmark moved to revision xyz").

#### 2c. Working loop (stash workflow)

1. `jj new` — create an unnamed staging revision (no description). This is the working copy.
2. Make file changes in small, incremental steps.
3. When the current changes clearly advance the parent revision toward its completion checks, run `jj squash` to merge them into the parent.
4. **Notify the user** on each squash with a brief summary of what was merged (e.g., "Squashed: added authentication middleware and route guards").
5. Repeat steps 1-4 until the parent revision's checks all pass.

Then move to the next planned revision and repeat from step 2a.

### Phase 3: Completion

After all planned revisions are done:

1. Leave the final empty staging revision in place — the user may want to make final touches before pushing.
2. Verify the bookmark points to the last completed revision (not the empty staging area). Run `jj log` to confirm.
3. Generate a summary for the user:
   - What was accomplished
   - How many revisions were created
   - Current bookmark location
   - Any notes or follow-up suggestions

### Conflict Handling

If any jj operation produces a conflict:

1. **Stop immediately.** Do not attempt to resolve it.
2. Alert the user with full context: which revision, what operation caused it, what the conflict is.
3. Wait for the user to resolve the conflict manually.
4. The user decides whether to resume implementation or return to planning.
