---
provider: beans
type: task
title: "Create ctx-organize skill"
date: 2026-03-14
status: clarified
---

## Goal

Add a `ctx-organize` skill to the `ctx-*` family that takes a clarified file and routes it to its proper destination based on the `provider` field in frontmatter. This closes the gap between `ctx-clarify` (which produces `clarified/` files) and whatever system those clarifications belong to.

## Core Flow

1. User triggers the skill against a file in `clarified/`
2. Skill reads the file's frontmatter to get `provider` and `type`
3. Skill loads `.claude/ctx/<provider>/PROVIDER.md` for organizing instructions
4. Skill executes provider-specific logic (e.g., create a bean, place a doc)
5. File moves from `clarified/` → `organized/`, with `status: organized` in frontmatter

## Provider Routing

The `provider` frontmatter field drives all routing — no user prompt needed at organize-time. Provider instructions live in `.claude/ctx/<provider>/PROVIDER.md`, which is shared by all `ctx-*` skills for that provider.

## Initial Providers

**beans** — creates a bean via the `beans` CLI using frontmatter fields as inputs. After creation, notes the bean ID in the organized file.

**docs** — places the file in the right folder by convention (TBD based on `type` or explicit path in frontmatter).

## File Lifecycle

```
clarified/<date>_<slug>.md   →   organized/<date>_<slug>.md
status: clarified                 status: organized
```

The organize step is a move + frontmatter update. The organized file should also include any provider-specific metadata added during organizing (e.g., `bean_id: playground-abc1`).

## PROVIDER.md Structure

`PROVIDER.md` is a single file per provider covering all `ctx-*` skill guidance — both clarification hints and organizing instructions. It replaces any per-skill `organize.md` or similar split. Sections within `PROVIDER.md` are labeled by skill (e.g., `## Organizing`, `## Clarifying`).

## Edge Cases

- If no provider is found in frontmatter: ask the user
- If the provider directory doesn't exist: report clearly, don't silently fail
- If the file is already in `organized/`: confirm before re-organizing

## Out of Scope

- Multi-file batch organizing (future)
- Interactive provider selection at organize-time (provider is set during clarify)
- Docs provider implementation details (deferred until needed)
