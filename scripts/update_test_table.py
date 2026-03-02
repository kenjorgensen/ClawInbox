from __future__ import annotations

import json
from pathlib import Path


CATEGORY_MAP = {
    "test_cleanup.py": "Maintenance",
    "test_db.py": "Database",
    "test_fts.py": "Search",
    "test_hybrid.py": "Search",
    "test_imap_errors.py": "IMAP",
    "test_integration_auth.py": "Integration",
    "test_integration_multiaccount.py": "Integration",
    "test_normalize.py": "Normalization",
    "test_normalize_property.py": "Normalization",
    "test_purge.py": "Maintenance",
    "test_rules.py": "Rules",
    "test_settings_dirs.py": "Settings",
    "test_status_tools.py": "Status",
    "test_store.py": "Storage",
}


def humanize(name: str) -> str:
    return name.replace("test_", "").replace("_", " ").strip().title()


def generate_table(report: dict) -> str:
    rows = []
    for test in report.get("tests", []):
        nodeid = test.get("nodeid", "")
        file = nodeid.split("::")[0].replace("tests/", "")
        name = nodeid.split("::")[-1]
        category = CATEGORY_MAP.get(file, "Other")
        outcome = test.get("outcome")
        rows.append((category, humanize(name), outcome))

    rows.sort()
    lines = [
        "| Category | Test | Pass? |",
        "| --- | --- | --- |",
    ]
    for category, name, outcome in rows:
        lines.append(f"| {category} | {name} | {'Yes' if outcome == 'passed' else 'No'} |")
    return "\n".join(lines)


def update_readme(readme_path: Path, table: str) -> None:
    text = readme_path.read_text()
    start = "<!-- TEST_TABLE_START -->"
    end = "<!-- TEST_TABLE_END -->"
    if start not in text or end not in text:
        raise RuntimeError("README missing test table markers.")
    before, rest = text.split(start, 1)
    _, after = rest.split(end, 1)
    updated = f"{before}{start}\n{table}\n{end}{after}"
    readme_path.write_text(updated)


def main() -> None:
    report_path = Path(".pytest-report.json")
    if not report_path.exists():
        raise RuntimeError("Missing .pytest-report.json. Run pytest with --json-report.")
    report = json.loads(report_path.read_text())
    table = generate_table(report)
    update_readme(Path("README.md"), table)


if __name__ == "__main__":
    main()
