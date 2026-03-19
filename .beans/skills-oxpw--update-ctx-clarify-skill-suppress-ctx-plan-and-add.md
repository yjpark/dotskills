---
# skills-oxpw
title: 'Update ctx-clarify skill: suppress ctx-plan and add opusplan nudge'
status: completed
type: task
priority: normal
created_at: 2026-03-15T06:47:33Z
updated_at: 2026-03-15T06:56:14Z
order: k
---

Based on clarified/2026-03-15_model-specification-in-skills.md

Two changes to ctx-clarify/SKILL.md:
- [x] Add end-of-session instruction: discard any plan mode output, do not invoke ctx-plan
- [x] Add soft nudge at session start when active model is `opusplan`: suggest enter plan mode to use opus if not already in plan mode (non-blocking)

## Summary of Changes

Added two sections to `ctx-clarify/SKILL.md`:
- **Session start**: soft nudge to enter plan mode when on `opusplan`
- **End of session**: explicit instruction to discard plan output and not invoke ctx-plan
