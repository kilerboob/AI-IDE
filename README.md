# AI-IDE — Local AI-Powered Developer Control System

A minimal, structured foundation for managing AI agents through a gated software development workflow.

```
Research → Guard → Code → QA → Report → Memory
```

---

## Quick Start

```bash
# 1. Start a new task (creates research stub)
python ai_task.py new "My feature"

# 2. Fill in .memory-bank/research/current-task.md, then validate
python ai_task.py guard

# 3. (Write code — only touch files listed in allowed_files)

# 4. Generate a task report
python ai_task.py report

# 5. Import the report into long-term memory
python ai_task.py memory --from-report .memory-bank/reports/<date>-my-feature.md
```

---

## Repository Structure

```
.
├── ai_task.py                          CLI — task lifecycle management
├── ai_guard.py                         CLI — safety validation
├── .ai/
│   ├── pipeline.md                     Workflow documentation
│   ├── rules.json                      Safety rules (R001–R005)
│   ├── hooks.json                      Task lifecycle event hooks
│   ├── skills.json                     Agent capability catalogue
│   └── agents/
│       ├── research.md
│       ├── coder.md
│       ├── memory.md
│       └── qa.md
└── .memory-bank/
    ├── project.md                      Project overview
    ├── roadmap.md                      Milestones
    ├── decisions.md                    Architectural decisions
    ├── changelog.md                    History of changes
    ├── context.md                      Current working context
    ├── import-ledger.json              Tracks imported reports
    ├── research/
    │   └── current-task.md             Active research document
    └── reports/
        └── <date>-<task-slug>.md       Completed task reports
```

---

## Safety Rules

| Rule | Description |
|------|-------------|
| R001 | No code without a completed research file |
| R002 | Only modify files listed in `allowed_files` |
| R003 | No direct `git push` to `main` |
| R004 | No Windows-style paths |
| R005 | Memory files must stay inside `.memory-bank/` |

---

## CLI Reference

### `ai_task.py`

| Command | Description |
|---------|-------------|
| `new "task name"` | Create research stub and log task start |
| `guard` | Run `ai_guard.py` validation |
| `report [--task NAME]` | Generate a timestamped report file |
| `memory --from-report FILE` | Import report into memory files |

### `ai_guard.py`

| Flag | Description |
|------|-------------|
| _(no flags)_ | Run all checks |
| `--check NAME` | Run one check (`research`, `allowed-files`, `no-push-to-main`, `no-windows-paths`, `project-scoped-memory`) |
| `--files FILE …` | Check specific files against allowed list and Windows path rule |

---

## Tech Stack
- Python 3 (no external dependencies)
- Markdown (memory and documentation)
- JSON (configuration)
