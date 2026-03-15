---
auto_organize: true
---

# Beans Provider

The `beans` provider structures clarified output for the beans issue tracker. Beans is an agentic-first issue tracker where issues ("beans") have distinct types with different purposes.

## Issue Types

| Type | Purpose |
|------|---------|
| `feature` | A user-facing capability or enhancement |
| `task` | A concrete piece of work (chore, sub-task) |
| `bug` | Something broken that needs fixing |
| `epic` | A thematic container for related work |
| `milestone` | A target release or checkpoint |

## How Templates Map

Each template in `templates/<type>.md` describes the sections a clarified document of that type should contain. The ctx-clarify skill reads the matching template based on the bean type the user is clarifying and uses it to structure the output.

Templates are structural guides — they define what sections belong in a document, not how to fill them in. Sections can be omitted if not applicable, and extra sections can be added when needed.

## Clarifying

Instructions for `ctx-clarify` when the provider is `beans`.

### Searching for existing items

When the user's input looks like a reference to an existing item, search with:

```bash
beans list --json -S "<keywords>"
```

Results:
- **One clear match** — show title, type, status. Confirm with user.
- **Multiple candidates** — show numbered list (title, type, status). User picks.
- **No match** — fall through to new-item flow.

### Source field

When clarifying an existing bean, set in the output frontmatter:

```yaml
source: beans://<bean-id>
```

## Organizing

Instructions for `ctx-organize` when the clarified file has `provider: beans`.

### Mapping frontmatter to bean fields

| Frontmatter field | Bean CLI flag | Notes |
|-------------------|---------------|-------|
| `type`            | `-t <type>`   | Map directly: `task`, `bug`, `feature`, `epic`, `milestone` |
| `title`           | first arg     | Use as the bean title |
| `priority`        | `-p <priority>` | Optional; omit if not in frontmatter |

### Updating an existing bean

If the clarified file has `source: beans://<bean-id>` in frontmatter:

1. Extract the bean ID from the URI (e.g., `beans://skills-9pqv` → `skills-9pqv`).
2. Confirm with the user: "This will update bean `<bean-id>`: _[title]_. Proceed?"
3. Update the bean's body with the clarified content using
   `beans update <bean-id> --body-replace-old ... --body-replace-new ...`,
   or append if the content is entirely new.
4. Do not change bean metadata (type, status, priority) unless the user requests it.
5. Skip the "Creating the bean" step below.
6. Add `bean_id: <bean-id>` to the organized file's frontmatter.

If `source` is absent, proceed with creating a new bean as below.

### Creating the bean

Run:

```bash
beans create --json "<title>" -t <type> -s todo -d "<body>"
```

Where `<body>` is the full markdown body of the clarified file (everything after the frontmatter `---` block). If the body is long, pass it via a heredoc or temp file to avoid shell escaping issues.

Example:
```bash
beans create --json "Auth refactor" -t task -s todo -d "$(cat clarified/2026-03-14_auth-refactor.md | tail -n +6)"
```

(Adjust the `tail` offset to skip past the frontmatter block.)

### After creation

The `beans create --json` output includes the bean `id`. Add this to the organized file's frontmatter as `bean_id: <id>`.

### Suggesting next steps

After organizing, tell the user:
- The bean ID and title (e.g., "Created bean `playground-abc1`: Auth refactor")
- How to view it: `beans show <id>`
- That initial status is `todo` — they can update it when ready to start
