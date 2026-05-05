# AI IDE — Pipeline Documentation

## Workflow

```
Research → Guard → Code → QA → Report → Memory
```

Each stage must complete successfully before the next stage begins.

---

## Stage Descriptions

### 1. Research
**Agent:** `research`  
**Goal:** Understand the task, explore implementation options, and select the best solution.

**Outputs:**
- `.memory-bank/research/current-task.md` containing:
  - Task description
  - Options considered
  - Selected solution with rationale
  - `allowed_files` list

**Gate:** No subsequent stage may begin without a valid `current-task.md`.

---

### 2. Guard
**Agent:** `guard` (`ai_guard.py`)  
**Goal:** Validate all safety rules before any code is written.

**Checks:**
- `current-task.md` exists and is complete
- `allowed_files` list is populated
- No Windows-style paths in any file
- Target branch is not `main`

**Outcome:** `PASS` or `FAIL` with a descriptive error.

---

### 3. Code
**Agent:** `coder`  
**Goal:** Implement the selected solution, touching only files in `allowed_files`.

**Constraints:**
- Must not modify files outside `allowed_files`
- Must not introduce Windows paths
- Must not push directly to `main`

---

### 4. QA
**Agent:** `qa`  
**Goal:** Verify the implementation is correct and complete.

**Checks:**
- Existing tests still pass
- Research goals are satisfied
- No regressions introduced

---

### 5. Report
**Agent:** `coder` / `qa` (collaborative)  
**Goal:** Write a structured task report.

**Output:** `.memory-bank/reports/<YYYY-MM-DD>-<task-slug>.md`

**Sections:**
- Task summary
- Solution implemented
- Files changed
- QA results
- Open issues

---

### 6. Memory
**Agent:** `memory`  
**Goal:** Absorb the completed report into long-term memory files.

**Actions:**
- Update `project.md`, `roadmap.md`, `decisions.md`, `context.md`
- Append entry to `changelog.md`
- Record report as imported in `import-ledger.json` (prevents duplicates)

---

## CLI Commands

| Command | Description |
|---|---|
| `python ai_task.py new "task name"` | Start a new task (creates research stub) |
| `python ai_task.py guard` | Run the guard validation |
| `python ai_task.py report` | Generate a task report |
| `python ai_task.py memory --from-report <file>` | Import a report into memory |

---

## Safety Rules (Summary)

| Rule ID | Rule |
|---|---|
| R001 | No code without research |
| R002 | Only modify allowed files |
| R003 | No `git push` to `main` |
| R004 | No Windows paths |
| R005 | Memory is project-scoped only |
