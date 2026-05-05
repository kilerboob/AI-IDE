# Changelog

## 2026-05-05 — Foundation release

### Added
- `.ai/` control layer
  - `agents/` directory with research, coder, memory, qa agent definitions
  - `hooks.json` — task lifecycle event hooks
  - `rules.json` — safety rules (R001–R005)
  - `skills.json` — agent capability catalogue
  - `pipeline.md` — full workflow documentation
- `.memory-bank/` memory system
  - `project.md`, `roadmap.md`, `decisions.md`, `changelog.md`, `context.md`
  - `reports/` directory for task reports
  - `research/` directory with example `current-task.md`
  - `import-ledger.json` for deduplication tracking
- `ai_task.py` — CLI tool (new, guard, report, memory --from-report)
- `ai_guard.py` — validation system enforcing all safety rules
- Example task report in `.memory-bank/reports/`
- Updated `README.md`
