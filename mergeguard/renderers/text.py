"""Plain-text renderer for MergeGuard reports."""

from __future__ import annotations

from mergeguard.config import CATEGORY_ORDER
from mergeguard.models import MergeGuardReport


def render_text(report: MergeGuardReport) -> str:
    lines = [
        "MERGE Review Readiness Report",
        f"Overall status: {report.overall_status}",
        "",
    ]

    for category in CATEGORY_ORDER:
        lines.append(category)
        findings = report.findings_for(category)
        if findings:
            lines.extend(f"- {finding.severity}: {finding.message}" for finding in findings)
        else:
            lines.append("- OK: No issues found.")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"
