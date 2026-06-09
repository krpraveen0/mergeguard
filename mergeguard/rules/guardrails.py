"""Guardrail checks for dependency, config, and large PR concerns."""

from __future__ import annotations

from pathlib import PurePosixPath

from mergeguard.models import Finding, ScanContext
from mergeguard.rules.base import Rule, is_dependency_file


class GuardrailsRule(Rule):
    category = "Guardrails"

    def run(self, context: ScanContext) -> list[Finding]:
        findings: list[Finding] = []
        dependency_paths = [
            changed_file.path
            for changed_file in context.changed_files
            if is_dependency_file(changed_file.path, context.config)
        ]

        for path in dependency_paths:
            filename = PurePosixPath(path.replace("\\", "/")).name
            findings.append(
                self.finding("WARNING", f"Dependency file changed: {filename}.", path)
            )

        if context.stats.files_changed > context.config.max_changed_files:
            findings.append(
                self.finding(
                    "WARNING",
                    f"Large PR touches {context.stats.files_changed} files.",
                )
            )

        total_line_changes = context.stats.additions + context.stats.deletions
        if total_line_changes > context.config.max_line_changes:
            findings.append(
                self.finding(
                    "WARNING",
                    f"Large PR changes {total_line_changes} lines.",
                )
            )

        return findings
