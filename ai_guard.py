#!/usr/bin/env python3
"""
ai_guard.py — Validation system for the AI IDE pipeline.

Enforces safety rules before any code changes are applied:
  R001  No code without research (.memory-bank/research/current-task.md must exist and be complete)
  R002  Only allowed files may be modified (list taken from current-task.md)
  R003  No git push to main
  R004  No Windows-style paths in any file
  R005  Memory files must stay inside .memory-bank/ (project-scoped)

Usage:
  python ai_guard.py                         # run all checks
  python ai_guard.py --check research        # only check research gate
  python ai_guard.py --check allowed-files   # only check allowed files
  python ai_guard.py --files a.py b.py       # check specific files against allowed list
"""

import os
import re
import sys
import json
import argparse
import subprocess

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
RESEARCH_FILE = os.path.join(REPO_ROOT, ".memory-bank", "research", "current-task.md")
MEMORY_ROOT = os.path.join(REPO_ROOT, ".memory-bank")

WINDOWS_PATH_RE = re.compile(r"[A-Za-z]:\\\\|[A-Za-z]:\\")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _error(rule_id: str, message: str) -> dict:
    return {"status": "FAIL", "rule": rule_id, "message": message}


def _ok(rule_id: str, message: str = "OK") -> dict:
    return {"status": "PASS", "rule": rule_id, "message": message}


def _read_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


# ---------------------------------------------------------------------------
# R001 — Research gate
# ---------------------------------------------------------------------------

def check_research_gate() -> dict:
    """R001: current-task.md must exist and contain required sections."""
    if not os.path.isfile(RESEARCH_FILE):
        return _error(
            "R001",
            f"Research file not found: {RESEARCH_FILE}\n"
            "Run 'python ai_task.py new \"<task>\"' to create it.",
        )

    content = _read_file(RESEARCH_FILE)
    required_sections = ["## Selected Solution", "## Allowed Files"]
    missing = [s for s in required_sections if s not in content]
    if missing:
        return _error(
            "R001",
            f"Research file is incomplete. Missing sections: {missing}",
        )

    return _ok("R001", f"Research file present and complete: {RESEARCH_FILE}")


# ---------------------------------------------------------------------------
# R002 — Allowed files
# ---------------------------------------------------------------------------

def _parse_allowed_files() -> list:
    """Extract the allowed files list from current-task.md."""
    if not os.path.isfile(RESEARCH_FILE):
        return []

    content = _read_file(RESEARCH_FILE)
    # Find the ## Allowed Files section and extract fenced code block contents
    match = re.search(
        r"## Allowed Files\s*```[^\n]*\n(.*?)```",
        content,
        re.DOTALL,
    )
    if not match:
        return []

    lines = match.group(1).strip().splitlines()
    return [ln.strip() for ln in lines if ln.strip()]


def check_allowed_files(files_to_check: list = None) -> dict:
    """R002: Files being modified must be in the allowed_files list."""
    allowed = _parse_allowed_files()
    if not allowed:
        return _error(
            "R002",
            "No allowed_files list found in research file. "
            "Add an '## Allowed Files' fenced code block to current-task.md.",
        )

    if files_to_check is None:
        # If no specific files provided, just confirm the list is non-empty
        return _ok("R002", f"Allowed files list found ({len(allowed)} entries).")

    violations = [f for f in files_to_check if f not in allowed]
    if violations:
        return _error(
            "R002",
            f"Files not in allowed list: {violations}\n"
            f"Allowed: {allowed}",
        )

    return _ok("R002", f"All {len(files_to_check)} file(s) are in the allowed list.")


# ---------------------------------------------------------------------------
# R003 — No push to main
# ---------------------------------------------------------------------------

def check_no_push_to_main() -> dict:
    """R003: Current branch must not be 'main'."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        branch = result.stdout.strip()
    except FileNotFoundError:
        return _ok("R003", "git not available — skipping branch check.")

    if branch == "main":
        return _error(
            "R003",
            "Current branch is 'main'. Direct commits to main are forbidden. "
            "Create a feature branch first.",
        )

    return _ok("R003", f"Current branch is '{branch}' (not main).")


# ---------------------------------------------------------------------------
# R004 — No Windows paths
# ---------------------------------------------------------------------------

def _scan_file_for_windows_paths(path: str) -> list:
    """Return list of (line_number, line) tuples containing Windows paths."""
    hits = []
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as fh:
            for i, line in enumerate(fh, start=1):
                if WINDOWS_PATH_RE.search(line):
                    hits.append((i, line.rstrip()))
    except OSError:
        pass
    return hits


def check_no_windows_paths(files_to_check: list = None) -> dict:
    """R004: No Windows-style paths may appear in tracked files."""
    if files_to_check is None:
        # Scan all non-binary tracked files
        try:
            result = subprocess.run(
                ["git", "ls-files"],
                capture_output=True,
                text=True,
                cwd=REPO_ROOT,
            )
            files_to_check = [
                os.path.join(REPO_ROOT, f)
                for f in result.stdout.strip().splitlines()
                if f
            ]
        except FileNotFoundError:
            return _ok("R004", "git not available — skipping Windows path scan.")

    violations = {}
    for fpath in files_to_check:
        full = fpath if os.path.isabs(fpath) else os.path.join(REPO_ROOT, fpath)
        hits = _scan_file_for_windows_paths(full)
        if hits:
            violations[fpath] = hits

    if violations:
        details = "; ".join(
            f"{f}: line {ln}" for f, lines in violations.items() for ln, _ in lines
        )
        return _error("R004", f"Windows-style paths found: {details}")

    return _ok("R004", "No Windows-style paths detected.")


# ---------------------------------------------------------------------------
# R005 — Project-scoped memory
# ---------------------------------------------------------------------------

def check_project_scoped_memory() -> dict:
    """R005: Memory files must reside inside .memory-bank/."""
    if not os.path.isdir(MEMORY_ROOT):
        return _error("R005", f".memory-bank/ directory not found at {MEMORY_ROOT}")

    # Check that no memory file references an absolute external path
    violations = []
    for dirpath, _dirs, filenames in os.walk(MEMORY_ROOT):
        for fname in filenames:
            fpath = os.path.join(dirpath, fname)
            try:
                content = _read_file(fpath)
            except OSError:
                continue
            # Look for absolute paths that escape the repo
            external_refs = re.findall(r"(?:^|[\s\(])(/(?!\.)[^\s\)]+)", content, re.MULTILINE)
            for ref in external_refs:
                if not ref.startswith(REPO_ROOT):
                    violations.append((fpath, ref))

    if violations:
        details = "; ".join(f"{f}: '{r}'" for f, r in violations[:5])
        return _error("R005", f"External path references found in memory files: {details}")

    return _ok("R005", "Memory files are project-scoped.")


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run_checks(check_name: str = None, files_to_check: list = None) -> list:
    all_checks = {
        "research": check_research_gate,
        "allowed-files": lambda: check_allowed_files(files_to_check),
        "no-push-to-main": check_no_push_to_main,
        "no-windows-paths": lambda: check_no_windows_paths(files_to_check),
        "project-scoped-memory": check_project_scoped_memory,
    }

    if check_name:
        if check_name not in all_checks:
            print(f"Unknown check: {check_name}. Available: {list(all_checks)}")
            sys.exit(1)
        checks_to_run = {check_name: all_checks[check_name]}
    else:
        checks_to_run = all_checks

    results = []
    for name, fn in checks_to_run.items():
        result = fn()
        results.append(result)
        status_symbol = "✓" if result["status"] == "PASS" else "✗"
        print(f"  [{status_symbol}] {result['rule']} — {result['message']}")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="AI IDE Guard — validates safety rules before code changes."
    )
    parser.add_argument(
        "--check",
        metavar="NAME",
        help="Run a single check by name (research, allowed-files, no-push-to-main, "
             "no-windows-paths, project-scoped-memory)",
    )
    parser.add_argument(
        "--files",
        nargs="+",
        metavar="FILE",
        help="Files to validate against the allowed list and Windows path check.",
    )
    args = parser.parse_args()

    print("=== AI Guard ===")
    results = run_checks(check_name=args.check, files_to_check=args.files)

    failures = [r for r in results if r["status"] == "FAIL"]
    print()
    if failures:
        print(f"RESULT: FAIL ({len(failures)} rule(s) violated)")
        sys.exit(1)
    else:
        print("RESULT: PASS — all checks passed")
        sys.exit(0)


if __name__ == "__main__":
    main()
