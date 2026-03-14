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

## Conclusion: Option 3 — don't specify

Model choice should remain a user concern, not be hardcoded in skills.

**Reasons:**
- **Model capabilities shift** — what's best today may not be tomorrow as models evolve
- **Context matters** — sometimes a quick clarification on a faster model is fine
- **Skills should define behavior, not infrastructure** — the skill says *what to do*, the user picks *how to run it*
- **`/model` exists for quick switching** — it's one command

**Alternative if needed:** Save a user preference memory so the agent can remind you when invoking ctx-clarify on a non-opus model. This is adaptive without hardcoding anything into the skill definition.
