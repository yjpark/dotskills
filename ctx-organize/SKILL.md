---
name: ctx-organize
description: >
  Route a clarified file to its proper destination based on the provider field in its
  frontmatter. Use this skill when the user says "organize this", "ctx-organize", wants
  to track or file a clarified document, or references a file in the clarified/ directory
  that needs to be acted on.
---

# ctx-organize

A skill for routing clarified documents to their proper destinations. Part of the `ctx-*`
skill family.

## Purpose

`ctx-clarify` produces files in `clarified/`. `ctx-organize` picks up from there: it
reads a clarified file, determines where it belongs based on the `provider` in frontmatter,
executes the provider's organizing logic, and moves the file to `organized/`.

## Identifying the Target File

When triggered, determine which clarified file to organize:

1. **User named it explicitly** — use that file.
2. **Single file in `clarified/`** — use it without asking.
3. **Multiple files in `clarified/`** — list them and ask the user which to organize.
4. **No files in `clarified/`** — tell the user there's nothing to organize.

## Arguments

- `--go` — execute immediately, skipping any provider-configured preview.

## Core Flow

```
1. Read the clarified file (frontmatter + body)
2. Extract provider, type, title from frontmatter
3. Load .claude/ctx/<provider>/PROVIDER.md
   - Check frontmatter for preview_organize: true
   - If preview_organize: true AND --go was NOT passed:
     - Print a preview summary:
       - Provider action (e.g., "Would create bean")
       - Key fields: type, title, priority
       - Truncated body excerpt (first ~200 chars)
     - Print: "Run `/ctx-organize --go <file>` to execute."
     - Stop. Do not create beans, move files, or modify anything.
4. Follow the "## Organizing" section in PROVIDER.md
5. Move the file: clarified/<slug>.md → organized/<slug>.md
6. Update frontmatter: status: clarified → status: organized
7. Add any provider metadata (e.g., bean_id) to the organized file's frontmatter
```

## Reading Provider Instructions

Load `.claude/ctx/<provider>/PROVIDER.md` from the project root. The `## Organizing`
section contains the instructions for this skill.

If the provider directory doesn't exist:
- Report clearly: "No provider configuration found for '<provider>' at .claude/ctx/<provider>/"
- Ask the user how to proceed — don't silently fail or guess

If `provider` is missing from frontmatter:
- Ask the user which provider to use
- Offer to update the frontmatter and continue

## Moving the File

After the provider action completes successfully:

1. Read the organized file path: `organized/<original-filename>`
2. Create `organized/` directory if it doesn't exist
3. Copy file content to `organized/` path with updated frontmatter
4. Delete the original from `clarified/`
5. Frontmatter changes:
   - `status: clarified` → `status: organized`
   - Add any provider-returned metadata fields (e.g., `bean_id`)

## Edge Cases

- **File already in `organized/`**: Warn the user and ask before re-organizing.
- **Provider action fails**: Do not move the file. Report the error clearly.
- **File not found**: Tell the user the path you looked for and ask them to confirm.

## Boundaries

This skill executes the organizing step only. It does not:

- **Clarify**: If the file seems incomplete or ambiguous, note it but still attempt
  to organize. Suggest `ctx-clarify` for further refinement.
- **Plan or implement**: If the user wants to start working on the thing, that's a
  separate step after organizing.

## After Organizing

Tell the user:
- What action was taken (e.g., "Created bean `playground-abc1`: Auth refactor")
- Where the file now lives (e.g., `organized/2026-03-14_auth-refactor.md`)
- Any next steps suggested by the provider (e.g., "You can view the bean with `beans show playground-abc1`")
