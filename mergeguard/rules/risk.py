"""Risk checks for sensitive paths and terms."""

from __future__ import annotations

from mergeguard.models import Finding, ScanContext
from mergeguard.rules.base import Rule


class RiskRule(Rule):
    category = "Risk"

    def run(self, context: ScanContext) -> list[Finding]:
        chunks: list[str] = []
        for changed_file in context.changed_files:
            chunks.extend(
                [
                    changed_file.path,
                    changed_file.old_path or "",
                    "\n".join(changed_file.added_lines),
                    "\n".join(changed_file.removed_lines),
                ]
            )

        haystack = "\n".join(chunks).lower()

        found_terms = [
            term for term in context.config.risky_terms if term.lower() in haystack
        ]

        if found_terms:
            return [
                self.finding(
                    "HIGH",
                    f"Risk-sensitive terms found: {', '.join(found_terms)}.",
                )
            ]

        return []
