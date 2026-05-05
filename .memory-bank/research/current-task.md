# Research: Foundation Setup

**Task:** Build the AI IDE foundation — CLI tools, memory system, and agent control layer.  
**Date:** 2026-05-05  
**Status:** Complete

---

## Problem Statement
Create a structured repository that manages AI agents for software development using a gated pipeline (Research → Guard → Code → QA → Report → Memory) with CLI tooling, a memory system, and enforceable safety rules.

---

## Options Considered

### Option A — Monolithic script
One large Python script handles all stages.  
**Pros:** Simple to start  
**Cons:** Hard to maintain, impossible to gate individual stages, no separation of concerns

### Option B — Separate CLI scripts per concern (selected)
`ai_task.py` manages the task lifecycle; `ai_guard.py` handles validation separately.  
**Pros:** Clear responsibilities, independently executable, easy to extend  
**Cons:** Slightly more files to maintain

---

## Selected Solution
**Option B** — Two focused Python scripts backed by a structured directory layout.

### Rationale
- Guard can be run independently without loading the full task manager
- Each agent definition lives in its own file under `.ai/agents/`
- Memory files are decoupled from code

---

## Allowed Files
```
ai_task.py
ai_guard.py
.ai/rules.json
.ai/hooks.json
.ai/skills.json
.ai/pipeline.md
.ai/agents/research.md
.ai/agents/coder.md
.ai/agents/memory.md
.ai/agents/qa.md
.memory-bank/project.md
.memory-bank/roadmap.md
.memory-bank/decisions.md
.memory-bank/changelog.md
.memory-bank/context.md
.memory-bank/import-ledger.json
.memory-bank/research/current-task.md
README.md
```
