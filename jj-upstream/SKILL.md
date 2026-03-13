---
name: jj-upstream
description: This skill should be used when the user invokes /jj-upstream, wants to generate or export upstream patches from jj revisions, needs to classify local jj changes for upstream contribution, or wants to separate company-specific changes from upstream-eligible patches.
version: 1.0.0
---

# jj-upstream

Generate and classify patches from local jj revisions for upstream contribution, separating company-specific changes.

## Steps

### Step 1: list

List all revisions between upstream and local HEAD, classified as upstream or company.

```bash
uv run .claude/skills/jj-upstream/scripts/jj_upstream.py list
```

After running, read and display the generated `revisions.md` files from both the upstream and company patches directories.

### Step 2: export

Export patches for all revisions, splitting company-specific content from upstream-eligible patches.

```bash
uv run .claude/skills/jj-upstream/scripts/jj_upstream.py export
```

After running, report the list of generated `.patch` files in both directories.

### Step 3: summary

Read every `.patch` file from the upstream patches folder (created in Step 2). Write a `<folder-name>-summary.md` in the same folder structured as a review document — the reader must be able to approve or reject each patch from this file alone, without opening raw diffs.

**Document structure:**

For each patch, produce a top-level section:

```
# {index}. {revision description}

change_id: {change_id}
commit_id: {commit_id}
```

Then for each file changed in the patch, add an H2 section:

```
## path/to/file.ext — one-line summary of what changed in this file
```

Within each file section, handle hunks as follows:

- **Short diff (roughly under 60 lines total for the file):** include the complete diff as a fenced code block with `diff` syntax highlighting.
- **Long diff:** summarize the change in prose, quoting only the first and last few lines of the diff inline as a `diff` fenced block.
- **Trivial/single-hunk file change:** skip the H3 level entirely — place the diff or summary directly under the H2.
- **Multi-hunk file change:** add an H3 heading per logical change (hunk or group of related hunks) before its diff block or prose summary.

**Emphasis:**
- Use `diff` syntax highlighting in all fenced code blocks.
- Keep descriptions precise and factual — what changed, not why.
- Completeness matters: do not omit files or truncate diffs unless they exceed the length threshold.
