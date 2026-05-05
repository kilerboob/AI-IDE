# Project Overview

## Name
AI IDE — Local AI-Powered Developer Control System

## Purpose
Manage AI agents for software development using a structured, gated workflow:

```
Research → Guard → Code → QA → Report → Memory
```

## Current Status
Foundation established. CLI tools and memory system operational.

## Key Components
- `.ai/` — Agent definitions, rules, hooks, skills, pipeline documentation
- `.memory-bank/` — Long-term memory: decisions, context, roadmap, changelog
- `ai_task.py` — CLI for task lifecycle management
- `ai_guard.py` — Safety validation before code changes

## Tech Stack
- Python (CLI tools, no external dependencies)
- Markdown (memory and documentation)
- JSON (configuration)

## Principles
1. No code without research
2. Only modify explicitly allowed files
3. All memory is project-scoped
4. Safety gates are enforced, not advisory
