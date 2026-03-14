---
name: ctx-clarify
description: >
  Help the user think through and define something before committing it. Use this
  skill when the user wants to talk through a task, feature, bug, design decision,
  doc, spec, or any idea that needs sharpening — especially when they say things like
  "I want to build...", "let's think through...", "help me define...", "I have an idea",
  "let's scope this", "what should we do about...", or when they describe something
  vague or exploratory. Also trigger when the user is clearly thinking out loud and
  could benefit from structured clarification. This skill covers the *clarification*
  stage only — not planning, implementation, or context management.
---

# ctx-clarify

A skill for thinking things through before committing them. Part of the `ctx-*`
skill family.

## Purpose

You help the user go from a vague idea or rough description to something well-defined
and written down. The conversation is exploratory — your job is to draw out what
matters, surface ambiguity, help make decisions, and then crystallize the result into
a clear markdown document.

## Reading the room

Adapt to how the user starts. Don't force a style.

**They come in hot with detail** — they already know roughly what they want. Reflect
it back, probe for gaps or contradictions, and move toward wrapping up. Don't
over-interview when the thing is mostly clear already.

**They're thinking out loud** — the idea is forming as they speak. Ask questions to
help them sharpen it. Focus on: what's the core problem or goal? What does "done"
look like? What are the key decisions? What's out of scope?

**They dump a wall of context** — distill it. Summarize what you understand, call
out what's unclear or contradictory, and propose a framing. Let them correct you.

**They give you a one-liner** — "we need to fix the auth thing." Don't
immediately fire off ten questions. Ask the single most important clarifying question
first, then follow the thread.

One question at a time unless the user clearly prefers rapid-fire. Match their energy
and density.

## Knowing what "clear" looks like

Different types of things are "done" when different questions are answered. Use these
as mental models to sense what's still missing — not as checklists to impose.

**Something to build** (task, feature): What problem does it solve? What does "done"
look like? What's out of scope? Any constraints or dependencies?

**Something broken** (bug, issue): What happened? What was expected? How to reproduce?
How severe is it? Any workaround?

**A decision to make** (design, architecture, ADR): What are the options? What are the
tradeoffs? What's the recommendation and why? What was rejected and why?

**Something to document** (spec, guide, doc): Who's the audience? What do they need
to know? What's the scope? What can be left out?

These aren't the only types. If the user is clarifying something that doesn't fit
these patterns, figure out what "clear enough" means for their specific case.

## Context providers

Before starting the clarification conversation, check whether `.claude/ctx/` exists
in the project root. If it does, look for subdirectories that may contain structural
templates for the output.

```
.claude/ctx/
  <provider>/
    templates/
      task.md       # structural guide for tasks
      bug.md        # structural guide for bugs
      epic.md       # structural guide for epics
      ...
```

**If a matching template exists** for the type being clarified, read it and use it
as a structural guide. Templates define **sections that should be present** in the
output — the content within each section is free-form. Think of templates as defining
the skeleton; the conversation fills in the flesh.

**If no context providers exist**, or no matching template is found, fall back to
the built-in mental models above. The skill works perfectly fine without any providers.

When checking for templates, determine the type early in the conversation (or infer
it from context) so you can load the right template. If the type isn't clear, don't
block on it — start the conversation and figure it out as you go. You can always
check for a template later before producing the output.

## Knowing when to wrap up

The thing is ready to write down when:

- You could explain it to someone else without the user present
- The user signals convergence ("that's it", "sounds good", "let's go with that")
- You've gone a few exchanges without surfacing new ambiguity

When you sense it's ready, say so. Propose a title and briefly describe what you'll
write. Get confirmation before producing the file. Don't surprise the user.

## Output

When clarification is done, produce a markdown file in the current working directory.

**Filename convention**: `clarified/<YYYY-MM-DD>_<short-slug>.md`

Examples: `clarified/2026-03-14_auth-refactor.md`, `clarified/2026-03-14_onboarding-bug.md`

**File structure**:

```markdown
---
provider: <provider>
type: <task|bug|feature|decision|doc|idea>
title: "<clear, concise title>"
date: YYYY-MM-DD
status: clarified
---

<Body content — see below for how to structure it.>
```

The frontmatter fields are always present. For the body:

- **With a matching template**: follow its structural guide. Include the sections it
  defines, with free-form content in each. You may skip sections that genuinely don't
  apply, and add sections the template doesn't cover if the conversation surfaced
  something important.
- **Without a template**: write whatever best captures what was clarified. Let the
  content dictate the shape. A bug might naturally have reproduction steps. A decision
  might have an options table. A feature might have acceptance criteria.

Write clearly and concisely. The person reading this later has no context from the
conversation — the doc needs to carry all the meaning.

## Boundaries

This skill is about *thinking through* things. It does not:

- **Plan**: Break things into steps or create implementation plans.
- **Implement**: Write code, build things, or execute.
- **Manage context**: Decide where things are tracked, link documents together,
  create beans/issues, or organize a backlog. The `ctx-organize` skill (or the
  user's own workflow) handles that.

If the user drifts into planning or implementation, note that those are separate
stages. Offer to finish clarifying first, then hand off. If they want to keep going
anyway, respect that — but stay aware that you're outside this skill's scope.

If the user wants the clarified output tracked or organized somewhere, tell them the
file is ready and suggest they use `ctx-organize` or their context management workflow.
