"""Evidence checks for tests accompanying source changes."""

from __future__ import annotations

from mergeguard.models import Finding, ScanContext
from mergeguard.rules.base import Rule, is_source_file, is_test_file


class EvidenceRule(Rule):
    category = "Evidence"

    def run(self, context: ScanContext) -> list[Finding]:
        source_files = [
            changed_file
            for changed_file in context.changed_files
            if is_source_file(changed_file, context.config)
        ]
        test_files = [
            changed_file
            for changed_file in context.changed_files
            if is_test_file(changed_file.path, context.config)
        ]

        if source_files and not test_files:
            return [
                self.finding(
                    "WARNING",
                    "Source files changed but no test files were modified.",
                )
            ]

        return []
