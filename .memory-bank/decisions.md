# Decisions

## 2026-05-05 — Foundation architecture

**Decision:** Use a six-stage pipeline (Research → Guard → Code → QA → Report → Memory).  
**Rationale:** Each stage has a single, clear responsibility. The Guard stage ensures safety rules are enforced before any code is written, preventing ad-hoc changes.  
**Alternatives considered:**
- Flat single-script approach — rejected (no separation of concerns)
- External CI only — rejected (requires network; we need local enforcement)

---

## 2026-05-05 — No external dependencies

**Decision:** All CLI tools use Python standard library only.  
**Rationale:** Keeps the project portable and avoids dependency management overhead at this early stage.  
**Alternatives considered:**
- `click` for CLI — deferred (can be added later without breaking changes)
- `pydantic` for config validation — deferred

---

## 2026-05-05 — Markdown for memory files

**Decision:** All long-term memory stored as Markdown.  
**Rationale:** Human-readable, diff-friendly, and easy for AI agents to parse without special tooling.

---

## 2026-05-05 — `import-ledger.json` for deduplication

**Decision:** Track imported reports in a JSON ledger rather than deleting or moving report files.  
**Rationale:** Preserves full history while preventing double-processing. Reports remain auditable.
