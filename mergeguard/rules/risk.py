"""Risk checks for sensitive paths and terms."""

from __future__ import annotations

from mergeguard.models import Finding, ScanContext
from mergeguard.rules.base import Rule, path_matches_patterns


class RiskRule(Rule):
    category = "Risk"

    def run(self, context: ScanContext) -> list[Finding]:
        findings: list[Finding] = []
        chunks: list[str] = []
        risky_paths: list[str] = []

        for changed_file in context.changed_files:
            if path_matches_patterns(changed_file.path, context.config.risk_paths):
                risky_paths.append(changed_file.path)
            chunks.extend(
                [
                    changed_file.path,
                    changed_file.old_path or "",
                    "\n".join(changed_file.added_lines),
                    "\n".join(changed_file.removed_lines),
                ]
            )

        haystack = "\n".join(chunks).lower()

        found_terms = _unique(
            [
                keyword
                for keyword in context.config.risk_keywords
                if keyword.lower() in haystack
            ]
        )

        if found_terms:
            findings.append(
                self.finding(
                    "HIGH",
                    f"Risk-sensitive terms found: {', '.join(found_terms)}.",
                )
            )

        if risky_paths:
            findings.append(
                self.finding(
                    "HIGH",
                    f"Risk-sensitive paths changed: {', '.join(_unique(risky_paths))}.",
                )
            )

        return findings


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    unique_values: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            unique_values.append(value)
    return unique_values
