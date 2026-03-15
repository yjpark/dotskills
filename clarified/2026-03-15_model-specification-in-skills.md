---
provider:
type: idea
title: "Model specification in skills"
date: 2026-03-15
status: clarified
---

## Question

Should skills specify a preferred LLM model (e.g., opus for ctx-clarify, sonnet for ctx-organize)?

## Options considered

1. **Add a suggestion step in the skill** — The skill checks the current model and suggests switching if it differs from the preferred one. Non-intrusive but adds friction every invocation.

2. **Add a `preferred_model` frontmatter field to SKILL.md** — A convention where skills declare a preferred model and suggest switching if the active model differs. Clean but soft.

3. **Don't specify it in the skill** — Keep model choice entirely as a user concern. Simplest approach, avoids coupling skills to specific models.

## Conclusion: Option 3 — don't specify (with soft nudge)

Model choice should remain a user concern, not be hardcoded in skills.

**Reasons:**
- **Model capabilities shift** — what's best today may not be tomorrow as models evolve
- **Context matters** — sometimes a quick clarification on a faster model is fine
- **Skills should define behavior, not infrastructure** — the skill says *what to do*, the user picks *how to run it*
- **`/model` exists for quick switching** — it's one command

**Nice-to-have:** A soft nudge at the start of ctx-clarify when the active model is `opusplan` — something like: "You're on `opusplan`. If you'd prefer to avoid plan mode for this session, run `/model opus` first." Non-blocking, just a reminder.

---

## Related: ctx-plan suppression during clarify sessions

### Problem

The user's default model is `opusplan` (opus + plan mode). When ctx-clarify is invoked, plan mode may generate a plan. The concern is not plan mode itself — it's that **ctx-plan would pick up that plan and track it as an implementation plan**, which is incorrect. Clarify sessions are exploratory; their plans are incidental and should not be persisted.

### Decision

**ctx-clarify owns the suppression rule (Option A).**

At the end of a ctx-clarify session, the skill explicitly instructs the agent: *do not save any plan generated during this session via ctx-plan.* The plan mode output is discarded.

**Why this approach:**
- ctx-clarify knows its own intent — it's the right place to express "this was not an implementation session"
- ctx-plan stays simple and doesn't need to detect its invocation context
- No inter-skill coupling required

### What to change

Update `ctx-clarify/SKILL.md` to include an explicit instruction at the end of the session: any plan generated during the clarify conversation should be discarded and not passed to ctx-plan.
