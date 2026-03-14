---
auto_organize: true
---

# Claude Provider

The `claude` provider stores artifacts produced by Claude Code itself — plan mode output, session exports, and similar Claude-generated content.

## Artifact Types

| Type | Purpose |
|------|---------|
| `plan` | Implementation plan from Claude's plan mode |

(Extensible — `session` and other types can be added later.)

## Organizing

Instructions for `ctx-organize` when the clarified file has `provider: claude`.

### type: plan

When organizing a `type: plan` file:

#### If `source` is present and starts with `beans://`

1. Extract the bean ID from the source URL (e.g., `beans://skills-abc1` → `skills-abc1`)
2. Append the plan content to the bean's body:

```bash
beans update <id> --body-append "$(cat clarified/<filename>.md | tail -n +N)"
```

(Adjust `tail` offset to skip past the frontmatter block — count the lines up to and including the closing `---`.)

3. Add `organized_to: beans://<id>` to the organized file's frontmatter
4. Move the file to `organized/`
5. Suggest: "Plan attached to bean `<id>`. View with `beans show <id>`"

#### If no `source`

1. Move the file to `organized/` (standard ctx-organize file move)
2. No additional action needed
