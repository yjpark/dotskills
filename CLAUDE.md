# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

This is a skills repository for Claude Code. Skills are self-contained units of behavior stored as directories, each containing a `SKILL.md` file that describes the skill's purpose, trigger conditions, and implementation.

## Structure

Each skill lives in its own top-level directory:

```
<skill-name>/
  SKILL.md    # Skill definition (trigger, description, prompt/instructions)
```

## Adding a New Skill

1. Create a new directory named after the skill (kebab-case)
2. Add a `SKILL.md` inside it with the skill definition

Use the `skill-creator` skill (available via `/skill-creator`) to create, modify, or evaluate skills interactively.

## Version Control

- This repo uses both Git and [Jujutsu (jj)](https://github.com/martinvonz/jj) — a `.jj/` directory is present alongside `.git/`.
- Prefer `jj` commands for day-to-day VCS operations if available.
