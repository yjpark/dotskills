---
# skills-9pqv
title: Support clarifying existing items in ctx-clarify
status: todo
type: feature
created_at: 2026-03-15T06:29:13Z
updated_at: 2026-03-15T06:29:13Z
---

## Problem

ctx-clarify currently only supports clarifying new items from scratch. In practice,
beans are often created as lightweight placeholders with minimal descriptions, then
need to be fleshed out before work begins. There's no way to enrich an existing bean
through the clarification workflow.

## Solution

Add an "existing item" flow to ctx-clarify that lets users reference an existing bean
with a few words, fuzzy-matches it, and runs the clarification conversation using the
bean's current content as a starting point.

## Workflow

### 1. Identifying the existing item

When the user invokes ctx-clarify, the agent should attempt to fuzzy-search existing
beans based on the user's input (a few keywords or a short phrase — not a bean ID).

**Search results lead to one of three paths:**

- **One clear match** — show the bean's title and ask the user to confirm. On
  confirmation, proceed to clarification.
- **Multiple candidates** — show a short list of matching beans (title, status, type).
  User picks one, then proceed.
- **No match** — tell the user no existing item was found. Fall back to the current
  new-item flow.

### 2. Starting the conversation

Once an existing bean is identified:

- **Skip type establishment** — the type is already known from the bean's metadata.
- **Show the user** the bean's title, current description, and status.
- **Use the existing content as starting context** — the conversation enriches what's
  already there rather than starting from scratch.

The rest of the clarification conversation follows the same mental models and flow
as the current skill.

### 3. Output

The clarified file is written to `clarified/` as today, with one addition in the
frontmatter:

```yaml
source: beans://<bean-id>
```

This links the clarified output back to the existing bean. The `ctx-organize` skill
(or the beans provider) uses this `source` field to update the existing bean with the
enriched content, rather than creating a new one.

## Scope

- This feature adds a new entry path to ctx-clarify; it does not change the
  clarification conversation itself or the output format (beyond adding `source`).
- The agent always confirms the matched bean with the user before proceeding — no
  silent assumptions.
- Updating the bean itself is handled by `ctx-organize`, not by ctx-clarify.
