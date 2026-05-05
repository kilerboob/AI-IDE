#!/usr/bin/env python3
"""
ai_task.py — CLI to manage the AI IDE task workflow.

Commands:
  new "<task name>"              Start a new task: creates research stub and logs to changelog.
  guard                          Run ai_guard.py validation before code changes.
  report                         Generate a timestamped task report in .memory-bank/reports/.
  memory --from-report <file>    Import a report into long-term memory files.

Usage examples:
  python ai_task.py new "Add login endpoint"
  python ai_task.py guard
  python ai_task.py report
  python ai_task.py memory --from-report .memory-bank/reports/2026-05-05-add-login-endpoint.md
"""

import os
import re
import sys
import json
import argparse
import subprocess
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
MEMORY_ROOT = os.path.join(REPO_ROOT, ".memory-bank")
RESEARCH_DIR = os.path.join(MEMORY_ROOT, "research")
REPORTS_DIR = os.path.join(MEMORY_ROOT, "reports")
RESEARCH_FILE = os.path.join(RESEARCH_DIR, "current-task.md")
CHANGELOG_FILE = os.path.join(MEMORY_ROOT, "changelog.md")
PROJECT_FILE = os.path.join(MEMORY_ROOT, "project.md")
CONTEXT_FILE = os.path.join(MEMORY_ROOT, "context.md")
DECISIONS_FILE = os.path.join(MEMORY_ROOT, "decisions.md")
ROADMAP_FILE = os.path.join(MEMORY_ROOT, "roadmap.md")
LEDGER_FILE = os.path.join(MEMORY_ROOT, "import-ledger.json")
GUARD_SCRIPT = os.path.join(REPO_ROOT, "ai_guard.py")


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def _today() -> str:
    return datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")


def _now_iso() -> str:
    return datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s-]+", "-", text)
    return text


def _ensure_dirs():
    os.makedirs(RESEARCH_DIR, exist_ok=True)
    os.makedirs(REPORTS_DIR, exist_ok=True)


def _read_file(path: str) -> str:
    if not os.path.isfile(path):
        return ""
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def _write_file(path: str, content: str):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)


def _prepend_to_file(path: str, content: str):
    existing = _read_file(path)
    _write_file(path, content + existing)


def _append_to_file(path: str, content: str):
    existing = _read_file(path)
    _write_file(path, existing + content)


def _read_ledger() -> dict:
    if not os.path.isfile(LEDGER_FILE):
        return {"version": "1.0", "imported": []}
    with open(LEDGER_FILE, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _write_ledger(ledger: dict):
    with open(LEDGER_FILE, "w", encoding="utf-8") as fh:
        json.dump(ledger, fh, indent=2)
        fh.write("\n")


# ---------------------------------------------------------------------------
# Command: new
# ---------------------------------------------------------------------------

def cmd_new(task_name: str):
    """Create a new task: generate research stub and log to changelog."""
    _ensure_dirs()
    today = _today()
    slug = _slugify(task_name)

    research_stub = f"""# Research: {task_name}

**Task:** {task_name}
**Date:** {today}
**Status:** In progress

---

## Problem Statement
<!-- Describe what needs to be done and why -->

---

## Options Considered

### Option A — <!-- name -->
<!-- Describe -->
**Pros:**
**Cons:**

### Option B — <!-- name -->
<!-- Describe -->
**Pros:**
**Cons:**

---

## Selected Solution
<!-- State which option was chosen and why -->

### Rationale
<!-- Explain the decision -->

---

## Allowed Files
```
<!-- List every file path that the coder is permitted to modify -->
```
"""

    _write_file(RESEARCH_FILE, research_stub)
    print(f"✓ Research stub created: {RESEARCH_FILE}")

    changelog_entry = f"\n## {today} — {task_name}\n\n### Started\n- Task '{task_name}' created (slug: {slug})\n"
    _append_to_file(CHANGELOG_FILE, changelog_entry)
    print(f"✓ Changelog updated: {CHANGELOG_FILE}")

    # Update context
    context_update = f"## Current Task\n**Name:** {task_name}  \n**Status:** In progress  \n**Research file:** `.memory-bank/research/current-task.md`\n\n"
    content = _read_file(CONTEXT_FILE)
    new_content = re.sub(
        r"## Current Task\n.*?(?=\n## |\Z)",
        context_update,
        content,
        flags=re.DOTALL,
    )
    if new_content == content:
        new_content = context_update + content
    _write_file(CONTEXT_FILE, new_content)
    print(f"✓ Context updated: {CONTEXT_FILE}")

    print(f"\nNext step: fill in {RESEARCH_FILE}, then run 'python ai_task.py guard'")


# ---------------------------------------------------------------------------
# Command: guard
# ---------------------------------------------------------------------------

def cmd_guard():
    """Run ai_guard.py validation."""
    if not os.path.isfile(GUARD_SCRIPT):
        print(f"Error: guard script not found at {GUARD_SCRIPT}", file=sys.stderr)
        sys.exit(1)

    result = subprocess.run(
        [sys.executable, GUARD_SCRIPT],
        cwd=REPO_ROOT,
    )
    sys.exit(result.returncode)


# ---------------------------------------------------------------------------
# Command: report
# ---------------------------------------------------------------------------

def cmd_report(task_name: str = None):
    """Generate a timestamped task report in .memory-bank/reports/."""
    _ensure_dirs()
    today = _today()

    # Try to derive task name from research file if not provided
    if not task_name:
        research_content = _read_file(RESEARCH_FILE)
        match = re.search(r"^# Research: (.+)$", research_content, re.MULTILINE)
        if match:
            task_name = match.group(1).strip()
        else:
            task_name = "unnamed-task"

    slug = _slugify(task_name)
    report_path = os.path.join(REPORTS_DIR, f"{today}-{slug}.md")

    report_content = f"""# Task Report: {task_name}

**Date:** {today}
**Task slug:** {slug}
**Status:** Complete

---

## Summary
<!-- Briefly describe what was done -->

---

## Solution Implemented
<!-- Describe the implementation -->

---

## Files Changed
```
<!-- List files that were created or modified -->
```

---

## QA Results
<!-- Describe tests run and outcomes -->
- Tests run:
- Tests passed:
- Tests failed:
- Regressions:

---

## Open Issues
<!-- List any unresolved items -->
"""

    _write_file(report_path, report_content)
    print(f"✓ Report created: {report_path}")

    changelog_entry = f"\n## {today} — {task_name} (report)\n\n### Reported\n- Report written to `{os.path.relpath(report_path, REPO_ROOT)}`\n"
    _append_to_file(CHANGELOG_FILE, changelog_entry)
    print(f"✓ Changelog updated: {CHANGELOG_FILE}")
    print(f"\nNext step: fill in the report, then run 'python ai_task.py memory --from-report {report_path}'")


# ---------------------------------------------------------------------------
# Command: memory --from-report
# ---------------------------------------------------------------------------

def _extract_section(content: str, heading: str) -> str:
    """Extract text under a markdown heading until the next heading of same or higher level."""
    pattern = rf"^{re.escape(heading)}\n(.*?)(?=^#{1,len(heading) - len(heading.lstrip('#'))+1} |\Z)"
    match = re.search(pattern, content, re.DOTALL | re.MULTILINE)
    if match:
        return match.group(1).strip()
    return ""


def cmd_memory(report_path: str):
    """Import a completed report into long-term memory files."""
    report_path = os.path.abspath(report_path)

    if not os.path.isfile(report_path):
        print(f"Error: report file not found: {report_path}", file=sys.stderr)
        sys.exit(1)

    # Deduplication check
    ledger = _read_ledger()
    report_key = os.path.relpath(report_path, REPO_ROOT)
    if report_key in ledger.get("imported", []):
        print(f"Report already imported (see import-ledger.json): {report_key}")
        sys.exit(0)

    report_content = _read_file(report_path)

    # Extract task name and date from report
    name_match = re.search(r"^# Task Report: (.+)$", report_content, re.MULTILINE)
    task_name = name_match.group(1).strip() if name_match else os.path.basename(report_path)
    date_match = re.search(r"\*\*Date:\*\*\s*(.+)$", report_content, re.MULTILINE)
    report_date = date_match.group(1).strip() if date_match else _today()

    # --- changelog.md ---
    summary_section = _extract_section(report_content, "## Summary")
    changelog_entry = (
        f"\n## {report_date} — {task_name} (imported)\n\n"
        f"### Summary\n{summary_section or '(see report)'}\n"
        f"\n_Report: `{report_key}`_\n"
    )
    _append_to_file(CHANGELOG_FILE, changelog_entry)
    print(f"✓ changelog.md updated")

    # --- context.md: replace Current Task block ---
    context_update = (
        f"## Current Task\n"
        f"**Name:** {task_name}  \n"
        f"**Status:** Complete  \n"
        f"**Report:** `{report_key}`\n\n"
    )
    content = _read_file(CONTEXT_FILE)
    new_content = re.sub(
        r"## Current Task\n.*?(?=\n## |\Z)",
        context_update,
        content,
        flags=re.DOTALL,
    )
    if new_content == content:
        new_content = context_update + content
    _write_file(CONTEXT_FILE, new_content)
    print(f"✓ context.md updated")

    # --- decisions.md: append if solution section exists ---
    solution_section = _extract_section(report_content, "## Solution Implemented")
    if solution_section and "<!-- " not in solution_section:
        decisions_entry = (
            f"\n## {report_date} — {task_name}\n\n"
            f"**Decision:** {solution_section[:200].splitlines()[0]}\n"
            f"**Source report:** `{report_key}`\n"
        )
        _append_to_file(DECISIONS_FILE, decisions_entry)
        print(f"✓ decisions.md updated")
    else:
        print(f"  (decisions.md skipped — solution section is a template placeholder)")

    # --- roadmap.md: mark task as complete ---
    roadmap_content = _read_file(ROADMAP_FILE)
    updated_roadmap = roadmap_content.replace(
        f"- [ ] {task_name}",
        f"- [x] {task_name}",
    )
    if updated_roadmap != roadmap_content:
        _write_file(ROADMAP_FILE, updated_roadmap)
        print(f"✓ roadmap.md updated (marked '{task_name}' complete)")
    else:
        print(f"  (roadmap.md — no matching in-progress entry found for '{task_name}')")

    # --- import-ledger.json ---
    ledger.setdefault("imported", []).append(report_key)
    _write_ledger(ledger)
    print(f"✓ import-ledger.json updated (report marked as imported)")

    print(f"\n✓ Memory import complete for: {task_name}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="AI Task CLI — manage the AI IDE task workflow."
    )
    subparsers = parser.add_subparsers(dest="command", metavar="COMMAND")

    # new
    p_new = subparsers.add_parser("new", help="Start a new task")
    p_new.add_argument("task_name", metavar="TASK_NAME", help='Name of the new task (e.g. "Add login endpoint")')

    # guard
    subparsers.add_parser("guard", help="Run guard validation (ai_guard.py)")

    # report
    p_report = subparsers.add_parser("report", help="Generate a task report")
    p_report.add_argument(
        "--task",
        metavar="TASK_NAME",
        help="Task name to use in the report filename (derived from research file if omitted)",
    )

    # memory
    p_memory = subparsers.add_parser("memory", help="Import a report into long-term memory")
    p_memory.add_argument(
        "--from-report",
        metavar="FILE",
        required=True,
        help="Path to the report file to import",
    )

    args = parser.parse_args()

    if args.command == "new":
        cmd_new(args.task_name)
    elif args.command == "guard":
        cmd_guard()
    elif args.command == "report":
        cmd_report(task_name=getattr(args, "task", None))
    elif args.command == "memory":
        cmd_memory(args.from_report)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
