---
description: >
  Generate a daily summary of Backlog.md task changes by parsing jj diffs.
  Produces a markdown "## Tasks" section with categorized task changes
  (completed, new, status changes, other updates) using Obsidian wikilinks.
trigger: Invoked by the /update-daily-tasks command to generate task summary markdown.
---

# backlog-summary

Parse jj version control diffs to produce a categorized markdown summary of Backlog.md task changes for a given date.

## Input

- `target_date`: `YYYY-MM-DD` string

## Data Collection

### Step 1 — Find the jj revision for the target date

Run:
```
jj log --no-pager -r 'description("<target_date>")' -T 'change_id ++ "\n"'
```

- If a change_id is returned, use that revision.
- If empty, check if the working copy has relevant changes: `jj diff --no-pager -r @ --summary -- backlog/tasks/ backlog/completed/`
  - If changes exist, use `@` as the revision.
  - If no changes, report "No backlog changes found for this date" and stop.

### Step 2 — Get the file-level summary

Run:
```
jj diff --no-pager -r <revision> --summary -- backlog/tasks/ backlog/completed/
```

This returns lines like:
```
A backlog/completed/task-13 - Some-title.md
M backlog/tasks/task-1 - Some-title.md
A backlog/tasks/task-9 - Some-title.md
```

- `A` = added file, `M` = modified file

### Step 3 — Get the full diff

Run:
```
jj diff --no-pager -r <revision> -- backlog/tasks/ backlog/completed/
```

## Diff Parsing

### Added files (A)

The diff shows the full file content after `Added regular file <path>:`. Parse the YAML frontmatter to extract: `id`, `title`, `status`, `labels`, `priority`, `created_date`.

### Modified files (M)

The diff shows changes with the format `Modified regular file <path>:`. Key patterns:

**Inline changes** (old and new on the same line):
```
   4    4: status: To DoPick
```
This means status changed from "To Do" to "To Pick" — the old value runs into the new value on the same line.

**Separate removed/added lines** (line numbers differ):
```
   9     :   - ci
  10    9:   - tooling
```
A line with number only on the left was removed; a line with number only on the right was added.

**Detecting field changes:**
- `status:` — look for inline merge or removed/added lines
- `labels:` — look for changed list items under `labels:`
- `priority:` — look for inline merge or removed/added lines
- `ordinal:` — **ignore** (display order, not meaningful)
- `updated_date:` — **ignore** (always changes, not meaningful)
- `created_date:` format changes (quoting) — **ignore**

For inline-merged status values, split by known status names: `To Do`, `To Pick`, `In Progress`, `Stuck`, `Done`, `Blocked`. The first match is the old value, the second is the new value.

For inline-merged label values, the format shows old value concatenated with new value on the same line (e.g., `- tools` becoming `- tooling` shows as `  - toolstooling`). To parse: compare with the current file content (from the right-side context) to determine the new value, and infer the old value from the remaining prefix.

## Change Categorization

Categorize each changed file in priority order:

1. **Completed**: status changed to `Done`, OR file added in `backlog/completed/`
2. **New Tasks**: file added (`A`) in `backlog/tasks/`
   - If a task was both created and completed on the same day (added in `completed/` with `created_date` matching `target_date`), mark it with `*(same-day)*` suffix
3. **Status Changes**: status field changed but NOT to `Done`
4. **Other Updates**: label or priority changed (NOT just `updated_date`, `ordinal`, or `created_date` format changes)

If a task qualifies for multiple categories, use the highest-priority one only.

## Output Format

Generate markdown with `## Tasks` as the top-level heading. Only include sections that have entries.

### Wikilink format

For each task, construct the Obsidian wikilink from the file path:
- Remove the `.md` extension
- Use the task ID as display text
- Format: `[[backlog/tasks/task-N - Slug|TASK-N]]` or `[[backlog/completed/task-N - Slug|TASK-N]]`

### Section templates

```markdown
# Tasks

## Completed (N)
- [[backlog/completed/task-13 - Fetch-google-doc-content-to-References|TASK-13]] Fetch google doc content to References `skills` [high] *(same-day)*
- [[backlog/tasks/task-8 - Finish-the-upstream-patch-exporter|TASK-8]] Finish the upstream patch exporter `flakes` [high]

## New Tasks (N)
- [[backlog/tasks/task-9 - Maintain-the-shell-title-and-tab-name-properly-for-zellij|TASK-9]] Maintain the shell title and tab name properly for zellij `flakes` [medium] -> To Pick

## Status Changes (N)
- [[backlog/tasks/task-6 - Setup-a-proper-Slack-MCP-to-manage-messages-with-agent|TASK-6]] Setup a proper Slack MCP to manage messages with agent: To Do -> To Pick

## Other Updates (N)
- [[backlog/tasks/task-1 - Replace-submodules-with-Josh|TASK-1]] Replace submodules with Josh — label: tools -> tooling
```

### Item format details

- **Completed**: `[[link|ID]] Title \`label\` [priority]` — add `*(same-day)*` if created and completed on the same date
- **New Tasks**: `[[link|ID]] Title \`label\` [priority] -> Status` — show the initial status
- **Status Changes**: `[[link|ID]] Title: OldStatus -> NewStatus`
- **Other Updates**: `[[link|ID]] Title — field: old -> new` (one line per task, combine multiple field changes with `, `)
- Labels: show the first label in backtick format; if multiple labels, join with `,` inside the backticks
- Priority: show in square brackets
- Use `->` (with spaces) for transitions

### Empty sections

Omit any section header that would have zero entries.

## Return

Return the complete markdown string (starting with `## Tasks`) to the caller.
