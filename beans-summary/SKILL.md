---
description: >
  Generate a daily summary of beans issue tracker changes by parsing jj diffs.
  Produces a markdown "# Tasks" section with categorized bean changes
  (completed, new beans, status changes, other updates) using Obsidian wikilinks.
trigger: Invoked by the /update-daily-tasks command to generate task summary markdown.
---

# beans-summary

Parse jj version control diffs to produce a categorized markdown summary of beans changes for a given date.

## Input

- `target_date`: `YYYY-MM-DD` string

## Data Collection

### Step 1 — Find the jj revision for the target date

Run:
```
jj log --no-pager -r 'description("<target_date>")' -T 'change_id ++ "\n"'
```

- If a change_id is returned, use that revision.
- If empty, check if the working copy has relevant changes: `jj diff --no-pager -r @ --summary -- beans/`
  - If changes exist, use `@` as the revision.
  - If no changes, report "No beans changes found for this date" and stop.

### Step 2 — Get the file-level summary

Run:
```
jj diff --no-pager -r <revision> --summary -- 'beans/yj-*'
```

This returns lines like:
```
A beans/yj-k6pf--learn-the-permission-config-for-claude-code.md
M beans/yj-b57l--replace-submodules-with-josh.md
```

- `A` = added file, `M` = modified file
- Exclude any files under `beans/.conversations/`

### Step 3 — Get the full diff

Run:
```
jj diff --no-pager -r <revision> -- 'beans/yj-*'
```

## Diff Parsing

### Added files (A)

The diff shows the full file content after `Added regular file <path>:`. Parse the YAML frontmatter to extract: `title`, `status`, `type`, `priority`, `tags`, `created_at`.

The bean ID is found in the frontmatter comment line: `# yj-XXXX` (the line immediately after `---`).

### Modified files (M)

The diff shows changes with the format `Modified regular file <path>:`. Key patterns:

**Inline changes** (old and new on the same line):
```
   3    3: status: drafttodo
```
This means status changed from "draft" to "todo" — the old value runs into the new value on the same line.

**Separate removed/added lines** (line numbers differ):
```
   8     :   - tools
        8:   - tooling
```
A line with number only on the left was removed; a line with number only on the right was added.

**Detecting field changes:**
- `status:` — look for inline merge or removed/added lines
- `tags:` — look for changed list items under `tags:`
- `priority:` — look for inline merge or removed/added lines
- `type:` — look for inline merge or removed/added lines
- `blocked_by:` — look for changed list items
- `updated_at:` — **ignore** (always changes, not meaningful)
- `created_at:` format changes — **ignore**

For inline-merged status values, split by known status names: `draft`, `todo`, `in-progress`, `completed`, `scrapped`. The first match is the old value, the second is the new value.

For inline-merged tag/priority values, compare with the right-side context lines to determine the new value and infer the old value from the remaining prefix.

## Change Categorization

Categorize each changed file in priority order:

1. **Completed**: status changed to `completed` or `scrapped`, OR file added with status `completed` or `scrapped`
2. **New Beans**: file added (`A`) with status other than `completed`/`scrapped`
   - If a bean was both created and completed on the same day (added with `completed`/`scrapped` status and `created_at` matching `target_date`), mark it with `*(same-day)*` suffix and place in Completed
3. **Status Changes**: status field changed but NOT to `completed` or `scrapped`
4. **Other Updates**: tags, priority, type, or blocked_by changed (NOT just `updated_at` changes)

If a bean qualifies for multiple categories, use the highest-priority one only.

## Output Format

Generate markdown with `# Tasks` as the top-level heading. Only include sections that have entries.

### Bean ID extraction

Extract the bean ID (`yj-XXXX`) from:
1. The frontmatter comment line `# yj-XXXX` in the diff content, OR
2. The filename itself: `beans/yj-XXXX--slug.md` → `yj-XXXX`

### Wikilink format

For each bean, construct the Obsidian wikilink from the file path:
- Remove the `.md` extension
- Use the bean ID as display text
- Format: `[[beans/yj-XXXX--slug|yj-XXXX]]`

### Section templates

```markdown
# Tasks

## Completed (N)
- [[beans/yj-8bc3--finish-the-upstream-patch-exporter|yj-8bc3]] Finish the upstream patch exporter `flakes` [high] *(same-day)*
- [[beans/yj-oi8t--generate-daily-summary-from-backlogmd-tasks|yj-oi8t]] Generate daily summary from backlog tasks `skills` [normal]

## New Beans (N)
- [[beans/yj-k6pf--learn-the-permission-config-for-claude-code|yj-k6pf]] Learn the permission config for Claude Code [high] -> todo

## Status Changes (N)
- [[beans/yj-27qa--setup-a-proper-slack-mcp-to-manage-messages-with-a|yj-27qa]] Setup a proper Slack MCP: draft -> todo

## Other Updates (N)
- [[beans/yj-b57l--replace-submodules-with-josh|yj-b57l]] Replace submodules with Josh -- tags: tools -> tooling
```

### Item format details

- **Completed**: `[[link|ID]] Title \`tag\` [priority]` — add `*(same-day)*` if created and completed on the same date; omit tag/priority if not present
- **New Beans**: `[[link|ID]] Title \`tag\` [priority] -> Status` — show the initial status; omit tag/priority if not present
- **Status Changes**: `[[link|ID]] Title: OldStatus -> NewStatus`
- **Other Updates**: `[[link|ID]] Title -- field: old -> new` (one line per bean, combine multiple field changes with `, `)
- Tags: show the first tag in backtick format; if multiple tags, join with `,` inside the backticks
- Priority: show in square brackets; omit if not set
- Use `->` (with spaces) for transitions

### Empty sections

Omit any section header that would have zero entries.

## Return

Return the complete markdown string (starting with `# Tasks`) to the caller.
