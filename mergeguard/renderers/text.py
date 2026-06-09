"""Plain-text renderer for MergeGuard reports."""

from __future__ import annotations

from mergeguard.config import CATEGORY_ORDER
from mergeguard.models import Finding, MergeGuardReport


def render_text(report: MergeGuardReport) -> str:
    lines = [
        "MERGE Review Readiness Report",
        f"Overall status: {report.overall_status}",
        (
            "Stats: "
            f"{report.stats.files_changed} files changed, "
            f"{report.stats.additions} additions, "
            f"{report.stats.deletions} deletions"
        ),
        "",
    ]

    for category in CATEGORY_ORDER:
        lines.append(category)
        findings = report.findings_for(category)
        if findings:
            lines.extend(_finding_line(finding) for finding in findings)
        else:
            lines.append("- OK: No issues found.")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def _finding_line(finding: Finding) -> str:
    file_path = f" ({finding.file_path})" if finding.file_path else ""
    return f"- {finding.severity}: {finding.message}{file_path}"
