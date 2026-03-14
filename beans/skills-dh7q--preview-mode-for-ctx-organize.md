---
# skills-dh7q
title: Preview mode for ctx-organize
status: completed
type: feature
priority: normal
created_at: 2026-03-14T08:01:35Z
updated_at: 2026-03-14T08:13:13Z
---

## What

Add a dry-run preview mode to `ctx-organize`. When invoked without flags, ctx-organize shows a terminal summary of what it *would* do — the bean that would be created, with its key fields — without actually executing. Pass `--go` to skip the preview and act immediately.

## Why

ctx-organize can be triggered automatically (e.g., via `auto_organize` in a provider config). A preview-by-default makes it safe to verify the output before committing, especially in automated flows where the user didn't explicitly request organization.

## Behavior

**Default (preview):**
- Read the clarified file and resolve the provider, type, title, priority, and body.
- Print a summary to the terminal, e.g.:
  ```
  Would create bean:
    type:     feature
    title:    Preview mode for ctx-organize
    priority: (none)
    body:     "Add a dry-run preview mode to ctx-organize..."

  Run with --go to create.
  ```
- Do not create the bean or modify any files.

**With `--go`:**
- Skip the preview and execute immediately (current behavior).

## Out of scope

- File-based preview output (terminal only).
- Interactive confirmation prompt (user runs `--go` explicitly).

## Summary of Changes

Updated  to add preview mode support:

- Added **Arguments** section documenting the  flag
- Updated **Core Flow** step 3 to check  in PROVIDER.md frontmatter
- Preview mode prints a dry-run summary (provider action, type, title, priority, body excerpt)
- Preview mode prints instruction to run `/ctx-organize --go <file>` to proceed
- Preview only activates when  AND  is not passed
- Default behavior (no flag) remains execute-immediately when provider has no  setting
