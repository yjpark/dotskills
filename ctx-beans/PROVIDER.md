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
