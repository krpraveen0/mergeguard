"""Markdown renderer for MergeGuard reports."""

from __future__ import annotations

from mergeguard.config import CATEGORY_ORDER
from mergeguard.models import Finding, MergeGuardReport


def render_markdown(report: MergeGuardReport) -> str:
    lines = [
        "## MERGE Review Readiness Report",
        "",
        f"### Overall status: {report.overall_status}",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Files changed | {report.stats.files_changed} |",
        f"| Additions | {report.stats.additions} |",
        f"| Deletions | {report.stats.deletions} |",
        "",
        "| Category | Status | Findings |",
        "| --- | --- | ---: |",
        *(_summary_rows(report)),
        "",
    ]

    for category in CATEGORY_ORDER:
        lines.append(f"### {category}")
        findings = report.findings_for(category)
        if findings:
            lines.extend(_finding_line(finding) for finding in findings)
        else:
            lines.append("- **OK**: No issues found.")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def _summary_rows(report: MergeGuardReport) -> list[str]:
    rows: list[str] = []
    for category in CATEGORY_ORDER:
        findings = report.findings_for(category)
        status = "Needs attention" if findings else "OK"
        rows.append(f"| {category} | {status} | {len(findings)} |")
    return rows


def _finding_line(finding: Finding) -> str:
    file_path = f" (`{_escape_inline_code(finding.file_path)}`)" if finding.file_path else ""
    return f"- **{finding.severity}**: {finding.message}{file_path}"


def _escape_inline_code(value: str) -> str:
    return value.replace("`", "\\`")
